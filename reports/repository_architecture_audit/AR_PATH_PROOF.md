# P1L6 — revisión estática de consumidores, sin ejecutar AR

La solicitud inicial de trasladar P1L6 fue rechazada por posibles referencias
activas. Este documento aporta evidencia adicional; no supone autorización
automática ni certifica funcionalidad AR.

| Referencia | Consumidor efectivo | Clase / decisión |
|---|---|---|
| ar/data/build_dataset.py: sources.geometry con ruta P1L5 | Se serializa como procedencia; CENTRAL=ROOT/model, STREAM se obtiene de config | HISTORICAL_ONLY; conservar código intacto |
| ar/data/geometry_overlay.json: source.dataset / central_model | element_query.py y tests leen ar/data/geometry_overlay.json, no abren source.dataset | HISTORICAL_ONLY; conservar JSON intacto |
| ar/transforms/ar_math.py: AR_TRANSFORM_CONTRACT.md | Docstring, no lectura de archivo | DOCUMENTATION_ONLY |
| ArTransformMath.cs: entregas/P1L6/transform/ar_math.py | Comentario XML, sin acceso al filesystem | DOCUMENTATION_ONLY |
| tests/ar/test_unity_ar_references.py: ruta Unity anterior | Suite AR congelada; no es llamada por validate_project, main o comandos desktop | HISTORICAL_ONLY para el pipeline desktop; no ejecutar ni alterar |
| model/model_master.json: axis_registration_evidence y source_audit | Procedencia de auditorías; ningún lector Python/C# usa esas claves como ruta | HISTORICAL_ONLY; preservar bytes y evidencia histórica |

Búsquedas realizadas: entregas/P1L6 y P1L7 en main, analysis, tools, config,
tests, ar, scripts C# y documentación; búsquedas de axis_registration_evidence,
source_audit, source.dataset, central_model y geometry_overlay en los lectores.
Los lectores efectivos usan model/, ar/data/, config y StreamingAssets configurado.

P1L6 conserva informes, correcciones aplicadas y evidencias antes/después, no
módulos productivos pendientes de migración. El QA vigente de sus núcleos se
ha reimplementado en tests/model/validate_wall_cores.py (45 muros, PASS), sin
ejecutar rutinas antiguas que alterarían CURRENT.

No se ejecutó prueba AR, generador AR, escena AR ni comparación de resultados AR.
Un traslado conservaría todos los archivos sin editar su contenido; las rutas
congeladas de procedencia pueden resolverse consultando el mapa de traslados o
el commit histórico, nunca reescribiendo datasets protegidos.
