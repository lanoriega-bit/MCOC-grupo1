# Semana 7 — auditoría técnica de preparación

Fecha: 2026-10-01. Alcance: modelo, datos, análisis, capacidad, Viewer y contrato para AR. **Auditoría de solo lectura, salvo este informe.** No se modificaron modelos, scripts, resultados, referencias, tags ni ramas; no se ejecutó un reanálisis ni se construyó un producto. No se abrió una nueva sesión Play durante esta auditoría.

## A. Resumen ejecutivo

**WEEK 7 MODEL READY: NOT YET — PARTIAL.** El CURRENT es funcional y tiene resultados compatibles, pero no debe congelarse como producto final todavía.

Versión estructural más completa comprobada: `codex/current-slab-reconstruction`, commit `3cc21d613377f295880974a62fe98c48c9eea50f`, sincronizado con su rama remota. Working tree limpio al comenzar. Al terminar, la única incorporación prevista es este informe sin commit. `origin/main` está ocho commits detrás; clonar main no entrega las últimas losas y UX.

Resultados principales:

- 679 elementos físicos: 442 vigas, 143 columnas, 84 muros y 10 losas; 33 apoyos visuales, 712 sólidos en Unity. 669 elementos estructurales con capacidad de screening.
- Validador central ejecutado hoy: PASS, sin errores ni advertencias. Pipeline CURRENT comprobado hoy en memoria, bloqueando sus escrituras: 15 comprobaciones, ninguna fallida; `PASS_WITH_EXPLICIT_NOTES`.
- FE: 677 segmentos candidatos; 673 analizados después de omitir cuatro segmentos redundantes dentro de clusters rígidos; 1170 nodos de topología, 1165 nodos en la corrida, 44 apoyos retenidos. Cero componentes sin camino a apoyo según QA CURRENT. Los 33 apoyos visuales no son el conteo de restricciones FE.
- G/Q/EX/EY guardados tienen PASS de equilibrio y valores finitos. No se recalcularon hoy.
- **Defecto localizado:** `G_total_N` por piso se calcula antes de agregar la carga lineal permanente de P4. EX/EY consumen ese total sin actualizar. El peso sísmico aplicado queda aproximadamente 2,2657 MN por debajo del G + 0,5Q global. Equilibrio PASS no detecta una carga omitida en la generación.
- **Handoff AR desactualizado:** dataset y overlay de septiembre contienen 658 elementos, frente a 712 sólidos actuales. Las pruebas de transformación pasan, pero no certifican vigencia del dataset completo.
- Hay Fiber Sections y M–φ reales históricos. **CURRENT usa capacidades analíticas aproximadas, no curvas Fiber.** No confundir ambos productos.
- La modificación estructural desde Unity sí está programada: solicitud de cambio de Q/sección y pipeline externo OpenSees en Windows. Falta demostrar el ciclo completo con el CURRENT final, incluida recarga de geometría, cargas y capacidad.
- Existe ejecutable desktop local, pero es del 21 de septiembre: no certifica este CURRENT. No se encontró APK local en Builds ni ejecutable versionado.

### Ramas y divergencias

Se actualizó el inventario remoto con fetch. Los números siguientes son commits exclusivos de HEAD/remoto, no cantidades de funcionalidades.

| Referencia remota | Commit | HEAD / remoto | Diagnóstico |
|---|---|---:|---|
| main; codex/main-current-organization | d3ee850 | 8 / 0 | Antecesoras; les faltan ocho commits actuales |
| codex/p1l6-current-cleanup-and-walls | ba889a7 | 17 / 0 | Incluida por ascendencia |
| codex/p1l6-wall-continuity-correction | d041da0 | 9 / 0 | Incluida por ascendencia |
| codex/unity-visual-ux | 21aa110 | 3 / 0 | Incluida por ascendencia |
| codex/current-slab-reconstruction | 3cc21d6 | 0 / 0 | CURRENT estructural más completo |
| p1l6/final-integration | 800160e | 29 / 2 | Divergente: informe Semana 6 y cambio de Viewer/build |
| p1l6/ar-tracking | 00c1243 | 50 / 3 | Commits de tracking no incluidos por ascendencia; revisar equivalencia y probar integración AR |
| p1l6/ar-transform-data | 198b64d | 44 / 1 | Commit no incluido por ascendencia, pero archivos ya incorporados casi íntegramente |

En `transform`, la comparación contra `ar-transform-data` solo presenta diferencias en `element_query.py`: **no es una funcionalidad enteramente ausente**. No decidir integración por hash únicamente. La rama final incluye `0e6b23b`, que propone losas ON por defecto y build PC; el CURRENT aprobado inicia losas OFF. No fusionar ese cambio a ciegas. El informe `reports/semana06.md` de José necesita revisión de cifras y contexto antes de incorporarlo a un informe final.

## B. Matriz de implementación Semana 7, puntos 2–18

PASS significa implementado, verificable, reproducible y compatible con CURRENT dentro de su alcance declarado. PARTIAL incluye funcionalidades que existen pero necesitan validación final, actualización de inputs o una limitación no resuelta. La matriz evalúa el requisito completo, no solo la existencia de archivos.

| Punto | Estado | Evidencia | Falta para cierre | Prioridad |
|---|---|---|---|---|
| 2 Edificio e idealización | PASS | AGENTS.md; run_current_opensees.py; assumptions en resultados | Incorporar al informe final la idealización, no venderla como diseño normativo | P2 |
| 3 Geometría y datos | PARTIAL | model_master.json; validador central PASS; QA losas | Certificar perímetros físicos pendientes; separar propiedad inferida de confirmada | P1 |
| 4 Gravedad y tributarias | PARTIAL | current_tributary_loads.json; conservación G/Q; QA receptores | Totales por piso, cargas especiales excluidas y exteriores sin certificación completa | P0/P1 |
| 5 Q | PARTIAL | Q por elemento, QA Unity 29/29, qQ/A/b/wQ | Resolver o declarar formalmente tres llamadas puntuales excluidas; aprobación de inputs finales | P1 |
| 6 Sismo pseudoestático | PARTIAL | run_current_opensees.py; EX/EY y sus seismic_floor_loads | Corregir agregado permanente por piso; justificar centro/nodo y excentricidad | P0 |
| 7 Superposición | PARTIAL | combinación lineal Unity; checks λQ 0/1/2; ejemplo R | Test explícito CURRENT de combinación arbitraria, desplazamiento/reacción/fuerza y signos | P1 |
| 8 Análisis global y QA | PARTIAL | cuatro casos PASS, conectividad y contrato | Regenerar casos afectados por defecto de peso; cerrar benchmark y reproducibilidad | P0/P1 |
| 9 Fiber Sections | PARTIAL | sección columna P1L3 y muro P1L4 con comandos Fiber reales | Seleccionar estudios defendibles y vincularlos a CURRENT o identificarlos como estudios separados | P1 |
| 10 M–φ | PARTIAL | moment_curvature.py y CSV real, ensayo P=0 | Reproducción controlada en entorno congelado y sección/hipótesis identificadas en Semana 7 | P1 |
| 11 P–M columna/muro | PARTIAL | CSV Fiber históricos; curvas screening CURRENT | No mezclar algoritmos; invalidaciones de convergencia y vínculo a sección vigente | P1 |
| 12 Demanda-capacidad | PARTIAL | 669/669 registros; evaluator y curvas My/Mz | Tracción vs compresión; supuestos; envolvente no concurrente; evidencia real vs screening | P1 |
| 13 Unity pre/postprocesador | PARTIAL | ViewerP1L5.cs; solicitudes y pipeline; inspector | Prueba completa de edición, reanálisis y recarga; documentar limitación Windows/repo | P1 |
| 14 Capas y diagramas | PARTIAL | QA visual 83/83; seis componentes; QA Q/losas | Capas sin datos deliberadas; ejes CAD no visibles; validación final sobre nuevo build | P1 |
| 15 Modificación del modelo | PARTIAL | SET_Q_SCALE/SET_SECTION; ReanalyseP1L5 | Demostración real no solo prueba de adaptadores; comprobar estado y datos después de recarga | P1 |
| 16 Datos para AR | PARTIAL | contrato, element_query y tests 20/20 | Dataset/overlay de 658 elementos obsoletos; actualizar y validar identidad/longitud/resultados | P0 |
| 17 Sidequests | PASS | funcionalidades concretas enumeradas en G | Contribuciones individuales y límites en informe, sin marketing | P2 |
| 18 QA/tests | PARTIAL | inventario y pruebas diferenciadas abajo | Runner reproducible, ensayo final de modificación/superposición/build; resolver hallazgos | P1 |

### Geometría, propiedades y losas

Fuente única: `entregas/P1L5/modelo_central/{model_master,sections,materials,loads}.json`. No editar derivados como fuente.

| Métrica | CURRENT comprobado |
|---|---:|
| Elementos físicos / nodos centrales | 679 / 1298 |
| Vigas / columnas / muros / losas | 442 / 143 / 84 / 10 |
| Secciones registradas / materiales registrados | 30 / 4 |
| IDs físicos duplicados | 0, validador central |
| Referencias FE activas / aliases históricos | 677 / 74 |
| Segmentos analizados / nodos analizados | 673 / 1165 |
| Nodos de topología / apoyos FE | 1170 / 44 |
| Restricciones FE registradas, incluyendo vínculos | 1240; no confundir con 44 nodos apoyados |
| Componentes FE sin apoyo | 0, pipeline CURRENT |
| Losas sin material confirmado | 10 MAT_UNKNOWN, no FE |
| Miembros ED1/P4 con material inferido | 85, nota explícita pipeline |
| Cargas puntuales sin receptor | 6 registros, tres llamadas físicas |

Los 669 miembros tienen material asignado: 263 con la ficha 2017 y 406 con la ficha 2024. Asignado no equivale a confirmado por plano para cada piso: permanece el fallback de 85 miembros ED1/P4. Losas excluidas del FE; su material UNKNOWN no implica que se haya modelado hormigón de rigidez cero.

Las cinco familias rectangulares de viga tienen dimensiones positivas y procedencia CAD/texto: 2 de 0,20×0,90; 25 de 0,30×0,80; 4 de 0,40×0,60; 20 de 0,40×0,80; 391 de 0,60×0,80 m. La última cifra incluye decisiones anteriores; no es una certificación independiente de las 391 alturas. El antiguo contador de 19 alturas pendientes no debe reutilizarse como contador CURRENT sin reconstruir su trazabilidad. Trece fichas de sección de muro declaran longitud derivada de geometría; no son trece ensayos independientes de capacidad.

Hay metadatos de elemento/ref que conservan `CURRENT_GEOMETRY_NOT_RUN` aunque el manifiesto global y el contrato compatibles están analizados: corregir esa contradicción de estado antes del handoff, no interpretar esas etiquetas locales como ausencia de todos los resultados. La continuidad y conectividad numérica son verificables; no certifican que todo apoyo o voladizo sea físicamente correcto.

Losas: diez superficies poligonales, no bounding boxes activas; 40 paños de carga y 45 componentes visuales. QA guardado: cero receptores huérfanos, cero IDs duplicados de paño, cero solapes de carga y cero triángulos degenerados. Los huecos se preservan. Fuera del modelo físico y de las cargas permanecen el sector sur ED1-S1 aprobado y las extensiones norte/sur ED1-P1 retiradas.

| Losa | Área física m² | Huecos |
|---|---:|---:|
| ED1 S1 | 160,763996 | 2 |
| ED1 P1 | 825,770177 | 1 |
| ED1 P2 | 843,913976 | 2 |
| ED1 P3 | 956,720753 | 3 |
| ED1 P4 | 934,561129 | 0 |
| ED2 S1/P1/P2/P3, cada piso | 557,894266 | 1 |
| ED2 P4 | 535,619974 | 6 |

**Certificación física: REVIEW_REQUIRED**, declarada por `SLAB_CLEANUP_QA.json`. El polígono visual y el de carga ya no deben confundirse; parte de la reconstrucción aún procede de zonas de carga y necesita contraste primario. La prueba de malla no certifica el perímetro arquitectónico. El diagnóstico de área fuera de convex hull estructural sigue siendo no nulo (aprox. 28,89–94,26 m² en ED1 según piso y 29,63/30,27 m² en ED2). Puede incluir voladizos válidos: no eliminarlo automáticamente, pero **no se ha demostrado “0 polígonos exteriores injustificados”**. Revisión primaria por sector pendiente.

### Cargas, Q y defecto del peso sísmico

`build_current_loads.py` calcula peso propio por sección × longitud × densidad × g, y transfiere cargas de superficie a las vigas activas mediante una grilla de 0,50 m de viga más cercana. Es una aproximación tributaria, no una solución exacta de placa ni una reconstrucción analítica universal a 45°. Conservación numérica no certifica el método de reparto.

| Total CURRENT | N |
|---|---:|
| G peso propio de miembros | 36.839.559,851 |
| G adicional incluyendo losas | 41.876.499,483 |
| G total generado | 78.716.059,334 |
| Q total generado | 22.637.353,432 |
| G + 0,5Q global | 90.034.736,050 |
| Peso usado por EX/EY | ≈87.769.016,5625 |
| Fuerza lateral aplicada, por dirección | ≈17.553.803,3125 |

La ligera diferencia generado/transferido de G por redondeo nodal (0,029 N) es distinta del defecto de 2,2657 MN por piso. Catálogo aplicado: 78 entradas CURRENT_RECONSTRUCTED, 2 RESOLVED_BY_REVIEW, 2 RESOLVED_BY_REVIEW_SLAB_ROUTE, 10 HISTORICAL_FALLBACK; seis entradas UNRESOLVED excluidas y cero conflictos de unidad activos según contrato. No interpretar exclusión como carga física nula.

Los seis registros corresponden a SC/PM_ADIC para las llamadas P2 7000 y P3 6000/6700 kgf; falta receptor inequívoco. Peso propio de losa usa espesor 0,15 m HISTORICAL_FALLBACK. Deben figurar como inputs provisionales/aprobaciones, no como propiedades confirmadas.

Q por elemento: `current_loads_by_element.json`, `Q = Σq_z A_z`; intensidad equivalente `qQ=Q/A`, ancho `b_eq=A/L`, `wQ=Q/L=qQ*b_eq`. Convertir N→kN solo al mostrar. Un paño multizona no obliga a dividir el sólido. **λQ=1** representa el caso Q base actual con escala de intensidad del contrato 1,0; no significa 1 kN/m² ni una carga nueva. λQ es combinación de resultados; modificar la intensidad Q base sí requiere reanálisis.

Ejemplo guardado E1-P1-V-002: qQ=4,1239468 kN/m², A=21,230775 m², b=2,589119 m, wQ=10,677389 kN/m, Q=87,554587 kN. QA Unity verifica tres vigas y λQ=0/1/2, fuerzas de doce extremos y coherencia q/A/b/w.

**Diagnóstico del agregado sísmico:** en `build_current_loads.py`, primero se asigna `G_total_N` por piso, después se suma a `G_superimposed_N` la carga `L700-P4-LINE-SC-800-PM_ADIC_LINE`. Esta última agrega 2.265.719,520 N a ED1/P4, pero no recalcula `G_total_N`. En P4 aparece G_total=10.188.283,905 N, aunque peso propio + adicional + losa suma ≈12.454.003,424 N. La diferencia global concuerda con esa carga, salvo redondeo. `run_current_opensees.py` toma el total atrasado para `0,20*(G+0,5Q)`.

No se corrigió aquí. Debe actualizarse la generación y repetirse EX/EY, combinación/demanda y contrato. No incrementar cifras manualmente en resultados ni “calibrar” a ETABS.

El sismo actual aplica +X en EX y +Y en EY, una fuerza por edificio/piso, en el nodo estructural retenido más cercano al **promedio geométrico de nodos del grupo**. No es el centro de masa calculado por ponderación de cargas; tampoco incluye el par de transporte de la fuerza desde ese centro. Registra centro objetivo, posición y offset. No hay distribución modal/por altura normativa ni diafragma rígido de piso; la fórmula de porcentaje de g se simplifica a porcentaje de peso. El capítulo puede describir exactamente esta implementación, pero necesita justificar la simplificación y la torsión inducida, no llamarla NCh433 completa.

### Resultados y superposición

| Caso | Máxima traslación m | Residual relativo de equilibrio |
|---|---:|---:|
| G | 0,0110394280 | 1,1358e-15 |
| Q | 0,0023763790 | 3,2913e-16 |
| EX | 0,0661980346 | 1,8675e-14 |
| EY | 0,0962320486 | 5,6875e-14 |

Listos como métricas de la corrida fechada 2026-10-01, **no como cifras finales después de corregir el agregado sísmico**. Resultados exportan desplazamientos, reacciones, fuerzas locales de extremos y bases de identidad; Unity combina G/Q/EX/EY sin ejecutar OpenSees al mover λ. Ejemplo QA R=G+0,5Q: My de E1-P2-V-041 = 402,9943379167455 kN·m.

El manifiesto escribe `linear_superposition_compatible=true` a partir del PASS de casos; ese flag no sustituye una corrida explícita arbitraria. Hay verificación histórica P1L3 y tests Unity de escala, pero no se acreditó una nueva prueba completa CURRENT de λ arbitrarios contra OpenSees explícito en esta auditoría. Agregar también prueba de signos de extremos, reacción y desplazamiento. Comparación ETABS disponible es de orden de magnitud: modelos LT1/LT2 separados con diafragmas, frente a marco combinado sin losas FE. No tratar coincidencia de períodos o Q como calibración certificada.

## C. Bloqueadores para los compañeros

| Bloqueador | Responsable/fuente | Requisito afectado | Resolución mínima |
|---|---|---|---|
| Handoff AR de 658 elementos obsoleto | Modelo/datos; preparación y transform | Identidad, geometría, resultados para AR | Regenerar desde 712 sólidos y contrato vigente; QA longitudes, tags 1:N, capacidad y signos |
| Peso sísmico incompleto por agregado de carga lineal G | Modelo/análisis; build_current_loads | EX/EY/R y demanda de AR/informe | Corregir agregado, validar suma por piso/global y regenerar derivados afectados |
| main no contiene últimos ocho commits | Integración del grupo | Clone y fuente común | Integrar hito aprobado después de QA; sin force push ni alterar entregas históricas |
| Ejecutable local antiguo | Viewer/build | Demo independiente del Editor | Nuevo build con manifiesto, datos y hash final; smoke test en otra carpeta/PC |
| Capacidades CURRENT no son curvas Fiber | Capacidad + redacción técnica | Defensa P-M/Mphi/D-C | Explicar screening y presentar estudios Fiber reproducibles con vínculo de sección explícito |

AR físico/trackeo es responsabilidad del equipo AR y no se certificó aquí. Las transformaciones matemáticas 20/20 pasan para muestras existentes; no convierten el dataset obsoleto en vigente. La validación AR guardada además declara tags OpenSees no únicos, 30 discrepancias de longitud y 615 registros con P de demanda cero: debe reevaluarse con reglas correctas de 1:N y demanda firmada, no ignorarse porque el título diga READY.

| Campo del handoff | Implementación encontrada | Estado de entrega |
|---|---|---|
| elementTag / element_id / solidTag | Cadena de identidad en current_ar_elements y element_query | Existe, cobertura antigua; regenerar |
| OpenSees tag(s) | Referencias por segmento y crosswalk | Existe; validar 1:N, no imponer un tag físico único a todo sólido |
| start/end/center y orientación | Overlay y query en modelo/Unity/AR | Existe, pero overlay antiguo; validar contra geometría vigente |
| Sección y material | Dataset/query y fichas canónicas | Existe; preservar UNKNOWN e inferencias sin rellenar |
| Resultados N/V/T/My/Mz y desplazamientos | Query y contrato de resultados | Existe; demanda/envolvente antigua necesita actualización |
| Capacidad y D/C | Consulta de p1l6_current_capacity y evaluator | Screening disponible; no garantiza demanda compatible con dataset AR antiguo |
| Transformación | [x,y,z] → [x,z,-y] y transformación de anchor/calibración | 20 tests matemáticos PASS; calibración/pose física fuera de esta auditoría |

No falta simplemente agregar un nuevo nombre de campo: el bloqueo es **vigencia y coherencia entre archivos que ya existen**. La ausencia de resultados para losas/apoyos visuales debe declararse como no aplicable, no inventar tags o fuerzas.

## D. Trabajo pendiente del responsable del modelo

### P0 — bloquea congelar datos/producto

1. Corregir G por piso después de cargas lineales; test de suma por piso = G global y de peso sísmico = G + 0,5Q según la convención adoptada. Reanalizar y no editar JSON de resultados manualmente.
2. Regenerar handoff AR y overlay; ninguna identidad eliminada debe sobrevivir; compatibilidad por hashes de geometría, resultados y capacidad.
3. Elegir una fuente final común y preparar build desktop CURRENT verificable. main aún no es la rama más completa.
4. Fijar entorno reproducible: el pipeline prefiere `.venv-p1l5`, cuyo OpenSeesPy 3.8.0.0 no coincide con requirements 3.7.1.2. Registrar versión usada para cada resultado y repetir QA bajo la versión final.

### P1 — necesario para defensa técnica

1. Cerrar o aceptar explícitamente cargas puntuales excluidas, espesor de losas, materiales inferidos y certificación de perímetros. No bloquear por exigir datos imposibles: acordar límites defendibles sin inventar.
2. Ensayo CURRENT de superposición explícita, signos/unidades y ejemplo manual de equilibrio de viga.
3. Ensayo de modificación real en copia controlada: sección o Q → STALE → pipeline → resultados nuevos → Viewer/capacidad/cargas recargados, restauración sin alterar historia.
4. Separar Fiber/Mphi/P-M históricos de screening CURRENT; documentar sección, acero asumido, eje y puntos inválidos. Revisar tracción vs compresión de D/C y demandas concurrentes.
5. Comprobar con fuentes primarias sectores de losa fuera de huella; no confundir convex hull con borde físico válido.
6. QA compile/Play y standalone final con selector de caso, seis fuerzas, diagramas, cargas, apoyos, tributarias, P-M y fallo cerrado.

### P2 — documentación/orden

1. README con comandos y versiones exactas; corregir textos obsoletos de P1L6 que aún hablan de preparación no implementada.
2. Crear `reports/final.md`: resumen, limitaciones, uso de IA, contribuciones individuales y Honors Track solo si aplica. No existe ese archivo versionado actualmente.
3. Uniformar metadatos locales `CURRENT_GEOMETRY_NOT_RUN` vs manifiesto analizado; registrar origen de cada decisión, no borrar historial.
4. Integrar texto Semana 6 y revisar cambios externos de tracking/build por funcionalidad, no por coincidencia de hashes.

## E. Diagnóstico separado Fiber / M–φ / P–M / D-C

### E1. Fiber real — implementado, no confundido con modelo global

Columna: `entregas/P1L3/capacidad_ha/opensees/section_model.py`, configuración `datos/seccion_estudio.json`. Sección 0,70×0,70 m, 12 barras Ø25 mm, recubrimiento 0,04 m; 28×28=784 fibras de hormigón y fibras discretas de acero. Usa `ops.section('Fiber',...)`, `patch('rect',...)`, `fiber(...)`, Concrete01 y Steel01. fc=35 MPa, fy=420 MPa, Es=200 GPa, endurecimiento b=0; hormigón sin tracción y sin confinamiento específico. Hormigón de patch bruto sin descontar explícitamente el acero: simplificación a declarar.

Muro: `entregas/P1L4/demanda_capacidad/opensees/wall_section_model.py`, `datos/wall_section_estudio.json`. Estudio histórico E2-P1-M-019, 5,80×0,22 m; recubrimiento 0,02 m, dos cortinas verticales Ø16 a separación nominal 0,20 m; 80×8=640 fibras de hormigón, barras repartidas para no exceder esa separación. Armadura/modelos constitutivos ASUMIDO_LAB. Misma familia Concrete01/Steel01. Eje declarado Mz, flexión fuerte del estudio. **El ID histórico E2-P1-M-019 no está como elemento activo en model_master actual**; no asignar esa curva a un muro CURRENT por semejanza de nombre.

Modelo global: elasticBeamColumn 3D, secciones/inercia lineales; **no usa Fiber para esos 673 segmentos globales**. Los ensayos no lineales de sección son análisis separados, consistente con arquitectura del proyecto. Los estudios reales existen, por eso no se clasifican MISSING; falta su incorporación defendible a la entrega actual.

### E2. M–φ real

`P1L3/capacidad_ha/opensees/moment_curvature.py`: ensayo zeroLengthSection 2D, axial impuesto, momento unitario y DisplacementControl en rotación; para longitud nula de sección la rotación controlada se interpreta como curvatura. φ en 1/m, momento del factor de carga en N·m, exportado kN·m.

CSV `results/moment_curvature.csv`; estudio P=0, 240 pasos convergentes, objetivo aproximadamente 6φy (φy≈0,00705882 1/m). Pico guardado: 766,076309 kN·m a φ=0,03105882 1/m. QA dentro del script verifica convergencia, finitud, incremento de curvatura y respuesta; `fiber_section_qa.py` verifica sección/materiales/refuerzo. No se reran hoy por implicar generación de outputs.

No afirmar que el gráfico P-M de CURRENT es este gráfico M-φ: no lo es. La curva M-φ debe mostrarse/documentarse como estudio de sección con sus hipótesis y versión de entorno.

### E3. P–M real histórico

Columna: `pm_interaction.py` repite ensayo de curvatura a niveles de P y ensaya compresión pura; `results/pm_interaction.csv` contiene:

| Punto | Compresión kN | M máximo kN·m | Validez guardada |
|---|---:|---:|---|
| P=0 | 0 | 766,0763 | PASS 240 pasos |
| P25 | 4873,0633 | 1696,4508 | PASS 240 pasos |
| P50 | 9746,1267 | 1650,0714 | PARTIAL, falla paso 237, 236 convergentes |
| Compresión pura | 19492,2534 | 0 | AXIAL_ONLY_PASS |

No presentar P50 como corrida totalmente convergente. Cuatro puntos no son una curva exhaustiva ni certifican una envolvente normativa. P tiene signo negativo en compresión en esos CSV.

Muro: `wall_pm_interaction.py` ejecuta ensayos Fiber; `results/wall_pm_interaction.csv` tiene 14 registros: siete flexiones PASS hasta razón P=0,30, seis INVALID por convergencia parcial entre 0,40–0,90 y un AXIAL_ONLY_PASS. Son ocho registros válidos incluyendo compresión pura, no catorce puntos válidos. Pico P=0: 13148,9736 kN·m; compresión pura: 49466,2661 kN. La línea directa desde P30 a compresión pura es una interpolación entre extremos verificados, **no la validación de los seis intervalos no convergentes**.

### E4. P–M y demanda-capacidad CURRENT

`entregas/P1L5/analysis/build_current_capacity.py` no ejecuta OpenSees Fiber. Calcula momento nominal con bloque rectangular y curvas de screening:

`Pn = 0,65*(0,80fc*(Ag-Ast)+fy*Ast)`; `M(P)=M0*sqrt(1-r^1,7)`, seis razones de compresión 0/0,25/0,50/0,75/0,95/1 por eje My/Mz. Refuerzo longitudinal asumido: viga ρ=0,008, columna 0,015, muro 0,0025; recubrimiento 0,05 m. Vigas también tienen corte aproximado y reducciones académicas. 33 firmas de configuración no equivalen a 33 ensayos Fiber.

| Tipo | Total | Capacidad screening | Sin capacidad de screening | APPROX/ASSUMED |
|---|---:|---:|---:|---:|
| Viga | 442 | 442 flexión/corte | 0 | 442 |
| Columna | 143 | 143 P-M por eje | 0 | 143 |
| Muro | 84 | 84 P-M por eje | 0 | 84 |
| Losa | 10 | 0, fuera de alcance FE | 10, no aplicable | — |

No hay 669 capacidades confirmadas por armadura real: las 669 son `APPROX_ASSUMED_FOR_LAB`. No se exporta un conteo separado REVIEW_REQUIRED que sustituya esa advertencia. D/C default R: vigas 392 controladas por My, 8 Mz y 42 Vz; columnas+muros 154 por My y 73 por Mz. Recalcular esa clasificación al cambiar λ; no es una propiedad permanente del miembro.

Demanda se obtiene primero superponiendo resultados firmados y después tomando máximos absolutos de componentes sobre segmentos/extremos. Puede combinar P y M que **no son concurrentes en una misma sección**. El código y `StructuralFailureEvaluator.cs` usan |N| para consultar compresión: no distinguen tracción real de compresión mediante una convención de corte validada. Esto no es defendible como chequeo de tracción ni interacción biaxial completa; requiere prueba de signos y tratamiento explícito. Para vigas no se afirma capacidad axial ni torsional; para columnas/muros el screening disponible es P-M, no chequeo completo de corte/torsión.

Los sliders actualizan demanda y D/C; mapa OK/WARNING/EXCEEDED usa 0,80/1,00 y gris sin datos. “Falla” es excedencia de screening; daño visual no redistribuye esfuerzos ni cambia rigidez. No es colapso físico ni análisis post-falla.

## F. Reproducibilidad y QA/tests

### Versiones verificadas

| Componente | Estado real |
|---|---|
| Python local | 3.12.14, Windows x64, ambos entornos inspeccionados |
| `.venv-p1l5` preferido por pipeline | OpenSeesPy/openseespywin 3.8.0.0; NumPy 2.5.3; Shapely 2.1.2 |
| `.venv` y requirements | OpenSeesPy 3.7.1.2; matplotlib 3.10.5; ezdxf 1.4.4; Shapely 2.1.2 |
| Unity | 6000.6.0f1; revisión f7f8ed4d1e24 |
| Paquetes Unity directos | ARFoundation/ARCore 6.6.2; UGUI 2.6.0; Multiplayer Center 2.0.1 |

Dependencias transitivas Unity están en packages-lock.json. No hay entorno único certificado para reproducir todas las figuras y análisis. El manifiesto de resultados no registra versiones Python/OpenSees: el entorno instalado es evidencia local, no prueba absoluta del binario que produjo cada CSV histórico. README dice Python 3.10+, insuficiente como versión evaluable exacta.

### Usuario nuevo clona

| Paso | Estado | Hallazgo |
|---|---|---|
| Clone y selección | PARTIAL | main no es último CURRENT; debe indicar rama/hash final |
| Python/dependencias | PARTIAL | requirements existe; versión usada y pipeline preferido difieren |
| Instalación OpenSees | PARTIAL | pip resuelve dependencia, falta congelar plataforma/versión real |
| Generación CURRENT | PARTIAL | build_and_validate.ps1 existe; no documentado claramente como único pipeline final |
| G/Q/EX/EY | PARTIAL | run_current_opensees.py produce resultados, defecto de agregado pendiente |
| R/datasets | PARTIAL | R es combinación en cliente, no quinto caso explícito; export y AR requieren orden |
| Tests | PARTIAL | scripts dispersos, no runner que diferencie históricos/CURRENT y efectos de escritura |
| Abrir proyecto/Viewer | PASS | guía y Abrir Unity; proyecto José/viewer_unity, Assets/Main.unity, Play/Game |
| Build desktop | PARTIAL | builder implementado, build local desactualizado y sin paquete final |
| Build móvil | PARTIAL | AndroidBuilder existe; licencia/SDK/ARCore y prueba física pendientes del equipo AR |
| Outputs | PARTIAL | contratos/config/guía dan rutas, documentos P1L6 y branch principal no uniformados |

`main.py estado` y `rutas` son read-only; `validar` produce QA. `build_and_validate.ps1` **modifica fuentes**: aplica solicitud, suposiciones y topología, genera cargas, ejecuta OpenSees y exporta. No ejecutarlo como “inspección inocua”. Previamente revisar solicitud pendiente y pipeline de la rama final.

Secuencia implementada: apply_modification_request → apply_p1l5_assumptions → rebuild_central_fe_topology → validate_central_model → build_central_derivatives → build_current_loads → validate → run_current_opensees → export_current_to_unity → build_current_capacity → build_ar_dataset → QA. El pipeline no incluye todos los exportadores de identidad/material de desktop ni build_geometry_overlay/QA transform; un solo éxito del script no garantiza handoff completo actualizado.

### Pruebas ejecutadas en esta auditoría

Comandos desde raíz, usando `.venv-p1l5\Scripts\python.exe -B`:

- `entregas/P1L5/modelo_central/validate_central_model.py`: PASS, cero errores/advertencias; invariantes internos, no número artificial de tests independientes.
- `-m unittest tools/test_project_entrypoint.py -v`: **10 PASS, 0 FAIL, 0 SKIP**.
- `entregas/P1L6/transform/test_ar_transform.py`: **20 PASS, 0 FAIL**, pero muestras del dataset antiguo; no cobertura CURRENT completa.
- `main.py estado`: identidad rápida PASS, seis registros excluidos informados.
- `validate_current_pipeline.py`: invocado en memoria con `Path.write_text` interceptado para impedir archivos nuevos; **15 checks sin fallos**, PASS_WITH_EXPLICIT_NOTES. No volvió a ejecutar OpenSees ni Unity.

### Evidencia guardada, no rerun hoy

| Suite/artefacto | Conteo | Resultado almacenado | Alcance |
|---|---:|---|---|
| current_cleanup/CURRENT_PIPELINE_QA | 15 checks | PASS_WITH_EXPLICIT_NOTES | JSON/identidad/equilibrio, no Play |
| slab_reconstruction/SLAB_CLEANUP_QA | 24 checks | PASS | Malla/cargas/exclusiones; certificación física REVIEW_REQUIRED |
| slab_reconstruction/P1_LATERAL_QA | 8 checks | PASS | Exclusiones laterales y equilibrio |
| p1_lateral_qa/UNITY_VISUAL_RUNTIME_QA | 83 checks | PASS | Runtime visual CURRENT guardado |
| p1_lateral_qa/UNITY_SLAB_QA | 44 checks | PASS | Losas/cargas/huecos guardado |
| p1_lateral_qa/UNITY_Q_QA | 29 checks | PASS | Intensidad y fuerzas λQ de tres vigas |
| G/Q/EX/EY | 4 casos | PASS | Finitud/equilibrio de inputs actuales, no corrección sísmica pendiente |
| Columna Fiber P-M | 4 registros | 2 PASS + 1 PARTIAL + 1 AXIAL_ONLY_PASS | Estudio histórico |
| Muro Fiber P-M | 14 registros | 7 PASS + 6 INVALID + 1 AXIAL_ONLY_PASS | Estudio histórico |
| AR_DATASET_VALIDATION | No denominador único | Checks mixtos, discrepancias | Dataset anterior, no aceptación CURRENT |

**No sumar estos conteos**: se solapan, mezclan invariantes, casos, registros de curvas y tests runtime. Suites no ejecutadas aquí se consideran SKIP_THIS_AUDIT por alcance read-only, no `unittest.skip`, ni FAIL por ausencia de una ejecución nueva. No existe un total global de casos únicos deduplicado ni una certificación de todas las suites históricas sobre CURRENT.

### Inventario de scripts de test/validación versionados

Inventario por nombres del repositorio: 40 candidatos, de los cuales tres no son suites (promote_validated_walls y dos record_*). Quedan **37 scripts de test/validación/QA nominales**, además de checks embebidos en análisis y C#. No todos consumen CURRENT y algunos escriben reportes o regeneran inputs. Comando individual: `python -B <ruta>`; para el archivo unittest usar el comando indicado arriba. Ejecutar los históricos solo en una copia de su entrega, no para “arreglar” CURRENT.

| Directorio relativo | Scripts nominales; ejecución de esta auditoría |
|---|---|
| entregas/P1L2/edificio/scripts | phase7_validate_3d; validate_axes_and_calce; validate_combined_geometry; validate_core_axis_continuity; validate_ed1_beam_proposal; validate_ed1_beams; validate_ed1_walls; validate_golden_in_combined; validate_luis_reference_diff — SKIP_THIS_AUDIT |
| entregas/P1L3/capacidad_ha/opensees | fiber_section_qa — SKIP_THIS_AUDIT; sección histórica |
| entregas/P1L3/gravedad | qa_verificaciones — SKIP_THIS_AUDIT |
| entregas/P1L3/scripts | validate_unity_integration — SKIP_THIS_AUDIT |
| entregas/P1L4/unity_integration | validate_p1l4_integration — SKIP_THIS_AUDIT |
| entregas/P1L5/modelo_central/Jose | qa_dinamico_p1l1_p1l4; qa_tributario — SKIP_THIS_AUDIT |
| entregas/P1L5/modelo_central | validate_central_model — PASS hoy |
| entregas/P1L5/validation | test_single_source_propagation; validate_current_loads_and_results; validate_e2_p4_zone_completion; validate_final_beam_geometry_review — SKIP_THIS_AUDIT |
| entregas/P1L6/current_cleanup | validate_current_pipeline — PASS con notas, memoria; validate_supported_wall_pipeline; validate_wall_candidate — SKIP_THIS_AUDIT |
| entregas/P1L6/preparation | validate_readiness — SKIP_THIS_AUDIT |
| entregas/P1L6/slab_reconstruction | validate_p1_lateral; validate_slab_cleanup — evidencia guardada, SKIP_THIS_AUDIT |
| entregas/P1L6/transform | test_ar_transform — 20 PASS hoy; validate_ar_dataset — SKIP_THIS_AUDIT, reporte obsoleto inspeccionado |
| entregas/P1L6/visual_ux | validate_visual_scope — SKIP_THIS_AUDIT |
| entregas/P1L6/wall_continuity | validate_corrected_cores — SKIP_THIS_AUDIT |
| entregas/POST_P1L4/scripts | validate_ed2_beams; validate_ed2_walls; validate_ext5_remaining — SKIP_THIS_AUDIT |
| entregas/PRE_P1L5/scripts | validate_current_readiness; validate_fe_pending_review; validate_pre5 — SKIP_THIS_AUDIT |
| tools | test_project_entrypoint — 10 PASS hoy |

Todos los nombres anteriores terminan en `.py`. `record_second_cleanup_unity_qa.py` y `record_user_review_unity_qa.py` registran evidencia; `promote_validated_walls.py` promueve geometría: no contarlos como tests ni ejecutarlos en esta auditoría.

Checks adicionales identificados: los scripts moment_curvature/pm_interaction/wall_pm_interaction verifican sus propios ensayos; `audit_integrated_model.py` genera auditoría integrada; builders/exportadores verifican sus contratos. Unity contiene `ViewerReviewQA`, `ViewerVisualQA`, `ViewerSlabQA`, `ViewerWallContinuityQA` y `P1L6AR/ARPrototypeSelfCheck`. Son self-checks propios, no una suite Unity Test Runner certificada. Los comandos/flags de runtime deben fijarse en la guía final; consultar scripts y artefactos citados, no sumar carpetas de snapshots históricos.

`test_single_source_propagation.py` modifica una sección en memoria y comprueba los adaptadores Unity/FE sin escribir fuentes. El resultado OpenSees que acompaña se toma de una corrida separada: **no demuestra un reanálisis de la sección modificada**. Esa es precisamente la prueba end-to-end que falta.

## G. Unity, producto y sidequests

Proyecto canónico: `entregas/P1L3/José/viewer_unity`; escena `Assets/Main.unity`. Estado normal: CURRENT, caso R, λG=1/λQ=0,5/λEX=λEY=0; nodos ON, losas OFF. No abrir `P1L6_AR_Final` para demostrar el Viewer desktop; aquella escena depende de subsistemas AR y puede mostrar STALE/NO DATA en Editor.

### Preprocesamiento real vs postprocesamiento

Visual: pisos/tipos, opacidad, cámara, materiales visuales, daño ilustrativo; no cambian estructura. Combinación: sliders λ modifican demanda/resultados combinados instantáneamente, no inputs del análisis. Preprocesamiento implementado: `ViewerP1L5.cs` guarda solicitudes SET_Q_SCALE y SET_SECTION; Q base 0,5–2,0 por control, sección de destino fija para viga/columna. `apply_modification_request.py` también soporta MOVE_START por API/archivo, no demostrado como control general de la interfaz.

**Sí existe botón REANALIZAR** que invoca PowerShell/OpenSees desde el Editor/PC con repositorio. No es disponible como análisis en teléfono ni como ejecutable portátil autónomo sin repo/Python. La rutina recarga casos y metadata, pero no demuestra por sí sola regeneración de sólidos ni recarga completa de capacidad/cargas/identidad tras cambio de sección. Debe validarse antes de afirmar que el circuito pre/post está terminado. No se probó modificando fuentes hoy.

### Cobertura de capas

| Capa | Estado/interpretación |
|---|---|
| Apoyos | Visual PASS, 33 sólidos; restricciones FE: 44 apoyos, contrato distinto |
| G/Q | Datos CURRENT y ficha por elemento; QA Q guardado PASS; inputs con fallbacks |
| EX/EY | Fuerzas nodales y visualización disponibles; PARTIAL por peso sísmico detectado |
| Tributarias | Paños CURRENT compatibles, cero huérfanos; reparto aproximado y borde físico pendiente |
| Especiales lineales | Cargas resueltas/strip en CURRENT; conservar método/receptor, no activarlas dos veces |
| Puntuales | NO DATA/aplicación pendiente para tres llamadas, seis registros excluidos |
| Ejes globales/locales | Disponibles; locales y fuerzas por segmento FE, no por numeración CAD |
| Ejes estructurales | Descripción por ejes en ficha/procedencia; no confundirla con overlay completo CAD |
| Ejes CAD | Segmentos CAD no construidos como capas en Viewer actual; fuentes conservadas para auditoría |
| N/Vy/Vz/T/My/Mz | Fuerzas de extremos y diagramas 3D/2D implementados, END_FORCES_INTERPOLATION |
| P-M/D-C | Screening CURRENT compatible, no curva Fiber histórica aplicada automáticamente |

NO DATA esperado: cargas puntuales sin receptor; capacidad N/T de viga; capacidad de losa/apoyo; cualquier resultado/capacidad de elemento no FE; curvas Fiber particulares no vinculadas a miembro CURRENT; catálogo histórico no aplicable automáticamente. “Ninguna carga especial asociada” no equivale a inexistencia física certificada. Datos incompatibles deben fallar cerrado, no volver a histórico.

Diagramas: OpenSees recibe `ops.load` en nodos, incluidas tributarias y cargas lineales equivalentes; no hay `eleLoad` en la corrida CURRENT. Por segmento prismático sin cargas repartidas internas, N/Vy/Vz/T son constantes y My/Mz lineales entre secciones, usando una convención de corte consistente. La implementación interpola datos de extremos para las seis componentes; la conversión de signos entre fuerzas de nodo y diagrama interno debe verificarse, no llamar “exacto” a dos vectores crudos interpolados. No fabricar parábolas porque las cargas originales del plano eran superficiales. Nodos intermedios de crosswalk 1:N pueden producir saltos por cargas nodales; no suavizarlos como una sola recta global.

### Producto ejecutable

Existe localmente `Builds/CurrentReview/StructuralReview.exe` (667136 bytes, 2026-09-21 20:17 hora local), con sus archivos acompañantes. Es anterior a muros/UX/losas actuales: **producto CURRENT final MISSING**. No se ejecutó hoy. `Assets/Editor/CurrentReviewBuild.cs` permite generar Windows64 Development desde Main. Excluir crash handler del conteo de productos. No hay .exe/.apk versionados, y no se encontró APK en Builds inspeccionado.

Para el modelo corresponde un build desktop probado; para la entrega grupal AR, APK probado físicamente si la pauta AR lo exige. Publicar ambos con datasets/manifest y hash final, no suponer que Editor Play constituye producto ejecutable. La licencia Unity y módulos Android/Windows son prerrequisitos del build, no certificados por leer ProjectVersion.

### Sidequests reales, no lista de marketing

| Función | Archivo/familia | Procedencia identificable | Estado/evidencia |
|---|---|---|---|
| CURRENT fail-closed e identidad hash | JsonLoader, current_dataset_contract; main.py | Integración CURRENT/organización | Tests de entrada y pipeline PASS |
| Mapa de capacidad y selección crítica | StructuralFailure/* | P1L6 visualización estructural | Screening; QA runtime guardado, no colapso |
| Filtros de edificio/piso/tipo y modo limpio | ViewerController/UX | UX y viewer del grupo | 83 checks guardados |
| Inspector compacto y tooltips | ViewerStructuralInspector; ViewerCurrentUX | codex/unity-visual-ux | Guardado PASS; no cambio analítico |
| Reconstrucción CAD y consolidación con aliases | modelo_central; auditorías POST_P1L4 | Ramas estructurales | Geometría/identidad PASS con límites primarios |
| Losas poligonales con huecos; malla de cargas | ViewerSlabQA y slab_reconstruction | current-slab-reconstruction | QA 44/24 guardado; perímetro REVIEW_REQUIRED |
| Explicación qQ/A/b/wQ y λQ | ViewerStructuralInspector; QA Q | Último CURRENT | 29 checks guardados |
| Panel Entregas/histórico vs actual | familia ViewerCurrentUX/metadata | Consolidación PRE-P1L5 | Función histórica, no mezcla automática de datasets |
| Transformación/query AR | transform/*; ArTransformMath | José, ar-transform-data | Matemática 20/20; dataset obsoleto |
| Daño ilustrativo | ElementFailureVisualizer | P1L6 | Solo visual, sin redistribución |

No adjudicar autoría individual de cada línea por nombre de carpeta. La contribución individual final necesita confirmación por commits y por cada integrante.

## H. Limitaciones que deben quedar en final.md

1. Marco global lineal elástico; no plastificación, fisuración distribuida, P-Delta no acreditado, redistribución post-falla ni simulación de colapso.
2. Losas sin elementos FE ni diafragma rígido de piso; cargas sí transferidas. Diferencias importantes frente a ETABS con diafragmas.
3. Espesor de losa 0,15 m provisional y material visual de losas UNKNOWN; polígonos físicos todavía sin certificación completa por plano.
4. Tributarias por grilla de 0,50 m y viga más cercana, no exactas de placa; conservación global no certifica reparto local.
5. Seis registros puntuales excluidos por falta de receptor: tres llamadas, no seis cargas físicas independientes.
6. 85 miembros ED1/P4 con material inferido; E/ν académicos. No todas las propiedades son confirmadas de detalle.
7. Sismo 20% del peso de piso y nodo cercano al centro geométrico; no centro de masa ponderado, no modelo normativo/modal completo; defecto de agregado G identificado.
8. Diagramas de extremos interpolados; distinguir fuerzas nodales de corte interno y FE segments vs sólido físico.
9. Todas las capacidades CURRENT son screening con acero/recubrimiento asumidos. No diseño normativo ni curvas Fiber por cada miembro.
10. Estudios Fiber separados con constitutivos de laboratorio; columna P50 parcial y seis puntos de muro inválidos; no interpolar como si fueran ensayos convergentes.
11. D/C con magnitud axial absoluta y envolventes no concurrentes; no acredita tracción ni interacción biaxial completa. N/T de viga y cortes/torsión de muro/columna fuera del screening P-M.
12. Sliders válidos solo para las cuatro bases lineales compatibles; cambiar inputs requiere reanálisis. Teléfono no ejecuta OpenSees.
13. QA geométrico/numérico no equivale a validación de ingeniería exhaustiva ni certificación de edificio real.
14. Runtime guardado corresponde a checkpoints; build/AR final y flujo de modificación deben volver a probarse, sin usar counts históricos como actuales.

## I. Plan mínimo hacia WEEK 7 MODEL READY

1. Aprobar este diagnóstico y fijar decisiones de alcance: fallbacks, cargas irresolubles, estudios Fiber separados y definición de centro sísmico.
2. Corregir agregado por piso y añadir regresión de conservación del peso sísmico; repetir G/Q/EX/EY y derivados/capacidad/handoff si cambia cualquier input.
3. Congelar versiones de entorno; reproducir en copia limpia usando instrucciones únicas y artefactos con hashes.
4. Validar modificación real y superposición explícita arbitraria; solucionar signos de P para D/C y dejar NO DATA para modos fuera de alcance.
5. Presentar al menos una Fiber, M-φ y P-M defendibles con sección/refuerzo, eje, unidades, convergencia y enlace a CURRENT o nota de estudio separado. No convertir screening en Fiber por etiquetado.
6. Regenerar AR elements + overlay y exports de identidad/material; auditar los 712 sólidos y crosswalk 1:N, sin exigir un tag FE a losas/apoyos visuales. Probar identidad, longitudes, orientación y demanda con contrato vigente.
7. Integrar a rama común los cambios aprobados y aportes pendientes por revisión de diff; preservar defaults UX y todos los tags históricos, incluida referencia original de Luis.
8. Compile/Play final y build Windows standalone probado fuera del proyecto. Equipo AR valida su APK/escena y tracking con el mismo manifiesto estructural.
9. README reproducible y `reports/final.md`: puntos 1–22, evidencia, limitaciones, IA, contribuciones, Honors si aplica. Incluir tabla requisito→archivo→prueba y ejemplo de demo.
10. Solo entonces preparar tag/release final nuevo (sin sobrescribir P1L4_FINAL ni historia), publicar binarios/JSON/figuras/QA, registrar hash evaluable y repetir smoke test de descarga.

**Criterio de cierre:** cero incompatibilidades de identidad/datasets; peso global y por piso consistente; fallbacks y exclusiones aprobados; resultados reproducibles; estudios de capacidad honestamente diferenciados; Viewer/build y handoff AR vigentes; documentación ejecutable por un usuario nuevo. No se creó tag ni release, ni se implementó ninguna corrección en esta etapa.
