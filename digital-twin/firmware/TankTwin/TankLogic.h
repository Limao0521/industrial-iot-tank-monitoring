#pragma once
#include <stdint.h>

class TankLogic {
 public:
  static constexpr uint32_t armMs = 2000;
  static constexpr uint32_t leaseMs = 30000;

  void update(uint32_t now, uint8_t sensors, bool start, bool stop) {
    rawMask = sensors;
    if (stop) active = false;
    else if (start && !lastStart) {
      active = true;
      armedSince = now;
      holdingStart = true;
    }
    lastStart = start;
    if (stop || !start) holdingStart = false;
    armed = active && holdingStart && now - armedSince >= armMs;
    if (!armed || now - commandedAt >= leaseMs) overridden = false;
  }

  bool command(uint32_t now, uint16_t level) {
    if (level == 0) {
      overridden = false;
      return true;
    }
    if (!armed || level > 4) return false;
    constexpr uint8_t levels[] = {0, 0, 1, 3, 7};
    requestedMask = levels[level];
    commandedAt = now;
    overridden = true;
    return true;
  }

  uint8_t effectiveMask() const { return overridden ? requestedMask : rawMask; }

  uint8_t status() const {
    if (!active) return 0;
    switch (effectiveMask()) {
      case 0: return 4;
      case 1: return 2;
      case 3: return 1;
      case 7: return 3;
      default: return 5;
    }
  }

  uint8_t rawMask = 0;
  bool active = false;
  bool armed = false;
  bool overridden = false;

 private:
  uint32_t armedSince = 0;
  uint32_t commandedAt = 0;
  uint8_t requestedMask = 0;
  bool lastStart = true;
  bool holdingStart = false;
};
