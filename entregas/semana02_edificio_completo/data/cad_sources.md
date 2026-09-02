# Fuentes CAD - Semana 2

## Archivos encontrados

Se encontraron y extrajeron localmente dos paquetes desde `C:\Users\matis\Downloads`:

| Archivo | Uso |
| --- | --- |
| `planos_edificio_ing.rar` | Planos estructurales actuales serie `2017_67` |
| `02_LT2_ESPECIALIDADES-20250117T170037Z-001.zip` | Planos de especialidades y calculo serie `2024_22` |

## Extraccion local

Los DWG se extrajeron en carpetas locales ignoradas por Git:

```text
recursos/planos/cad_original/
recursos/planos/dxf_generated/
```

Estas carpetas se ignoran para evitar subir accidentalmente archivos CAD grandes o propietarios. Si el grupo decide versionarlos, se debe hacer un commit explicito.

## Conversion DWG a DXF

Se uso AutoCAD 2026 Core Console:

```text
C:\Program Files\Autodesk\AutoCAD 2026\accoreconsole.exe
```

Herramienta creada:

```text
tools/convert_dwg_to_dxf.py
```

Planos convertidos inicialmente:

| DWG | DXF generado | Motivo |
| --- | --- | --- |
| `2017_67-100.dwg` | `2017_67-100.dxf` | Fundaciones y apoyos |
| `2017_67-101.dwg` | `2017_67-101.dxf` | Cielo 1S y cielo piso 1 |
| `2017_67-102.dwg` | `2017_67-102.dxf` | Cielo piso 2 y cielo piso 3 |
| `2017_67-103.dwg` | `2017_67-103.dxf` | Cielo piso 4 |
| `2017_67-700.dwg` | `2017_67-700.dxf` | Cargas de diseno |

## Capas estructurales detectadas

En los DXF convertidos aparecen capas separadas que permiten automatizar parte de la lectura:

| Capa | Interpretacion probable |
| --- | --- |
| `RLE-VIGA` | Vigas estructurales |
| `RLE-MURO` | Muros estructurales |
| `RLE-PILAR` | Pilares/columnas |
| `RLE-EJE` | Etiquetas de ejes |
| `RLE-EJES` | Lineas de ejes |
| `RLA-COTAS` | Cotas |
| `RLA-COTAS1` | Cotas secundarias |
| `RLA-LOSAS` | Etiquetas/sectores de losa |
| `HATCH CARGAS` | Zonas y textos de cargas en plano 700 |

## Hallazgo clave

El plano `2017_67-101.dxf` contiene, entre otras, estas capas:

| Capa | Cantidad de entidades |
| --- | ---: |
| `RLE-VIGA` | `197` |
| `RLE-MURO` | `137` |
| `RLE-PILAR` | `94` |
| `RLE-EJE` | `130` |
| `RLE-EJES` | `90` |
| `RLA-COTAS` | `90` |

Esto confirma que desde CAD se puede extraer mucho mas que desde PDF raster.
