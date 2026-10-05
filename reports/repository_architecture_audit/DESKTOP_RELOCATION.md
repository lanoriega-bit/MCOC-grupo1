# Checkpoint: traslado desktop (2026-10-05)

Rama: `codex/final-repository-architecture`. No merge a main.

## Traslado

Proyecto único: `viewer/unity/`, antes `entregas/P1L3/José/viewer_unity/`.
Assets, Packages, ProjectSettings, Tests y GUID/.meta trasladados con Git.
La carpeta anterior solo conserva restos locales ignorados; no tiene Assets ni
ProjectSettings y ya no es un proyecto productivo. No se borró historia.

Productores/exportadores leen la ubicación desde `config/project_config.json`.
El lanzador raíz apunta al proyecto nuevo. Unity Hub también registra esa ruta.
El script desktop de reanálisis está en `tools/reanalyse_current.ps1` y no invoca AR.
No se ejecutó ese script durante la migración.

## QA realizado

| Comprobación | Estado | Evidencia |
|---|---|---|
| Modelo | PASS | `python main.py validar`, 0 errores/avisos de geometría |
| Pipeline | PASS_WITH_EXPLICIT_NOTES | `results/validation/CURRENT_PIPELINE_QA.json` |
| Identidad protegida desktop | PASS | 117/117 bytes idénticos; `migration_equivalence_desktop.json` |
| Editor/Main desde carpeta nueva | PASS | Unity Hub abre proyecto `unity`, Main, 6000.6.0f1 |
| Compilación y ciclo Play/Edit | PASS | Menú MCOC → Probar interfaz en Play, 17:00 |
| Selección/casos/deformada/diagramas/R | PASS | `[P1L5 DEMO QA] PASS: selección; casos; deformada; My/Mz/N/Vy/Vz; sliders y R instantánea.` |
| Final de prueba | PASS | `[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.` |
| Copia limpia modelo/pipeline | PASS_WITH_NOTE | `CLEAN_DESKTOP_CHECKPOINT.md`; Play del clon no ejecutado |

Captura de logs local: `viewer/unity/Temp/p1l4-ui-smoke.result.txt` (no versionada).
Sin cambios de modelo, cargas, resultados estructurales, capacidad ni datasets.

## AR: límite explícito

Sin ejecución de pruebas AR, apertura de escenas AR, generación de datasets,
comparación de resultados ni integración de funciones. Solo organización.
Los assets AR ligados al proyecto Unity se conservan con sus GUID y contenido.
No se presenta esta prueba desktop como validación de AR.

## Pendientes de arquitectura

Consolidar entradas tools/tests; actualizar guías antiguas; trasladar auxiliares
productivos restantes y después archivar lo superseded; QA de copia limpia.
La referencia original de Luis no se toca.
