# Flujo estructurado global P1L2

Este directorio separa la interpretacion de planos del modelo 3D final.

## Flujo

```text
TODOS LOS PLANOS -> INVENTARIO -> EXTRACCION VECTORIAL -> DATOS POR PISO -> SISTEMA GLOBAL -> RELACIONES ENTRE PISOS -> VALIDACION 2D -> CONFLICTOS -> BUILDING_MASTER -> CONTROL DE CALIDAD -> DECISION 3D
```

El Piso 1 se conserva como prototipo del metodo, pero el avance del proyecto se hace ahora a escala edificio. No se debe modificar ni regenerar el modelo 3D hasta que la base logica global este suficientemente completa y coherente.

## Carpetas

| Carpeta | Uso |
| --- | --- |
| `datos/` | Ejes, niveles y elementos estructurados por piso |
| `validacion/` | Plantas 2D y comparaciones entre pisos |
| `modelo/` | Respaldos y futuras salidas 3D generadas desde datos validados |
| `issues/` | Diferencias, conflictos por piso, conflictos globales y elementos `NEEDS_REVIEW` |
| `scripts/` | Extractores verificables reutilizables |

## Regla base

No se debe crear ningun elemento estructural si no existe una fuente. Si una extraccion es incierta, el elemento queda marcado como `NEEDS_REVIEW`.

El archivo `unity_export/model_viewer.json` esta congelado para esta etapa. El respaldo local de referencia se guarda en `modelo/model_viewer_backup_576f014.json` cuando existe el modelo actual.

## Archivos Globales

| Archivo | Uso |
| --- | --- |
| `datos/planos_index.json` | Inventario maestro de planos DXF disponibles |
| `datos/sistema_global.json` | Origen, ejes, niveles y transformaciones entre sectores |
| `datos/relaciones_verticales.json` | Continuidad de columnas y muros entre niveles |
| `datos/building_master.json` | Modelo logico consolidado del edificio |
| `issues/conflicts_global.json` | Conflictos globales con severidad |
| `issues/quality_global.md` | Informe global de calidad y recomendacion para modelado 3D |

## Datos Por Piso

Los pisos extraidos desde los DXF disponibles quedan en:

| Archivo | Nivel |
| --- | --- |
| `datos/fundacion.json` | Fundaciones/base |
| `datos/piso_01.json` | Piso 1 |
| `datos/piso_02.json` | Piso 2 |
| `datos/piso_03.json` | Piso 3 o nivel superior, pendiente de confirmar por rotulo |

## Validaciones 2D

Cada nivel tiene una carpeta propia en `validacion/` con vistas `completo`, `parte_1` y `parte_2` cuando corresponde. Tambien se generan comparaciones en `validacion/comparacion_pisos/`.

Aliases historicos de Piso 1 conservados:

| Archivo | Que muestra |
| --- | --- |
| `validacion/piso_01_completo.svg` | Superposicion completa Parte 1 + Parte 2 |
| `validacion/piso_01_parte_1.svg` | Solo Parte 1 (`2017_67`) contra modelo actual |
| `validacion/piso_01_parte_2.svg` | Solo Parte 2 (`2024_22/LT2`) |
| `validacion/piso_01_completo.png` | Version raster de alta resolucion del completo |
| `validacion/piso_01_parte_1.png` | Version raster de alta resolucion de Parte 1 |
| `validacion/piso_01_parte_2.png` | Version raster de alta resolucion de Parte 2 |

Leyenda visual:

| Color/estilo | Significado |
| --- | --- |
| Gris claro | Plano original vectorial DXF usado como underlay |
| Azul | Vigas detectadas |
| Verde | Muros detectados |
| Naranjo | Columnas detectadas |
| Negro punteado | Elementos que ya existen en el modelo 3D actual |
| Rojo | Elementos faltantes en el modelo actual |
| Magenta | Elementos sobrantes del modelo actual |
| Amarillo | Elementos dudosos o `NEEDS_REVIEW` |

Reportes de investigacion:

| Archivo | Uso |
| --- | --- |
| `datos/piso_01.json` | Datos estructurados completos del Piso 1 |
| `issues/conflicts.json` | Conflictos con ID, fuente, ubicacion aproximada y geometria |
| `issues/quality_piso_01.md` | Resumen humano del control de extraccion |
| `issues/vigas_piso_01_review.json` | Revision especifica de vigas |
| `issues/muros_piso_01_review.json` | Revision especifica de muros |
| `issues/columnas_piso_01_review.json` | Revision especifica de columnas |
| `issues/calce_parte_1_parte_2.json` | Transformacion Parte 1 / Parte 2 y evidencia disponible |

## Ejecucion

```powershell
$env:MCOC_DXF_DIR="C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf"
$env:MCOC_LT2_DXF_DIR="C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf_2024_22"
python entregas\P1L2\edificio\scripts\extract_building.py
```
