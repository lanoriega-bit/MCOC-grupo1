# Cierre espacial de cargas 700 — EDIFICIO_2 y cargas especiales

> EDIFICIO_1 permanece congelado según la auditoría aprobada. No se recalculó Q, G, masas, EX/EY, superposición, OpenSees ni Unity.

## Transformación definitiva 2024_22-700

| Planta | Pisos | Xref | Matriz | Residual máximo |
| --- | --- | --- | --- | ---: |
| PLANTA CARGAS CIELO 1° SUBTERRANEO A CIELO PISO 3° | S1, P1, P2, P3 | 2024_22-101 | `[[0.01, 0.0, -9.85437078], [0.0, -0.01, 56.56439718]]` | 7.1054273576e-15 m |
| PLANTA CARGAS CIELO PISO 4° | P4 | 2024_22-102 | `[[0.01, 0.0, -59.794620249999], [0.0, -0.01, 56.56439718]]` | 1.2809491336e-14 m |

Ambas inserciones son 1:1, giro 0° y requieren `mirror_y=true`. La transformación no usa ajuste visual ni modifica los ejes del edificio.

## Correspondencia de niveles

- La lámina rotula literalmente `CIELO 1° SUBTERRANEO A CIELO PISO 3°`; esa planta usa el xref 101 que `global_axes.json` comparte para S1/P1/P2/P3.
- `CIELO PISO 4°` usa el xref 102 y el origen estructural P4.

## SC encontradas en EDIFICIO_2

- S1/P1/P2/P3: zonas superficiales `SC=200`, `300` y `500 kgf/m²`; la intensidad 500 aparece con dos tramas/zonas distintas.
- P4: zona superficial `SC=200 kgf/m²`.
- P4: banda lineal `SC=100 kgf/m` con `PM.ADIC=1500 kgf/m`; su geometría está localizada, pero el receptor permanece `UNRESOLVED` y no está lista para aplicar.

## QA de cobertura sobre paños actuales

| Piso | Paños | Área [m²] | Confirmed | Unmapped | Overlap | Multizona |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 6 | 91.264 | 91.264 (100.00%) | 0.000 (0.00%) | 0.000000 | 6 |
| P1 | 6 | 91.264 | 91.264 (100.00%) | 0.000 (0.00%) | 0.000000 | 6 |
| P2 | 6 | 91.264 | 91.264 (100.00%) | 0.000 (0.00%) | 0.000000 | 6 |
| P3 | 6 | 91.264 | 91.264 (100.00%) | 0.000 (0.00%) | 0.000000 | 6 |
| P4 | 6 | 90.949 | 90.949 (100.00%) | 0.000 (0.00%) | 0.000000 | 0 |

Paños multizona:
- S1: E2-S1-P-001, E2-S1-P-002, E2-S1-P-003, E2-S1-P-004, E2-S1-P-005, E2-S1-P-006.
- P1: E2-P1-P-001, E2-P1-P-002, E2-P1-P-003, E2-P1-P-004, E2-P1-P-005, E2-P1-P-006.
- P2: E2-P2-P-001, E2-P2-P-002, E2-P2-P-003, E2-P2-P-004, E2-P2-P-005, E2-P2-P-006.
- P3: E2-P3-P-001, E2-P3-P-002, E2-P3-P-003, E2-P3-P-004, E2-P3-P-005, E2-P3-P-006.
- P4: ninguno.

## Cargas especiales EDIFICIO_1

- `L700-P2-POINT-SC-7000`: **UNRESOLVED**. No existen LEADER/MLEADER, flechas, bloques, nodos ni polilíneas conectadas al texto en `HATCH CARGAS`; magnitud y tipo confirmados, posición/receptor no confirmados.
- `L700-P3-POINT-SC-6000`: **UNRESOLVED**. No existen LEADER/MLEADER, flechas, bloques, nodos ni polilíneas conectadas al texto en `HATCH CARGAS`; magnitud y tipo confirmados, posición/receptor no confirmados.
- `L700-P3-POINT-SC-6700`: **UNRESOLVED**. No existen LEADER/MLEADER, flechas, bloques, nodos ni polilíneas conectadas al texto en `HATCH CARGAS`; magnitud y tipo confirmados, posición/receptor no confirmados.
- `L700-P4-LINE-SC-800`: **LIKELY**. Banda y centrolinea de 35.000 m, orientación horizontal y cadena de 11 segmentos estructurales compatibles; no hay líder que identifique un único receptor.
- `P1 PM.ADIC=2800`: **CONFIRMED_UNIT = kgf/m2**. El superíndice `2` existe como entidad TEXT separada, igual que el de SC; la leyenda no dice carga lineal.

## Catálogo

Estado: `READY_FOR_Q_REVIEW_NOT_APPLIED`. Entradas: 108.

| Tipo | Cantidad |
| --- | ---: |
| SC_SURFACE | 44 |
| SC_LINE | 2 |
| SC_POINT | 3 |
| PM_ADIC_SURFACE | 44 |
| PM_ADIC_LINE | 2 |
| PM_ADIC_POINT | 3 |
| PP_LOSA | 10 |

Listas espacialmente para aplicar después de aprobación: zonas `SC_SURFACE` y `PM_ADIC_SURFACE` de ambos edificios, incluida `PM.ADIC=2800 kgf/m²`. La banda E1-P4 de 800/7600 kgf/m queda `LIKELY`: puede incorporarse sólo si se acepta distribuirla sobre la cadena receptora.

Siguen `REVIEW_REQUIRED`: las tres cargas puntuales de EDIFICIO_1; la banda lineal EDIFICIO_2-P4 de 100/1500 kgf/m por receptor no resuelto; y `PP_LOSA` hasta mapear espesores locales. No quedan zonas superficiales `UNMAPPED` en los paños actuales de EDIFICIO_2.

## Overlays EDIFICIO_2

- [S1](overlay_EDIFICIO_2_S1.png)
- [P1](overlay_EDIFICIO_2_P1.png)
- [P2](overlay_EDIFICIO_2_P2.png)
- [P3](overlay_EDIFICIO_2_P3.png)
- [P4](overlay_EDIFICIO_2_P4.png)
