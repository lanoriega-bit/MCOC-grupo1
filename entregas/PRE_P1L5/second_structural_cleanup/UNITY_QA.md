# Unity QA — segundo saneamiento

PASS: Unity 6000.6.0f1 compilado y Main ejecutado en Player.

PASS: current model; archived layers blocked; beam/column/wall/slab inspector; summary/results defaults; current identity negative gates; signed basis/NaN tests; building/floor filters; 1366x768 and 1920x1080; non-overlapping panels; local axes; historical opt-in; presentation isolation; fullscreen.

Se verificó identidad de siete archivos entre StreamingAssets y aplicación compilada, fechas posteriores a la compilación y hashes de logs. Se recorrieron las 38 cadenas, filtros y reset. Pruebas a 1366×768 y 1920×1080. Capturas adjuntas.

La primera pasada señaló un ID de fixture inexistente; se sustituyó por E1-P4-C-001, manteniendo la prueba de material desconocido. La revisión visual detectó recorte superior en stacks: se corrigió el encuadre y se añadió una comprobación de proyección vertical. La última pasada es PASS. No se ejecutó OpenSees.
