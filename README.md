# MCOC-grupo1

Repositorio de trabajo para el Proyecto 1 del curso. El grupo desarrollara durante el semestre un laboratorio estructural digital del Edificio de Ingenieria, usando OpenSeesPy para analisis estructural y Unity para visualizacion/interaccion en etapas posteriores.

## Entrada rapida para el equipo

- Enunciado completo organizado: `docs/enunciado-proyecto-p1.md`.
- Entrega actual P1L0: `docs/p1l0-explicacion.md`.
- Script OpenSeesPy P1L0: `opensees/p1l0/ejemplo_minimo_2d.py`.
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

## P1L0 - Ejemplo minimo 2D OpenSeesPy

La entrega actual corresponde solo a `P1L0`: mostrar, validar y explicar un ejemplo minimo 2D de OpenSeesPy.

## Como ejecutar

Requisitos:

- Python 3.12 (no usar 3.9 ni otras versiones anteriores).
- OpenSeesPy 3.8.0.0 (definido en `requirements.txt`).

Este repositorio puede usarse desde WSL y Windows en la misma carpeta.
Cada entorno usa su propia carpeta `.venv` para evitar conflictos.

### WSL / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import openseespy.opensees as ops; print('OpenSeesPy OK')"
python opensees/p1l0/ejemplo_minimo_2d.py
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import openseespy.opensees as ops; print('OpenSeesPy OK')"
python opensees/p1l0/ejemplo_minimo_2d.py
```

## Que modela

Se modela una viga simplemente apoyada 2D con una carga puntual vertical en el centro.

- Modelo: `basic`, 2 dimensiones, 3 GDL por nodo.
- GDL por nodo: desplazamiento `ux`, desplazamiento `uy`, rotacion `rz`.
- Elementos: `elasticBeamColumn`.
- Transformacion geometrica: `Linear`.
- Apoyo izquierdo: pasador, restringe `ux` y `uy`.
- Apoyo derecho: rodillo, restringe `uy`.
- Carga: fuerza puntual vertical descendente en el nodo central.

## Validacion manual

Para una viga simplemente apoyada de largo `L` con carga puntual centrada `P`:

- Reaccion izquierda: `R_A = P / 2`.
- Reaccion derecha: `R_B = P / 2`.
- Momento maximo: `M_max = P * L / 4`.
- Deflexion vertical central: `delta = P * L^3 / (48 * E * I)`.

El script compara las reacciones y la deflexion de OpenSeesPy contra estas expresiones teoricas.

## Criterio de aceptacion

La entrega P1L0 se considera correcta si:

- El analisis converge.
- La suma de reacciones verticales equilibra la carga aplicada.
- Las reacciones coinciden con `P/2` dentro de tolerancia numerica.
- La deflexion central coincide con la solucion teorica dentro de tolerancia numerica razonable.
- Se puede explicar claramente el modelo, los GDL, apoyos, carga y verificacion.
