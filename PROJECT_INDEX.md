# Índice maestro del proyecto

Estado: `POST-P1L4 / EXT-5 + UNITY CURRENT UX`

Rama de trabajo: `codex/post-p1l4-structural-audit`

Snapshot P1L4 preservado: tag `P1L4_FINAL`, commit `56e24ac0568b24eba3cf119f2e3cc66fc0af3a35`

Interfaz visual principal única: Unity de José

Este índice responde qué archivo debe usarse hoy. El inventario máquina a
máquina de todos los archivos, hashes, ramas y duplicados está en
`REPOSITORY_INVENTORY.json` y se regenera con
`tools/inventory_repository.py`.

## Inicio rápido

1. Doble clic en `Abrir_Unity.bat`.
2. En Unity, abrir `Assets/Main.unity` y pulsar **Play**.
3. Para revisar los contratos sin recalcular OpenSees, doble clic en
   `Validar_Modelo.bat`.

Unity 6000.6.0f1 debe tener una licencia activa mediante Unity Hub. El botón no
instala ni activa licencias.

## Estado que muestra Unity

La interfaz normal muestra únicamente el modelo actual. El histórico requiere
activación explícita en Avanzado y nunca se presenta como resultado vigente:

| Capa | Estado | Interpretación |
| --- | --- | --- |
| Geometría | `POST_P1L4_CURRENT` | 909 sólidos; auditorías EXT-1 a EXT-4, sin cambios geométricos en EXT-5. |
| Diagnóstico FE | `CANDIDATE / NOT RUN` | 856 miembros, 16 relaciones 1:N; 43 geometrías flotantes / 22 componentes. |
| Resultados actuales | `NONE` | Sin corrida compatible; fuerzas, deformada y demanda actuales no disponibles. |
| G/Q/EX/EY/R y capacidad anteriores | `HISTORICAL` | Avanzado → Histórico, apagado por defecto. |
| Catálogo de cargas | Auditadas, no aplicadas | No confundir su geometría con G/Q recalculados. |

El diagnóstico visible cubre 116 elementos: 63 `CONNECTED_EXPECTED`, 10
`FREE_END_EXPECTED`, 31 `DISCONNECTED_ERROR` y 12 `UNRESOLVED`.
Estos dos últimos grupos son las 43 geometrías flotantes; se incluye ahora
`E2-P4-V-009`, antes omitida del foco. Un extremo libre en el grafo no prueba
por sí solo un voladizo real. Ver [EXT-5](entregas/POST_P1L4/EXT_5_REMAINING_AUDIT.md)
y [guía/QA Unity](entregas/POST_P1L4/UNITY_CURRENT_UX_QA.md).

## Fuentes canónicas

| Componente | Ruta canónica | Estado/uso |
| --- | --- | --- |
| Planos originales | `C:/Users/matis/OneDrive/Documentos/Planos_edificio_ingeniera/` | Fuente primaria local, no versionada. Planos/cotas/ejes > fotos > inferencia. |
| Ejes globales | `entregas/P1L2/edificio/datos/global_axes.json` | Vigente. |
| Geometría ED1 | `entregas/P1L2/unity_export/model_1_audited_corrected.json` | Vigente; no confundir con `model_1_audited.json`. |
| Geometría ED2 | `entregas/P1L2/unity_export/model_2_viewer.json` | Vigente. |
| Geometría combinada | `entregas/P1L2/unity_export/model_combined_viewer.json` | Única geometría actual para consumidores. |
| Referencia de Luis | `entregas/P1L2/unity_export/model_viewer.json` | Solo lectura; referencia histórica, nunca regenerar ni modificar. |
| Modelo FE actual | `entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json` | Candidato topológico, no aprobado y no ejecutado. |
| Modelo FE entregado | `entregas/P1L3/results/a3a4/analysis_model.json` | Histórico P1L3; conservar para reproducibilidad. |
| Catálogo de cargas | `entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json` | 108 entradas; `READY_FOR_Q_REVIEW_NOT_APPLIED`; G y Q separados. |
| Resultados entregados | `entregas/P1L3/results/a7/` | Histórico `G/Q/EX/EY/R`, no recalcular en esta etapa. |
| Capacidad HA | `entregas/P1L3/capacidad_ha/` | Histórico de laboratorio, separado del modelo global. |
| Unity | `entregas/P1L3/José/viewer_unity/` | Única interfaz primaria. Escena `Assets/Main.unity`. |
| Bundle Unity | `entregas/P1L3/scripts/build_unity_bundle.py` | Único adaptador de fuentes a `StreamingAssets`. No edita números a mano. |
| Validación Unity | `entregas/P1L3/scripts/validate_unity_integration.py` | Verifica geometría, hashes, estados y crosswalk sin OpenSees. |
| OpenSees entregado | `entregas/P1L3/scripts/run_p1l3_integrated.py` + `entregas/P1L3/p1l3/` | Pipeline histórico reproducible; no ejecutar hasta validar Q completo. |

## Artefactos no canónicos

| Ruta | Clasificación | Decisión |
| --- | --- | --- |
| `entregas/P1L2/viewer/` | `LEGACY_DEBUG_VIEWER` | Consulta técnica histórica. No es interfaz de presentación ni debe crecer. |
| `entregas/semana2/viewer/` | `DELIVERED_LEGACY_VIEWER` | Entrega histórica autocontenida. No modificar salvo corrección histórica explícita. |
| `entregas/P1L2/unity_export/model_1_audited.json` | `SUPERSEDED_RETAINED` | Checkpoint anterior a la geometría corregida. |
| `model_viewer_candidate.json` y backups `model_viewer_*backup*` | `SUPERSEDED_RETAINED` | Evidencia de recuperación; no usar como entrada. |
| `entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/` | `GENERATED_ADAPTER` | Copias necesarias para ejecución Unity; sus fuentes se declaran en `integration_manifest.json`. |

## Ramas

| Rama remota | Clasificación | Acción |
| --- | --- | --- |
| `origin/codex/post-p1l4-structural-audit` | `CURRENT` | Auditoría y Unity vigentes. |
| `origin/codex/pre-p1l4-consolidation` | `HISTORICAL` | Consolidación anterior. |
| `origin/main` | `SHARED_MAIN_REVIEW_BEFORE_INTEGRATION` | Tiene un PDF agregado después de la base; revisar al integrar, sin merge ciego. |
| `origin/codex/arquitectura-p4` | `DELIVERED_HISTORY_FULLY_CONTAINED` | Ya está contenida en esta rama. |
| `origin/jose-viewer` | `SUPERSEDED` | Funciones útiles ya portadas a Unity actual. |
| `origin/luis-semana3-capacidad-ha` | `SUPERSEDED_PORTED` | Capacidad ya integrada. |
| `origin/luis-gravedad-tributarias` | `PARTIALLY_PORTED_REFERENCE` | Consultar QA útil; geometría/IDs son antiguos. |
| `origin/e2-work` | `SUPERSEDED_GEOMETRY_REFERENCE` | Antecedente de ED2; no fusionar completo. |
| `origin/luis` | `HISTORICAL_SETUP` | Configuración temprana. |

## Duplicados y limpieza segura

El inventario detecta siete grupos de contenido idéntico. Las copias de imágenes
HA, arquitectura y sismo dentro de `StreamingAssets` son intencionales: Unity
las necesita como bundle autocontenido. Los tres `model_viewer` históricos
idénticos y la copia de superposición Semana 3 son redundantes, pero forman
parte de entregas/checkpoints ya versionados.

Resultado R5: **0 archivos eliminados y 0 archivos movidos**. No existe todavía
certeza suficiente para borrar historia sin afectar trazabilidad. Las rutas
ambiguas quedan clasificadas y fuera de la lista canónica.

## Estructura conceptual futura (sin migración masiva)

```text
project/
  sources/          manifiestos de planos; originales fuera de Git
  geometry/         ED1, ED2, combinado y auditorías
  analysis/
    delivered/      snapshots P1L0–P1L3 inmutables
    candidates/     modelos PRE-P1L4 aún no aprobados
  loads/            catálogo, paños y QA de conservación
  unity/            única interfaz y adaptadores JSON
  docs/             índice, handoff, decisiones y defensa
```

Por ahora esta estructura es solo una guía. Mover cientos de archivos rompería
rutas, historia y scripts; cualquier migración futura debe hacerse por
adaptadores y en commits pequeños.

## Próximo trabajo técnico autorizado

1. Revisar las 43 geometrías flotantes agrupadas por causa en EXT-5.
2. Validar las restricciones del adaptador (424 nodos multi-maestro y 376 nodos retenidos/restringidos), sin conectar artificialmente.
3. Terminar perímetros/huecos de losas y cobertura.
4. Validar Q completo.
5. Solo entonces recalcular G/Q, masas, EX/EY, superposición y OpenSees.
