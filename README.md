# MCOC-grupo1

Repositorio de trabajo para el Proyecto 1 del curso. El grupo desarrollara durante el semestre un laboratorio estructural digital del Edificio de Ingenieria, usando OpenSeesPy para analisis estructural y Unity para visualizacion/interaccion en etapas posteriores.

## Entrada rapida para el equipo

- Enunciado completo organizado: `docs/enunciado-proyecto-p1.md`.
- Enunciado P1L0 usado: `docs/p1l0-pregunta-2-control-1.md`.
- Entrega actual P1L0: `docs/p1l0-explicacion.md`.
- Script OpenSeesPy P1L0: `opensees/p1l0/ejemplo_minimo_2d.py`.
- Ejercicio adicional columna-viga: `docs/ejercicio-columna-viga.md`.
- Indice preliminar de planos: `planos/notas/indice-planos.md`.
- Registro semanal: `docs/weekly-log.md`.
- Registro de uso de IA: `docs/ai-usage-log.md`.
- Reglas para agentes IA: `AGENTS.md`.

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

## Foco actual

### P1L0 - Ejemplo minimo 2D OpenSeesPy basado en Pregunta 2

La entrega actual corresponde solo a `P1L0`: mostrar, validar y explicar un ejemplo minimo 2D de OpenSeesPy.

Como el curso pidio usar un ejercicio existente, el ejemplo se basa en la Pregunta 2 del Control 1 de Estructuras Isostaticas: marco isostatico de tres articulaciones con carga distribuida vertical.

## Como ejecutar

```powershell
python -m pip install -r requirements.txt
python opensees/p1l0/ejemplo_minimo_2d.py
```

Para ejecutar el ejercicio adicional de columna-viga:

```powershell
python opensees/ejercicio_columna_viga/columna_viga_2d.py
```

Al ejecutarlo, ademas de imprimir la verificacion numerica, se genera una imagen con el resultado fisico del modelo:

```text
results/p1l0/diagrama_pregunta_2.png
results/p1l0/diagramas_nvm_pregunta_2.png
```

El primer diagrama muestra la geometria original, la deformada amplificada, la carga distribuida, la rotula interna, las reacciones y los esfuerzos maximos. El segundo contiene los diagramas `N`, `V` y `M`.

El ejercicio adicional de columna-viga genera:

```text
results/ejercicio_columna_viga/diagrama_columna_viga.png
results/ejercicio_columna_viga/diagramas_nvm_columna_viga.png
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
- Se genera el diagrama `results/p1l0/diagrama_pregunta_2.png`.
- Se puede explicar claramente el modelo, los GDL, apoyos, rotula interna, carga y verificacion.
