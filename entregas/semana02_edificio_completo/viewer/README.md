# Viewer web 3D preliminar

## Objetivo

Visualizar el modelo 3D preliminar del edificio desde el navegador, con navegacion tipo orbita y controles de QA para revisar pisos, categorias y elementos individuales.

## Como abrir

Desde la raiz del repositorio:

```powershell
python -m http.server 8000
```

Luego abrir:

```text
http://localhost:8000/entregas/semana02_edificio_completo/viewer/
```

No abrir `index.html` con doble click, porque el navegador puede bloquear la lectura de `model_viewer.json`.

## Controles

| Control | Uso |
| --- | --- |
| Mouse izquierdo | Orbitar el modelo |
| Rueda | Acercar/alejar |
| Mouse derecho | Pan/desplazamiento lateral |
| Vista inicial | Vuelve a una vista isometrica general |
| Vista planta | Mira el edificio desde arriba |
| Centrar | Ajusta el modelo completo a la camara |
| IDs | Activa/desactiva etiquetas de `elementTag` |
| Pisos | Apaga/enciende `base`, `1S`, `1`, `2`, `3`, `4` |
| Solo | Aisla un piso para inspeccion |
| Tipos | Apaga/enciende vigas, muros, pilares, apoyos, ejes, diafragmas y borde de losa |
| Buscar elemento | Busca por `elementTag` completo o parcial |

## Seleccion

Al hacer click sobre un segmento se muestra:

- `elementTag`;
- tipo;
- piso;
- capa CAD;
- plano fuente;
- longitud;
- coordenadas inicial/final;
- confianza de extraccion.

Tambien se dibuja una guia de ejes locales sobre el elemento seleccionado:

| Color | Eje |
| --- | --- |
| Rojo | `x local`, desde nodo inicial hacia nodo final |
| Verde | `y local` aproximado |
| Azul | `z local` aproximado |

## Dependencia externa

Este intento preliminar usa Three.js desde CDN (`unpkg.com`). Por eso requiere conexion a internet al abrir el viewer. Si la demo debe funcionar offline, el siguiente paso es guardar Three.js localmente o migrarlo al viewer Unity.
