# Comandos por función

Ejecutar desde la raíz con el Python del entorno del proyecto.

| Comando | Comportamiento |
|---|---|
| `python main.py estado` | Consulta CURRENT, sin regenerar |
| `python main.py unity` | Abre el proyecto configurado |
| `python tools/validate_project.py` | QA modelo/desktop; no ejecuta solver ni AR |
| `python tools/build_model.py` | Plan de validación y derivados de vista previa |
| `python tools/run_analysis.py` | Plan del solver; por sí solo no publica Viewer CURRENT |
| `python tools/generate_unity_data.py` | Plan de exportación desktop desde resultados compatibles |
| `python tools/rebuild_all.py` | Plan completo desktop, sin AR |

Los últimos cuatro solo muestran el plan por defecto. Añadir `--execute` permite
escribir/recalcular en **esa copia**. No usarlos para abrir Unity ni como rutina
de una reorganización. `build_model` no cambia la fuente física ni reconstruye
tributarias; genera derivados de vista previa en `results/validation/model_preview`.
`rebuild_all` usa topología y tributarias canónicas aprobadas, no reconstruye CAD.

Los nombres de formatos JSON históricos se conservan por compatibilidad, no
significan una dependencia productiva de la semana correspondiente.
OpenSees calcula; Unity visualiza; capacidad Fiber es un estudio independiente.
AR está excluido de estos comandos.

## Auditoría estática de organización

Para revisar exclusivamente rutas, referencias, duplicados y fuentes protegidas,
sin abrir Unity/AR ni ejecutar análisis:

```bash
python tools/verify_migration.py --scope desktop
python tools/map_historical_references.py
python tools/audit_repository_layout.py
```

El informe queda en `reports/repository_architecture_audit/STATIC_ORGANIZATION_QA.json`.
Esta auditoría no sustituye pruebas funcionales futuras; no las exige para cerrar
la rama de reorganización.
