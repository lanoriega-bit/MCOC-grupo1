# Lote D — P1L6/P1L7 históricos y módulos reemplazados

## Cobertura vigente antes del archivo

- Modelo/floors/IDs y secciones: tests/model/validate_model.py.
- Contratos CURRENT/equilibrio/crosswalk/capacidad: tests/model/validate_pipeline.py.
- Q/OpenSees/R: tests/loads/test_live_loads.py, entrada tests/opensees/run_checks.py.
- Capacidad numérica aislada: tests/capacity/test_migration_capacity.py.
- Núcleos: tests/model/validate_wall_cores.py, 45 muros en 3 núcleos/5 pisos,
  tolerancias originales 2 mm de huella y 1 mm de espesor, PASS.
- Desktop: proyecto único viewer/unity y tests/unity; QA Play ya validado.

Las comparaciones antes/después, auditorías CAD y candidatos históricos son
evidencia única: se conservan íntegros, no se borran ni se presentan como tests
de una versión nueva. Las rutinas aplicadoras de correcciones a IDs específicos
no son pasos del pipeline actual y no se vuelven a ejecutar.

## Referencias

Búsqueda operativa P1L6/P1L7: enlaces de documentación e información de
procedencia. Los consumidores Python/C# del pipeline actual usan model/analysis/
results/config/StreamingAssets. Las guías operativas se actualizan primero.
AR: generador y transformaciones ya están en ar; assets Unity preservados en
viewer/unity. Solo traslado de archivos históricos restantes, sin ejecutar
AR, regenerar datos, abrir escenas ni cambiar código funcional.

## Alcance y destinos

P1L6: TRASLADADO tras aportar AR_PATH_PROOF.md. La primera solicitud fue
rechazada por posibles dependencias; se autorizó el nuevo intento con evidencia
estática adicional. P1L7: PROPUESTO, todavía sin trasladar en este checkpoint.

Cada carpeta es un lote separado y se valida antes de continuar:
`entregas/P1L6` → `archive/historical_deliveries/P1L6`;
`entregas/P1L7` → `archive/historical_deliveries/P1L7`.
No se elimina evidencia única ni tags. QA modelo/pipeline y bytes protegidos
obligatorio después de cada traslado. No cambio de Assets/escena/C#.
