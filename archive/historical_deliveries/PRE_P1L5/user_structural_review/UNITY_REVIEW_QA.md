# Unity — revisión de alcance y fusiones

PASS: compilación Unity 6000.6.0f1 y ejecución de Main en Player.

PASS: current model; archived layers blocked; beam/column/wall/slab inspector; summary/results defaults; current identity negative gates; signed basis/NaN tests; building/floor filters; 1366x768 and 1920x1080; non-overlapping panels; local axes; historical opt-in; presentation isolation; fullscreen.

Pruebas adicionales: cada exclusión ausente de model.solids; cada fusión tiene exactamente un ID canónico y ningún ID absorbido activo; registro de cambios y pendientes ligados a hash de geometría; número de pendientes leído desde metadata, no 43 fijo. Se comprueba igualdad de los cuatro payloads principales entre fuente y aplicación compilada.

La primera prueba detectó un fixture que seleccionaba el muro excluido E1-P4-M-007. Fue reemplazado por E1-P4-M-003 y la segunda pasada resultó PASS; no se debilitó el test de ejes/material desconocido.

Capturas: `unity_current_1366x768.png`, `unity_current_1920x1080.png`, `unity_state_1920x1080.png`. No constituye validación resistente ni corrida OpenSees.
