# P1L2 Status

## Reorganización funcional — comandos y copia limpia (2026-10-05)

- `tools/validate_project.py`: entrada QA segura, sin AR ni solver.
- Planes build_model/run_analysis/generate_unity_data/rebuild_all; escritura exige `--execute`.
- Copia Git limpia: modelo/pipeline/117 bytes protegidos/17 tests PASS; notas explícitas intactas.
- Q y superposición OpenSees en memoria, capacidad aislada de 669 miembros PASS; resultados activos intactos.
- Corregida preservación LF/CRLF para clones sin alterar valores ni contratos declarados.
- Archivo masivo rechazado por seguridad; 998 candidatos inventariados, requieren revisión individual.
- Evidencia: `reports/repository_architecture_audit/CLEAN_DESKTOP_CHECKPOINT.md`.

## Reorganización funcional — traslado desktop (2026-10-05)

- Unity productivo trasladado a `viewer/unity/`, con GUID/.meta conservados.
- Compile/Play desde Unity Hub PASS: selección, casos, deformada, diagramas y R.
- QA modelo PASS; pipeline PASS_WITH_EXPLICIT_NOTES; 117/117 protegidos desktop idénticos.
- AR limitado a organización; no se ejecutaron pruebas ni regeneración AR.
- Sin reanálisis ni modificación de resultados. Copia limpia/archivo final pendientes.
- Evidencia: `reports/repository_architecture_audit/DESKTOP_RELOCATION.md`.

## Reorganización funcional — Editor CURRENT (2026-10-05)

- Editor abierto; scripts recompilados tras actualizar Assets.
- Corregidas rutas del gate de configuración y detección de raíz a `config/`.
- Play/Edit y demo CURRENT PASS: selección, casos, deformada, diagramas y R.
- Modelo/cargas/resultados/capacidad/AR intactos: 120/120 archivos protegidos iguales.
- Traslado Unity y pruebas AR Play/dispositivo aún pendientes.
- Evidencia: `reports/repository_architecture_audit/EDITOR_RUNTIME_CHECKPOINT.md`.

## Reorganización funcional — integración AR (2026-10-05)

- Scripts/escena/suites AR finales integrados selectivamente desde `862da8c`.
- Colocación, escalas, selección y diagramas; Main/terreno/tema y dataset intactos.
- Generador y transformaciones en `ar/`, una sola salida AR generada en StreamingAssets.
- QA Python PASS; runtime/suites compilan con referencias cacheadas y métricas offline PASS.
- Equivalencia: dataset temporal igual salvo timestamp; 120/120 archivos protegidos iguales.
- Editor compile/Play bloqueado por licencia; usuario verificando apertura en Hub.
- No se trasladó Unity ni se limpió historia antes de pasar esa barrera.
- Detalle: `reports/repository_architecture_audit/AR_INTEGRATION_QA.md`.

## Reorganización funcional — resultados (2026-10-05)

- Resultados CURRENT en `results/{G,Q,EX,EY}`, capacidad/cargas/Fiber separados.
- Traslado sin recalcular: 120/120 archivos protegidos idénticos, referencia Luis intacta.
- Modelo/pipeline PASS, prueba de capacidad aislada PASS, fuente única 4 tests PASS.
- Procedencia histórica dentro de JSON conservada; no es una ruta fallback.
- Pendientes: auxiliares y funciones AR finales, Unity, wrappers, histórico y QA limpio.

## Reorganización funcional — implementaciones (2026-10-05)

- OpenSees/capacidad/postproceso/Fiber trasladados a `analysis/`; tests a `tests/`.
- Algoritmos conservados; rutas/imports ajustados, pipeline y superposición PASS.
- Fiber ejecutado en carpeta temporal: cuatro CSV exactamente iguales a históricos.
- Baseline 120/120 protegido; no se sustituyen resultados o datasets.
- Resultados, auxiliares, Unity/AR e histórico siguen pendientes de las siguientes fases.

## Reorganización funcional — fuentes canónicas (2026-10-05)

- Fuentes únicas trasladadas a `model/` mediante `git mv`; configuración en `config/`.
- Las losas permanecen en `model_master.json`: no se crea una fuente duplicada.
- Consumidores CURRENT dirigidos a las nuevas fuentes. Referencias Git antiguas
  solo para verificar propiedades contra el commit de procedencia del resultado.
- QA: modelo PASS, pipeline PASS_WITH_EXPLICIT_NOTES, 10 tests de entrada PASS,
  prueba OpenSees Q/superposición en memoria PASS y FE preview READY_TO_RUN.
- Equivalencia: 120/120 archivos protegidos idénticos byte a byte; Luis intacto.
- No se regeneraron ni sustituyeron resultados guardados, capacidades o datasets.
- Pendientes: módulos de análisis/resultados, integración AR funcional, traslado
  Unity, wrappers finales, histórico y QA desde copia limpia. No es cierre final.

## Reorganización funcional — checkpoint de auditoría (2026-10-05)

- Rama `codex/final-repository-architecture`; `main` e historia entregada intactas.
- Inventario read-only: 1.362 archivos, 281 archivos de código, 321 JSON.
- 27 grupos JSON equivalentes pendientes de clasificación, no eliminación automática.
- Base desktop/terreno `53a0484`; funcionalidades AR finales identificadas en `p1l7/ar-final-search`.
- Dataset AR idéntico en contenido y sus 102.811 hojas numéricas; no sustituir los datos CURRENT.
- Baseline de 120 archivos protegido en `reports/repository_architecture_audit/baseline.json`.
- Todavía no hay migración de fuentes, cambios físicos ni regeneración de resultados.
- Referencia original de Luis intacta. Este checkpoint no certifica la arquitectura final.

## Semana 7 — Q uniforme y sincronización (2026-10-01)

- Rama de cierre `codex/week7-model-closure`, base `3cc21d6`; no modificar historia.
- Geometría/FE/tributarias físicas intactas; Q configurable sustituye toda SC histórica.
- qQ inicial 0,667 kN/m² (hipótesis), λQ separado; flujo Unity → STALE → OpenSees → recarga probado.
- Agregado G por piso corregido: 2,265720 MN permanentes antes omitidos del peso sísmico.
- AR sincronizado: 712 sólidos, 54 muros faltantes añadidos, 0 IDs retirados.
- Fiber separado de capacidad aproximada; puntos no convergidos explícitos.
- qQ restaurado exactamente a 0,667; Unity compiló/Play PASS (83 UX, 29 Q, 44 losas).
- Clone limpio y nuevo entorno regeneraron CURRENT con la misma respuesta; cierre con bloques explícitos, no release final.
- Cierre y QA: [Semana 7](../P1L7/WEEK7_MODEL_CLOSURE.md). Build final todavía no aprobado.

## Exclusión lateral ED1-P1 y cargas visibles (2026-10-01)

- Excluidos H08 (100,850 m²) y H10/H12 (70,422 m²), incluida su SC/PM y tributarias.
- CURRENT recalculado: G 78.716,059 kN; Q 22.637,353 kN; cuatro casos en equilibrio.
- Losas OFF por defecto; CAD fuera del flujo visual; ficha CARGAS explica Q base y λ.
- FE estructural/Luis original sin cambios. [Reporte](../P1L6/slab_reconstruction/P1_LATERAL_FINAL.md).

## Losas CURRENT — saneamiento aprobado (2026-10-01)

- Rama `codex/current-slab-reconstruction`: exclusión sur ED1-S1 227,099 m²,
  franja lineal duplicada corregida y cargas/análisis/capacidades regenerados.
- Diez losas poligonales accesibles en Modelo, OFF al iniciar; sin piloto P4 duplicado.
- FE y referencia original Luis intactos. Contornos físicos todavía REVIEW_REQUIRED;
  no confundir QA numérico con certificación de perímetros/huecos.
- Fuente/tabla/pendientes: [losas CURRENT](../P1L6/slab_reconstruction/README.md).

## Viewer CURRENT — checkpoint visual/UX (2026-10-01)

- Rama `codex/unity-visual-ux`: materiales visuales, paneles compactos,
  ayuda contextual y ficha ordenada. No modifica el modelo ni resultados.
- Validación compile/Play y regresión visual: [QA](../P1L6/visual_ux/FINAL_QA.md).
- Losas parciales y overlays de cargas sin datos CURRENT siguen explícitos;
  no se sustituyen por datasets históricos.
- Export original de Luis, geometría central y `P1L4_FINAL` intactos.

## main CURRENT — organización y núcleos (2026-10-01)

- Fuente única: `entregas/P1L5/modelo_central/`; 712 sólidos: 442 vigas,
  143 columnas, 84 muros, 10 losas y 33 apoyos visuales.
- FE: 1170 nodos topológicos, 677 segmentos, 1240 restricciones y 44 tags
  fijos; 0 componentes sin camino a apoyo. G/Q/EX/EY/R CURRENT verificados.
- Entrada de uso: `Proyecto.bat` / `main.py`. `Validar_Modelo.bat` ahora
  verifica CURRENT, no el histórico. No se recalcula física al ordenar main.
- La referencia original de Luis y los tags históricos permanecen intactos.
- Guía vigente: [índice canónico](../../PROJECT_INDEX.md) y
  [QA de núcleos](../P1L6/wall_continuity/CURRENT_PIPELINE_QA.md).
- Los apartados siguientes son checkpoints históricos, no el estado actual.

## P1L6 readiness CURRENT (2026-09-29)

- Fuente vigente: `entregas/P1L5/modelo_central/model_master.json`.
- 658 sólidos: 442 vigas, 143 columnas, 30 muros, 10 losas poligonales de
  0,15 m y 33 apoyos visuales coincidentes con los 33 apoyos FE.
- FE: 1.100 nodos, 623 segmentos, 1.225 restricciones, 0 componentes
  desconectados. OpenSees CURRENT G/Q/EX/EY/R verificado.
- Los checkpoints históricos siguientes se conservan para reproducibilidad;
  sus conteos ya no describen CURRENT.
- Estado completo: [P1L6_READINESS](../P1L6/P1L6_READINESS.md).

## PRE-P1L5 — continuidad manual de vigas (2026-09-23)

- CURRENT: 695 sólidos; 466 vigas. Se consolidaron 29 grupos físicos (33 IDs absorbidos),
  se agregaron cinco vigas equivalentes ED2 S1–P4, se reconectaron cuatro extremos y
  se retiró `E1-S1-V-005` con trazabilidad archivada.
- La anotación repetida `E1-P1-V-086 + V-086` se resolvió geométricamente como
  `E1-P1-V-086 + E1-P1-V-087 → E1-P1-V-087`.
- `E1-P1-V-066/067` llegan ahora a nudos existentes; no se agregaron nodos ni apoyos ficticios.
- FE candidato: 647 miembros, 1126 nodos, 1203 restricciones y 33 apoyos; un pendiente/
  un componente (`E2-P4-V-009`). No ejecutado.
- Unity compile/Play/UX PASS. Cargas, OpenSees y resultados históricos intactos.
- Informe vigente: [corrección manual de vigas](../PRE_P1L5/manual_beam_revision/REVIEW_STATUS.md).
- Las secciones siguientes son checkpoints anteriores, no métricas CURRENT.

## PRE-P1L5 — segundo saneamiento (2026-09-23)

- CURRENT: 724 sólidos; 143 columnas, 495 vigas, 30 muros ED2, 10 losas visuales y 46 apoyos geométricos.
- Los 44 muros ED1 activos se excluyeron por decisión de alcance, junto a siete apoyos exclusivos.
  Se preservan 19 apoyos de columnas y ocho compartidos ED1; no se afirma que el edificio real no tenga muros.
- 16 nuevas fusiones físicas y 74 ajustes XY de columnas con contornos/ejes primarios; sin cambios de sección/material.
- Candidato: 676 miembros, seis pendientes / cuatro componentes; no ejecutado.
- El registro de stacks se refiere a P2; la discrepancia con ejes nominales/registro global sigue explícita antes de aprobar cargas.
- Informe vigente: [segundo saneamiento](../PRE_P1L5/second_structural_cleanup/REVIEW_STATUS.md).
- Las secciones siguientes son checkpoints anteriores, no métricas CURRENT.

## PRE-P1L5 — revisión manual aplicada (2026-09-23)

- 116 exclusiones aprobadas individualmente en `EXCLUSION_APPROVAL.md`, archivadas en
  `entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json`; referencia Luis intacta.
- Dos fusiones físicas ED2 P4: 042+046 → 042; 048+049 → 049. IDs restantes estables.
- Modelo actual: 791 sólidos; FE candidato 736 miembros, 22 pendientes / 16 componentes.
- De los 43 anteriores: 15 excluidos, 6 recuperados por continuidad numérica de muros;
  ninguno nuevo. No se añadieron apoyos ni se ejecutó OpenSees.
- Columnas no alineadas: offsets predominantes ~18 cm exigen revisar origen por planta.
- Las 19 alturas pendientes pertenecían a elementos excluidos; no fueron inventadas.
- Informe vigente: `entregas/PRE_P1L5/user_structural_review/REVIEW_STATUS.md`.
- Las secciones siguientes son checkpoints históricos, no métricas CURRENT.

## PRE-P1L5 — expediente de revisión manual (2026-09-22)

- Correcciones automáticas de los pendientes FE pausadas por solicitud de Matías.
- Regeneración temporal desde fuente canónica: mismos 43 elementos / 22 componentes;
  nodos, miembros, restricciones, apoyos, crosswalk y encuentros idénticos al candidato.
- Expediente individual: `entregas/PRE_P1L5/FE_PENDING_43_DETAILED_REVIEW.md`
  y versiones JSON/CSV. Prioridad A: 20; B: 23; C: 0. No se resolvió ningún elemento.
- Reporte de ejes usa offsets explícitos; elevaciones aplican Z fuente = Z modelo − 7.97 m.
  Estas aclaraciones no modifican propiedades ni geometría canónica.
- Unity: Diagnóstico → Pendientes FE selecciona/aisla con vecinos y ejes estructurales.
- Sin corrida OpenSees; cargas/resultados/tag histórico y referencia Luis intactos.

## POST-P1L4 — EXT-5 + Unity actual (2026-09-21)

- Geometría sin cambios respecto a EXT-4: 909 sólidos. No se regeneró ni ejecutó FE.
- Diagnóstico Unity actualizado: 116 elementos de foco, incluyendo E2-P4-V-009.
- 43 flotantes/22 componentes; 19 alturas de viga pendientes.
- Auditoría de restricciones: 424 nodos multi-maestro y 376 retenidos/restringidos;
  no aprobar el candidato de 856 miembros para análisis todavía.
- Unity normal usa POST_P1L4_CURRENT; resultados históricos apagados y aislados.
- `LUIS_REFERENCE_FILES_MODIFIED = 0`; tags y resultados históricos preservados.
- Evidencia: `entregas/POST_P1L4/EXT_5_REMAINING_AUDIT.md` y `UNITY_CURRENT_UX_QA.md`.

## Consolidacion PRE-P1L4 — FASE 7 CANDIDATO FE (2026-09-12)

- Creado `analysis_model_post_p1l3_candidate.json` sin reemplazar A3-A4 ni
  ejecutar OpenSees.
- Estrategia: miembro equivalente único por muro, nodos de incidencia y brazos
  rígidos internos; vigas segmentadas solo en intersecciones de huellas/ejes.
- La topología pasa de 72 geometrías flotantes/50 componentes a 45/23.
- Crosswalk 1:N PASS: 33 geometrías se dividen, con máximo 3 segmentos FE.
- Clasificación foco: 26 `FE_ADAPTER_ERROR` resueltos, 5 columnas
  `TRANSFERRED`, 1 `REAL_CANTILEVER`, 40 `UNRESOLVED` (31 son muros marcados
  `DISCONNECTED_ERROR` y 9 requieren interpretación adicional).
- Candidato detenido para revisión: no se inventan los 40 enlaces restantes.

## Consolidacion PRE-P1L4 — CONECTIVIDAD POST-GEOMETRIA (2026-09-12)

- Se reevaluo en memoria la topologia con las mismas reglas P1L3, sin escribir
  `analysis_model.json`, ejecutar OpenSees ni modificar cargas/resultados.
- Los flotantes bajan de 93 elementos/61 componentes a 72/50.
- De los 93 IDs historicos: 1 queda conectado, 55 siguen flotantes y 37 fueron
  eliminados o sustituidos al consolidar caras/fragmentos; aparecen 17 IDs
  nuevos o renombrados flotantes.
- Los 72 actuales se separan en 45 muros ED1 afectados por idealizacion de nodo
  central, 15 vigas ED1 que requieren distinguir incidencia de voladizo, 7
  columnas con camino vertical/transferencia por revisar y 5 elementos ED2 P4.
- No se agregaron conexiones. El siguiente paso FE es validar incidencias y
  solapes con conservacion de rigidez antes de reconstruir el modelo analitico.

## Consolidacion PRE-P1L4 — FASE 5 EN CURSO (2026-09-11)

- Diagnostico directo de `RLE-LOSA/RLE-LOSAS` generado para los 10 pares
  edificio/piso en `edificio/validacion/slabs/`.
- Los bordes crudos tienen numerosos extremos abiertos; no se rellenan ni se
  convierten automaticamente en superficies.
- `2024_22-101` confirma por titulo una planta comun S1-P3 de EDIFICIO_2. Se
  usan 22 segmentos dentro de la region; tres trazos del JSON derivado quedaron
  excluidos por pertenecer a un detalle fuera de planta.
- Los bounding boxes provisionales de losas no son areas reales y deben ser
  reemplazados por perimetros auditados.
- Propuesta exterior ED2 sin aplicar: `565.392 m2` en S1-P3 y `566.465 m2` en
  P4; todos sus lados son directos RLE-LOSA o cierres respaldados por
  RLE-VIGA/RLE-MURO. Los rasgos interiores siguen en revision.
- El bloque `losa-ne` se repite una vez por numerosos panos (22 en la planta
  comun y 23 en P4); no se interpreta como "no existe losa" ni confirma huecos.
- Propuesta parcial ED1 sin aplicar: P2 `806.605 m2` y P3 `914.175 m2`, con
  todos los lados directos o respaldados por estructura. S1 no dibuja el borde
  exterior RLE-LOSA y P1 mezcla el bloque principal con la transicion outboard;
  ambos permanecen `UNRESOLVED` hasta revisar fuentes complementarias.
- Siguiente paso: cierres respaldados por vigas/notas y clasificacion individual
  de huecos; sin modificar aun FE, cargas ni resultados P1L3.

## Consolidacion PRE-P1L4 — FASE 4 COMPLETA (2026-09-10)

- `GEO-SPECIAL-001`: la elevacion `2017_67-308` confirma las columnas S1 H-1,
  H-2 y H-3 y sus apoyos; el contorno cerrado `RLA-MURO DILATADO` confirma y
  añade un muro local S1 de 0.20 x 2.360 m.
- `GEO-INTERFACE-001`: D/E mantiene residual 0.009 m. No se encontro evidencia
  de transferencia estructural entre edificios; no se crean conexiones FE por
  proximidad.
- Los cinco remates que sobrepasan geometricamente D/E pertenecen a un solo
  edificio y no forman enlaces ED1-ED2.
- EDIFICIO_1: 524 solidos; combinado: 1212; elementos
  `UNRESOLVED_REQUIRES_REVIEW`: 0.
- Piloto P4 revalidado tras consolidacion de vigas: 958.392750 m2,
  `participates_in_FE=false`, dependencias migradas a `sourceTag` estable.
- Validaciones de calce, combinado, nucleo, referencia Luis, muros, vigas y
  visual: PASS. `LUIS_REFERENCE_FILES_MODIFIED = 0`.
- Evidencia: `edificio/validacion/special_interface/`.
- Siguiente hito: losas y arquitectura visual ED1/ED2, sin tocar aun FE ni
  resultados P1L3.

## Consolidacion PRE-P1L4 — FASE 3 COMPLETA (2026-09-10)

- Auditoría directa de `RLE-VIGA`: 553 segmentos fuente; propuesta validada de
  300 centrolineas (S1 53, P1 69, P2 64, P3 60, P4 54).
- Los 545 prismas históricos se consolidaron; 46 cierres cortos y 4 detalles
  interiores fueron excluidos. No quedan caras largas/diagonales sin resolver.
- Ancho 300/300 trazable; altura 281 con evidencia directa o de familia inequívoca y 19
  `UNKNOWN`. En esas 19, 0.60 m es solo profundidad visual, no sección asumida.
- Propuesta, aplicación, geometría combinada, continuidad, muros, diff de Luis
  y auditoría visual: `PASS`. La referencia original permanece intacta.

## Consolidacion PRE-P1L4 — FASE 2 (2026-09-10)

- Corregido el defecto del extractor histórico que interpretaba cada cara de
  un contorno `RLE-MURO` como un muro resistente independiente.
- Auditoría directa de DXF: 193 segmentos fuente, 67 segmentos analíticos
  confirmados (S1 21, P1 25, P2/P3/P4 7), 72 cierres cortos excluidos y 0
  entidades sin clasificación.
- ED1: 134→67 muros y 60→21 apoyos lineales S1. Modelo corregido: 767 sólidos;
  combinado: 1455 sólidos.
- Espesor: 67/67 confirmado desde geometría; 58 también coinciden con etiqueta,
  9 solo por contorno y 0 conflictos.
- `ED1_WALL_VALIDATION`, calce, core, geometría combinada, enriquecimiento y
  diff contra la referencia: `PASS`. `LUIS_REFERENCE_FILES_MODIFIED = 0`.
- Evidencia y overlays: `edificio/validacion/ed1_walls/`.

## Consolidacion PRE-P1L4 — FASE 1 (2026-09-10)

- Cerradas las seis columnas S1 de ejes I/I' × 1/2/3 que figuraban como
  `UNRESOLVED_REQUIRES_REVIEW`.
- Evidencia primaria: elevaciones `2017_67-309` (I) y `2017_67-310` (I'), con
  luces 8.90/7.25 m, rótulos `P. 70x70` y continuidad hasta vigas de fundación.
- Veredicto: seis `CONFIRMED_BY_AXIS_ELEVATION`; centros y secciones
  normalizados. Informe reproducible en
  `edificio/validacion/s1_columns_final/REPORT.md`.
- Regenerados EDIFICIO_1 corregido y modelo combinado. Validaciones de calce,
  ejes, continuidad, geometría, enriquecimiento y referencia Luis: `PASS`.
- La referencia original `unity_export/model_viewer.json` permanece intacta.

## Interfaz P1L3 vigente (2026-09-10)

- El modelo combinado P1L2 vigente tiene 1212 solidos; el Unity entregado P1L3
  conserva su snapshot hasta la fase prevista de actualización de interfaz.
  por el Unity de Jose; no se reemplazo por snapshots historicos.
- P1L3 integra `G/Q/EX/EY/R`, capacidad HA y resultados OpenSees en Unity.
- La renovacion UI se documenta en `../P1L3/UI_QA.md`; no modifica esta
  geometria ni la referencia original de Luis.
- El piloto arquitectonico EDIFICIO_1/P4 vive en un JSON separado y no modifica
  `model_combined_viewer.json`, la topologia FE, cargas, masas ni resultados.
  La caja de losa provisional se conserva y queda apagada por defecto en Unity.

## Auditoria completa de fuentes (2026-09-09)

- Inventariados y convertidos con AutoCAD 60/60 DWG de las series
  `2017_67` (38) y `2024_22` (22), sin modificar los archivos originales.
- Indice CAD: `edificio/datos/planos_full_index.json`.
- Informe y prioridades: `edificio/validacion/AUDITORIA_PLANOS_COMPLETA.md`.
- Hallazgos principales: cajetines de nivel desfasados en 2017_67-101..103,
  numero duplicado en el cajetin 2024_22-305, cobertura tributaria incompleta,
  EX/EY historicos desacoplados y propiedades de material mayoritariamente
  `UNKNOWN` en el JSON combinado.

## P1L3 (Parte A completada, commits `558874b`, `f006d3f`, `487ff69` en `main`)

- A1-A2: panos analiticos (110, 3392.62 m2, 647 vigas cargadas) + casos G/Q + conservacion PASS (`rel_error=0.0`).
- A3-A4: `results/a3a4/analysis_model.json` FE (813 nodos, 1312 elementos: 148 columnas, 163 muros, 1001 vigas; 106 soportes) + crosswalk `element_id`/`geometry_elementTag`/`analysis_id`/`opensees_*`. Componentes flotantes (93 elementos) excluidos e idealizados (`floating_excluded`).
- A5: OpenSees elasticBeamColumn clasico (A,E,G,J,Iy,Iz,transf); superposicion `G/Q` PASS (rel_errors: disp 2.2e-12, reacc 4.5e-13, internas 1.4e-12). Equilibrio residual ~0.8% = carga de flotantes excluidos (documentado).
- A6: contrato EX/EY (interfaz sola; demo FICTICIO en `entregas/P1L3/results_local/`, no versionado) + A7: viewer con capa de resultados via `?analysis=...&run=...`.
- Detalles: `entregas/P1L3/DEFENSA.md`, `entregas/P1L3/PLANIFICACION.md`.

## Transferencia
- Documento maestro: `PROJECT_HANDOFF.md` (raiz del repositorio) + plan P1L3 en `entregas/P1L3/PLANIFICACION.md`. Leerlos antes de modificar geometria o iniciar P1L3.

## Current Model
- Floors: S1 / P1 / P2 / P3 / P4
- EDIFICIO_1: audited corrected model in progress
- EDIFICIO_2: current geometry validated
- Combined viewer: updated from EDIFICIO_1_AUDITED_CORRECTED + EDIFICIO_2
- Source policy: PLANOS = primary truth, Luis = provisional reference

## Luis Audit
- Inferred columns reviewed: 61
- Confirmed correct: 19 (incluye seis ejes I/I' confirmados por elevaciones 309/310)
- Wrong and corrected: 39
- Still unresolved/requires review: 3
- Derived supports invalid and removed: 15
- Luis original modified: 0

## Last Important Change
- FASE 2 cerró la auditoría ED1 de muros: 134 prismas históricos, originados
  al extruir cada cara `RLE-MURO`, se reemplazaron por 67 centrolineas con
  espesor medido entre caras. Los apoyos lineales S1 pasaron de 60 a 21.
- FASE 1 confirmó `E1-S1-C-014..019` mediante las elevaciones 309/I y 310/I':
  sección 70x70 y continuidad a fundación en ejes 1/2/3.
- Modelo vigente: ED1 522 sólidos; combinado 1210. Todas las validaciones
  dependientes pasan y la referencia original de Luis permanece intacta.

## Viewer
- Main viewer model: `entregas/P1L2/unity_export/model_combined_viewer.json`
- Corrected EDIFICIO_1: `entregas/P1L2/unity_export/model_1_audited_corrected.json`
- Audit checkpoint: `entregas/P1L2/unity_export/model_1_audited.json`

## Validations
- AXIS/CALCE_A: PASS / AXIS_CONFIRMED
- COLUMN_AXIS_MATRIX: PASS_WITH_OFF_AXIS_NOTES
- CAD_PROPERTY_AUDIT: PASS_WITH_REVIEW_NOTES
- ENRICHED_MODEL: PASS
- CORE_AXIS_CONTINUITY: PASS
- COMBINED_GEOMETRY_VALIDATION: PASS
- VISUAL_AUDIT_COMBINED: PASS
- LUIS_REFERENCE_DIFF_VALIDATION: PASS
- GOLDEN_IN_COMBINED_LEGACY: SUPERSEDED_BY_LUIS_REFERENCE_DIFF

## Next Work
- Auditar sectores especiales/outboard, voladizos, canopias y la interfaz
  física entre EDIFICIO_1 y EDIFICIO_2 usando planos como fuente primaria.
- Resolver las 19 alturas de viga ED1 `UNKNOWN` solo si aparece evidencia de
  detalle/elevación; no confundir la profundidad visual con una sección.
- Sector specials: `outboard_room_reconstruction.json` still exposes `UNRESOLVED_REQUIRES_REVIEW` groups for the east outboard/transitional zones; review overlaps with the P1 outboard non-modelable/detail imports (C-021, C-022, C-019).
- The remaining 3 slab-edge/transitional S1 columns keep their documented
  review status; the six I/I' stations are already confirmed and must not be
  reopened without contradictory primary evidence.
# POST-P1L4 EXT-2 — muros

- Auditoría primaria EDIFICIO_2 (`2024_22-101/102`): `PASS`.
- Corrección canónica: 100 prismas históricos de caras/cierres → 54 muros físicos (S1/P1/P2/P3/P4 = 11/11/11/11/10).
- Espesores confirmados: 0.25/0.30/0.60 m; conflictos etiqueta-geometría: 0.
- EDIFICIO_1 permanece en 68 muros auditados; `E1-P4-M-007` conserva continuidad S1–P4.
- Modelo combinado y bundle Unity regenerados. Resultados OpenSees P1L4 permanecen históricos y no fueron recalculados.
- QA de datos/pipeline: `PASS`. Unity Play pendiente por licencia local no disponible (`com.unity.editor.ui/headless`).

# POST-P1L4 EXT-3 — vigas

- EDIFICIO_1 revalidado: 300 vigas físicas desde 553 segmentos CAD; 46 cierres cortos y 4 detalles interiores excluidos.
- EDIFICIO_2 corregido: 515 prismas históricos → 267 vigas físicas (`44/44/44/44/91`), todas con sección trazable al plano.
- Total canónico: 567 vigas; `E1-P2-V-075` confirmado como viga de descanso y `E2-P4-V-050/051` consolidado como una V60/80.
- Comparación externa: 457 coincidencias 3/3, 3 coincidencias 2/3; diferencias externas sin fuente primaria no se incorporaron.
- Conectividad: 247 apoyadas geométricamente en ambos extremos, 259 con un extremo/borde/voladizo y 60 para revisión FE posterior. No se crearon conexiones artificiales.
- Resultados OpenSees P1L4 siguen históricos; no fueron recalculados.
- Unity 6000.6.0f1 compila y la prueba automática en Play registra `PASS` para carga del modelo (909 sólidos), capas/pisos, diagnóstico y secuencia P1L4.

# POST-P1L4 EXT-4 — losas, propiedades y conectividad

- Los 10 pisos fueron auditados contra `RLE-LOSA`, estructura y ambos modelos externos. No se aplicaron superficies: ED1 S1/P1 y los rasgos interiores siguen sin evidencia suficiente.
- ED1 P2/P3 y ED2 S1–P4 quedan como propuestas reproducibles; ED1 P4 sigue siendo piloto visual congelado, no FE.
- Propiedades: 545/567 vigas con sección confirmada, 19 alturas ED1 pendientes; materiales de vigas/columnas permanecen UNKNOWN hasta evidencia primaria.
- El adaptador histórico deja 115 geometrías flotantes/59 componentes. El candidato de incidencia física, aún no ejecutado, reduce a 43/22 y conserva 42 unresolved sin forzar conexión.
- OpenSees, cargas, masas y resultados P1L4 no fueron recalculados.
- QA final: geometría/ejes/continuidad/referencia Luis/contrato Unity `PASS`;
  Unity 6000.6.0f1 compila y Play completa capas, diagnóstico y demo P1L4 sin
  errores. IDs consolidados de capacidad se vinculan por `geometry_elementTag`
  manteniendo visible el ID histórico.
# PRE-P1L5 — HIST-1 (2026-09-22)

Unity conserva el modelo actual e incorpora Entregas y Estado del proyecto,
con estadísticas de tags inmutables y resultados históricos solo por opt-in.
Compilación y prueba de ejecución en dos resoluciones: PASS. No cambia geometría,
cargas ni resultados. Ver `entregas/PRE_P1L5/UNITY_QA.md`.

## EXT-6/7, FE-2 y UX-5

361 miembros ED2 con material confirmado desde 2024_22-100/53994. Coordenadas,
secciones, cargas y resultados anteriores sin cambios. 43 pendientes FE,
19 alturas y losas ED1 S1/P1 aún abiertos. Ocho muros revisados individualmente.
Normalización cinemática 1482→946 solo propuesta; clusters extensos impiden
declararla físicamente aprobada. PRE_P1L5_BASELINE: BLOCKED.
Guía y QA vigentes: `entregas/PRE_P1L5/PRE_P1L5_STATUS.md`.

## Última etapa PRE5 — inspector y alcance ED1

391 miembros ED1 S1–P3 adicionales reciben G35/A630-420H desde nota 100/1E116.
El título de 600 confirma SALA ELECTRICA: no asignar G25 a escaleras globalmente.
752 materiales confirmados en el combinado/Unity; ED1 P4 y losas pendientes.
Geometría, secciones, candidato y resultados históricos no cambiados.
Inspector semántico con Resumen/Resultados; actuales no disponibles, archivo
histórico sólo opt-in. Contrato de versiones y preparación de superposición.
Persisten 43/22, alturas19 y restricciones físicamente no aprobadas. Ver informe
`entregas/PRE_P1L5/current_readiness/CURRENT_READINESS_REPORT.md`.

## CURRENT — auditoría de continuidad de núcleos (2026-10-01)

Rama `codex/p1l6-wall-continuity-correction`. Auditoría de 54 muros activos,
15 líneas y tres conjuntos en C contra ejes y caras CAD. El candidato aislado
de 84 muros pasa FE (0 componentes sin apoyo) y OpenSees G/Q/EX/EY.
Todavía no promovido en este checkpoint. ED1-P4 conserva el supuesto material
G35 explícito; no se declara confirmación primaria nueva. El muro largo ED2
se mantiene en su lado CAD, según aclaración del usuario.
Ver `entregas/P1L6/wall_continuity/WALL_CONTINUITY_BEFORE.md`.

### Promoción y análisis CURRENT de núcleos

30 muros reintegrados, cuatro muros S1 registrados contra ejes primarios;
84 muros activos. E2-P4-C-004/C-007: sección existente 70×70 cm de P3,
con XY, altura, material e IDs preservados. FE 677 segmentos, 1170 nodos,
44 apoyos FE, 0 componentes sin apoyo. OpenSees G/Q/EX/EY PASS; capacidad
669 registros y export CURRENT_VERIFIED con hashes coherentes.
Muros duplicados y solapes accidentales: 0. Luis original intacto.
Véase `entregas/P1L6/wall_continuity/WALL_CONTINUITY_AFTER.md`.

## Contexto visual de terreno — 2026-10-04

Dos niveles de terreno/plataforma en el viewer, sin cambio estructural:
13 columnas ED1 S1 C-007–C-019 cubiertas visualmente; acceso exterior junto
a P1 V-106/V-107 hasta base de P2. Controles independientes en Contexto.
Unity Main/Play, Right/ISO, selección y filtro S1 comprobados. CURRENT,
OpenSees y AR intactos; Luis original sin cambios. QA y alcance esquemático:
`entregas/P1L7/visual_terrain/RUNTIME_VALIDATION.md`.

### Entorno visual continuo — revisión 2

Base ampliada bajo ED1/ED2, terrazas rectangulares sin talud, pasto discreto
y camino sobre el acceso P2. Reserva perimetral para contexto futuro.
ISO/Right/Top, selección y filtro S1 comprobados en Play; 19 checks PASS,
260 archivos protegidos intactos. Sin cambios estructurales, CURRENT ni AR.
Diseño vigente: `entregas/P1L7/visual_terrain/TERRAIN_V2_VALIDATION.md`.

### Terrazas visuales hasta el perímetro — revisión 3

Los niveles intermedio y superior ahora alcanzan ambos bordes laterales del
terreno general. El superior llega también al borde exterior de su base;
camino prolongado hasta ese borde. Pasto, acceso P2 y cotas conservados.
Main/Play y perímetros PASS; 22 checks PASS, 260 archivos protegidos intactos.
Diseño vigente: `entregas/P1L7/visual_terrain/TERRAIN_V3_VALIDATION.md`.
