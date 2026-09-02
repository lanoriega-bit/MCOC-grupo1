# Estado modelo 3D - P1L2

## Alcance

Se esta modelando todo lo que aparece en los planos actuales, incluyendo primera etapa y segunda etapa. La tercera etapa/no construida queda fuera hasta recibir planos nuevos.

## Fuente de geometria

La geometria se esta extrayendo desde CAD, no desde PDF raster.

| Fuente | Estado |
| --- | --- |
| `2017_67-100.dwg` | Convertido a DXF; fundaciones/apoyos por procesar |
| `2017_67-101.dwg` | Convertido a DXF; usado para cielo 1S y cielo piso 1 |
| `2017_67-102.dwg` | Convertido a DXF; usado para cielo piso 2 y cielo piso 3 |
| `2017_67-103.dwg` | Convertido a DXF; usado para cielo piso 4 |
| `2017_67-700.dwg` | Convertido a DXF; usado para cargas preliminares |

Los archivos DWG/DXF quedan ignorados por Git. El repositorio versiona scripts, datos procesados y resultados, no los planos CAD originales.

## Capas usadas

| Capa CAD | Categoria del modelo | Color |
| --- | --- | --- |
| `RLE-VIGA` | `beam` | Azul |
| `RLE-MURO` | `wall` | Verde |
| `RLA-MURO INV DILATADO` | `wall` | Verde |
| `RLE-PILAR` | `column_plan` | Naranjo |
| `RLE-LOSA` | `slab_edge` | Gris |
| `RLE-EJES` | `axis` | Rojo tenue |
| Diafragma por piso | `diaphragm` | Morado punteado |

## Archivos generados

| Archivo | Uso |
| --- | --- |
| `entregas/P1L2/unity_export/model_viewer.json` | Export directo para viewer web/Unity |

## Resumen actual

| Nivel | Segmentos extraidos |
| --- | ---: |
| `base` | `526` |
| `1S` | `348` |
| `1` | `347` |
| `2` | `296` |
| `3` | `284` |
| `4` | `659` |
| **Total** | **2460** |

Etiquetas estructurales extraidas desde texto CAD: `514`.

| Etiqueta | Cantidad aproximada |
| --- | ---: |
| Vigas de hormigon | `297` |
| Columnas/pilares | `105` |
| Muros | `62` |
| Vigas metalicas | `10` |

## Estado de calce

La geometria visual usa coordenadas CAD reales convertidas de cm a m, apiladas por nivel. Esto permite que vigas, muros, pilares, ejes y diafragmas coincidan con la posicion de planta mucho mejor que usando lectura manual desde PDF.

## Siguiente paso tecnico

El siguiente trabajo es transformar la geometria CAD de inspeccion en un modelo estructural OpenSees:

1. Detectar centros de pilares desde `RLE-PILAR` y etiquetas `P.`.
2. Detectar ejes medios de vigas desde `RLE-VIGA` y etiquetas `V.`.
3. Detectar muros equivalentes desde `RLE-MURO` y etiquetas `M.H.A.`.
4. Crear nodos conectados por piso.
5. Agregar columnas/muros verticales entre niveles.
6. Aplicar diafragmas rigidos por nivel.
7. Generar areas tributarias y cargas lineales sobre vigas.
8. Verificar areas, cargas, equilibrio global y compatibilidad del diafragma.
