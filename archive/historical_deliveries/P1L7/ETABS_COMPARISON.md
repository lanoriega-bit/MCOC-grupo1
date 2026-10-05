# ETABS: contraste sin calibración

resumen_modelos.pdf, page 1, forces N; LT1=ED1/LT2=ED2

| Edificio | Caso | CURRENT [MN] | ETABS [MN] | Diferencia |
| --- | --- | ---: | ---: | ---: |
| EDIFICIO_1 | G | 45.213021 | 47.140276 | -4.09% |
| EDIFICIO_1 | Q | 2.482394 | 11.620380 | -78.64% |
| EDIFICIO_1 | EX | 9.290844 | 6.593501 | +40.91% |
| EDIFICIO_1 | EY | 9.290844 | 4.331107 | +114.51% |
| EDIFICIO_2 | G | 33.503038 | 34.723194 | -3.51% |
| EDIFICIO_2 | Q | 1.847801 | 11.096777 | -83.35% |
| EDIFICIO_2 | EX | 6.885388 | 2.953084 | +133.16% |
| EDIFICIO_2 | EY | 6.885388 | 3.680735 | +87.07% |

G/Q: resultantes por edificio; EX/EY: fuerza aplicada por edificio, no reacción basal individual asignada arbitrariamente.
La nueva Q uniforme explica gran parte de la diferencia CV. G conserva espesores de losa/materiales académicos; no se han ajustado contra ETABS.

- ETABS node 311/2987 and C9/C21/B739/C1/C4/B189 have no verified CURRENT crosswalk; no false displacement/internal-force comparison.
- ETABS modal periods not comparable: this CURRENT pipeline does not perform eigenanalysis.
- Pseudo-static 0.2*(G+0.5Q), centroid-nearest-node and rigid-arm simplifications differ from ETABS.
