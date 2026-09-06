# Auditoria CAD de propiedades

- Estado: **PASS_WITH_REVIEW_NOTES**
- Labels revisados: 871
- Labels con propiedad/indicio estructural: 734
- Distancia maxima asociacion tentativa: 2.0 m
- La auditoria no modifica el modelo 3D ni asigna propiedades globales de material.

## Labels por tipo

| Tipo | Conteo |
|---|---:|
| beam_section | 445 |
| column_section | 102 |
| foundation_beam_label_incomplete | 23 |
| foundation_beam_section | 59 |
| wall_thickness | 105 |

## Asociacion tentativa

| Estado | Conteo |
|---|---:|
| ASSOCIATED_NEAREST | 681 |
| NEAREST_OVER_LIMIT | 51 |
| NO_TARGET | 2 |

## Evidencia textual agrupada

| Tipo | Propiedad | Conteo | Edificios | Pisos | Textos ejemplo |
|---|---|---:|---|---|---|
| beam_section | 20/130 cm | 3 | EDIFICIO_1 | S1 | V. 20/130 |
| beam_section | 20/80 cm | 8 | EDIFICIO_1 | S1, P1 | V. 20/80 |
| beam_section | 20/90 cm | 1 | EDIFICIO_1 | P1 | V. 20/90 |
| beam_section | 30/45 cm | 2 | EDIFICIO_1 | P2 | V. 30/45 |
| beam_section | 30/80 cm | 20 | EDIFICIO_2 | S1, P1, P2, P3, P4 | V. 30/80 |
| beam_section | 40/60 cm | 4 | EDIFICIO_1 | P3, P4 | V. 40/60 |
| beam_section | 40/80 cm | 15 | EDIFICIO_2 | S1, P1, P2, P3, P4 | V. 40/80 |
| beam_section | 60/80 cm | 392 | EDIFICIO_1, EDIFICIO_2 | S1, P1, P2, P3, P4 | V. 60/80 |
| column_section | 20/20 cm | 19 | EDIFICIO_2 | P4 | P.H.I 20x20 |
| column_section | 20/50 cm | 1 | EDIFICIO_1 | P1 | P. 20x50 |
| column_section | 30/30 cm | 3 | EDIFICIO_1 | P1 | P. 30x30 |
| column_section | 70/70 cm | 79 | EDIFICIO_1 | S1, P1, P2, P3, P4 | P. 70x70 |
| foundation_beam_label_incomplete | incomplete_section | 20 | EDIFICIO_2 | S1 | V.F. |
| foundation_beam_label_incomplete | incomplete_section | 1 | EDIFICIO_1 | S1 | V.F. 1 |
| foundation_beam_label_incomplete | incomplete_section | 1 | EDIFICIO_1 | S1 | V.F. 2 |
| foundation_beam_label_incomplete | incomplete_section | 1 | EDIFICIO_1 | S1 | V.F. 3 |
| foundation_beam_section | 15/100 cm | 2 | EDIFICIO_1 | P1 | V.F. 15/100 |
| foundation_beam_section | 15/225 cm | 2 | EDIFICIO_1 | S1 | V.F. 15/225 |
| foundation_beam_section | 20/120 cm | 28 | EDIFICIO_2, EDIFICIO_1 | S1 | V.F. 20/120 |
| foundation_beam_section | 20/160 cm | 8 | EDIFICIO_1, EDIFICIO_2 | S1 | V.F. 20/160 |
| foundation_beam_section | 20/180 cm | 14 | EDIFICIO_1, EDIFICIO_2 | S1 | V.F. 20/180 |
| foundation_beam_section | 20/220 cm | 3 | EDIFICIO_1 | S1 | V.F. 20/220 |
| foundation_beam_section | 30/136 cm | 1 | EDIFICIO_1 | S1 | V.F. 30/136 |
| foundation_beam_section | 30/170 cm | 1 | EDIFICIO_1 | S1 | V.F. 30/170 |
| wall_thickness | e=15 cm | 4 | EDIFICIO_1 | P1 | M.H.A. e=15; M.H.A. e= 15 |
| wall_thickness | e=20 cm | 26 | EDIFICIO_1 | S1, P1, P2, P3, P4 | M.H.A. e= 20; M.H.A. e=20 |
| wall_thickness | e=25 cm | 29 | EDIFICIO_2, EDIFICIO_1 | S1, P1, P2, P3, P4 | M.H.A. e=25; M.H.A. e= 25 |
| wall_thickness | e=30 cm | 36 | EDIFICIO_1, EDIFICIO_2 | S1, P1, P2, P3, P4 | M.H.A. e= 30; M.H.A. e=30 |
| wall_thickness | e=60 cm | 10 | EDIFICIO_2 | S1, P1, P2, P3, P4 | M.H.A. e=60 |

## Layers estructurales usados

| Layer | Roles detectados |
|---|---|
| RLE-MURO | wall |
| RLE-MURO_merged | wall |
| RLE-PILAR | column |
| RLE-TEXTO-1 | beam_label, column_label, steel_beam_label, wall_label |
| RLE-VIGA | beam |
| generated_connected_support | support |
| generated_diaphragm_bbox | slab |

## Labels a revisar

| Label | Tipo | Texto | Edificio | Piso | Asociacion | Distancia [m] |
|---|---|---|---|---|---|---:|
| LBL2_base_beam_label_0001 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0021 | 4.199 |
| LBL2_base_beam_label_0002 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0022 | 4.908 |
| LBL2_base_beam_label_0003 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0022 | 4.1 |
| LBL2_base_beam_label_0004 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0022 | 4.211 |
| LBL2_base_beam_label_0005 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0021 | 4.361 |
| LBL2_base_beam_label_0006 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0026 | 3.416 |
| LBL2_base_beam_label_0007 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0027 | 3.267 |
| LBL2_base_beam_label_0008 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0005 | 4.924 |
| LBL2_base_beam_label_0009 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0027 | 4.89 |
| LBL2_base_beam_label_0010 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0026 | 4.515 |
| LBL2_base_beam_label_0018 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0014 | 4.174 |
| LBL2_base_beam_label_0020 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0025 | 2.71 |
| LBL2_base_beam_label_0023 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0024 | 3.629 |
| LBL2_base_beam_label_0026 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0024 | 4.974 |
| LBL2_base_beam_label_0031 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0021 | 4.361 |
| LBL2_base_beam_label_0036 | foundation_beam_section | V.F. 20/120 | EDIFICIO_2 | S1 | SOL2_base_support_0015 | 3.853 |
| LBL2_4_column_label_0095 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0001 | 6.821 |
| LBL2_4_column_label_0096 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0001 | 4.472 |
| LBL2_4_column_label_0097 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0001 | 2.443 |
| LBL2_4_column_label_0098 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0001 | 2.107 |
| LBL2_4_column_label_0099 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0001 | 3.926 |
| LBL2_4_column_label_0100 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0002 | 4.472 |
| LBL2_4_column_label_0101 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0002 | 2.443 |
| LBL2_4_column_label_0103 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0005 | 5.856 |
| LBL2_4_column_label_0104 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0006 | 4.314 |
| LBL2_4_column_label_0105 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0006 | 2.141 |
| LBL2_4_column_label_0107 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0006 | 3.745 |
| LBL2_4_column_label_0108 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0007 | 4.314 |
| LBL2_4_column_label_0109 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0007 | 2.141 |
| LBL2_4_column_label_0111 | column_section | P.H.I 20x20 | EDIFICIO_2 | P4 | SOL2_4_column_0003 | 3.38 |

## Criterio

- Las secciones y espesores reportados provienen de texto CAD, no de inferencia resistente.
- `M.H.A.` se conserva como indicio textual de muro de hormigon armado cuando aparece en el label; no se transforma en material global del modelo.
- Las asociaciones son nearest-neighbor sobre el mismo edificio y piso; deben revisarse visualmente antes de usar en calculo resistente.
