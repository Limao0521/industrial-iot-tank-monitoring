# Industrial IoT – Chemical Tank Level Monitoring

Proyecto RA2.3 de monitoreo de un tanque químico mediante tres sensores digitales, CODESYS HMI y OpenPLC con ESP32.

- [Wiki técnica recuperada](wiki/Home.md)
- [Entrega, criterios de evaluación y guía de video](docs/Entrega_RA2.3.md)
- [Lámina de referencia del ejercicio](references/RA2.3%20%281%29.pdf)
- [Rúbrica original](references/Rubricas_RA_2026-1v1.0%20%281%29.xlsx)

## Estado de preparación

La documentación está preparada localmente. La creación del repositorio público y de la Wiki nativa de GitHub sigue pendiente porque el acceso del navegador a GitHub fue rechazado por la política de permisos.

Los proyectos CODESYS y OpenPLC no están incluidos todavía: sus rutas originales dejaron de existir durante la revisión. Falta confirmar su ubicación actual para incorporarlos y preparar los dos ZIP de entrega.

La Wiki conserva el texto técnico recuperado, el placeholder del GPIO de STOP, las seis indicaciones para insertar figuras y el enlace de video pendiente. El final de la lista del video no pudo recuperarse del mensaje original, que se truncó desde «7. OpenPLC implemen…»; no se reconstruyó.

Las pruebas PASS del texto son las reportadas por el autor en la documentación anterior. No se ejecutaron pruebas nuevas de CODESYS, OpenPLC o hardware al preparar estos archivos.

La configuración OpenPLC leída al inicio asignaba STOP a GPIO 16 y SystemActive a GPIO 17. El dato se registra en la guía de entrega sin modificar el placeholder de la Wiki original.

## Archivos pendientes para entregar

1. ZIP del proyecto CODESYS editable.
2. ZIP del proyecto OpenPLC editable con configuración y pin mapping.
3. URL de la Wiki publicada, con figuras, esquema eléctrico y referencias completadas.
4. Video de diez minutos que muestre la simulación y el prototipo funcionando.

Consultar la guía de entrega para distinguir los requisitos del PDF, los de la rúbrica y los del enunciado compartido.
