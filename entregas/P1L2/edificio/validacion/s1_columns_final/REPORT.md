# Auditoria final de columnas S1 en ejes I e I'

Estado: `PASS`
Alcance: `GEO-COL-S1-001`
Metodo: lectura directa de las elevaciones estructurales completas, no extrapolacion desde plantas superiores.

## Evidencia geometrica

| Eje | Lamina | Elevacion | Luz 1-2 | Luz 2-3 | Residual maximo |
| --- | --- | --- | ---: | ---: | ---: |
| I | 2017_67-309 | ELEVACION EJE I | 8.900 m | 7.250 m | 0.000 m |
| I' | 2017_67-310 | ELEVACION EJE I' | 8.900 m | 7.250 m | 0.000 m |

En ambos ejes, los contornos inferiores llegan desde el nivel del primer piso hasta la viga de fundacion. Cada estacion 1, 2 y 3 tiene rotulo `P. 70x70`.

## Veredicto individual

| ID | Ubicacion | Seccion | Veredicto | Fuente |
| --- | --- | --- | --- | --- |
| E1-S1-C-014 | I-2 | 0.70 x 0.70 m | CONFIRMED | 2017_67-309 |
| E1-S1-C-015 | I-1 | 0.70 x 0.70 m | CONFIRMED | 2017_67-309 |
| E1-S1-C-016 | I-3 | 0.70 x 0.70 m | CONFIRMED | 2017_67-309 |
| E1-S1-C-017 | I'-1 | 0.70 x 0.70 m | CONFIRMED | 2017_67-310 |
| E1-S1-C-018 | I'-2 | 0.70 x 0.70 m | CONFIRMED | 2017_67-310 |
| E1-S1-C-019 | I'-3 | 0.70 x 0.70 m | CONFIRMED | 2017_67-310 |

## Correccion derivada

La existencia de las seis columnas deja de ser una inferencia. Sus centros se normalizan a las intersecciones de ejes canonicos y su seccion a 0.70 x 0.70 m. Esto corrige especialmente `E1-S1-C-016`, cuya envolvente extraida de planta (0.85 x 0.92 m y centro desplazado) contradice la elevacion estructural explicita.

## Archivos visuales

- `2017_67-309_I_crop.png`: elevacion I, estaciones 1-3 y tramo inferior.
- `2017_67-310_Iprime_crop.png`: elevacion I', estaciones 1-3 y tramo inferior.
- `s1_columns_final_audit.json`: evidencia estructurada reproducible.
