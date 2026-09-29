# P1L5 CURRENT — estado de cargas, análisis y Unity

Estado: **PASS_WITH_EXPLICIT_UNRESOLVED**  
Rama: `codex/p1l5-integration`  
Geometría congelada respecto de `9172acc`: **PASS**

## Correspondencia y alcance

`EDIFICIO_1 = LT1` (parte antigua) y `EDIFICIO_2 = LT2` (parte nueva). El Q histórico de aproximadamente 11.259 kN era parcial en ambos bloques: 9.130 kN en ED1 y cerca de 2.174 kN en ED2; no representaba un bloque completo ni el edificio completo.

## Catálogo y tributarias

- `CURRENT_RECONSTRUCTED`: 88 entradas.
- `HISTORICAL_FALLBACK`: 10 entradas de PP.LOSA a 0,15 m.
- `UNRESOLVED`: 6 entradas.
- `RESOLVED_BY_REVIEW`: 2 entradas (líneas de fachada E1-P4, dual 7600/800).
- `RESOLVED_BY_REVIEW_SLAB_ROUTE`: 2 entradas (líneas E2-P4 vía losa/tira equivalente).
- `UNIT_CONFLICT_UNRESOLVED`: 0 entradas (conflicto 7600/800).
- Paños/zonas `CURRENT_RECOMPUTED`: 46 (44 zonas CAD + 2 tiras equivalentes de las cargas lineales E2-P4). La exportación visual genera 51 polígonos exteriores porque cinco zonas multipolígono se dibujan por componente y las dos tiras se exportan por separado.
- Conservación G: residual 0.027463 N (3.515e-08 %), **PASS**.
- Conservación Q: residual 0.000000 N (0.000e+00 %), **PASS**.

| Piso | Bloque | Área total m² | Área con Q m² | Área sin Q m² | Q kN |
|---|---:|---:|---:|---:|---:|
| P1 | LT1 | 997.042 | 997.042 | 0.000 | 3826.343 |
| P2 | LT1 | 843.914 | 843.914 | 0.000 | 3069.019 |
| P3 | LT1 | 956.721 | 956.721 | 0.000 | 2843.204 |
| P4 | LT1 | 934.561 | 934.561 | 0.000 | 2010.178 |
| S1 | LT1 | 387.863 | 387.863 | 0.000 | 1637.082 |
| P1 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P2 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P3 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |
| P4 | LT2 | 541.860 | 541.860 | 0.000 | 1099.482 |
| S1 | LT2 | 557.894 | 557.894 | 0.000 | 2537.821 |

Los huecos interiores se conservan y suman dentro de cada registro como exclusiones geométricas. `área sin Q = 0` significa que toda la superficie neta de las 44 zonas CAD confirmadas tiene una intensidad Q; no afirma que todo vacío arquitectónico esté cargado.

## G y Q frente a ETABS

| Magnitud | Nuestro LT1 kN | ETABS LT1 kN | Dif. | Nuestro LT2 kN | ETABS LT2 kN | Dif. | Nuestro total kN | ETABS total kN | Dif. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q / CV | 13385.826 | 11620.380 | +15.19% | 11250.768 | 11096.777 | +1.39% | 24636.594 | 22717.157 | +8.45% |
| G / CM | 46969.149 | 47140.276 | -0.36% | 31171.978 | 34723.194 | -10.23% | 78141.127 | 81863.470 | -4.55% |

Nuestro G se separa en 32945.738 kN de peso propio y 45195.389 kN de carga muerta adicional, para 78141.127 kN. No se forzó ETABS: las diferencias son coherentes con un modelo de barras sin losas FE, fallbacks documentados y cargas puntuales/lineales aún sin receptor o unidad inequívoca.

## Materiales

Hay 79 elementos estructurales con `INFERRED_MATERIAL_FALLBACK`; no se presentan como confirmados por plano. Se usa G35, `f'c = 35 MPa`, `E = 28 GPa`, `ν = 0,2`. Las 10 losas son geometría/tributarias/peso y no bloquean el FE.

## OpenSees CURRENT

- Estado: **PASS**; versión `P1L5_CURRENT_ZONED_V2`.
- 1,100 nodos FE, 623 segmentos físicos activos y 619 barras analizadas.
- 1,225 restricciones FE y 33 apoyos FE.
- G/Q/EX/EY: finitos, sin NaN ni infinitos, equilibrio **PASS**.
- Reacción vertical G: 78141.127 kN; Q: 24636.594 kN.
- Corte basal EX: 17638.741 kN; EY: 17638.741 kN.
- Desplazamientos máximos vectoriales: G 96.853 mm; Q 38.702 mm; EX 66.978 mm; EY 99.288 mm.

### Contraste vertical P3

| Bloque | Caso | Nodo CURRENT comparable | Uz CURRENT mm | Uz ETABS mm | Razón |
|---|---|---:|---:|---:|---:|
| LT1 | G | 482 | -4.715 | -5.060 | 0.93 |
| LT1 | Q | 482 | -1.376 | -1.466 | 0.94 |
| LT2 | G | 177 | -2.816 | -7.181 | 0.39 |
| LT2 | Q | 177 | -1.095 | -3.213 | 0.34 |

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
