# Modelo estructural — fuentes únicas

Editar deliberadamente estas fuentes; no editar los derivados de Unity o AR.

| Archivo | Contenido |
|---|---|
| `model_master.json` | Geometría física, identidades, historial de fusiones, nodos y topología FE aprobada |
| `sections.json` | Catálogo de secciones y dimensiones |
| `materials.json` | Catálogo de materiales, propiedades y calidad de evidencia |
| `loads.json` | Cargas, catálogo de evidencia, tributarias congeladas y aplicación nodal |

Las losas ya están en `model_master.json`; no se crea `slabs.json` porque duplicaría
la fuente. No participan como elementos FE. Sus superficies tributarias de carga
están en `loads.json`, y no son una segunda geometría física editable.

Unidades: m, N, Pa. Véase [diccionario](DATA_DICTIONARY.md).

Configuración de análisis: `config/analysis_settings.json`. qQ y λQ no son lo mismo.
Los valores no fueron modificados durante el traslado.

Checkpoint de migración: los ejecutables aún conservan ubicaciones semanales.
Validar con `python main.py validar`; generar el contrato FE de comprobación con
`python entregas/P1L5/modelo_central/build_central_derivatives.py`.
Este último no ejecuta OpenSees ni sustituye resultados. Las entradas funcionales
de `tools/` se consolidarán junto con los módulos de análisis.
