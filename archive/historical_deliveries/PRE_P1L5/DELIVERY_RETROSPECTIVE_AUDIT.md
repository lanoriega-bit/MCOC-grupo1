# Auditoría retrospectiva técnica P1L2 / P1L3 / P1L4

Fecha: 2026-09-22. No se reescribe ninguna entrega. Las correcciones pertenecen
a POST-P1L4/PRE-P1L5. Un método puede ser correcto y sus inputs estar superados.

## Identidad reproducible

| Entrega | Tag | Commit evaluable |
|---|---|---|
| P1L2 | entregap1l2 | d2e40be4292b2a55b2e0db8be6be51cd31535bd6 |
| P1L3 | P1L3_DELIVERED | c847c131512d00cc85bb95aa5719278d70da0c2b |
| P1L4 | P1L4_FINAL | 56e24ac0568b24eba3cf119f2e3cc66fc0af3a35 |

Los conteos de `project_state.json` provienen de los archivos en esos commits.
No adjudicar a P1L2 entregado cada defecto de un checkpoint intermedio posterior.
La transición ED2 100→54 muros corresponde a la consolidación de los modelos
posteriores, no necesariamente a los 927 sólidos del snapshot inicial de Luis.

## P1L2 — geometría y gravedad

| Componente | Evaluación | Qué rige hoy |
|---|---|---|
| Modelo CAD/viewer inicial | STILL_VALID como evidencia histórica | No es fuente CURRENT |
| Caras de muros/vigas contadas como miembros | ERROR_HISTORICAL donde consta en EXT-2/3 | Centrolineas y huellas físicas consolidadas |
| Muros ED2 100→54; vigas ED2 515→267 | IMPROVED_POST_DELIVERY | 122 muros y 567 vigas físicos entre ambos edificios |
| Columnas/ejes/calce | IMPROVED_POST_DELIVERY | 150 columnas, cinco pisos, ejes canónicos y residual de interfaz 0.009 m |
| C-016/C-017 de escalera B | STILL_VALID_GEOMETRY | Mantener 0.35×0.35; participación FE pendiente, no eliminar por omisión externa |
| Viga E1-P2-V-075 | IMPROVED_POST_DELIVERY | Descanso B 0.30×0.45 confirmado, camino FE pendiente |
| Núcleo E1-P4-M-007 | STILL_VALID tras reauditoría | Continuidad propia; no copiar fragmentación externa |
| Losas bounding boxes | SUPERSEDED como geometría definitiva | Diez proxies visuales; S1/P1 sin cierre aprobado; P4 piloto visual separado |
| Sectores outboard/cubierta | IMPROVED_POST_DELIVERY parcial | No confundir envolvente arquitectónica y miembro FE |
| Topografía/accesos/escaleras | IMPROVED_POST_DELIVERY visual | Contexto no métrico; no genera apoyos |
| Material UNKNOWN | IMPROVED_POST_DELIVERY parcial | 361 ED2 + 391 ED1 S1–P3 G35/A630-420H de notas primarias; ED1 P4/losas pendientes |
| Secciones | SUPERSEDED/PARTIAL | 19 alturas sin asignación resistente; no usar dimensión de proxy |
| Tributarias/gravedad | SUPERSEDED_INPUT | Método de conservación útil; áreas/cargas deben reconstruirse sobre geometría validada |

**P1L2_CORRECTED_CURRENT** es una vista conceptual del modelo canónico actual,
no otro archivo/copia del edificio ni una reentrega del tag antiguo.

## P1L3 — método frente a input

| Bloque | Clasificación | Fundamento / acción |
|---|---|---|
| Transferencia tributaria y conservación Q | STILL_VALID_METHOD | Sumar q_z A_iz; no rellenar UNMAPPED ni sumar dos veces OVERLAP |
| Q uniforme | VALID_AS_DELIVERED_ASSUMPTION + SUPERSEDED_INPUT | Ensayo del motor, no Q definitivo del edificio |
| G y PP.LOSA | SUPERSEDED_INPUT / NEEDS_RECALCULATION | Espesores, áreas netas y PM.ADIC todavía no cerrados |
| Cargas reales 700 | NEEDS_RECALCULATION, después de aprobación | Catálogo separado; puntuales/receptores/unidades pendientes no aplicados |
| Masa G+0.5Q | STILL_VALID_METHOD bajo el supuesto de laboratorio | Cambiará cuando cambien G/Q; coeficiente no se certifica aquí como norma universal |
| EX/EY | VALID_AS_DELIVERED_ASSUMPTION + NEEDS_RECALCULATION | Patrón y fuerzas corresponden a masas y FE histórico |
| R/superposición | STILL_VALID_METHOD | Linealidad y mismos K/apoyos/casos; no trasladar R al nuevo FE |
| FE histórico, 93 excluidos | SUPERSEDED_INPUT | Candidato actual 856 miembros, 43 residuales/22 componentes; no equivalencia 1:1 |
| Ejes/fuerzas históricas | VALID_AS_DELIVERED_ASSUMPTION | Nueva prueba: 1312 triadas y 6560 barra/casos PASS |
| Equilibrio global G | PASS_WITH_NOTE histórico, no cierre físico | El bundle declara déficit 0.763564%; no esconderlo con apoyos artificiales |
| Fiber, M-phi, P-M | STILL_VALID_METHOD / VALID_AS_DELIVERED_ASSUMPTION | Separado del FE, armaduras ASUMIDO_LAB; no capacidad confirmada de todo el edificio |

Equilibrio de extremo comprobado: ΣN=ΣVy=ΣVz=ΣT=0;
My_i+My_j+Vz_i L=0; Mz_i+Mz_j−Vy_i L=0. Unidades N, N·m, m.
El residual relativo máximo es 3.652e-16. No se ejecutó otra corrida.
Esto no valida rigidez, apoyos, cargas omitidas o valores de capacidad.

## P1L4 — visualización y compatibilidad

| Función | Clasificación | Tratamiento actual |
|---|---|---|
| Inspector identidad/nodos/sección | UI_ONLY_UPDATE / NEEDS_REINTEGRATION | Datos geométricos actuales separados de nodos FE candidatos y resultados antiguos |
| Material/ejes | UI_ONLY_UPDATE | f'c de plano separado del E histórico; ejes geométricos no presentados como FE nuevo |
| Deformada | DATASET_SUPERSEDED / NEEDS_RECALCULATION | Solo opt-in histórico; no activar automáticamente |
| N/V/T/My/Mz y gráficos 2D/3D | STILL_VALID como representación etiquetada; dataset histórico | DATOS: acciones de extremos; END_FORCES_INTERPOLATION no es corte interno exacto |
| Forma física con cargas nodales | STILL_VALID_METHOD | N/V/T constantes y momentos lineales en la convención de corte adecuada |
| Formas parabólicas | No justificadas para estos casos | No agregar si no hay cargas distribuidas reales sobre la barra |
| P-M/demanda | DATASET_SUPERSEDED / NEEDS_REINTEGRATION | Curva de sección con supuestos; demanda histórica, no compatible con CURRENT |
| Cargas/apoyos/tributarias | DATASET_SUPERSEDED parcial | Catálogo 700 visible NO APLICADO; apoyos FE/tributarias antiguas solo histórico |
| Trazabilidad/crosswalk | NEEDS_REINTEGRATION | Conservar geometry ID, candidato 1:N y tag del resultado histórico por separado |
| Contexto/presentación/filtros | UI_ONLY_UPDATE | Interfaz semántica, modo limpio y reset; contexto no participa FE |
| Entregas/evolución | UI_ONLY_UPDATE | Resumen por snapshot; no cuatro edificios superpuestos |

Interpolar acciones de extremos sin cambiar sus signos no equivale a un diagrama
de esfuerzos de corte. La etiqueta explicita la representación; para un futuro
diagrama interno exacto se debe fijar la convención y aplicar equilibrio con los
element loads reales del caso. No se fabrican parábolas por estética.

## Decisión PRE-P1L5 por componente

| Componente | P1L2 | P1L3 | P1L4 | Acción PRE-P1L5 |
|---|---|---|---|---|
| Geometría | Superada parcialmente | Input superado | Modelo de resultado histórico | UPDATE en CURRENT; no tocar tags |
| Propiedades | Incompletas | Supuestos del FE | Mostrar fuente/alcance | UPDATE parcial; completar 19 alturas/material ED1 |
| FE | Esqueleto preliminar | Modelo histórico | Crosswalk histórico | REBUILD solo después de aprobar conexiones/restricciones |
| Cargas | Gravedad preliminar | Q uniforme/inputs provisionales | Catálogo no aplicado | UPDATE cobertura/receptores/unidades; no calcular aún |
| Masas | No objetivo principal | G+0.5Q histórico | Informativo | RECALCULATE después de G/Q validados |
| Sismo | No objetivo principal | EX/EY histórico | Visual histórico | RECALCULATE después de masas/FE |
| Resultados y R | Histórico | Válidos bajo inputs de entrega | Históricos incompatibles | KEEP archivado + RECALCULATE futuro compatible |
| P-M | No objetivo principal | Supuestos HA | Demanda histórica | KEEP estudios; UPDATE inputs/RECALCULATE solo si cambian |
| Unity | Viewer inicial | Integración inicial | Postprocesador | UPDATE semántica/metadata; NEEDS_REINTEGRATION futuro |
| Documentación | Fuente histórica | Hipótesis/método | Demostración histórica | DOCUMENT_ONLY historia + UPDATE guía CURRENT |

No hay permiso implícito para que “RECALCULATE” ejecute un análisis en esta
etapa: es la decisión de preparación, condicionada por el cierre de inputs.
