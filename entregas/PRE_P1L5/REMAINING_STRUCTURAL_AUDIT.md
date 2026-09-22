# EXT-7 / FE-2 — pendientes y evidencia primaria

Estado: REVIEW_REQUIRED. No se ejecuta OpenSees.

## Propiedades confirmadas

361 miembros RC de ED2 reciben G35_10 (fc=35 MPa) y A630-420H (fy=420 MPa),
por 2024_22-100, MTEXT 53994, desde fundaciones a cielo P4. Se conserva E/nu
histórico sin alteración: resistencia nominal no determina toda la rigidez ni la armadura.
Ed1 tiene G35 hasta cielo P3 en 2017_67-100 y G25 en detalles de 2017_67-600:
se registra la evidencia, pero no se propaga globalmente. Radier G20 no se copia a losas.
Se corrigió la búsqueda anterior: las notas sí existen. Render original en qa/material_*.png.

## Ocho muros: revisión uno por uno

Estos son ocho elementos con incidencias, no ocho pares independientes. Los pares
de pisos adyacentes no son duplicados de un mismo sólido. La clasificación es geométrica;
un encuentro L/T estructural necesita detalle de transferencia. No se conecta por cercanía.

| Elemento | Vecino | Distancia ejes m | Área intersección m² | Lectura | Decisión |
|---|---|---:|---:|---|---|
| E1-P1-M-004 | E1-S1-M-026 | 0.181300 | 0.048620 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P1-M-004 | E1-P2-M-007 | 0.181400 | 0.048358 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P1-M-010 | E1-S1-M-029 | 0.181300 | 0.059840 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P1-M-010 | E1-P2-M-008 | 0.181400 | 0.059518 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P1-M-010 | E1-P2-M-005 | 0.124900 | 0.000018 | NUMERICAL_CORNER_TOUCH_NOT_A_JOINT | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P2-M-003 | E1-P1-M-002 | 0.000100 | 0.324220 | PARALLEL_VERTICAL_CONTINUITY_AXIS_ROUNDING | FE_ADAPTER_ERROR_CANDIDATE_NOT_APPLIED |
| E1-P2-M-005 | E1-P1-M-010 | 0.124900 | 0.000018 | NUMERICAL_CORNER_TOUCH_NOT_A_JOINT | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P2-M-005 | E1-P1-M-026 | 0.000100 | 0.324220 | PARALLEL_VERTICAL_CONTINUITY_AXIS_ROUNDING | FE_ADAPTER_ERROR_CANDIDATE_NOT_APPLIED |
| E1-P2-M-007 | E1-P1-M-012 | 0.149900 | 0.000018 | NUMERICAL_CORNER_TOUCH_NOT_A_JOINT | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P2-M-007 | E1-P1-M-004 | 0.181400 | 0.048358 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P2-M-008 | E1-P1-M-010 | 0.181400 | 0.059518 | PARALLEL_OFFSET_VERTICAL_OVERLAP | NO_CONNECTION_WITHOUT_JUNCTION_DETAIL |
| E1-P2-M-009 | E1-P1-M-025 | 0.000100 | 0.590383 | PARALLEL_VERTICAL_CONTINUITY_AXIS_ROUNDING | FE_ADAPTER_ERROR_CANDIDATE_NOT_APPLIED |
| E1-P2-M-010 | E1-P1-M-012 | 0.000100 | 0.590383 | PARALLEL_VERTICAL_CONTINUITY_AXIS_ROUNDING | FE_ADAPTER_ERROR_CANDIDATE_NOT_APPLIED |

Cuatro continuidades paralelas difieren 0.1 mm: M-003/M-005/M-009/M-010 de P2.
Son candidatos claros de tolerancia del adaptador, no cambios de geometría.
No se promueven a soporte aprobado mientras los brazos rígidos y su extensión física sigan pendientes.
Las áreas minúsculas (<0.0001 m²) son contacto numérico de esquina, no unión probada.
No se eliminó ningún muro. Las incidencias ortogonales requieren distinguir L/T/transferencia
con detalle primario; no es riguroso adjudicar una T solo porque se tocan huellas.

## 19 alturas: todas conservadas sin valor inventado

Los tres labels próximos incluyen VAR en los 19 casos. Esto es una pista de búsqueda,
NO confirmación de que las 19 vigas sean variables. La revisión amplía a TEXT/MTEXT/atributos
y definiciones de bloques en 60 DXF. No asignar por vecino más próximo ni copiar A/I equivalentes externos.

| Viga | Fuente | Tres labels próximos | Decisión |
|---|---|---|---|
| E1-S1-V-014 | 2017_67-101.dxf | V.F. 20/220; V.F. 20/220; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-063 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; +V.I. 15/VAR. (2ºETAPA) | REVIEW_REQUIRED |
| E1-S1-V-070 | 2017_67-101.dxf | +V.I. 15/VAR. (2ºETAPA); V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-077 | 2017_67-101.dxf | V. 30/VAR.; V. 20/VAR; +V.I. 15/VAR. (2ºETAPA) | REVIEW_REQUIRED |
| E1-S1-V-050 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-072 | 2017_67-101.dxf | V. 20/VAR; V. 30/VAR.; +V.I. 15/VAR. (2ºETAPA) | REVIEW_REQUIRED |
| E1-S1-V-071 | 2017_67-101.dxf | V. 20/VAR; V. 30/VAR.; +V.I. 15/VAR. (2ºETAPA) | REVIEW_REQUIRED |
| E1-S1-V-079 | 2017_67-101.dxf | V. 30/VAR.; V. 20/VAR; +V.I. 15/VAR. (2ºETAPA) | REVIEW_REQUIRED |
| E1-S1-V-010 | 2017_67-101.dxf | V. 60/80; V. 20/VAR; V.F. 20/120 | REVIEW_REQUIRED |
| E1-S1-V-042 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-051 | 2017_67-101.dxf | V. 20/VAR; V.F. 20/120; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-073 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 30/VAR. | REVIEW_REQUIRED |
| E1-S1-V-057 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-056 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-058 | 2017_67-101.dxf | V. 20/VAR; V.F. 20/120; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-065 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-064 | 2017_67-101.dxf | V. 20/VAR; +V.I. 15/VAR. (2ºETAPA); V. 20/VAR | REVIEW_REQUIRED |
| E1-S1-V-066 | 2017_67-101.dxf | V. 20/VAR; V. 20/VAR; V. 20/VAR | REVIEW_REQUIRED |
| E1-P2-V-069 | 2017_67-102.dxf | V. 60/VAR; V. 30/45; V. 60/80 | REVIEW_REQUIRED |

## 43 pendientes FE agrupados

| Edificio | Piso | Tipo | Causa | Cantidad |
|---|---|---|---|---:|
| EDIFICIO_1 | P1 | beam | ED1_OUTBOARD_BEAM_SUPPORT_REVIEW | 3 |
| EDIFICIO_1 | P1 | column | EXTERIOR_STAIR_SUPPORT_FE_SCOPE | 2 |
| EDIFICIO_1 | P1 | wall | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 2 |
| EDIFICIO_1 | P1 | wall | WALL_SUPPORT_PATH_REVIEW | 11 |
| EDIFICIO_1 | P2 | beam | CONFIRMED_LANDING_BEAM_FE_SCOPE | 2 |
| EDIFICIO_1 | P2 | wall | WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST | 6 |
| EDIFICIO_1 | P3 | wall | WALL_SUPPORT_PATH_REVIEW | 6 |
| EDIFICIO_1 | P4 | wall | WALL_SUPPORT_PATH_REVIEW | 6 |
| EDIFICIO_2 | P4 | beam | ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW | 5 |

| ID | Clasificación | Fuente | Acción |
|---|---|---|---|
| E1-P1-C-016 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-C-017 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-004 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-010 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-016 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-020 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-021 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-022 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-023 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-024 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-031 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-034 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-035 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-036 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-M-037 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-V-068 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-V-072 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P1-V-098 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-101.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-003 | FE_ADAPTER_ERROR (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-005 | FE_ADAPTER_ERROR (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-007 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-008 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-009 | FE_ADAPTER_ERROR (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-M-010 | FE_ADAPTER_ERROR (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-V-055 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P2-V-075 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-003 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-005 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-007 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-008 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-009 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P3-M-010 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-102.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-003 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-007 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-008 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-009 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-010 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E1-P4-M-012 | UNRESOLVED_REAL (diagnóstico candidato) | 2017_67-103.dxf | Mantener; no apoyo ficticio |
| E2-P4-V-004 | UNRESOLVED_REAL (diagnóstico candidato) | 2024_22-102.dxf | Mantener; no apoyo ficticio |
| E2-P4-V-005 | UNRESOLVED_REAL (diagnóstico candidato) | 2024_22-102.dxf | Mantener; no apoyo ficticio |
| E2-P4-V-006 | UNRESOLVED_REAL (diagnóstico candidato) | 2024_22-102.dxf | Mantener; no apoyo ficticio |
| E2-P4-V-007 | UNRESOLVED_REAL (diagnóstico candidato) | 2024_22-102.dxf | Mantener; no apoyo ficticio |
| E2-P4-V-009 | UNRESOLVED_REAL (diagnóstico candidato) | 2024_22-102.dxf | Mantener; no apoyo ficticio |

## FE-2: propuesta cinemática separada

1482 restricciones → 946 enlaces estrella dentro de los mismos componentes.
Ensayo de seis movimientos base: residual máximo 3.55e-15; PASS algebraico.
No se cambió el candidato ni se resolvió el sistema. No añade aristas entre componentes.
La equivalencia presupone brazos rígidos completos y pequeñas rotaciones; no prueba su extensión física.
Clusters con varios apoyos requieren tratamiento SP coherente. No copiar directamente a Transformation.
Referencia: [rigidLink](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidLink.html)
y [Transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/constraint/TransformationMethod.html).

## Losas S1/P1 y huecos

Se conserva EXT-4: S1=UNRESOLVED_OUTER_PERIMETER; P1=UNRESOLVED_OUTBOARD_TRANSITION.
Las regiones manuales y huecos de Cáceres no cambian en el snapshot nuevo; Santiago aporta paños,
no una prueba métrica de esos límites. No hubo nueva confirmación primaria para cerrar bordes.
La resta explícita de vacíos y balance bruto/neto se adopta como criterio de QA futuro, no como geometría.
No se extrajeron cotas de fotos ni se clasificaron loops automáticamente como huecos.

## Alcance y bloqueos reales

Esta relectura textual no equivale a identificar visualmente cada leader/corte/armadura de 60 láminas.
No afirmar que se agotó toda la información de los originales. Faltan asociaciones inequívocas
de perfiles variables, alcance material ED1, detalles de encuentros/transferencia y contornos S1/P1.
Ningún miembro eliminado/añadido/movido. 43 residuales, 22 componentes y 856 miembros se mantienen.
Las fuentes insuficientes se dejan explícitas; no se certifica aptitud resistente para P1L5.
