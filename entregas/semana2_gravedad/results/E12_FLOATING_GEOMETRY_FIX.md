# E12 FLOATING GEOMETRY FORENSIC FIX — FINAL

- Fecha: 2026-09-05
- Ámbito: vista E12 en Unity (Both buildings) en Windows. E1 congelado (c0c0cdb). E2 corregido en la fuente del pipeline.
- Directiva: no ocultar, no offsets en Unity; clasificar y filtrar en la fuente; QA/FE byte-idénticos.

## FLOATING OBJECTS FOUND

Auditoría objeto por objeto de `edificios12_unity.json` frente al frame estructural E2 (grid FE de columnas + huella planimétrica de columnas):

- **1072 vigas** E2 → **365 elementos fuera del frame** (73 vigas, 179 muros, 113 soportes).
- Banda 1S parte_1: vigas/muros a y[20.4, 43.5] (ej. `VIGA_P1_1S_0001` en y=22.6; `MURO_P1_1S_0013..0048` en y≥22), plano 2017_67-101 (ventana-y 4400-9000).
- Banda fundacion parte_1: muros/vigas a y[20.5, 31.4], plano 2017_67-100 (ej. `FUNDACION_P1_FUNDACION_0026..`), más soportes a y<0 (hasta -11.7) sin columna debajo.
- Piso 1 parte_1: bandas y[21.9, 28.8] (`NOTAS`: `detalle_cad_superior_no_planta_principal`, `modelable_3d=false`).
- Sin columnas alteradas: las 125 columnas E2 coinciden con el grid FE (`7.606,0.118,0→3.96`, etc.) y nunca se filtran.

## ROOT CAUSES

1. Geometría "extra" (sótano + muro de contención + piso 1) alineada **sin control de columnas**: `dy=+49.489` (subterráneo parte_1, `no columns available`) y `dy=+28.706` (fundación parte_1). `region_specs.json`/`calibration_offsets.json`/`ejes.json` lo documentan.
2. Soportes/apoyos CAD no asociados a nodo FE ni a columna real (y<0 e y>21).
3. El pipeline volcaba **toda** la geometría `modelable_3d` al payload visual sin distinguir estructura vs contexto; en "Both" esas bandas se veían como líneas flotando bajo/al lado del frame E2.

## FLOOR LEVELS

Vía `niveles.json` (`z_offset_m=7.97`; `model_z = source_elevation + 7.97`):

| Building | RAW floor | Display | expected_z_m | source_elevation_m |
|---|---|---|---|---|
| E2 | fundacion | fundacion | 0.00 | -7.97 |
| E2 | 1S | 1S | 3.96 | -4.01 |
| E2 | 1 | 1 | 7.92 | -0.05 |
| E2 | 2 | 2 | 11.88 | 3.91 |
| E2 | 3 | 3 | 15.84 | 7.87 |
| E2 | 4 | 4 | 19.80 | 11.83 |

Vigas/slabs en el plano del piso; muros a cota media (z-1.98); columnas entre extremos de historia; soportes en z=0. Tabla completa (11 filas) en `results/e12_floating_geometry_audit.json`.

## FIXES

En `opensees/final_e2_e12_pipeline.py` (fuente, no Unity):

- Nueva clasificación `classify_visual_contexto`: huella = bbox de centros de columnas E2 (x[0.103,77.382] y[-0.000,20.389]) + pad 1.20 m; soporte sin base FE/columna en 2.50 m → CONTEXTO.
- `edificio2_unity.json` y `edificios12_unity.json` regenerados **deterministas** (PYTHONHASHSEED=1 y 999 → idénticos) con:
  - solo elementos ESTRUCTURAL (999 vigas, 211 muros, 201 soportes, 125 columnas),
  - `elementos_contexto[]` (365 registros completos, geometría+zona+motivo) y `clasificacion_geometrica` (regla/frame explícitos).
- El FE, las losas, las cargas, los blockers y QA **no se tocan**: el filtro solo cambia el payload visual Unity.

## BOUNDS

- E1: x[-0.35,49.90] y[-11.48,28.34] z[0,19.80] (sin cambios).
- E2 columns/walls renderizados: x[0.10,77.38] y[-0.00,21.97] z[0,19.80].
- CONTEXTO E2 (fuera de vista): x[-4.04,73.04] y[-11.71,49.04] (bandas 1S/fundacion/piso1 + alero parte_2).
- Cámara E12 ya no incluye las bandas CONTEXTO en el auto-bounds.

## QA

- E2 OpenSees: applied=3023.097005 kN, sum_Rz=3023.097005 kN, residual=2.27e-12, **PASS**.
- E1: 21189.36 kN / 21189.36 kN, PASS (c0c0cdb intacto).
- TOTAL=24212.457005 kN, E1 max disp=0.018001 m, E2 max disp=0.00142895 m.
- `edificio2_opensees_analysis.json` (`55a3ba83…`), `edificio2_gravity.json` (`18a11329…`) y `edificio1_*` byte-idénticos a la entrega congelada.

## GEOMETRY TEST

`opensees/validate_e12_geometry.py` (endurecido con reglas forenses):

- Clasificación ESTRUCTURAL/CONTEXTO determinista (recalculada sobre el output, **OK**).
- Float plane: vigas/slabs = plano de piso; columnas = extremos de historia; muro = media historia; soporte = base; delta>0.10 m → error.
- Duplicados por span 3D completo (0), zero-length (0), NaN/Inf (0), z fuera de stack [0,19.8] (0).
- Resultado: **GEOMETRIA VISUAL: SIN ERRORES** → `results/E12_GEOMETRY_DIAGNOSTIC.md`.

## UNITY

- Cantidades E12 actualizadas: 164 losas, 1264 vigas, 274 columnas, 345 muros, 295 apoyos (las bandas CONTEXTO ya no se renderizan en "Both").
- Los registros CONTEXTO permanecen en el JSON (`elementos_contexto[]`) por si se necesita inspección/auditoría; no contaminan la cámara ni el inspector.
- Sincronizado y verificado por SHA256 a `E12_UNITY_FINAL_TEST/{results,opensees}` (10/10 MATCH). Validar en Windows con Play-test (pantalla no disponible en este entorno).

## VALIDATION

- `test_e2_e12_final.py` → OK.
- `validate_unity_quaternions.py` → OK (2 transforms, finitas, norma 1).
- `validate_unity_project.py` → OK (104/265/149/134/94/5/1) — E1 intacto.
- `validate_e12_unity_project.py` → OK (164/1264/274/345/295).
- `git diff --check` → limpio.
- Audit completo: `results/e12_floating_geometry_audit.json` + `results/E12_FLOATING_GEOMETRY_AUDIT.md`.