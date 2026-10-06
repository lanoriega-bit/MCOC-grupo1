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

Checkpoint de migración: los módulos principales están en `analysis/`.
Validar con `python main.py validar`; generar el contrato FE de comprobación con
`python analysis/opensees/build_fe.py`.
Este último no ejecuta OpenSees ni sustituye resultados. Las entradas funcionales
ya están consolidadas en `tools/`; consultar `tools/README.md`.

`reference/connectivity_prior.json` es evidencia de conectividad anterior para
comparación del reconstructor, no una segunda fuente geométrica editable.
