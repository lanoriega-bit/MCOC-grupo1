# EXT-5 — pendientes estructurales y barrera FE

Estado: `AUDITED_WITH_REVIEW_REQUIRED`. Geometría conservada; OpenSees no ejecutado.

42 casos heredados y 43 geometrías flotantes. El caso adicional es **E2-P4-V-009**; ahora se incluye en el diagnóstico Unity. No se redujo artificialmente el conteo.

## Agrupación

| Edificio | Piso | Tipo | Causa | Cantidad |
|---|---|---|---|---:|
| EDIFICIO_1 | P1 | beam | ED1_OUTBOARD_BEAM_SUPPORT_REVIEW | 3 |
| EDIFICIO_1 | P1 | column | EXTERIOR_STAIR_SUPPORT_FE_SCOPE | 2 |
| EDIFICIO_1 | P1 | wall | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2 |
| EDIFICIO_1 | P1 | wall | WALL_SUPPORT_PATH_REVIEW | 11 |
| EDIFICIO_1 | P2 | beam | CONFIRMED_LANDING_BEAM_FE_SCOPE | 2 |
| EDIFICIO_1 | P2 | wall | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 6 |
| EDIFICIO_1 | P3 | wall | WALL_SUPPORT_PATH_REVIEW | 6 |
| EDIFICIO_1 | P4 | wall | WALL_SUPPORT_PATH_REVIEW | 6 |
| EDIFICIO_2 | P4 | beam | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 5 |

## Hallazgos

- 8 muros residuales tienen solape físico con muros de pisos vecinos que la intersección exacta de ejes no reconoce. Esto es pista de adaptador, no autorización para unir todos sus nodos.
- C-016/C-017 y V-055/V-075 conservan su evidencia de escalera B y su revisión de participación FE; no desaparecen por la omisión externa.
- 19 alturas pendientes: el JSON enumera cada viga y sus tres etiquetas de sección más cercanas. La asociación por proximidad no se promueve a confirmación.
- Se releen 60 DXF originales: 15581 textos y 0 notas candidatas de material. Se guardan hoja, handle, layer y posición; falta delimitar el alcance resistente de cada nota.
- Losas ED1 S1/P1 y huecos interiores mantienen las decisiones EXT-4: no existe en esta revisión evidencia nueva para completar superficies.

## Barrera antes de FE-1

- 424 nodos esclavos tienen más de un maestro en las restricciones propuestas.
- 376 nodos aparecen tanto retenidos como restringidos; 536 aristas son redundantes en el grafo de restricciones.
- La documentación de [Transformation](https://opensees.berkeley.edu/wiki/index.php/Transformation_Method) advierte contra cadenas de nodos retenidos/restringidos. Estas incidencias necesitan formulación y validación mecánica antes de una corrida.
- El candidato sigue en 856 miembros, 16 relaciones 1:N y 43 flotantes/22 componentes. No es un modelo resistente validado; no se crea POST_P1L4_ANALYSIS_MODEL ni resultados CURRENT todavía.

## Revisión elemento por elemento

| ID | Causa | Fuente primaria | Acción |
|---|---|---|---|
| E1-P1-C-016 | EXTERIOR_STAIR_SUPPORT_FE_SCOPE | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-C-017 | EXTERIOR_STAIR_SUPPORT_FE_SCOPE | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-004 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-010 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-016 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-020 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-021 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-022 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-023 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-024 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-031 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-034 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-035 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-036 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-M-037 | WALL_SUPPORT_PATH_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-V-068 | ED1_OUTBOARD_BEAM_SUPPORT_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-V-072 | ED1_OUTBOARD_BEAM_SUPPORT_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P1-V-098 | ED1_OUTBOARD_BEAM_SUPPORT_REVIEW | 2017_67-101.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-003 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-005 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-007 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-008 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-009 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-M-010 | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-V-055 | CONFIRMED_LANDING_BEAM_FE_SCOPE | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P2-V-075 | CONFIRMED_LANDING_BEAM_FE_SCOPE | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-003 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-005 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-007 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-008 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-009 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P3-M-010 | WALL_SUPPORT_PATH_REVIEW | 2017_67-102.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-003 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-007 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-008 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-009 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-010 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E1-P4-M-012 | WALL_SUPPORT_PATH_REVIEW | 2017_67-103.dxf | Conservar; revisar conexión/alcance FE |
| E2-P4-V-004 | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 2024_22-102.dxf | Conservar; revisar conexión/alcance FE |
| E2-P4-V-005 | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 2024_22-102.dxf | Conservar; revisar conexión/alcance FE |
| E2-P4-V-006 | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 2024_22-102.dxf | Conservar; revisar conexión/alcance FE |
| E2-P4-V-007 | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 2024_22-102.dxf | Conservar; revisar conexión/alcance FE |
| E2-P4-V-009 | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 2024_22-102.dxf | Conservar; revisar conexión/alcance FE |

## Alcance de la evidencia

Las comparaciones externas son las de EXT-1/2/3 fijadas por commit. No se modificaron ni se usaron para rellenar propiedades. La relectura textual de DXF no sustituye una inspección completa de cada detalle: las notas materiales y asociaciones siguen pendientes cuando su alcance no es inequívoco.
