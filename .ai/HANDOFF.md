# Handoff

## Digital twin

- Implementation lives in `digital-twin/` and the native wiki page is `Gemelo-digital-del-tanque-RA2.3`.
- ESP32 on COM9 was flashed. The current bench lacks DIP switches and pushbuttons, so use `--serial-demo`. The original GPIO map remains selectable for restored hardware.
- ESP32 RTU verified all eight input combinations, override and release, STOP priority and timeout of injected inputs. The gateway has 16 passing tests. CODESYS Control Win build generated with zero errors and warnings.
- Live Ubidots STEM telemetry and command 4 verified against COM9. The v2 last-values API returned the command and v1.6 accepted telemetry. CODESYS Control Win ran the test copy and read `GVL.ModbusOK = TRUE` and `GVL.SerialInputs = TRUE` with the ESP32 in STOP. The web dashboard remains blocked by HTTP 402. Never commit tokens, compiler caches or raw flash backups.

## RA2.3 baseline

Completed: final tank documentation published to the public repository and native GitHub Wiki. Both Home.md and Home-Tank-monitoring.md contain the final text.

Repository: https://github.com/Limao0521/industrial-iot-tank-monitoring
Wiki for delivery: https://github.com/Limao0521/industrial-iot-tank-monitoring/wiki/Home-Tank-monitoring

Verification: Wiki and repository HTTP 200; all six images load in the browser and match source SHA256 hashes. CODESYS source matches the desktop original; four OpenPLC project files match the final author archive. Author ZIP copied unchanged. STOP GPIO 16 and SystemActive GPIO 17 confirmed by saved mapping and screenshot.

Pending delivery action: author submits video file directly in Teams. A detailed electrical schematic is unavailable; the Wiki identifies the confirmed signal map as such.

Program logic and desktop originals were not modified. No new archives or hardware tests were generated.
