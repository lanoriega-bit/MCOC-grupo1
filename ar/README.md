# Realidad aumentada

Generación en `data/`, matemática/consultas en `transforms/`, validación en `tests/`
y guía de runtime en `tracking/`. El dataset vigente coincide con
`origin/p1l7/ar-final-search`: sus funciones de colocación, escalas, selección y
diagramas se integraron junto con su escena y pruebas, sin sustituir datos.

Consume modelo/resultados mediante derivados; el móvil no ejecuta OpenSees.
La generación escribe un único dataset en StreamingAssets del Viewer configurado.
La copia predecesora queda fuera del pipeline activo, pendiente de limpieza.
Runtime y suites compilan offline con referencias cacheadas; Editor compile/Play
está pendiente por licencia. No declarar integración funcional completa antes de
validar la escena en el Editor y cerrar el checkpoint.
