# Cargas CURRENT tras reintegrar muros

Estado del hito: **LOADS_REBUILT / RESULTS_STALE**. Los 30 muros nuevos participan en el peso propio que alimentará la futura masa G + 0,5Q; las tributarias superficiales se asignan a vigas físicas activas. El contrato de Unity continúa `STALE_REANALYSIS_REQUIRED` hasta ejecutar y verificar OpenSees y capacidades de la misma geometría.

| Control | Resultado |
| --- | ---: |
| Elementos estructurales activos | 645 (442 vigas, 143 columnas, 60 muros) |
| Paneles tributarios | 46 |
| G total generado | 80.399.489,148 N |
| G transferido a nodos | 80.399.489,180 N |
| Residual G | +0,032316 N (4,0194×10⁻⁸ %) — PASS |
| Q generado/transferido | 24.636.593,938 N — PASS, residual 0 N |
| Peso propio estructural | 35.204.100,412 N |
| Cargas puntuales sin receptor inequívoco | 6 entradas de catálogo (tres llamadas SC + tres PM.ADIC) |

Comparación orientativa ETABS: LT1 G +0,485 %, Q +15,193 %; LT2 G −4,875 %, Q +1,388 %. No se alteraron intensidades ni resultados para igualar ETABS. La diferencia LT1 Q requiere investigación adicional, especialmente correspondencia de áreas y supuestos de sobrecarga, pero no invalida la conservación numérica de la transferencia aplicada. Persisten los supuestos explícitos de losa de 0,15 m y tributaria por malla de 0,50 m.

`validate_central_model.py` pasó con 60 muros, 1.242 nodos físicos, 653 segmentos FE y cero componentes flotantes. `build_central_derivatives.py` quedó `READY_TO_RUN`; OpenSees aún no se ejecutó en este checkpoint.
