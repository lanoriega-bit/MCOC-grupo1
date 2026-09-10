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

Existe ademas una banda angosta cuya leyenda indica `SC=500` y
`PM.ADIC.=2800`, pero la conversion DXF perdio el superindice de la unidad. A
diferencia de las otras bandas lineales, su titulo no dice `CARGA LINEAL`.
Ambos valores deben verificarse en el DWG original antes de clasificarlos como
superficiales (`4.903325` y `27.458620 kN/m2`) o lineales (`4.903325` y
`27.458620 kN/m`).

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
   y validar coordenadas con al menos dos ejes estructurales.
3. Resolver huecos, escaleras y juntas antes de sumar areas.
4. Comprobar por piso que la union de zonas superficiales cubre la huella una
   sola vez, sin vacios ni solapes.
5. Transferir cargas hacia vigas, muros y columnas sin duplicar las etapas de
   carga del JSON historico.
6. Mantener toda lectura ambigua con estado `REVIEW_REQUIRED`; en particular,
   confirmar las unidades de la banda `SC=500 / PM.ADIC.=2800` en el cielo de
   piso 1 del EDIFICIO_1.
