# Lote C — P1L5 histórico, después de retirar dependencias activas

La fuente física y cargas ya están en model; OpenSees/capacidad/exportación en
analysis. El reconstructor FE y su kernel/dependencia fueron trasladados en
`1faecdf`; las funciones del kernel son AST-idénticas y no se ejecutó sobre CURRENT.

Antes de mover P1L5, búsqueda de referencias operativas en main/config/analysis/
tools/tests/C#: solo procedencia de resultados y rutas del commit histórico.
Las rutas `historical_property_paths` de config son **ACTIVE_REQUIRED para Git**:
`git show <commit>:<ruta_original>` no abre la carpeta de trabajo. Se preservan
sin modificar el commit; no requieren que P1L5 exista en el checkout actual.
No hay consumidor activo del filesystem de P1L5.

Los productores ahora emitirán rutas funcionales de procedencia al regenerar
en el futuro. No se reexportaron ni modificaron los resultados actuales.
Se conserva el antiguo constructor de cargas/tributarias como código histórico:
no reemplaza el refresh uniforme CURRENT ni se ejecuta para reorganizar.

Estado: **BLOCKED_WHOLE_FOLDER_MOVE** por revisión de seguridad; no movido.
La revisión señala rutas activas en config. No forzar ni sustituir hashes para
evitar el control. Se requieren pruebas específicas y aprobación del alcance
antes de mover la carpeta completa; se pueden revisar sublotes independientes.

Destino propuesto: `archive/historical_deliveries/P1L5/`. Mantener evidencia única y
entrega oficial. Herramientas productivas documentadas en PROJECT_INDEX.
AR no se ejecuta ni modifica; no cambio de escenas/datasets.

QA obligatorio del lote: modelo, pipeline, identidad protegida y pruebas.
