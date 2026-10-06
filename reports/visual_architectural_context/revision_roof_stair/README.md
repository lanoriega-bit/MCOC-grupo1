# Revisión visual: cubierta, escalera y circulación

Base: `8e850ec`, rama `codex/visual-architectural-context`.
Fecha: 2026-10-06. Solo objetos pasivos de presentación en Unity desktop.

## Recorrido de escalera

Referencias leídas del contrato CURRENT, sin modificarlo:

| Tramo | Referencia | X inicial/final (m) | Z inicial/final (m) |
|---|---|---|---|
| Subida 1 | base E1-P2-C-021 → base E1-P3-C-012 | 72,491 → 57,491 | 7,92 → 11,88 |
| Horizontal | zona E1-P2-V-064 / V-059 | 57,491 → 47,841 | 11,88 → 11,88 |
| Subida 2 | llegada E1-P3-V-027 | 47,841 → 39,691 | 11,88 → 15,84 |

Y del recorrido = 17,661 m, al costado exterior de la fachada, entre las
caras del edificio y el borde de llegada; no atraviesa los ejes de columna.
La anchura visual es 1,80 m. Los tramos comparten endpoints y nivel de piso.
Peldaños, intradós continuo, laterales naranjas y barandas son solo visuales.
No se valida normativa ni se define una escalera estructural resistente.

La plataforma de llegada va entre V-020 (X=37,491) y V-027 (X=39,691),
Y=16,681–18,641, a Z=15,84 m, con espesor de presentación de 0,16 m.
Se elimina la tapa visual superior de la caja baja para liberar el recorrido.

## Cubierta y suelo

- Cubierta gris neutra de 0,18 m sobre ambos cuerpos y la caja vidriada alta.
  Dos paneles principales comparten un borde sin superposición coplanar;
  abarcan también los extremos salientes de las vigas P4, no solo las columnas;
  siguen los filtros de edificio y P4. Tiene control independiente en Contexto.
- Se retiran el paseo inferior de la primera propuesta y la explanada
  `Future_context_free_paved_area`: ya no quedan esas placas sobre el pasto.
- Se retiran los dos caminos pequeños anteriores del terreno elevado.
- Se mantiene la explanada de entrada con personas. El nuevo camino es
  perpendicular al eje longitudinal X: recorre todo el ancho Y de la terraza,
  detrás de las personas, y usa el mismo material que la explanada de entrada.
- La zona libre para futuro contexto permanece sin pavimento aislado.

## Validación

Compilación C# y Main/Play PASS en Unity 6000.6.0f1. `QA.json` registra
33/33 checks PASS con dataset `CURRENT_VERIFIED`. Las capturas se guardan
en `viewer/unity/Temp/architecture_visual_revision/` mediante
`MCOC → Revisar arquitectura visual`; la evidencia final se conserva aquí.
La revisión comprueba referencias, continuidad, cubierta, camino, filtros,
selección, CURRENT y despeje al mostrar deformada/diagramas.

Comprobación manual: selección por clic de E1-P3-V-094 con arquitectura
visible; sección/material y fuerzas R con unidades correctas en la ficha;
My 2D y deformada CURRENT desde la interfaz. Las vistas frontal, superior,
vidriada y Right comprueban recorrido, llegada, cubierta y camino.
Unity queda abierto en Main/Play, caso R, arquitectura visible y sin gráfico
o diagnóstico tapando la pantalla.

Capturas: `before.png`, `orange_facade.png`, `glazing_and_stairs.png`,
`stair_front.png`, `roof_and_path_top.png`, `right_access.png`.

Los archivos protegidos desktop se comparan por SHA256 contra el baseline
de migración: 117 comprobados, 117 idénticos, 0 cambios. No se modifica el modelo, cargas, resultados, OpenSees,
capacidades, datasets AR, escenas, paquetes, ProjectSettings ni tags.
No se invoca ningún solver ni se ejecutan escenas o pruebas AR.
