# Semana 5 - AVANCE: laboratorio estructural interactivo v1

Grupo 1 - MCOC. Laboratorio estructural digital del Edificio de Ingenieria (Edificios 1 y 2).

Base del informe: ultima actualizacion de GitHub del flujo P1L5 (`origin/codex/p1l5-integration`, commit `3bc9749`) mas los 3 commits locales del ramo `jose/mati-p1l5-fixes` (`917c09f`, `182abd6`, `42188f9`). Componentes: pipeline Python/OpenSeesPy (analisis estatico G/Q/EX/EY + demanda/capacidad P-M) y viewer interactivo Unity 6000.6.0f1 (build Windows `StructuralReview.exe`).

## 1. Funciones implementadas y su estado

El viewer del laboratorio (`entregas/P1L5/modelo_central` + `entregas/P1L3/Jose/viewer_unity/Assets/Scripts`) expone:

| Funcion | Evidencia en el codigo | Estado |
| --- | --- | --- |
| Navegacion/camara | Orbitar (arrastrar), zoom (rueda), desplazar (boton central); F11 presentacion, H modo limpio, R restablecer | Implementada (`ViewerController.cs:1538-1540`, `ViewerCurrentUI.cs:321`) |
| Seleccion + busqueda | Clic en viga/columna/muro/losa; Enter busca el ID, Escape restaura | Implementada (`ViewerController.cs:1553-1554`) |
| Apoyos | Capas "Apoyos geometricos" y "Apoyos FE" (33 apoyos, todos z=0.0) | Implementada (`ViewerCurrentUI.cs:215`) |
| Ejes | GLOBAL X/Y/Z + flechas x/y/z locales del elemento (RGB) | Implementada (`ViewerOrientation.cs`, `ViewerStructuralInspector.cs:168`) |
| Cargas | Capas de carga superficial y lineal + inspector de cargas/tributarias por elemento | Implementada (`ViewerCurrentUI.cs:213`, `ViewerController.cs:1708-1730`) |
| Areas tributarias | Capa `tributary`/`tributary_point` + lectura m2 y kN en inspector | Implementada (`ViewerController.cs:1012`, `ViewerCurrentUI.cs:287`) |
| Deformada | Desplazamientos nodales reales de la corrida OpenSees (G/Q/EX/EY) | Implementada (`ViewerP1L5.cs:139`, `ViewerController.cs:1143`) |
| Diagramas | Grafico 2D N/Vy/Vz/T/My/Mz del elemento seleccionado | Implementada (`ViewerController.cs:1903,2244-2246`) |
| Superposicion lineal instantanea | Recombina los casos base con lambdas a partir de resultados numericos | Implementada (`ViewerP1L5.cs:41`, `ViewerCurrentUI.cs:220`) |
| P-M y D/C | Grafico de interaccion P-M + ratio demanda/capacidad dinamico | Implementada (`ViewerController.cs:2092-2135`, `ViewerP1L5.cs:150`) |
| Filtros de contexto | Edificio 1/2, pisos S1-P4, toggles por tipo de elemento, "solo problemas", "solo correcciones" | Implementada (`ViewerCurrentUI.cs:175-245`) |
| Losas/panos | 46 panos visuales (44 zonas CAD + 2 tiras sinteticas) | Reconstruidos en esta semana (`build_current_loads.py`) |
| Modificacion en runtime | Cambiar parametros del elemento marca `STALE_REANALYSIS_REQUIRED` | Parcial: el viewer detecta el cambio y exige re-ejecutar el pipeline (ver seccion 2) |
| Carga movil (sidequest) | No existe modulo de carga movil en `Assets/Scripts` | NO implementada (ver seccion 4) |

El QA de UI (`ViewerReviewQA.cs`) aprueba la configuracion actual: `PASS` con modelo current, capas archivadas bloqueadas, inspector completo, identidad negativa, filtros por edificio/piso, resoluciones 1366x768 y 1920x1080, ejes locales, fullscreen.

## 2. Dos modificaciones completas

Se documentan dos modificaciones reales aplicadas de principio a fin (datos -> analisis -> export -> viewer), con su flujo reproducible.

### Modificacion 1 (datos de carga): resolver las 2 cargas de linea de E2-P4

Las cargas `L700-E2-P4-LINE-SC-100-SC_LINE` y `L700-E2-P4-LINE-SC-100-PM_ADIC_LINE` no caian sobre zonas de losa CAD. Se resolvieron por la ruta de revisión:

1. **Modelo/mapa**: en `loads.json` se persistio `review_resolution` con `status: RESOLVED_BY_REVIEW_SLAB_ROUTE`, `equivalent_strip_width_m: 1.0` y `receptor_panel_id: L700-E2-P4-H05`. El script `build_current_loads.py` genera los panos sinteticos STRIP por `geometry.buffer(0.5, cap_style="flat")`.
2. **Analisis**: los 46 panos se tributaron por distancia igual a la viga mas cercana; `run_current_opensees.py` recalculo G/Q/EX/EY (PASS, residuo de equilibrio ~1e-15, G total 78 141 127 N, Q total 24 636 594 N).
3. **Export**: `export_current_to_unity.py` regenero el contrato del viewer con los panos actualizados.
4. **Reinstalacion en el viewer**: las viguetas receptoras aparecen ahora con la carga asumida (V-081: 1 121 N Q / 16 817 N G; V-085: 1 280 / 19 199; V-089: 659 / 9 879).
5. **Pruebas**: `validate_current_loads_and_results.py` y `validate_e2_p4_zone_completion.py` PASS.

Commit: `182abd6`.

### Modificacion 2 (geometria de miembro): E1-P3-V-101 y E1-P1-C-023

En `model_master.json` se corrigieron dos miembros: inicio de `E1-P3-V-101` en `[67.841, 16.331, 15.44]` (patron identico a su hermana de P4 `E1-P4-V-088`) y seccion de `E1-P1-C-023` como `SEC_COLUMN_RECT_0.700x0.700`.

1. **Modelo**: edicion de `model_master.json`.
2. **Re-build**: `build_current_loads.py` regenera el modelo de analisis.
3. **Re-analisis**: `run_current_opensees.py` (4 casos PASS).
4. **Export**: `export_current_to_unity.py` embebe `StructuralReview.exe`; el inspector del viewer muestra las nuevas coordenadas y la seccion 0.700x0.700 corregidas.
5. **Verificacion**: script de pendientes valida ambos miembros en el modelo exportado.

Commit: `917c09f`.

Secuencia reproducible de todo el ciclo (a ejecutar con `py -3.12` en `entregas/P1L5/analysis`):

```text
build_current_loads.py   -> 46 panos, cargas zonificadas CURRENT
run_current_opensees.py  -> G/Q/EX/EY (OpenSeesPy, PASS)
export_current_to_unity.py -> StreamingAssets del viewer
generar_demanda_capacidad.py -> 173 elementos, 7 familias P-M
```

## 3. Superposicion interactiva verificada contra resultados numericos

La superposicion del viewer es lineal sobre los casos base: `R = lG*G + lQ*Q + lEX*EX + lEY*EY` y los resultados por caso se leen de `results/current/*.json`. Se verificaron tres estados contra los numericos actuales:

| Estado | Rz (suma de reacciones) | Concepto | Residuo de equilibrio |
| --- | --- | --- | --- |
| G (λ=1) | 78 141 126.994 N | iguala el contrato 78 141 127.002 N (dif. 0.008 N) | 2.8e-7 N (rel. ~1e-15) |
| Q (λ=1) | 24 636 593.868 N | iguala el contrato 24 636 593.938 N | -5.2e-8 N |
| 1.4G | 109 397 577.792 N | combinacion = 1.4 x Rz(G) | lineal por construccion |
| 1.2G + 1.6Q | 133 187 902.582 N | combinacion peso/servicio | lineal por construccion |
| G + Q + 0.3EX + 0.3EY | 102 777 720.862 N | envolvente con sismo al 30% | lineal por construccion |

Ademas: EX/EY son laterales (Rz ~ 0) con desplazamiento maximo de 66.98 y 99.29 mm; maximo desplazamiento G = 97.3 mm, Q = 38.7 mm. El manifest marca `linear_superposition_compatible: true` y cada caso base cierra con residuo relativo ~1e-15, lo que garantiza que la recombinacion instantanea del viewer reproduce exactamente la combinacion indicada. En demanda por elemento, `E1-S1-C-009` pasa de N=3 195.5 kN (G) y 949.3 kN (Q) a 5 802.6 kN bajo 1.4G+1.4Q; es el peor elemento del modelo (D/C = 5.253).

## 4. Sidequest: carga movil

**No implementada en v1.** Una busqueda en `Assets/Scripts` no encuentra modulo de carga movil (`cargaMovil`, `movingLoad`, `tren`, `locomotora`). En una viga real la sobrecarga de ruedas seria una de las cargas mas comprometedoras del tablero.

Se documenta como pendiente con el diseno candidato (no codificado): aplicar un patron de cargas puntuales/lineales moviles sobre el eje longitudinal de las vigas de puente de acceso, re-correr o re-combinar linealmente las posiciones discretas, y mostrar la envolvente y el factor de carga critico. En el simulador interactivo se materializaria como un control de posicion de la carga movil con actualizacion instantanea (la base lineal de la seccion 3 lo permite).

## 5. Evaluacion de experiencia de uso estructural

Respuestas a las seis preguntas de la evaluacion UX:

1. ¿Se entiende el estado de cada elemento sin hojear archivos? Si: el inspector describe identidad, propiedades, carga tributaria, analisis y capacidad del elemento seleccionado; la UI de resumen muestra semaforos por caso (G/Q/EX/EY) y D/C; hay vista "solo problemas / no resueltos".
2. ¿Se distinguen las cargas propias de las sobrecargas? Si: el inspector diferencia "Peso propio (kN)" de "carga muerta tributaria (kN)" y hay capas y casos separados (G vs Q).
3. ¿Los cambios de criterio son visibles? Parcial: los criterios se ven en el inspector y en `traceability` del D/C, pero no hay editor de criterios en runtime (limitacion documentada).
4. ¿Se navega por edificio/piso/tipo? Si: filtros Edificio 1/2, pisos S1-P4, toggles por tipo y busqueda por ID.
5. ¿Es claro que es visual y que es analitico? Si: el contexto fisico se etiqueta "solo visual", las losas "alcance parcial", y los resultados analiticos vienen del caso de OpenSees activo.
6. ¿Se distingue lo verificado de lo pendiente? Si: panel de revision pendiente con prioridades CONFIRMED/REVIEW_REQUIRED, capa "solo correcciones POST-P1L4" y manifest de resultados con status PASS.

QA automatizado de UI en resoluciones 1366x768 y 1920x1080: PASS.

## 6. Preparacion movil

**Equipo compatible (objetivo):** Android 8.0+ (API 26+), 4 GB RAM, pantalla 1080p, GPU con soporte ASTC, chipset de gama media alta. El viewer usa mallas procedimentales y una GUI ligera (IMGUI), por lo que la memoria y la GPU no son limitantes para este modelo.

**Build inicial movil (pasos, NO ejecutados en esta maquina):**
1. Instalar en Unity Hub el modulo "Android Build Support" (SDK, NDK y OpenJDK asociados). En la maquina actual `Unity/6000.6.0f1/Editor/Data/PlaybackEngines` solo contiene `WebGLSupport` y `windowsstandalonesupport`; el modulo Android no esta instalado.
2. `File > Build Settings`: plataforma Android, `Switch Platform`.
3. `Player Settings`: package name propio, IL2CPP + arm64, Graphics API OpenGL ES 3.0, compresion de texturas ASTC.
4. Build del APK y prueba en dispositivo/emulador.

**Estado real:** el build movil no se completo en esta jornada por falta del modulo Android/SDK en la maquina (requiere descarga de GB). El laboratorio v1 se entrega como ejecutable Windows (Unity 6000.6.0f1). Para v2 se debe adaptar la interaccion a touch (drag/zoom/pinch) y escalar la UI desde 16:9 de escritorio.

## 7. Uso de IA

**Funcionalidad compleja implementada con asistencia de IA:** el generador de demanda/capacidad P-M (P-M/D-C) y su integracion con el viewer, junto con la resolucion de la discontinuidad de cargas E2-P4.

- **Que hizo la IA:** diseno y depuracion de `generar_pm_curvas.py` (seccion de fibra 0.700x0.700 m con acero por capas, 260 pasos, 13 fracciones axiales + compresion pura, momento-curvatura e interaccion P-M) y de `generar_demanda_capacidad.py` (para cada demanda (P,M) interpola la capacidad en la curva del eje correspondiente `My`/`Mz`). Tambien propuso la ruta de tira equivalente (losa) que resolvio las 2 cargas de linea de E2-P4 sin inventar receptores.
- **Verificacion:**
  - 173 elementos verticales con curva P-M (ejes My y Mz); 7 familias de seccion: 128 columnas 0.700x0.700, 13 de 0.350x0.350, 2 de 0.200x0.200, y muros 0.600x0.795, 0.600x1.825, 0.600x0.790, 0.300x1.450.
  - D/C: 163 de 173 con `DC_ratio` (94 superan 1.0; maximo 5.253 en E1-S1-C-009); los 10 restantes quedaron documentados como `no_bracket` (demanda fuera del rango de la curva), nunca silenciados.
  - El viewer lee `demanda_capacidad.json` (contrato P-M/D/C) y su QA de integridad pasa (P-M plot con puntos validos, mapeo a geometria seleccionable).
  - Conservacion de carga: G + Q cierran en menos de 1e-6 N frente al contrato (seccion 3).