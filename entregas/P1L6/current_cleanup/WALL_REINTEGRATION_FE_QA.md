# Reintegración de muros — prueba FE aislada

Estado: **CANDIDATE_NOT_PROMOTED**. Ningún muro de esta prueba se agregó aún al `model_master.json` activo; `loads.json`, resultados OpenSees, capacidad y Unity siguen sin cambios. Los archivos grandes del candidato se generaron en una carpeta temporal local y no son fuente canónica.

## Evidencia y límites

De 92 muros retirados, la auditoría CAD de pares de caras y el contraste geométrico con Santiago/Cáceres dejan 29 candidatos `CONFIRMED_REINTEGRATE`. Otros 55 siguen `REVIEW_REQUIRED`; cuatro de ED1/P4 carecen de confirmación del alcance de material; cuatro de E2/P4 contradicen la instrucción manual previa de retirar esa zona. Los repositorios externos no son fuente primaria ni fueron modificados.

La prueba reconstruyó la topología FE de forma aislada, sin correr OpenSees ni modificar resultados. **Los 29 juntos no pasan conectividad:** 16 muros aparecen en seis componentes flotantes. No se añadió ningún apoyo ni enlace artificial.

| Componente | Muros | Diagnóstico pendiente |
| --- | --- | --- |
| 1 | E1-P2-M-007, E1-P3-M-007 | Confirmar conexión física inferior/encuentro con vigas |
| 2 | E1-P2-M-008, E1-P3-M-008 | Confirmar conexión física inferior/encuentro con vigas |
| 3 | E2-P1-M-007, E2-P2-M-007, E2-P3-M-007 | Revisar continuidad a S1 y adaptador FE |
| 4 | E2-P1-M-008, E2-P2-M-008, E2-P3-M-008 | Revisar continuidad a S1 y adaptador FE |
| 5 | E2-P1-M-010, E2-P2-M-010, E2-P3-M-010 | Revisar continuidad a S1 y adaptador FE |
| 6 | E2-P1-M-009, E2-P2-M-009, E2-P3-M-009 | Revisar continuidad a S1 y adaptador FE |

Los muros E2-S1-M-007/008/009/010/011 tienen pares de caras CAD únicos y coincidencia con Cáceres, pero Santiago no ofrece un control S1 equivalente. La posible continuidad vertical es una pista, **no** una justificación para activarlos o apoyar los flotantes automáticamente. Debe cotejarse planta/corte y formulación de conexión.

## Subconjunto técnicamente conectable

Una segunda prueba aislada, excluyendo los 16 miembros flotantes, pasa la validación del modelo central con **0 componentes flotantes**: 43 muros totales (30 actuales + 13 candidatos), 1.208 nodos físicos, 636 segmentos FE y 0 errores del validador.

Los 13 candidatos son:

`E1-S1-M-005`, `E1-S1-M-026`, `E1-S1-M-029`, `E1-S1-M-049`, `E1-P1-M-002`, `E1-P1-M-026`, `E1-P2-M-003`, `E1-P2-M-005`, `E1-P3-M-003`, `E1-P3-M-005`, `E2-P1-M-011`, `E2-P2-M-011`, `E2-P3-M-011`.

**PASS de topología no equivale a modelo CURRENT listo.** Antes de promover el subconjunto hay que decidir cómo manejar los 16 muros físicamente respaldados pero FE-desconectados, y regenerar cargas, masa, análisis, capacidades, contratos y Unity en una misma revisión. El `CURRENT_VERIFIED` vigente corresponde a la geometría anterior y no debe reutilizarse tras cualquier promoción.

## Reproducción

Ejecutar `prepare_confirmed_walls.py --output-dir <carpeta temporal>` y luego `validate_wall_candidate.py --candidate-dir <carpeta temporal>` con el Python del entorno `.venv-p1l5` (requiere `shapely`). La primera prueba termina con error por los seis componentes, de forma esperada; el archivo `candidate_qa.json` lista los IDs flotantes. Para probar el subconjunto, preparar otra carpeta con `--exclude-floating-from <candidate_qa.json>` y validarla de la misma forma. Ambas herramientas escriben solo en la carpeta de candidato indicada.
