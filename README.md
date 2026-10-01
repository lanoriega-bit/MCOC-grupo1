# MCOC grupo 1 — laboratorio estructural digital

Edificios 1 y 2: modelo 3D canónico, OpenSees y Unity. Rama compartida: **main**.
El estado vigente incluye las correcciones de núcleos y columnas de P1L6;
las entregas históricas se conservan, no se sobrescriben.

## Empieza aquí

1. **Abrir el edificio:** doble clic en `Abrir_Unity.bat`.
2. En Unity abre `Assets/Main.unity`, pulsa **Play** y usa la pestaña **Game**.
3. **Menú del proyecto:** doble clic en `Proyecto.bat`.
4. **Comprobar el modelo actual sin recalcular:** doble clic en `Validar_Modelo.bat`.

Unity: 6000.6.0f1, licencia activa en Unity Hub.
El visor de escritorio es la interfaz habitual; la escena AR no sustituye Main.

## Qué abrir y qué editar

| Necesidad | Entrada |
| --- | --- |
| Instrucciones detalladas y dónde cambiar código | [Guía de uso y cambios](docs/GUIA_USO_Y_CAMBIOS.md) |
| Archivos vigentes / históricos / generados | [Índice canónico](PROJECT_INDEX.md) |
| Menú y coordinación de comandos | [main.py](main.py) |
| Configuración de rutas | [project_config.json](project_config.json) |
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
Capacidad HA separada. Persisten supuestos de materiales/armaduras/losas y seis
registros de cargas puntuales sin receptor, explícitamente excluidos; ver las
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
