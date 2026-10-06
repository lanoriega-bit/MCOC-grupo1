# Diagramas AR CURRENT — implementación y validación

Selección única: LuisARDiagrams lee ARStructuralElementController.SelectedElement y escucha ElementShown. No llama a ShowElement, Render ni a APIs de tracking/anchors. Las notificaciones repetidas del mismo objeto de datos conservan el componente y segmento elegidos. El buscador sigue siendo la única fuente de selección.

## Datos y compatibilidad

Solo CASE_R: Assets/StreamingAssets/p1l6_current_ar_elements.json, campo current_result_R.segments. Contrato MCOC_P1L6_AR_CURRENT_ELEMENTS_V1; estado raíz READY_PRECOMPUTED_PHONE_DOES_NOT_RUN_OPENSEES; fila CURRENT_VERIFIED. Cada segmento verifica analysis_id, pertenencia de opensees_tag y ambos nodos FE al elemento, seis entradas por extremo y valores finitos del componente. No se inventan ceros; un cero finito presente sí es un resultado válido.

No se cargan ni combinan otros archivos:
- analysis_cases.json / analysis_results.json pertenecen a P1L3, con identidades FE históricas.
- p1l4_jose declara P1L3_ENTREGADO_HISTORICO.
- seismic_ex_ey.json contiene resultados globales de edificio/piso, no los vectores locales CURRENT por segmento.
- p1l5_current_analysis_cases.json ofrece G/Q/EX/EY pero no coincide con el contrato AR: SHA256 real 34ddcea3fa37cf1d06d5aaaef3b2e50f848ef0195bca5bf38f26a53df77ca354; el dataset AR referencia f1cf961a58b9431fb92d743ea5bd3c9011771287a62409110f2084ec2ecda7e3. current_dataset_contract.json también referencia otro hash. E1-P1-V-002 comparte POST-A-00464/tag 10464, pero sus nodos son 317/318 en AR y 237/238 en el archivo de casos. E2-P1-M-007 no está en esos casos base. No hay vinculación inequívoca para habilitarlos.

El exportador del JSON no está disponible en este checkout. El orden se confirma en force_components del schema histórico, FormatForces y DiagramForceVector de ViewerController, y la respuesta localForce de OpenSees. Se usa solo su documentación/convención, nunca sus resultados históricos.
Fuente primaria: https://opensees.berkeley.edu/OpenSees/api/doxygen2/html/ElasticBeam3d_8cpp-source.html (getResponse, local forces).

Índices: 0 N, 1 Vy, 2 Vz, 3 T, 4 My, 5 Mz. Dividir por 1000: fuerzas en kN; momentos/torsión en kN·m. Ejes locales FE independientes de los ejes visuales AR.

Convención del gráfico: valor i = acción i / 1000; valor j = −acción j / 1000 para una misma cara de sección. El panel también muestra ambas acciones originales. La línea interpola los extremos; no representa una solución interna con cargas distribuidas. El eje horizontal usa distancia entre coordenadas de nodos FE en node_displacements, no longitud física en planta. En el muro de prueba es 3.96 m. Si faltan coordenadas, la longitud se declara no disponible.

## UI y alcance

Canvas UGUI automático del LuisARDiagrams ya presente en Luis_AR_Test. Usa el EventSystem/Input System existente, área segura, etiqueta Caso: R · CURRENT y botones N/Vy/Vz/T/My/Mz, título dinámico y cierre. Información y diagramas no quedan abiertos simultáneamente. La pérdida de tracking oculta/cierra los diagramas; no se pierde selección ni se modifica el objeto. Segmentos múltiples se recorren con Anterior/Siguiente, mostrando índice/total, analysis_id, tag y nodos. Los segmentos inválidos tampoco se descartan silenciosamente: muestran datos no disponibles.

No se modificaron renderer, controller, selector, información, tracking, anchors, escena, JSON, paquetes ni ProjectSettings. No hace falta asignación manual.

## Pruebas

Unity 6000.6.0f1 en Play Mode de un proyecto temporal aislado, Input System activo y únicamente el dataset AR copiado. No incluye los JSON históricos.

Pasaron A–F: selección sucesiva de E1-P1-V-002 / E1-P1-C-001 / E2-P1-M-007 y título exacto; AAA-123 retiene selección/diagrama; 12 ciclos por tipo de abrir/cerrar, mover cámara y actualizar anchor mantienen misma instancia, parent y transform local. También pérdida/recuperación de tracking, seis botones de componentes, etiquetas visibles, CanvasRenderer y malla del gráfico, navegación de ambos segmentos, ausencia de resultados, NaN y tag incompatible.

Cobertura de datos: 669 elementos, 673 segmentos, seis componentes por segmento; cuatro elementos tienen dos segmentos (E1-P3-V-112, E1-P3-V-114, E1-P4-V-104, E1-P4-V-106). Conversión/signos comparados contra datos originales y longitud FE válida en todos. N del muro: 239.55929899999982 kN; sus momentos cero se conservan como datos reales.

Compilación adicional de los 72 scripts de Assets con Roslyn y referencias instaladas: exit code 0, sin errores; advertencias de campos serializados/no usados y una API obsoleta existente. Logs: compilation.log y UnityChecks.log. Unity emitió una excepción en su índice de búsqueda del Editor al arrancar; ajena al código runtime probado.

Repetir desde PowerShell en el proyecto:

    ./Tests/ARDiagrams/RunChecks.ps1

Requiere Unity instalado y Library/PackageCache y ScriptAssemblies del proyecto actual. El script crea .diagram-check, nunca abre ni guarda la escena funcional. Tests fuera de Assets para no incluirlos en Android. Además se inspeccionó un render de UI en formato vertical 1080 × 1920 (diagram-preview.png): buscador y panel no se solapan; título, botones, datos, gráfico y cierre visibles. No son pruebas físicas de toque/legibilidad en Android: queda pendiente verificar el panel en el teléfono.


