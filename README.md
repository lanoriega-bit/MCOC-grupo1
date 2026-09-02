# MCOC-grupo1

Repositorio de trabajo para el Proyecto 1 del curso. El grupo desarrollara durante el semestre un laboratorio estructural digital del Edificio de Ingenieria, usando OpenSeesPy para analisis estructural y Unity para visualizacion/interaccion en etapas posteriores.

## Entrada Rapida

- Enunciado completo organizado: `docs/gestion/enunciado-proyecto-p1.md`.
- Entrega P1L0: `entregas/p1l0/`.
- Entrega P1L1 benchmark 3D: `entregas/p1l1_benchmark_3d/`.
- Semana 2 edificio completo desde CAD: `entregas/semana02_edificio_completo/`.
- Entrega P1L1 benchmark 3D 2: `entregas/p1l1_benchmark_3d_2/`.
- Ejercicio adicional columna-viga: `entregas/ejercicios/columna_viga/`.
- Indice preliminar de planos: `recursos/planos/notas/indice-planos.md`.
- Registro semanal: `docs/gestion/weekly-log.md`.
- Registro de uso de IA: `docs/gestion/ai-usage-log.md`.
- Reglas para agentes IA: `AGENTS.md`.

## Entregas

| Entrega | Descripcion | Script principal | Resultados |
| --- | --- | --- | --- |
| P1L0 | Benchmark 2D basado en Pregunta 2 del Control 1. | `entregas/p1l0/opensees/ejemplo_minimo_2d.py` | `entregas/p1l0/results/` |
| P1L1 | Benchmark 3D del sector `P1L1-S01`: pano entre ejes `F-G` y `2-3`. | `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py` | `entregas/p1l1_benchmark_3d/results/` |
| Semana 2 | Edificio completo preliminar desde CAD, con modelo 3D coloreado, export Unity y esqueleto OpenSees de gravedad. | `entregas/semana02_edificio_completo/opensees/extract_cad_model.py` | `entregas/semana02_edificio_completo/results/` |
| P1L1 3D 2 | Benchmark 3D del sector `P1L1-S02`: dos panos entre ejes `F-G-H` y `2-3`. | `entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py` | `entregas/p1l1_benchmark_3d_2/results/` |
| Ejercicio adicional | Modelo 2D columna-viga de acero. | `entregas/ejercicios/columna_viga/opensees/columna_viga_2d.py` | `entregas/ejercicios/columna_viga/results/` |

Cada entrega se organiza igual:

- `docs/`: explicacion, informe o enunciado usado.
- `opensees/`: scripts OpenSeesPy.
- `results/`: figuras, tablas y verificaciones generadas.

## Organizacion

```text
entregas/
  p1l0/
    docs/       documentacion de la entrega
    opensees/   scripts OpenSeesPy
    results/    figuras y resultados generados
  p1l1_benchmark_3d/
    docs/
    opensees/
    results/
  semana02_edificio_completo/
    data/
    docs/
    opensees/
    results/
    unity_export/
  p1l1_benchmark_3d_2/
    docs/
    opensees/
    results/
  ejercicios/
    columna_viga/
      docs/
      opensees/
      results/
recursos/
  planos/
    pdf/        planos originales
    notas/      indices y observaciones
    logs/       archivos auxiliares no estructurales
docs/gestion/   bitacoras, enunciado y registros generales
```

## Alcance general del proyecto

- Modelo estructural global lineal elastico 3D en OpenSees/OpenSeesPy.
- Nodos 3D con 6 GDL para el modelo global.
- Vigas, columnas y muros idealizados con elementos lineales equivalentes.
- Cargas gravitacionales y vivas transferidas por areas tributarias.
- Casos base `G`, `Q`, `EX`, `EY` y uso de superposicion.
- Capacidad no lineal de secciones RC separada del modelo global.
- Unity como herramienta de visualizacion, preproceso, postproceso e interaccion.
- AR basica en etapas posteriores.
- Uso documentado y critico de IA durante el semestre.

## Como ejecutar

```powershell
python -m pip install -r requirements.txt
python entregas/p1l0/opensees/ejemplo_minimo_2d.py
```

Para ejecutar el ejercicio adicional de columna-viga:

```powershell
python entregas/ejercicios/columna_viga/opensees/columna_viga_2d.py
```

Para ejecutar el benchmark 3D P1L1:

```powershell
python entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py
```

Para ejecutar el benchmark 3D P1L1 2:

```powershell
python entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py
```

Para generar el modelo 3D preliminar de Semana 2 desde DXF locales:

```powershell
python entregas/semana02_edificio_completo/opensees/extract_cad_model.py
```

Para correr el esqueleto OpenSees de gravedad de Semana 2:

```powershell
python entregas/semana02_edificio_completo/opensees/building_gravity_skeleton.py
```

Al ejecutarlo, ademas de imprimir la verificacion numerica, se genera una imagen con el resultado fisico del modelo:

```text
entregas/p1l0/results/diagrama_pregunta_2.png
entregas/p1l0/results/diagramas_nvm_pregunta_2.png
```

El primer diagrama muestra la geometria original, la deformada amplificada, la carga distribuida, la rotula interna, las reacciones y los esfuerzos maximos. El segundo contiene los diagramas `N`, `V` y `M`.

El ejercicio adicional de columna-viga genera:

```text
entregas/ejercicios/columna_viga/results/diagrama_columna_viga.png
entregas/ejercicios/columna_viga/results/diagramas_nvm_columna_viga.png
```

## Que modela

Se modela el marco 2D de la Pregunta 2:

- Modelo: `basic`, 2 dimensiones, 3 GDL por nodo.
- GDL por nodo: desplazamiento `ux`, desplazamiento `uy`, rotacion `rz`.
- Elementos: `elasticBeamColumn`.
- Transformacion geometrica: `Linear`.
- Apoyos en `A` y `E`: articulaciones, restringen `ux` y `uy`.
- Rotula interna en `C`: se duplican nodos y se igualan solo las traslaciones.
- Carga: distribuida vertical de `3 tonf/m` sobre la proyeccion horizontal.
- Geometria: `A(0,0)`, `B(4,3)`, `C(6.5,3)`, `D(9,3)`, `E(13,0)`.

## Validacion contra la pauta

El script compara automaticamente contra los resultados de la pauta:

- Reacciones verticales: `R_Ay = R_Ey = 19.5 tonf`.
- Reacciones horizontales: `|R_Ax| = |R_Ex| = 21.13 tonf`.
- Axial maximo: `|N|max = 28.6 tonf`.
- Corte maximo: `|Q|max = 7.5 tonf`.
- Momento maximo: `|M|max = 9.38 tonf*m`.
- Tension maxima por flexion: aproximadamente `80.511 MPa`.
- Tension tangencial maxima por corte: aproximadamente `29.6 MPa`.

Tambien verifica equilibrio global:

```text
sum Fx = 0
sum Fy = 0
```

## Criterio de aceptacion

La entrega P1L0 se considera correcta si:

- El analisis converge.
- Las reacciones equilibran la carga aplicada.
- Las reacciones coinciden con la pauta de la Pregunta 2 dentro de redondeo.
- Los maximos de axial, corte y momento coinciden con la pauta dentro de redondeo.
- Se genera el diagrama `entregas/p1l0/results/diagrama_pregunta_2.png`.
- Se puede explicar claramente el modelo, los GDL, apoyos, rotula interna, carga y verificacion.
