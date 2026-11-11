# Gemelo digital del tanque RA2.3

El ESP32 de RA2.3 calcula el estado y conserva los GPIO originales. En el banco disponible, los DIP y los pulsadores se emulan con mensajes Modbus por USB. CODESYS lee la misma imagen de proceso que se publica a Ubidots. El mando remoto cambia la combinación efectiva usada por el ESP32.

## Arranque en Windows

1. Conecta el ESP32 por USB. Verifica el puerto en el Administrador de dispositivos o con `arduino-cli board list`. Durante la integración apareció como `COM9`.
2. Carga [TankTwin.ino](firmware/TankTwin/TankTwin.ino) para `esp32:esp32:esp32` con Arduino IDE o CLI. El montaje mantiene los pines de [RA2.3](../openplc/devices/pin-mapping.json) y el nivel lógico directo del HAL original. Deja libre el puerto serie durante la ejecución del puente.
3. Instala la dependencia del puente y arráncalo desde esta carpeta. Usa `--serial-demo` para el banco disponible. Con los interruptores y pulsadores de RA2.3 conectados y verificados, `--physical-inputs` selecciona los GPIO.

   ```powershell
   python -m pip install -r gateway/requirements.txt
   python gateway/tank_gateway.py --port COM9 --serial-demo
   ```

4. Abre [TankTwin.project](codesys/TankTwin.project) en CODESYS V3.5 SP22 Patch 3. Arranca el runtime local **CODESYS Control Win V3 x64**, selecciona el dispositivo local, descarga la aplicación, arráncala y abre **Visualization** en línea. El cliente de lectura Modbus TCP ya apunta a `127.0.0.1:1502` y usa ModbusFB 4.5.0.0.
5. Para publicar y habilitar la recepción de órdenes, cierra el puente anterior con Ctrl+C y arranca el siguiente comando. Introduce el token de la cuenta Ubidots en el prompt oculto.

   ```powershell
   python gateway/tank_gateway.py --port COM9 --serial-demo --ubidots --enable-remote
   ```

## Tablero Ubidots

- El puente crea o actualiza el dispositivo `tanque-ra23` con `estado-tanque`, `entradas-fuente`, `entradas-efectivas`, `sistema-activo`, `mando-activo`, `mando-habilitado`, `entradas-serial` y `enlace-modbus`. Un enlace en 0 indica que las demás métricas conservan su último valor histórico.
- Crea una variable **raw** con etiqueta API `comando-nivel`. En el tablero, enlaza un **Manual Input** a esa variable o configura un **Slider** con cinco pasos. Añade métricas de último valor para estado, enlace y mando activo. Usa un gráfico temporal para comparar entradas físicas y efectivas.
- Activa START y mantenlo durante dos segundos. En la consola de prueba, `110 1 0` deja B1 y B2 en 1, START activo y STOP liberado. Con el permiso activo, envía un comando nuevo. `110 0 0` libera START, `110 0 1` aplica STOP y `q` cierra el puente. Si se pierden los mensajes de prueba durante cinco segundos, el ESP32 borra las entradas emuladas y apaga las salidas. Una orden remota caduca a los 30 segundos.

| Comando | Acción | B1 B2 B3 efectivos |
|---:|---|:---:|
| 0 | Volver a la entrada de origen | Según GPIO o consola |
| 1 | Vacío | 000 |
| 2 | Bajo | 100 |
| 3 | Correcto | 110 |
| 4 | Alto | 111 |

Los códigos de **estado** corresponden a las lámparas H1–H5 y tienen un mapa distinto al de **comando**. Consulta el contrato y la validación en la [wiki del gemelo](https://github.com/Limao0521/industrial-iot-tank-monitoring/wiki/Gemelo-digital-del-tanque-RA2.3). Para reproducir la HMI desde el original, ejecuta [build_project.py](codesys/build_project.py) desde la consola de scripting de CODESYS con el repositorio completo.
