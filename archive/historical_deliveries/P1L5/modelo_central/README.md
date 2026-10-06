# Modelo central P1L5

Esta carpeta es la fuente central para el estado CURRENT. Los
contratos históricos de P1L2/P1L3/P1L4 se conservan, pero nunca se usan como
fallback CURRENT. OpenSees CURRENT ya fue ejecutado y verificado; la última
evidencia está en `../../P1L6/wall_continuity/CURRENT_PIPELINE_QA.md`.

## Fuentes Editables Canonicas

Editar estas fuentes con evidencia, validación y trazabilidad:

- `model_master.json`: nodos geométricos, elementos, apoyos visuales, topología FE, restricciones, `section_id`, `material_id`, `active`, aliases y trazabilidad PRE5.
- `sections.json`: catalogo unico de secciones.
- `materials.json`: catalogo unico de materiales, separando propiedades elasticas y resistentes.
- `loads.json`: casos, catálogo, tributarias y aplicación CURRENT; pendientes explícitos no se rellenan.

Estas son las unicas fuentes editables del modelo central. No editar derivados
para modificar CURRENT.

## GENERATED

No editar manualmente:

- `generated/`: derivados de prueba creados por `build_central_derivatives.py`.
- `generated/` es regenerable, esta ignorado por Git y no forma parte del commit.
- Cualquier futuro contrato Unity/OpenSees producido desde estos JSON.
- `Assets/StreamingAssets/` es generado por los adaptadores CURRENT, no una fuente editable.

## RESULT

Resultados OpenSees son salidas de analisis. No son fuente editable del modelo.
Los resultados CURRENT están en `../analysis/results/current/` y son compatibles
con el modelo verificado. Los casos entregados P1L3/P1L4 siguen históricos.

## LEGACY / HISTORICAL

Se conservan por trazabilidad, pero no deben editarse para cambiar CURRENT:

- `entregas/P1L2/unity_export/model_viewer.json`: referencia historica de Luis.
- `entregas/P1L3/results/a3a4/analysis_model.json`: FE historico P1L3.
- `entregas/P1L3/results/a7/`: resultados historicos P1L3.
- `entregas/P1L4/Jose/resultados/`: export historico P1L4.

Caso explicito de trazabilidad: `E2-P1-M-019` es una referencia historica de
Semana 4/P1L4. En CURRENT PRE5 el muro activo correspondiente al `solidTag`
historico `SOL2_1_wall_0021` es `E2-P1-M-002`. `E2-P1-M-019` no debe aparecer
como elemento activo CURRENT ni crear un segundo muro fisico.

El pendiente histórico `E2-P4-V-009` fue revisado en correcciones posteriores.
El CURRENT validado tiene cero componentes sin camino a apoyo; esto no autoriza
inventar conectividad para futuras modificaciones.

## Flujo con reanalisis

```text
modelo_central
    -> adaptador OpenSees
    -> reanalisis cuando corresponda
    -> resultados
    -> adaptador Unity
    -> Unity
```

Requiere reanalisis cambiar seccion, material elastico, apoyo/restriccion,
activacion estructural, nodos, conectividad, cargas fisicas o areas tributarias.

## Flujo sin reanalisis

```text
modelo_central
    -> cambio solo de combinacion
    -> superposicion de resultados existentes compatibles
    -> Unity
```

No requiere reanalisis cambiar coeficientes de combinacion lineal de casos base ya
analizados y compatibles, mover sliders de superposicion o cambiar capas/filtros

Cambiar un coeficiente de superposicion de resultados existentes no equivale a
cambiar fisicamente la carga del modelo. Cambiar la carga fisica o su tributaria
si requiere reanalisis.

## Bootstrap

- `bootstrap_model_central.py`: construye la primera version de los cuatro JSON
  centrales desde las fuentes CURRENT PRE5.
- Es una herramienta de migracion inicial, no parte del flujo normal futuro.
- No usar para sobrescribir cambios manuales futuros en `model_master.json`,
  `sections.json`, `materials.json` o `loads.json`.

## Generador fail-closed

```text
model_master.json
sections.json
materials.json
loads.json
    -> build_central_derivatives.py
    -> OpenSees / Unity
```

- `build_central_derivatives.py` lee exclusivamente los cuatro canonical inputs.
- Escribe contratos regenerables en `generated/`, expande crosswalk 1:N y separa
  apoyos visuales de condiciones de borde FE.
- Si falta evidencia estructural, el derivado OpenSees queda `BLOCKED`; no usa
  resultados históricos ni valores por defecto ocultos.

## Validador

- `validate_central_model.py`: valida identidad, referencias, aliases y politica de cargas.

## Validar sin recalcular

Desde la raíz: `Proyecto.bat validar`. Para rutas: `Proyecto.bat rutas`.
Guía completa: [uso y cambios](../../../docs/GUIA_USO_Y_CAMBIOS.md).

## Flujo especializado P1L5 con reanálisis

Desde la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File entregas/P1L5/build_and_validate.ps1
```

Para incluir compilación de Unity:

```powershell
powershell -ExecutionPolicy Bypass -File entregas/P1L5/build_and_validate.ps1 -UnityCompile
```

Este flujo modifica fuentes y aplica solicitudes/supuestos P1L5, además de
reanálisis y preparación AR. Revisar su secuencia antes de usarlo; no es una
validación de solo lectura. Cerrar Unity antes de usar -UnityCompile.
