# Semana 7 — cierre técnico CURRENT

Estado de este checkpoint: **IN PROGRESS**. No es un tag/release evaluable final.
Rama `codex/week7-model-closure`, base `3cc21d613377f295880974a62fe98c48c9eea50f`.

## A. Estado inicial

La base más completa era `codex/current-slab-reconstruction`, no `main`.
Incluye las correcciones de muros/núcleos, UX y losas posteriores.
Working tree inicial: solo el informe previo `TECHNICAL_READINESS_AUDIT.md` sin versionar.
`main` estaba ocho commits detrás. `p1l6/final-integration` es divergente: no se mezcló sin revisar.
Historia entregada, `P1L4_FINAL` y referencia original de Luis intactos.

## B. Cambios realizados

Geometría, secciones, materiales, apoyos y tributarias no se modificaron.
442 vigas + 143 columnas + 84 muros + 10 losas + 33 apoyos visuales = 712 sólidos.
FE: 1170 nodos topológicos, 677 segmentos candidatos, 673 analizados,
1165 nodos analizados, 44 apoyos retenidos, cero componentes sin camino a apoyo.
Cuatro segmentos redundantes dentro de clusters rígidos no añaden doble rigidez.

## C. qQ editable

Una única configuración fuente: `entregas/P1L5/modelo_central/analysis_settings.json`.
Su copia Unity es generada; no editarla a mano.
qQ inicial = **0,667 kN/m²**, hipótesis de proyecto: 68 kg × 9,81 ≈ 667 N/m².
No es una exigencia normativa ni una instrucción verificada del profesor.
La autorización del usuario reemplaza toda SC histórica, incluidas SC lineales/puntuales.
PM/PP permanecen en G; los valores originales del catálogo se conservan como referencia.

`week7_loads.py` aplica Q = qQ × A sobre las 40 zonas/tributarias ya existentes.
No recalcula polígonos, A, anchos ni nodos; bloquea cambios de geometría/áreas con hashes congelados.
Se conserva byte-equivalente la lista nodal G. Las fuerzas tributarias Q se convierten
a cargas nodales; no se fabrican diagramas parabólicos de element loads inexistentes.

Unity: **Análisis → qQ → Guardar → REANALIZAR**. Resultado anterior STALE inmediato;
regeneración Python/OpenSees/capacidad/AR y recarga completa de escena al pasar QA.
Fallo en cualquier etapa vuelve a bloquear CURRENT. Standalone portable: consulta,
sin OpenSees móvil/embebido; reanálisis necesita repositorio + Python en Windows.
λQ está en Resultados y solo combina respuestas: no cambia Q ni ejecuta OpenSees.

Prueba automática real (`test_week7_loads.py`, entorno aislado limpio):

| qQ [kN/m²] | Q [N] | Máx traslación Q [m] |
| ---: | ---: | ---: |
| 0 | 0 | 0 |
| 0,667 | 4330195,420369 | 0,000683889335429 |
| 1,334 | 8660390,840738 | 0,001367778670858 |
| restaurar 0,667 | baseline recuperado | baseline recuperado |

Todos los DOF, reacciones y fuerzas de extremo comprobados; G/áreas idénticas.
Negativos/NaN/Inf rechazados. Para Q, qQ doble con λQ=1 equivale a baseline
con λQ=2; **EX/EY no son equivalentes**, porque la masa educativa depende de Q.
Demostración Editor: guardar 1,334 → STALE → reanálisis → recarga CURRENT verificada.
Restauración desde Unity demostrada; baseline final exacto 0,667 regenerado
y QA de hashes/contrato aprobado. La demo integral final sigue pendiente.

## D. Peso sísmico

Error: `build_current_loads.py` fijaba `G_total_N` por piso antes de añadir
`L700-P4-LINE-SC-800-PM_ADIC_LINE`. La PM lineal de fachada estaba en G nodal/global,
pero faltaba en el agregado usado por EX/EY. No se añadió una constante arbitraria:
se recompone G por piso desde G_self + G_superimposed + G_slab al terminar.
Faltaban **2265719,518 N**, localizados en ED1-P4; la SC lineal Q se reemplazó,
pero la PM lineal G se conserva.

Peso sísmico antes: 87769016,5625 N. Con Q antigua y G corregida:
90034736,0805 N. Con Q nueva: 80881157,0742 N; EX/EY cada uno
16176231,4148 N. El desfase de 0,03 N frente al total global proviene
del redondeo de componentes agregados, no de otra omisión.

`ETABS_COMPARISON.json` separa peso antiguo, peso antiguo corregido con Q antigua
y peso nuevo con qQ uniforme. No confundir el descenso por nueva Q con el efecto
de corregir G. La política explícita conservada es **0,20 × (G + 0,50 Q)**;
no se encontró una regla específica nueva del profesor para el 50%.
Aplicación pseudoestática al nodo retenido más próximo al centro geométrico
de cada grupo piso/edificio; no es un modelo modal ni un centro de masa exacto.

## E. OpenSees / ETABS

G permanece **78716059,334 N**. Baseline Q nuevo **4330195,420369 N**.
G/Q/EX/EY regenerados, finitos y en equilibrio; resultados/metadata/capacidad
comparten hashes de modelo, análisis y configuración.
R explícita (cargas combinadas en una nueva corrida) comparada contra bases:
coeficientes cero, todos uno y G=0,83 Q=1,17 EX=−0,21 EY=0,13.
Error relativo global < 5e−14; se comparan desplazamientos, reacciones y fuerzas.

ETABS: [tabla reproducible](ETABS_COMPARISON.md), fuente `resumen_modelos.pdf`, p.1.
G por edificio difiere aproximadamente −4,09% / −3,51%.
Nueva Q y sismo difieren significativamente por hipótesis/input/formulación;
no se calibraron para igualar ETABS. No existe crosswalk verificado para sus
nodos 311/2987 o C9/C21/B739/C1/C4/B189: no hacer comparación puntual engañosa.
CURRENT no calcula períodos modales; los del PDF no certifican este modelo.

## F. AR data synchronization

[Diff exacto por ID/tipo/edificio/piso](AR_EXACT_DIFF.json): 658 → 712,
**54 muros añadidos, 0 IDs retirados**. ED1: 6 por cada nivel (30);
ED2: 5 S1/P1/P2/P3 y 4 P4 (24). La exportación anterior precedía los núcleos CURRENT.
669 elementos estructurales con resultados/capacidad; 10 losas y 33 apoyos
intencionalmente visual-only, sin resultados FE fabricados.
Datos: identidad, tags OpenSees, geometría/dimensiones, materiales, R y D/C.
QA corrigió una falsa tolerancia: diferencias de longitud ahora producen FAIL,
y los muros usan eje físico en planta, no la columna vertical equivalente FE.
No se modificaron tracking, anchors ni calibración AR.

## G. Fiber / M–φ / P–M

Reproducción nueva en `fiber_studies`, sin escribir resultados históricos
ni sustituir capacidades CURRENT analíticas aproximadas.

Columna: sección estudio P.70x70, 12Ø25, recubrimiento 0,04 m,
hormigón Concrete01 fc 35 MPa sin confinamiento, acero Steel01 fy 420 MPa,
28×28 fibras de hormigón + 12 barras. No es un mapeo certificado a una columna CURRENT.
OpenSees: `uniaxialMaterial`, `section Fiber`, `patch rect`, `fiber`,
`zeroLengthSection`, compresión axial y control de curvatura.
M–φ P=0: 240 pasos completos, unidades kN·m y 1/m.
P–M: P=0 y 0,25P0 convergen, compresión pura axial converge;
0,50P0 queda parcial al paso 237. Se conserva y etiqueta, no se inventa un pico.

Muro: estudio histórico E2-P1-M-019 (no es un miembro activo CURRENT),
5,8×0,22 m, altura 3,96 m, dos cortinas Ø16@0,20 m, recubrimiento 0,02 m,
80×8 fibras, materiales de estudio/armadura asumidos. Flexión Mz de eje fuerte.
8/14 puntos válidos; **6 no convergidos** excluidos como capacidad fiable.
`fiber_studies/QA.json` registra ambos límites. CURRENT sigue siendo screening
académico con armaduras asumidas, no Fiber ni diseño certificado.

## H. Versiones

Python 3.12.14 x64; OpenSeesPy/openseespywin 3.8.0.0, motor 3.8.0.
NumPy 2.5.3; Matplotlib 3.10.5; ezdxf 1.4.4; Shapely 2.1.2.
Dependencias transitivas fijadas en `requirements.txt`.
Unity 6000.6.0f1, AR Foundation/Core 6.6.2, UGUI 2.6.0 (manifest/lock versionados).
El entorno antiguo no se actualizó; cada tag histórico conserva sus inputs.

## I. Reproducibilidad

Comandos relativos exactos en [README](../../README.md).
Entorno nuevo `.venv-week7-check` creado, instalación desde requirements completada;
Q/superposición real y 20 pruebas de transformación pasaron en él.
No equivale todavía a un smoke test de descarga/standalone ni licencia portátil de Unity.

## J. Desktop build

**NOT BUILT — FINAL BUILD NOT APPROVED**. El ejecutable previo sigue histórico.
No se declara un build PASS sin ejecutarlo fuera del Editor y comprobarlo.

## K. QA consolidado de este checkpoint

| Bloque | Estado | Evidencia / límite |
| --- | --- | --- |
| Geometría: vigas/columnas/muros/IDs/conectividad | PASS | validate_central_model; 0 errores/advertencias |
| Losas/mallas/tributarias | PASS_WITH_NOTE | 24 checks; contornos físicos REVIEW_REQUIRED |
| G / qQ / conservación | PASS | tests q=0/default/doble/restaurado; G intacto |
| Peso sísmico / EX/EY | PASS_WITH_NOTE | agregado corregido; fracción Q académica explícita |
| OpenSees cuatro casos / NaN / equilibrio | PASS | manifest y QA por caso |
| R desplazamiento/reacción/fuerzas | PASS | corrida explícita compatible vs bases |
| Capacidad / D-C | PASS_WITH_NOTE | cobertura 669; analítica aproximada, refuerzo asumido |
| Fiber / M–φ | PASS_WITH_NOTE | estudio reproducido, no capacidad CURRENT |
| P–M columna / muro completo | REVIEW_REQUIRED | 1 caso parcial / 6 puntos no convergidos |
| AR crosswalk / longitudes / demanda | PASS | AR_DATASET_VALIDATION; 712 / 669 FE |
| Unity compile / Play / qQ reanálisis | PASS_WITH_NOTE | flujo doble demostrado; suite integral final pendiente |
| Entorno nuevo | PASS_WITH_NOTE | instalado y tests físicos/transformación; clone completo pendiente |
| Documentación / enlaces | IN_PROGRESS | completar evidencias finales antes de release |
| Desktop externo | NOT_TESTED | requiere build final + smoke test |

## L. Limitaciones reales restantes

- Perímetros/huecos y espesores de losas conservan incertidumbre primaria; no inventar CAD.
- Tres PM puntuales sin receptor inequívoco siguen excluidas; no inventar aplicaciones.
- Materiales/armaduras educativos y capacidad aproximada no certifican seguridad real.
- Política sísmica educativa pendiente de contraste con instrucción específica del profesor.
- Puntos Fiber no convergidos no sirven para extrapolar una envolvente completa.
- Falta cerrar demo completa, compilación final y prueba standalone externo.

## M. Integración final

Mantener esta rama separada. Propuesta: revisar diff de `p1l6/final-integration`,
integrar solo cambios compatibles de informe/configuración después de QA,
y posteriormente merge no destructivo de esta rama hacia main **solo con autorización**.
No tag/release nuevo todavía; `P1L4_FINAL`, entregas históricas y Luis intactos.
Los hashes de cada checkpoint se comunicarán tras commit/push, no se inventa un hash autorreferente.
