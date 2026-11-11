from io import BytesIO
import socket
from struct import pack, unpack
from threading import Thread

import pytest

from tank_gateway import (
    Command, MAGIC, ModbusError, ModbusServer, RtuClient, Snapshot,
    crc, demo_input_bits, modbus_response, new_command,
)

VALUES = (3, 3, 1, 1, 0, 0, MAGIC, 1)
READ = bytes.fromhex("010400000008")


class SerialReply:
    def __init__(self, response):
        self.response = BytesIO(response)
        self.sent = None

    def reset_input_buffer(self):
        pass

    def write(self, data):
        self.sent = data

    def read(self, size):
        return self.response.read(size)


def test_rtu_read_and_crc():
    assert crc(bytes.fromhex("010300000001")) == bytes.fromhex("840A")
    payload = bytes((1, 4, 16)) + pack(">8H", *VALUES)
    serial = SerialReply(payload + crc(payload))
    assert RtuClient(serial).read() == VALUES
    assert serial.sent == READ + crc(READ)


@pytest.mark.parametrize("response", [b"", b"\x01\x04\x0e", b"\x01\x84\x03\0\0"])
def test_rtu_rejects_incomplete_or_invalid_reply(response):
    with pytest.raises(ModbusError):
        RtuClient(SerialReply(response)).read()


def test_rtu_write_echo_and_exception():
    request = bytes.fromhex("010600000003")
    RtuClient(SerialReply(request + crc(request))).write(3)
    error = bytes.fromhex("018603")
    with pytest.raises(ModbusError, match="exception 3"):
        RtuClient(SerialReply(error + crc(error))).write(3)


def test_serial_demo_uses_separate_register_and_encodes_start_stop():
    request = bytes.fromhex("01060001010B")
    serial = SerialReply(request + crc(request))
    RtuClient(serial).write_demo_inputs(demo_input_bits("110 1 0"))
    assert serial.sent == request + crc(request)
    assert demo_input_bits("001 0 1") == 20
    with pytest.raises(ValueError):
        demo_input_bits("110 2 0")


@pytest.mark.parametrize("value", [True, "3", 2.5, -1, 5, None, float("nan")])
def test_command_rejects_invalid_value(value):
    assert new_command({"timestamp": 39_999, "value": value}, 30_000, 40_000, 10) == (39_999, None)


def test_command_requires_fresh_timestamp_and_deduplicates():
    dot = {"timestamp": 39_000, "value": 3.0}
    assert new_command(dot, 30_000, 40_000, 10) == (39_000, Command(3, 24))
    assert new_command(dot, 39_000, 40_000, 11) == (39_000, None)
    assert new_command(dot, 0, 54_000, 11) == (39_000, None)
    assert new_command(dot, 0, 38_999, 11) == (0, None)


def test_tcp_contract():
    pdu = READ[1:]
    assert modbus_response(1, pdu, None) == bytes.fromhex("840b")
    assert modbus_response(1, bytes.fromhex("0600000003"), VALUES) == bytes.fromhex("8601")
    assert modbus_response(1, bytes.fromhex("0400080001"), VALUES) == bytes.fromhex("8402")


def test_tcp_round_trip():
    snapshot = Snapshot()
    with ModbusServer(snapshot, 0) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as sock:
                with sock.makefile("rb") as response:
                    for transaction, values in ((42, None), (43, VALUES)):
                        snapshot.set(values)
                        sock.sendall(pack(">HHH", transaction, 0, len(READ)) + READ)
                        header = response.read(7)
                        actual, protocol, length, unit = unpack(">HHHB", header)
                        assert (actual, protocol, unit) == (transaction, 0, 1)
                        assert response.read(length - 1) == modbus_response(1, READ[1:], values)
        finally:
            server.shutdown()
            thread.join()
