# Indice preliminar de planos

Este indice organiza los planos originales subidos al repositorio para usarlos durante el semestre.

## Advertencia de lectura

Los PDFs disponibles se leen principalmente como imagen. El OCR recupera algunos textos, pero no todas las cotas ni etiquetas con precision suficiente para automatizar el modelo completo.

Por eso, cualquier dimension, seccion o carga extraida desde estos planos debe verificarse manualmente antes de usarla como dato definitivo del modelo OpenSees.

## Carpeta oficial de PDFs

```text
planos_pdf/
```

La carpeta fue creada por el grupo y se mantiene como ubicacion comun de los planos originales. La carpeta `planos/notas/` se usa solo para indices y observaciones.

## Inventario

| Archivo | Lectura preliminar | Uso probable |
| --- | --- | --- |
| `2017_67-000-Model.pdf` | Lamina general con simbologias, nomenclatura, consideraciones generales, detalles tipicos e indice de laminas. | Punto de partida para entender convenciones, simbolos, nombres de elementos y criterios graficos. |
| `2017_67-001-Model.pdf` | Detalles tipicos de armado de muros con confinamiento. | Criterios de interpretacion de muros; no es prioritario para el benchmark elastico global. |
| `2017_67-002-Model.pdf` | Detalles de muros de contencion, encuentro losa-rampa, ganchos, drenajes y muros no estructurales. | Detalles constructivos; util mas adelante para distinguir elementos estructurales y no estructurales. |
| `2017_67-100-Model.pdf` | Planta de fundaciones. Se observan vigas de fundacion, muros, pilares y dimensiones generales en planta. | Apoyos, ubicacion de elementos verticales y geometria base del modelo. |
| `2017_67-101-Model.pdf` | Planta cielo 1° subterraneo y planta cielo piso 1°. Se leen vigas, muros, pilares y reticula de ejes. | Muy util para definir una planta estructural inicial y conectividad del benchmark 3D. |
| `2017_67-102-Model.pdf` | Planta cielo piso 2° y planta cielo piso 3°. Se observan grillas, vigas, muros/pilares y tablas de contraflechas. | Geometria repetitiva de pisos superiores; buena base para modelo 3D parcial. |
| `2017_67-103-Model.pdf` | Plano de planta adicional de pisos superiores, con vigas, muros y pasadas. | Complemento para continuidad de elementos y detalles de vanos/pasadas. |
| `2017_67-200-I-Model.pdf` | Armadura inferior de losa en una planta. | Referencia de losa y aberturas; no modelar como FE en el proyecto base. |
| `2017_67-200-S-Model.pdf` | Armadura superior de losa en una planta. | Referencia de losa, continuidad y apoyos; util para entender areas tributarias. |
| `2017_67-201-Model.pdf` | Armadura de losa de otro nivel o sector. | Apoyo para reconocer losas, aberturas y zonas de transferencia de carga. |
| `2017_67-202-I-Model.pdf` | Armadura inferior de losa de nivel superior. | Referencia de losa para carga tributaria y aberturas. |
| `2017_67-202-S-Model.pdf` | Armadura superior de losa de nivel superior. | Referencia de continuidad sobre vigas/muros. |
| `2017_67-203-Model.pdf` | Plano de armadura o detalle de losa. | Uso secundario para geometria de losa. |
| `2017_67-204-Model.pdf` | Plano de armadura o detalle de losa. | Uso secundario para geometria de losa. |
| `2017_67-205-Model.pdf` | Armadura malla inferior y superior de losa cielo 4° piso. Incluye ejes, aberturas/shafts y distribucion de losa. | Geometria de planta del nivel 4, aberturas y referencia para areas tributarias. |
| `2017_67-300-Model.pdf` | Elevacion eje 1-1'. Se observan niveles 1°S, 1°, 2°, 3° y 4°, ejes E' a J, muros/columnas, vigas y fundaciones. | Alturas de piso, continuidad vertical de elementos y seleccion de un marco longitudinal. |
| `2017_67-301-Model.pdf` | Conjunto de elevaciones parciales en ejes 1C, 1A, 1b, 1AA y 1BB. Aparecen etiquetas como `V.F. 15/225`, `V. 15/125`, `V. 15/VAR`, `V. 20/80`. | Detalles de vigas y muros en zonas locales; apoyo para definir secciones preliminares. |
| `2017_67-302-Model.pdf` | Elevacion eje 2. Muestra marco de varios pisos entre ejes E/F/G/H y continuidad de vigas y elementos verticales. | Candidato fuerte para benchmark 3D parcial junto con una franja de planta. |
| `2017_67-303-Model.pdf` | Elevacion eje 3-3'. Muestra pisos 1° a 4°, ejes E' a J, vigas, muros/columnas y detalles de cortes. | Candidato para comparar continuidad vertical y elegir un marco paralelo al eje 2. |
| `2017_67-304-Model.pdf` | Elevaciones de ejes 2a, Ea, Ec/Ed y eje 8. Se observan muros angostos, niveles y vigas profundas como `V.F. 20/220` y `V. 20/130`. | Identificar zonas de muros y elementos verticales equivalentes. |
| `2017_67-305-Model.pdf` | Elevacion eje E-E', elevacion eje Ga y elevacion eje H'. Incluye cortes de elementos y una prolongacion hacia eje 8. | Candidata para estudiar una direccion transversal y fundaciones. |
| `2017_67-306-Model.pdf` | Elevacion eje F-F'. Incluye pisos 1°S a 4°, ejes 3, 2, 1, 1b y 8, ademas de cortes A/B/C. | Marco transversal con vigas y columnas/muros; util para modelo parcial real. |
| `2017_67-307-Model.pdf` | Elevacion eje G. Incluye pisos 1° a 4°, ejes 3, 2, 1, 1b y 8. Se observa diagonal/refuerzo o elemento inclinado en zona superior. | Marco transversal y deteccion de irregularidades locales. |
| `2017_67-308-Model.pdf` | Elevacion eje H. Incluye pisos 1° a 4° y ejes 3, 2, 1, 1b. | Marco transversal relativamente claro para alturas y elementos verticales. |
| `2017_67-309-Model.pdf` | Elevacion eje I. Incluye pisos 1° a 4°, ejes 3, 2, 1 y 1AA. | Marco transversal; util para continuidad de elementos hacia el borde del edificio. |
| `2017_67-310-Model.pdf` | Elevacion eje I', elevacion eje IB y elevacion eje J. Incluye cortes A, B y B2. | Detalles de borde y cortes de secciones; apoyo para idealizacion de elementos equivalentes. |
| `2017_67-400-Model.pdf` | Serie de detalles o elevaciones relacionadas con elementos estructurales. Lectura pendiente con zoom. | Pendiente de clasificacion fina. |
| `2017_67-401-Model.pdf` | Serie de detalles o elevaciones relacionadas con elementos estructurales. Lectura pendiente con zoom. | Pendiente de clasificacion fina. |
| `2017_67-402-Model.pdf` | Serie de detalles o elevaciones relacionadas con elementos estructurales. Lectura pendiente con zoom. | Pendiente de clasificacion fina. |
| `2017_67-500-Model.pdf` | Serie de detalles estructurales. Lectura pendiente con zoom. | Uso posterior para detalles, no para partir el benchmark global. |
| `2017_67-501-Model.pdf` | Serie de detalles estructurales. Lectura pendiente con zoom. | Uso posterior para detalles, no para partir el benchmark global. |
| `2017_67-502-Model.pdf` | Serie de detalles estructurales. Lectura pendiente con zoom. | Uso posterior para detalles, no para partir el benchmark global. |
| `2017_67-503-Model.pdf` | Serie de detalles estructurales. Lectura pendiente con zoom. | Uso posterior para detalles, no para partir el benchmark global. |
| `2017_67-600-Model.pdf` | Plano de detalles o elementos especiales. Lectura pendiente con zoom. | Uso posterior. |
| `2017_67-700-Model.pdf` | Plantas de cargas de diseno. Se distinguen planta cielo 1° subterraneo, cielo piso 1° y cielo piso 4°. Incluye leyendas de `PP. LOSA`, `PP. ADIC.` y `SC`. | Fuente principal para cargas gravitacionales de losa y sobrecargas por zona. |
| `2017_67-800-Model.pdf` | Plano de detalle o serie especial. Lectura pendiente con zoom. | Uso posterior. |
| `2017_67-801-Model.pdf` | Plano de detalle o serie especial. Lectura pendiente con zoom. | Uso posterior. |
| `2017_67-802-Model.pdf` | Plano de detalle o serie especial. Lectura pendiente con zoom. | Uso posterior. |
| `acad.err` | Archivo de error/log de AutoCAD subido junto a los PDFs. No es un plano. | No usar como dato estructural. Se puede eliminar en una limpieza futura si el grupo lo aprueba. |

## Informacion que se puede extraer con confianza moderada

- El edificio tiene niveles identificables `1°S`, `1°`, `2°`, `3°` y `4°`.
- Hay una reticula estructural con ejes alfanumericos, por ejemplo `E`, `F`, `G`, `H`, `I`, `J`, y ejes numericos como `1`, `2`, `3`, `8`.
- La serie `100` contiene plantas estructurales y fundaciones.
- La serie `200` contiene informacion de losas y armaduras.
- La serie `300-310` corresponde principalmente a elevaciones y cortes estructurales.
- El plano `700` es clave para cargas de diseno.
- Se observan vigas/muros con etiquetas de seccion del tipo `V. 20/80`, `V. 20/130`, `V.F. 20/220`, `V.F. 15/225`, `V. 60/80`, `P. 70x70`, `M.H.A. e=20`, `M.H.A. e=30`, pero deben verificarse por zoom antes de usarlas.

## Informacion que NO conviene automatizar aun

- Cotas pequenas de vigas, muros y separaciones entre ejes.
- Cuantias de armadura.
- Secciones definitivas de todos los elementos.
- Cargas por zona sin revisar la leyenda con mayor zoom.
- Coordenadas exactas del modelo global.

## Recomendacion para iniciar el benchmark 3D Semana 1

Para el benchmark 3D conviene elegir un subconjunto real y simple, no todo el edificio.

Sector recomendado preliminar:

- Usar una franja entre dos ejes transversales, por ejemplo cerca de ejes `F-G-H` y pisos `1° a 2°`.
- Tomar un rectangulo de un vano en una direccion y un vano en la otra.
- Modelar 4 columnas o muros equivalentes, vigas perimetrales y una losa tributaria no modelada con elementos finitos.
- Usar el plano `700` para definir una carga superficial simplificada.
- Usar una elevacion de la serie `300-310` para alturas de piso y continuidad vertical.

La prioridad de Semana 1 no es representar todo el edificio, sino construir un benchmark 3D realista, verificable y explicable.

## Archivos que deben revisarse con zoom antes de modelar

- `2017_67-100-Model.pdf`: fundaciones y apoyos.
- `2017_67-101-Model.pdf`: plantas cielo 1° subterraneo y piso 1°.
- `2017_67-102-Model.pdf`: plantas cielo piso 2° y 3°.
- `2017_67-700-Model.pdf`: cargas por zona.
- `2017_67-300-Model.pdf`: elevacion eje 1-1', niveles y alturas.
- `2017_67-302-Model.pdf`: elevacion eje 2.
- `2017_67-303-Model.pdf`: elevacion eje 3-3'.
- `2017_67-306-Model.pdf`: elevacion eje F-F'.
- `2017_67-307-Model.pdf`: elevacion eje G.

## Pendientes

- Confirmar si existen PDFs vectoriales, DWG o DXF originales.
- Extraer una tabla limpia de ejes y cotas.
- Confirmar secciones estructurales definitivas para vigas, columnas y muros.
- Confirmar cargas de diseno desde `2017_67-700-Model.pdf` con zoom suficiente.
- Definir el sector real que se usara como benchmark 3D de Semana 1.
