# Índice maestro del proyecto

Estado: `POST-P1L3 / PRE-P1L4`  
Rama de trabajo: `codex/pre-p1l4-consolidation`  
Snapshot entregado: tag `P1L3_DELIVERED` (`c847c13`)  
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

La interfaz mantiene dos líneas temporales visibles y separadas:

| Capa | Estado | Interpretación |
| --- | --- | --- |
| Geometría | `POST_P1L3_CURRENT` | 1212 sólidos consolidados: ED1 524, ED2 688. |
| Diagnóstico FE | `POST_P1L3_CANDIDATE_NOT_RUN` | 1167 miembros candidatos; sirve para revisar topología, no son resultados. |
| G/Q/EX/EY/R | `P1L3_DELIVERED_HISTORICAL` | Resultados entregados preservados; no corresponden todavía a un recálculo de la geometría actual. |
| Cargas y masas mostradas | `P1L3_DELIVERED_HISTORICAL` | Demostración histórica; el catálogo 700 nuevo aún no se aplicó. |
| Capacidad HA | `P1L3_DELIVERED_HISTORICAL` | Demostración de laboratorio preservada. |

El diagnóstico FE conserva el foco heredado de 72 elementos: 31
`CONNECTED_EXPECTED`, 1 `FREE_END_EXPECTED`, 31 `DISCONNECTED_ERROR` y 9
`UNRESOLVED`. Los 40 pendientes no fueron resueltos desde código.

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
| `origin/codex/pre-p1l4-consolidation` | `CURRENT` | Desarrollo vigente. |
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

1. Revisar visualmente en Unity los 31 `DISCONNECTED_ERROR` y 9 `UNRESOLVED`.
2. Volver a planos para resolver únicamente conexiones respaldadas.
3. Terminar perímetros/huecos de losas y cobertura.
4. Validar Q completo.
5. Solo entonces recalcular G/Q, masas, EX/EY, superposición y OpenSees.
