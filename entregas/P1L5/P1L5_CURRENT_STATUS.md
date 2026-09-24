# P1L5 CURRENT — estado de cargas, análisis y Unity

Estado: **PASS_WITH_EXPLICIT_UNRESOLVED**  
Rama: `codex/p1l5-integration`  
Geometría congelada respecto de `1d81b945fca7567bbf5aa8cc0bd374315a3d6a38`: **PASS**

## Correspondencia y alcance

`EDIFICIO_1 = LT1` (parte antigua) y `EDIFICIO_2 = LT2` (parte nueva). El Q histórico de aproximadamente 11.259 kN era parcial en ambos bloques: 9.130 kN en ED1 y cerca de 2.174 kN en ED2; no representaba un bloque completo ni el edificio completo.

## Catálogo y tributarias

- `CURRENT_RECONSTRUCTED`: 88 entradas.
- `HISTORICAL_FALLBACK`: 10 entradas de PP.LOSA a 0,15 m.
- `UNRESOLVED`: 8 entradas.
- `UNIT_CONFLICT_UNRESOLVED`: 2 entradas (conflicto 7600/800).
- Paños/zonas `CURRENT_RECOMPUTED`: 44. La exportación visual genera 49 polígonos exteriores porque cinco zonas multipolígono se dibujan por componente.
- Conservación G: residual 0.027813 N (3.671e-08 %), **PASS**.
- Conservación Q: residual -0.000000 N (-0.000e+00 %), **PASS**.

| Piso | Bloque | Área total m² | Área con Q m² | Área sin Q m² | Q kN |
|---|---:|---:|---:|---:|---:|
| P1 | LT1 | 997.042 | 997.042 | 0.000 | 3826.343 |
| P2 | LT1 | 843.914 | 843.914 | 0.000 | 3069.019 |
| P3 | LT1 | 956.721 | 956.721 | 0.000 | 2843.204 |
| P4 | LT1 | 934.561 | 934.561 | 0.000 | 1771.681 |
| S1 | LT1 | 387.863 | 387.863 | 0.000 | 1637.082 |
| P1 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P2 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P3 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P4 | LT2 | 535.620 | 535.620 | 0.000 | 1050.528 |
| S1 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |

Los huecos interiores se conservan y suman dentro de cada registro como exclusiones geométricas. `área sin Q = 0` significa que toda la superficie neta de las 44 zonas CAD confirmadas tiene una intensidad Q; no afirma que todo vacío arquitectónico esté cargado.

## G y Q frente a ETABS

| Magnitud | Nuestro LT1 kN | ETABS LT1 kN | Dif. | Nuestro LT2 kN | ETABS LT2 kN | Dif. | Nuestro total kN | ETABS total kN | Dif. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q / CV | 13147.329 | 11620.380 | +13.14% | 11201.813 | 11096.777 | +0.95% | 24349.143 | 22717.157 | +7.18% |
| G / CM | 44659.682 | 47140.276 | -5.26% | 31100.076 | 34723.194 | -10.43% | 75759.758 | 81863.470 | -7.46% |

Nuestro G se separa en 32901.991 kN de peso propio y 42857.767 kN de carga muerta adicional, para 75759.758 kN. No se forzó ETABS: las diferencias son coherentes con un modelo de barras sin losas FE, fallbacks documentados y cargas puntuales/lineales aún sin receptor o unidad inequívoca.

## Materiales

Hay 79 elementos estructurales con `INFERRED_MATERIAL_FALLBACK`; no se presentan como confirmados por plano. Se usa G35, `f'c = 35 MPa`, `E = 28 GPa`, `ν = 0,2`. Las 10 losas son geometría/tributarias/peso y no bloquean el FE.

## OpenSees CURRENT

- Estado: **PASS**; versión `P1L5_CURRENT_ZONED_V2`.
- 1.110 nodos FE, 633 segmentos físicos activos, 629 barras analizadas y 4 segmentos redundantes dentro de clusters rígidos omitidos para evitar lazos de deformación nula.
- 1.223 restricciones FE y 33 apoyos FE.
- G/Q/EX/EY: finitos, sin NaN ni infinitos, equilibrio **PASS**.
- Reacción vertical G: 75759.758 kN; Q: 24349.142 kN.
- Corte basal EX: 17586.866 kN; EY: 17586.866 kN.
- Desplazamientos máximos vectoriales: G 93.841 mm; Q 38.706 mm; EX 68.104 mm; EY 102.133 mm.

### Contraste vertical P3

| Bloque | Caso | Nodo CURRENT comparable | Uz CURRENT mm | Uz ETABS mm | Razón |
|---|---|---:|---:|---:|---:|
| LT1 | G | 482 | -4.617 | -5.060 | 0.91 |
| LT1 | Q | 482 | -1.366 | -1.466 | 0.93 |
| LT2 | G | 177 | -2.820 | -7.181 | 0.39 |
| LT2 | Q | 177 | -1.098 | -3.213 | 0.34 |

Es un contraste secundario de orden de magnitud: se usa el nodo retenido más cercano al centro geométrico de P3, no el mismo punto ETABS. Los períodos ETABS se registran, pero no se comparan directamente porque LT1/LT2 son modelos separados con diafragmas, mientras CURRENT es un marco combinado sin losas FE ni diafragma rígido.

## Unity CURRENT

- Contrato y hashes: **PASS**.
- Selector G/Q/EX/EY/R, deformada, N/Vy/Vz/T/My/Mz, gráficos 2D y superposición instantánea: **PASS**.
- Inspector CARGAS: área/ancho tributario, qQ, wQ, Q equivalente, peso propio, muerta adicional, zonas y fuentes: **PASS**.
- P–M y D/C usan demanda CURRENT combinada y capacidad compatible existente: **PASS_WITH_NOTE**.
- Cambiar λG/λQ/λEX/λEY solo superpone. Cambiar carga, sección, material, apoyo, `active` o tributaria marca `STALE_REANALYSIS_REQUIRED` hasta ejecutar nuevamente el pipeline.

## Pauta funcional P1L5

| Criterio | Estado |
|---|---|
| Interactividad | PASS |
| Modificación física → STALE / reanálisis | PASS |
| Superposición Unity sin reanálisis | PASS |
| Demanda-capacidad dinámica | PASS_WITH_NOTE |
| Defensa y criterios de reanálisis | PASS |

## Limitaciones explícitas

Siguen sin aplicarse 10 entradas: seis registros asociados a tres cargas puntuales sin punto/receptor inequívoco, dos registros de la carga lineal E2 P4 sin receptor confirmado y las dos entradas del conflicto de unidad 7600/800. `UNRESOLVED` nunca se interpreta como cero. `E1-P3-V-101` conserva su revisión geométrica documentada, sin impedir la corrida.
