# Checkpoint final AR — 2026-10-05

Fecha: 5 de octubre de 2026, America/Santiago.
Proyecto: `C:\MCOC_UNITY_P1L6_AR`.
Escena funcional: `Assets/Scenes/Luis_AR_Test.unity`.

**Este checkpoint es la base validada antes de implementar escalas.**

## Base validada físicamente en Android

Validación confirmada por el propietario del proyecto al cerrar esta jornada:

- Búsqueda por ID, normalización, reemplazo y conservación ante ID inválido.
- BEAM / COLUMN / WALL con geometría y orientación correctas.
- Surface placement y colocación libre nivelada; worldUp correcto.
- Ajustes ±5°, 90°, SUBIR / BAJAR y ACERCAR / ALEJAR.
- Anchors fijos; objetos/overlays fijos relativos al anchor, sin billboard.
- REUBICAR / CANCELAR y cambio entre tipos.
- Información dinámica y diagramas 2D CASE_R CURRENT.
- Overlay 3D BEAM, COLUMN y WALL, seis componentes N/Vy/Vz/T/My/Mz.
- UI compacta y safeArea.

La confirmación Android de esta jornada prevalece sobre notas históricas de los README que indicaban validación física pendiente.

## Datos, IDs y convenciones que deben conservarse

Dataset exclusivo: `Assets/StreamingAssets/p1l6_current_ar_elements.json`.
Caso: **CASE_R CURRENT**, formato `MCOC_P1L6_AR_CURRENT_ELEMENTS_V1`.

IDs prioritarios:
- `E1-P2-V-041`: BEAM.
- `E1-P2-C-001`: COLUMN, sección 0.70 × 0.70 m, altura 3.96 m.
- `E2-P2-M-007`: WALL, largo 2.82 m, altura 3.96 m, espesor 0.25 m.

Geometría visual local: BEAM longitudinal X, COLUMN longitudinal Y, WALL largo X / altura Y / espesor Z. Placement nivelado respecto a worldUp; cámara utilizada para orientación inicial, sin seguimiento posterior. Escala AUTO existente: dimensión mayor aproximada de 0.65 m AR y proporciones conservadas.

Resultados: i = acción_i / 1000; j = −acción_j / 1000. N/Vy/Vz en kN, T/My/Mz en kN·m. Interpolación lineal `(1−t)i + tj`, con cruce por cero; amplitud gráfica máxima 0.20 m AR, normalizada por max(abs(i),abs(j)). Offset gráfico exterior 15 mm AR. No reinterpretar fuerzas ni modificar CASE_R.

Jerarquía fija: ARAnchor → PlacedStructuralElementRoot_ID → StructuralMesh + ResultOverlay3D. Preview conserva el elemento/overlay anteriores; CANCELAR conserva su instancia; FIJAR reemplaza los propios sin huérfanos.

## Archivos runtime relevantes de la base acumulada

La clasificación siguiente documenta las implementaciones de esta jornada; no es un diff Git. Todos están físicamente en disco y sus assets tienen `.meta`.

En `Assets/Scripts/P1L6AR/`:
- Selección/datos/información: `ARDatasetRepository.cs`, `ARStructuralElementController.cs`, `ARStructuralElementSelectionUI.cs`, `ARSelectionTextInput.cs`, `ARSelectedElementInfo.cs`, `StructuralElementARData.cs`.
- Geometría/frame fijo: `StructuralARElementRenderer.cs`, `TrackedModelToARTransformBehaviour.cs`; infraestructura existente `LuisAnchorProviderAdapter.cs`, `ArTransformMath.cs`.
- Placement incorporado y posteriormente ajustado: `ARSurfacePlacementController.cs`, `ARFoundationSurfaceBackend.cs`, `ARSurfacePlacementMath.cs`, `ARPlacementPreview.cs`, `ARSurfacePlacementUI.cs`.
- Diagramas 2D incorporados: `ARCurrentDiagramData.cs`, `ARForceDiagramGraphic.cs`.
- Overlay incorporado: `ARStructuralResultOverlay3D.cs`, `ARForceDiagram3DRenderer.cs`; ambos extendidos en el último cambio para COLUMN/WALL.
- Nuevo en el último cambio: `ARVerticalResultMapping.cs` y `.meta`.

En `Assets/AR/`: `LuisARDiagrams.cs`, `LuisARTrackingUI.cs` integran UI/información/diagramas. `LuisARImageAnchor.cs` se conserva como infraestructura de tracking; no debe modificarse para escalas.
Recurso nuevo del overlay: `Assets/Resources/ARForceOverlay.shader` y `.meta`.

No se edita funcionalidad durante este cierre: ni scripts runtime, escena, tracking, placement, anchors, overlays, UI, geometría, dataset, resultados ni ProjectSettings.

## Auditoría y excepción

- BEAM: 446/446 segmentos con correspondencia válida, idéntica al renderer previamente validado.
- COLUMN: 142/143 segmentos válidos.
- WALL: 84/84 segmentos válidos.
- **`E2-P4-C-008`: solo diagrama 2D**, conservando selección y geometría/placement. Eje FE oblicuo: nodo 182 (27.471, 0.001, 15.84), nodo 196 (27.502, 0.001, 19.80); desplazamiento horizontal 31 mm > tolerancia vertical 2 mm. No fabricar correspondencia 3D.

COLUMN/WALL del dataset actual tienen un único segmento. Anterior/Siguiente conserva el flujo existente; fixtures de prueba verifican fracciones verticales de varios segmentos sin modificar dataset.

## Pruebas automáticas aprobadas y compilación

Unity 6000.6.0f1. Logs persistidos:
- `Tests/AROverlay3D/UnityChecks.log`: BEAM exactamente igual a copia anterior, seis componentes COLUMN/WALL, 1200 updates, libre/pared, traslado/cancelación/cambio de tipo, sin huérfanos, subsegmentos/cruce por cero/rechazo ambiguo y auditoría completa.
- `Tests/ARFreePlacement/UnityChecks.log`: colocación libre, controles, nivelación, tracking recovery, 1200 updates fijos.
- `Tests/ARSurfacePlacement/UnityChecks.log`: placement/UI/cancelación/anchors, 1200 updates fijos.
- `Tests/ARDiagrams/UnityChecks.log`: 669 elementos / 673 segmentos CURRENT, seis componentes y multi-segmentos.

No se repiten suites largas durante este cierre. La compilación ya fue aprobada en las suites; adicionalmente `Logs/Editor.log` registra build Android **Succeeded**, finalizado el 2026-10-05 a las 00:30:31. `Library/ScriptAssemblies/Assembly-CSharp.dll` es posterior a todos los scripts AR actuales.

Verificación final: ningún `.meta` faltante en Assets; ninguna referencia GUID sin resolver en la escena Luis_AR_Test, Assets/AR y Assets/XR. Auditoría general encuentra 333 ocurrencias de referencias sin resolver exclusivamente bajo `Assets/TextMesh Pro/`, incluyendo sus ejemplos y recursos; no afectan a las referencias AR verificadas y se conservan sin reparación/refactor. Detalle: `Tests/FINAL_AR_REFERENCE_AUDIT_2026-10-05.txt`.

## Limitaciones conocidas

- WALL muestra exclusivamente el resultado lineal del segmento equivalente OpenSees; no campo superficial, heatmap, shell ni tensiones inventadas.
- E2-P2-M-007 tiene My/Vy/Vz/T/Mz CURRENT nulos: diagrama plano correcto; N no nulo.
- Convención transversal gráfica local; no reconstrucción de ejes FEM no documentados.
- Normalización gráfica por segmento/componente; comparar magnitudes mediante valores UI, no tamaños de gráficos.
- Planos gráficos reales pueden verse de canto u ocultarse desde la cara opuesta; no billboard.
- Sin deformada ni varios segmentos dibujados simultáneamente.
- El respaldo copia archivos guardados en disco. No existe acceso para certificar buffers no guardados de ventanas/editor externos; los cambios realizados por el agente no dependen de esos buffers.

## Guardado y respaldo local

No es un repositorio Git válido. No se inicializa Git, no hay commit ni push.

Se crea un archivo ZIP local de cierre bajo `Tests/Checkpoints/`, junto a manifiesto SHA256 y comprobación del contenido. Incluye Assets (con .meta, escena y dataset), Packages, ProjectSettings, Tests (checkpoint/logs/capturas), UserSettings, Logs, build, BuildsAndroid y archivos raíz del proyecto. Excluye el propio directorio de respaldo, Library y caches/temporales regenerables. No se sobrescribe ningún archivo existente para crear el ZIP.

No hay respaldo externo/remoto ni protección frente a pérdida del equipo/disco. Los archivos generados de Library no se archivan; los APK actuales sí.

## Próxima tarea — NO implementada hoy

**SISTEMA DE ESCALAS AR: AUTO / 1:10 / 1:5 / 1:2 / 1:1 REAL.**

Continuar desde esta base validada, preservando comportamiento actual, geometría, tracking/anchors y resultados. Inspeccionar y definir el cambio mínimo antes de implementar escalas.
