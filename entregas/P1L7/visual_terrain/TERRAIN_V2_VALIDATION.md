# Entorno visual continuo — revisión 2

Fecha: 2026-10-04. Rama: `codex/unity-visual-terrain`.
Continúa el hito visual `7f661775469980694778842cdd47e1a52698fe64`.
El informe `RUNTIME_VALIDATION.md` y el JSON V1 conservan el diseño anterior.
Esta revisión sustituye el talud; no modifica datos estructurales ni históricos.

## Diseño actual

Tres terrazas rectangulares conectadas, no topografía medida:

| Grupo visual | Función | Cota superior canónica |
|---|---|---|
| CONTINUOUS_SITE_FUTURE_CONTEXT | Base amplia bajo ambas alas y superficie libre perimetral | −0,04 m |
| LEVEL_1_S1_C007_C019 | Terreno intermedio ampliado, conserva enterramiento de las 13 columnas | 3,96 m |
| LEVEL_2_ACCESS_V106_V107 | Plataforma horizontal exterior al acceso ED1, sin talud | 7,92 m |

Base inferior aproximadamente 107,19 × 48,28 m; margen visual de 12 m,
incluyendo superficie exterior al acceso. Terreno intermedio con margen 4 m;
acceso de 10 m de fondo. Son proporciones de presentación, NO límites del
predio ni dimensiones deducidas de fotos. La base se obtiene de las columnas
de ambos edificios y la plataforma exterior; su coronación está ligeramente
bajo la base estructural mínima, por lo que no entierra el S1 de ED2.
Los volúmenes se unen bajo cota de terreno, sin espacios inferiores vacíos.

Cada terraza tiene cuerpo neutro y una capa superficial verde discreta;
cuerpo y pasto tienen caras superiores separadas, evitando parpadeo coplanar.
El talud de la primera versión fue retirado del constructor de contexto:
solo quedan cajas con superficies horizontales y caras verticales.

Camino pavimentado de 3 m de ancho sobre el acceso elevado, conectado a un
paseo frente a V-106/V-107. Los materiales diferencian pasto, contención y
pavimento. No se añaden coches, estacionamiento, árboles, ornamentos, ni una
rampa ficticia que conecte cotas: el camino orienta la llegada en la terraza
superior; no certifica accesibilidad peatonal entre los tres niveles.

## Extensiones futuras

La base perimetral deja áreas abiertas para incorporar estacionamiento o
contexto después. Grupos independientes y nombres `VISUAL_ONLY_*` permiten
añadir decoración sin registrar miembros FE. Parámetros de presentación
centralizados en `ViewerVisualTerrain.cs`: TerrainMargin, SiteMargin,
AccessRun, PathWidth y TerrainBaseDepth. No se requiere modificar JSON.

En Contexto: interruptor general, base continua, Nivel 1 y Nivel 2. Reset
restaura los cuatro. ED1 apagado oculta sus terrazas; la base general sigue
disponible para ED2. Aislar elementos y diagnóstico FE ocultan el entorno.

## Validación real

Unity 6000.6.0f1 compiló la revisión y se reinició Play en Main.
Game Scale=1x para mostrar la interfaz completa.

| Prueba | Estado | Evidencia |
|---|---|---|
| Compilación y Play | PASS | Sesión real del editor; registro QA nuevo con `continuous site, box terraces and paved entry path` |
| ISO | PASS | Base continua, terrazas rectas, camino y pasto observados |
| Right | PASS | Frente vertical limpio; plataforma horizontal en base de P2; talud anterior ausente |
| Top | PASS | Terreno más ancho que el edificio y espacio perimetral observados |
| Selección | PASS | Click en E1-P3-C-013 con contexto ON; ficha y fuerzas CURRENT/R visibles |
| Filtro S1 | PASS | Apagado/restaurado manualmente; Nivel 1 acompaña el filtro, base general y acceso conservados |
| Regresión existente | PASS | UI QA, CURRENT UI QA, P1L5 QA y DEMO QA en el registro de esta sesión |
| Cobertura e inmutabilidad | PASS | 19 checks de `VISUAL_TERRAIN_V2_QA.json`; 13 columnas cubiertas; 260 archivos protegidos intactos |

Todas las cajas, incluso pasto y camino, son Ignore Raycast, sin colisiones
activas ni ElementInfo; no se registran como estructura ni alteran el encuadre
estructural. Para inspeccionar partes enterradas puede apagarse el contexto.
No se cambiaron Main.unity, nodos, miembros, losas, cargas, tributarias,
OpenSees, resultados CURRENT, capacidades, datasets ni exportaciones AR.
No se ejecutó OpenSees ni ningún generador estructural.
`LUIS_REFERENCE_FILES_MODIFIED = 0`.

Digest agregado de los mismos 260 archivos protegidos:
`f078008112752032565004938ea6300636325e37121de07ea868d4ec981932b6`.

Para repetir el QA desde la raíz: ejecutar Python sobre
`entregas/P1L7/visual_terrain/validate_visual_terrain.py`; solo escribe el informe
de esta tarea. Las pruebas de interfaz deben repetirse en Play, no son sustituidas
por la inspección del código. Unity queda abierto en ISO, caso R, con contexto ON.
