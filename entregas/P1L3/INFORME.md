# Semana 3 - carga viva, sismo, superposicion y capacidad HA

Fecha del checkpoint: 2026-09-09.

## Resultado ejecutivo

La entrega P1L3 esta integrada de extremo a extremo: el modelo actual ejecuta
OpenSees para `G`, `Q`, `EX`, `EY` y `R`, exporta el contrato JSON y presenta
los resultados y la capacidad HA en Unity. Todas las verificaciones numericas
programadas pasan. La geometria y las masas aun tienen limitaciones auditadas,
por lo que este checkpoint es funcional para la demostracion y no representa
una certificacion final del edificio real.

## A. Carga viva

Se usa la misma geometria tributaria de Semana 2: 110 panos aceptados, con area
efectiva de 3392.624 m2. Para el valor parametrizado actual de `q_Q`:

- `Q transferida = 8317.569065 kN`;
- `q_Q A = 8317.569065 kN`;
- error relativo de conservacion: `1.12e-16` (`PASS`).

Las losas no son elementos FE. La carga superficial se reparte a vigas por
areas tributarias y se aplica en sus nodos extremos.

## B. Sismo pseudoestatico

Los patrones `EX` y `EY` son independientes. La fuente vigente usa masa de
piso basada en peso sismico y un coeficiente basal configurable de `0.10`; el
parametro puede cambiarse cuando el profesor defina el patron definitivo.

Cada fuerza de piso se aplica en `CM + excentricidad accidental` y se reparte
baricentricamente a tres nodos del piso. Esto conserva fuerza, punto de
aplicacion y momento torsional sin modelar losas FE.

- fuerza total EX/EY: `6384.122192 kN` en cada direccion;
- error relativo de corte basal EX: `3.13e-13`;
- error relativo de corte basal EY: `7.83e-13`;
- error maximo del punto de aplicacion: `7.11e-15 m`;
- sentido de deformada EX y EY: `PASS`.

## C. Superposicion

Se verifico la combinacion arbitraria:

`R = 1.20 G + 0.50 Q + 1.00 EX + 0.30 EY`.

La suma de respuestas independientes se comparo con una quinta corrida
OpenSees explicita que aplica simultaneamente la combinacion:

- desplazamientos: error relativo `2.41e-12`;
- reacciones: error relativo `4.75e-13`;
- fuerzas internas locales: error relativo `1.30e-12`;
- tolerancia: `1e-9`; resultado global: `PASS`.

La superposicion funciona porque el modelo global usa materiales, geometria y
condiciones de borde lineales. Dejaria de ser valida con plasticidad,
fisuracion/rigidez dependiente del estado, grandes desplazamientos, contacto o
otras no linealidades.

## D. Capacidad de hormigon armado

Se construyo una Fiber Section OpenSees de columna de 0.70 x 0.70 m, malla de
28 x 28 fibras de hormigon y 12 barras longitudinales de 25 mm. Se usa
`Concrete01` con `f'c=35 MPa` y `Steel01` con `fy=420 MPa`.

Resultados principales:

- M-phi con P=0: momento maximo `766.08 kNm`;
- P=0: `Mmax=766.08 kNm` (`PASS`);
- P=4873.06 kN: `Mmax=1696.45 kNm` (`PASS`);
- P=9746.13 kN: `Mmax=1650.07 kNm` (236/240 pasos; post-pico parcial);
- compresion pura: `19492.25 kN`, `M=0`.

Cada fibra integra la tension del material sobre una pequena porcion de area;
las barras son fibras discretas de acero. La carga axial cambia la posicion del
eje neutro y el estado de deformacion, por eso modifica la capacidad a momento.
Capacidad es lo que la seccion resiste; demanda es lo que solicita el analisis
global. No se hace aun una comprobacion normativa demanda/capacidad.

## Demostracion en Unity

1. Abrir `entregas/P1L3/Jose/viewer_unity/Assets/Main.unity` y pulsar Play.
2. En `Resumen`, mostrar los cuatro bloques y sus estados `PASS`.
3. En `Casos FE`, alternar `G`, `Q`, `EX`, `EY` y `R`.
4. Seleccionar una viga/columna para ver las fuerzas locales del caso activo.
5. En `Capacidad HA`, explicar discretizacion/refuerzo, M-phi y P-M.
6. Buscar `E2-P1-C-002` para mostrar el mapeo de la seccion estudiada.

## Reproduccion

```powershell
python entregas/P1L3/scripts/run_p1l3_integrated.py
python entregas/P1L3/scripts/build_unity_bundle.py
```

El detalle numerico queda en `results/a7/a7_report.json`; cada caso conserva
`manifest.json`, desplazamientos nodales, reacciones y fuerzas de elementos.

## Limitaciones declaradas

- La geometria tributaria cubre 3392.624 m2 y sigue incompleta.
- Las masas EX/EY provienen del trabajo sismico historico y usan una cobertura
  distinta; deben recalcularse cuando se cierre la huella de losa.
- Hay 93 elementos flotantes excluidos del FE, sin inventar conexiones.
- Las deformaciones globales actuales son anormalmente grandes y no deben
  interpretarse como demanda final antes de auditar rigidez, conectividad y
  ejes locales.
- Armadura, recubrimiento y parte de los parametros constitutivos de la Fiber
  Section son hipotesis de laboratorio explicitamente identificadas.
