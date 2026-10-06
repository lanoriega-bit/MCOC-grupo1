# PRE5-REVIEW-2 — integración visual de pendientes

Fecha: 2026-09-22. Resultado: **PASS** para la herramienta de revisión.
No significa que los 43 encuentros estén resueltos ni aprueba el FE candidato.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Compilación Windows canónica | PASS | `CurrentReviewBuild.Build`, `[CURRENT BUILD] PASS` |
| Expediente vinculado a geometría vigente | PASS | hash de geometría y 43 IDs en `dossier_qa.json` |
| Selección de los 43 IDs en Play | PASS | bucle de `ViewerReviewQA.RunUxReview` |
| Vecinos aislados / sin fuga del resto del modelo | PASS | comprobación de cada objeto activo para cada caso |
| Ejes estructurales del edificio seleccionado | PASS | mínimo cuatro líneas por caso; coordenadas del contrato canónico |
| Núcleo, escalera B y outboard ED2 | PASS | capturas tras actualizar cámara en 1366×768 y 1920×1080 |
| Etiquetas legibles sin invadir el inspector | PASS | ajuste de posición y separación de etiquetas; revisión visual |
| Reset R restaura el modelo completo | PASS | aislamiento y grilla eliminados por `ResetPresentation` |
| Resultados históricos no activados automáticamente | PASS | pruebas previas de aislamiento de datasets y modo presentación |
| Regresión general | PASS | 12 scripts y controles de tags/referencias en `../GLOBAL_VALIDATION.md` |
| Geometría y candidato inalterados | PASS | regeneración temporal, comparación de siete campos topológicos y SHA-256 |

Capturas de la compilación final: `pending_core_1366.png`, `pending_stair_1366.png`,
`pending_outboard_1920.png`. El player conserva la secuencia completa en su carpeta
local `Builds/CurrentReview/QA`, que no se versiona. Los logs locales no se publican.

Se verificó el CSV mediante la tabla de 43 registros/33 campos y lectura independiente.
`csv_preview.png` es únicamente la comprobación de los campos de identificación;
CSV no conserva estilos y las fichas Markdown son la vista de lectura detallada.

Límites: no se han leído nuevos detalles resistentes inequívocos para aprobar las
uniones; ejes y/z FE siguen NO SABEMOS; matching externo no demuestra conectividad;
las geometrías vecinas visibles no son automáticamente receptores. Estado de
consolidación general: PRE_P1L5_BASELINE BLOCKED, sin cambios respecto a este hito.
