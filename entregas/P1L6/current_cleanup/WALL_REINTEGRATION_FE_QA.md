# Reintegración de muros — prueba FE aislada

Estado: **PROMOTED_GEOMETRY_RESULTS_STALE**. Los 30 muros que pasaron la prueba se incorporaron al `model_master.json` activo, se reconstruyó la topología FE y se publicaron los sólidos derivados para Unity. `loads.json`, resultados OpenSees y capacidad todavía no se han recalculado. El contrato de Unity quedó bloqueado como `STALE_REANALYSIS_REQUIRED`: no debe mostrar esfuerzos antiguos como CURRENT.

## Evidencia y límites

De 92 muros retirados, 30 quedan `CONFIRMED_REINTEGRATE`: par de caras único en nuestro CAD, correspondencia externa cuando hay cobertura y continuidad comprobada en una prueba FE aislada. Otros 50 siguen `REVIEW_REQUIRED` general; cuatro de ED1/P4 carecen de confirmación del alcance de material; cuatro de E2/P4 contradicen la instrucción manual previa de retirar esa zona; cuatro ED1/P2–P3 carecen de camino FE inferior comprobado. Los repositorios externos no son fuente primaria ni fueron modificados.

La prueba reconstruyó la topología FE de forma aislada, sin correr OpenSees ni modificar resultados. **Los 29 juntos no pasan conectividad:** 16 muros aparecen en seis componentes flotantes. No se añadió ningún apoyo ni enlace artificial.

| Componente | Muros | Diagnóstico pendiente |
| --- | --- | --- |
| 1 | E1-P2-M-007, E1-P3-M-007 | Confirmar conexión física inferior/encuentro con vigas |
| 2 | E1-P2-M-008, E1-P3-M-008 | Confirmar conexión física inferior/encuentro con vigas |
| 3 | E2-P1-M-007, E2-P2-M-007, E2-P3-M-007 | Revisar continuidad a S1 y adaptador FE |
| 4 | E2-P1-M-008, E2-P2-M-008, E2-P3-M-008 | Revisar continuidad a S1 y adaptador FE |
| 5 | E2-P1-M-010, E2-P2-M-010, E2-P3-M-010 | Revisar continuidad a S1 y adaptador FE |
| 6 | E2-P1-M-009, E2-P2-M-009, E2-P3-M-009 | Revisar continuidad a S1 y adaptador FE |

Los muros E2-S1-M-007/008/009/010/011 tienen pares de caras CAD únicos, coincidencia con Cáceres y continuidad geométrica exacta con P1. Santiago no ofrece un control S1 equivalente. Al introducirlos en el candidato aislado, las cuatro cadenas flotantes E2/P1–P3 pasan a estar conectadas sin apoyos ficticios. Esta es evidencia de topología, no de capacidad ni de resultados.

## Subconjunto promovido

La prueba final difiere los cuatro ED1/P2–P3 sin soporte inferior e incluye cinco E2/S1 con continuidad primaria. Pasa la validación central con **0 componentes flotantes**: 60 muros totales (30 actuales + 30 candidatos), 1.242 nodos físicos y 0 errores del validador.

Los 30 candidatos constan en `removed_wall_candidates.json` y se enumeran con geometría, sección, material y fuente en el `restoration_manifest.json` que genera la prueba. Los cuatro diferidos son `E1-P2-M-007`, `E1-P2-M-008`, `E1-P3-M-007` y `E1-P3-M-008`.

Las vigas P1 más cercanas a los paños P2 diferidos están a 3,70 m y 2,12 m, respectivamente. No se puede crear una unión por simple proximidad. Requieren corte/detalle o una interpretación verificable de su ruta de cargas.

**PASS de topología no equivale a modelo CURRENT listo.** Ya se bloqueó el contrato de resultados antes de publicar la nueva geometría. Faltan cargas, masa, análisis, capacidades, contratos y QA Play de Unity. El `CURRENT_VERIFIED` previo correspondía a la geometría anterior y no debe reutilizarse.

## Reproducción

Ejecutar `prepare_confirmed_walls.py --output-dir <carpeta temporal>` y luego `validate_wall_candidate.py --candidate-dir <carpeta temporal>` con el Python del entorno `.venv-p1l5` (requiere `shapely`). La promoción se realizó con `promote_validated_walls.py`, que exige QA PASS, cero componentes flotantes y que ningún sólido o sección existente cambie; preserva el archivo original de Luis. `promoted_walls_manifest.json` registra los IDs, geometrías y fuentes del hito. Para regenerar la clasificación CAD/externos, `audit_removed_walls.py` requiere los dos clones como argumentos de solo lectura y un Python con Pillow.
