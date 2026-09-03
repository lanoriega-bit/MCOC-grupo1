# Resumen técnico: `extract_building.py`

> Pipeline de re-extracción del edificio. Convierte los planos DXF estructurales en un modelo lógico JSON (`building_master.json`) listo para el modelado 3D y el análisis (OpenSees/Unity). No modifica el modelo 3D final.

## 1. Propósito
Orquestador del pipeline. Toma los **planos CAD estructurales (DXF)** de un edificio real y produce un **modelo lógico completo en JSON**: muros, vigas, columnas, losas, fundaciones y ejes de cada piso, unidos en un modelo global.

## 2. Dependencias
- `ezdxf` → **lee** archivos DXF.
- `matplotlib` → genera **imágenes de validación** (PNG/SVG).
- `extract_piso_01.py` (= `core`) → módulo base con las funciones de bajo nivel de extracción (segmentos, agrupación de columnas, escritura JSON, niveles).

## 3. Series de planos (¿por qué dos?)
- **`2017_67`** → **Parte 1** (`DXF_2017_DIR`)
- **`2024_22`** → **Parte 2 / LT2** (`DXF_2024_DIR`)

Están dibujadas con escalas, orígenes y desplazamientos de viewport distintos → primero se **calibran** (solo traslación) y se unen en un sistema de coordenadas único.

## 4. Estructura clave: `SheetSpec` (línea 44)
Catálogo de cada lámina DXF:
- `source_key` / `dxf_name` / `codigo` → identificación.
- `piso` → planta (`fundacion`, `1`, `2`, `3`).
- `sector` → `parte_1` / `parte_2`.
- `disciplina` = `"estructura"`, `tipo_lamina` = `"planta"`/`"cargas"`, `extraer_planta` (bool).
- **Geometría de mapeo**: `bbox_cm`, `origin_cm`, `global_offset_m` → coordenadas CAD (cm) → coordenadas reales (m).

`SHEETS` (línea 62): inventario de 12 láminas declaradas manualmente.

## 5. Flujo del `main()` (línea 1230)
```
1. ensure_building_dirs()        – crea carpetas
2. respaldo del modelo 3D        – model_viewer_backup_576f014.json
3. calibrate_sheet_transforms()  – alinea láminas (traslación)
4. build_plan_index()            – índice de láminas → planos_index.json
5. for cada piso: process_floor()– extrae y agrupa elementos por piso
6. build_system_global()         – calce global (Parte 1 vs 2) → sistema_global.json
7. build_vertical_relations()    – continuidad vertical entre pisos
8. build_global_conflicts()      – conflictos por severidad
9. build_master()                – building_master.json (resultado maestro)
10. write_global_validation()    – imágenes SVG/PNG
```

## 6. Funciones importantes
- **`calibrate_sheet_transforms` (118)**: usa las **columnas** como patrón para estimar la traslación que alinea cada lámina al origen global. Solo traslación (sin rotación/escala).
- **`build_plan_index` (271)**: lista las láminas → `planos_index.json`.
- **`process_floor` (324)**: agrupa segmentos del DXF en entidades lógicas; añade espesor de muros (`estimate_wall_thickness`), soporte y evidencia por etiquetas de texto.
- **`build_system_global` (595) + `_fit_affine` (657) + `_resid_stats` (646)**: ajuste afín sobre puntos de control para cuadrar Parte 1 y Parte 2 → `sistema_global.json`.
- **`build_vertical_relations` (770)**: conecta columnas/muros/vigas que continúan entre pisos; `relation_continuity` (858) etiqueta continuidad.
- **`build_global_conflicts` (869)**: detecta incoherencias y las clasifica por severidad: `critical`, `medium`, `low`.
- **`build_master` (1111)**: empaqueta todo → `building_master.json`; `recommendation` (1137) devuelve `LISTO PARA MODELADO 3D`.
- **`write_floor_comparisons` (975) / `write_global_validation` (987)**: generan SVG/PNG de validación visual.

## 7. Resultados (JSON de salida)
| Archivo | Contenido |
|---|---|
| `building_master.json` | Modelo maestro completo (3255 elementos, 6 niveles) |
| `piso_01.json` | Piso 1 re-extraído (489 elementos) |
| `sistema_global.json` | Calce global confirmado humanamente |
| `niveles.json` | Elevaciones de los 6 niveles |
| `planos_index.json` | Índice de láminas |
| `conflicts_global.json` | Conflictos por severidad |

## 8. Datos clave
- **6 niveles**: fundacion(0), 1S(3.96), 1(7.92), 2(11.88), 3(15.84), 4(19.8) m; offset Z = 7.97 m.
- **3255 elementos**: 603 muros, 388 perimetro_losa, 314 fundaciones, 1251 vigas, 142 columnas, 395 ejes gráficos, 162 vanos.
- **Recomendación**: `LISTO PARA MODELADO 3D`.
- **Calce**: traslación de Parte 1 en +27.491 m en X para unir con Parte 2/LT2.

## 9. Limitación para correr
Para ejecutar el script se necesitan los **planos DXF** (entrada `*.dxf`), que **no están en el repositorio** ni en la máquina local. Los resultados actuales ya fueron generados por los compañeros y están en `main` (carpeta `entregas/P1L2/edificio/datos/`).
