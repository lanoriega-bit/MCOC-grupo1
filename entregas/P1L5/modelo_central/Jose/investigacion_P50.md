# Investigacion: caso P50 — columna de capacidad (P1L2 QA dinamico)

Fecha: 2026-09-23 · Sesion Jose (P1L2 dinamica) · FUENTE: bundle build actual
`UnityViewer\Builds\Windows\MCOC-Viewer_Data\StreamingAssets\capacity_ha.json` (Solo lectura; no se modifico nada del modelo.)

## Columna analizada
| Campo | Valor |
|---|---|
| section_id | C_P2_01_0001_lab_fiber_section |
| building_column_id | C_P2_01_0001 (confirmado edificio) |
| mapped_element_id (FE) | E2-P1-C-002 |
| mapped_analysis_id | A-C-0009 |
| matching | MATCHED_BY_SOURCE_FLOOR_SECTION_AND_COORDINATE (dx 0.157 m, OK) |
| Seccion | 0.70 x 0.70 m, recub 0.04 m |
| Armado | 12 barras de 25 mm |
| Materiales | f'c=35 MPa, fy=420 MPa, Es=200 GPa |

## Veredicto del QA dinamico P1L2 (rev3)
`REVISAR` — los checks que pasan: elementos 1312/1312, tributarias, pm P0/P25/PureCompression.
Checks que fallan/verifican: conservacion global G vs q·A (~14%), y el caso P50 de ductilidad.

## Causa raiz del PARTIAL_FAIL (consolidado del bundle)
- `axial_load_kN = -9746.1` (P50 = 50% del Nmax nominal).
- `Nmax` (PureCompression) = -19492 kN  ->  N/Nmax = **0.50**.
- Nivel P50: `max_moment_kNm = 1650.1`, `curvature_at_max = 0.00441/m`, corte en paso **236/240**
  con `status = PARTIAL_FAIL_STEP_237_PHI_TARGET_REDUCED_TO_1.25PHIY`.
- No hay pasos no-convergentes en `moment_curvature` (0/241). El momento entra en plateau
  descendente (758.8 -> 757.9 kNm, steps 233..240) -> la seccion agota su capacidad de giro.
- Comparativo de ductilidad (curvatura en el max):
  - P0  (N=0)        : 0.03106/m, 240 steps, PASS
  - P25 (N=4873 kN)  : 0.00865/m, 240 steps, PASS
  - P50 (N=9746 kN)  : 0.00441/m, 236 steps, PARTIAL_FAIL  (~3.5x menos giro que P0)

Conclusion: la columna E2-P1-C-002 es adecuada en capacidad de momento (diseño por resistencia, D/C<1.0
histórico 0.204), pero bajo 50% de carga axial su **ductilidad de rotacion** no cubre el objetivo Φ
de la curva (el solver reduce a 1.25Φy como red de seguridad). Es un hallazgo de ductilidad, no de
resistencia ni de error numerico. Si mañana cambian la columna/geometria, al re-correr el QA dinamico
se re-evalua solo (objetivo P1L1-P1L4 dinamicos).

## Recomendacion (a decidir por el equipo de estructuras)
- Reportar P50 como ductilidad limitada bajo alta compresion y evaluar si el objetivo Φ del trazado
  es el adecuado para columnas con N>0.4·Nmax (normativa permite reduccion; el bundle ya la aplica a 1.25Φy).
- El QA queda operativo y dinamico; el veredicto lo fijan los umbrales de este documento.