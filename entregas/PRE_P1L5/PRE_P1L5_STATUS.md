# PRE-P1L5 — estado y baseline de trabajo

**PRE_P1L5_BASELINE: BLOCKED** para declararla base estructural cerrada.
La interfaz y la documentación consolidada son utilizables. No se implementó
P1L5 ni se corrió OpenSees. No se creó un tag READY engañoso.

Rama: `codex/post-p1l4-structural-audit`. Hitos exactos: `git log` de esta carpeta
y [CHECKPOINTS.md](CHECKPOINTS.md). P1L4_FINAL permanece en
`56e24ac0568b24eba3cf119f2e3cc66fc0af3a35`.

## Qué está disponible

- Revisión 2026-09-23: [REVIEW_STATUS](user_structural_review/REVIEW_STATUS.md).
- Geometría CURRENT: 791 sólidos; 143 columnas, 511 vigas, 74 muros,
  10 losas visuales y 53 apoyos geométricos. 116 exclusiones aprobadas y dos fusiones.
- Propiedades: 644 miembros actuales con G35_10/fc35 MPa y A630-420H/fy420 MPa.
  Notas primarias 2024_22-100/53994 y 2017_67-100/1E116; propiedades de sobrevivientes intactas.
  Lámina 600 = sala eléctrica, no excepción genérica de escaleras. ED1 P4 y
  losas no asignados. No se dedujeron E ni armaduras.
- FE candidato: 736 miembros, 7 relaciones 1:N, 22 residuales/16 componentes.
  No hay FE canónico ejecutable aprobado nuevo: no llamar “canónico” al candidato.
- Resultados actuales: NONE. G/Q/EX/EY/R y P-M son históricos y opt-in.
- Entregas P1L2/P1L3/P1L4/POST-P1L4 + Evolución y Estado del proyecto en Unity.
- QA local histórico ampliado: 6560 barra/casos y 1312 ejes PASS.
- Catálogo de cargas 700 separado de los resultados; no hay cargas definitivas
  completas aprobadas para CURRENT.

## Bloqueos exactos / fuente que debe resolverlos

| Bloqueo | Evidencia / responsable de decisión | Qué falta |
|---|---|---|
| 22 caminos FE / 16 componentes | Planos y decisión estructural del grupo | Confirmar transferencias, exteriores restantes, bordes y muros; no apoyos ficticios |
| Brazos rígidos encadenados | FE-2, clusters hasta 26.448 m en planta | Revisar físicamente alcance del cuerpo rígido y formulación del adaptador |
| Alineación columnas >5 cm | Contraste S1/P1 vs P2–P4 | Desfase habitual ~18 cm: resolver transformación por planta antes de mover |
| Material ED1 P4/losas | Nota 100 termina en cielo P3; 600 G25 es sala eléctrica | Confirmar alcance superior y losas; no extrapolar G35 |
| ED1 S1/P1 y huecos | RLE-LOSA, arquitectura, cortes | Cerrar perímetro exterior/transición outboard y distinguir vacíos de bordes de paño |
| 8 muros con huellas solapadas | Tabla individual en REMAINING_STRUCTURAL_AUDIT | Cuatro redondeos y otros offsets/esquinas: validar incidencia FE, no eliminar |
| G/Q definitivos | Catálogo 700, PP.LOSA, cargas especiales | Completar cobertura, unidades, receptores y áreas netas antes de masas/sismo |

La normalización 1482→946 enlaces es **propuesta algebraica**, no corrección
aplicada: conserva relaciones de un grafo que aún puede imponer rigidez física
excesiva. No cerrar este bloqueo solo por residual cinemático pequeño.
Sus números de nodo son históricos. Usar `user_structural_review/current_constraint_clusters.json`
para el candidato actual (1346 restricciones). Las 19 alturas desconocidas pertenecían a
elementos excluidos, no fueron resueltas por asignación de valores.

## Fuentes canónicas y no canónicas

| Uso | Archivo / estado |
|---|---|
| ED1 geometría | entregas/P1L2/unity_export/model_1_audited_corrected.json |
| ED2 geometría | entregas/P1L2/unity_export/model_2_viewer.json |
| Geometría combinada actual | entregas/P1L2/unity_export/model_combined_viewer.json |
| Propiedades primarias actuales | entregas/PRE_P1L5/primary_material_catalog.json + scripts/primary_materials.py |
| FE candidato NO EJECUTADO | entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json |
| Cargas 700 auditadas NO APLICADAS | entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json |
| Resultados históricos | entregas/P1L3/results/a7/cases/{G,Q,EX,EY,R} |
| Unity único | entregas/P1L3/José/viewer_unity/Assets/Main.unity |
| Metadata proyecto | entregas/PRE_P1L5/project_state.json → StreamingAssets/project_state.json |
| QA PRE5 | entregas/PRE_P1L5/global_validation.json + GLOBAL_VALIDATION.md |
| No aplicar | constraint_normalization_proposal.json, propuestas de losas EXT-4 |

`Luis model_viewer.json` es referencia histórica inmutable, NO CURRENT.
Los resultados candidate viejos permanecen para reproducibilidad, no se borran.
Los scripts apply_* son migraciones de checkpoints, no deben ejecutarse todos
indiscriminadamente. Ningún original CAD se agrega en este hito.

## Regeneración segura sin OpenSees

Desde la raíz, con Python y dependencias CAD disponibles:

```text
python entregas/PRE_P1L5/scripts/primary_materials.py --apply
python entregas/PRE_P1L5/scripts/audit_historical_equilibrium.py
python entregas/P1L3/scripts/build_unity_bundle.py
python entregas/PRE_P1L5/scripts/build_project_state.py
python entregas/PRE_P1L5/scripts/validate_pre5.py
```

La aplicación de materiales es idempotente. Si se reconstruye geometría desde
los modelos por edificio, ejecutar build_combined_model y enrich_combined_model
en su orden vigente; el enriquecedor integra la asignación primaria ED2.
También integra ED1 principal S1–P3. Para renovar evidencia del título 600,
ejecutar `directed_source_review.py` antes de `primary_materials.py`.
No rehacer modelos originales de entregas ni aplicar globalmente materiales.

Revisión de fuentes (solo lectura) reproducible:
`audit_remaining.py --santiago <snapshot> --caceres <snapshot>`,
`render_material_notes.py`, `report_remaining.py`. Requiere ezdxf/shapely/matplotlib.

## Abrir y demostrar Unity

Abrir `Abrir_Unity.bat`, Main y Play. Modelo actual por defecto.
ENTREGAS abre resúmenes y enlaces sin habilitar históricos. En P1L3/P1L4 el
botón histórico es explícito y advierte incompatibilidad. R restablece CURRENT,
H limpia pantalla, F11 presentación. En ED2 seleccionar una columna y abrir
Detalle técnico para ver nota primaria/material; no confundir fc con E.
El inspector nuevo abre Resumen y Resultados; propiedades, conexiones, cargas,
ejes, capacidad, fuente y detalle son retraíbles. No muestra esfuerzos archivados
en el uso normal. Ver `current_readiness/CURRENT_READINESS_REPORT.md` para el
último diagnóstico y `current_readiness/CURRENT_RESULTS_CONTRACT.md` para versiones.

Prueba automatizada: `CurrentReviewBuild.Build` y ejecutable `--ux-review`.
Valida filtros, aislamiento histórico, Entregas, propiedades, ejes y gráficos
en dos resoluciones. QA visual conservado en `qa/`.

## Lo aprendido y límite del cierre

Santiago: explicaciones/consultas por entrega y P-M multicaso; rechazados
apoyos artificiales, curva auxiliar sin carga de elemento e inconsistencias
de material. Cáceres: QA exhaustivo local/ejes (adoptado), balance de huecos,
propiedades por región y detalle de refuerzo (pistas, no copias automáticas).
Los informes separados y matriz explican qué se adoptó y qué no.

La relectura ampliada encontró notas materiales omitidas antes. Por ello no
es correcto afirmar que “ya no queda información en los planos”. Persisten
asociaciones y decisiones físicas que esta pasada no resolvió; deben revisarse
con el grupo antes de declarar READY. Los históricos continúan reproducibles.
