# Cargas CURRENT tras reintegrar muros

Estado del hito: **LOADS_REBUILT / CURRENT_VERIFIED_WITH_NOTES**. La primera reconstrucción incluyó 30 muros nuevos, pero hizo singular el modelo OpenSees. La revisión vigente difiere seis muros sin camino FE a apoyo e incluye **24 muros reintegrados activos**. Su peso propio alimenta la masa G + 0,5Q; las tributarias superficiales se asignan a vigas físicas activas. El análisis y la capacidad de esta misma geometría ya se recalcularon y el contrato Unity está `CURRENT_VERIFIED`.

| Control | Resultado |
| --- | ---: |
| Elementos estructurales activos | 639 (442 vigas, 143 columnas, 54 muros) |
| Paneles tributarios | 46 |
| G total generado | 80.184.104,226 N |
| G transferido a nodos | 80.184.104,255 N |
| Residual G | +0,029368 N (3,6626×10⁻⁸ %) — PASS |
| Q generado/transferido | 24.636.593,938 N — PASS, residual 0 N |
| Peso propio estructural | 34.988.715,490 N |
| Cargas puntuales sin receptor inequívoco | 6 entradas de catálogo (tres llamadas SC + tres PM.ADIC) |

Comparación orientativa ETABS: LT1 G +0,028 %, Q +15,193 %; LT2 G −4,875 %, Q +1,388 %. No se alteraron intensidades ni resultados para igualar ETABS. La diferencia LT1 Q requiere investigación adicional, especialmente correspondencia de áreas y supuestos de sobrecarga, pero no invalida la conservación numérica de la transferencia aplicada. Persisten los supuestos explícitos de losa de 0,15 m y tributaria por malla de 0,50 m.

`validate_central_model.py` pasó con 54 muros, 1.230 nodos físicos, 647 segmentos FE y cero componentes sin apoyo en el nuevo control DOF. `build_central_derivatives.py` quedó `READY_TO_RUN`. La corrida OpenSees canónica pasó G/Q/EX/EY y sus resultados se exportaron a Unity.
