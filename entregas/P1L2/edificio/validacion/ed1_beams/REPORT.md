# Diagnostico inicial de vigas EDIFICIO_1

Estado: `DIAGNOSTIC_COMPLETE_NO_GEOMETRY_CHANGE`

| Piso | Segmentos DXF | Prismas actuales | Un par posible | Pareo ambiguo | Diagonales | Cortos <0.75 m | Grupos colineales | Extremos aislados |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 83 | 79 | 66 | 8 | 0 | 5 | 18 | 9 |
| P1 | 111 | 108 | 91 | 10 | 2 | 4 | 2 | 28 |
| P2 | 113 | 112 | 91 | 16 | 0 | 8 | 6 | 22 |
| P3 | 124 | 124 | 107 | 9 | 0 | 12 | 11 | 20 |
| P4 | 122 | 122 | 82 | 35 | 0 | 17 | 6 | 22 |

## Alcance de este paso

No se modifico ninguna viga. El diagnostico separa defectos seguros (duplicados exactos) de candidatos que requieren evidencia adicional (caras paralelas, fragmentos, extremos y cruces).

La coincidencia dominante entre separacion de caras y ancho rotulado (0.20/0.30/0.40/0.60 m) indica que `RLE-VIGA` contiene contornos. Los casos ambiguos, diagonales y extremos aislados deben resolverse antes de crear centrolineas.
