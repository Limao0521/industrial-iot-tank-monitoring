"""USB Modbus RTU master, local read-only Modbus TCP mirror, and Ubidots client."""

import argparse
from dataclasses import dataclass
from getpass import getpass
import json
import logging
import os
from queue import Empty, Full, Queue, SimpleQueue
import socketserver
from struct import pack, unpack
from threading import Event, Lock, Thread
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

UNIT = 1
COUNT = 8
MAGIC = 0xA231
TCP_PORT = 1502
MAX_AGE_MS = 15_000
DEVICE_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/tanque-ra23/"
COMMAND_PATH = "comando-nivel/values/?page_size=1"
LOG = logging.getLogger("tank")


def crc(data):
    value = 0xFFFF
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
    return pack("<H", value)


class ModbusError(OSError):
    pass


class RtuClient:
    def __init__(self, serial_port):
        self.port = serial_port

    def exchange(self, function, argument, address=0):
        request = pack(">BBHH", UNIT, function, address, argument)
        self.port.reset_input_buffer()
        self.port.write(request + crc(request))
        header = self.port.read(3)
        if len(header) != 3 or header[0] != UNIT:
            raise ModbusError("missing RTU header")
        if header[1] == (function | 0x80):
            tail_length = 2
        elif header[1] != function:
            raise ModbusError("unexpected RTU function")
        elif function == 4:
            if header[2] != 2 * COUNT:
                raise ModbusError("unexpected register count")
            tail_length = 2 * COUNT + 2
        else:
            tail_length = 5
        tail = self.port.read(tail_length)
        response = header + tail
        if len(tail) != tail_length or crc(response[:-2]) != response[-2:]:
            raise ModbusError("incomplete RTU response or bad CRC")
        if header[1] != function:
            raise ModbusError(f"RTU exception {header[2]}")
        if function == 6 and response[:-2] != request:
            raise ModbusError("unexpected write echo")
        return response

    def read(self):
        values = unpack(">8H", self.exchange(4, COUNT)[3:-2])
        raw, effective, active, state, override, armed, magic, demo = values
        if (magic != MAGIC or raw > 7 or effective > 7 or active > 1
                or state > 5 or override > 1 or armed > 1 or demo > 1):
            raise ModbusError("invalid tank registers")
        return values

    def write(self, value):
        self.exchange(6, value)

    def write_demo_inputs(self, bits):
        self.exchange(6, 0x0100 | bits, address=1)

    def select_gpio(self):
        self.exchange(6, 0, address=1)


class Snapshot:
    def __init__(self):
        self._lock = Lock()
        self._values = None
        self._updated = 0

    def set(self, values):
        with self._lock:
            self._values = values
            self._updated = time.monotonic()

    def get(self):
        with self._lock:
            if time.monotonic() - self._updated <= 1:
                return self._values
            return None


def modbus_response(unit, pdu, snapshot):
    function = pdu[0]
    if unit != UNIT:
        return bytes((function | 0x80, 11))
    if function != 4:
        return bytes((function | 0x80, 1))
    if len(pdu) != 5:
        return bytes((0x84, 3))
    address, count = unpack(">HH", pdu[1:])
    if not 1 <= count <= 125:
        return bytes((0x84, 3))
    if address + count > COUNT:
        return bytes((0x84, 2))
    if snapshot is None:
        return bytes((0x84, 11))
    return bytes((4, 2 * count)) + pack(f">{count}H", *snapshot[address:address + count])


class ModbusHandler(socketserver.StreamRequestHandler):
    timeout = 3

    def handle(self):
        try:
            while True:
                header = self.rfile.read(7)
                if len(header) != 7:
                    return
                transaction, protocol, length, unit = unpack(">HHHB", header)
                if protocol != 0 or not 2 <= length <= 254:
                    return
                pdu = self.rfile.read(length - 1)
                if len(pdu) != length - 1:
                    return
                reply = modbus_response(unit, pdu, self.server.snapshot.get())
                self.wfile.write(pack(">HHHB", transaction, 0, len(reply) + 1, unit) + reply)
        except OSError:
            return


class ModbusServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, snapshot, port=TCP_PORT):
        self.snapshot = snapshot
        super().__init__(("127.0.0.1", port), ModbusHandler)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Ubidots:
    def __init__(self, token):
        self.token = token
        self.opener = build_opener(NoRedirect)

    def request(self, path="", data=None):
        request = Request(
            DEVICE_URL + path,
            data=None if data is None else json.dumps(data).encode(),
            headers={"X-Auth-Token": self.token, "Content-Type": "application/json"},
        )
        with self.opener.open(request, timeout=4) as response:
            return json.loads(response.read(32_768))

    def latest(self):
        try:
            payload = self.request(COMMAND_PATH)
        except HTTPError as error:
            if error.code == 404:
                return None
            raise
        results = payload.get("results", [])
        return results[0] if results else None

    def publish(self, values):
        data = {"enlace-modbus": int(values is not None)}
        if values is not None:
            raw, effective, active, state, override, armed, _, demo = values
            data.update({
                "entradas-fuente": raw, "entradas-efectivas": effective,
                "sistema-activo": active, "estado-tanque": state,
                "mando-activo": override, "mando-habilitado": armed,
                "entradas-serial": demo,
            })
        response = self.request(data=data)
        for label in data:
            statuses = response.get(label)
            if (not statuses or any(not 200 <= row["status_code"] < 300 for row in statuses)):
                raise OSError("Ubidots rejected a telemetry variable")


@dataclass(frozen=True)
class Command:
    value: int
    expires: float


def new_command(dot, last_seen, now_ms, now_monotonic):
    if not isinstance(dot, dict):
        return last_seen, None
    timestamp = dot.get("timestamp")
    if type(timestamp) is not int or not last_seen < timestamp <= now_ms:
        return last_seen, None
    value = dot.get("value")
    age = now_ms - timestamp
    if age >= MAX_AGE_MS or type(value) not in (int, float) or value not in range(5):
        return timestamp, None
    return timestamp, Command(int(value), now_monotonic + (MAX_AGE_MS - age) / 1000)


def cloud_loop(client, snapshot, commands, stop, remote, started_ms):
    previous = object()
    last_published = float("-inf")
    last_seen = started_ms
    last_error = None
    while not stop.is_set():
        try:
            values = snapshot.get()
            now = time.monotonic()
            age = now - last_published
            if age >= 300 or (age >= 4 and values != previous):
                client.publish(values)
                if last_published == float("-inf"):
                    LOG.info("Ubidots recibió telemetría")
                previous = values
                last_published = time.monotonic()
            if remote:
                dot = client.latest()
                last_seen, command = new_command(
                    dot, last_seen, time.time_ns() // 1_000_000, time.monotonic()
                )
                values = snapshot.get()
                if command and values and (command.value == 0 or values[5]):
                    try:
                        commands.put_nowait(command)
                    except Full:
                        LOG.warning("Comando omitido, cola ocupada")
            last_error = None
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            reason = f"HTTP {error.code}" if isinstance(error, HTTPError) else type(error).__name__
            if reason != last_error:
                LOG.warning("Ubidots no disponible (%s)", reason)
            last_error = reason
        stop.wait(5 if last_error else 1)


def serial_loop(serial_module, port_name, snapshot, commands, stop, demo_updates, select_gpio):
    while not stop.is_set():
        try:
            port = serial_module.Serial(
                baudrate=19200, parity=serial_module.PARITY_EVEN,
                timeout=0.25, write_timeout=0.25,
            )
            port.port = port_name
            port.dtr = False
            port.rts = False
            with port:
                rtu = RtuClient(port)
                previous = None
                has_link = False
                demo_bits = 0
                last_demo = float("-inf")
                gpio_selected = False
                while not stop.is_set():
                    try:
                        # Verify the register map before sending any write to this COM port.
                        values = rtu.read()
                        if select_gpio and not gpio_selected:
                            rtu.select_gpio()
                            gpio_selected = True
                            values = rtu.read()
                        if demo_updates is not None:
                            try:
                                demo_bits = demo_updates.get_nowait()
                                last_demo = float("-inf")
                            except Empty:
                                pass
                            if time.monotonic() - last_demo >= 1:
                                rtu.write_demo_inputs(demo_bits)
                                last_demo = time.monotonic()
                                values = rtu.read()
                    except ModbusError:
                        snapshot.set(None)
                        try:
                            commands.get_nowait()
                        except Empty:
                            pass
                        if has_link or previous is None:
                            LOG.warning("ESP32 sin respuesta Modbus RTU válida")
                        previous = ()
                        has_link = False
                        demo_bits = 0
                        last_demo = float("-inf")
                        gpio_selected = False
                        stop.wait(0.3)
                        continue
                    snapshot.set(values)
                    has_link = True
                    if values != previous:
                        LOG.info(
                            "ESP32 fuente=%s efectivo=%s activo=%s H=%s remoto=%s permiso=%s serial=%s",
                            *values[:6], values[7],
                        )
                        previous = values
                    try:
                        command = commands.get_nowait()
                    except Empty:
                        command = None
                    if (command and time.monotonic() < command.expires
                            and (command.value == 0 or values[5])):
                        try:
                            rtu.write(command.value)
                            LOG.info("Comando %s confirmado por ESP32", command.value)
                        except ModbusError:
                            LOG.warning("ESP32 no confirmó el comando %s", command.value)
                    stop.wait(0.15)
        except OSError as error:
            snapshot.set(None)
            LOG.warning("Enlace RTU no disponible (%s)", type(error).__name__)
            stop.wait(1)


def demo_input_bits(line):
    fields = line.split()
    if (len(fields) != 3 or len(fields[0]) != 3
            or any(bit not in ("0", "1") for bit in fields[0])
            or any(bit not in ("0", "1") for bit in fields[1:])):
        raise ValueError("Usa B1B2B3 START STOP, por ejemplo: 110 1 0")
    return sum(int(bit) << index for index, bit in enumerate("".join(fields)))


def demo_console(updates):
    print("Entradas de prueba por USB. Escribe B1B2B3 START STOP o q para salir.")
    while True:
        line = input("demo> ").strip()
        if line == "q":
            return
        try:
            updates.put(demo_input_bits(line))
        except ValueError as error:
            print(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="Puerto USB del ESP32, p. ej. COM9")
    parser.add_argument("--ubidots", action="store_true", help="Publicar telemetría en Ubidots")
    parser.add_argument("--enable-remote", action="store_true", help="Consultar comandos de Ubidots")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--serial-demo", action="store_true", help="Emular B1–B3 y botones por USB")
    inputs.add_argument("--physical-inputs", action="store_true", help="Seleccionar el montaje GPIO conectado")
    args = parser.parse_args()
    if args.enable_remote and not args.ubidots:
        parser.error("--enable-remote requiere --ubidots")
    try:
        import serial
    except ImportError:
        parser.error("Instala pyserial con python -m pip install -r requirements.txt")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    client = None
    if args.ubidots:
        token = (os.environ.get("UBIDOTS_TOKEN") or getpass("Token de Ubidots: ")).strip()
        if not token:
            parser.error("Se requiere un token de Ubidots")
        client = Ubidots(token)
    snapshot = Snapshot()
    commands = Queue(maxsize=1)
    demo_updates = SimpleQueue() if args.serial_demo else None
    stop = Event()
    with ModbusServer(snapshot) as server:
        LOG.info("Modbus TCP local en 127.0.0.1:%s", TCP_PORT)
        workers = [
            Thread(target=server.serve_forever, daemon=True),
            Thread(target=serial_loop,
                   args=(serial, args.port, snapshot, commands, stop, demo_updates,
                         args.physical_inputs), daemon=True),
        ]
        if client:
            cloud_args = (client, snapshot, commands, stop, args.enable_remote,
                          time.time_ns() // 1_000_000)
            workers.append(Thread(target=cloud_loop, args=cloud_args, daemon=True))
        for worker in workers:
            worker.start()
        try:
            if demo_updates is None:
                stop.wait()
            else:
                demo_console(demo_updates)
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            stop.set()
            server.shutdown()
            for worker in workers:
                worker.join(timeout=5)


if __name__ == "__main__":
    main()
