# Índice canónico — main CURRENT

Este índice identifica qué usar hoy. Las auditorías anteriores son evidencia
histórica; sus conteos y estados no sustituyen los datos CURRENT.

Reorganización en curso: `codex/final-repository-architecture`. Fuentes activas
en `model/`, análisis en `analysis/`, resultados en `results/`, Viewer en
`viewer/unity/`. [Comandos](tools/README.md) y
[QA de copia limpia](reports/repository_architecture_audit/CLEAN_DESKTOP_CHECKPOINT.md).
El archivo definitivo de auxiliares/entregas sigue pendiente de revisión individual.
AR: solo organización, sin ejecución ni nuevas integraciones.

## Fuentes editables

| Componente | Ruta | Cómo usar |
| --- | --- | --- |
| Geometría, IDs, aliases y topología FE | `model/model_master.json` | Fuente única; cambios trazables por ID |
| Secciones | `model/sections.json` | Propiedades geométricas |
| Materiales | `model/materials.json` | Propiedades elásticas y resistentes separadas |
| Cargas | `model/loads.json` | Catálogo, tributarias y aplicación CURRENT |
| Rutas del menú | `config/project_config.json` | No contiene propiedades estructurales |

Las modificaciones físicas requieren QA y reanálisis antes de presentar resultados como vigentes.
No ejecutar bootstrap ni migraciones antiguas como rutina.

## Código y resultados actuales

| Función | Archivo/carpeta |
| --- | --- |
| Entrada y menú | `main.py`, `Proyecto.bat` |
| Validador canónico | `tests/model/validate_model.py` |
| Reconstrucción topología (solo cambio físico autorizado) | `analysis/geometry/rebuild_topology.py` |
| Derivados geométricos de vista previa | `analysis/opensees/build_fe.py` |
| Refresh Q sobre tributarias congeladas | `analysis/opensees/live_loads.py` |
| OpenSees | `analysis/opensees/run_cases.py` |
| Resultados actuales | `results/` |
| Adaptador de resultados Unity | `analysis/postprocessing/export_unity.py` |
| Capacidad CURRENT | `analysis/capacity/build_capacity.py` |
| QA integrado, hashes, equilibrio y crosswalk | `tests/model/validate_pipeline.py` |
| QA CURRENT de núcleos | `tests/model/validate_wall_cores.py` |

`Validar_Modelo.bat` verifica CURRENT, no el bundle histórico.
`build_and_validate.ps1` es el flujo especializado de modificaciones P1L5;
es un flujo histórico; no usarlo como entrada del pipeline reorganizado.
El flujo desktop vigente es `tools/reanalyse_current.ps1` o el plan
`python tools/rebuild_all.py`; no incluye AR.
No es una comprobación de solo lectura ni el botón para empezar a usar el proyecto.

## Unity único

Proyecto: `viewer/unity/` (configurado en `config/project_config.json`).
Escena de escritorio: `Assets/Main.unity`.
Código: `Assets/Scripts/`; herramientas del editor: `Assets/Editor/`.
Datos generados: `Assets/StreamingAssets/`, nunca editar a mano como fuente.
Contrato vigente: `current_dataset_contract.json`; las versiones/hashes determinan
compatibilidad, no el nombre de rama ni un conteo histórico.

[Guía para abrir y modificar](docs/GUIA_USO_Y_CAMBIOS.md).
[Guía funcional desktop](viewer/README.md).

## Estado y evidencia

La última corrección validó 712 sólidos, 669 miembros físicos estructurales,
677 segmentos FE, 1170 nodos topológicos y 0 componentes sin camino a apoyo.
No confundir 33 apoyos visuales con 44 tags fijos FE.
OpenSees usa 1165 nodos y analiza 673 segmentos; cuatro enlaces redundantes
se omiten del análisis, conservando trazabilidad.

- [Informe primario histórico](archive/historical_deliveries/P1L6/wall_continuity/WALL_CONTINUITY_AFTER.md).
- [QA geométrico y físico CURRENT](results/validation/CURRENT_PIPELINE_QA.md).
- [Prueba real Unity compile/Play reorganizado](reports/repository_architecture_audit/DESKTOP_RELOCATION.md).
- [Estado general histórico](archive/historical_deliveries/P1L6/P1L6_READINESS.md).

Mantener visibles las limitaciones académicas: materiales ED1 P4, espesor de
losas, armaduras/capacidad asumidas, cargas puntuales unresolved y candidatos
de muros fuera del modelo. Conectividad PASS no prueba un diseño real correcto.

## Historia y referencias protegidas

| Archivo/etapa | Clasificación |
| --- | --- |
| `entregas/P1L2/unity_export/model_viewer.json` | LUIS_REFERENCE — no modificar |
| `entregas/P1L2/unity_export/model_1_audited_corrected.json` | Derivado actualizado desde central |
| `entregas/P1L2/unity_export/model_combined_viewer.json` | Derivado actualizado desde central |
| `entregas/P1L3/results/a3a4/`, `a7/` | HISTORICAL — resultados entregados |
| `entregas/P1L3/scripts/build_unity_bundle.py` | Adaptador histórico, no usar para reemplazar CURRENT |
| `entregas/POST_P1L4/`, `entregas/PRE_P1L5/` | Auditorías/checkpoints previos |
| `P1L4_FINAL` | Tag evaluable inmutable |

Commit del tag P1L4: `56e24ac0568b24eba3cf119f2e3cc66fc0af3a35`.
La [auditoría retrospectiva](entregas/PRE_P1L5/DELIVERY_RETROSPECTIVE_AUDIT.md)
explica método válido frente a inputs superados.

`main` reúne el estado compartido actual. Las ramas de Luis/José y las ramas
de auditoría se preservan como procedencia; no se eliminan ni se fusionan a ciegas.
`archive/old_data/REPOSITORY_INVENTORY.json` es un inventario de un checkpoint
anterior, no un selector de fuentes actuales. El mapa vigente se genera con
`tools/map_historical_references.py`; el inventariador antiguo está archivado.
