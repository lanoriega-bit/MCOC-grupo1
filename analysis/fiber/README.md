# Estudios Fiber independientes

`column/` y `wall/` conservan los algoritmos existentes para sección discretizada,
M-φ y muestreo P-M. Las configuraciones de estudio están en `sections/`, separadas
del catálogo físico `model/sections.json`: son hipótesis de laboratorio, no una
segunda fuente de secciones confirmadas del edificio.

Ejecutar `python analysis/fiber/reproduce_studies.py`. El destino de reproducción
y las llamadas directas de los módulos usan `results/fiber/`.
No confundir salidas de estudios históricos con capacidad
aproximada CURRENT. Los puntos no convergidos se conservan explícitos; no completar
la envolvente por interpolación ni presentarla como verificación normativa.
