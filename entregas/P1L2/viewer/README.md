# Viewer 3D del edificio

## Objetivo

Visualizar el edificio completo como estructura 3D con volumenes reales (vigas, muros, columnas, losas), con navegacion tipo Google Earth y controles de QA para revisar pisos, categorias y elementos individuales.

## Como abrir

Desde la raiz del repositorio:

```powershell
python -m http.server 8000
```

Luego abrir:

```text
http://localhost:8000/entregas/P1L2/viewer/
```

Por defecto carga `model_combined_viewer.json`. Tambien se puede abrir explicitamente:

```text
http://localhost:8000/entregas/P1L2/viewer/?model=model_combined_viewer.json
```

No abrir `index.html` con doble click, porque el navegador puede bloquear la lectura del JSON.

## Controles

| Control | Uso |
| --- | --- |
| Mouse izquierdo | Orbitar el modelo |
| Rueda | Acercar/alejar |
| Mouse derecho | Pan/desplazamiento lateral |
| Lado A/B/C/D | Muestra las cuatro fachadas, manteniendo piso base abajo y piso 4 arriba |
| Vista planta | Mira el edificio desde arriba |
| IDs | Activa/desactiva etiquetas de `elementTag` |
| Modelo | Permite elegir combinado, EDIFICIO_1 candidato, EDIFICIO_2 o GOLDEN de referencia |
| Pisos | Apaga/enciende `S1`, `P1`, `P2`, `P3`, `P4` en los modelos canonicos |
| Solo | Aisla un piso para inspeccion |
| Tipos | Apaga/enciende vigas, muros, pilares, apoyos, ejes, diafragmas y borde de losa |
| Buscar elemento | Busca por `elementTag` completo o parcial |

## Contenido del modelo

El viewer carga por defecto `model_combined_viewer.json`. El archivo `model_viewer.json` sigue siendo el GOLDEN de Luis y solo se abre como referencia comparativa.

El modelo combinado contiene:

- EDIFICIO_1 transformado por `CALCE_A = AXIS_CONFIRMED`.
- EDIFICIO_2 en sistema base A-D.
- Cinco pisos canonicos: `S1`, `P1`, `P2`, `P3`, `P4`.
- Niveles auxiliares como fundacion/radier asociados mediante `level_kind`, no como pisos adicionales.

Los solidos se renderizan como `THREE.Mesh` con material colorido por categoria. Los planos CAD se muestran como lineas finas apagables por defecto.

## Seleccion

Al hacer click sobre un solido se muestra:

- `elementTag`;
- tipo (viga, muro, pilar, losa, etc.);
- piso;
- dimensiones (largo, ancho, alto en metros);
- capa CAD;
- plano fuente;
- edificio;
- piso canonico y piso/nivel fuente cuando existe;
- ejes o ubicacion relativa cuando esta disponible;
- seccion/espesor/material cuando esta disponible;
- confianza de extraccion.

Tambien se dibuja una guia de ejes locales sobre el solido seleccionado:

| Color | Eje |
| --- | --- |
| Rojo | `x local`, desde nodo inicial hacia nodo final |
| Verde | `y local` aproximado |
| Azul | `z local` aproximado |

## Dependencia externa

Este viewer usa Three.js desde CDN (`unpkg.com`). Por eso requiere conexion a internet al abrir el viewer. Si la demo debe funcionar offline, el siguiente paso es guardar Three.js localmente o migrarlo al viewer Unity.
