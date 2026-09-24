# Auditoría CAD de dilatación EDIFICIO_1

Estado: `PASS_WITH_SCOPE_LIMIT` — diagnóstico, sin cambio de modelo.

- La serie 2017_67 contiene `393` entidades en capas con `DILAT` y `22` textos relacionados.
- En S1, lámina 101, hay `4` entidades de `RLA-MURO DILATADO` que forman `1` contorno cerrado único.
- Contorno global: centro `(27.241, 7.531) m`, tamaño `0.200 x 2.360 m`.
- La dimensión transversal de 0.20 m y el contorno cerrado confirman un segmento local de muro ED1 rotulado `DILATADO`.
- Las entidades `RLA-MURO INV DILATADO` se conservan como gráficos de armadura separados; no se usan para agrandar el contorno.
- Esta evidencia no demuestra conexión física ni transferencia FE entre EDIFICIO_1 y EDIFICIO_2.
- Veredicto de interfaz: `NO_CROSS_BUILDING_FE_CONNECTION_PROVEN`.

Overlay: `entregas/P1L2/edificio/validacion/special_interface/s1_dilatation_wall_contour.png`

## Conteos por región de planta

| Lámina | Región | Capa | Entidades |
| --- | --- | --- | ---: |
| 2017_67-101.dxf | S1 | RLA-MURO DILATADO | 4 |
| 2017_67-101.dxf | S1 | RLA-MURO INV DILATADO | 104 |
| 2017_67-103.dxf | P4 | RLA-MURO INV DILATADO | 285 |
