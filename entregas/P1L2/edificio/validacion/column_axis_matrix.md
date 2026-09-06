# Matriz columnas-ejes-pisos

- Estado: **PASS_WITH_OFF_AXIS_NOTES**
- Columnas: 176
- Estaciones de columna: 42
- Tolerancia eje-columna: 0.35 m
- Redondeo de estacion: 0.05 m
- Columnas fuera de ejes canonicos: 31
- CSV: `entregas\P1L2\edificio\datos\column_axis_matrix.csv`

## Columnas por piso

| Piso | Columnas |
|---|---:|
| S1 | 33 |
| P1 | 40 |
| P2 | 37 |
| P3 | 32 |
| P4 | 34 |

## Columnas por edificio

| Edificio | Columnas |
|---|---:|
| EDIFICIO_1 | 136 |
| EDIFICIO_2 | 40 |

## Matriz

Celdas S1/P1/P2/P3/P4 indican cantidad de columnas en esa estacion. `OFF_AXIS_REFERENCE` significa que la columna se conserva, pero queda fuera de la tolerancia respecto de los ejes canonicos actualmente registrados.

| Edificio | X eje/ref | Y eje/ref | x [m] | y [m] | S1 | P1 | P2 | P3 | P4 | Estado | Clasificacion |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| EDIFICIO_2 | A | 2 | 0.00 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | B | 1 | 7.50 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | B | 2 | 7.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | B | 3 | 7.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | C | 1 | 17.50 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | C | 2 | 17.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | C | 3 | 17.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_2 | D/E | 1 | 27.45 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | D/E | 1 | 27.50 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | D/E | 2 | 27.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | D/E | 3 | 27.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | F | 1 | 37.50 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | F | 2 | 37.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | F | 3 | 37.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | F | Y=20.45 near 3 +4.30m | 37.50 | 20.45 |  | 1 | 1 |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | X=45.00 near G -2.51m | 3 | 45.00 | 16.35 | 1 | 1 | 1 |  |  | OFF_AXIS_REFERENCE | SPECIAL_POSITION_CONFIRMED |
| EDIFICIO_1 | X=45.00 near G -2.51m | Y=20.45 near 3 +4.30m | 45.00 | 20.45 |  | 1 | 1 |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | G | 1 | 47.50 | 0.00 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | G | 2 | 47.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | G | 3 | 47.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | G | Y=20.45 near 3 +4.30m | 47.50 | 20.45 |  |  | 1 |  | 1 | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H | 1 | 57.50 | 0.05 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | H | 2 | 57.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | H | 3 | 57.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | H | Y=18.85 near 3 +2.69m | 57.50 | 18.85 |  | 1 |  |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H | Y=20.45 near 3 +4.30m | 57.50 | 20.45 |  |  | 1 |  | 1 | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H | Y=26.20 near 3 +10.03m | 57.50 | 26.20 |  | 1 |  |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H' | Y=18.90 near 3 +2.76m | 61.95 | 18.90 |  | 1 |  |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H' | Y=23.60 near 3 +7.47m | 61.95 | 23.60 |  | 1 |  |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | H' | Y=28.35 near 3 +12.19m | 61.95 | 28.35 |  | 1 |  |  |  | OFF_AXIS_REFERENCE | OFF_AXIS_LEGITIMATE |
| EDIFICIO_1 | I | 2 | 67.40 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | I | 1 | 67.45 | 0.10 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | I | 3 | 67.65 | 16.35 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | I' | 1 | 72.50 | 0.05 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | I' | 2 | 72.50 | 8.90 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | I' | 3 | 72.50 | 16.15 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | X=75.05 near IB +1.68m | 1 | 75.05 | 0.20 | 1 | 1 | 1 | 1 | 1 | OFF_AXIS_REFERENCE | SPECIAL_POSITION_CONFIRMED |
| EDIFICIO_1 | X=75.05 near IB +1.68m | 2 | 75.05 | 9.10 | 1 | 1 | 1 | 1 | 1 | OFF_AXIS_REFERENCE | SPECIAL_POSITION_CONFIRMED |
| EDIFICIO_1 | X=75.05 near IB +1.68m | 3 | 75.05 | 16.35 | 1 | 1 | 1 | 1 | 1 | OFF_AXIS_REFERENCE | SPECIAL_POSITION_CONFIRMED |
| EDIFICIO_1 | J | 1 | 77.40 | 0.20 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | J | 2 | 77.40 | 9.10 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |
| EDIFICIO_1 | J | 3 | 77.40 | 16.35 | 1 | 1 | 1 | 1 | 1 | ON_AXIS | ON_CANONICAL_AXIS |

## Clasificacion off-axis

| Clasificacion | Columnas |
|---|---:|
| OFF_AXIS_LEGITIMATE | 13 |
| SPECIAL_POSITION_CONFIRMED | 18 |

## Notas fuera de eje

Las columnas fuera de eje no se eliminan ni se corrigen. Se reportan porque el set canonico de ejes todavia no contiene todos los posibles ejes secundarios de los planos.

| Tag | Edificio | Piso | x [m] | y [m] | X cercano | dx [m] | Y cercano | dy [m] | Clasificacion |
|---|---|---|---:|---:|---|---:|---|---:|---|
| SOL_1_column_0025 | EDIFICIO_1 | P1 | 37.491 | 20.452 | F | -0.000 | 3 | 4.302 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0026 | EDIFICIO_1 | P1 | 44.981 | 16.332 | G | -2.510 | 3 | 0.182 | SPECIAL_POSITION_CONFIRMED |
| SOL_1_column_0024 | EDIFICIO_1 | P1 | 44.981 | 20.452 | G | -2.510 | 3 | 4.302 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0022 | EDIFICIO_1 | P1 | 57.518 | 18.843 | H | 0.027 | 3 | 2.693 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0023 | EDIFICIO_1 | P1 | 57.518 | 26.176 | H | 0.027 | 3 | 10.026 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0019 | EDIFICIO_1 | P1 | 61.968 | 18.912 | H' | 0.000 | 3 | 2.762 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0020 | EDIFICIO_1 | P1 | 61.968 | 23.625 | H' | 0.000 | 3 | 7.475 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0021 | EDIFICIO_1 | P1 | 61.968 | 28.337 | H' | 0.000 | 3 | 12.187 | OFF_AXIS_LEGITIMATE |
| SOL_1_column_0032 | EDIFICIO_1 | P1 | 75.041 | 0.181 | IB | 1.675 | 1 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_1_column_0034 | EDIFICIO_1 | P1 | 75.041 | 9.081 | IB | 1.675 | 2 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_1_column_0033 | EDIFICIO_1 | P1 | 75.041 | 16.331 | IB | 1.675 | 3 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_2_column_0019 | EDIFICIO_1 | P2 | 37.491 | 20.452 | F | -0.000 | 3 | 4.302 | OFF_AXIS_LEGITIMATE |
| SOL_2_column_0021 | EDIFICIO_1 | P2 | 44.981 | 16.332 | G | -2.510 | 3 | 0.182 | SPECIAL_POSITION_CONFIRMED |
| SOL_2_column_0018 | EDIFICIO_1 | P2 | 44.981 | 20.452 | G | -2.510 | 3 | 4.302 | OFF_AXIS_LEGITIMATE |
| SOL_2_column_0026 | EDIFICIO_1 | P2 | 47.491 | 20.451 | G | -0.000 | 3 | 4.301 | OFF_AXIS_LEGITIMATE |
| SOL_2_column_0025 | EDIFICIO_1 | P2 | 57.491 | 20.451 | H | -0.000 | 3 | 4.301 | OFF_AXIS_LEGITIMATE |
| SOL_2_column_0027 | EDIFICIO_1 | P2 | 75.041 | 0.181 | IB | 1.675 | 1 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_2_column_0029 | EDIFICIO_1 | P2 | 75.041 | 9.081 | IB | 1.675 | 2 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_2_column_0028 | EDIFICIO_1 | P2 | 75.041 | 16.331 | IB | 1.675 | 3 | 0.181 | SPECIAL_POSITION_CONFIRMED |
| SOL_3_column_0024 | EDIFICIO_1 | P3 | 75.041 | 0.181 | IB | 1.675 | 1 | 0.181 | SPECIAL_POSITION_CONFIRMED |
