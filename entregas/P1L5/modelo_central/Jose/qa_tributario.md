# P1L2 QA tributario-gravitatorio DINAMICO (rev3)

Fuente: bundle FE actual + tributarias actuales. Se recalcula entero en cada corrida.

| Check | Valor | Estado |
|---|---|---|
| Elementos G / Q | 1312 / 1312 (target 1312) | OK |
| Fuerza axial columnas G | 69959 kN | |
| Fuerza axial columnas Q | 27543 kN | |
| Vigas tributarias | 1551 | OK |
| Area tributaria | 17132 m2 | OK |
| Global G vs q*A | 69959 vs 81375 kN | FALLA |
| Equilibrio G vs Q | 69959 vs 27543 kN | FALLA |
| pm_interaction | {'P0_Mflexion': 'PASS', 'P25': 'PASS', 'P50': 'PARTIAL_FAIL_STEP_237_PHI_TARGET_REDUCED_TO_1.25PHIY', 'PureCompression': 'AXIAL_ONLY_PASS'} | REVISAR |

**Veredicto: REVISAR**