# Arquitectura y contexto visual — QA

Fecha: 2026-10-06. Rama: `codex/visual-architectural-context`.
Base estructural: main `c243a7bcccb21134e0bb7b1cdbd1203faacc2b9d`.

## Resultado

PASS de compilación y Play en Main, Unity 6000.6.0f1.
`QA.json`: 22/22 checks PASS, dataset `CURRENT_VERIFIED`.
El menú `MCOC → Revisar arquitectura visual` reproduce la prueba desktop.
Genera capturas y QA local en Temp; no escribe fuentes ni resultados.

Además, comprobación manual en la interfaz:

- Clic en E1-P4-V-093 con la piel visible: selección y ficha correctas.
- Lectura de sección 60 × 80 cm, longitud 6,55 m y material existente.
- Caso R: N/V/T/My/Mz visibles con kN y kN·m, sin reanálisis.
- My 2D y 3D visibles; arquitectura retirada automáticamente.
- Deformada CURRENT activada/desactivada: arquitectura se retira y restaura.
- Cámara y vistas conservadas; Contexto muestra los controles por capa.

## Antes / después

- `before.png`: arquitectura apagada, terreno previo conservado.
- `orange_facade.png`: piel naranja, franjas claras y acceso P2.
- `glazing_and_stairs.png`: vidrio transparente, cajas y escalera exterior.
- `right_access.png`: cota del acceso sobre la terraza existente.

Las capturas salen del mismo Play, sin alterar la geometría estructural.
Representación simplificada: ventanas, barandas, escaleras y paisajismo no
constituyen una extracción métrica de fotografías ni una comprobación CAD.
Las cotas de piso y las dos cajas se apoyan en el modelo CURRENT.

## Integridad

117/117 archivos protegidos desktop byte-idénticos al baseline de
`reports/repository_architecture_audit/migration_equivalence_desktop.json`.
Hash original de Luis preservado:
`0193a4f37d77519fd10f86bade537accdee823da8b261c8cecd008b44837fe5d`.

Sin diferencias contra main en model/, config/, analysis/, results/, ar/,
StreamingAssets/, Packages/ o ProjectSettings/. Sin modificación de Main.unity,
tags o datasets; no ejecución de OpenSees ni de escenas/pruebas AR.
Los objetos añadidos tienen capa Ignore Raycast, sin ElementInfo ni colliders
habilitados, y el registro estructural permanece idéntico durante la revisión.

## Alcance y mantenimiento

La implementación está aislada en ViewerArchitecturalContext.cs con tres hooks
en el controlador/UI; no duplica el modelo ni crea elementos FE.
Contexto permite apagar arquitectura, fachada, vidrio, escalera, paisaje y figuras.
Se mantienen tres árboles discretos y tres personas; la explanada baja libre
queda preparada para futuro contexto/estacionamiento, sin coches por ahora.

No se afirma validación AR: ese módulo queda intacto y fuera del alcance.
