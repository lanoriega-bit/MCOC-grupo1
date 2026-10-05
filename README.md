# MCOC grupo 1 — laboratorio estructural digital

> Migración en curso en `codex/final-repository-architecture`, sin modificar `main`.
> Las fuentes oficiales están ahora en [model/](model/README.md) y
> [config/](config/README.md). Los módulos de análisis, Unity y AR aún se están
> consolidando. Véase [arquitectura](docs/ARCHITECTURE.md).

Edificios 1 y 2: modelo 3D canónico, OpenSees y Unity. Rama de cierre Semana 7:
**codex/week7-model-closure**. `main` todavía no incorpora este cierre.
El estado vigente incluye las correcciones de núcleos y columnas de P1L6;
las entregas históricas se conservan, no se sobrescriben.

## Empieza aquí

1. **Abrir el edificio:** doble clic en `Abrir_Unity.bat`.
2. En Unity abre `Assets/Main.unity`, pulsa **Play** y usa la pestaña **Game**.
3. **Menú del proyecto:** doble clic en `Proyecto.bat`.
4. **Comprobar el modelo actual sin recalcular:** doble clic en `Validar_Modelo.bat`.

Unity: 6000.6.0f1, licencia activa en Unity Hub.
El visor de escritorio es la interfaz habitual; la escena AR no sustituye Main.

## Reproducir CURRENT Semana 7 desde cero (Windows / PowerShell)

Python canónico: **3.12.14 x64**. OpenSeesPy **3.8.0.0** (motor 3.8.0).
Unity **6000.6.0f1**; versiones de paquetes en `Packages/manifest.json` y
`packages-lock.json` del Viewer. No actualizar paquetes silenciosamente.

```powershell
git clone --branch codex/week7-model-closure https://github.com/lanoriega-bit/MCOC-grupo1.git
cd MCOC-grupo1
python --version
python -m venv .venv-p1l5
.\.venv-p1l5\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File entregas/P1L7/reanalyse_current.ps1
.\.venv-p1l5\Scripts\python.exe -B entregas/P1L7/test_week7_loads.py
.\.venv-p1l5\Scripts\python.exe -B entregas/P1L6/transform/test_ar_transform.py
.\.venv-p1l5\Scripts\python.exe -B entregas/P1L7/benchmark_and_ar_diff.py
```

El pipeline usa la geometría y tributarias CURRENT versionadas: **no necesita CAD
original ni reconstruye áreas al editar qQ**. Produce G/Q/EX/EY, capacidades
aproximadas, contratos Unity y paquete de datos AR. Si falla, CURRENT queda STALE.
No sustituirlo por el pipeline geométrico antiguo para cambiar solo qQ.

En Unity Hub → Add → proyecto `entregas/P1L3/José/viewer_unity` →
`Assets/Main.unity` → Play → Game, escala 1x.
En **Análisis**: campo qQ [kN/m²] → Guardar → Reanalizar → recarga de escena.
En **Resultados**: λQ solo combina respuestas; no cambia el caso físico Q.
Un standalone fuera del repositorio es de consulta: no incluye OpenSees/Python.

Configuración única: `entregas/P1L5/modelo_central/analysis_settings.json`.
Valor inicial qQ = **0,667 kN/m²**, hipótesis de proyecto, no norma.
SC originales (incluidas lineales/puntuales) son referencia, no se suman a Q.
G permanente permanece; el sismo conserva explícitamente la hipótesis
educativa **0,20 × (G + 0,50 Q)**, sin atribuirla a una instrucción verificada
del profesor. Cambiar qQ invalida Q/EX/EY/R/D-C (se regenera también G por QA).

Fiber separado, sin sobrescribir historia ni capacidad CURRENT:

```powershell
.\.venv-p1l5\Scripts\python.exe -B entregas/P1L7/reproduce_fiber_studies.py
```

Outputs: `entregas/P1L7/fiber_studies`. Algunos puntos P-M no convergen:
ver `QA.json`; no son capacidad certificada ni se usan para calibrar D/C.
Los gráficos nuevos no interpolan intervalos no convergidos. Para volver a dibujar
los CSV existentes sin repetir ensayos: añadir `--plots-only` al comando anterior.

La regeneración también se comprobó en una copia Git limpia con un entorno nuevo;
ver `entregas/P1L7/CLEAN_CLONE_QA.json`. Para repetir esa comprobación, tras preparar
otra copia y su `.venv-p1l5`, desde el proyecto principal ejecutar:

```powershell
.\.venv-p1l5\Scripts\python.exe -B entregas/P1L7/verify_clean_clone.py --clone-root ../MCOC-grupo1-repro
```

Esto verifica Python/JSON, no sustituye Play ni la prueba del ejecutable final.
Estado de cierre y límites: [WEEK7_MODEL_CLOSURE](entregas/P1L7/WEEK7_MODEL_CLOSURE.md).

## Qué abrir y qué editar

| Necesidad | Entrada |
| --- | --- |
| Instrucciones detalladas y dónde cambiar código | [Guía de uso y cambios](docs/GUIA_USO_Y_CAMBIOS.md) |
| Archivos vigentes / históricos / generados | [Índice canónico](PROJECT_INDEX.md) |
| Menú y coordinación de comandos | [main.py](main.py) |
| Configuración de rutas | [project_config.json](config/project_config.json) |
| Geometría, secciones, materiales y cargas editables | [modelo_central](entregas/P1L5/modelo_central/README.md) |
| Auditoría estructural y QA más recientes | [Muros y núcleos CURRENT](entregas/P1L6/wall_continuity/README.md) |
| Uso del visor y funcionalidades | [Unity desktop P1L6](entregas/P1L6/desktop/README.md) |

`modelo_central` es la única fuente del modelo. No corregir geometría editando
`StreamingAssets`, resultados OpenSees o exportaciones antiguas.

## Comandos sencillos

En PowerShell, dentro de la carpeta principal:

```powershell
.\Proyecto.bat estado
.\Proyecto.bat rutas
.\Proyecto.bat validar
```

También se puede usar Python 3.10+ directamente: `python main.py estado`.
El menú y el resumen solo leen datos; validar actualiza su informe QA, pero no
cambia geometría/cargas ni ejecuta OpenSees. No instala dependencias automáticamente.

## Estado técnico y límites

Checkpoint CURRENT: 442 vigas, 143 columnas, 84 muros, 10 losas y 33 apoyos visuales.
FE: 1170 nodos topológicos, 677 segmentos (673 analizados), 0 componentes sin camino a apoyo.
G/Q/EX/EY y superposición compatibles; el comando `estado` calcula conteos y verifica
identidad del dataset, y `validar` ejecuta el QA técnico.

Laboratorio lineal elástico en SI (m, N, Pa), no un modelo de diseño certificado.
Losas sin elementos FE; cargas transmitidas por tributarias.
Capacidad HA separada. Persisten supuestos de materiales/armaduras/losas y tres
registros permanentes puntuales sin receptor, explícitamente excluidos; SC
histórica es referencia bajo la política Q uniforme. Ver las
notas del [QA vigente](entregas/P1L6/wall_continuity/CURRENT_PIPELINE_QA.md).

## Entregas y reproducibilidad

| Etapa | Documentación |
| --- | --- |
| P1L0 | [Benchmark mínimo](entregas/P1L0/README.md) |
| P1L1 | [Benchmark 3D](entregas/p1l1_benchmark_3d) |
| P1L2 | [Entrega y evolución](entregas/P1L2/README.md) |
| P1L3 | [Informe](entregas/P1L3/INFORME.md) |
| P1L4 | [Entrega histórica](entregas/P1L4/README.md) |
| P1L5 | [Guía funcional](entregas/P1L5/README.md) |
| P1L6 | [Integración](entregas/P1L6/README.md) |

`P1L4_FINAL` permanece intacto. La referencia original de Luis
`entregas/P1L2/unity_export/model_viewer.json` es solo lectura.
No mover masivamente carpetas históricas: las rutas forman parte de la reproducción.
