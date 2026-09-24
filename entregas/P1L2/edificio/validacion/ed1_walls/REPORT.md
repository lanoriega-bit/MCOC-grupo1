# Diagnostico de caras de muro EDIFICIO_1

Estado: `PASS`

El extractor historico fusiono lineas colineales de `RLE-MURO`, pero luego dio 0.22 m de espesor a cada cara del contorno. Dos caras de un mismo muro quedaron por tanto como dos elementos resistentes. Esta revision vuelve a leer los DXF completos sin el redondeo historico de 0.15 m.

| Piso | Segmentos fuente | Prismas actuales | Muros analiticos confirmados | Cierres excluidos | Sin resolver |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 | 86 | 60 | 21 | 44 | 0 |
| P1 | 53 | 38 | 25 | 13 | 0 |
| P2 | 18 | 12 | 7 | 5 | 0 |
| P3 | 18 | 12 | 7 | 5 | 0 |
| P4 | 18 | 12 | 7 | 5 | 0 |

Total actual: `134` prismas. Segmentos analiticos recuperados desde pares: `67`. Cierres cortos excluidos: `72`. Sin resolver: `0`.

## Decision

Los pares confirmados deben reemplazarse por una sola centrolinea con el espesor medido directamente entre caras. Las caras no emparejadas son todas cierres de 0.15–0.70 m; se excluyen como geometria auxiliar del contorno y no se convierten en muros independientes.

## QA pendiente antes de aplicar

- revisar visualmente los overlays por piso;
- conservar el registro de cada cierre excluido;
- comprobar continuidad vertical y elevaciones estructurales;
- regenerar ED1/combinado solo cuando no queden decisiones silenciosas.
