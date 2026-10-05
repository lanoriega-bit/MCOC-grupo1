# Reglas de extraccion de elementos - P1L2

## Alcance

Se modela todo lo que aparece en los planos actuales, incluyendo primera etapa y segunda etapa. La tercera etapa/no construida queda fuera hasta recibir planos nuevos.

## Convenciones

- Todas las cotas entregadas por el usuario se consideran en cm y se convierten a m.
- Los ejes principales se toman desde `grid_axes_draft.json`.
- Los niveles se toman desde `levels_draft.json`.
- La losa no se modela con elementos finitos.
- Las cargas de losa se transfieren a vigas mediante areas tributarias explicitas.

## Identificacion grafica preliminar

| Elemento | Como se reconoce en plano | Modelacion preliminar |
| --- | --- | --- |
| Viga | Rectangulo/trazo azul o morado entre apoyos o sobre ejes | `elasticBeamColumn` 3D |
| Columna/pilar | Cuadrado/rectangulo azul en interseccion o cerca de ejes, con etiqueta `P.` | `elasticBeamColumn` vertical |
| Muro H.A. | Trazo verde/achurado o muro etiquetado `M.H.A. e=...` | Muro equivalente vertical |
| Apoyo | Nodo de base asociado a columna o muro que llega a fundacion | Restriccion basal preliminar |
| Diafragma | Nodos de un mismo piso | `rigidDiaphragm` por nivel |

## Niveles de confianza

| Confianza | Criterio |
| --- | --- |
| Alta | Elemento claro, alineado con ejes conocidos y con seccion legible |
| Media | Elemento claro, pero falta alguna cota interna o detalle de continuidad |
| Baja | Elemento visible pero ambiguo por resolucion del PDF o cruce de informacion |

## Regla de trazabilidad

Cada elemento debe registrar:

```text
id, plano_origen, nivel, tipo, ejes/nodos, seccion, etapa, confianza, comentario
```

Esto permite responder en la demostracion:

- que `elementTag` tiene;
- donde esta en planta;
- que apoyos tiene;
- cual es su eje local;
- que area tributaria carga;
- cuantos kN recibe.
