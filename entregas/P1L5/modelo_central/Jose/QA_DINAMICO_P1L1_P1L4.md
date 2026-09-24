# QA DINAMICO P1L1-P1L4 (Jose) — se regenera solo en cada corrida

Fuente viva: `UnityViewer\Builds\Windows\MCOC-Viewer_Data\StreamingAssets`

| Entrega | Dinamico | Veredicto hoy |
|---|---|---|
| P1L1 | benchmark 3D/3D_2 (repo) | OK en repo |
| P1L2 | fuerzas 1312/caso + pm | REVISAR |
| P1L3 | fuerzas+apoyos+pm | REVISAR |
| P1L4 | despl + demanda_capacidad | PASS |

Detalle por caso:

| Caso | Fuerzas | Desplazamientos |
|---|---|---|
| G | 1312 elems | 813 nodos |
| Q | 1312 elems | 813 nodos |
| EX | 1312 elems | 813 nodos |
| EY | 1312 elems | 813 nodos |
| R | 1312 elems | 813 nodos |

Apoyos: 106 | pm_interaction: {'P0_Mflexion': 'PASS', 'P25': 'PASS', 'P50': 'PARTIAL_FAIL_STEP_237_PHI_TARGET_REDUCED_TO_1.25PHIY', 'PureCompression': 'AXIAL_ONLY_PASS'}