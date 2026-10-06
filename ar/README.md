# AR — organización, sin intervención funcional

AR está fuera del alcance funcional de esta etapa. No ejecutar pruebas AR,
abrir escenas AR, regenerar datasets, comparar resultados ni integrar nuevas funciones.

## Ubicaciones

- `data/`: productores existentes, sin ejecución en esta etapa.
- `transforms/`: matemática y consultas existentes.
- `tests/`: validadores existentes, no ejecutados en esta etapa.
- `tracking/`: documentación de runtime.
- `viewer/unity/Assets/AR`, `Assets/Scripts/P1L6AR` y escenas AR: assets ligados
  al proyecto Unity y sus GUID. Se trasladan con el proyecto, conservando código,
  datos y `.meta`, sin cambiar tracking, anchors, transforms ni comportamiento.
- Suites Unity AR: `viewer/unity/Tests/AR*`, conservadas sin ejecutarlas.

No se certifica funcionalidad AR en este checkpoint. El pipeline desktop no debe
invocar módulos AR. Las evidencias anteriores son históricas, no pruebas de esta etapa.
