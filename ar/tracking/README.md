# Tracking y colocación

Runtime Unity integrado desde `origin/p1l7/ar-final-search` (commit `862da8c`):
`Assets/Scripts/P1L6AR/` y `Assets/AR/` del Viewer configurado.

Incluye colocación libre/superficie, anchors, worldUp, rotación y desplazamiento,
reubicación/cancelación, selección por ID, escalas AUTO/1:10/1:5/1:2/1:1 e información
métrica. Diagramas 2D/overlays 3D consumen fuerzas CURRENT, no otro modelo.

Los archivos runtime deben permanecer bajo `Assets/` para ser importados por Unity;
no se duplican aquí. Los namespaces y nombres de contrato históricos se conservan
para no romper referencias serializadas. El traslado del proyecto a `viewer/unity/`
espera la validación del Editor.
