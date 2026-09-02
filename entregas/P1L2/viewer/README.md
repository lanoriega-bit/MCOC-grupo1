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

## Contenido del modelo

El viewer carga `model_viewer.json` que contiene:

- **1264 solidos**: vigas (prismas), muros (paneles verticales), columnas (agrupadas entre pisos), losas (cajas transparentes), apoyos
- **2460 segmentos CAD**: lineas extraidas de los planos para referencia
- **514 etiquetas**: texto de los planos CAD
- **18 ejes**: ejes verticales del edificio

Los solidos se renderizan como `THREE.Mesh` con material colorido por categoria. Los planos CAD se muestran como lineas finas apagables por defecto.

## Seleccion

Al hacer click sobre un solido se muestra:

- `elementTag`;
- tipo (viga, muro, pilar, losa, etc.);
- piso;
- dimensiones (largo, ancho, alto en metros);
- capa CAD;
- plano fuente;
- confianza de extraccion.

Tambien se dibuja una guia de ejes locales sobre el solido seleccionado:

| Color | Eje |
| --- | --- |
| Rojo | `x local`, desde nodo inicial hacia nodo final |
| Verde | `y local` aproximado |
| Azul | `z local` aproximado |

## Dependencia externa

Este viewer usa Three.js desde CDN (`unpkg.com`). Por eso requiere conexion a internet al abrir el viewer. Si la demo debe funcionar offline, el siguiente paso es guardar Three.js localmente o migrarlo al viewer Unity.
