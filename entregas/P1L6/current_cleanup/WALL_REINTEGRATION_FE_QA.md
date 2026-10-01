# Reintegración de muros — prueba FE aislada

Estado: **24 ACTIVE / 6 DEFERRED / RESULTS STALE**. Una primera promoción de 30 muros pasó el control geométrico pero hizo singular a OpenSees. El control nuevo de camino FE hasta apoyos detectó seis muros ED1 en cuatro grupos aislados. Esos seis se retiraron del modelo activo y quedaron documentados como `FE_SUPPORT_PATH_UNRESOLVED`; los 24 restantes están en `model_master.json` y en los derivados para Unity. El contrato sigue `STALE_REANALYSIS_REQUIRED` hasta publicar análisis y capacidad de esta revisión.

## Evidencia y límites

De 92 muros retirados, **24 ya están restituidos en CURRENT**. Otros 50 siguen `REVIEW_REQUIRED` general; cuatro de ED1/P4 carecen de confirmación del alcance de material; cuatro de E2/P4 contradicen la instrucción manual previa de retirar esa zona; diez de ED1/P1–P3 carecen de camino FE hasta apoyo. El primer filtro geométrico propuso 30, pero el control OpenSees posterior difirió seis. Los repositorios externos no son fuente primaria ni fueron modificados.

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

## Subconjunto promovido y corrección posterior

La prueba geométrica inicial difería cuatro ED1/P2–P3 e incluía cinco E2/S1. El nuevo control de nodos/DOF detectó además `E1-P1-M-002`, `E1-P1-M-026`, `E1-P2-M-003`, `E1-P2-M-005`, `E1-P3-M-003` y `E1-P3-M-005` sin ruta FE a apoyo. El subconjunto final tiene **54 muros activos** (30 anteriores + 24 reintegrados), 1.230 nodos físicos, 647 segmentos FE, cero componentes sin apoyo y cero errores del validador central.

Los 30 candidatos iniciales constan en `removed_wall_candidates.json` y en `promoted_walls_manifest.json`. Este último distingue los seis diferidos posteriores y el conteo activo 24. Los cuatro diferidos desde la primera prueba son `E1-P2-M-007`, `E1-P2-M-008`, `E1-P3-M-007` y `E1-P3-M-008`.

Las vigas P1 más cercanas a los paños P2 diferidos están a 3,70 m y 2,12 m, respectivamente. No se puede crear una unión por simple proximidad. Requieren corte/detalle o una interpretación verificable de su ruta de cargas.

La prueba aislada de este subconjunto recalculó cargas y ejecutó OpenSees G/Q/EX/EY con estado **PASS** y equilibrio relativo mejor que 6,3×10⁻¹⁴. El modelo activo ya recibió esta geometría y estas cargas, pero los resultados live aún no se han publicado; siguen bloqueados. Faltan capacidades, contratos y QA Play de Unity. El `CURRENT_VERIFIED` previo correspondía a la geometría anterior y no debe reutilizarse.

## Reproducción

Ejecutar `prepare_confirmed_walls.py --output-dir <carpeta temporal>` y luego `validate_wall_candidate.py --candidate-dir <carpeta temporal>` con el Python `.venv-p1l5`. El control actual incluye componentes FE sin ruta a apoyo. `prepare_supported_wall_subset.py`, `validate_supported_wall_pipeline.py` y `promote_supported_wall_subset.py` documentan la corrección posterior. El archivo original de Luis permaneció intacto. Para regenerar la clasificación CAD/externos, `audit_removed_walls.py` requiere los dos clones como argumentos de solo lectura y un Python con Pillow.
