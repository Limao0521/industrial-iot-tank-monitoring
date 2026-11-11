# Pruebas y entrega del gemelo digital RA2.3

## Antes de la demostración

1. Conecta por USB el ESP32 con el firmware del gemelo. En el banco de prueba aparece como `COM9`. Si el puente anterior sigue abierto, escribe `q` en esa consola o ciérrala antes de iniciar otra.
2. Desde la carpeta `digital-twin`, ejecuta en PowerShell:

   ```powershell
   python -m pip install -r gateway/requirements.txt
   python gateway/tank_gateway.py --port COM9 --serial-demo --ubidots --enable-remote
   ```

   Pega el token de Ubidots cuando la consola lo pida. La entrada es oculta. Espera una línea del ESP32 con `serial=1` y el mensaje «Ubidots recibió telemetría».
3. Abre **CODESYS Control Win V3 - x64 SysTray** desde Inicio. En el icono de CODESYS de la bandeja de Windows, elige **Iniciar autómata**. Abre [TankTwin.project](../codesys/TankTwin.project), selecciona el controlador **local** en la pestaña de comunicación de **Device** e inicia sesión con el administrador que creaste. Descarga la aplicación si CODESYS lo solicita, pulsa **F5** y abre **Visualization** en línea. El cliente de la HMI usa el puente en `127.0.0.1:1502`. [Manual de CODESYS](https://content.helpme-codesys.com/es/CODESYS%20Control/_rtsl_cmd_menu.html)

## Qué probar

Escribe cada línea por separado en la consola del puente y espera a que el ESP32 indique el cambio antes de enviar la siguiente. Los tres campos locales representan **B1B2B3**, **START** y **STOP**.

| Paso | Entrada en la consola | Resultado esperado |
|---|---|---|
| 1. Activar en vacío | `000 0 0` y después `000 1 0` | H4 encendido. Se activa el sistema con entradas de origen y efectivas en 000. |
| 2. Nivel correcto | `110 0 0` | H1 encendido. El ESP32 indica `fuente=3 efectivo=3 H=1`. El valor 3 codifica B1 y B2 activos. |
| 3. Inconsistencia | `010 0 0` | H5 encendido porque B2 está activo con B1 apagado. Vuelve a `110 0 0` antes de seguir. |
| 4. Autorizar el mando | `110 1 0` | Mantén START activo. Espera al menos dos segundos y confirma `permiso=1` en el registro. |
| 5. Mandar nivel alto por Ubidots | `iot 4` | Ubidots recibe la orden. Espera «Comando 4 confirmado por ESP32» y `fuente=3 efectivo=7 H=3 remoto=1`. El nivel efectivo pasó a 111 y el origen sigue en 110. |
| 6. Leer la respuesta desde Ubidots | `iot estado` | `comando-nivel=4`, `estado-tanque=3`, `entradas-fuente=3`, `entradas-efectivas=7`, `mando-activo=1`. Si ves el valor anterior, espera unos segundos y consulta otra vez mientras la orden siga activa. |
| 7. Retirar la orden y parar | `110 0 0` y después `110 0 1` | Al liberar START, vuelve H1. Con STOP, el ESP32 informa `activo=0 H=0 remoto=0` y la HMI apaga los estados. |

`iot 4` publica en la variable `comando-nivel` de Ubidots. El puente lee la orden desde la nube y se la pasa al ESP32 por Modbus RTU. `iot estado` consulta a Ubidots para mostrar el valor publicado de vuelta por el ESP32. Esta secuencia se puede usar mientras el tablero web muestre HTTP 402. Usa el [guion de cinco minutos](Sustentacion-5-min.md) para narrarla.

## Evidencia de la prueba realizada

- El ESP32 conectado en COM9 reportó `fuente=3 efectivo=3 H=1 serial=1`. Ubidots aceptó H1 con origen 110.
- La orden 4 se publicó en Ubidots y llegó a la placa. El ESP32 respondió `fuente=3 efectivo=7 H=3 remoto=1` y Ubidots aceptó la telemetría de retorno. STOP dejó `activo=0 H=0 remoto=0`.
- Con el ESP32 en STOP, CODESYS Control Win descargó y arrancó la aplicación de prueba. Leyó `GVL.ModbusOK = TRUE` y `GVL.SerialInputs = TRUE`. Durante la sustentación, usa los pasos de la tabla para mostrar las transiciones de la visualización.
- El hardware de RA2.3 usado fue el ESP32. Los DIP y pulsadores del banco actual se emularon por USB. El tablero web de Ubidots devolvió HTTP 402; el tráfico en ambos sentidos se comprobó con su API.

## Qué entregar

1. **Entrega principal:** pega el enlace de la [wiki técnica del gemelo](https://github.com/Limao0521/industrial-iot-tank-monitoring/wiki/Gemelo-digital-del-tanque-RA2.3). Incluye el diagrama, el mapa Modbus y la matriz de validación.
2. **Archivos reproducibles:** agrega el enlace de la [implementación en GitHub](https://github.com/Limao0521/industrial-iot-tank-monitoring/tree/main/digital-twin). Allí están el firmware, el puente y el proyecto CODESYS editable.
3. **Evidencia si la plataforma admite adjuntos:** graba la placa conectada, CODESYS en línea y la consola al pasar de H1 a H3 por Ubidots y luego a STOP. Si Teams pide video, súbelo como archivo allí. La consigna del gemelo pide una sustentación de cinco minutos y una wiki.

Texto para pegar en la entrega:

> Gemelo digital del tanque RA2.3. La wiki documenta diseño, implementación y validación del ESP32 con CODESYS por Modbus y con Ubidots STEM en ambos sentidos. El ESP32 recibe las entradas de prueba por USB. La orden de nivel alto se verificó en la placa y en la telemetría de retorno.
>
> Wiki: https://github.com/Limao0521/industrial-iot-tank-monitoring/wiki/Gemelo-digital-del-tanque-RA2.3
