# Sustentación de cinco minutos

Ten abiertos la wiki, la HMI en línea, la consola de prueba USB y el tablero privado. Deja STOP liberado, B1–B3 en 000 y el puente conectado. Ensaya la secuencia en el montaje antes de exponer.

| Tiempo | Guion y acción |
|---|---|
| 0:00–0:40 | «En RA2.3 construimos un banco de nivel discreto. Los interruptores representaban tres sensores y cada LED correspondía a una condición. Para esta prueba, el mismo ESP32 recibe las entradas de prueba por USB.» Muestra la foto de RA2.3 y el banco actual. |
| 0:40–1:30 | «El ESP32 calcula una sola imagen de proceso. El PC la lee por Modbus RTU vía USB. CODESYS la consulta por Modbus TCP local y Ubidots recibe la telemetría por HTTPS.» Señala las tres rutas en el diagrama. |
| 1:30–2:40 | Envía `000 1 0` y después `110 0 0` en la consola. Señala H4 y después H1. Envía `010 0 0` para provocar H5 y vuelve a 110. |
| 2:40–4:15 | Envía `110 1 0`, espera dos segundos y envía **4** desde Ubidots. «La entrada de prueba conserva 110. La orden aplica 111 a la lógica y activa H3. El cambio vuelve a CODESYS y Ubidots como estado confirmado.» Envía `110 0 0` para volver a H1 y `110 0 1` para apagar las salidas. |
| 4:15–5:00 | Muestra los resultados de validación y explica que se ensaya un nivel emulado con LEDs. «La prueba demuestra telemetría y escritura con realimentación. El mando tiene permiso local, caduca y STOP conserva la prioridad.» |

Si una etapa sigue pendiente el día de la presentación, muéstrala como pendiente en la matriz y distingue la evidencia grabada de la demostración en vivo.
