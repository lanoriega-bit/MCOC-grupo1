# Lote A — herramientas históricas y duplicados exactos

## Archivado

- `tools/audit_architecture.py` y `tools/inventory_repository.py` →
  `archive/deprecated_code/repository_audits/`: contienen constantes del
  checkout anterior y etiquetas CURRENT superseded. Los reemplazan el mapa
  estático actual, el plan de archivo y `tools/validate_project.py`.
- `tools/build_viewer.py` → `archive/deprecated_code/viewers/`: generador HTML
  de Semana 2; no participa en Unity desktop actual. Conservar código histórico.
- `REPOSITORY_INVENTORY.json` → `archive/old_data/`: snapshot histórico, no configuración.

Búsquedas por nombre completo: consumidores solo documentación histórica,
inventarios/reportes y autorreferencia del inventario. Ninguna entrada CURRENT
ni build desktop invoca estos scripts. No ejecutarlos desde archive: para
reproducir su contexto original usar el commit correspondiente.

## Borrado de duplicados

Dos archivos eliminados:

- `entregas/P1L2/edificio/modelo/model_viewer_backup_576f014.json`
- `entregas/P1L2/unity_export/model_viewer_pre_reextraction_backup.json`

Ambos y la referencia conservada `entregas/P1L2/unity_export/model_viewer.json`
tienen SHA256 `0193a4f37d77519fd10f86bade537accdee823da8b261c8cecd008b44837fe5d`.
Búsqueda en código productivo y documentación operativa: sin consumidores de
los backups. No son evidencias únicas ni entregas diferentes. Recuperables desde Git.
La referencia de Luis no se mueve ni modifica.

## QA

Modelo/pipeline e identidad protegida desktop; pruebas de rutas/entrada/algoritmo.
Sin cambios de Unity ni resultados, sin pruebas AR. Ningún borrado adicional.
