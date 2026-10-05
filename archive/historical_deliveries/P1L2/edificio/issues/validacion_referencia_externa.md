# VALIDACIÓN DIRIGIDA DE LA REFERENCIA EXTERNA PARA VALIDACIÓN

Draft de trabajo. La referencia externa NO es fuente de verdad; se usa para confirmar/contradecir
la geometría extraída de los DXF. Los planos siguen siendo la fuente primaria.

## Resumen ejecutivo
- Las **dimensiones estructurales** de la referencia externa quedaron **CONFIRMADAS** por el texto de los DXF.
- Los **ejes numéricos** de la referencia externa (X=0,5,10,...,35; Y=8.9/0/−7.25) usan un **grid regular idealizado de 5 m** que **NO reproduce** los ejes reales de los DXF (parte_2 usa ejes A,B,C,D; parte_1 usa E,F,G,H,I,J a 10 m). Los números de ejes de la externa son modelización propia del alumno, **no confirmables ni forceables**.
- La **existencia geométrica** (extensión negativa en X, voladizos, muros núcleo, columnas que aparecen/desaparecen) está corroborada cualitativamente, pero las **posiciones/cotas exactas externas difieren** de las reales.

## Sistema de coordenadas (diferencia clave)
- Modelo local resuelto: origen `Eje A-1 de Parte 2 / LT2 = (0,0,0)`.
  - parte_1 X: A'=−3.78, A=0, B=7.5, C=17.49, C'=25.04, D=27.49, D'=28.17
  - parte_1 X: E=27.49, F=37.49, G=47.49, H=57.49, I=67.49, J=77.49
  - Y: 1=0, 2=8.9 (parte_2 y parte_1); parte_1 2a=14.95, 3=17.25.
- La externa (X=0..35 @5m, especial 7.51, Y=8.9/0/−7.25/−11.37) es un grid simplificado:
  - `Y=8.9` SI coincide con el eje real "2" (ambas partes).
  - `X=0`→eje A (parte_2), `Y=0`→eje 1.
  - `X=5,10,15,20,25,30,35` y `7.51` NO son ejes reales (no aparecen como líneas estructurales verticales ni como rótulos en los DXF; los rótulos reales son letras A–D' y E–J).
  - `CONCLUYE: no forzar el modelo sobre el grid externo.`

## CONFIRMADO (evidencia textual en DXF)
| Ítem externo | Evidencia DXF | Resultado |
|---|---|---|
| Columnas principales ≈ 70×70 | `P. 70x70` (2017_67-101:25, 102:36, 103:18); `70x70` (2024_22-101:8, 102:8) | CONFIRMADO |
| Vigas principales ≈ 60×80 | `V. 60/80` (2017_67-101:55, 102:110, 103:54; 2024_22-101:35, 102:33) | CONFIRMADO |
| Viga especial ≈ 30×45 | `V. 30/45` (2017_67-102:2) | CONFIRMADO (rara) |
| Losa espesor 0.15 | `LOSA e=15` y `(LOSA e=15 (S.I.C.))` en todas las láminas (también e=12/20/25 puntuales) | CONFIRMADO (referencia 0.15) |

## CONTRADICHO / SIN-EVIDENCIA (geométrico)
| Ítem externo | Hallazgo | Resultado |
|---|---|---|
| Extensión X=−10 (ala) | Fundaciones (2024_22-100) llegan a **X≈−9.0**; pisos superiores (101/102) solo a **X=−4.0** | PARCIAL: −9 en fundaciones, NO −10 en pisos |
| Muros X −6.7..−3.3, Y≈−4.945/+5.00, espesor 0.20-0.25 | Pisos: muros núcleo en X∈[−3.84,−3.24] (caja 0.60 m), Y∈[−4.18,1.94]; fundaciones: núcleo en X∈[−8.84,−6.79], Y∈[−0.68,2.24] y [14.74,17.66]. No hay muros en X −6.8..−3.8 de pisos | NO CONFIRMADO en posición/cota exacta; el núcleo real está en −3.84/−3.24 (pisos) y −8.84/−6.79 (fundaciones). La Y externa no coincide |
| Voladizos X→37.55/40, −11.37 | Los voladizos se analizan en parte_1 (X 17..78, Y −29..29). Valores externos están en grid del alumno | SIN-EVIDENCIA para cotas exactas |
| Columnas intermedias aparecen/desaparecen en X=5,7.51,15,25 | Se CONFIRMA el fenómeno real, pero en parte_1: 12 grupos `REQUIERE_REVISION_DATOS` (columnas solo en piso 01 o 02, no continuas) en X≈57–72, Y≈0–28 | CONFIRMADO cualitativo; posición en X diferente (externo en grid alumno) |
| Conteos (89 col, 317 barras, etc.) | Modelo actual: 72 columnas lógicas, 39 grupos verticales, 424 vigas lógicas, 144 muros lógicos. Conteos externos son solo comparativos (parte de un modelo 3D de alumno con grid distinto) | NO OBJETIVO |

## Efecto sobre POSIBLE / conflictos
- La confirmación de **P. 70×70 / V. 60/80 / LOSA e=15** como texto explícito en ambas partes aumenta la confianza de los elementos POSIBLE que ya coinciden con esas dimensiones (no desambiguó los 190 POSIBLE restantes, que son por falta de payload/etiqueta, no por dimensión).
- La **diferencia de grid** explica por qué los ejes externos no asignan en el modelo: no es un error de extracción sino una convención distinta del alumno. Se documenta en `sistema_global` (no como conflicto de datos).
- El **ala X negativa** y los **muros núcleo** quedan como geometría real pero su posición/cota NO se ajusta a la externa.

## Sistema Z (confirmado por usuario, pendiente consolidar en planos)
- `model_z_m = source_elevation_m + 7.97`; radier −7.97; 1S −4.01; P1 −0.05; P2 +3.91; P3 +7.87; P4 +11.83.
- Modelo: base 0, 1=3.96, 2=7.92, 3=11.88, 4=15.84 (niveles separados 3.96 m, NO 4.00).
- Documentar `source_elevation_m` / `model_z_m` / `z_offset_m=7.97` por plano y verificar consistencia en todas las láminas antes de modelar 3D.

## Conclusión
La referencia externa CONFIRMA dimensiones y la existencia de la geometría problemática (ala negativa,
núcleos, columnas discontinuas) pero NO valida sus cotas de grid (son idealización del alumno). No se
adelantan cambios al modelo; se usará como referencia independiente de existencia, no de posición.
Pendiente humana: decisión de calce (A vs B) y de identidad de `2017_67-103` (PISO 4 / +11.83).