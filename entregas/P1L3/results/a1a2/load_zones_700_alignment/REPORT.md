# Auditoría espacial de zonas de carga — lámina 2017_67-700

> Estado: transformación confirmada; cargas no aplicadas. El caso uniforme vigente se conserva como `LEGACY_UNIFORM_Q_VALIDATION`.

## Alcance y decisión

La lámina contiene **seis** intensidades superficiales SC distintas: 100, 200, 250, 300, 400 y 500 kgf/m². El calce usa los xrefs estructurales 101/102/103 insertados 1:1 en la lámina 700 y el sistema canónico de `global_axes.json`; no recalibra el edificio.

La convención del CAD exige `scale=0.01`, `rotation=0°` y `mirror_y=true`. Luego se aplica el calce global confirmado de EDIFICIO_1: `dx=27.491 m`, `dy=0`.

## Transformaciones y correspondencia de niveles

| Planta fuente | Nivel analítico | Xref | Residual máximo [m] | Estado |
| --- | --- | --- | ---: | --- |
| PLANTA CIELO 1° SUBTERRANEO | S1 | 2017_67-101 | 0.000000000 | CONFIRMED |
| PLANTA CIELO PISO 1° | P1 | 2017_67-101 | 0.000000000 | CONFIRMED |
| PLANTA CIELO PISO 2° | P2 | 2017_67-102 | 0.000000000 | CONFIRMED |
| PLANTA CIELO PISO 3° | P3 | 2017_67-102 | 0.000000000 | CONFIRMED |
| PLANTA CIELO PISO 4° | P4 | 2017_67-103 | 0.000000000 | CONFIRMED |

La correspondencia no se asumió por nombre: cada planta cielo contiene un xref cuya planta y origen coinciden con la observación del mismo nivel en `global_axes.json` (101: S1/P1; 102: P2/P3; 103: P4). Las vigas y ejes pertenecen, por tanto, al nivel analítico homónimo.

## Puntos de control

### S1

| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |
| --- | --- | --- | --- | ---: |
| E/1 | FIT | [-1193.9754, 7854.120837] | [27.491, 0.0] | 0.000000000 |
| H/2 | FIT | [1806.0246, 6964.120837] | [57.491, 8.9] | 0.000000000 |
| J/3 | FIT | [3806.0246, 6239.120837] | [77.491, 16.15] | 0.000000000 |
| F/3 | INDEPENDENT_CHECK | [-193.9754, 6239.120837] | [37.491, 16.15] | 0.000000000 |
| I/1 | INDEPENDENT_CHECK | [2806.0246, 7854.120837] | [67.491, 0.0] | 0.000000000 |
| G/2a | INDEPENDENT_CHECK | [806.0246, 6469.620837] | [47.491, 13.845] | 0.000000000 |

### P1

| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |
| --- | --- | --- | --- | ---: |
| E/1 | FIT | [3271.133741, 8165.872827] | [27.491, -0.0] | 0.000000000 |
| H/2 | FIT | [6271.133741, 7275.872827] | [57.491, 8.9] | 0.000000000 |
| J/3 | FIT | [8271.133741, 6550.872827] | [77.491, 16.15] | 0.000000000 |
| F/3 | INDEPENDENT_CHECK | [4271.133741, 6550.872827] | [37.491, 16.15] | 0.000000000 |
| I/1 | INDEPENDENT_CHECK | [7271.133741, 8165.872827] | [67.491, -0.0] | 0.000000000 |
| G/2a | INDEPENDENT_CHECK | [5271.133741, 6781.372827] | [47.491, 13.845] | 0.000000000 |

### P2

| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |
| --- | --- | --- | --- | ---: |
| E/1 | FIT | [9305.64568, 8881.986213] | [27.491, -0.0] | 0.000000000 |
| H/2 | FIT | [12305.64568, 7991.986213] | [57.491, 8.9] | 0.000000000 |
| J/3 | FIT | [14305.64568, 7266.986213] | [77.491, 16.15] | 0.000000000 |
| F/3 | INDEPENDENT_CHECK | [10305.64568, 7266.986213] | [37.491, 16.15] | 0.000000000 |
| I/1 | INDEPENDENT_CHECK | [13305.64568, 8881.986213] | [67.491, -0.0] | 0.000000000 |
| G/2a | INDEPENDENT_CHECK | [11305.64568, 7497.486213] | [47.491, 13.845] | 0.000000000 |

### P3

| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |
| --- | --- | --- | --- | ---: |
| E/1 | FIT | [9078.564636, 2702.082017] | [27.491, 0.0] | 0.000000000 |
| H/2 | FIT | [12078.564636, 1812.082017] | [57.491, 8.9] | 0.000000000 |
| J/3 | FIT | [14078.564636, 1087.082017] | [77.491, 16.15] | 0.000000000 |
| F/3 | INDEPENDENT_CHECK | [10078.564636, 1087.082017] | [37.491, 16.15] | 0.000000000 |
| I/1 | INDEPENDENT_CHECK | [13078.564636, 2702.082017] | [67.491, 0.0] | 0.000000000 |
| G/2a | INDEPENDENT_CHECK | [11078.564636, 1317.582017] | [47.491, 13.845] | 0.000000000 |

### P4

| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |
| --- | --- | --- | --- | ---: |
| E/1 | FIT | [-1889.833864, 1908.141237] | [27.491, 0.0] | 0.000000000 |
| H/2 | FIT | [1110.166136, 1018.141237] | [57.491, 8.9] | 0.000000000 |
| J/3 | FIT | [3110.166136, 293.141237] | [77.491, 16.15] | 0.000000000 |
| F/3 | INDEPENDENT_CHECK | [-889.833864, 293.141237] | [37.491, 16.15] | 0.000000000 |
| I/1 | INDEPENDENT_CHECK | [2110.166136, 1908.141237] | [67.491, 0.0] | 0.000000000 |
| G/2a | INDEPENDENT_CHECK | [110.166136, 523.641237] | [47.491, 13.845] | 0.000000000 |

## Cobertura de los paños actuales

Estas áreas sólo diagnostican el mapeo espacial. No se multiplicaron por SC ni se reemplazó el Q vigente.

| Piso | Paños | Área [m²] | Confirmed | Unmapped | Overlap | Review required | Multizona |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 7 | 82.268 | 81.522 (99.09%) | 0.746 (0.91%) | 0.000000 (0.000%) | 0.000 (0.00%) | 7 |
| P1 | 14 | 588.659 | 574.835 (97.65%) | 13.824 (2.35%) | 0.000000 (0.000%) | 0.000 (0.00%) | 13 |
| P2 | 18 | 702.374 | 682.823 (97.22%) | 19.550 (2.78%) | 0.000000 (0.000%) | 0.000 (0.00%) | 18 |
| P3 | 21 | 762.038 | 754.275 (98.98%) | 7.763 (1.02%) | 0.000000 (0.000%) | 0.000 (0.00%) | 3 |
| P4 | 20 | 801.281 | 791.831 (98.82%) | 9.450 (1.18%) | 0.000034 (0.000%) | 0.000 (0.00%) | 2 |

## Zonas SC

| ID | Piso | SC original | SI | Trama | Confianza |
| --- | --- | ---: | ---: | --- | --- |
| L700-E1-S1-H01-SC | S1 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-S1-H02-SC | S1 | 300 kgf/m2 | 2.941995 kN/m2 | AR-HBONE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-S1-H03-SC | S1 | 250 kgf/m2 | 2.451662 kN/m2 | ANGLE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-S1-H04-SC | S1 | 500 kgf/m2 | 4.903325 kN/m2 | HONEY | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-S1-H05-SC | S1 | 500 kgf/m2 | 4.903325 kN/m2 | AR-CONC | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H06-SC | P1 | 200 kgf/m2 | 1.961330 kN/m2 | GRAVEL | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H07-SC | P1 | 250 kgf/m2 | 2.451662 kN/m2 | ANGLE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H08-SC | P1 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H09-SC | P1 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H10-SC | P1 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H11-SC | P1 | 300 kgf/m2 | 2.941995 kN/m2 | AR-HBONE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P1-H12-SC | P1 | 500 kgf/m2 | 4.903325 kN/m2 | BRASS | REVIEW_REQUIRED_UNIT |
| L700-E1-P1-H13-SC | P1 | 400 kgf/m2 | 3.922660 kN/m2 | ANSI34 | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H14-SC | P2 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H15-SC | P2 | 250 kgf/m2 | 2.451662 kN/m2 | ANGLE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H16-SC | P2 | 400 kgf/m2 | 3.922660 kN/m2 | ANSI34 | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H17-SC | P2 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H18-SC | P2 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H19-SC | P2 | 300 kgf/m2 | 2.941995 kN/m2 | AR-HBONE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P2-H20-SC | P2 | 200 kgf/m2 | 1.961330 kN/m2 | GRAVEL | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P3-H21-SC | P3 | 250 kgf/m2 | 2.451662 kN/m2 | ANGLE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P3-H22-SC | P3 | 300 kgf/m2 | 2.941995 kN/m2 | AR-HBONE | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P3-H23-SC | P3 | 500 kgf/m2 | 4.903325 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P3-H24-SC | P3 | 200 kgf/m2 | 1.961330 kN/m2 | GRAVEL | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P4-H25-SC | P4 | 100 kgf/m2 | 0.980665 kN/m2 | _USER | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P4-H26-SC | P4 | 200 kgf/m2 | 1.961330 kN/m2 | GRAVEL | CONFIRMED_FROM_PLAN_AND_AXES |
| L700-E1-P4-H28-SC | P4 | 200 kgf/m2 | 1.961330 kN/m2 | GRAVEL | CONFIRMED_FROM_PLAN_AND_AXES |

## Cargas puntuales y lineales

| ID | Piso | Tipo | Referencia XY global [m] | Receptor | Estado |
| --- | --- | --- | --- | --- | --- |
| L700-P2-POINT-SC-7000 | P2 | POINT | [71.264121, 22.461906] | None | REVIEW_REQUIRED_NO_EXPLICIT_LEADER |
| L700-P3-POINT-SC-6000 | P3 | POINT | [72.698823, 22.462057] | None | REVIEW_REQUIRED_NO_EXPLICIT_LEADER |
| L700-P3-POINT-SC-6700 | P3 | POINT | [26.277333, 21.947653] | None | REVIEW_REQUIRED_NO_EXPLICIT_LEADER |
| L700-P4-LINE-SC-800 | P4 | LINE | [54.640881, 16.356404] | E1-P4-V-012 | CENTERLINE_CANDIDATE_FROM_HATCH_BAND |

Las tres cargas puntuales aparecen como anotaciones junto al borde superior de sus plantas, pero no poseen un líder o símbolo inequívoco en la capa de cargas. Se registra la coordenada de inserción del texto sólo como referencia documental; no es una posición de aplicación y no se asigna receptor. La carga lineal P4 sí conserva su banda HATCH y una línea central geométrica candidata, también sin aplicación mecánica.

## Zonas pendientes

- `P1 / BRASS / SC=500 / PM.ADIC=2800`: geometría alineada, unidad de `2800` aún `REVIEW_REQUIRED`.
- Cargas puntuales P2/P3: posición de aplicación y receptor `REVIEW_REQUIRED`.
- Carga lineal P4: eje central y receptor quedan como candidatos geométricos hasta comprobar el detalle/DWG.
- EDIFICIO_2 no fue promovido a confirmado en esta etapa; debe auditarse separadamente con `2024_22-700`.

## Overlays

- [S1](overlay_EDIFICIO_1_S1.png)
- [P1](overlay_EDIFICIO_1_P1.png)
- [P2](overlay_EDIFICIO_1_P2.png)
- [P3](overlay_EDIFICIO_1_P3.png)
- [P4](overlay_EDIFICIO_1_P4.png)

## Invariantes

- Q actual: intacto.
- G: intacta.
- `analysis_model.json`: intacto.
- Masas, EX/EY y superposición: intactas.
- OpenSees y Unity: no regenerados.
- `model_viewer.json` original de Luis: intacto.
