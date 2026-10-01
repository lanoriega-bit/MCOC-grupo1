# Auditoría vertical de muros CURRENT — antes de corregir

54 muros activos; 15 líneas geométricas distintas. Coincidencia vertical estricta: endpoints ≤0,02 m y espesor ≤0,001 m. Las ausencias no se consideran terminaciones válidas sin respaldo primario.

## Controles de ejes originales

Los 15 ejes se releyeron por handle y se verificaron contra el hash DXF. ED1 S1/P2/P3/P4 muestran un error sistemático de origen de 0,1813 m; P1 está correctamente referido al eje 1. El registro de los muros debe corregirse desde ese control primario, no por copiar posiciones externas. Esta auditoría no autoriza desplazar las vigas/columnas de todo ED1.

| Línea | Edificio | S1 | P1 | P2 | P3 | P4 | Estado |
|---|---|---|---|---|---|---|---|
| WALL_LINE_001 | EDIFICIO_2 | E2-S1-M-001 | E2-P1-M-001 | E2-P2-M-001 | E2-P3-M-001 | E2-P4-M-001 | CONTINUOUS |
| WALL_LINE_002 | EDIFICIO_2 | E2-S1-M-002 | E2-P1-M-002 | E2-P2-M-002 | E2-P3-M-002 | E2-P4-M-002 | CONTINUOUS |
| WALL_LINE_003 | EDIFICIO_2 | E2-S1-M-003 | E2-P1-M-003 | E2-P2-M-003 | E2-P3-M-003 | E2-P4-M-003 | CONTINUOUS |
| WALL_LINE_004 | EDIFICIO_2 | E2-S1-M-004 | E2-P1-M-004 | E2-P2-M-004 | E2-P3-M-004 | E2-P4-M-004 | CONTINUOUS |
| WALL_LINE_005 | EDIFICIO_2 | E2-S1-M-005 | E2-P1-M-005 | E2-P2-M-005 | E2-P3-M-005 | E2-P4-M-005 | CONTINUOUS |
| WALL_LINE_006 | EDIFICIO_2 | E2-S1-M-006 | E2-P1-M-006 | E2-P2-M-006 | E2-P3-M-006 | E2-P4-M-006 | CONTINUOUS |
| WALL_LINE_007 | EDIFICIO_1 | E1-S1-M-026 | — | — | — | — | REVIEW_REQUIRED |
| WALL_LINE_008 | EDIFICIO_1 | E1-S1-M-029 | — | — | — | — | REVIEW_REQUIRED |
| WALL_LINE_009 | EDIFICIO_2 | E2-S1-M-007 | E2-P1-M-007 | E2-P2-M-007 | E2-P3-M-007 | — | REVIEW_REQUIRED |
| WALL_LINE_010 | EDIFICIO_2 | E2-S1-M-008 | E2-P1-M-008 | E2-P2-M-008 | E2-P3-M-008 | — | REVIEW_REQUIRED |
| WALL_LINE_011 | EDIFICIO_2 | E2-S1-M-010 | E2-P1-M-010 | E2-P2-M-010 | E2-P3-M-010 | — | REVIEW_REQUIRED |
| WALL_LINE_012 | EDIFICIO_2 | E2-S1-M-011 | E2-P1-M-011 | E2-P2-M-011 | E2-P3-M-011 | — | REVIEW_REQUIRED |
| WALL_LINE_013 | EDIFICIO_2 | E2-S1-M-009 | E2-P1-M-009 | E2-P2-M-009 | E2-P3-M-009 | — | REVIEW_REQUIRED |
| WALL_LINE_014 | EDIFICIO_1 | E1-S1-M-005 | — | — | — | — | REVIEW_REQUIRED |
| WALL_LINE_015 | EDIFICIO_1 | E1-S1-M-049 | — | — | — | — | REVIEW_REQUIRED |

## Núcleos identificados

| Grupo | Piso | IDs (ala / fondo / ala) | Activos antes | Fuente |
|---|---|---|---:|---|
| CORE_C_ED1_01 | S1 | E1-S1-M-020, E1-S1-M-026, E1-S1-M-034 | 1/3 | 2017_67-101.dxf |
| CORE_C_ED1_01 | P1 | E1-P1-M-012, E1-P1-M-004, E1-P1-M-025 | 0/3 | 2017_67-101.dxf |
| CORE_C_ED1_01 | P2 | E1-P2-M-010, E1-P2-M-007, E1-P2-M-009 | 0/3 | 2017_67-102.dxf |
| CORE_C_ED1_01 | P3 | E1-P3-M-010, E1-P3-M-007, E1-P3-M-009 | 0/3 | 2017_67-102.dxf |
| CORE_C_ED1_01 | P4 | E1-P4-M-009, E1-P4-M-007, E1-P4-M-010 | 0/3 | 2017_67-103.dxf |
| CORE_C_ED1_02 | S1 | E1-S1-M-005, E1-S1-M-029, E1-S1-M-049 | 3/3 | 2017_67-101.dxf |
| CORE_C_ED1_02 | P1 | E1-P1-M-002, E1-P1-M-010, E1-P1-M-026 | 0/3 | 2017_67-101.dxf |
| CORE_C_ED1_02 | P2 | E1-P2-M-003, E1-P2-M-008, E1-P2-M-005 | 0/3 | 2017_67-102.dxf |
| CORE_C_ED1_02 | P3 | E1-P3-M-003, E1-P3-M-008, E1-P3-M-005 | 0/3 | 2017_67-102.dxf |
| CORE_C_ED1_02 | P4 | E1-P4-M-003, E1-P4-M-008, E1-P4-M-012 | 0/3 | 2017_67-103.dxf |
| CORE_C_ED2_01 | S1 | E2-S1-M-007, E2-S1-M-008, E2-S1-M-010 | 3/3 | 2024_22-101.dxf |
| CORE_C_ED2_01 | P1 | E2-P1-M-007, E2-P1-M-008, E2-P1-M-010 | 3/3 | 2024_22-101.dxf |
| CORE_C_ED2_01 | P2 | E2-P2-M-007, E2-P2-M-008, E2-P2-M-010 | 3/3 | 2024_22-101.dxf |
| CORE_C_ED2_01 | P3 | E2-P3-M-007, E2-P3-M-008, E2-P3-M-010 | 3/3 | 2024_22-101.dxf |
| CORE_C_ED2_01 | P4 | E2-P4-M-007, E2-P4-M-008, E2-P4-M-009 | 0/3 | 2024_22-102.dxf |

Se identifican **tres** grupos en C: dos en ED1 y uno en ED2. ED1_01 conserva solo el fondo S1; ED1_02 conserva sus tres lados únicamente en S1; ED2 conserva la C S1–P3 y falta en P4. Sus paños son elementos independientes, no una sección C monolítica.

El tramo E2-S1/P1/P2/P3-M-009 no tiene equivalente P4 en la auditoría de caras de 2024_22-102: no se prolonga automáticamente. El muro largo X=27,727 m coincide con CAD y externos; no hay prueba para reflejarlo al lado opuesto. El usuario resolvió seguir el CAD únicamente para este caso: se conserva X=27,727 m, sin reflejar ni inventar un traslado.

## Columnas P4

Ambas líneas tienen XY idéntico en los cinco pisos y sección 70×70 cm de S1 a P3. P4 conserva 20×20 cm por una antigua asignación de etiqueta. La corrección solicitada reutiliza la sección existente de P3, mantiene el material/ID/altura y registra el antes/después.
