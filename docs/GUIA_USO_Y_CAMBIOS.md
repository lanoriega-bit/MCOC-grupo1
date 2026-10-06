# Usar y modificar el proyecto desde main

## 1. Abrir sin pedir ayuda a Codex

En el Explorador entra en la carpeta local del repositorio.
Haz doble clic en **Abrir_Unity.bat**. Unity Hub debe tener activa tu licencia
y estar instalada la versión 6000.6.0f1.

En Unity abre **Assets → Main.unity**, pulsa el triángulo **Play** arriba
y selecciona **Game**. Si la imagen está recortada, reduce Scale a 1x.
No abras P1L6_AR_Final para la demostración de escritorio.
No se reinstala Unity ni se crea otro edificio.
Si el lanzador directo queda bloqueado por licencia, abrir Unity Hub → Añadir
desde disco → `viewer/unity`. No abrir el registro antiguo de `viewer_unity`.

Para tener acceso fácil: clic derecho sobre Abrir_Unity.bat → Mostrar más opciones
→ Enviar a → Escritorio (crear acceso directo). El acceso directo debe apuntar
al archivo en el repositorio, no a una copia aislada del .bat.

## 2. Menú de tareas

Doble clic en **Proyecto.bat**:

| Opción | Qué hace | Qué NO hace |
| --- | --- | --- |
| estado | Lee conteos y comprueba identidad rápida | No certifica todo el QA |
| rutas | Muestra rutas completas | No modifica archivos |
| validar | QA del central y del dataset CURRENT | No recalcula cargas ni OpenSees |
| unity | Abre el proyecto canónico | No activa Play automáticamente |

Python 3.10+ requerido. El lanzador busca .venv-p1l5, luego .venv y luego python.
Conservar la historia Git: la comprobación de propiedades contrasta secciones y
materiales con el commit fuente declarado por el exportador. Un clon superficial
sin ese commit se marca REVIEW REQUIRED, no se certifica por el nombre del archivo.
Para validar también se requiere Shapely. Si faltan dependencias, se muestra el
error: no se instala software ni se inventa un PASS.

En un clon nuevo, desde PowerShell en la raíz, preparar el entorno:

```powershell
python -m venv .venv-p1l5
.\.venv-p1l5\Scripts\python.exe -m pip install -r requirements.txt
.\Proyecto.bat validar
```

En tu PC ya existe el entorno: no hace falta recrearlo.

## 3. Dónde poner cada cambio

Abre la carpeta del repositorio en tu editor de código. No pegar código en la
Console de Unity: esa ventana solo muestra mensajes y errores.

| Quiero cambiar | Archivo/carpeta |
| --- | --- |
| Menú, coordinación o mensajes | main.py |
| Rutas que muestra el menú | config/project_config.json |
| Geometría/conectividad/IDs | model/model_master.json |
| Dimensiones de secciones | model/sections.json |
| Propiedades de materiales | model/materials.json |
| Cargas físicas y tributarias | model/loads.json y analysis/opensees/live_loads.py |
| Construcción/casos OpenSees | analysis/opensees/run_cases.py |
| Contrato resultados → Unity | analysis/postprocessing/export_unity.py |
| P-M / screening demanda-capacidad | analysis/capacity/build_capacity.py |
| Interfaz/filtros/selección Unity | viewer/unity/Assets/Scripts/ |
| Acciones del menú MCOC | viewer/unity/Assets/Editor/ |
| Instrucciones del equipo | README.md, PROJECT_INDEX.md, docs/ |

El código está dividido por responsabilidades. `main.py` es una entrada completa,
no una copia enorme de los cálculos. Para añadir una tarea, crear su función
y registrarla en COMMANDS; mantener el cálculo estructural en su módulo.

## 4. Flujo seguro para una modificación física

1. Crear una rama desde main y salir de Play antes de regenerar datos.
2. Cambiar la fuente canónica con evidencia y trazabilidad del ID.
3. Validar central, reconstruir topología cuando corresponda y generar derivados.
4. Regenerar tributarias/cargas si cambió geometría o carga física.
5. Ejecutar los cuatro casos OpenSees, comprobar equilibrio/ejes/unidades.
6. Exportar resultados, actualizar capacidad y sus versiones; actualizar exports
   desktop de identidad/materiales si cambiaron esos datos.
7. Ejecutar validar y probar compile/Play, casos, selección, diagramas y capacidad.
8. Revisar diff, commit y push; nunca force push.

No hay un botón de reanálisis en el nuevo menú: evita activar migraciones o
supuestos viejos accidentalmente. El flujo P1L5 especializado permanece disponible
para las solicitudes de modificación que admite; revisar su secuencia antes de
usarlo sobre cambios geométricos nuevos.

Cambiar solo filtros o una combinación lineal de casos compatibles no cambia K
y no requiere OpenSees. Cambiar sección, material, apoyo, geometría, tributaria o
carga física sí invalida resultados. Hasta cerrar el flujo: STALE / REANALYSIS REQUIRED.

## 5. Historia y revisión

No editar resultados numéricos para hacerlos coincidir ni cambiar tags entregados.
No tocar la referencia original de Luis en P1L2.
No usar repos externos como fuente confirmada sin evidencia primaria.

Prueba real de Unity tras la reorganización: reports/repository_architecture_audit/DESKTOP_RELOCATION.md.
El QA del menú comprueba datos, no sustituye esa prueba visual.
La reorganización de main no cambia geometría, materiales, cargas o resultados.
