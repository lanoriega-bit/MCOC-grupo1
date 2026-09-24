# Demanda-capacidad P1L4

## Objetivo

Este modulo arma un contrato JSON trazable para comparar la demanda elastica 3D de OpenSees contra curvas P-M de capacidad de laboratorio para dos elementos de estudio. La salida principal es `demanda_capacidad.json`, pensada como dato consumible por visualizacion o QA, sin modificar Unity ni resultados historicos.

## Elementos y caso activo

Caso activo: `CASE_R`.

Columna seleccionada: `E2-P1-C-002`, OpenSees elementTag `10009`, analysis_id `A-C-0009`, nodos `[2, 17]`, eje P-M `My`.

Muro seleccionado: `E2-P1-M-019`, OpenSees elementTag `10171`, analysis_id `A-M-0171`, nodos `[227, 266]`, eje P-M `Mz`.

## Extraccion automatica de demanda

`build_demanda_capacidad.py` lee `elementos_estudio.json`, busca cada `opensees_tag` en `entregas/P1L3/results/a3a4/analysis_model.json` y extrae las fuerzas locales de `CASE_R` desde `entregas/P1L3/results/a7/cases/R/elements.json`.

El orden de componentes es `[P, Vy, Vz, T, My, Mz]`, con datos fuente en `N` y `N.m`. El contrato convierte a `kN` y `kN.m`, conserva `end1` y `end2`, y selecciona el extremo con mayor momento absoluto del eje P-M usado.

## Trazabilidad

Cadena usada para cada elemento:

`elementTag -> element_id -> nodos -> seccion/geometria -> resultados CASE_R -> curva P-M -> punto de demanda`.

Para la columna:

`10009 -> E2-P1-C-002 -> [2, 17] -> P.70x70 / C_P2_01_0001_lab_fiber_section -> CASE_R -> entregas/P1L3/capacidad_ha/results/pm_interaction.csv -> demanda P-My`.

Para el muro:

`10171 -> E2-P1-M-019 -> [227, 266] -> 5.800000000020009 x 0.22 m / E2-P1-M-019_lab_wall_fiber_section -> CASE_R -> entregas/P1L4/demanda_capacidad/results/wall_pm_interaction.csv -> demanda P-Mz`.

## Armadura y materiales

Columna `E2-P1-C-002`: la capacidad P-M viene de Semana 3, `entregas/P1L3/capacidad_ha/results/pm_interaction.csv`, con entrada `entregas/P1L3/capacidad_ha/datos/seccion_estudio.json`. En esos archivos la geometria `P.70x70`, `fc = 35 MPa` y `fy = 420 MPa` estan confirmados; la armadura usada para el modelo de capacidad esta marcada como `ASUMIDO_LAB`: 12 barras de diametro `0.025 m` y recubrimiento `0.04 m`.

Muro `E2-P1-M-019`: no se encontro detalle verificable de armadura vertical, horizontal ni elementos de borde en las fuentes auditadas. Por eso la armadura esta marcada explicitamente como `ASUMIDO_LAB` en `datos/wall_section_estudio.json`: barras verticales de diametro `0.016 m` cada `0.20 m` en `2` caras/capas, barras horizontales de diametro `0.012 m` cada `0.20 m` solo documentales para trazabilidad, y sin elementos de borde confirmados. Para la P-M vertical se usan `60` fibras/barras verticales, `640` fibras de hormigon, `As = 0.012063715789784806 m2`, `Ag = 1.2760000000044018 m2` y cuantia `rho = 0.009454322719234475` (`0.9454322719234475 %`).

## Generacion de archivos

`wall_pm_interaction.csv` y `wall_pm_interaction.png` se generan con:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 entregas/P1L4/demanda_capacidad/opensees/wall_pm_interaction.py
```

QA de la seccion Fiber del muro:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 entregas/P1L4/demanda_capacidad/opensees/wall_section_model.py
```

`demanda_capacidad.json` se genera con:

```bash
python3 entregas/P1L4/demanda_capacidad/build_demanda_capacidad.py
```

## Criterio de validez de curva

Los puntos con problemas de convergencia se conservan por trazabilidad con `valid=false`. Esos puntos no se usan como frontera valida ni para interpolar `inside_envelope`; la interpolacion usa solo puntos con `valid=true`.

## Resultado demanda-capacidad

Columna `10009`: `P = -57.57961084098628 kN`, `My = 423.28153608023047 kN.m`, `Mz = 159.73758901688075 kN.m`, eje P-M `My`, `inside_envelope = true`.

Muro `10171`: `P = 2632.200566732805 kN`, `My = -198.95206729130788 kN.m`, `Mz = -7636.192288738655 kN.m`, eje P-M `Mz`, `inside_envelope = true`.

## Fuentes principales

`entregas/P1L4/demanda_capacidad/elementos_estudio.json`: seleccion de elementos, tags, nodos y fuentes.

`entregas/P1L3/results/a3a4/analysis_model.json`: modelo de analisis, nodos, secciones FE y tags OpenSees.

`entregas/P1L3/results/a7/cases/R/manifest.json`: caso activo `CASE_R`.

`entregas/P1L3/results/a7/cases/R/elements.json`: resultados locales de demanda para `CASE_R`.

`entregas/P1L3/capacidad_ha/datos/seccion_estudio.json`: entrada de seccion de la columna usada en Semana 3.

`entregas/P1L3/capacidad_ha/results/pm_interaction.csv`: curva P-M historica de la columna.

`entregas/P1L4/demanda_capacidad/datos/wall_section_estudio.json`: entrada trazable de seccion del muro y armadura `ASUMIDO_LAB`.

`entregas/P1L4/demanda_capacidad/results/wall_pm_interaction.csv`: curva P-M generada para el muro.

`entregas/P1L4/demanda_capacidad/results/wall_pm_interaction.png`: grafico P-M generado para el muro.
