# Consolidación POST-P1L3 / PRE-P1L4

Estado: `FASE_1_COMPLETE_PHASE_2_NEXT`
Fecha de apertura: 2026-09-10  
Rama vigente: `codex/pre-p1l4-consolidation`

## Regla de preservación

- Snapshot entregado: tag anotado `P1L3_DELIVERED`.
- Commit preservado: `c847c131512d00cc85bb95aa5719278d70da0c2b`.
- El repositorio no contenía antes un tag P1L3 ni otro hash escrito como entrega.
  `main` terminaba en `8fa367c`; el hash `c847c13` fue el hito explícitamente
  indicado para esta consolidación y contiene además el piloto P4 y el cierre
  espacial de cargas 700. Se adoptó como snapshot reconstruible sin reescribir
  historia.
- Todo cambio nuevo vive en `codex/pre-p1l4-consolidation` y se clasifica
  `POST_P1L3 / PRE_P1L4`.
- No se implementan requisitos de P1L4 en esta etapa.

## Auditoría Git

Se ejecutaron `git status`, `git fetch --all --prune`, `git branch -a` y
`git log --all --graph --decorate --oneline`. El árbol estaba limpio antes de
crear esta documentación.

| Referencia | Clasificación | Evidencia | Decisión |
| --- | --- | --- | --- |
| `codex/pre-p1l4-consolidation` | VIGENTE | Nace exactamente en `P1L3_DELIVERED`. | Única rama para la consolidación. |
| `P1L3_DELIVERED` / `c847c13` | DELIVERED_HISTORY | Snapshot completo indicado por el usuario. | Inmutable; base de comparación. |
| `origin/main` / `8fa367c` | DELIVERED_HISTORY | P1L3 funcional y UI integrada, pero no incluye los tres hitos posteriores P4/cargas. | No avanzar directamente aquí durante la auditoría. |
| `origin/codex/arquitectura-p4` | DELIVERED_HISTORY | Contiene `807558b`, `c056c6c`, `c847c13`; ya está íntegro en el tag. | No requiere integración adicional. |
| `origin/jose-viewer` | SUPERSEDED | Viewer/EX-EY antiguos; las funciones útiles fueron reorganizadas e integradas en `entregas/P1L3/José/viewer_unity`. | No fusionar. Consultar solo como antecedente. |
| `origin/luis-semana3-capacidad-ha` | SUPERSEDED | `git cherry` marca `ac1afa9` como ya aplicado; `capacidad_ha/` existe en la base vigente. | No fusionar. |
| `origin/luis-gravedad-tributarias` | UTIL_REQUIERE_INTEGRACION | Auditoría `localForce`, taxonomía de stubs y QA de gravedad útiles; geometría, IDs y viewer son anteriores al modelo combinado vigente. | Portar solo verificaciones faltantes, nunca la rama completa. |
| `origin/e2-work` | EXPERIMENTAL / UTIL_REQUIERE_INTEGRACION | Declara explícitamente `UNRESOLVED_INTERFACE`, transformaciones visuales identidad y composición E1/E2 no terminada; contiene QA y auditoría de componentes/contexto. | No fusionar. Reusar criterios forenses al auditar conectividad. |
| `origin/luis` | LEGACY | Solo configuración P1L0/entorno desde una base muy antigua. | No integrar. |

## Inventario y clasificación del repositorio

| Clase | Alcance actual | Regla PRE-P1L4 |
| --- | --- | --- |
| SOURCE | Planos locales `recursos/planos/`, enunciado y DWG/DXF; los planos están ignorados por Git. | Solo lectura; registrar hashes/índice y conversiones. |
| CANONICAL | Ejes `global_axes.json`; ED1 `model_1_audited_corrected.json`; ED2 `model_2_viewer.json`; combinado `model_combined_viewer.json`; FE `results/a3a4/analysis_model.json`; Unity `entregas/P1L3/José/viewer_unity`. | Pueden cambiar únicamente mediante pipeline y validación. |
| GENERATED | JSON y gráficos bajo `results/`; `Assets/StreamingAssets`; modelos exportados. | No editar cifras manualmente. Regenerar desde fuentes. |
| VALIDATION | `edificio/validacion`, archivos `*_validation.*`, reportes A1-A7 y overlays. | Conservar junto a la revisión/hash de sus entradas. |
| DELIVERED_HISTORY | Tag `P1L3_DELIVERED`, entregas P1L0-P1L3 y referencia Luis `model_viewer.json`. | No modificar el snapshot ni la referencia Luis. |
| LEGACY | `entregas/semana2`, `entregas/semana3`, viewer web y modelos idealizados anteriores. | Mantener por historia; no usar como fuente canónica. |
| DEPRECATED | `ejes.json`, `golden_in_combined_validation`, candidatos/pre-reextracción y bounding boxes de losa. | Documentar sustituto; no consumir en pipeline nuevo. |
| EXPERIMENTAL | Ramas E2/gravedad antiguas, drafts, candidates y reconstrucciones aún no aprobadas. | Extraer evidencia o pruebas de forma selectiva. |

No se moverán ni borrarán archivos en la primera pasada. La reorganización se
hará después de definir adaptadores y consumidores para no romper rutas.

## Fuentes canónicas provisionales

| Pregunta | Respuesta actual | Condición para promover nueva versión |
| --- | --- | --- |
| Geometría estructural | `entregas/P1L2/unity_export/model_combined_viewer.json` | Auditorías de columnas, muros, vigas y conectividad completas. |
| Geometría ED1 | `model_1_audited_corrected.json` | Regeneración trazable desde decisiones auditadas. |
| Geometría ED2 | `model_2_viewer.json` | Auditoría equivalente y registro estable de IDs. |
| Modelo FE | `entregas/P1L3/results/a3a4/analysis_model.json` | Reconstrucción posterior a estabilizar geometría. |
| Catálogo de cargas | `load_zones_700_completion/load_catalog_700.json` | Está auditado espacialmente pero aún `NOT_APPLIED`. |
| Resultados entregados | `entregas/P1L3/results/a7/` | Histórico bajo `P1L3_DELIVERED`; no sobrescribir. |
| Arquitectura visual | `entregas/P1L3/arquitectura/architectural_visual_model.json` | Extender por piso manteniendo `participates_in_FE=false`. |
| Unity | `entregas/P1L3/José/viewer_unity/` | Actualizar solo mediante `build_unity_bundle.py`. |
| Viewer histórico | `entregas/P1L2/viewer/` | Antecedente, no interfaz objetivo. |

## Formato del backlog

Prioridad: P0 bloquea la base; P1 alta; P2 media; P3 documental. Estados:
`OPEN`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `UNRESOLVED_FINAL`.

### GEOMETRÍA

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GEO-COL-S1-001 — E1-S1-C-014..019 | Inferencias verticales de Luis | Elevaciones estructurales completas 309 eje I y 310 eje I', más ejes canónicos | Seis `CONFIRMED_BY_AXIS_ELEVATION`; sección 0.70×0.70 m y centro de eje normalizados | Cierra apoyos y continuidad del ala este sin extrapolar plantas | P0 | Fuentes CAD completas | Auditoría reproducible en `validacion/s1_columns_final/`; corregido y regenerado | DONE |
| GEO-WALL-E1-001 — muros S1-P4 | Drafts de extracción | RLE-MURO, 234 muros combinados, reviews por piso | POSIBLE/FRAGMENTADO/FALSO_POSITIVO mezclados | Rigidez y caminos de carga inciertos | P0 | GEO-COL-S1-001 | Auditoría piso a piso, duplicados y continuidad vertical | OPEN |
| GEO-BEAM-E1-001 — vigas S1-P4 | Drafts de extracción | RLE-VIGA, reviews, etiquetas y geometría combinada | POSIBLE/FRAGMENTADA/NEEDS_REVIEW | Paños, carga y conectividad dependen de ellas | P0 | GEO-WALL-E1-001 | Auditoría por piso, receptores, continuidad y vigas especiales | OPEN |
| GEO-SPECIAL-001 — outboard/voladizos/canopias | Extracción automática deficiente fuera de grilla | `outboard_room_reconstruction.json`, planos, fotos secundarias | Grupos `UNRESOLVED_REQUIRES_REVIEW` | Forma real y elementos flotantes | P1 | Muros y vigas estabilizados | Revisar por sector con overlays y evidencia primaria | OPEN |
| GEO-INTERFACE-001 — interfaz ED1/ED2 | Modelos extraídos por separado | Calce D/E confirmado; rama E2 antigua declara interfaz no resuelta | Alineación confirmada, conexión física no auditada | Transferencia entre bloques | P1 | Muros/vigas de ambos lados | Inventariar miembros que cruzan o terminan en junta | OPEN |
| GEO-ID-ED2-001 — estabilidad de IDs ED2 | Regeneración actual puede renumerar | Handoff y extractor ED2 | Sin registro/tombstones formal equivalente a ED1 | Rompe crosswalk/resultados | P1 | Auditoría ED2 | Crear registro persistente antes de regenerar | OPEN |

### LOSAS / ARQUITECTURA

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SLAB-E1-P4-001 — verificar piloto | Commit `807558b` | RLE-LOSA, vigas P4, overlay y auditoría | Piloto vigente, 958.392618 m², no FE | Patrón para niveles restantes | P1 | Ninguna | Revalidar contra base y congelar metodología | OPEN |
| SLAB-E1-001 — S1/P1/P2/P3 | Bounding boxes provisionales | RLE-LOSA, vigas, ejes, notas y huecos | Sin perímetros visuales definitivos | Apariencia, áreas y PP | P0 | Muros/vigas por piso | Reconstruir perímetro/huecos/gaps y documentar cierres | OPEN |
| SLAB-E2-001 — S1-P4 | Bounding boxes provisionales | Serie 2024_22 exclusivamente | Sin reconstrucción auditada | Apariencia, áreas y PP | P0 | Geometría ED2 estable | Aplicar metodología sin copiar ED1 | OPEN |
| ARCH-SEPARATION-001 | Riesgo de mezclar visual/FE | Contrato P4 | P4 declara `participates_in_FE=false` | Evita alterar rigidez/cargas por estética | P0 | Toda extensión arquitectónica | Exigir el campo explícito y validar consumidores | OPEN |

### CONECTIVIDAD FE

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FE-FLOAT-001 — 93 elementos/61 componentes | Topología A3-A4 | `floating_excluded`, déficit 0.763564%, auditorías de rama E2 | Excluidos sin camino a apoyo | Equilibrio y respuesta incompletos | P0 | Geometría estable | Reporte por componente: causa, evidencia, conexión esperada y decisión | OPEN |
| FE-STUB-001 — segmentos cortos | Segmentación de vigas | Rama Luis: taxonomía y verificación EI/L | No clasificados explícitamente en contrato vigente | Fuerzas máximas engañosas | P1 | FE reconstruido | Portar criterio basado en parent/visual/longitud y QA `localForce` | OPEN |
| FE-INTERFACE-001 — conexión de bloques | Junta ED1/ED2 | Ejes coincidentes, sin conexión FE demostrada | No evaluada como sistema integrado | Camino lateral/gravitacional | P1 | GEO-INTERFACE-001 | Resolver solo con detalle/plano; no crear vínculos artificiales | OPEN |

### PROPIEDADES

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PROP-BEAM-001 | Etiquetas CAD parciales | `cad_property_audit.json`; ~431/1060 conocidas | Mayoría UNKNOWN | Rigidez y fuerzas FE | P1 | GEO-BEAM-E1-001 | Asociar etiquetas por planta, layer, eje y continuidad | OPEN |
| PROP-WALL-001 | Espesores parciales | 73/234 conocidos | ~69% UNKNOWN | Rigidez equivalente | P1 | GEO-WALL-E1-001 | Mapear notas y espesores, sin propagar globalmente | OPEN |
| PROP-COL-001 | Geometría vs etiqueta | 150/150 dimensiones geométricas; etiquetas parciales | Dimensión disponible, procedencia heterogénea | Rigidez/capacidad | P1 | GEO-COL-S1-001 | Clasificar CONFIRMED_FROM_PLAN/INFERRED/DEFAULT/UNKNOWN | OPEN |
| PROP-SUPPORT-001 | Apoyos nominales | 3/107 dimensiones conocidas | DEFAULT/UNKNOWN dominante | Condición de borde | P1 | FE-FLOAT-001 | Relacionar fundaciones/pedestales con apoyos reales | OPEN |
| PROP-MATERIAL-001 | Datos de laboratorio y notas | LT2 f'c=35 MPa/fy=420 MPa; otras hipótesis | No hay catálogo por edificio/elemento | Rigidez y capacidad | P1 | Índice de planos/detalles | Crear catálogo trazable por fuente y alcance | OPEN |

### CARGAS

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LOAD-700-001 — catálogo espacial | Láminas 700 | Auditorías c056/c847 y 108 entradas | Geometría confirmada, no aplicada | Entrada correcta para G/Q | P0 | Paños definitivos | Mantener y remapear solo si cambia geometría | OPEN |
| LOAD-Q-001 — Q_POST_P1L3 | Q uniforme histórico | `zone_contributions`, cobertura auditada | Placeholder entregado | Masas, sismo y demanda | P0 | Losas/paños estables | Intersección multizona y conservación por paño/piso/edificio/total | OPEN |
| LOAD-POINT-001 — tres puntuales E1 | Textos sin llamada | Auditoría DXF/DWG c847 | UNRESOLVED | Carga concentrada potencialmente alta | P1 | Geometría/receptores estabilizados | Última correlación con detalles; si no, UNRESOLVED_FINAL y no aplicar | OPEN |
| LOAD-LINE-E1-001 — 800/7600 kgf/m | Banda P4 | Centrolinea 35 m y 11 segmentos compatibles | LIKELY | Afecta Q/G local | P1 | Vigas P4 | Confirmar receptor/distribución o cerrar sin aplicar | OPEN |
| LOAD-LINE-E2-001 — 100/1500 kgf/m | Banda P4 | Geometría localizada, receptor vacío | UNRESOLVED | Afecta Q/G local | P1 | Vigas ED2 P4 | Buscar elemento receptor; si no, UNRESOLVED_FINAL | OPEN |
| LOAD-PP-001 — PP.LOSA | Espesores locales 15/20/25 cm | Fórmula 2500 kgf/m³ confirmada | Espesores no mapeados | G y masas | P0 | SLAB-E1/SLAB-E2 | Zona de losa → espesor → PP con trazabilidad | OPEN |

### OPENSEES

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPS-BASE-001 — reconstrucción FE | FE entregado sobre geometría provisional | A3-A4 y crosswalk | Histórico reproducible | Todo cálculo posterior | P0 | Geometría/conectividad/propiedades | Generar revisión `POST_P1L3_VALIDATED`, sin sobrescribir A7 | OPEN |
| OPS-CASCADE-001 — G/Q/masas/EX/EY/R | Resultados entregados provisionales | A7 con QA lineal | PASS histórico, entradas no finales | Demanda final | P0 | OPS-BASE y cargas | Recalcular en cascada y comparar equilibrio/superposición | OPEN |
| OPS-LOCALFORCE-001 | Riesgo de interpretación global/local | Código vigente usa `eleResponse(...,"localForce")`; rama Luis tiene QA | API correcta, falta QA exhaustivo post-cambio | Interpretación de fuerzas | P1 | OPS-BASE | Incorporar prueba de equilibrio local por miembro | OPEN |

### CAPACIDAD HA

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HA-001 — sección/ID/armadura | Demostración P1L3 | E2-P1-C-002, Fiber, M-φ, P-M | Sección 0.70x0.70 trazable; armadura/recubrimiento hipótesis; P50 parcial | Capacidad no normativa | P2 | Propiedades consolidadas | Revalidar ID y fuentes; conservar si sigue correcto | OPEN |

### UNITY

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UNITY-001 — actualización final | Bundle P1L3 | UI QA PASS y filtros funcionales | Funcional sobre snapshot entregado | Interfaz de la nueva base | P1 | Modelos/resultados post-P1L3 | Regenerar por adaptador; no editar números a mano | OPEN |
| UNITY-002 — regresión UI | Cambios futuros de datos/capas | `UI_QA.md`, `[UI QA] PASS` | Baseline estable | Riesgo de perder filtros/IDs/gráficos | P1 | UNITY-001 | Mantener batería UI y comparación con snapshot | OPEN |

### PIPELINE

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PIPE-001 — entrada única | Muchos scripts por fases | Handoff sección 13 | Flujo documentado pero fragmentado | Reproducibilidad | P1 | Definir canónicos | Crear orquestador/manifest sin reescribir lógica validada | OPEN |
| PIPE-002 — fuentes locales ignoradas | `recursos/planos/` fuera de Git | Índice 60/60 y AutoCAD local | Otra máquina no puede regenerar | Reproducibilidad del equipo | P0 | Política de distribución | Manifest de hashes, rutas relativas y procedimiento de conversión | OPEN |
| PIPE-003 — provenance de generados | JSON parecidos | Algunos manifiestos A7/Unity | Inconsistente entre P1L2/P1L3 | Difícil saber qué está vigente | P1 | PIPE-001 | Hash de entradas, script, commit y estado en cada artefacto canónico | OPEN |

### DOCUMENTACIÓN

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DOC-001 — backlog maestro | Pendientes dispersos | Handoff, STATUS, reportes y ramas | Creado en este archivo | Evita perder decisiones | P0 | Ninguna | Actualizar en cada hito | DONE |
| DOC-002 — handoff consolidado | Handoff describe todavía trabajo previo | `PROJECT_HANDOFF.md` | Snapshot añadido; consolidación incompleta | Continuidad de trabajo | P1 | Todos los hitos | Completar sección POST-P1L3 al final | IN_PROGRESS |
| DOC-003 — matriz canónica | Cinco JSON parecidos | Inventario FASE 0 | Respuesta provisional definida | Riesgo de usar artefacto incorrecto | P1 | Consolidación | Promover una única respuesta por dominio | OPEN |
| DOC-004 — registro de incertidumbres | Estados heterogéneos | JSON/reportes actuales | No centralizado | Puede ocultar unresolved | P1 | Auditorías | Índice final PASS/PASS_WITH_NOTES/UNRESOLVED_FINAL/FAIL | OPEN |

### GIT / ORGANIZACIÓN

| Issue | Origen | Evidencia disponible | Estado actual | Impacto | Prioridad | Dependencia | Solución propuesta | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GIT-001 — preservar P1L3 | No había tag | Hash indicado `c847c13` | Tag y rama aislada creados | Reconstrucción garantizada | P0 | Ninguna | No mover el tag | DONE |
| GIT-002 — ramas no integradas | Cinco ramas remotas históricas | Auditoría Git FASE 0 | Clasificadas, sin merge | Evita regresiones | P0 | Ninguna | Portar selectivamente con evidencia | DONE |
| GIT-003 — archivos históricos | Candidates, backups, results, viewers | Inventario actual | No borrados ni movidos | Desorden y rutas ambiguas | P2 | Canónicos definidos | Crear mapa de deprecación y luego adaptadores | OPEN |
| GIT-004 — estrategia de integración | `main` detrás del tag | Historial actual | Consolidación aislada | Integración futura requiere revisión | P1 | Validación global | PR/revisión al terminar; nunca force push | OPEN |

## Orden de ejecución ajustado

El orden propuesto se mantiene, con dos dependencias explícitas:

1. Columnas S1.
2. Muros ED1.
3. Vigas ED1.
4. Sectores especiales e interfaz.
5. Losas ED1 y ED2.
6. Conectividad FE y componentes flotantes.
7. Propiedades.
8. Paños, PP.LOSA y cargas 700.
9. Recálculo OpenSees POST-P1L3.
10. Capacidad HA.
11. Unity.
12. Canónicos, orden, handoff y validación global.

La conectividad se deja después de las losas visuales solo para el cierre FE;
sin embargo, se medirá en paralelo durante muros/vigas para no perder las causas
de cada componente flotante.

## Hitos ejecutados

### FASE 1 — columnas S1

- `E1-S1-C-014..019` quedaron `CONFIRMED_BY_AXIS_ELEVATION`.
- Las elevaciones 309/I y 310/I' miden 8.90 m entre ejes 1–2 y 7.25 m entre
  2–3, residual 0.000 m respecto del sistema canónico.
- En las seis estaciones existe rótulo `P. 70x70` y contorno continuo bajo el
  primer piso hasta vigas de fundación.
- Los centros se normalizaron a I/I' × 1/2/3 y la sección a 0.70×0.70 m. La
  corrección mayor fue `E1-S1-C-016`, antes 0.85×0.92 m y fuera del centro de
  eje por la envolvente automática de planta.
- Evidencia: `entregas/P1L2/edificio/validacion/s1_columns_final/REPORT.md` y
  `s1_columns_final_audit.json`.
- Regenerados `model_1_audited_corrected.json` y
  `model_combined_viewer.json`. Calce, continuidad, geometría combinada,
  enriquecimiento y diff de referencia: `PASS`.
- `LUIS_REFERENCE_FILES_MODIFIED = 0`.

## Próximo hito

`FASE 2 — GEO-WALL-E1-001`: auditoría piso a piso de muros EDIFICIO_1,
incluyendo fragmentación, duplicados, falsos positivos y continuidad vertical.
