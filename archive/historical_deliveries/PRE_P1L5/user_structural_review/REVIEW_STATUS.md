# PRE5 — revisión manual, exclusiones y vigas continuas

Checkpoint aplicado sobre `b11d12d`, rama `codex/post-p1l4-structural-audit`.
**REVIEW_REQUIRED / no iniciar P1L5. CURRENT_RESULTS = NONE.**
Las correcciones confirmadas están incorporadas; la alineación de columnas se detiene por contradicción primaria de registro de plantas.

## Resultado

| Métrica | Antes | Ahora |
|---|---:|---:|
| Sólidos canónicos | 909 | 791 |
| Columnas | 150 | 143 |
| Vigas | 567 | 511 |
| Muros | 122 | 74 |
| Apoyos geométricos | 60 | 53 |
| Losas visuales | 10 | 10 |
| Miembros FE candidatos | 856 | 736 |
| Sin camino FE a apoyo | 43 | 22 |
| Componentes sin camino FE a apoyo | 22 | 16 |

De los 43 pendientes previos: **15 excluidos del alcance, 6 recuperados por continuidad vertical, 22 permanecen, 0 nuevos**. No se atribuye una exclusión a una reparación resistente.

## Exclusiones exactas y núcleo

Las **116 exclusiones** de [EXCLUSION_APPROVAL.md](EXCLUSION_APPROVAL.md) fueron aprobadas expresamente por Matías antes de aplicarlas. Todas conservan snapshot, ID, razón, fuente y fecha en [CURRENT_MODEL_EXCLUSIONS.json](../CURRENT_MODEL_EXCLUSIONS.json).

- ED1: cadenas M007/M008/M002 identificadas en [REMOVAL_CHAIN_PROPOSAL.md](REMOVAL_CHAIN_PROPOSAL.md). No se añadió un muro S1 supuesto para M002. No hubo recorrido indiscriminado por contactos.
- ED2: se retiró el grupo este, incluidas las continuidades y el paño inferior M009 S1–P3; se conservó el grupo oeste M001–M006 de cada piso, alrededor de los M002/M003 indicados por el usuario.
- S1: 53 elementos del sector sur entre M001 y M060: 7 muros, 7 apoyos y 39 vigas. Ver [propuesta espacial](S1_EXTERIOR_REMOVAL_PROPOSAL.md). No fue un rango de IDs ni todos los elementos OUTBOARD.
- C007/C009 P1: retiradas tras aclaración expresa; P2 se conserva. La conectividad del grafo no demuestra la suficiencia de la transferencia del volumen que sobresale.
- M028/M029 P1: retirados tras advertir y confirmar que son interiores del eje I; **no** se reclasificaron falsamente como exteriores.
- Escaleras: retiradas las vigas/columnas explícitas, incluido V075 P2. Subsisten paños exteriores P1 en el diagnóstico; no se agregaron al lote aprobado por mera proximidad.

Los muros excluidos existen en CAD: esta es una decisión de alcance, no una certificación de que el edificio real carezca de ellos. No está aprobada la suficiencia estructural del modelo sin esos miembros.

## Fusiones

| IDs anteriores | ID canónico | Gap original | Longitud actual | FE |
|---|---|---:|---:|---|
| E2-P4-V-042 + E2-P4-V-046 | E2-P4-V-042 | 0.1745 m | 2.5148 m | 1 geometría → 1 segmento |
| E2-P4-V-048 + E2-P4-V-049 | E2-P4-V-049 | 0.0910 m | 8.0004 m | 1 geometría → 1 segmento |

Ambos pares: mismo piso, sección 60/80, cota, orientación, caras CAD continuas y sin apoyo intermedio en el hueco. Son fragmentaciones de extracción, no pequeños errores de coma flotante. `merged_from` conserva los IDs retirados; no se renumeraron sobrevivientes. La decisión de ID favorece el tramo principal/etiquetado y la mayor continuidad geométrica previa.

La [auditoría de todas las vigas](../BEAM_FRAGMENTATION_AUDIT.md) cribó 567 vigas y obtuvo 90 pares candidatos amplios: dos comprobados y fusionados; los otros 88 se clasifican por sección, apoyo, alcance o revisión CAD pendiente. No se fusionaron automáticamente. No se afirma haber probado una junta real donde solo falta evidencia.

## Continuidad de muros

Se aplicó una excepción numérica **solo** a P1-M002 → P2-M003 y P1-M012 → P2-M010 de ED1. Separación transversal 0.1 mm; solape longitudinal real >0.5 m. El adaptador exige pisos contiguos, mismo edificio, paralelismo y separación ≤1 mm. No mueve geometría, no crea apoyos, no conecta por losas visuales.

Recupera las rutas de E1-P2-M003/M010, E1-P3-M003/M010 y E1-P4-M003/M009. Ver [diagnóstico después](FE_PENDING_AFTER_USER_REVIEW.md) para la lista completa de los 22 restantes.

## Columnas: contradicción que requiere nueva revisión

**0 columnas movidas; desplazamiento aplicado máximo 0 m.** Cero en todos los intervalos solicitados (<1 cm, 1–2, 2–5 y >5 cm).
Se compararon 45 columnas ED1 S1/P1 con candidatas superiores. Los 15 [controles primarios RLE-EJES](COLUMN_AXIS_PRIMARY_CONTROLS.md) muestran ~+0.181 m en S1/P2/P3/P4 con las transformaciones de caras/ejes vigentes, frente a P1 prácticamente en los ejes canónicos. Algunas columnas S1 se normalizaron usando otro origen.

Por ello **no** se toma automáticamente el XY superior como verdad ni se trasladan solo las columnas inferiores. Próximo bloque: reconciliar transformación de cada planta completa con ejes canónicos, verificar vigas/muros/losas y registros de cargas antes de aplicar una corrección >5 cm. El calce 700 aprobado no se modificó. [Detalle](../COLUMN_ALIGNMENT_AUDIT.md).

## Propiedades, cargas y FE

- Propiedades de todos los sobrevivientes: sin cambios. 644 materiales confirmados por nota primaria en miembros activos.
- Las 19 alturas desconocidas correspondían a miembros ahora excluidos; no se dedujeron ni rellenaron alturas.
- Se regeneraron FE, nodos, crosswalk, incidencias y componentes. El candidato sigue sin ejecutar ni aprobar; 1346 restricciones requieren revisión de idealización.
- [Clústeres actuales](current_constraint_clusters.json): numeración regenerada. Las propuestas antiguas 1482→946 y sus números de nodo son históricas, no aplicables directamente.
- [Receptores tributarios](current_tributary_receptor_crosswalk.json): elegibilidad/aliases actualizados. **No** es reparto nuevo de áreas o cargas: deben reconstruirse las áreas receptoras con la nueva geometría antes de aprobar Q. Cargas históricas intactas; ninguna carga aplicada al candidato actual. No se suman dos cargas históricas por fusionar IDs.

## QA y Unity

- PASS: contrato de pisos, conservación del sistema de ejes declarado, geometría fuente→combinado, IDs, propiedades, duplicados, exclusiones del FE, crosswalk, fusiones, referencia Luis y resultados históricos.
- REVIEW_REQUIRED: registro físico de plantas/ejes primarios, alineación, caminos FE restantes e idealización de restricciones. Un PASS del contrato de ejes no resuelve la contradicción primaria recién detectada.
- Unity: compilación y QA Play en 1366×768 y 1920×1080; resultado verificable en `UNITY_REVIEW_QA.md`. Se preserva la organización de paneles.
- Diagnóstico → Cambios de esta revisión: MERGED, REMOVED, CONNECTIVITY_FIXED, REVIEW_REQUIRED; IDs históricos y fuente. La lista REMOVED es registro, no sólidos estructurales actuales.
- Los 43 expedientes anteriores se conservan; el panel Pendientes FE usa el nuevo listado de 22 ligado al hash de geometría.
- P1L2/P1L3/P1L4, P1L4_FINAL, Luis y repos externos intactos. No G/Q/EX/EY/R/P-M nuevos.

## Regenerar sin repetir exclusiones

Desde las fuentes actuales: `build_combined_model.py` → `enrich_combined_model.py` → `build_post_p1l3_topology_candidate.py` → `build_unity_bundle.py` (incluye `finalize_user_review.py`). Validar con `validate_combined_geometry.py` y `validate_luis_reference_diff.py`, luego compilar/Play Unity.
`apply_user_review.py` es migración con guardas de hash desde el checkpoint previo; no se vuelve a aplicar sobre el estado actual.

Unity canónico: `entregas/P1L3/José/viewer_unity`, `Assets/Main.unity`, Play, modelo CURRENT y resultados actuales NONE.
