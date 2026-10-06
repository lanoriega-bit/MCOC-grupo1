# QA del inspector y aislamiento CURRENT

2026-09-22. Unity 6000.6.0f1, Main, build Windows64; prueba runtime `--ux-review`.

Cobertura: viga E2-P4-V-009, columna E2-P1-C-001, muro E1-P4-M-007, losa visual,
pisos y edificio completo. Resoluciones 1366×768 y 1920×1080. Se comprueban
accordions por defecto, filtros, paneles sin solape, triadas geométricas,
históricos bloqueados sin opt-in, presentación y acceso explícito al archivo.
Los gráficos históricos My/N/P-M siguen siendo demostrables en ese modo.

Se detectaron y corrigieron dos problemas durante QA:

- Columnas sin endpoints: JsonUtility proporciona listas vacías. El visor debe
  construir la triada desde centro/altura, no abandonar la selección por vector cero.
- M.H.A. confirmado como tipo no certifica fc. El resumen del muro de P4 conserva
  «grado resistente por confirmar», aunque el tipo hormigón armado figure en CAD.

Pruebas numéricas de contrato: rechazo de versiones, unidades y estado histórico;
combinación firmada de cuatro bases sintéticas y rechazo de NaN. No son un nuevo
análisis del edificio. Las 752 asignaciones materiales son de fuente primaria;
los resultados actuales permanecen ausentes.

Evidencia final: `../qa/current_readiness_UX_QA.txt`,
`../qa/current_inspector_beam.png`, `../qa/current_inspector_column.png`,
`../qa/current_inspector_wall.png`, `../global_validation.json`.
Las capturas se revisan visualmente, no sólo por existencia de archivos.

La habilidad computer-use se utiliza para verificar y cerrar/abrir la ventana
real del Editor. La ejecución automatizada complementa, no reemplaza esa revisión.
Ningún PASS de interfaz autoriza el FE, las cargas o una corrida CURRENT.
