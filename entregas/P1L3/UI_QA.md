# QA de interfaz Unity P1L3

Fecha: 2026-09-10. Proyecto: Unity 6000.6.0f1.

## Alcance preservado

No se modificaron geometria estructural, cargas, masas, fuerzas, capacidad,
IDs ni resultados OpenSees. El adaptador `analysis_cases.json` solo incorpora
las coordenadas y desplazamientos nodales ya existentes en `results/a7` para
dibujar deformadas trazables.

## Errores encontrados y correccion

| Hallazgo | Causa | Correccion |
| --- | --- | --- |
| Capas inferiores no aparecian | Lista mas alta que panel rigido | Scroll y accesos rapidos permanentes |
| Masa no obedecia piso | Todos los objetos se registraban como S1 | Registro con piso/edificio real |
| Tributarias puntuales no reflejaban toggle | Se registraban como `tributary` aunque su categoria era distinta | Capas consistentes y toggle conjunto |
| Textos duplicados | Canvas historico + inspector IMGUI | Canvas historico desactivado |
| IDs ilegibles | Hasta 1561 etiquetas simultaneas | Decluttering por celdas de pantalla |
| Cajas sismicas superpuestas | Posicion fija en proyeccion | Colocacion con deteccion de colisiones y respeto de paneles |
| Deformada no trazable | Perfil visual cuadratico fijo | Desplazamientos nodales EX/EY de OpenSees con escala declarada |
| Graficos ilegibles | Tres imagenes pequenas sin zoom | Vista ampliada modal |
| Botones A/B/C/D cortados | Ancho de 44 px | Ancho y tipografia ajustados |
| `slab_edge` no respondia | Se registraba como referencia CAD generica y perdia el piso al reaplicar filtros | Categoria y piso persistentes para cada objeto lineal |
| Diafragmas y contornos vacios | `JsonUtility` no admite listas anidadas de coordenadas | Adaptador `points_flat` sin alterar la fuente geometrica |
| Losa visual confundida con analisis | Caja provisional visible como piso/techo | Arquitectura P4 separada, `participates_in_FE=false`; caja y diafragma OFF por defecto |

## Matriz de controles

El metodo `RunVisibilitySelfCheck` prueba en Play que cada grupo tenga objetos,
que `OFF` los desactive y que `ON` vuelva a activarlos. Incluye:

- vigas, columnas, muros, losas provisionales y apoyos;
- 259 bordes DXF, diafragmas analiticos, losa arquitectonica P4 y su borde;
- areas tributarias;
- flechas, CM, masa, corte basal y torsion;
- deformadas OpenSees EX y EY;
- pisos S1, P1, P2, P3 y P4.

Ademas deben revisarse manualmente busqueda, seleccion, copiar ID, vistas,
pestanas P1L3, ampliacion/cierre de graficos, `H` y `R`.

## Verificaciones ejecutadas

- Compilacion de `Assembly-CSharp`: PASS, sin errores C#.
- Compilacion de `Assembly-CSharp-Editor`: PASS, sin errores C#.
- Contrato Unity: cinco casos y 813 nodos por caso: PASS.
- Hash de referencia original de Luis:
  `0193A4F37D77519FD10F86BADE537ACCDEE823DA8B261C8CECD008B44837FE5D`.
- Contrato arquitectonico: 1 objeto EDIFICIO_1/P4, 0.15 m, 958.392618 m2,
  `participates_in_FE=false`: PASS.
- No interferencia: fuentes estructurales/resultados sin cambios y referencia
  original de Luis con hash intacto: PASS.
- Prueba automatica Play real: `[UI QA] PASS: capas y pisos responden a ON/OFF.`
- Unity emitio una excepcion interna de `UnityEditor.Search.SearchDatabase`
  durante el indexado de la copia temporal; no proviene del proyecto ni afecta
  el arranque, la carga JSON o la prueba de visibilidad.
