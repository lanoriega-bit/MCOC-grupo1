# FASE 5 — diagnóstico de topología de losas

Estado: `DIAGNOSTIC_COMPLETE_NO_SURFACE_CHANGE`

Los conteos provienen directamente de `RLE-LOSA/RLE-LOSAS`. Los lazos cerrados no se consideran huecos automáticamente y los extremos abiertos no se rellenan en este paso.

La lámina 2024_22-101 declara una planta común desde cielo S1 hasta cielo P3; por eso esos cuatro niveles comparten 22 segmentos directos. Los 25 del JSON derivado incluyen tres trazos de detalle fuera de la región aprobada y no se usan.

| Edificio | Piso | Segmentos | Extremos abiertos | Lazos crudos | Componentes | Área bbox provisional |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| EDIFICIO_1 | S1 | 8 | 4 | 1 | 3 | 1073.172 m² |
| EDIFICIO_1 | P1 | 25 | 26 | 1 | 14 | 2384.193 m² |
| EDIFICIO_1 | P2 | 19 | 22 | 1 | 12 | 1664.285 m² |
| EDIFICIO_1 | P3 | 22 | 19 | 1 | 10 | 1799.578 m² |
| EDIFICIO_1 | P4 | 50 | 37 | 2 | 20 | 1802.479 m² |
| EDIFICIO_2 | S1 | 22 | 22 | 0 | 11 | 964.425 m² |
| EDIFICIO_2 | P1 | 22 | 22 | 0 | 11 | 964.425 m² |
| EDIFICIO_2 | P2 | 22 | 22 | 0 | 11 | 964.425 m² |
| EDIFICIO_2 | P3 | 22 | 22 | 0 | 11 | 964.425 m² |
| EDIFICIO_2 | P4 | 28 | 26 | 0 | 13 | 951.900 m² |

Los cierres automáticos solo colineales no reconstruyen el perímetro principal: se necesita evidencia adicional de vigas y notas en esquinas/cambios de nivel.

Siguiente paso: clasificar perímetro exterior, huecos reales y cierres respaldados por vigas/notas para cada piso. No se modificó FE ni el modelo combinado.
