# Continuidad vertical de columnas

- Mapeo de pisos: fundacion -> 1S -> 1 -> 2 -> 3 -> 4
- Altura de entrepiso: 3.96 m
- Tolerancia XY: 0.35 m

## Relaciones verticales (27)

| Rel | Pisos declarados | Continuidad | Columnas | Centro XY | Estado 3D |
|---|---|---|---|---|---|

| REL_COL_0001 | fundacion;2 | PARCIAL | 2 | 65.663,9.052 | REVISAR |
| REL_COL_0002 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 7.606,0.118 | OK |
| REL_COL_0003 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 17.606,0.118 | OK |
| REL_COL_0004 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 17.606,9.018 | OK |
| REL_COL_0005 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 7.606,9.018 | OK |
| REL_COL_0006 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 0.106,9.031 | OK |
| REL_COL_0007 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 7.606,16.268 | OK |
| REL_COL_0008 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 17.606,16.268 | OK |
| REL_COL_0009 | fundacion;1S;1;2;3;4 | CONTINUA_DESDE_FUNDACION_A_PISO_4 | 6 | 27.559,0.118 | OK |
| REL_COL_0010 | 1;3;4 | CONTINUA | 3 | 37.489,0.079 | REVISAR |
| REL_COL_0011 | 1;3;4 | CONTINUA | 3 | 37.489,16.229 | REVISAR |
| REL_COL_0012 | 1;3;4 | CONTINUA | 3 | 37.489,8.979 | REVISAR |
| REL_COL_0013 | 1;3;4 | CONTINUA | 3 | 27.498,8.979 | REVISAR |
| REL_COL_0014 | 1;3;4 | CONTINUA | 3 | 27.489,0.079 | REVISAR |
| REL_COL_0015 | 1;3;4 | CONTINUA | 3 | 27.498,16.229 | REVISAR |
| REL_COL_0016 | 1;3;4 | CONTINUA | 3 | 47.489,8.979 | REVISAR |
| REL_COL_0017 | 1;3;4 | CONTINUA | 3 | 47.489,16.229 | REVISAR |
| REL_COL_0018 | 1;3;4 | CONTINUA | 3 | 57.489,16.229 | REVISAR |
| REL_COL_0019 | 1;4 | PARCIAL | 2 | 67.576,16.310 | REVISAR |
| REL_COL_0020 | 1;4 | PARCIAL | 2 | 67.443,8.960 | REVISAR |
| REL_COL_0021 | 1;4 | PARCIAL | 2 | 67.465,0.097 | REVISAR |
| REL_COL_0022 | 1;3;4 | CONTINUA | 3 | 57.489,0.092 | REVISAR |
| REL_COL_0023 | 1;3;4 | CONTINUA | 3 | 57.489,8.979 | REVISAR |
| REL_COL_0024 | 1;3;4 | CONTINUA | 3 | 47.489,0.079 | REVISAR |
| REL_COL_0025 | 1;4 | PARCIAL | 2 | 72.487,0.079 | REVISAR |
| REL_COL_0026 | 1;4 | PARCIAL | 2 | 72.487,16.209 | REVISAR |
| REL_COL_0027 | 1;4 | PARCIAL | 2 | 72.487,8.960 | REVISAR |

## Resumen

- Relaciones continuas Fundacion->Piso4: **8**
- Relaciones parciales contiguas: **0**
- Relaciones con hueco (soltura): **19**
- Columnas modelables cubiertas por alguna relacion: **98/139**

## Relaciones a revisar

| Rel | Pisos | Continuidad | Motivo |
|---|---|---|---|
| REL_COL_0001 | fundacion;2 | PARCIAL | hueco; xy_incoherente |
| REL_COL_0010 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0011 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0012 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0013 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0014 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0015 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0016 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0017 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0018 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0019 | 1;4 | PARCIAL | hueco |
| REL_COL_0020 | 1;4 | PARCIAL | hueco |
| REL_COL_0021 | 1;4 | PARCIAL | hueco |
| REL_COL_0022 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0023 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0024 | 1;3;4 | CONTINUA | hueco |
| REL_COL_0025 | 1;4 | PARCIAL | hueco |
| REL_COL_0026 | 1;4 | PARCIAL | hueco |
| REL_COL_0027 | 1;4 | PARCIAL | hueco |

## Columnas descubiertas (sin relacion vertical)

| Columna | Piso | Centro XY |
|---|---|---|
| C_P1_FUNDACION_0001 | fundacion | 65.30,16.69 |
| C_P1_FUNDACION_0003 | fundacion | 65.25,0.34 |
| C_P1_FUNDACION_0004 | fundacion | 69.90,0.12 |
| C_P1_FUNDACION_0005 | fundacion | 69.90,16.34 |
| C_P1_FUNDACION_0006 | fundacion | 69.85,9.09 |
| C_P1_01_0019 | 1 | 61.97,18.91 |
| C_P1_01_0022 | 1 | 57.52,18.84 |
| C_P1_02_0001 | 2 | 31.08,0.12 |
| C_P1_02_0002 | 2 | 31.08,16.39 |
| C_P1_02_0003 | 2 | 31.08,9.02 |
| C_P1_02_0004 | 2 | 21.08,9.02 |
| C_P1_02_0005 | 2 | 21.08,0.12 |
| C_P1_02_0006 | 2 | 21.08,16.27 |
| C_P1_02_0007 | 2 | 41.08,9.02 |
| C_P1_02_0008 | 2 | 41.08,16.39 |
| C_P1_02_0009 | 2 | 51.08,16.27 |
| C_P1_02_0010 | 2 | 61.08,16.27 |
| C_P1_02_0011 | 2 | 61.08,9.02 |
| C_P1_02_0012 | 2 | 61.08,0.12 |
| C_P1_02_0013 | 2 | 51.08,0.12 |
| C_P1_02_0014 | 2 | 51.08,9.02 |
| C_P1_02_0015 | 2 | 41.08,0.12 |
| C_P1_02_0016 | 2 | 66.08,0.12 |
| C_P1_02_0017 | 2 | 66.08,16.27 |
| C_P1_02_0018 | 2 | 38.57,20.39 |
| C_P1_02_0019 | 2 | 31.08,20.39 |
| C_P1_02_0021 | 2 | 38.57,16.27 |
| C_P1_03_0004 | 3 | 17.50,9.02 |
| C_P1_03_0005 | 3 | 17.50,0.12 |
| C_P1_03_0006 | 3 | 17.50,16.27 |
| C_P1_03_0016 | 3 | 62.49,0.12 |
| C_P1_03_0017 | 3 | 62.49,16.27 |
| C_P1_03_0018 | 3 | 62.49,9.02 |
| C_P1_04_0018 | 4 | 77.38,9.02 |
| C_P1_04_0019 | 4 | 77.38,16.27 |
| C_P1_04_0020 | 4 | 77.38,0.12 |
| C_P1_04_0021 | 4 | 57.48,20.39 |
| C_P1_04_0022 | 4 | 47.48,20.39 |
| C_P1_04_0023 | 4 | 75.03,0.12 |
| C_P1_04_0024 | 4 | 75.03,16.27 |
| C_P1_04_0025 | 4 | 75.03,9.02 |
