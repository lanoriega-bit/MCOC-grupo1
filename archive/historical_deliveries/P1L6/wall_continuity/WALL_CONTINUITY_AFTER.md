# Corrección CURRENT de núcleos y columnas

Estado geométrico: PASS_WITH_EXPLICIT_NOTES. 84 muros activos; 38 candidatos previos siguen fuera del modelo y requieren revisión.

## Grupos en C

| Grupo | Piso | Muros | Continuidad |
|---|---|---|---|
| CORE_C_ED1_01 | S1 | E1-S1-M-020, E1-S1-M-026, E1-S1-M-034 | CONTINUOUS |
| CORE_C_ED1_01 | P1 | E1-P1-M-012, E1-P1-M-004, E1-P1-M-025 | CONTINUOUS |
| CORE_C_ED1_01 | P2 | E1-P2-M-010, E1-P2-M-007, E1-P2-M-009 | CONTINUOUS |
| CORE_C_ED1_01 | P3 | E1-P3-M-010, E1-P3-M-007, E1-P3-M-009 | CONTINUOUS |
| CORE_C_ED1_01 | P4 | E1-P4-M-009, E1-P4-M-007, E1-P4-M-010 | CONTINUOUS |
| CORE_C_ED1_02 | S1 | E1-S1-M-005, E1-S1-M-029, E1-S1-M-049 | CONTINUOUS |
| CORE_C_ED1_02 | P1 | E1-P1-M-002, E1-P1-M-010, E1-P1-M-026 | CONTINUOUS |
| CORE_C_ED1_02 | P2 | E1-P2-M-003, E1-P2-M-008, E1-P2-M-005 | CONTINUOUS |
| CORE_C_ED1_02 | P3 | E1-P3-M-003, E1-P3-M-008, E1-P3-M-005 | CONTINUOUS |
| CORE_C_ED1_02 | P4 | E1-P4-M-003, E1-P4-M-008, E1-P4-M-012 | CONTINUOUS |
| CORE_C_ED2_01 | S1 | E2-S1-M-007, E2-S1-M-008, E2-S1-M-010 | CONTINUOUS |
| CORE_C_ED2_01 | P1 | E2-P1-M-007, E2-P1-M-008, E2-P1-M-010 | CONTINUOUS |
| CORE_C_ED2_01 | P2 | E2-P2-M-007, E2-P2-M-008, E2-P2-M-010 | CONTINUOUS |
| CORE_C_ED2_01 | P3 | E2-P3-M-007, E2-P3-M-008, E2-P3-M-010 | CONTINUOUS |
| CORE_C_ED2_01 | P4 | E2-P4-M-007, E2-P4-M-008, E2-P4-M-009 | CONTINUOUS |

Continuidad verificada con tolerancia 2 mm en endpoints y 1 mm en espesor: ED1_02 tiene 1 mm de diferencia de extremo entre S1 y superiores por redondeo CAD; no se alteró para imponer igualdad numérica.

Los tres paños de cada C conservan IDs físicos distintos. El FE utiliza muros equivalentes de barra; esto no equivale a una sección C monolítica ni a un modelo shell.

## Continuidad global

| Línea | S1 | P1 | P2 | P3 | P4 | Estado |
|---|---|---|---|---|---|---|
| WALL_LINE_001 | E2-S1-M-001 | E2-P1-M-001 | E2-P2-M-001 | E2-P3-M-001 | E2-P4-M-001 | CONTINUOUS |
| WALL_LINE_002 | E2-S1-M-002 | E2-P1-M-002 | E2-P2-M-002 | E2-P3-M-002 | E2-P4-M-002 | CONTINUOUS |
| WALL_LINE_003 | E2-S1-M-003 | E2-P1-M-003 | E2-P2-M-003 | E2-P3-M-003 | E2-P4-M-003 | CONTINUOUS |
| WALL_LINE_004 | E2-S1-M-004 | E2-P1-M-004 | E2-P2-M-004 | E2-P3-M-004 | E2-P4-M-004 | CONTINUOUS |
| WALL_LINE_005 | E2-S1-M-005 | E2-P1-M-005 | E2-P2-M-005 | E2-P3-M-005 | E2-P4-M-005 | CONTINUOUS |
| WALL_LINE_006 | E2-S1-M-006 | E2-P1-M-006 | E2-P2-M-006 | E2-P3-M-006 | E2-P4-M-006 | CONTINUOUS |
| WALL_LINE_007 | E1-S1-M-026 | E1-P1-M-004 | E1-P2-M-007 | E1-P3-M-007 | E1-P4-M-007 | CONTINUOUS |
| WALL_LINE_008 | E1-S1-M-029 | E1-P1-M-010 | E1-P2-M-008 | E1-P3-M-008 | E1-P4-M-008 | CONTINUOUS |
| WALL_LINE_009 | E2-S1-M-007 | E2-P1-M-007 | E2-P2-M-007 | E2-P3-M-007 | E2-P4-M-007 | CONTINUOUS |
| WALL_LINE_010 | E2-S1-M-008 | E2-P1-M-008 | E2-P2-M-008 | E2-P3-M-008 | E2-P4-M-008 | CONTINUOUS |
| WALL_LINE_011 | E2-S1-M-010 | E2-P1-M-010 | E2-P2-M-010 | E2-P3-M-010 | E2-P4-M-009 | CONTINUOUS |
| WALL_LINE_012 | E2-S1-M-011 | E2-P1-M-011 | E2-P2-M-011 | E2-P3-M-011 | E2-P4-M-010 | CONTINUOUS |
| WALL_LINE_013 | E2-S1-M-009 | E2-P1-M-009 | E2-P2-M-009 | E2-P3-M-009 | — | EXPECTED_TERMINATION |
| WALL_LINE_014 | E1-S1-M-005 | E1-P1-M-002 | E1-P2-M-003 | E1-P3-M-003 | E1-P4-M-003 | CONTINUOUS |
| WALL_LINE_015 | E1-S1-M-049 | E1-P1-M-026 | E1-P2-M-005 | E1-P3-M-005 | E1-P4-M-012 | CONTINUOUS |
| WALL_LINE_016 | E1-S1-M-020 | E1-P1-M-012 | E1-P2-M-010 | E1-P3-M-010 | E1-P4-M-009 | CONTINUOUS |
| WALL_LINE_017 | E1-S1-M-034 | E1-P1-M-025 | E1-P2-M-009 | E1-P3-M-009 | E1-P4-M-010 | CONTINUOUS |

## Muros activos

| ID | Edificio | Piso | Largo m | Espesor m | Grupo | Fuente |
|---|---|---|---:|---:|---|---|
| E2-P1-M-001 | EDIFICIO_2 | P1 | 0.795 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-002 | EDIFICIO_2 | P1 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-003 | EDIFICIO_2 | P1 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-004 | EDIFICIO_2 | P1 | 0.790 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-005 | EDIFICIO_2 | P1 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-006 | EDIFICIO_2 | P1 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-001 | EDIFICIO_2 | P2 | 0.795 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-002 | EDIFICIO_2 | P2 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-003 | EDIFICIO_2 | P2 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-004 | EDIFICIO_2 | P2 | 0.790 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-005 | EDIFICIO_2 | P2 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-006 | EDIFICIO_2 | P2 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-001 | EDIFICIO_2 | P3 | 0.795 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-002 | EDIFICIO_2 | P3 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-003 | EDIFICIO_2 | P3 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-004 | EDIFICIO_2 | P3 | 0.790 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-005 | EDIFICIO_2 | P3 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-006 | EDIFICIO_2 | P3 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P4-M-001 | EDIFICIO_2 | P4 | 0.795 | 0.600 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-P4-M-002 | EDIFICIO_2 | P4 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-P4-M-003 | EDIFICIO_2 | P4 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-P4-M-004 | EDIFICIO_2 | P4 | 0.790 | 0.600 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-P4-M-005 | EDIFICIO_2 | P4 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-P4-M-006 | EDIFICIO_2 | P4 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-102.dxf |
| E2-S1-M-001 | EDIFICIO_2 | S1 | 0.795 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-002 | EDIFICIO_2 | S1 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-003 | EDIFICIO_2 | S1 | 1.825 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-004 | EDIFICIO_2 | S1 | 0.790 | 0.600 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-005 | EDIFICIO_2 | S1 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-006 | EDIFICIO_2 | S1 | 1.450 | 0.300 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E1-S1-M-026 | EDIFICIO_1 | S1 | 2.600 | 0.200 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-S1-M-029 | EDIFICIO_1 | S1 | 3.200 | 0.200 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E2-S1-M-007 | EDIFICIO_2 | S1 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P1-M-007 | EDIFICIO_2 | P1 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P2-M-007 | EDIFICIO_2 | P2 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P3-M-007 | EDIFICIO_2 | P3 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-S1-M-008 | EDIFICIO_2 | S1 | 2.395 | 0.300 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P1-M-008 | EDIFICIO_2 | P1 | 2.395 | 0.300 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P2-M-008 | EDIFICIO_2 | P2 | 2.395 | 0.300 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P3-M-008 | EDIFICIO_2 | P3 | 2.395 | 0.300 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-S1-M-010 | EDIFICIO_2 | S1 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P1-M-010 | EDIFICIO_2 | P1 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P2-M-010 | EDIFICIO_2 | P2 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-P3-M-010 | EDIFICIO_2 | P3 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-101.dxf |
| E2-S1-M-011 | EDIFICIO_2 | S1 | 7.950 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-011 | EDIFICIO_2 | P1 | 7.950 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-011 | EDIFICIO_2 | P2 | 7.950 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-011 | EDIFICIO_2 | P3 | 7.950 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-S1-M-009 | EDIFICIO_2 | S1 | 2.680 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P1-M-009 | EDIFICIO_2 | P1 | 2.680 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P2-M-009 | EDIFICIO_2 | P2 | 2.680 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E2-P3-M-009 | EDIFICIO_2 | P3 | 2.680 | 0.250 | OTHER_CAD_WALL | 2024_22-101.dxf |
| E1-S1-M-005 | EDIFICIO_1 | S1 | 1.478 | 0.250 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E1-S1-M-049 | EDIFICIO_1 | S1 | 1.478 | 0.250 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E1-S1-M-020 | EDIFICIO_1 | S1 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-S1-M-034 | EDIFICIO_1 | S1 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-P1-M-012 | EDIFICIO_1 | P1 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-P1-M-004 | EDIFICIO_1 | P1 | 2.600 | 0.200 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-P1-M-025 | EDIFICIO_1 | P1 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-101.dxf |
| E1-P2-M-010 | EDIFICIO_1 | P2 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P2-M-007 | EDIFICIO_1 | P2 | 2.600 | 0.200 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P2-M-009 | EDIFICIO_1 | P2 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P3-M-010 | EDIFICIO_1 | P3 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P3-M-007 | EDIFICIO_1 | P3 | 2.600 | 0.200 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P3-M-009 | EDIFICIO_1 | P3 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-102.dxf |
| E1-P4-M-009 | EDIFICIO_1 | P4 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-103.dxf |
| E1-P4-M-007 | EDIFICIO_1 | P4 | 2.600 | 0.200 | CORE_C_ED1_01 | 2017_67-103.dxf |
| E1-P4-M-010 | EDIFICIO_1 | P4 | 2.150 | 0.300 | CORE_C_ED1_01 | 2017_67-103.dxf |
| E1-P1-M-002 | EDIFICIO_1 | P1 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E1-P1-M-010 | EDIFICIO_1 | P1 | 3.200 | 0.200 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E1-P1-M-026 | EDIFICIO_1 | P1 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-101.dxf |
| E1-P2-M-003 | EDIFICIO_1 | P2 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P2-M-008 | EDIFICIO_1 | P2 | 3.200 | 0.200 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P2-M-005 | EDIFICIO_1 | P2 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P3-M-003 | EDIFICIO_1 | P3 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P3-M-008 | EDIFICIO_1 | P3 | 3.200 | 0.200 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P3-M-005 | EDIFICIO_1 | P3 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-102.dxf |
| E1-P4-M-003 | EDIFICIO_1 | P4 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-103.dxf |
| E1-P4-M-008 | EDIFICIO_1 | P4 | 3.200 | 0.200 | CORE_C_ED1_02 | 2017_67-103.dxf |
| E1-P4-M-012 | EDIFICIO_1 | P4 | 1.479 | 0.250 | CORE_C_ED1_02 | 2017_67-103.dxf |
| E2-P4-M-007 | EDIFICIO_2 | P4 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-102.dxf |
| E2-P4-M-008 | EDIFICIO_2 | P4 | 2.395 | 0.300 | CORE_C_ED2_01 | 2024_22-102.dxf |
| E2-P4-M-009 | EDIFICIO_2 | P4 | 2.820 | 0.250 | CORE_C_ED2_01 | 2024_22-102.dxf |
| E2-P4-M-010 | EDIFICIO_2 | P4 | 7.950 | 0.250 | ED2_LONG_WALL_CAD_POSITION | 2024_22-102.dxf |

## OpenSees antes / después

| Caso | Máximo antes m | Máximo después m | Residual equilibrio |
|---|---:|---:|---:|
| G | 0.09486793 | 0.01105420 | 7.27e-16 |
| Q | 0.02236640 | 0.00238136 | 4.54e-16 |
| EX | 0.06704658 | 0.06887272 | 7.69e-15 |
| EY | 0.09936989 | 0.09972031 | 5.08e-14 |

Reacciones globales, ejes X/Y/Z en kN:

| Caso | Antes Rx/Ry/Rz kN | Después Rx/Ry/Rz kN |
|---|---|---|
| G | 0.000 / -0.000 / 80184.104 | 0.000 / 0.000 / 82034.949 |
| Q | 0.000 / 0.000 / 24636.594 | 0.000 / 0.000 / 24636.594 |
| EX | -18047.336 / -0.000 / 0.000 | -18417.505 / -0.000 / 0.000 |
| EY | -0.000 / -18047.336 / -0.000 | -0.000 / -18417.505 / -0.000 |

No se fuerza una reducción de desplazamientos: cambian rigidez, caminos de carga y peso propio. Q conserva su total; G incluye el peso nuevo.

## Alcance y límites

El muro largo ED2 X=27,727 m permanece en el lado CAD. No se inventó una inversión. Los ejes CAD corrigen únicamente los núcleos ED1; no se trasladan vigas o columnas ajenas a esta revisión.

ED1-P4 G35 is existing lab fallback, not newly primary-confirmed; capacity reinforcement remains ASSUMED_FOR_LAB.

Las columnas E2-P4-C-004/C-007 pasan 20×20→70×70 cm por revisión explícita del usuario y continuidad con P3. XY, altura, material e IDs quedan intactos. No se afirma haber descifrado una etiqueta CAD nueva.

## QA

- unrelated_beams_and_slabs_preserved: PASS
- wall_materials_preserved: PASS
- CORE_C_ED1_01_vertical: PASS
- CORE_C_ED1_02_vertical: PASS
- CORE_C_ED2_01_vertical: PASS
- wall_duplicates_zero: PASS
- unexpected_wall_overlap_zero: PASS
- columns_follow_immediately_lower_section: PASS
- luis_reference_unchanged: PASS
