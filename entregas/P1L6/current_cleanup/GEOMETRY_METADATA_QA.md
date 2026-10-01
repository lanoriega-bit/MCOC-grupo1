# Fase B — metadatos geométricos CURRENT

Las coordenadas, nodos y secciones de `model_master.json` **no cambiaron**. El generador deriva ahora la longitud real, dirección unitaria y orientación XY de cada elemento lineal a partir de `start_m`/`end_m`; falla ante un largo no positivo o no finito. Para muros, se comprobó además que el largo geométrico difiere menos de 0,02 m del largo de la sección equivalente.

| Contrato | Elementos lineales actualizados | Alcance |
| --- | ---: | --- |
| Unity `model_viewer.json` | 478 | 442 vigas, 30 muros y 6 apoyos lineales |
| `model_combined_viewer.json` | 478 | derivado combinado, no referencia original de Luis |
| `model_1_audited_corrected.json` | 215 | derivado EDIFICIO_1 |

Los 472 miembros estructurales lineales tienen ahora `length_m > 0`, `direction_unit` y `orientation_deg_xy` en el contrato visible. La fuente canónica conserva los extremos; la longitud es un **derivado exacto**, no una cota nueva inferida del plano. La geometría física y la topología FE siguen idénticas, por lo que no se invalidan los resultados actuales. Se actualizó únicamente el hash del stream geométrico en `current_dataset_contract.json`; el estado sigue `CURRENT_VERIFIED`.

Secciones vigentes: 442/442 vigas con dimensiones asociadas a plano/contorno, 143/143 columnas con dimensiones de geometría CAD (2 con etiqueta revisada), 30/30 muros con sección equivalente derivada del contorno; ninguna dimensión estructural activa es cero. Los 10 espesores de losa son los aprobados para la línea base y las losas siguen fuera del FE. Los materiales de vigas/columnas/muros están asignados 615/615, **pero 79 miembros EDIFICIO_1/P4 requieren revisar alcance**: usan el material vinculado a la nota 2024_22 de EDIFICIO_2, que no es evidencia primaria para EDIFICIO_1/P4. `E=28 GPa`, `ν=0,2` y densidad `2500 kg/m³` son supuestos académicos autorizados, no valores confirmados en plano.

**Pendiente real:** las 10 losas conservan `MAT_UNKNOWN` porque las notas de material confirmadas para G35 excluyen expresamente losas/radier. No se les asignó G35 por analogía. Se buscará la especificación en los originales antes de decidir un material de losa; de no existir, quedará `REVIEW_REQUIRED` con el peso propio asumido claramente separado de la resistencia del material.

QA: `validate_central_model.py` PASS; `build_central_derivatives.py` READY_TO_RUN; `validate_current_loads_and_results.py` PASS_WITH_EXPLICIT_UNRESOLVED, incluyendo hashes Unity, equilibrio G/Q, casos G/Q/EX/EY y superposición. Ese último validador reescribe instantáneas P1L5 históricas; dichas instantáneas no se incluyen en este hito. El smoke de Unity había pasado en el checkpoint `7f216bb`; se intentó repetir tras este cambio de datos, pero el editor se detuvo antes de compilar por `Licensing initialization failed`/desconexión del Licensing Client. Por lo tanto **Unity compile/Play de este checkpoint no está verificado**; no se modificó C#.
