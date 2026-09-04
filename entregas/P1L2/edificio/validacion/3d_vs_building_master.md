# Validacion 3D vs building_master

- Fuente 3D: `unity_export/model_viewer_candidate.json`
- Base logica: `building_master.json`

## Resultado global

- Entidades logicas modelables: **3071**
- MATCH: **3071**
- MISSING_IN_3D: **0**
- GEOMETRY_MISMATCH: **0**
- METADATA_MISMATCH: **0**
- EXTRA_IN_3D: **0** (sin contar slab fill)
- Slab fill (referencia visual): **45**
- EXTRA ejes en 3D: **0**

## Desglose por tipo / estado

| Tipo | MATCH | MISSING | GEOMETRY | METADATA |
|---|---|---|---|---|
| columna | 139 | 0 | 0 | 0 |
| viga | 1241 | 0 | 0 | 0 |
| muro | 600 | 0 | 0 | 0 |
| perimetro_losa | 382 | 0 | 0 | 0 |
| fundacion | 314 | 0 | 0 | 0 |
| eje_grafico | 395 | 0 | 0 | 0 |

## Elementos con problema (no MATCH)

Ninguno.

## Conteos 3D por piso (solids)

| Piso       |   Col |   Viga |  Muro |  LosaBorde |  Fund | SlabFill |
|---|---|---|---|---|---|---|
| base       |    14 |    169 |   210 |         21 |   314 |        3 |
| 1S         |     8 |    177 |   136 |         56 |     0 |        5 |
| 1          |    28 |    195 |    86 |         64 |     0 |        6 |
| 2          |    29 |    205 |    61 |         66 |     0 |        6 |
| 3          |    26 |    213 |    61 |         70 |     0 |        6 |
| 4          |    34 |    282 |    46 |        105 |     0 |       19 |

## Notas
- Vigas modeladas con seccion confirmada V.60/80 (0.60 x 0.80 m); el default de linea en building_master (0.32) no se usa para la seccion estructural.
- Muros con espesor 0.22 m (datos master); las etiquetas M.H.A. del DXF indican e=15/20/25/30 (refinamiento pendiente por muro).
- Fundaciones como tiras de apoyo nominales (NEEDS_REVIEW).
- Relleno de losa (slab fill) = caja envolvente de cada bucle cerrado de bordes; aproximacion visual, relleno poligonal real pendiente.
