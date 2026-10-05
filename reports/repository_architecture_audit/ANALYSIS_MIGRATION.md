# Checkpoint — traslado de implementaciones

Sin reescribir física: OpenSees en `analysis/opensees/`, capacidad aproximada en
`analysis/capacity/`, exportación en `analysis/postprocessing/` y estudios Fiber
en `analysis/fiber/`. Validaciones de modelo y conectividad en `tests/model/`;
prueba de Q/superposición en `tests/loads/`.

## Evidencia ejecutada

- Validación modelo: PASS, sin errores ni avisos.
- Pipeline CURRENT: PASS_WITH_EXPLICIT_NOTES, cero controles fallidos.
- Menú: 10 tests PASS. Fuente única/migración: 4 tests PASS.
- OpenSees en memoria: qQ 0 / 0,667 / 1,334 / 0,667; conservación y linealidad PASS.
- Combinación explícita `[0,0,0,0]`: diferencia cero.
- Combinación explícita `[1,1,1,1]`: error global relativo 1,32225e-14.
- Combinación explícita `[0,83,1,17,-0,21,0,13]`: error relativo 1,42735e-14.
- Preview FE generado: READY_TO_RUN; no sustituye un resultado analizado.
- Baseline protegido: 120/120 archivos idénticos byte a byte.
- Capacidad regenerada en carpeta temporal: igualdad exacta de cada hoja numérica,
  incluidos valores de demanda/capacidad; 669 registros y 33 firmas.
- Fiber ejecutado en carpeta temporal, cuatro CSV con igualdad exacta respecto
  de `entregas/P1L7/fiber_studies/`: M-φ columna, compresión axial columna,
  P-M columna y P-M muro.

Fiber conserva limitaciones históricas: P50 parcial, 8/14 puntos de muro válidos.
Los avisos de no convergencia observados corresponden a esos estudios, no se
ocultan ni se corrigen como parte de una migración semánticamente neutra.

## Pendiente

Los resultados guardados y algunos exportadores auxiliares todavía conservan
rutas anteriores. Su traslado es una fase separada. AR final aún no integrado;
Unity aún no trasladado. No se ejecutó aquí QA de copia limpia ni compile/Play.
Este informe no declara completada la reestructuración.
