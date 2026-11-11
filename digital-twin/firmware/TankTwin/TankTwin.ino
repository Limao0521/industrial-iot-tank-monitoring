#include "TankLogic.h"

namespace {
constexpr uint8_t inputPins[] = {19, 21, 22, 23, 16};
constexpr uint8_t lampPins[] = {2, 4, 15, 5, 18};
constexpr uint8_t activeLamp = 17;
constexpr uint8_t unit = 1;
constexpr uint16_t identity = 0xA231;
constexpr uint32_t frameGapUs = 3000;
constexpr uint32_t demoTimeoutMs = 5000;

TankLogic tank;
uint8_t stableInputs;
uint8_t pendingInputs;
uint32_t pendingSince;
uint8_t frame[8];
size_t received;
uint32_t lastByte;
bool overflow;
bool serialInputs = true;
bool demoExpired = true;
uint8_t injectedInputs;
uint32_t injectedAt;

uint8_t readInputs() {
  uint8_t sample = 0;
  for (uint8_t i = 0; i < sizeof(inputPins); ++i) {
    if (digitalRead(inputPins[i])) sample |= 1U << i;
  }
  return sample;
}

void updateInputs() {
  const uint32_t now = millis();
  if (serialInputs && !demoExpired && now - injectedAt >= demoTimeoutMs) {
    demoExpired = true;
    injectedInputs = 0;
    tank = TankLogic{};
  }
  const uint8_t sample = serialInputs ? injectedInputs : readInputs();
  if (sample != pendingInputs) {
    pendingInputs = sample;
    pendingSince = now;
  }
  if (now - pendingSince >= 15) stableInputs = pendingInputs;
  tank.update(now, stableInputs & 7, stableInputs & 8, (sample | stableInputs) & 16);
}

bool setInputSource(uint16_t value) {
  constexpr uint16_t demoFlag = 0x0100;
  if (value != 0 && (value < demoFlag || value > demoFlag + 31)) return false;
  const bool wasSerial = serialInputs;
  serialInputs = value != 0;
  demoExpired = false;
  injectedInputs = value & 31;
  injectedAt = millis();
  if (serialInputs != wasSerial) {
    tank = TankLogic{};
    stableInputs = pendingInputs = serialInputs ? injectedInputs : readInputs();
    pendingSince = millis();
  }
  return true;
}

void updateLamps() {
  const uint8_t status = tank.status();
  for (uint8_t i = 0; i < sizeof(lampPins); ++i) {
    digitalWrite(lampPins[i], status == i + 1);
  }
  digitalWrite(activeLamp, tank.active);
}

uint16_t crc(const uint8_t* data, size_t length) {
  uint16_t value = 0xFFFF;
  for (size_t i = 0; i < length; ++i) {
    value ^= data[i];
    for (uint8_t bit = 0; bit < 8; ++bit) {
      value = (value >> 1) ^ ((value & 1) ? 0xA001 : 0);
    }
  }
  return value;
}

uint16_t word(const uint8_t* data) {
  return (static_cast<uint16_t>(data[0]) << 8) | data[1];
}

void reply(uint8_t* buffer, size_t length) {
  const uint16_t check = crc(buffer, length);
  buffer[length] = check & 0xFF;
  buffer[length + 1] = check >> 8;
  Serial.write(buffer, length + 2);
}

void exception(uint8_t function, uint8_t code) {
  uint8_t response[5] = {unit, static_cast<uint8_t>(function | 0x80), code};
  reply(response, 3);
}

void serveFrame() {
  if (overflow || received != sizeof(frame) || frame[0] != unit) return;
  if (crc(frame, 6) != (frame[6] | (frame[7] << 8))) return;

  const uint8_t function = frame[1];
  const uint16_t address = word(frame + 2);
  const uint16_t argument = word(frame + 4);
  if (function == 4) {
    const uint16_t registers[] = {
      tank.rawMask, tank.effectiveMask(), tank.active, tank.status(),
      tank.overridden, tank.armed, identity, serialInputs
    };
    const size_t count = sizeof(registers) / sizeof(registers[0]);
    if (argument == 0 || argument > 125) {
      exception(function, 3);
    } else if (address >= count || argument > count - address) {
      exception(function, 2);
    } else {
      uint8_t response[3 + sizeof(registers) + 2] = {
        unit, function, static_cast<uint8_t>(2 * argument)
      };
      for (uint16_t i = 0; i < argument; ++i) {
        const uint16_t value = registers[address + i];
        response[3 + 2 * i] = value >> 8;
        response[4 + 2 * i] = value & 0xFF;
      }
      reply(response, 3 + 2 * argument);
    }
  } else if (function == 6) {
    if (address > 1) {
      exception(function, 2);
      return;
    }
    const bool applied = address == 0 ? tank.command(millis(), argument) : setInputSource(argument);
    if (!applied) {
      exception(function, 3);
      return;
    }
    updateInputs();
    updateLamps();
    reply(frame, 6);
  } else {
    exception(function, 1);
  }
}

void pollSerial() {
  if ((received || overflow) && !Serial.available() && micros() - lastByte >= frameGapUs) {
    serveFrame();
    received = 0;
    overflow = false;
  }
  while (Serial.available()) {
    const uint8_t byte = Serial.read();
    if (received < sizeof(frame)) frame[received++] = byte;
    else overflow = true;
    lastByte = micros();
  }
}
}  // namespace

void setup() {
  for (uint8_t pin : inputPins) pinMode(pin, INPUT);
  for (uint8_t pin : lampPins) pinMode(pin, OUTPUT);
  pinMode(activeLamp, OUTPUT);
  updateLamps();
  stableInputs = pendingInputs = serialInputs ? 0 : readInputs();
  pendingSince = millis();
  Serial.begin(19200, SERIAL_8E1);
}

void loop() {
  updateInputs();
  updateLamps();
  pollSerial();
}
