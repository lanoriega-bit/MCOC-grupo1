# Terreno visual de dos niveles — validación

Fecha: 2026-10-04. Rama: `codex/unity-visual-terrain`.
Base sin cambios estructurales: `88a463b36d8a7a319167d7dd9c2d415c798ef78c`.

## Alcance

Solo contexto del viewer de escritorio, generado en memoria desde referencias
existentes. No es topografía levantada ni diseño de rampa accesible. La fotografía
define la lectura visual, no dimensiones métricas. No se modifica la escena
`Assets/Main.unity`, el modelo canónico ni ningún dataset AR.

Objetos bajo `VISUAL_ONLY_TERRAIN_NO_FE`:

- `VISUAL_ONLY_LEVEL_1_S1_C007_C019`: volumen de terreno con coronación Z=3,96 m,
  derivada de la base de P1. Cubre las 13 columnas S1 C-007 a C-019 sin retirarlas.
- `VISUAL_ONLY_LEVEL_2_ACCESS_V106_V107`: plataforma exterior +X junto a las
  referencias E1-P1-V-106/107, a Z=7,92 m, base de P2; descanso horizontal y
  talud esquemático de transición hacia el nivel inferior.

La base de P2 no es su cielo/losa superior Z=11,88 m. Márgenes 1,5 m,
descanso 3 m y recorrido exterior 8 m son elecciones visuales ajustables en
`ViewerVisualTerrain.cs`, no cotas deducidas de una fotografía.

## Prueba real en Unity

Unity 6000.6.0f1, escena Main, Play; Game Scale corregida de 1,3x a 1x para
evitar recorte de interfaz. El editor abierto por el usuario compiló los scripts.

| Prueba | Estado | Evidencia |
|---|---|---|
| Cobertura de las 13 columnas | PASS | Registro `[VISUAL TERRAIN QA] PASS: 13 S1 columns covered`; cotejo geométrico independiente |
| Acceso elevado desde Right | PASS | Observación en Play: coronación en base de P2; apagar solo Nivel 2 deja visible el terreno inferior |
| Terreno completo ON/OFF | PASS | Acción manual en Contexto: al apagarlo reaparecen los niveles y columnas ocultos |
| Nivel 2 independiente | PASS | Apagado y restaurado manualmente, sin ocultar Nivel 1 |
| Navegación ISO/RIGHT | PASS | Ambas vistas accionadas manualmente y escena observada |
| Selección con terreno activo | PASS | Click en E1-P3-C-013; ficha con identidad, sección, material y resultados CURRENT caso R |
| Filtro S1 | PASS | Apagado y restaurado: terreno inferior acompaña a S1; acceso elevado permanece |
| Selección pasiva del contexto | PASS | Sin ElementInfo ni registro estructural; Ignore Raycast; collider del cubo deshabilitado y eliminado, plataforma sin collider |
| Regresión de interfaz/resultados | PASS | Registro de la sesión: CURRENT UI QA y comprobaciones automáticas existentes de capas y casos |

Los objetos no participan en `allElements`, FE, cargas ni encuadre estructural.
Por ello la selección atraviesa el contexto; para ver un elemento enterrado,
apagar Terreno y acceso. Aislar un elemento o mostrar solo FE oculta este contexto.

## Inmutabilidad

`validate_visual_terrain.py` verifica 13 condiciones sin ejecutar OpenSees ni
generadores. Solo escribe `VISUAL_TERRAIN_QA.json` en esta carpeta. Verifica contra
la base todos los archivos protegidos: StreamingAssets, resultados, capacidad,
P1L5, preparación/exportación AR y referencia original de Luis.

260 archivos protegidos sin cambio; digest SHA256 agregado:
`f078008112752032565004938ea6300636325e37121de07ea868d4ec981932b6`.

OpenSees no se ejecutó ni modificó. Nodos, miembros, losas, materiales, cargas,
tributarias, resultados CURRENT y capacidades siguen siendo los existentes.
`LUIS_REFERENCE_FILES_MODIFIED = 0`.

## Uso

Abrir el proyecto `entregas/P1L3/José/viewer_unity`, escena `Assets/Main.unity`,
Play. En **Contexto** están el interruptor general y los dos niveles independientes.
**RIGHT** permite revisar la llegada a P2; **ISO** muestra mejor ambos niveles.
Los volúmenes son opacos intencionalmente para representar enterramiento.
