# Auditoria visual arquitectonica P4 - EDIFICIO_1

La capa es exclusivamente visual y `participates_in_FE = false`.

- Segmentos RLE-LOSA inspeccionados: 50.
- Segmentos exteriores usados directamente: 13.
- Centrolineas de viga de respaldo del resalto: 3.
- Cierres colineales inferidos: 6.
- Bordes probables del resalto respaldado por vigas: 3.
- Area bbox anterior: 1802.479 m2.
- Area visual reconstruida: 958.393 m2.
- Reduccion respecto del bbox: 844.086 m2 (46.83%).
- Espesor: 0,15 m, segun `LOSA e=15 (S.I.C.)` de 2017_67-103.

## Criterio de confianza

- **CONFIRMED:** trece tramos exteriores dibujados en RLE-LOSA y espesor general de lamina.
- **LIKELY:** resalto norte cerrado por las vigas perimetrales P4.
- **INFERRED:** seis interrupciones colineales cortas cerradas entre tramos RLE-LOSA.

Los lazos y trazos interiores no se interpretan como huecos: se conservan como bordes DXF revisables.
