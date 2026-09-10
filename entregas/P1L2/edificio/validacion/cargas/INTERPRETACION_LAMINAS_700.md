# Interpretacion de las laminas 700

Fecha de corte: 2026-09-09.

## Alcance

Lectura visual y CAD de `2017_67-700` y `2024_22-700`. Los valores se
transcriben separados por naturaleza de carga. Todavia no se asignan al modelo:
antes se deben transformar los contornos HATCH desde las coordenadas de cada
planta de la lamina a las coordenadas globales del edificio.

Conversion usada: `1 kgf = 9.80665 N`.

## Peso propio de losa

Ambas laminas especifican:

`PP.LOSA = e(m) x 2500 kgf/m3`.

Por tanto, el peso propio superficial depende del espesor local:

| Espesor | PP losa |
| ---: | ---: |
| 0.15 m | 3.677494 kN/m2 |
| 0.20 m | 4.903325 kN/m2 |
| 0.25 m | 6.129156 kN/m2 |

No es valido usar 15 cm en toda la planta: los planos estructurales contienen
indicaciones locales de 20 y 25 cm.

## EDIFICIO_1 - serie 2017_67

La lamina contiene **seis intensidades superficiales SC distintas**: 100, 200,
250, 300, 400 y 500 kgf/m2. No son siete ni forman un unico `q_Q` global.

### Cielo primer subterraneo

Combinaciones superficiales identificadas en la leyenda:

| SC | PM adicional |
| ---: | ---: |
| 4.903325 kN/m2 (500 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.941995 kN/m2 (300 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.451663 kN/m2 (250 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 4.903325 kN/m2 (500 kgf/m2) | 2.941995 kN/m2 (300 kgf/m2) |

### Cielo piso 1

Combinaciones superficiales identificadas:

| SC | PM adicional |
| ---: | ---: |
| 3.922660 kN/m2 (400 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 1.961330 kN/m2 (200 kgf/m2) | 1.961330 kN/m2 (200 kgf/m2) |
| 4.903325 kN/m2 (500 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.941995 kN/m2 (300 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.451663 kN/m2 (250 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |

Existe ademas una banda angosta cuya leyenda indica `SC=500 kgf/m2` y
`PM.ADIC.=2800 kgf/m2`, equivalentes a `4.903325` y `27.458620 kN/m2`. La
unidad quedo confirmada en la revision final: tanto el DXF como el respaldo DWG
original de 2018 conservan el `2` como una entidad TEXT separada sobre `Kg/m`.
La misma composicion tipografica aparece en SC, mientras que las bandas
lineales estan tituladas explicitamente `CARGA LINEAL` y no llevan superindice.

### Cielo piso 2

Combinaciones superficiales identificadas:

| SC | PM adicional |
| ---: | ---: |
| 3.922660 kN/m2 (400 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 1.961330 kN/m2 (200 kgf/m2) | 1.961330 kN/m2 (200 kgf/m2) |
| 4.903325 kN/m2 (500 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.941995 kN/m2 (300 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.451663 kN/m2 (250 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |

La lamina marca una carga puntual de `SC=7000 kgf` y `PM.ADIC.=13000 kgf`,
equivalentes a `68.646550 kN` y `127.486450 kN`.

### Cielo piso 3

Combinaciones superficiales identificadas:

| SC | PM adicional |
| ---: | ---: |
| 1.961330 kN/m2 (200 kgf/m2) | 1.961330 kN/m2 (200 kgf/m2) |
| 2.941995 kN/m2 (300 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 4.903325 kN/m2 (500 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.451663 kN/m2 (250 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |

Se identifican dos pares de cargas puntuales:

- `SC=6000 kgf` y `PM.ADIC.=10000 kgf`: `58.839900 kN` y `98.066500 kN`.
- `SC=6700 kgf` y `PM.ADIC.=13000 kgf`: `65.704555 kN` y `127.486450 kN`.

### Cielo piso 4

Combinaciones superficiales identificadas:

| SC | PM adicional |
| ---: | ---: |
| 0.980665 kN/m2 (100 kgf/m2) | 3.432328 kN/m2 (350 kgf/m2) |
| 1.961330 kN/m2 (200 kgf/m2) | 1.961330 kN/m2 (200 kgf/m2) |

La leyenda `CARGAS DE DISEÑO (CARGA LINEAL)` indica:

- `SC=800 kgf/m` = `7.845320 kN/m`;
- `PM.ADIC.=7600 kgf/m` = `74.530540 kN/m`.

## EDIFICIO_2 - serie 2024_22

### Cielo primer subterraneo a cielo piso 3

La misma planta de cargas se declara para S1, P1, P2 y P3. Combinaciones
superficiales:

| SC | PM adicional |
| ---: | ---: |
| 1.961330 kN/m2 (200 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 4.903325 kN/m2 (500 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |
| 2.941995 kN/m2 (300 kgf/m2) | 2.549729 kN/m2 (260 kgf/m2) |

### Cielo piso 4

La carga superficial indicada es `SC=200 kgf/m2` y `PM.ADIC.=200 kgf/m2`,
equivalentes a `1.961330 kN/m2` cada una.

La leyenda `CARGAS DE DISEÑO (CARGA LINEAL)` indica:

- `SC=100 kgf/m` = `0.980665 kN/m`;
- `PM.ADIC.=1500 kgf/m` = `14.709975 kN/m`.

## Reglas para la integracion

1. Conservar `PP`, `PM`, `SC`, cargas lineales y cargas puntuales como campos
   separados; no reducirlos anticipadamente a un unico `q` uniforme.
2. Intersectar cada HATCH con la huella de losa del piso despues de transformar
   y validar coordenadas con al menos tres intersecciones de ejes estructurales
   independientes.
3. Resolver huecos, escaleras y juntas antes de sumar areas.
4. Comprobar por piso que la union de zonas superficiales cubre la huella una
   sola vez, sin vacios ni solapes.
5. Transferir cargas hacia vigas, muros y columnas sin duplicar las etapas de
   carga del JSON historico.
6. Mantener toda lectura ambigua con estado `REVIEW_REQUIRED`; la unidad de la
   banda `SC=500 / PM.ADIC.=2800 kgf/m2` ya fue confirmada y deja de pertenecer
   a esta categoria.

## Extraccion geometrica HATCH

Se extrajeron 34 zonas directamente de la capa `HATCH CARGAS`. El factor de
escala observado es `0.01 m/unidad`; cada planta tiene una traslacion distinta
dentro de la lamina. La primera extraccion uso transformaciones candidatas y se
conserva como antecedente. La auditoria posterior de EDIFICIO_1 confirmo las
transformaciones mediante los xrefs 101/102/103, seis intersecciones de ejes por
piso y `global_axes.json`. La transformacion correcta incluye inversion de Y
(`mirror_y=true`), giro 0 grados y el calce global `dx=27.491 m`.

| Edificio | Piso(s) | Zona superficial [m2] | Union de todos los HATCH [m2] | Historica [m2] | HATCH/historica |
| --- | --- | ---: | ---: | ---: | ---: |
| EDIFICIO_1 | S1 | 387.863 | 387.863 | 1145.088 | 0.339 |
| EDIFICIO_1 | P1 | 967.554 | 997.042 | 1829.364 | 0.545 |
| EDIFICIO_1 | P2 | 843.914 | 843.914 | 919.252 | 0.918 |
| EDIFICIO_1 | P3 | 956.721 | 956.721 | 732.410 | 1.306 |
| EDIFICIO_1 | P4 | 934.561 | 957.317 | 1018.575 | 0.940 |
| EDIFICIO_2 | S1-P3 | 557.894 | 557.894 | 584.230 | 0.955 |
| EDIFICIO_2 | P4 | 535.620 | 544.652 | 584.230 | 0.932 |

La columna `todos los HATCH` incluye bandas lineales o ambiguas dibujadas con
ancho solo como referencia grafica; por ello no es todavia el area fisica final
de losa. Aun asi, el contraste prueba que el historico no tiene un factor de
error unico: subestima EDIFICIO_1 P3 y sobrestima los demas pisos, de forma muy
severa en S1 y P1.

El overlay muestra un problema adicional en EDIFICIO_1 S1: existe zona cargada
aproximadamente entre `X=37..49 m` y `Y=6..16 m` sin vigas o muros receptores
visibles en el modelo combinado. Debe verificarse en las plantas estructurales
antes de completar la transferencia.

Archivos reproducibles:

- `entregas/P1L3/scripts/extract_load_zones_700.py`.
- `entregas/P1L3/results/a1a2/load_zones_700_source.json`.
- `entregas/P1L3/results/a1a2/load_zones_700_overlay.png`.
- `entregas/P1L3/scripts/audit_load_zones_700_alignment.py`.
- `entregas/P1L3/results/a1a2/load_zones_700_alignment/REPORT.md`.
- `entregas/P1L3/results/a1a2/load_zones_700_alignment/spatial_audit.json`.
