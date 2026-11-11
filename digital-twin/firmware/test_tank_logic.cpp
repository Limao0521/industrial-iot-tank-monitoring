#include "TankTwin/TankLogic.h"
#include <assert.h>

int main() {
  TankLogic tank;
  tank.update(0, 0, true, false);
  assert(!tank.active);  // A held START at power-up cannot activate the bank.
  tank.update(1, 0, false, false);
  tank.update(2, 0, true, false);
  tank.update(3, 0, false, false);
  assert(tank.active);

  constexpr uint8_t expected[] = {4, 2, 5, 1, 5, 5, 5, 3};
  for (uint8_t mask = 0; mask < 8; ++mask) {
    tank.update(10 + mask, mask, false, false);
    assert(tank.status() == expected[mask]);
  }

  tank.update(100, 3, true, false);
  tank.update(2099, 3, true, false);
  assert(!tank.command(2099, 4));
  tank.update(2100, 3, true, false);
  assert(!tank.command(2100, 5));
  assert(tank.command(2100, 4));
  assert(tank.rawMask == 3 && tank.effectiveMask() == 7 && tank.status() == 3);
  tank.update(32100, 3, true, false);
  assert(!tank.overridden && tank.status() == 1);
  assert(tank.command(32101, 4));
  tank.update(32102, 3, true, true);
  assert(!tank.active && !tank.armed && tank.status() == 0);
  tank.update(32103, 3, true, false);
  assert(!tank.active);

  tank.update(32104, 3, false, false);
  tank.update(32105, 3, true, false);
  tank.update(34105, 3, true, false);
  assert(tank.command(34105, 4));
  assert(tank.command(34106, 0) && !tank.overridden);
  assert(tank.command(34107, 4));
  tank.update(34108, 3, false, false);
  assert(tank.active && !tank.armed && !tank.overridden && tank.status() == 1);
}
