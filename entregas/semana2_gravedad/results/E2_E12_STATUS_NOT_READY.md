# E2/E12 STATUS — NOT READY (visual)

Fecha: 2026-09-05
Estado: **ESTE VIEWER E2/E12 NO ESTÁ TERMINADO VISUALMENTE.**

## Qué fue revertido

El intento de **"E12 FINAL COMPOSITION RECONCILIATION"** (clasificación por
elemento NEW / DUP / REAL / UNRES, transformación visual E1→E2 `T=(27.491,0)`,
suppression de `E2_DUPLICATE_OF_E1` en Both, manifest de composición y toggles
asociados) **fue revertido** porque empeoraba la vista Both en el viewer:
mostraba múltiples elementos dispersos/desconectados hacia la derecha.

Se volvió exclusivamente al estado visual inmediatamente anterior:

- `opensees/compose_e12_visual.py` eliminado (ya no es parte del pipeline).
- `opensees/final_e2_e12_pipeline.py`: sin `composition`, sin `reconcile`, sin flags.
- `transforms` en `edificios12_unity.json`: **identidad** para E1 y E2
  (E1 en coordenadas locales, E2 en coordenadas de proyecto).
- C# (`E1GravityModels.cs`, `E1ViewerController.cs`): sin DTO/toggles/gating de composición.
- Tests de composición retirados de `opensees/test_e2_e12_final.py`.
- JSON E2/E12 regenerados con el pipeline estable.

## SÍ validado

- E2 gravity (real, cerrado): 3023.097005 kN, PASS.
- E2 OpenSees: equilibrio PASS, análisis (`edificio2_opensees_analysis.json`
  hash `55a3ba83…`) validado.
- E1 preservation: 21189.36 kN, intacto respecto a c0c0cdb.
- Combined QA: 24212.457005 kN, residual ≈ 2e-12 kN, PASS.
- JSON/runtime: `source_plan` string normalizado, parse Linux/Windows PASS,
  JSON strict sin NaN.
- Loader E12: carga `edificios12_unity.json` y `edificios12_unity_response.json`.
- Panel: E12 Global / Controls, QA no-cero correcto.
- Building 1 / Building 2 / Both básico.
- Inspector E2: metadata FE, supports, reactions.
- Deformed shape verified 20x.
- Fix de support keys compuestas.
- Validators/tests: `test_e2_e12_final.py`, `validate_unity_quaternions.py`,
  `validate_unity_project.py`, `validate_e12_unity_project.py`.
- Clasificación forense ESTRUCTURAL/CONTEXTO y sus auditorías
  (`E12_SOURCE_COVERAGE_AUDIT.*`, `clasificacion_geometrica`, `elementos_contexto`)
  conservadas como documentación/auditoría; no se usa para ocultar/recomponer
  geometría mediante la lógica NEW/DUP/REAL.

## Pendiente (no resuelto)

- Composición visual E1/E2 definitiva.
- Reconciliación de geometría visual real (E1/E2 en un solo sitio coherente).
- Interface E1/E2 (UNRESOLVED_INTERFACE).
- Revisión de REAL_VISUAL_ONLY / CONTEXTO.

## Nota

No se seguirá iterando geometría tras este rollback. El viewer actual es
**imperfecto pero estable**: QA correcto, OpenSees correcto, datos reproducibles.