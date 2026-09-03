# P1L2 - Edificio completo desde CAD

## Alcance

Esta carpeta contiene la entrega P1L2: el modelo completo del edificio modelado desde CAD.

Se modela todo lo que aparece en los planos actuales, incluyendo primera etapa y segunda etapa. La tercera etapa/no construida queda fuera hasta recibir planos nuevos.

Los planos CAD originales y DXF convertidos no se suben a GitHub. Se trabaja con ellos localmente y se versionan solo scripts, datos procesados e informes.

## Carpetas

| Carpeta | Contenido |
| --- | --- |
| `data/` | Datos trazables: ejes, niveles, reglas de extraccion, cargas preliminares y fuentes CAD |
| `opensees/` | Scripts Python para extraer modelo CAD y correr esqueleto OpenSees |
| `unity_export/` | JSON preparado para viewer Unity/web |
| `viewer/` | Viewer 3D interactivo del edificio |
| `docs/` | Estado tecnico del modelo |
| `edificio/` | Flujo estructurado: datos, validacion 2D, comparacion e issues antes del 3D |

## Archivos principales

| Archivo | Uso |
| --- | --- |
| `data/grid_axes_draft.json` | Ejes X/Y en metros, convertidos desde cotas en cm |
| `data/levels_draft.json` | Niveles Z en metros |
| `data/load_definitions_draft.json` | Cargas gravitacionales preliminares desde plano 700 |
| `data/cad_sources.md` | Registro de DWG encontrados, conversion DXF y capas usadas |
| `opensees/extract_cad_model.py` | Extrae segmentos CAD por capas y genera el modelo 3D del edificio |
| `opensees/building_gravity_skeleton.py` | Modelo OpenSees preliminar de gravedad para QA |
| `unity_export/model_viewer.json` | Export para viewer Unity/web con colores y toggles |
| `viewer/index.html` | Viewer web 3D interactivo tipo orbit/zoom para QA |
| `edificio/datos/piso_01.json` | Extraccion estructurada inicial del Piso 1, separando Parte 1 y Parte 2 |
| `edificio/validacion/piso_01_completo.svg` | Superposicion visual completa para revisar Piso 1 antes del 3D |
| `edificio/validacion/piso_01_parte_1.svg` | Superposicion visual de Parte 1 (`2017_67`) |
| `edificio/validacion/piso_01_parte_2.svg` | Superposicion visual de Parte 2 (`2024_22/LT2`) |
| `edificio/issues/conflicts.json` | Comparacion Piso 1: correctos, faltantes, sobrantes y dudosos |

## Ejes X preliminares

Todas las cotas entregadas por el usuario se interpretan en cm y se convierten a m.

| Eje | X [m] |
| --- | ---: |
| `E_prime` | `-0.250` |
| `E` | `0.000` |
| `Ea` | `3.300` |
| `Eb` | `3.600` |
| `Ec` | `6.400` |
| `Ed` | `6.700` |
| `F` | `10.000` |
| `F_prime` | `10.250` |
| `G` | `20.000` |
| `Ga` | `21.450` |
| `H` | `30.000` |
| `H1` | `33.825` |
| `H_prime` | `34.477` |
| `H2` | `38.825` |
| `I` | `40.000` |
| `IA` | `42.600` |
| `I_prime` | `45.000` |
| `IB` | `45.345` |
| `J` | `50.000` |

## Ejes Y preliminares

| Eje | Y [m] |
| --- | ---: |
| `1` | `0.000` |
| `1_prime` | `0.250` |
| `1b` | `0.550` |
| `2` | `10.000` |
| `2a` | `14.945` |
| `3` | `17.250` |
| `3_prime` | `17.500` |

## Niveles Z preliminares

| Nivel | Z [m] |
| --- | ---: |
| `base` | `0.000` |
| `1S` | `3.960` |
| `1` | `7.920` |
| `2` | `11.880` |
| `3` | `15.840` |
| `4` | `19.800` |

## Colores de categorias

| Categoria | Color |
| --- | --- |
| Vigas `beam` | Azul |
| Muros `wall` | Verde |
| Pilares/columnas en planta `column_plan` | Naranjo |
| Apoyos/fundaciones `support` | Negro |
| Ejes `axis` | Rojo tenue |
| Diafragmas `diaphragm` | Morado punteado |
| Borde de losa `slab_edge` | Gris |

## Resultados actuales

| Resultado | Valor |
| --- | ---: |
| Solidos limpios para viewer | `927` |
| Segmentos CAD extraidos | `2460` |
| Etiquetas estructurales extraidas | `514` |
| Segmentos estructurales usados en esqueleto OpenSees | `985` |
| Nodos OpenSees preliminares | `2266` |
| Elementos OpenSees preliminares | `2650` |
| Diafragmas identificados | `5` |
| Suma cargas Z | `-54322.527 kN` |
| Suma reacciones Z | `54322.527 kN` |
| Error equilibrio Z | `-1.27e-10 kN` |

## Como ejecutar

Primero instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Si los DXF ya existen localmente, indicar su carpeta y generar el modelo CAD 3D:

```powershell
$env:MCOC_DXF_DIR="C:\ruta\local\a\dxf\2017_67"
python entregas/P1L2/opensees/extract_cad_model.py
```

Luego correr el esqueleto OpenSees de gravedad:

```powershell
python entregas/P1L2/opensees/building_gravity_skeleton.py
```

Para abrir el viewer web 3D, levantar un servidor HTTP local desde la raiz del repositorio:

```powershell
python -m http.server 8000
```

Luego abrir en el navegador:

```text
http://localhost:8000/entregas/P1L2/viewer/
```

El viewer permite:

1. Orbitar, acercar, alejar y hacer pan con controles tipo Google Earth.
2. Activar/desactivar pisos: `base`, `1S`, `1`, `2`, `3`, `4`.
3. Activar/desactivar categorias: vigas, muros, pilares, apoyos, ejes, diafragmas y bordes de losa.
4. Aislar un piso con el boton `solo`.
5. Buscar un `elementTag`, por ejemplo `CAD_1_beam_0042`.
6. Hacer click sobre un elemento para ver tipo, piso, capa CAD, plano, longitud, coordenadas y ejes locales del seleccionado.

## Estado del modelo OpenSees

El archivo `building_gravity_skeleton.py` es un modelo preliminar de QA. Ya verifica equilibrio vertical, pero todavia no reemplaza la geometria CAD por centrolineas estructurales definitivas ni aplica cargas mediante areas tributarias explicitas sobre cada viga.

Proximos pasos:

1. Extraer centrolineas de vigas reales desde `RLE-VIGA`.
2. Asociar cada viga a su etiqueta de seccion `V.60/80`, `V.20/80`, etc.
3. Convertir pilares y muros a elementos verticales equivalentes.
4. Aplicar diafragmas rigidos analiticos por piso en la malla centrolineal.
5. Calcular areas tributarias explicitas y descargar `qG` sobre vigas.
6. Exportar el mismo modelo final a Unity para inspeccion.
