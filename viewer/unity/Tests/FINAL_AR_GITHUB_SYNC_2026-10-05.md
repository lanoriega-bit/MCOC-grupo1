# Sincronización de base AR final — 2026-10-05

El usuario confirmó la aplicación terminada y validada físicamente en Android, incluyendo placement libre/superficie, BEAM/COLUMN/WALL, worldUp, anchors fijos, REUBICAR/CANCELAR, información, diagramas 2D, overlays 3D, cinco escalas y la nueva paleta.

Fuente: C:\MCOC_UNITY_P1L6_AR. Destino canónico: entregas/P1L3/José/viewer_unity. Rama: p1l7/ar-final-search.

Los checkpoints anteriores se conservan como registros históricos; sus menciones de validación física pendiente quedan superadas por esta confirmación del usuario. El APK final validado físicamente es AR_Final_Colors_2026-10-05.apk, SHA256 C094CEE4912809F0444F3E2B45E15BAA8DBA8816F2540A4AE2176AAAEB4A6091.

Se sincronizan exclusivamente scripts AR finales y sus .meta, shader Unlit/double-sided, documentación y herramientas pequeñas de prueba. El dataset CURRENT existente en WSL ya coincidía byte por byte con Windows y se conservó sin volver a copiarlo; sus cambios previos respecto a HEAD se incluyen porque corresponden exactamente a la fuente final.

## Excepción justificada: escena funcional

La escena Windows agrega en XR Origin los cinco componentes ARDatasetRepository, StructuralARElementRenderer, ARStructuralElementController, LuisAnchorProviderAdapter y TrackedModelToARTransformBehaviour y sus referencias. La escena anterior en el repo carecía de esta conexión y aún asignaba el cubo de prueba. Se copia la escena final ya validada, conservando su .meta idéntico. No se añade comportamiento nuevo durante la sincronización.

Packages, ProjectSettings y ReferenceLibrary coinciden por SHA256 con Windows y no se copian. Tampoco se alteran otras escenas, datos de otros integrantes ni la referencia original de Luis en P1L2.

La comprobación de transferencia usa SHA256 por archivo, referencias GUID y auditoría selectiva del diff. No se recompila. Las últimas suites ARDiagrams, AROverlay3D y ARScale y el build/firma Android estaban aprobados antes de esta sincronización.

APK, ZIP, capturas masivas, logs y cachés permanecen locales; la carpeta Unity incorpora reglas mínimas para APK/ZIP, BuildsAndroid, Tests/Checkpoints y copias temporales de pruebas. Los README/checkpoints Markdown y tests pequeños sí se versionan.

No se agrega funcionalidad ni se modifica lógica estructural. No se toca main/master ni se crea PR, tag o release.
