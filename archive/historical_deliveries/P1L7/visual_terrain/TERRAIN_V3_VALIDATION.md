# Terrazas hasta el perímetro — revisión 3

Fecha: 2026-10-04. Rama: `codex/unity-visual-terrain`.
Base de esta revisión: `4864ec35de1f81387515ca042b8a58135995f877`.

## Ajuste exclusivamente visual

Las terrazas dejan de ser cajas interiores: ambas llegan a los bordes laterales
del sitio, Y=−15,650 / 32,627 m. El nivel superior llega también al límite
exterior X=94,841 m y ocupa completamente la franja de su base.

| Nivel | X mínimo / máximo (m) | Y mínimo / máximo (m) | Coronación Z (m) |
|---|---|---|---|
| Base general | −12,348 / 94,841 | −15,650 / 32,627 | −0,04 |
| Intermedio | 40,806 / 72,841 | −15,650 / 32,627 | 3,96 |
| Superior/acceso | 72,841 / 94,841 | −15,650 / 32,627 | 7,92 |

Los niveles intermedio y superior comparten X=72,841 m: no hay solape de
volúmenes elevados ni hueco entre ambos. Se conserva el sector bajo de ED2;
no se extiende la cota intermedia sobre todo el edificio. Estos contornos son
esquemáticos de presentación, no nuevas cotas CAD ni un levantamiento del predio.

Pasto y paseo frente a V-106/V-107 conservados. El camino de llegada se prolonga
hasta el nuevo borde exterior del nivel superior. Acceso en base de P2, no en
su cielo; sin nuevas rampas ni caras inclinadas.

## QA

Unity 6000.6.0f1 recompiló; Main ejecutada nuevamente en Play.
ISO y Top comprobadas visualmente; Unity queda en ISO, contexto ON, caso R.
El registro real de Play confirma:

`[VISUAL TERRAIN QA] PASS: ... full-width terraces reach site perimeter and share boundary.`

Esta comprobación en runtime compara los bordes Y de las dos terrazas con la
base, el borde X exterior superior y el encuentro entre niveles. Confirma además
la cobertura de las 13 columnas y ausencia de colliders activos/ElementInfo.
UI QA, P1L5 QA y CURRENT UI QA también PASS en la sesión.

22 comprobaciones de inspección geométrica/código en
`VISUAL_TERRAIN_V3_QA.json`: PASS. Esta prueba no sustituye Play.
260 archivos protegidos sin cambios respecto a la base estructural original;
digest idéntico a las revisiones anteriores:
`f078008112752032565004938ea6300636325e37121de07ea868d4ec981932b6`.

No se modificaron estructura, nodos, miembros, losas, cargas, tributarias,
OpenSees, CURRENT, capacidades, StreamingAssets ni datasets AR. No se ejecutó
OpenSees. Luis original intacto. Solo código visual, QA y documentación cambian.
Informes V1/V2 conservados como registro de diseños anteriores.
