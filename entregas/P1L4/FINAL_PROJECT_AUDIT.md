# Auditoría final integral P1L4

Estado: `P1L4 STATUS: COMPLETE`

- Rama: `codex/p1l4-unity-integration`
- Tag evaluable: `P1L4_FINAL_AUDITED`
- Unity canónico: `entregas/P1L3/José/viewer_unity`
- Escena: `Assets/Main.unity`

Esta auditoría es de interpretación, contratos, visualización y trazabilidad.
No cambia geometría, apoyos, resultados OpenSees ni capacidad estructural.

## ERRORS_FOUND

| Error | Impacto | Evidencia | Solución | Archivo afectado | Commit |
| --- | --- | --- | --- | --- | --- |
| El diagrama unía directamente las acciones crudas i/j de OpenSees. | El signo de `j` corresponde a la cara opuesta; podía mostrar una inversión ficticia y pendientes incompatibles con el equilibrio interno. | En `E2-P1-V-056`, R entregaba My i=+846.089 y My j=-48.227 kN·m; `My_i + My_j - L·Vz_j = 0`. | Mantener crudos los valores del inspector, pero dibujar i=`end1`, j=`-end2` en convención común de cara interna. | `ViewerController.cs` | Incluido en `P1L4_FINAL_AUDITED`. |
| El rótulo no explicaba fuente, convención ni ausencia de carga interior. | Una recta podía interpretarse erróneamente como estaciones internas o como una curva exacta reconstruida. | Los JSON solo contienen fuerzas de extremos; no existen estaciones. | Mostrar `DATOS`, `REPRESENTACIÓN`, clasificación y carga interior en el gráfico. | `ViewerController.cs`, `CONTRACT.md` | Incluido en `P1L4_FINAL_AUDITED`. |
| Había dos modelos C# y dos loaders para `demanda_capacidad.json`. | Riesgo de desalineación futura y ambigüedad sobre el contrato de Luis. | `LoadDemandaCapacidad`/`DemandaCapacidadData` no tenían consumidores; `LoadDemandCapacity` sí. | Eliminar únicamente las clases y loader muertos; conservar el contrato activo y el JSON. | `JsonLoader.cs`, `JsonModels.cs` | Incluido en `P1L4_FINAL_AUDITED`. |
| `PROJECT_INDEX.md`, `PROJECT_HANDOFF.md` y la auditoría inicial aún presentaban PRE-P1L4 como estado vigente. | Una persona nueva podía abrir la rama incorrecta o asumir que P1L4 no estaba integrada. | Ramas y títulos obsoletos en cabecera. | Actualizar la cabecera vigente y conservar las secciones antiguas como historia explícita. | `PROJECT_INDEX.md`, `PROJECT_HANDOFF.md`, `P1L4_INTEGRATION_AUDIT.md` | Incluido en `P1L4_FINAL_AUDITED`. |
| La documentación podía sugerir que los crosswalk 1:N candidatos tenían resultados históricos navegables. | Riesgo de asociar resultados P1L3 a una segmentación FE que nunca fue ejecutada. | Hay 33 geometrías 1:N en el diagnóstico candidato, pero ninguna relación histórica 1:N seleccionable en `analysisByElementId`. | Declarar el 1:N como trazabilidad `CANDIDATE_NOT_RUN`; no transferir ni combinar resultados. | `README.md`, `FINAL_STATUS.md`, `CONTRACT.md`, smoke test | Incluido en `P1L4_FINAL_AUDITED`. |

## FIXED

1. Convención física común de cara interna aplicada a diagramas 2D y 3D para
   N, Vy, Vz, T, My y Mz. No se modificaron los resultados fuente.
2. Etiquetas visibles añadidas:
   `DATOS: fuerzas de extremos OpenSees` y
   `REPRESENTACIÓN: END_FORCES_INTERPOLATION`.
3. Auditoría reproducible creada en `audit_diagram_physics.py`; verifica 1312
   miembros en G/Q/EX/EY/R y el equilibrio manual de `E2-P1-V-056`.
4. Loader/modelo demanda-capacidad duplicado y no utilizado eliminado.
5. README, estado, contrato, índice y handoff sincronizados con el Unity actual.
6. QA automático ampliado para comprobar igualdad exacta entre la exportación
   de José y los casos históricos, unicidad de apoyos, física de diagramas y
   unicidad del loader demanda-capacidad.

## REMAINING_NOTES

Estas son limitaciones declaradas; no son errores ocultos ni bloquean la pauta
visual P1L4.

- Los cinco casos son `P1L3_ENTREGADO_HISTORICO`. Los 1312 registros de José
  coinciden exactamente con `analysis_cases.json`; no existe mezcla numérica,
  pero tampoco una corrida OpenSees post-consolidación P1L4.
- Geometría y resultados pertenecen a líneas temporales distintas: 156 IDs de
  geometría actual no tienen resultado histórico y 256 IDs históricos no están
  en la geometría actual. Unity muestra `N/A`; no remapea por proximidad.
- El FE post-P1L3 permanece `CANDIDATE_NOT_APPROVED_NOT_RUN`.
- Las 108 cargas del catálogo 700 son proyecto auditado y `NOT_APPLIED`: 90
  `READY_SPATIAL_NOT_APPLIED`, 6 posiciones puntuales no resueltas, 2
  `REVIEW_REQUIRED` y 10 `PP_LOSA` sin mapeo local de espesor. Unity dibuja solo
  las 82 superficies/líneas con geometría confirmada.
- Las tributarias visibles son históricas: 1060 paños y 491 áreas puntuales;
  192 no tienen polígono, 117 tienen área explícita cero y ninguna contiene
  `zone_contributions`. No se fabrica cobertura multizona ni huella faltante.
- El catálogo de material disponible es el material elástico global del modelo;
  no existe un catálogo material independiente por elemento.
- `E2-P4-V-050/051` continúan `UNRESOLVED_REAL`. El contexto físico no crea
  conexiones, apoyos ni terreno estructural.
- La armadura del muro `E2-P1-M-019` sigue `ASUMIDO_LAB`; los puntos
  `valid=false` quedan visibles para trazabilidad pero fuera de la envolvente.
- Al no existir cargas interiores de elemento ni estaciones exportadas, todos
  los gráficos se conservan bajo la clasificación prudente
  `END_FORCES_INTERPOLATION`. Un futuro modelo con `eleLoad` deberá usar
  `DIRECT_RESULT` o `RECONSTRUCTED_FROM_ELEMENT_LOADS` con fuente explícita.

## VERIFIED_OK

### Física de cargas y diagramas

- El pipeline ejecutado usa `ops.load`: G/Q transfieren `P/2` a nodos y EX/EY
  distribuyen fuerzas de piso a nodos. Búsqueda ejecutable: 0 `ops.eleLoad`.
- Para miembros sin carga interior: N/Vy/Vz/T constantes; My lineal ligado a
  Vz; Mz lineal ligado a Vy.
- `E2-P1-V-056`: L=4.709565 m, tag 10473, `A-V-0473`; x local casi global X y
  z local vertical. La gravedad dominante corresponde a Vz–My.
- Convención interna de My: +846.089 → +48.227 kN·m; Vz=-169.413 kN.
- Residual manual My y Mz: 0; residual máximo global: `1.862645149e-09` SI.
- Unidades visibles: N/V en kN, T/My/Mz en kN·m.

### Contratos, resultados y trazabilidad

- IDs de geometría, `analysis_id` y tags OpenSees únicos dentro de sus
  contratos; nodos de miembros existentes y coordenadas legibles.
- G/Q/EX/EY/R completos: 1312 miembros y 813 nodos por caso.
- Exportación de José idéntica componente por componente a los cinco casos
  históricos; estado histórico visible en Unity.
- Crosswalk 1:N candidato preservado para 33 geometrías como trazabilidad no
  ejecutada. No se asignan resultados históricos a esos segmentos.
- Selección y caso activo alimentan el mismo `analysis_id`/tag para inspector,
  deformada y diagrama.

### Apoyos, cargas, tributarias y contexto

- 106 apoyos, 106 nodos únicos y 106 posiciones únicas; UX/UY/UZ/RX/RY/RZ
  presentes y fijados según el snapshot.
- Catálogo 700 separado de cargas aplicadas mediante
  `AUDITADO_NOT_APPLIED`/`is_structurally_applied=false`.
- Cargas puntuales sin posición inequívoca no reciben símbolo inventado.
- Lados B/D, escaleras B/D, núcleo y elementos físicos auditados se conservan
  como contexto visual sin participación FE.

### Demanda-capacidad

- Columna `E2-P1-C-002`, tag 10009: CASE_R, eje My, 3 puntos válidos y 1
  inválido excluido; demanda y `inside_envelope` legibles.
- Muro `E2-P1-M-019`, tag 10171: CASE_R, eje Mz, 8 puntos válidos y 6
  inválidos excluidos; demanda, `inside_envelope` y `ASUMIDO_LAB` legibles.

### Pauta y ejecución

| Requisito | Estado |
| --- | --- |
| ID, nodos, sección, material | PASS |
| ejes locales, restricciones | PASS |
| N, Vy/Vz, T, My/Mz | PASS |
| deformada, diagramas 3D, gráficos 2D | PASS |
| áreas tributarias | PASS_WITH_NOTE |
| cargas | PASS_WITH_NOTE |
| apoyos | PASS |
| P-M columna/muro y demanda | PASS |
| combinación activa y trazabilidad | PASS |

Evidencia máquina-legible: `P1L4_INTEGRATION_QA.json` y
`DIAGRAM_PHYSICS_AUDIT.json`. La referencia original de Luis
`entregas/P1L2/unity_export/model_viewer.json` permanece intacta.

La ejecución final en Play seleccionó específicamente `E2-P1-V-056`, recorrió
G/Q/EX/EY/R, verificó ejes, deformada, los cinco diagramas, conversión de `j`,
clasificación visible, trazabilidad 1:N candidata, P-M de columna/muro y las
capas de cargas, apoyos y tributarias. Resultado: `PASS`, sin excepciones.
