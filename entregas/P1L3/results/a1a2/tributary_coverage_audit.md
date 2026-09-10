# Auditoria de cobertura tributaria

Estado: **REVIEW_REQUIRED**. Este informe no modifica cargas ni geometria.

## Diagnostico por edificio y piso

| Edificio | Piso | Vigas H/V | Muros H/V | Area grilla [m2] | Solo vigas [m2] | + muros [m2] | Historica [m2] | Actual/historica |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| EDIFICIO_1 | S1 | 24/55 | 32/28 | 568.595 | 82.268 | 221.700 | 1145.088 | 0.0718 |
| EDIFICIO_1 | P1 | 55/51 | 16/22 | 1076.090 | 588.659 | 594.950 | 1829.364 | 0.3218 |
| EDIFICIO_1 | P2 | 57/55 | 4/8 | 913.542 | 702.374 | 702.374 | 919.252 | 0.7641 |
| EDIFICIO_1 | P3 | 65/59 | 4/8 | 1007.586 | 762.038 | 762.038 | 732.410 | 1.0405 |
| EDIFICIO_1 | P4 | 67/55 | 4/8 | 1007.960 | 801.281 | 801.281 | 1018.575 | 0.7867 |
| EDIFICIO_2 | S1 | 51/39 | 10/10 | 422.205 | 91.264 | 91.264 | 584.230 | 0.1562 |
| EDIFICIO_2 | P1 | 51/39 | 10/10 | 422.205 | 91.264 | 91.264 | 584.230 | 0.1562 |
| EDIFICIO_2 | P2 | 51/39 | 10/10 | 422.205 | 91.264 | 91.264 | 584.230 | 0.1562 |
| EDIFICIO_2 | P3 | 51/39 | 10/10 | 422.205 | 91.264 | 91.264 | 584.230 | 0.1562 |
| EDIFICIO_2 | P4 | 96/59 | 10/10 | 420.890 | 90.949 | 90.949 | 584.230 | 0.1557 |

## Sensibilidad de tolerancias

| Tolerancia viga [m] | Cobertura minima | Panos | Area [m2] | Excluidas |
| ---: | ---: | ---: | ---: | ---: |
| 0.35 | 0.30 | 110 | 3392.624 | 222 |
| 0.35 | 0.50 | 110 | 3392.624 | 222 |
| 0.35 | 0.70 | 98 | 3217.889 | 234 |
| 0.35 | 0.90 | 21 | 1008.951 | 311 |
| 0.50 | 0.30 | 110 | 3392.624 | 222 |
| 0.50 | 0.50 | 110 | 3392.624 | 222 |
| 0.50 | 0.70 | 98 | 3217.889 | 234 |
| 0.50 | 0.90 | 22 | 1053.000 | 310 |
| 0.70 | 0.30 | 110 | 3392.624 | 222 |
| 0.70 | 0.50 | 110 | 3392.624 | 222 |
| 0.70 | 0.70 | 98 | 3217.889 | 234 |
| 0.70 | 0.90 | 22 | 1053.000 | 310 |

Los detalles de las mayores celdas excluidas y el borde responsable quedan en `tributary_coverage_audit.json`.

## Capas historicas de transferencia contra CAD

`areas` es la etapa losa->vigas y `point_areas` la etapa hacia muros/columnas. Representan la misma carga y nunca se suman.

| Dataset | Edificio | Piso | Area declarada | Union poligonos | Entradas con diferencia | Sin poligono [m2] | Borde CAD cerca 0,60 m |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| areas | EDIFICIO_1 | S1 | 1145.088 | 986.024 | 47 | 0.493 | 0.1409 |
| areas | EDIFICIO_1 | P1 | 1829.364 | 1477.133 | 107 | 17.399 | 0.5547 |
| areas | EDIFICIO_1 | P2 | 919.252 | 647.862 | 101 | 13.551 | 0.3660 |
| areas | EDIFICIO_1 | P3 | 732.410 | 515.479 | 73 | 8.551 | 0.0511 |
| areas | EDIFICIO_1 | P4 | 1018.576 | 722.320 | 101 | 16.645 | 0.4651 |
| areas | EDIFICIO_2 | S1 | 584.231 | 378.675 | 90 | 7.895 | 0.9075 |
| areas | EDIFICIO_2 | P1 | 584.231 | 378.675 | 90 | 7.895 | 0.8358 |
| areas | EDIFICIO_2 | P2 | 584.231 | 378.675 | 90 | 7.895 | 0.8358 |
| areas | EDIFICIO_2 | P3 | 584.231 | 378.675 | 90 | 7.895 | 0.8358 |
| areas | EDIFICIO_2 | P4 | 584.231 | 346.396 | 154 | 17.023 | 0.8459 |
| point_areas | EDIFICIO_1 | S1 | 1145.088 | 963.594 | 64 | 5.428 | 0.2668 |
| point_areas | EDIFICIO_1 | P1 | 1829.364 | 1599.180 | 61 | 3.728 | 0.5557 |
| point_areas | EDIFICIO_1 | P2 | 919.252 | 777.040 | 32 | 0.000 | 0.4761 |
| point_areas | EDIFICIO_1 | P3 | 732.410 | 609.399 | 29 | 0.000 | 0.2367 |
| point_areas | EDIFICIO_1 | P4 | 1018.575 | 849.269 | 38 | 0.000 | 0.2779 |
| point_areas | EDIFICIO_2 | S1 | 584.230 | 497.212 | 24 | 7.155 | 0.8764 |
| point_areas | EDIFICIO_2 | P1 | 584.230 | 497.212 | 24 | 7.155 | 0.7878 |
| point_areas | EDIFICIO_2 | P2 | 584.230 | 497.212 | 24 | 7.155 | 0.7878 |
| point_areas | EDIFICIO_2 | P3 | 584.230 | 497.212 | 24 | 7.155 | 0.7878 |
| point_areas | EDIFICIO_2 | P4 | 584.230 | 496.816 | 24 | 7.155 | 0.6840 |

Los `polygon` historicos son geometria de visualizacion incompleta: en muchas entradas su area no coincide con `area_m2`, que acumula la transferencia. El repositorio no conserva el algoritmo que genero esa discretizacion. Por eso el area historica solo se usa como contraste y la huella debe reconstruirse desde los planos y `RLE-LOSA` antes de adoptarla como fuente final.
