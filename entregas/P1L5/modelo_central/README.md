# Modelo central P1L5

Esta carpeta es la fuente central reversible para el estado POST-P1L4. Los
contratos históricos de P1L2/P1L3/P1L4 se conservan, pero nunca se usan como
fallback CURRENT. OpenSees permanece bloqueado hasta cerrar los gates indicados
por el generador y `../validation/INTEGRATION_QA.md`.

## Fuentes Editables Canonicas

Editar manualmente solo estos archivos cuando se migre el flujo de produccion:

- `model_master.json`: nodos geométricos, elementos, apoyos visuales, topología FE, restricciones, `section_id`, `material_id`, `active`, aliases y trazabilidad PRE5.
- `sections.json`: catalogo unico de secciones.
- `materials.json`: catalogo unico de materiales, separando propiedades elasticas y resistentes.
- `loads.json`: casos, catalogo de cargas, tributarias y estado `AUDITED_NOT_APPLIED` / `HISTORICAL`.

Estas son las unicas fuentes editables del modelo central. No editar derivados
para modificar CURRENT.

## GENERATED

No editar manualmente:

- `generated/`: derivados de prueba creados por `build_central_derivatives.py`.
- `generated/` es regenerable, esta ignorado por Git y no forma parte del commit.
- Cualquier futuro contrato Unity/OpenSees producido desde estos JSON.
- `Assets/StreamingAssets/` sigue siendo generado por los adaptadores existentes y no se toca en esta etapa.

## RESULT

Resultados OpenSees son salidas de analisis. No son fuente editable del modelo.
Los resultados actuales PRE5 son `NONE`; los casos `G/Q/EX/EY/R` disponibles hoy
son historicos.

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

Caso pendiente explicito: `E2-P4-V-009` permanece activo en CURRENT PRE5, pero
su trayectoria FE sigue pendiente. No se inventa conectividad, apoyo ni enlace
para forzar `PASS`; el pendiente queda documentado en `model_master.json`.

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

## Comando único

Desde la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File entregas/P1L5/build_and_validate.ps1
```

Para incluir compilación de Unity:

```powershell
powershell -ExecutionPolicy Bypass -File entregas/P1L5/build_and_validate.ps1 -UnityCompile
```

El comando falla ante errores de integridad, pero informa los bloqueos
estructurales honestos por separado.
