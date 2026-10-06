# Saneamiento estructural 2 — revisión PRE-P1L5

Base histórica de esta revisión: `d323e248434162bfc8cd5a888ad6578cd3600ac9`. Rama `codex/post-p1l4-structural-audit`. Commit evaluable del checkpoint: consultar el commit que contiene este archivo (`git log -1 --format=%H -- entregas/PRE_P1L5/second_structural_cleanup/REVIEW_STATUS.md`).

**Checkpoint geométrico para revisión. PRE_P1L5_BASELINE: BLOCKED.** No se ejecutó OpenSees, no se recalcularon cargas/resultados y no se inició P1L5.

## Muros y apoyos

44 muros ED1 excluidos por decisión de alcance: **cero activos**. Esto no significa que el edificio real no tenga muros ni certifica la resistencia del modelo sin ellos. Se archivó su geometría.

Se retiraron siete apoyos visuales exclusivos de muro y 13 restricciones de base exclusivas de muro del candidato FE. Se preservaron los 19 apoyos visuales de columnas, los ocho compartidos y las restricciones de base de todas las columnas. Apoyos UNKNOWN: ninguno. Los apoyos generados de columnas siguen su nuevo XY; no se trasladaron cimentaciones levantadas en terreno.

Detalle de los 34 apoyos ED1: [ED1_WALL_SCOPE_REMOVAL_AUDIT](../ED1_WALL_SCOPE_REMOVAL_AUDIT.md).

## Vigas

511 vigas inspeccionadas; 67 pares candidatos; 13 cadenas candidatas de tres miembros. Se fusionaron 16 pares nuevos (32 fragmentos → 16 vigas); sumando las dos fusiones anteriores: 18 pares históricos corregidos. No se fusionó una cadena de tres sin evidencia completa.

| ID canónico | ID absorbido | Gap original m | Motivo de conservar ID |
|---|---|---:|---|
| E2-P4-V-060 | E2-P4-V-059 | 0.091000 | Etiqueta directa; luego tramo histórico más largo |
| E2-P4-V-081 | E2-P4-V-080 | 0.091000 | Etiqueta directa; luego tramo histórico más largo |
| E2-P4-V-085 | E2-P4-V-090 | 0.174500 | Etiqueta directa; luego tramo histórico más largo |
| E2-P4-V-071 | E2-P4-V-070 | 0.091000 | Etiqueta directa; luego tramo histórico más largo |
| E2-P4-V-016 | E2-P4-V-015 | 0.091000 | Etiqueta directa; luego tramo histórico más largo |
| E2-P4-V-037 | E2-P4-V-036 | 0.091000 | Etiqueta directa; luego tramo histórico más largo |
| E1-S1-V-021 | E1-S1-V-019 | 0.089900 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-016 | E1-P1-V-012 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-044 | E1-P1-V-042 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-062 | E1-P1-V-060 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-107 | E1-P1-V-105 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-029 | E1-P1-V-026 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-054 | E1-P1-V-050 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P1-V-079 | E1-P1-V-076 | 0.200000 | Etiqueta directa; luego tramo histórico más largo |
| E1-P2-V-021 | E1-P2-V-018 | 0.004700 | Etiqueta directa; luego tramo histórico más largo |
| E1-P2-V-041 | E1-P2-V-043 | 0.004700 | Etiqueta directa; luego tramo histórico más largo |

Otros 51 pares no se fusionaron: 26 sin caras continuas inequívocas; 19 con anotaciones de abertura/junta o indicios CAD de apoyo que requieren resolver la llamada; cinco con apoyo físico intermedio; uno con altura inferida. No se afirma que los 51 sean discontinuidades reales.

Se detectaron 0 miembros menores de 0.30 m; no se borraron por longitud. Las 16 vigas fusionadas tienen longitud FE concordante dentro de 0.4 mm y ningún segmento nuevo menor de 2 cm.

## Columnas y patrón 18,13 cm

143 columnas revisadas, 38 grupos de continuidad. 74 ajustes XY: {'<=1cm': 36, '1–5cm': 0, '5–10cm': 0, '>10cm': 38}. Máximo 0.201318 m. 36 ajustes son menores de 0.1 mm. Se preservaron Z, dimensiones, sección y material. 14 columnas en 12 grupos siguen en revisión; no se forzó su alineación.

La prueba usa LINE de RLE-EJES, no inserciones de texto: P1 transforma el eje 1 a −0.000030 m; P2 a +0.181358 m; P3/P4 a +0.181341/+0.181321 m. La diferencia de registro P1→P2 es +0.181388 m. S1 incorpora columnas inferidas desde P1, por eso hereda ese desfase aunque su propia planta tenga otro origen. No son decenas de transferencias independientes.

Además, el extractor promediaba extremos de segmentos: al cortar una cara o subdividirla en varias líneas, desplazaba el centro. Ejemplos primarios: P1 C002 (cara incompleta), C013 (cara cortada), C021/C022 (fragmentos asimétricos), P2 C004/C010 (cara superior subdividida). Se reconstruyó el centro entre caras opuestas o del rectángulo cerrado y se contrastó cada arista con handles del DXF.

**Referencia adoptada:** contorno primario P2 de cada stack y controles de P3/P4. Se alinearon únicamente columnas y apoyos visuales generados de esas columnas; no se trasladaron plantas completas ni se alteraron ejes globales o transformaciones 700 aprobadas. La diferencia de ~0.181 m entre ese registro de columnas y los ejes globales nominales permanece explícita; debe reconciliarse antes de aprobar cargas/FE. No debe presentarse como calce global resuelto.

P1 C023 conserva su dimensión geométrica previa, aunque el rectángulo principal CAD es distinto; está marcado `UNCHANGED_DIMENSIONS_REVIEW_REQUIRED`, no se cambió la sección durante esta operación.

## Controles externos

Santiago aporta columnas con continuidad por pisos en el snapshot c1f434b; para una estación como E1-S1-C004 su XY normalizado previo es (37.47,0.18), cercano al piso superior nuestro. Cáceres aporta la retícula manual vertical: C-8 normalizada a (37.49,0.18). Ambas son pistas concordantes, no prueba métrica: las transformaciones externas originales siguen siendo ajustes de nube de puntos candidatos. Los movimientos se decidieron por contornos/ejes propios. No hubo escritura ni ejecución de código en los repositorios externos.

## Candidato reconstruido

676 miembros; 1183 nodos; 1205 restricciones; 33 apoyos FE; siete relaciones geometría→varios segmentos FE. Seis geometrías sin camino a apoyo / cuatro componentes. No se ha validado su formulación rígida ni ejecutado el solver.

Pendientes: E1-S1-V-005, E2-P4-V-004, E2-P4-V-005, E2-P4-V-006, E2-P4-V-007, E2-P4-V-009. `E1-S1-V-005` es nuevo tras retirar su sistema de muros; no se le inventó apoyo. La reducción 22→6 no es prueba de mejor comportamiento resistente: principalmente refleja el cambio de alcance.

## Unity

Abrir `entregas/P1L3/José/viewer_unity`, `Assets/Main.unity`, Play. Modelo actual sin muros ED1; resultados actuales NONE. Diagnóstico → Cambios de esta revisión muestra WALL_REMOVED / WALL_SUPPORT_REMOVED / BEAM_MERGED / COLUMN_ALIGNED / REVIEW_REQUIRED. Diagnóstico → COLUMN STACKS aísla cada cadena, permite apagar S1/P1/P2/P3/P4 y usar vistas XZ/YZ. R vuelve al edificio.

## QA

- ED1_ACTIVE_WALLS_ZERO: PASS
- COLUMN_SUPPORTS_PRESERVED: PASS
- SHARED_SUPPORTS_PRESERVED: PASS
- UNKNOWN_SUPPORTS_PRESERVED: PASS
- COLUMNS_PRESERVED: PASS
- SLABS_PRESERVED: PASS
- STABLE_IDS: PASS
- CROSSWALK: PASS
- NO_EXCLUDED_FE: PASS
- FE_INPUT_HASH: PASS
- NO_ANALYSIS: PASS
- LUIS_REFERENCE: PASS
- FE_COLUMN_SHARED_SUPPORTS_PRESERVED: PASS
- COLUMN_XY_TARGET: PASS
- COLUMN_Z_SECTION_MATERIAL_PRESERVED: PASS
- STABLE_GLOBAL_AXES: PASS
- STACK_VERTICALITY: PASS
- MERGED_BEAM_LENGTHS_NO_MICROSEGMENTS: PASS
- NO_DUPLICATE_FE_MEMBER: PASS
- NO_DUPLICATE_FE_NODE: PASS
- DELIVERED_TAGS_PRESERVED: PASS
- HISTORICAL_RESULT_INPUTS_UNCHANGED: PASS
- BEAM_FRAGMENTATION: PASS_WITH_NOTE
- COLUMN_ALIGNMENT: PASS_WITH_NOTE
- UNITY_COMPILE: PASS
- UNITY_PLAY: PASS

## Fuentes vigentes

- Geometría ED1: `entregas/P1L2/unity_export/model_1_audited_corrected.json`.
- Geometría ED2: `entregas/P1L2/unity_export/model_2_viewer.json`.
- Contrato conjunto: `entregas/P1L2/unity_export/model_combined_viewer.json`.
- FE candidato: `entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json`.
- Datos auditables: `wall_scope_audit.json`, `GLOBAL_BEAM_FRAGMENTATION_AUDIT.json`, `COLUMN_VERTICAL_STACKS.json`, `confirmed_beam_pairs.json`, `review_qa.json`.
- Receptores: `current_tributary_receptor_crosswalk.json`, elegibilidad únicamente; cargas no aplicadas.

Regeneración segura después del checkpoint: build_combined_model.py → enrich_combined_model.py → build_post_p1l3_topology_candidate.py → build_unity_bundle.py → report_second_cleanup.py → build/Play QA. Las migraciones --apply-walls y apply_second_geometry.py están protegidas contra reaplicación; no se deben repetir sobre CURRENT. Los informes de propuesta documentan el estado previo, no deben sobrescribirse con una nueva auditoría post-migración.
