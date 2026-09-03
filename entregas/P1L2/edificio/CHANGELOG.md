# CHANGELOG P1L2

## Base logica global del edificio

- Cambiada la metodologia: el Piso 1 queda como prototipo del flujo, no como etapa de aprobacion piso por piso.
- Congelado el modelo 3D actual; `unity_export/model_viewer.json` no se modifica durante la etapa de interpretacion global.
- Agregado `scripts/extract_building.py` como orquestador reutilizable para procesar todos los DXF disponibles.
- Agregado `datos/planos_index.json` como inventario maestro de planos.
- Agregado `datos/sistema_global.json` con origen, ejes, niveles y transformacion candidata parte_1/parte_2.
- Agregados `datos/fundacion.json`, `datos/piso_02.json`, `datos/piso_03.json` y actualizacion de `datos/piso_01.json` desde el flujo global.
- Agregado `datos/relaciones_verticales.json` para continuidad de columnas y muros entre niveles.
- Agregado `datos/building_master.json` como modelo logico consolidado previo al 3D.
- Agregado `issues/conflicts_global.json` con severidades `CRITICAL`, `HIGH`, `MEDIUM` y `LOW`.
- Agregado `issues/quality_global.md` con recomendacion global `AÚN NO LISTO PARA MODELADO 3D`.
- Agregadas validaciones por nivel en subcarpetas de `validacion/` y comparaciones en `validacion/comparacion_pisos/`.

## Piso 1

- Creado flujo inicial separado para extraccion, datos estructurados, validacion 2D y comparacion contra modelo existente.
- Agregada division `parte_1` (2017_67) y `parte_2` (2024_22/LT2) sin modificar automaticamente el modelo 3D final.
- Agregada comparacion inicial de elementos del piso 1 en `issues/conflicts.json`.
- Agregadas validaciones visuales superpuestas `piso_01_completo`, `piso_01_parte_1` y `piso_01_parte_2` en SVG y PNG.
- Agregados reportes separados para vigas, muros, columnas, calidad de extraccion y calce Parte 1/Parte 2.
