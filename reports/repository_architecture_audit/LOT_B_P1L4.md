# Lote B — entrega histórica P1L4

Base: `05e885b`. Alcance exacto: los 51 archivos versionados de `entregas/P1L4/`.
Destino: `archive/historical_deliveries/P1L4/`. No borrado ni cambio de contenido.

## Referencias revisadas antes del traslado

- Búsqueda `entregas/P1L4/` en main, config, analysis, tools, tests y código C#
  productivo: solo README principal, enlace DOCUMENTATION_ONLY.
- Viewer carga contratos usando `Application.streamingAssetsPath`; campos
  históricos de manifiestos son procedencia, no lecturas del filesystem.
- `ViewerDeliveries` muestra model_path/source_path como texto. Sus enlaces Git
  a commits históricos no necesitan que esa carpeta siga en el checkout actual.
- Runners de entregas precedentes son históricos, no llamados por herramientas
  desktop actuales. Para reproducirlos usar el commit/tag original.
- P1L4_FINAL y commit evaluable no se modifican.
- AR no se ejecuta ni modifica en este lote.

## Duplicados

Conservar la entrega oficial completa es una razón histórica concreta. No eliminar
CSV/JSON entregados solo porque StreamingAssets tenga una copia de consumo.

## QA

Validación modelo/pipeline, identidad protegida desktop y pruebas de entradas.
No hay cambios de Assets/escena/C#; no requiere nueva prueba Play por este lote.
Ejecutado: modelo PASS, pipeline PASS_WITH_EXPLICIT_NOTES, 117/117 protegidos
desktop idénticos y 17 pruebas PASS. Búsqueda operativa post-traslado sin resultados.
