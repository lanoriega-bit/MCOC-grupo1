# Checkpoint — resultados por función

Movidos sin regeneración: G/Q/EX/EY, manifiesto, capacidad aproximada, tres
contratos de cargas y estudios Fiber. Los lectores/escritores trasladados usan
las nuevas ubicaciones de `results/`.

QA ejecutado después del traslado:

- Modelo: PASS.
- Pipeline: PASS_WITH_EXPLICIT_NOTES, cero controles fallidos.
- Test aislado de capacidad: PASS; todas las hojas numéricas iguales a CURRENT.
- Fuente única: 4 tests PASS.
- Baseline: 120/120 archivos idénticos byte a byte.

Las rutas antiguas dentro de los JSON guardados son procedencia histórica, no
lecturas productivas alternativas. Mantenerlas en este checkpoint evitó cambiar
hashes o recertificar resultados durante un simple movimiento.

No se ha completado integración AR, traslado/compile/Play Unity, wrappers finales,
clasificación final de duplicados, archivo histórico o prueba desde copia limpia.
`main` sigue intacta. Este es un checkpoint, no la entrega final de arquitectura.
