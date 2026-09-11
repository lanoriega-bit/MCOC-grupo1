# PROJECT_HANDOFF.md

Transferencia tecnica completa del proyecto "Laboratorio estructural digital 3D de un edificio real".
Fecha de revision: 2026-09-11. Base P1L3 integrada: `beb0006`.
Este documento NO repite planificacion P1L3: eso vive en `entregas/P1L3/PLANIFICACION.md`.

Estado vigente: P1L3 ya esta implementado e integrado en el Unity de Jose. Los
casos reales `G/Q/EX/EY/R`, resultados OpenSees y capacidad HA se adaptan a
`Assets/StreamingAssets`; la interfaz principal tiene filtros, inspector,
graficos ampliables y modo presentacion. Ver `entregas/P1L3/INFORME.md` y
`entregas/P1L3/UI_QA.md`. No volver a tratar P1L3 como "solo planificado".

## POST-P1L3 CONSOLIDATED BASELINE — EN CONSTRUCCION

- Snapshot entregado preservado: tag `P1L3_DELIVERED` en
  `c847c131512d00cc85bb95aa5719278d70da0c2b`.
- Rama vigente de consolidacion: `codex/pre-p1l4-consolidation`.
- Backlog maestro y auditoria de ramas/canonicos:
  `PRE_P1L4_CLEANUP.md`.
- No se inicia P1L4 y no se sobrescriben resultados A7. Las futuras salidas se
  identificaran `POST_P1L3_VALIDATED`.
- FASE 0 cerro la preservacion y el inventario sin merges de ramas historicas.
- FASE 1 cerro las seis columnas S1: las elevaciones 309/I y 310/I' muestran
  pilares 70x70 continuos hasta fundacion en 1/2/3. Los seis elementos estan
  `CONFIRMED_BY_AXIS_ELEVATION` y normalizados a sus intersecciones canonicas.
  Evidencia: `entregas/P1L2/edificio/validacion/s1_columns_final/REPORT.md`.
- FASE 2 consolidó las caras DXF de muro: 134 prismas ED1 pasaron a 67
  segmentos analíticos, con espesor medido, y los apoyos lineales S1 pasaron de
  60 a 21. Evidencia y overlays: `entregas/P1L2/edificio/validacion/ed1_walls/`.
- FASE 3 cerró las vigas ED1: 553 trazos `RLE-VIGA` se resolvieron en 300
  centrolineas, reemplazando 545 prismas. Se excluyeron 46 cierres y 4 detalles
  interiores, sin caras largas/diagonales pendientes. Ancho 300/300; altura
  281 con evidencia inequívoca y 19 `UNKNOWN`. Evidencia:
  `entregas/P1L2/edificio/validacion/ed1_beams/`.
- FASE 4 cerró la geometría estructural especial: la elevación 308/H confirmó
  tres columnas S1 y apoyos; un contorno cerrado añadió el muro dilatado local
  S1. La interfaz D/E fue auditada y no existe conexión entre edificios
  demostrada. ED1 queda con 524 sólidos, combinado 1212 y 0 elementos
  `UNRESOLVED_REQUIRES_REVIEW`. Evidencia: `validacion/special_interface/`.
- FASE 5 está en diagnóstico de losas. La lectura directa `RLE-LOSA(S)` muestra
  contornos fragmentados: ED1 tiene 4/26/22/19/37 extremos abiertos en
  S1/P1/P2/P3/P4 y ED2 22/22/22/22/26. La lámina 2024_22-101 confirma por
  título una planta común desde cielo S1 hasta cielo P3; tres trazos del JSON
  derivado quedaron fuera de la región de planta aprobada. Los cierres
  colineales automáticos no resuelven el perímetro principal y no se han
  modificado superficies, FE ni resultados. Evidencia:
  `entregas/P1L2/edificio/validacion/slabs/`.
- La propuesta exterior ED2 queda en 565.392 m² para S1-P3 y 566.465 m² para
  P4, sin lados exteriores `REVIEW_REQUIRED`; aún no se aplica porque los
  trazos interiores no distinguen inequívocamente hueco de borde de paño. El
  bloque `losa-ne` aparece repetido por toda la planta y no prueba ausencia de
  losa.
- En ED1, P2 tiene un candidato de 806.605 m² y P3 de 914.175 m², sin lados
  exteriores pendientes. S1 carece de borde exterior RLE-LOSA y P1 contiene
  una transición norte/outboard que todavía no forma un perímetro único; no se
  aplican por envolvente ni se copian desde otros pisos.
- Proximo paso: reconstruir perímetros y huecos piso a piso con respaldo de
  `RLE-LOSA`, vigas y notas, conservando `participates_in_FE=false` para la
  arquitectura visual.

---

## QUICK START FOR NEXT AGENT

1. Lee este archivo completo (`PROJECT_HANDOFF.md`).
2. Lee `entregas/P1L2/STATUS.md` (estado P1L2 al dia).
3. Lee `entregas/P1L3/PLANIFICACION.md` (plan G/Q/EX/EY/capacidad; NO lo reescribas).
4. Revisa `git status`, `git log --oneline -15`, `git branch -a` y `git fetch --all --prune` antes de tocar nada.
5. Archivos esenciales para entender la geometria:
   - `entregas/P1L2/unity_export/model_combined_viewer.json` (modelo VIGENTE).
   - `entregas/P1L2/unity_export/model_1_audited_corrected.json` (EDIFICIO_1 corregido).
   - `entregas/P1L2/unity_export/model_2_viewer.json` (EDIFICIO_2).
   - `entregas/P1L2/edificio/datos/global_axes.json` (ejes canonicos).
   - `entregas/P1L2/edificio/datos/luis_inferred_column_resolution.json` (clasificacion columnas).
   - `entregas/P1L2/edificio/datos/building_master.json` y `building_2_master.json` (modelos logicos).
6. NO modifiques: `entregas/P1L2/unity_export/model_viewer.json` (referencia Luis, read-only), el working tree de otras personas, ni `recursos/` (ignorado por Git). Nunca: `force push`, `reset --hard`, `git clean`, borrar trabajo ajeno.
7. Estado de geometria: EDIFICIO_1 auditado-corregido 524 solidos; EDIFICIO_2 688; combinado 1212 solidos en 5 pisos (S1/P1/P2/P3/P4). Ver seccion 8.
8. Proximo trabajo recomendado: no reiniciar lo hecho. Continuar con losas y arquitectura visual ED1/ED2 y luego el resto de la consolidacion PRE-P1L4. No
reabrir las seis columnas I/I' de S1 salvo contradiccion primaria: ya fueron
confirmadas directamente en 309/310.

Reglas Git obligatorias (ver seccion 20): cada hito = VALIDAR -> STATUS.md -> COMMIT -> PUSH; commits P1L2 y P1L3 separados.

---

## 1. QUE ES EL PROYECTO

- Objetivo: construir un laboratorio estructural digital 3D de un edificio real (Edificio de Ingenieria), usando:
  - **OpenSees** (analisis estructural, elasticidad lineal 3D); las losas NO se modelan por FE: la carga de piso = peso propio de losa + terminaciones uniformes, transferida por areas tributarias.
  - **Unity / viewer web** (visualizacion, preprocesamiento e interaccion); JSON es el contrato entre ambos.
  - **Capacidad HA** separada del modelo global (secciones RC, M-phi, P-M).
- Entregas por etapas:
  - P1L0: benchmark 2D minimo (OpenSees + calculo manual independiente).
  - P1L1: benchmark 3D de un portico simple.
  - P1L2: edificio real completo 3D auditado (geometria, ejes, calce, ids, viewer) - trabajo actual.
  - P1L3: carga viva Q, sismo pseudoestatico EX/EY, superposicion y capacidad HA integrados en OpenSees/JSON/Unity.
- El edificio tiene DOS ala/partes del mismo edificio:
  - EDIFICIO_1 (ED1): serie de planos 2017_67, ejes E..J.
  - EDIFICIO_2 (ED2): serie de planos 2024_22, ejes A..D.
- Unidades: SI (m, N, Pa); cargas de planos en kgf/m2 convertidas a kN/m2.

## 2. HISTORIA TECNICA (por que el pipeline es como es)

Enfoque inicial fallido:

```
planos -> interpretacion directa -> 3D   (genero errores graves)
```

Problemas concretos del enfoque inicial que cambiaron el rumbo:
- Se creaba/copiaba geometria verticalmente cuando faltaba evidencia del mismo piso (p.ej. el extractor historico `entregas/P1L2/opensees/extract_cad_model.py`).
- Se podian generar "supports" artificiales desde esas columnas inferidas.
- Sin sistema de coordenadas formal, las dos alas no calzaban de forma verificable.

Pipeline actual (aprobado y en produccion):

```
planos/DXF -> extraccion CAD -> ejes canonicos -> sistemas de coordenadas
  -> pisos reales -> elementos estructurales -> auditoria -> modelo combinado
  -> enriquecimiento -> validaciones -> viewer
```

Regla central evolucionada: primero se construye un MODELO LOGICO por piso (building_master) y recien despues el 3D; el 3D SIEMPRE se valida contra planos, no al reves. Esto impide que "auto-inferencias" de un script se conviertan en verdad.

## 3. REGLAS FUNDAMENTALES (no negociables)

- **Pisos**: el edificio tiene EXACTAMENTE `S1, P1, P2, P3, P4` (`EXPECTED_FLOORS = 5`). Fundacion, radier, cielo, losa superior, base y diafragmas NO son pisos adicionales. Niveles auxiliares se marcan `level_kind` (FOUNDATION_LEVEL, etc.), nunca `FLOOR`.
- **Planos**: `2017_67` = EDIFICIO_1; `2024_22` = EDIFICIO_2. Son dos partes del MISMO edificio.
- **Ejes**: un mismo eje conserva su posicion XY entre pisos. Los ejes son la referencia principal del calce.
- **Union de edificios**: `EDIFICIO_2:D <-> EDIFICIO_1:E`. `CALCE_A = AXIS_CONFIRMED` con residual ~9 mm (dx global = +27.491 m para ED1).
- **Jerarquia de evidencia**:
  ```
  PLANOS > EJES / COTAS / NOTAS / DETALLES > MODELO AUDITADO > MODELO ORIGINAL DE LUIS > INFERENCIA
  ```
- **Convencion S1**: el plano "planta cielo 1º subterraneo" (2017_67-101, region S1) NO dibuja columnas como `RLE-PILAR` en piso 1; por eso **ausencia de RLE-PILAR en S1 != ausencia de columna**. Se usa la columna confirmada del piso P1 arriba mas la evidencia de estructura de subterraneo.

## 4. EL MODELO DE LUIS (conservar historia)

- `entregas/P1L2/unity_export/model_viewer.json` fue una referencia MUY buena de EDIFICIO_1, pero contiene geometria creada con inferencias automaticas (columnas copiadas verticalmente y supports derivados) cuando faltaba evidencia del mismo piso.
- Por eso Luis ya NO es verdad absoluta. Su archivo queda como `REFERENCE_READ_ONLY` y NO se modifica (`LUIS_REFERENCE_FILES_MODIFIED = 0`; validacion `LUIS_REFERENCE_DIFF_VALIDATION` y overlays lo vigilan).
- Nuestro modelo auditado/corregido tiene prioridad cuando existe evidencia de planos. La auditoria de inferencias esta en `luis_inferred_column_resolution.json`; el diff contra la referencia en `luis_reference_diff.json`.

## 5. ESTADO ACTUAL DE EDIFICIO_1 (conteos vigentes)

Fuente: `model_1_audited_corrected.json` (LOCAL-ED1) + `luis_inferred_column_resolution.json` + STATUS.md.

- Pisos: `1S, 1, 2, 3, 4` + `base` (40 supports, nivel auxiliar).
- Solid plan total: **522** (beam 300, wall 67, column 110, support 40, slab 5).
- Desde los 927 sólidos originales se retiraron 39 columnas inferidas, 15
  apoyos derivados inválidos y representaciones duplicadas/de detalle de
  muros, vigas y apoyos. Cada consolidación conserva su crosswalk y motivo.
- Columnas por piso (ED1, total 110): S1 19, P1 26, P2 21, P3 18, P4 26.
- **Clasificacion S1 (ultimas 19 columnas)**:
  - 10 `CONFIRMED_BY_BASEMENT_EVIDENCE` (X<=49.2 global, o sea zona oeste con estructura de subterraneo).
  - 3 `LIKELY_CORRECT` (slab-edge/transicional, 49.2<X<=60).
  - 6 `CONFIRMED_BY_AXIS_ELEVATION` = `E1-S1-C-014..019` (ejes I/I' × 1/2/3), verificadas en elevaciones 309/310 como pilares 70x70 continuos hasta fundacion.
- 39 columnas rechazadas incluyen: 24 estaciones east-edge IB/J (P4-only, sin pilar en S1-P3 ni pedestal de fundacion) + outboard G/H de P2 + otros outboard.
- Nucleo (core): `CORE_AXIS_CONTINUITY` PASS (nucleo identificado como bay de ejes con muros en S1..P4).
- Muros ED1: auditoría exhaustiva cerrada; 67 segmentos analíticos confirmados y 0 caras sin clasificación.
- Vigas ED1: 300 centrolineas; ancho 300/300, altura 281 con evidencia inequívoca y 19 `UNKNOWN`; 0 caras largas/diagonales sin resolver.
- Zonas outboard (salas sobresalientes): hay reconstruccion documentada en `outboard_room_reconstruction.json` con grupos `UNRESOLVED_REQUIRES_REVIEW` (ver seccion 17).

## 6. ESTADO ACTUAL DE EDIFICIO_2

Fuente: `model_2_viewer.json`, `building_2_master.json`, `edificio_2_levels_review.json`, `extract_cad_model_ed2.py`.

- Planos: `2024_22-100.dxf` (fundaciones/radier), `-101` (cielos S1..P3 superpuestos), `-102` (P4). Serie LT2, ala secundaria ejes A..D.
- Extractor propio: `entregas/P1L2/edificio/scripts/extract_cad_model_ed2.py` -> `building_2_master.json` -> `model_2_viewer.json` (**688 solidos**).
- Ejes canonizados en `global_axes.json`: X A=0, B=7.5, C=17.5, D=27.5; Y 1/2/3 = 0/8.9/16.15. Origen por lamina = interseccion eje A x eje 1.
- Sistema Z: datum radier = -7.97 m (model z 0.0); modulo de piso 3.96 m: S1=3.96, P1=7.92, P2=11.88, P3=15.84, P4=19.8. Elevacion de S1/P1/P2/P3 es INFERIDA desde P4(+11.83) y el datum porque la lamina 101 superpone cielos; N.O.G/N.S.M/N.R son notas locales, NO pisos.
- `floor_validation`: PASS con `["S1","P1","P2","P3","P4"]` (orden canonico).
- Resumen por piso (building_2_master): S1: column_plan 65, wall 58, beam 179; P1-P3 simetricos (column 32, wall 29, beam 90); P4: column 32, wall 28, beam 160.
- Incertidumbres conocidas: elevaciones S1-P3 inferidas; lamina 101 superpuesta; la integracion con ED1 esta validada por ejes (CALCE_A) pero el registro persistente de IDs de ED2 requiere cuidado (ver seccion 10).
- CONFIRMED vs INFERRED: ejes y levels FLOOR = CONFIRMED (salvo elevaciones S1-P3 = INFERRED); envolvente 3D = modelo computable generado.

## 7. SISTEMA DE COORDENADAS Y EJES (leer `global_axes.json`, `axis_calce_validation.json`)

- **Global**: el origen (0,0,0) es `A-1` de EDIFICIO_2. EDIFICIO_2 local = global (dx 0).
- **EDIFICIO_1 local**: eje E = 0 local; global = local + `dx_m=27.491`. Transformacion del combinado: ED1 `{dx:27.491,dy:0,rot:0,scale:1}` status `AXIS_CONFIRMED`; ED2 identidad.
- `ejes.json` (los globales del draft viejo, con Y 2=10 y 3=17.25) esta en `DRAFT_NEEDS_REVIEW` y queda SUPERADO por `global_axes.json`. No usarlo como fuente de verdad.
- Ejes canonicos ED1 (locales, m): X: E=0, Ea=3.3, Eb=3.6, Ec=6.4, Ed=6.7, F=10, G=20, Ga=21.45, H=30, H1=33.825, H'=34.477, H2=38.825, I=40, IA=42.6, I'=45, IB=45.875, J=50. Y: 1=0, 1''=3.9, 2=8.9, 2a=13.845, 3=16.15. Primarios: E,F,G,H,I,J y 1,2,3; el resto secundarios (RLE-EJE + cotas).
- Ejes ED2 (m): X A=0, B=7.5, C=17.5, D=27.5; Y 1=0, 2=8.9, 3=16.15 (todos canonicos; en el DXF ademas hay A', C', D', 1A' etc.).
- Z: `niveles.json` z_offset=7.97; model_z: fund 0.0, 1S 3.96, 1 7.92, 2 11.88, 3 15.84, 4 19.8; source_elevation: -7.97, -4.01, -0.05, 3.91, 7.87, 11.83.
- Tolerancias: calce D/E <= 0.02 m (residual real 0.009); Y comun tol 0.001; asociacion ejes tol 0.35 m (`column_axis_matrix`).

## 8. MODELOS / JSON IMPORTANTES (tabla)

| Archivo | Funcion | Estado | Vigente | Generado | Read-only | Consumido por |
|---|---|---|---|---|---|---|
| `unity_export/model_viewer.json` | Referencia original de Luis (ED1) | GOLDEN/REFERENCE de Luis; contiene inferencias | NO (referencia) | historico | SI (protegido) | `audit_luis_reference`, `validate_luis_reference_diff`, overlays, diff |
| `unity_export/model_viewer_candidate.json` | ED1 3D candidato directo desde DXF | superseded | NO | SI (phase6_build_3d.py) | - | phase7/8, goldens viejos |
| `unity_export/model_1_audited.json` | ED1 auditado (pre-correccion, 927 solidos) | checkpoint de auditoria | NO | SI (audit) | - | resolution |
| `unity_export/model_1_audited_corrected.json` | ED1 corregido (524 solidos) | VIGENTE ED1 | SI | SI (columnas + consolidación de muros/vigas + muro dilatado S1) | - | `build_combined_model.py`, viewer (dropdown) |
| `unity_export/model_2_viewer.json` | ED2 (688 solidos, ejes A-D) | VIGENTE ED2 | SI | SI (extract_cad_model_ed2) | - | `build_combined_model.py`, viewer (dropdown) |
| `unity_export/model_combined_viewer.json` | MODELO COMBINADO FINAL (1212 solidos, 3808 segmentos, 871 labels, 10 diaphragms) | VIGENTE - modelo que el grupo debe revisar | SI | SI (build_combined_model + enrich) | - | viewer por defecto; validaciones; P1L3 |
| `edificio/datos/global_axes.json` | Ejes canonicos y regla de pisos | `AXES_CANONICALIZED_FROM_DXF` | SI | SI (extract_axes.py) | - | casi todos |
| `edificio/datos/building_master.json` | Modelo logico consolidado ED1 | `LOGICAL_MODEL_REEXTRACTED_READY_FOR_3D` | medio | SI (phase5) | - | phase6 |
| `edificio/datos/building_2_master.json` | Modelo logico ED2 | floor_validation PASS | SI | SI (ed2 extractor) | - | model_2_viewer |
| `edificio/datos/luis_inferred_column_resolution.json` | Clasificacion de las 61 columnas inferidas + findings top | `PASS_WITH_CORRECTIONS_AND_UNRESOLVED_ITEMS` | SI | SI | - | decisiones |
| `edificio/datos/luis_reference_diff.json` | Diff trazable ED1 corregido vs referencia Luis | vigente con columnas y consolidación de muros/vigas/apoyos | SI | SI | - | validate_luis_reference_diff |
| `edificio/datos/outboard_room_reconstruction.json` | Reconstruccion histórica de salas/outboard | SUPERSEDED por evidencia DXF completa de FASE 4 | NO | SI | - | antecedente |
| `edificio/validacion/special_interface/` | Auditoría de geometría especial, eje H, muro dilatado e interfaz D/E | PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED | SI | SI | - | FASE 5 losas/arquitectura y futura conectividad FE |

Observacion: `model_combined_viewer.json` es el archivo que debe revisar el grupo y sobre el que se enriquecen ids/ejes/propiedades.

## 9. IDS Y TRAZABILIDAD

Cadena objetivo: `plano -> entidad -> ID estable -> elementTag -> viewer -> OpenSees`.

- Formato de ID: `E{1|2}-{S1|P1|P2|P3|P4}-{C|V|M|A|L|D}-###` (C columna, V viga, M muro, A apoyo, L losa, D diafragma).
- Por solido se guarda: `id`/`human_id` (iguales hoy), `solidTag`/`legacy_solidTag`, `elementTag` (TEXTO de geometria: `SOL[2]?_<piso>_<tipo>_####`), `sourceTag(s)` (CAD...), `axis_location`, `coordinates`, `confidence`, `building`, `source_sheet`.
- Ejemplos reales del combinado:
  - Columna: `E2-S1-C-002` / `SOL2_1S_column_0001` (0.70x0.70, RLE-PILAR, 2024_22-101).
  - Viga: `E2-S1-V-030` / `SOL2_1S_beam_0001` (RLE-VIGA).
  - Muro: `E2-S1-M-019` / `SOL2_1S_wall_0001` (RLE-MURO).
  - ED1 columna: `E1-S1-C-017` / `SOL_1S_column_0016`.
- **Los IDs sobrevivientes son estables**. Los gap producidos por elementos eliminados son INTENCIONALES (tombstones). NO renumerar para cerrar gaps.
- **Advertencia P1L3**: `elementTag` actual es texto geometrico, NO es el entero de elemento OpenSees. Hacen falta extremos con referencias persistentes (nodeI/nodeJ) y un crosswalk. Ejemplo `E1-P2-C-034` NO existe hoy; no reciclar IDs retirados. Ver PLANIFICACION.md seccion 7.1.
- EDIFICIO_2 necesita un registro persistente de IDs para evitar renumerar al regenerar (`extract_cad_model_ed2`).

## 10. VIEWER

- Abrir (desde la raiz del repo): `python -m http.server 8000` y luego `http://localhost:8000/entregas/P1L2/viewer/` (el batch `Abrir_Viewer_Semana2.bat` lo automatiza). No abrir `index.html` directo (CORS bloquea el JSON).
- Carga por defecto `model_combined_viewer.json` (tambien `?model=model_combined_viewer.json`).
- Controles: orbitar (izq), zoom (rueda), pan (der); vistas Lado A/B/C/D; Vista planta; toggle IDs; selector de modelo (combinado/ED1 candidato/ED2/GOLDEN Luis); toggles por Piso y Solo; toggles por Tipo (vigas, muros, pilares, apoyos, ejes, diafragmas, borde losa); Buscar elemento por `elementTag`.
- Seleccion (click) muestra: elementTag, tipo, piso, dimensiones (m), capa CAD, plano fuente, edificio, piso canonico/fuente, ejes/ubicacion relativa, seccion/espesor/material si existe, confianza. Guia de ejes locales (x rojo, y verde, z azul).
- Limitaciones: Three.js venga de CDN (requiere internet); es visualizacion/preprocesamiento (no analiza); los supports se renderizan; los resultados de OpenSees no estan integrados (pendiente P1L3).

## 11. PROPIEDADES ESTRUCTURALES EXTRAIDAS

Fuente: `cad_property_audit.json` (PASS_WITH_REVIEW_NOTES) y `enriched_model_validation.json`.

- Columnas: 150/150 con dimensiones (la mayoria 0.70x0.70; casos especiales 0.85x0.92). Clasificacion: `CONFIRMED_FROM_PLAN` (66 por geometria CAD RLE-PILAR) + asociacion de etiquetas cuando existe.
- Vigas: solo ~431/1060 con seccion conocida por etiqueta de texto (ej: `V. 20/130` S1, `V. 20/80` S1/P1, `V. 20/90`, `V. 30/45` P2, `V. 30/80` ED2...). El resto: `UNKNOWN` (geometria del solido en width/height pero sin etiqueta de seccion).
- Muros ED1: 67/67 con espesor confirmado por pares de contorno; 58 también coinciden con etiqueta y 9 son confirmación geométrica exclusiva. ED2 permanece pendiente de auditoría equivalente.
- Apoyos: 3/107 con dimensiones conocidas; resto `DEFAULT`/`UNKNOWN`.
- Materiales: solo hints del tipo `M.H.A.` (hormigon armado) en etiquetas; NO hay f'c/fy, recubrimiento ni armadura confirmada (seccion 14 de PLANIFICACION: `DEPENDENCIA_PENDIENTE`). No inventar armadura.

## 12. OPENSEES Y GRAVEDAD: QUE EXISTE Y QUE PUEDE USAR EL GRUPO HOY

Fuente: repositorio actual en `main` (sin integrar ramas).

- `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py`: benchmark 3D valido (elasticidad lineal, diagramas N/V/M), con `verificacion.json`. Reusar en P1L3 para vetar NVM del edificio.
- `entregas/semana2/opensees/edificio_completo.py` y `edificio_completo_2bloques.py`: modelos 3D de RETICULA IDEALIZADA (no del modelo combinado) con gravedad `q_G=6.35 kN/m2`, `SC=2.5 kN/m2`, `rigidDiaphragm`, 1/4 del vano por borde, chequeo de equilibrio. Resultados en `results/verificacion*.json`. Metodologia reutilizable, geometria idealizada.
- `entregas/semana3/tarea8_superposicion/opensees/superposicion_GQ.py`: superposicion G/Q VALIDADA (R(G+Q)=R(G)+R(Q)) en reacciones y desplazamientos (no compara fuerzas internas). `status` en `results/superposicion_GQ.json`. Base directa para la Parte C P1L3.
- `entregas/P1L2/opensees/building_gravity_skeleton.py`: esqueleto preliminar de gravedad del modelo auditado (cargas nodales, qG=6.227), NO conectado al combinado y con tributarias pendientes (TODO). Punto de partida, no producto.
- `entregas/P1L2/opensees/extract_cad_model.py`: HISTORICO - es el extractor que creaba inferencias verticales de columnas y supports. Documentar/depurar esa logica, no reusarla como extraccion valida.
- Motores de terceros SOLO en ramas (no fusionadas): `origin/luis-gravedad-tributarias` (`carga_gravedad.py`, `integracion.py`, `qa_verificaciones.py` = nucleo tributario + QA mas completo) y `origin/e2-work` (E2/E12, no final). Ver PLANIFICACION.md secciones 4.2-4.4 para el port selectivo.
- `entregas/P1L2/data/load_definitions_draft.json`: catalogo G (qG por espesor: 12cm=5.492, 15cm=6.227, 18cm=6.963 kN/m2; PM.ADIC 260; SC variable 250/300/400/500 segun zona). status: draft.
- **Que puede usar el grupo hoy**: patrones de benchmarks validados, motor tributario (adaptandolo), QA y superposicion validada. **Que FALTA**: gravedad conectada al modelo combinado, validacion de conservacion (sum Q = q*A), y cualquier caso Q/EX/EY sobre geometria vigente.

## 13. PIPELINE REAL DE REGENERACION (HOW TO REBUILD)

Ubicacion: `entregas/P1L2/edificio/scripts/` (+ `entregas/P1L2/opensees/` para ED2/historico).

| Paso | Script | Entrada (local) | Salida | Depende de |
|---|---|---|---|---|
| 0 | (manual) herramientas CAD | DWG originales NO versionados | `recursos/planos/dxf_generated/*.dxf` | AutoCAD Core Console (`tools/convert_dwg_to_dxf.py`), DWG |
| 1 | `extract_axes.py` | DXF 2017_67-100..103 y 2024_22-100..102 | `datos/global_axes.json` | DXF |
| 2 | `phase1_analyze_regions.py` | mismos DXF | `datos/dxf_region_analysis.json` | DXF |
| 2b | `phase1b_region_map.py`, `phase2_regions.py`, `phase3_region_specs.py` | DXF | `datos/region_specs.json` (bbox por piso real) | region analysis |
| 3 | `phase3_reextract_floors.py` (reusa nucleo de `extract_piso_01.py`) | DXF + region_specs | `datos/fundacion.json`, `subterraneo_01.json`, `piso_01..04.json`, `reextraction_summary.json` | DXF + specs |
| 3b | `phase3b_calibrate_y.py` (+ `phase3d_apply_calibration.py`) | pisos reextraidos | `datos/calibration_offsets.json`, `alignment_final.json` | pisos |
| 4 | `phase4_continue_from_reextract.py`; `phase5_build_master_and_checks.py` | pisos + alignment | `datos/building_master.json`, `conflicts_global.json`, `niveles.json`, `planos_index.json` | pisos alineados |
| 5 | `phase6_build_3d.py` | building_master | `unity_export/model_viewer_candidate.json` (+ `building_to_3d_map.json`) | master |
| 5b | `phase7_validate_3d.py`, `phase8_vertical_continuity.py` | candidate | validaciones de candidato | candidate |
| 6 | `audit_luis_reference.py` | candidate + `model_viewer.json` | `luis_reference_audit.json`, `model_1_audited.json` | red de referencia |
| 7 | `resolve_luis_inferred_columns.py` | audited + DXF (100-103) + `fundacion.json` + P1 model | `luis_inferred_column_resolution.json`, `luis_reference_diff.json`, `model_1_audited_corrected.json` (+ overlays) | audited + DXF |
| 7b | `validate_luis_reference_diff.py` | corrected + reference | `luis_reference_diff_validation.json` | corrected |
| 7c | `audit_s1_axis_h.py`, `audit_ed1_dilatation.py`, `apply_s1_axis_h.py`, `apply_ed1_dilatation_wall.py`, `audit_special_interface.py` | elevaciones 308, plantas 101–103, serie completa y modelo corregido | evidencia `validacion/special_interface/`, ED1 corregido y decisión de interfaz | corrected + DXF |
| 8 | `extract_cad_model_ed2.py` (en `opensees/`) | DXF 2024_22-100/101/102 | `building_2_master.json`, `edificio_2_levels_review.json` -> `model_2_viewer.json` | DXF |
| 9 | `build_combined_model.py` | corrected ED1 + model_2_viewer | `model_combined_viewer.json` + `combined_model_validation.json` | ambos modelos |
| 10 | `build_column_axis_matrix.py` | combined | `column_axis_matrix.{json,csv}` | combined |
| 11 | `validate_axes_and_calce.py`; `validate_combined_geometry.py`; `validate_core_axis_continuity.py`; `validate_golden_in_combined.py` (SUPERSEDED) | combined + global_axes | `axis_calce_validation.json`, `combined_geometry_validation.json`, `core_axis_continuity.json`, `golden_in_combined_validation.json` | combined |
| 12 | `audit_cad_properties.py` | combined | `cad_property_audit.json` | combined |
| 13 | `enrich_combined_model.py` | combined + column_axis_matrix | ids/ejes/propiedades + `enriched_model_validation.json` | combined |
| 14 | `visual_audit_combined.py` | combined | `validacion/visual/visual_audit_combined.json` + PNG | combined |

Si se cambia geometria de ED1, se DEBE regenerar: `model_1_audited_corrected.json` (paso 7) y luego `model_combined_viewer.json` (paso 9) antes de push. Revisiones humanas bloqueantes: `revision_humana_calce.py` y `revision_humana_niveles.py`.

## 14. RECURSOS LOCALES NO VERSIONADOS (CRITICO)

- `recursos/planos/dxf_generated/2017_67/` (100..103) y `2024_22/` (100..102) estan IGNORADOS por Git (`.gitignore`: `recursos/planos/`; igual `entregas/P1L2/results/`).
- Por eso NO aparecen en GitHub. Casi todos los scripts del apartado 13 los leen por ruta exacta configurada (ver `dxf_availability` en `luis_inferred_column_resolution.json`). Sin estos archivos el pipeline no corre.
- Como se generan: los DXF son conversiones de DWG originales (no versionados) mediante AutoCAD Core Console con `tools/convert_dwg_to_dxf.py` (DXFOUT v16). Requiere AutoCAD (`C:\Program Files\Autodesk\AutoCAD 2026\accoreconsole.exe`). Si se abre el repo en otra maquina SIN estos DXF, primero hay que regenerarlos/repartirlos (mismo `recursos/` o mismo path) antes de correr extraccion/validaciones.
- Los `piso*.json` y `*.json` de `datos/` SI estan versionados (son las extracciones ya procesadas), asique el viewer y las validaciones finales funcionan sin los DXF; solo la regeneracion los necesita.

## 15. VALIDACIONES (tabla)

| Validacion | Que comprueba | Resultado actual | Archivo |
|---|---|---|---|
| AXES / CALCE_A | Un ejercicio D/E de PE2 con PE1, residual 9 mm | `AXIS_CONFIRMED` | `axis_calce_validation.json` |
| COLUMN_AXIS_MATRIX | 150 col en 42 estaciones; tol 0.35 m; matriz por piso | `PASS_WITH_OFF_AXIS_NOTES` | `column_axis_matrix.json/.csv` |
| CAD_PROPERTY_AUDIT | Etiquetas de seccion/espesor por solido | `PASS_WITH_REVIEW_NOTES` | `cad_property_audit.json` |
| ENRICHED_MODEL | ids/ejes/propiedades completos en combinado | `PASS` | `enriched_model_validation.json` |
| CORE_AXIS_CONTINUITY | Nucleo con muros en S1..P4 dentro del bay de ejes | `PASS` | `core_axis_continuity.json` |
| COMBINED_GEOMETRY | Geometria del combinado contra global_axes | `PASS` | `combined_geometry_validation.json` |
| COMBINED_MODEL | Modelo combinado (pisos, contracto) | `PASS` | `combined_model_validation.json` |
| VISUAL_AUDIT | Overlays/render del combinado | `PASS` | `validacion/visual/visual_audit_combined.json` |
| LUIS_REFERENCE_DIFF | ED1 corregido vs referencia, incluidos muros/apoyos consolidados | `PASS`; original de Luis intacto | `luis_reference_diff_validation.json` |
| ED1_BEAM_PROPOSAL / FINAL | 553 trazos contabilizados y 300 centrolineas aplicadas | `PASS` / `PASS` | `validacion/ed1_beams/BEAM_PROPOSAL_VALIDATION.md`, `VALIDATION.md` |
| SPECIAL / INTERFACE | Eje H, muro dilatado, remates D/E y ausencia de conexión entre bloques | `PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED` | `validacion/special_interface/REPORT.md` |
| GOLDEN_IN_COMBINED | Igualdad con golden de Luis | `SUPERSEDED_BY_LUIS_REFERENCE_DIFF` | `golden_in_combined_validation.json` |
| FLOOR CONTRACT | 5 pisos canonico (por modelo) | `PASS` | `building_2_master.floor_validation`, `model_2_viewer/model_viewer_candidate.expectedFloors` |

Nota: `AXIS_CONFIRMED` y las validaciones anteriores corresponden al modelo
POST-P1L3 vigente. Al modificar geometria deben re-correrse las dependientes.

## 16. P1L2 - STABLE / TERMINADO vs OPEN / PENDIENTE

STABLE / TERMINADO:
- Pipeline DXF -> modelo logico -> 3D -> auditoria -> combinado -> enriquecido -> validado.
- ED1 auditado-corregido (524 solidos) con columnas S1 cerradas y muros/vigas consolidados desde sus caras DXF.
- 15 supports derivados eliminados; east-edge IB/J P4-only rechazados.
- Muros ED1: 67 segmentos regulares más 1 muro dilatado especial confirmados;
  72 cierres de contorno excluidos; 22 apoyos lineales S1.
- Vigas ED1: 300 centrolineas confirmadas; 46 cierres y 4 detalles interiores excluidos; 19 alturas siguen `UNKNOWN`.
- Geometría especial estructural: H-1/H-2/H-3 confirmadas, muro dilatado S1
  incorporado y 0 elementos `UNRESOLVED_REQUIRES_REVIEW`.
- Interfaz D/E auditada: residual 9 mm, sin conexión ED1–ED2 demostrada y sin
  links FE creados por proximidad.
- `CALCE_A = AXIS_CONFIRMED` (9 mm) y sistemas de coordenadas/ejes canonicos.
- Modelo combinado + enriquecimiento + validaciones PASS.
- Viewer funcional con seleccion/busqueda/filtros.
- ED2: extraccion, niveles revisados, modelo exportado.
- Documentacion: STATUS.md al dia y este handoff.

OPEN / PENDIENTE:
- Losas S1–P4 de ED1/ED2 y arquitectura visual: perímetros, huecos, voladizos,
  aleros y canopias; estos últimos deben permanecer fuera de FE.
- Revision visual final despues de futuras correcciones (volver a correr paso 14 del pipeline).
- Propiedades faltantes: vigas, muros ED2 y apoyos sin sección/espesor completamente confirmados; materiales/armadura siguen `DEPENDENCIA_PENDIENTE`.
- OpenSees conectado al modelo vigente (ver seccion 12).

## 17. P1L3 - YA TIENE PLANIFICACION (NO duplicar)

- Plan vigente: `entregas/P1L3/PLANIFICACION.md` (revisado y verificado contra el repo al 2026-09-08; sigue vigente).
- Resumen (detalle alla, commit `0552534`):
  - REUSA: nucleo tributario/QA de `origin/luis-gravedad-tributarias` (port con adaptador al combinado), superposicion G/Q validada (`semana3`), patrones FE de benchmarks, runtime Unity de Jose (`origin/jose-viewer`, sin datos embebidos), filosofia de resultados de `enrich_response` de Luis.
  - FALTA: topologia analitica + crosswalk (id <-> nodeTag/elementTag OpenSees), panos reales conectados a tributarias, Q (`sum Q = q_Q*A`), masas y centros de masa, EX/EY, generalizacion de superposicion a 4 casos + fuerza interna, Fiber/M-phi/P-M (sin inventar armadura; buscar en planos/detalles).
  - Riesgos: `elementTag` geometrico != tag OpenSees; ramas de terceros usan geometria anterior (no fusionar; portar); `J=Iy+Iz` en scripts viejos debe reemplazarse; parametros docentes = `DEPENDENCIA_PENDIENTE`.
- NO implementar P1L3 en esta etapa.

## 18. PROPUESTA DE DIVISION P1L3 (A/B/C, NO asignada)

Base: separar demanda (G/Q/EX/EY/superposicion) de capacidad (Fiber), con un contrato comun de resultados por elemento (`analysis_id` + campos estables). Carga equilibrada y trabajo en paralelo.

- INTEGRANTE A - Envolvente de analisis y casos de carga:
  - Responsabilidades: topologia analitica y crosswalk desde `model_combined_viewer.json`; motor G/Q con tributarias reales (`sum Q = q_Q*A`); caso EX/EY y masas; superposicion R = lG*G+lQ*Q+lEX*EX+lEY*EY con l editables y comparacion vc corrida explcita.
  - Inputs: combinado enriquecido, `load_definitions_draft.json`, nucleo tributario de `luis-gravedad-tributarias`, superposicion de semana3.
  - Outputs: `analysis_model.json`, `results/<run>/cases/G,Q,EX,EY.json`, `combinations/R-*.json`.
  - Archivos esperados: `entregas/P1L3/model/`, `entregas/P1L3/opensees/`, `entregas/P1L3/results/`.
  - Dependencias: ids estables de A (o del pipeline P1L2), ejes canonicos.
  - Integracion: manifiesto de resultados por run que consuman B y C.

- INTEGRANTE B - Viewer de resultados y QA de conservation:
  - Responsabilidades: adaptar runtime viewer (seleccion geometrica, capas por caso, desplazamientos, fuerzas locales, tags OpenSees); QA de conservation (equilibrio, unidades, W vs cargas, superposicion); dashboards de resultados.
  - Inputs: manifiestos de A, `model_combined_viewer.json`.
  - Outputs: viewer P1L3 (web/Unity) + reportes QA por run.
  - Archivos esperados: `entregas/P1L3/viewer/`, `entregas/P1L3/qa/`.
  - Dependencias: contrato `analysis_id`/`nodeTag`/resultados de A.
  - Integracion: mismo manifiesto que A.

- INTEGRANTE C - Capacidad HA y comparacion demanda-capacidad:
  - Responsabilidades: encontrar detalle de armadura CONFIRMADO en planos/detalles (f'c, fy, recubrimiento, barras, estribos) sin inventar; Fiber Section (P), M-phi y primeros puntos P-M para una columna confirmada; carpeta demanda+seccion, comparacion.
  - Inputs: columnas confirmadas (`luis_inferred_column_resolution.json`), planos DXF, catalogo de materiales de la catedra (DEPENDENCIA_PENDIENTE).
  - Outputs: `entregas/P1L3/capacidad/` (fiber, M-phi, P-M) + notas de trazabilidad de armadura.
  - Archivos esperados: `entregas/P1L3/capacidad/*.py`, `*.json`.
  - Dependencias: seccion de una columna confirmada + materiales disponibles; NO depende de A/B (puede arrancar cuando haya detalle de armadura).
  - Integracion: referencia de demanda por columna (desde A/B) en un bloque separado.

Punto de integracion unico: `entregas/P1L3/results/<run_id>/manifest.json` (unidades SI, revision/hash de geometria, convergencia, equilibrio, desplazamientos nodales, reacciones, fuerzas locales por `analysis_id`). Progreso incremental por hitos la entrega.

## 19. ADVERTENCIAS OPERATIVAS PARA EL PROXIMO AGENTE

- Este documento + STATUS.md + PLANIFICACION.md son la fuente. Si contradicen codigo viejo, vale el codigo actual y la evidencia de planos.
- Nunca re-planificar P1L3 desde cero, ni re-resolver las 6 columnas S1, ni renumerar IDs.
- No modificar geometria sin regenerar dependientes (combined y corrected) y correr validaciones (apartado 15).
- No integrar ramas completas de terceros; portar solo lo clasificado como util (ver PLANIFICACION.md seccion 5).
- Shell de trabajo: Windows PowerShell. `rg` NO esta disponible; usar `git grep` o `python -c`.
- `ACoreConsole` CSV: los DXF requieren el equipo local (recursos ignorados); ver seccion 14.
- Git: nunca force push/reset --hard/clean; fetch antes de integrar; commits descriptivos por hito (P1L2 y P1L3 por separado); persistir `STATUS.md` en cada hito.
- AGENTS.md de la raiz es vinculante (reglas de sync, P1L0 scope, unidades, verificación).

## 20. REFERENCIAS INMEDIATAS

- `entregas/P1L2/STATUS.md` - estado P1L2 al dia.
- `entregas/P1L3/PLANIFICACION.md` - plan P1L3 (inventario, dependencias, arquitectura, division).
- `AGENTS.md` - reglas del proyecto (unit, sync, verification).
- `entregas/P1L2/viewer/README.md` - viewer completo.
- `entregas/P1L2/edificio/datos/global_axes.json`, `axis_calce_validation.json` - ejes/calce.
- `entregas/P1L2/edificio/datos/luis_inferred_column_resolution.json` - clasificacion columnas.
- `entregas/P1L2/edificio/datos/cad_property_audit.json` - propiedades.
- `entregas/P1L2/edificio/datos/building_master.json`, `building_2_master.json` - modelos logicos.
- `entregas/P1L2/data/load_definitions_draft.json` - cargas G/SC draft.
- Scripts del pipeline: `entregas/P1L2/edificio/scripts/` y `entregas/P1L2/opensees/extract_cad_model_ed2.py`.
