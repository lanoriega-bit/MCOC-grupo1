# Auditoría de integración P1L4

Fecha: 2026-09-14  
Rama de trabajo: `codex/p1l4-unity-integration`  
`PRE_P1L4_CONSOLIDATED_BASELINE`: `aa6bc4b7a207dde4ddac2f3deef1eee54e042f5f`

## Preservación

- El tag `P1L3_DELIVERED` y sus resultados históricos no se modifican.
- La geometría consolidada sigue en `entregas/P1L2/unity_export/model_combined_viewer.json`.
- El único Unity activo sigue en `entregas/P1L3/José/viewer_unity`.
- El diagnóstico FE post-P1L3 continúa identificado como candidato no ejecutado.
- `entregas/P1L2/unity_export/model_viewer.json`, referencia original de Luis, permanece intacto.
- Los viewers web y snapshots antiguos continúan como historia/legacy.

## Matriz de requisitos

| Requisito P1L4 | Estado al iniciar | Evidencia existente | Fuente de datos / pendiente |
| --- | --- | --- | --- |
| Selección e ID | YA EXISTE | Raycast, búsqueda y resaltado en `ViewerController.cs` | `model_viewer.json` |
| Edificio, piso y tipo | YA EXISTE | Inspector vigente | `model_viewer.json` |
| `elementTag`, `analysis_id`, nodos | PARCIAL | Resultados P1L3 y diagnóstico muestran la relación | A7 + `post_p1l3_fe_diagnostic.json`; falta ordenar el inspector P1L4 |
| Sección y material | PARCIAL | Dimensiones visuales y material genérico disponibles | `analysis_model.json` contiene sección FE; no existe catálogo material por elemento |
| Ejes locales | PARCIAL | Se conserva `orient` y la regla `vecxz` en el pipeline | Falta contrato explícito y dibujo x/y/z sobre el elemento |
| Restricciones | FALTA EN UI | 106 apoyos, todos con vector de fijación en el modelo entregado | `analysis_model.json/supports` |
| N, Vy, Vz, T, My, Mz | YA EXISTE/PARCIAL | Fuerzas locales de extremo visibles para el primer mapeo | A7 G/Q/EX/EY/R; falta presentar ambos extremos y crosswalk 1:N sin sobrescritura |
| Selector de caso | YA EXISTE | G, Q, EX, EY y R | `analysis_cases.json`; botones estaban dentro del panel P1L3 |
| Caso activo siempre visible | FALTA | — | Añadir encabezado P1L4 permanente |
| Deformada real | PARCIAL | EX/EY usa nodos y desplazamientos OpenSees | A7; está precalculada solo para EX/EY y no sigue cualquier caso activo |
| Factor de amplificación | PARCIAL | Factor automático EX/EY se informa | Falta control único editable y volver a escala 1/geometría original |
| Diagrama de momento | FALTA | Existen fuerzas My/Mz en extremos | Representación lineal entre extremos, declarada como visualización, no resultado distribuido exacto |
| Diagrama axial/corte | FALTA | Existen N/Vy/Vz en extremos | Mismo criterio de representación explícita |
| Cargas | PARCIAL | Tributarias y sismo histórico visibles | Falta contrato unificado surface/line/point y distinguir aplicado/no aplicado |
| Áreas tributarias | YA EXISTE/PARCIAL | 1060 áreas y 491 áreas puntuales seleccionables | Contrato P1L3 histórico; falta listar receptores múltiples y estado de fuente |
| Apoyos | PARCIAL | Geometría de apoyos visible | Falta símbolo/leyenda y UX/UY/UZ/RX/RY/RZ en inspector |
| Demanda-capacidad columna | DATOS LISTOS, UI FALTA | `E2-P1-C-002`, tag 10009, CASE_R | Contrato de Luis `demanda_capacidad.json` |
| Demanda-capacidad muro | DATOS LISTOS, UI FALTA | `E2-P1-M-019`, tag 10171, CASE_R | Armadura `ASUMIDO_LAB`; puntos inválidos no forman envolvente |
| Curva P-M y punto de demanda | FALTA EN UI | Curvas y punto existen en JSON | Dibujar solo puntos `valid=true`; conservar inválidos para trazabilidad |
| Trazabilidad visual | PARCIAL | Crosswalk 1:N y fuentes en contratos | Falta sección dedicada y cadena completa capacidad/resultados |
| Modo diagnóstico separado | PARCIAL | Controles existen y funcionan | Debe pasar a modo secundario frente a RESULTADOS |
| QA P1L4 | FALTA | QA P1L3 de visibilidad/diagnóstico | Crear validación de contratos y smoke test P1L4 |

## Integración de Luis

- Rama revisada: `origin/luis-semana4-demanda-capacidad`.
- Commit fuente: `8c933f4b3e87626fb837ff103bd38c7f0e315163`.
- El commit añade nueve archivos bajo `entregas/P1L4/demanda_capacidad`; no reemplaza archivos de Unity, geometría ni resultados históricos.
- Cherry-pick aplicado limpiamente como `60353c6`.
- `build_demanda_capacidad.py` se ejecutó nuevamente y reprodujo el JSON sin diferencias.
- Validaciones: tags 10009/10171 únicos, IDs y nodos coincidentes, seis componentes locales presentes y puntos fallidos/parciales excluidos mediante `valid=false`.

## Estado de José

Después de `git fetch --all --prune`, no existe una rama P1L4 nueva de José.
La referencia remota más reciente de su trabajo sigue siendo `origin/jose-viewer`
(`295d780`, 2026-09-09), anterior a la consolidación. No se fusiona esa rama.

Los únicos resultados estructurales completos disponibles para consumo son los
históricos P1L3 bajo `entregas/P1L3/results/a7`. Se pueden integrar y etiquetar
como históricos, pero no presentarlos como un recálculo P1L4.

## Datos realmente faltantes

1. Salida P1L4 de José posterior a la geometría/conectividad consolidada.
2. Catálogo definitivo de materiales por elemento.
3. Cargas P1L4 aplicadas y tipificadas; el catálogo 700 vigente sigue `NOT_APPLIED`.
4. Resultados OpenSees de la topología post-P1L3 candidata, que aún no está aprobada ni ejecutada.
5. Resultados distribuidos internos. Mientras solo existan fuerzas de extremos, los diagramas deben declararse interpolaciones gráficas.

Nada de lo anterior impide construir el loader, inspector, selectores y gráficos
contra los contratos existentes, siempre que el estado histórico quede visible.

