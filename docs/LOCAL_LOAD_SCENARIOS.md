# Escenarios de carga local — desktop

Rama `codex/local-load-scenarios`, base visual `b4b7ade` (incluye `3150f28`,
`8e850ec` y la arquitectura consolidada). No modifica main ni tags.

## Contrato estructural

CURRENT BASE es solo lectura. Q_LOCAL es gravedad adicional temporal (g=9,81
m/s²), no reemplaza Q ni qQ. Se analiza usando `prepare_contract` / `run_case`
del motor OpenSees existente y su entrada de cargas nodales arbitrarias.
R_SCENARIO = R_BASE + Q_LOCAL, con λLOCAL=1. Las capacidades son las mismas;
el Viewer evalúa las nuevas demandas con `StructuralFailureEvaluator`.

## Tributarias

Las tributarias congeladas almacenan áreas por receptor, no polígonos de cada
receptor. Se recuperan sus celdas originales de 0,50 m, punto representativo y
viga activa más cercana, conservando el orden de desempate. Antes de permitir
un escenario se verifican TODAS las áreas por receptor contra CURRENT (tol.
0,0001 m²; diferencias comprobadas inferiores a 0,000001 m²).

La selección se intersecta con los polígonos físicos de las losas CURRENT,
incluyendo huecos, luego con las celdas originales. Nunca se recalcula propiedad
de una celda usando la selección parcial. Se rechazan huecos, áreas exteriores,
receptores ausentes, gaps/solapes superiores a tolerancia y cambios de BASE.
La franja no cubierta por redondeo micrométrico de coordenadas se excluye, no
se rellena. qLocal se calcula sobre el área efectiva realmente cubierta.

Las cargas se acumulan por ID de viga física y se aplican P/2 en sus dos nodos
FE existentes (igual que CURRENT). Un crosswalk 1:N no multiplica la carga.
Las restricciones existentes conservan sus nodos retenidos. No se añaden nodos,
apoyos, propiedades, masas ni casos sísmicos.

## Archivos y ejecución

- `analysis/opensees/local_scenarios.py`: geometría temporal y adaptador al motor.
- `tools/run_local_scenario.py`: worker solo con salida en `results/scenarios/`.
- `tests/loads/test_local_scenarios.py`: QA numérico read-only.
- `results/scenarios/`: solicitudes / resultados de usuario ignorados por Git.

Los archivos BASE se fijan mediante SHA-256 antes y después de cada operación.
No se llama al pipeline de reanálisis CURRENT ni a sus exportadores canónicos.
Un cambio de BASE durante el cálculo descarta el resultado.

## QA inicial del motor

Ejecutar desde raíz con el Python del proyecto:
`python -B tests/loads/test_local_scenarios.py`.

Demo: EDIFICIO_1 / P2, rectángulo XY (45,4)–(52,9) m; área 35 m²;
10 × 68 kg = 6670,8 N; qLocal=0,1905942857 kN/m²; cuatro receptores
E1-P2-V-045/048/058/060. Reacciones verticales 6670,8 N; residual relativo
2,07e-16; desplazamiento incremental máximo 8,27755e-6 m.

PASS: 0/1/10/20 personas; masa/superficie equivalentes; inputs inválidos;
selección parcial exterior; huecos; conservación; equilibrio; linealidad;
ED2 no afectado; comparación contra corrida explícita R+Q_LOCAL;
recuperación de partición en todos los pisos disponibles; hashes BASE intactos.

## Uso en Main / Play

1. Abre `viewer/unity/Assets/Main.unity`, Play, pestaña Game, escala 1x.
2. Despliega **CARGA LOCAL**. Selecciona Personas / Peso [kg] / kN/m²,
   edificio y piso. Default: 10 personas de 68 kg, editable.
3. **Seleccionar zona · TOP** aísla temporalmente el piso y edificio. Arrastra
   un rectángulo sobre la losa. La arquitectura visual se oculta temporalmente
   para no tapar el piso. Esc cancela; un clic sin área no genera un escenario.
4. Se muestran área dibujada, efectiva, q adicional y receptores. El amarillo
   identifica la selección, no D/C. **Mostrar zona local** permite ocultarla.
5. **ANALIZAR ESCENARIO** ejecuta OpenSees asíncronamente: mientras calcula
   solo BASE es válido. Al finalizar aparece **R_SCENARIO**.
6. Selecciona un miembro. En **Ficha estructural → Resultados** compara
   R_BASE / R_SCENARIO / Δ: My, Vz, desplazamiento y D/C. Desplaza la ficha
   hacia abajo para ver este bloque. Se comparan máximos absolutos de extremos
   de todos sus segmentos FE; Δ es diferencia de envolventes, no el incremento
   en un extremo concreto. Signos completos permanecen en la tabla original.
7. En **Resultados**, diagramas 3D/2D y deformada usan el caso visible. R se
   convierte en R_SCENARIO cuando está activo; G/Q/EX/EY siguen disponibles.
   Sus cuatro sliders reconstruyen R_BASE + Q_LOCAL, sin reanalizar Q_LOCAL.
8. En **Capacidad**, activa los colores D/C existentes: naranja ≥0,80,
   rojo ≥1,00, gris sin datos y cyan para selección. No se añadió una banda
   amarilla ni otro evaluador. Las capacidades y sus hipótesis no cambian.
9. **RESTAURAR BASE** retira la zona y resultados temporales, restaura filtros
   previos y demanda/colores BASE sin ejecutar OpenSees. R también resetea.

La ejecución requiere el repositorio Windows y `.venv-p1l5/Scripts/python.exe`
preparado con `requirements.txt`. Un standalone aislado no contiene el solver:
falla con un mensaje claro, no inventa resultados.

## Implementación y separación

`ViewerLocalScenarios.cs` conserva solicitudes, geometría amarilla y respuesta
Q_LOCAL fuera de las colecciones físicas canónicas; clona R antes de sumar los
vectores SI. El worker existente se reutiliza por `prepare_contract/run_case`,
sin crear otro solver. El proceso es oculto y asíncrono; polling, timeout,
identidad de BASE y revisión de la solicitud evitan aceptar salidas tardías,
obsoletas o incompatibles. Cambiar entrada desactiva el escenario hasta analizar.

El caso independiente no incluye G, Q ni EX/EY, ni modifica masas. La combinación
visible añade cada vector una sola vez. Los receptores siguen siendo vigas
físicas, aunque su crosswalk tenga varios segmentos. OpenSees propaga después
su efecto a columnas, muros y reacciones.

Archivos desktop integrados: `ViewerController.cs` (caso/selección/reset),
`ViewerCurrentUI.cs` (panel), `ViewerP1L5.cs` (R y protección de edición BASE),
`ViewerStructuralInspector.cs` (comparación), `ViewerArchitecturalContext.cs`
(visibilidad temporal y liberación de objetos/proceso). No cambia escenarios AR,
packages, Main, materiales estructurales, geometría ni datasets canónicos.

## QA de Unity

En Main/Play: menú **MCOC → Validar carga local en Main Play**.
`ViewerLocalScenarioQA.cs` y `Editor/LocalScenarioReviewMenu.cs` prueban
solves reales, comparación, todos los componentes de diagramas, deformada,
sliders R, identidad de BASE, colores renderizados y restauración. Salida local:
`viewer/unity/Temp/local_scenario_review/QA.json` y capturas; evidencia de cierre
en `reports/local_load_scenarios/`. No abre escenas AR ni ejecuta pruebas AR.

La búsqueda incremental de carga grande encontró 10240 personas equivalentes
(6830,8992 kN) sobre 35 m²: E1-P2-V-058 pasa de D/C 0,414194 a 1,702513.
Es un ensayo numérico extremo, no un aforo real ni el default. Comprueba estados
naranja/rojo provenientes del solver. No representa fractura ni comportamiento
post-falla. Grandes desplazamientos muestran advertencia del modelo lineal.

Para 10 personas, E1-P2-V-048 tiene |ΔMy Q_LOCAL| máximo 0,089026 kN·m y
|Δu Q_LOCAL| máximo en sus nodos 0,002555 mm. Su D/C pasa de 0,013778942 a
0,013778469: una demanda firmada puede disminuir una componente existente;
no se fuerza crecimiento en todos los miembros. Ningún miembro con D/C BASE
<0,50 saltó a capacidad excedida con esta pequeña carga.

## Límites explícitos

- Conserva la hipótesis CURRENT de tributarias por celdas de 0,50 m; no es un
  modelo de placa ni una nueva reconstrucción CAD.
- Conserva aplicación nodal P/2 por receptor físico; no representa la forma
  exacta de carga distribuida a lo largo de una viga. Diagramas siguen usando
  las convenciones existentes, nunca curvas académicas fabricadas.
- Una sola selección rectangular y escenario activo a la vez. Pueden quedar
  salidas locales ignoradas; no se añadió gestión de biblioteca/exportación.
- Solo peso gravitatorio temporal; no nuevas masas, sismo, no linealidad ni AR.
- D/C sigue siendo el cálculo educativo CURRENT y sus hipótesis de capacidad,
  no una certificación de seguridad/aforo.
- BASE STALE/cambiado o selección sin cobertura válida: rechazo explícito.

## Cierre

LOCAL LOAD SCENARIOS — READY. Evidencia reproducible y revisión manual en
`../reports/local_load_scenarios/README.md`; no hay blockers funcionales abiertos.
La regresión verificada está detallada allí, sin afirmar cobertura exhaustiva de
todo el Viewer. Persisten advertencias preexistentes del editor, no fallos de este módulo.
El máximo D/C global puede corresponder a un miembro ya excedido en BASE
(en R=G+0,5Q, E1-P3-V-109 ≈1,045); no atribuirlo automáticamente a Q_LOCAL.
