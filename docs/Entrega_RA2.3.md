# Entrega RA2.3: monitoreo del tanque químico

## Qué entregar

La lista de archivos proviene del enunciado de la actividad que compartiste en la conversación «Diseño HMI y OpenPLC». El PDF adjunto tiene una sola página y presenta el problema técnico; no contiene las instrucciones de envío.

1. **ZIP del proyecto CODESYS:** proyecto editable, Ladder, variables, Visualization/HMI y lógica de inicio y parada.
2. **ZIP del proyecto OpenPLC:** proyecto editable, Ladder, configuración del controlador ESP32 y mapeo de entradas y salidas.
3. **URL de la Wiki en GitHub o Bitbucket:** explicación del diseño lógico, tabla de verdad, ecuaciones, Ladder, HMI, esquema eléctrico, implementación, pruebas, resultados, conclusiones y referencias.
4. **Video de diez minutos:** demuestra CODESYS y OpenPLC con hardware real. Según el enunciado compartido, se entrega en la actividad de Teams o mediante enlace de YouTube y debe poder reproducirse desde Teams. Recomiendo no superar diez minutos.

El enunciado compartido establece trabajo **individual**. El repositorio ayuda a organizar la entrega, pero no sustituye los ZIP, el video y la URL que deben adjuntarse en la actividad.

## Requisitos técnicos del PDF

Fuente: `RA2.3 (1).pdf`, página 1, «PLC – Programming – Ladder Logic (LD)».

| B1 | B2 | B3 | Estado | Indicador |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | Tanque vacío | H4 |
| 1 | 0 | 0 | Nivel bajo | H2 |
| 1 | 1 | 0 | Nivel correcto | H1 |
| 1 | 1 | 1 | Nivel alto | H3 |
| 0 | 0 | 1 | Sensores incoherentes | H5 |
| 0 | 1 | 0 | Sensores incoherentes | H5 |
| 0 | 1 | 1 | Sensores incoherentes | H5 |
| 1 | 0 | 1 | Sensores incoherentes | H5 |

La figura muestra los cuatro estados válidos. La advertencia exige encender H5 cuando las señales de sensores no tienen sentido físico y excluye expresamente `000` de los errores. Las cuatro filas de error de la tabla se deducen de esa advertencia y de la ubicación vertical de los sensores.

La pregunta guía relaciona el monitoreo con la reducción del consumo de energía y del desperdicio de líquido. Conviene explicar cómo detectar nivel alto o bajo permite apoyar decisiones operativas. No afirmar ahorros medidos si no se midieron ni control automático de bomba si no se implementó.

## Qué evalúa la rúbrica

Fuente: `Rubricas_RA_2026-1v1.0 (1).xlsx`, hoja `Team_1`.

| Grupo | Peso | Evidencia esperada | Ubicación |
|---|---:|---|---|
| Diseño y validación de ingeniería | 60 % | Diseño CODESYS, simulación, diseño OpenPLC y prototipo funcional | B5; E5:I11 |
| Comunicación | 30 % | Presentación oral y documento Wiki | B13; D13:I15 |
| Aprendizaje | 10 % | Apropiación del conocimiento y contribución al trabajo | B17; E17:I19 |

### Diseño y simulación CODESYS

- Ladder documentado y respuesta a todos los requisitos.
- HMI con todas las etapas y estados, cambios de colores, textos y etiquetas; aparición/desaparición de objetos cuando corresponda al diseño.
- HMI conectado a la lógica Ladder.
- Transiciones correctas y funcionamiento de indicadores, animaciones e interruptores de inicio y parada.
- Para el nivel experto: interfaz armónica, profesional y fácil de seguir; propuesta que aporte mejoras pertinentes.

Fuente: `Team_1!E5:I7`.

### OpenPLC y hardware

- Ladder documentado en OpenPLC y prototipo que represente todos los estados.
- Entradas físicas conectadas a la lógica y salidas que respondan correctamente.
- Sensores o entradas de prototipado, indicadores e interruptores de inicio y parada funcionando.
- Demostración clara y precisa de las transiciones y del diagnóstico de error.

Fuente: `Team_1!E9:I11`.

### Wiki y video

- Wiki completa, coherente, clara y sin errores ortográficos.
- Tablas y figuras pertinentes, legibles, con títulos y explicaciones.
- Referencias y citas según IEEE; la rúbrica pide que la mayoría sean de los últimos cinco años.
- Video claro y conciso, dominio del lenguaje técnico, ayudas visuales y capacidad de explicar y justificar el diseño.
- La competencia de comunicación menciona expresión en una segunda lengua, inglés; no fija en estas celdas que todo el video deba estar en inglés. La Wiki redactada está en inglés.

Fuente: `Team_1!D13:I15`.

### Criterios genéricos que conviene confirmar

La rúbrica menciona CODESYS con proceso controlado por tiempo (`E5`, `E7`), conteo de lotes (`H11`) y acta de reunión/rol dentro de equipo (`E19`, `I19`). El PDF del tanque describe monitoreo combinacional por sensores; no especifica temporizadores ni lotes. El enunciado compartido indica trabajo individual.

Estos puntos parecen proceder de una rúbrica general. Esa es una interpretación, no una exención confirmada: consultar al profesor cuáles aplican a RA2.3. No añadir funciones ajenas al ejercicio ni inventar actas de equipo para cubrirlos.

La nota de `I26` indica que la ausencia de entregable para un indicador implica calificación cero para ese indicador. Los valores de nota existentes en el archivo son una plantilla sin completar y no constituyen una calificación de este proyecto.

## Evidencia que falta completar en la Wiki recuperada

- [ ] Figura 1: captura del HMI CODESYS.
- [ ] Figura 2: captura Ladder OpenPLC.
- [ ] Figura 3: configuración de variables OpenPLC.
- [ ] Figura 4: pin mapping OpenPLC.
- [ ] Figura 5: fotografía del prototipo.
- [ ] Figura 6: esquema eléctrico real.
- [ ] Capturas Ladder y simulación CODESYS y evidencias de las ocho pruebas.
- [ ] Enlace de video en `[ADD VIDEO LINK HERE]`.
- [ ] Revisar y completar las referencias IEEE con datos bibliográficos, enlaces y fechas.
- [ ] Recuperar el final original de la lista del video, truncado desde «7. OpenPLC implemen…» en la conversación disponible.

La configuración OpenPLC leída al comenzar la revisión asigna STOP a **GPIO 16** (`%IX0.4`) y `SystemActive` a GPIO 17 (`%QX0.5`). El placeholder `[GPIO USED FOR STOP]` se conserva en la Wiki por la instrucción de mantener el texto original; el dato del archivo no prueba por sí solo el cableado físico.

Las tablas PASS de la Wiki proceden del texto anterior y del funcionamiento reportado por el autor. Esta revisión documental no ejecutó CODESYS, OpenPLC ni pruebas físicas.

## Guía de video recomendada

| Tiempo | Contenido |
|---|---|
| 0:00–0:45 | Objetivo, tres sensores y cinco indicadores |
| 0:45–1:45 | Tabla de verdad, estados válidos e incoherentes |
| 1:45–3:15 | Ladder CODESYS, SystemActive, inicio/parada y H5 |
| 3:15–5:15 | HMI funcionando: 000, 100, 110, 111, errores e inicio/parada |
| 5:15–6:15 | Ladder OpenPLC, direcciones IEC y pin mapping |
| 6:15–8:45 | ESP32, DIP switch y LEDs; demostrar cambios físicos y respuestas |
| 8:45–9:30 | Comparación de resultados con la simulación y la tabla |
| 9:30–10:00 | Conclusiones y limitaciones del prototipo |

Esta distribución es una recomendación; no aparece como cronograma obligatorio en el PDF o la rúbrica.
