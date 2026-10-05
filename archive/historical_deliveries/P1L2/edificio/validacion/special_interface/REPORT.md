# FASE 4 — diagnóstico de sectores especiales e interfaz

Estado: `PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED`

- Calce D/E: `AXIS_CONFIRMED`, residual `0.009 m`.
- Textos generales coincidentes con palabras de búsqueda: `51`; menciones de junta/dilatación: `18`; candidatas localizadas junto a D/E: `1`.
- En S1, cuatro entidades de `RLA-MURO DILATADO` forman un único contorno cerrado de `0.200 x 2.360 m`; el receptor local ED1 queda confirmado.
- Contexto DXF de esa llamada: `entregas/P1L2/edificio/validacion/special_interface/s1_dilatado_source_detail.png`.
- El elemento local no cruza D/E y no demuestra transferencia entre bloques.
- Veredicto de conexión física: `NO_CROSS_BUILDING_FE_CONNECTION_PROVEN`.
- Regla: la proximidad y los contactos geométricos no autorizan vínculos FE entre edificios.
- Elementos ED1 todavía `UNRESOLVED_REQUIRES_REVIEW`: `0`; las columnas H-1/H-2/H-3 y sus apoyos quedaron confirmados por 2017_67-308.
- Miembros individuales cuyo eje geométrico sobrepasa D/E: `5`. Son remates locales de un solo edificio; ninguno enlaza un miembro ED1 con uno ED2.
- Piloto arquitectónico P4: `958.392750 m²`, `participates_in_FE=false`.

| Piso | Contactos geométricos D/E | Elementos fuera de envolvente | Overlay interfaz | Overlay outboard |
| --- | ---: | ---: | --- | --- |
| S1 | 13 | 58 | `entregas/P1L2/edificio/validacion/special_interface/interface_s1.png` | `entregas/P1L2/edificio/validacion/special_interface/outboard_s1.png` |
| P1 | 7 | 32 | `entregas/P1L2/edificio/validacion/special_interface/interface_p1.png` | `entregas/P1L2/edificio/validacion/special_interface/outboard_p1.png` |
| P2 | 10 | 13 | `entregas/P1L2/edificio/validacion/special_interface/interface_p2.png` | `entregas/P1L2/edificio/validacion/special_interface/outboard_p2.png` |
| P3 | 10 | 7 | `entregas/P1L2/edificio/validacion/special_interface/interface_p3.png` | `entregas/P1L2/edificio/validacion/special_interface/outboard_p3.png` |
| P4 | 8 | 6 | `entregas/P1L2/edificio/validacion/special_interface/interface_p4.png` | `entregas/P1L2/edificio/validacion/special_interface/outboard_p4.png` |

Los sectores estructurales especiales quedan sin elementos `UNRESOLVED_REQUIRES_REVIEW`. Los perímetros, aleros y canopias arquitectónicas continúan junto con la reconstrucción de losas; no participan en FE. Para FE, mantener separados ambos edificios mientras no exista un detalle primario que pruebe transferencia. Las fotografías solo se usan como contraste visual.
