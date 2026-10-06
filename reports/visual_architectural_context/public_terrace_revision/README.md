# Terraza pública y contexto habitable — QA visual

Fecha: 2026-10-06. Rama: `codex/visual-architectural-context`.
Base de esta revisión: `3150f2883e7eba2d44dd0e6a7723c7b7689143a3`.

## Cambios exclusivamente de presentación

- Plataforma intermedia ampliada hasta X=37,491 m, eje de S1 C004/C005/C006.
  Toda su superficie y sus caras tienen acabado de hormigón.
- Dos escaleras públicas macizas exteriores, una por costado ±Y, con 22 peldaños
  entre Z=3,96/7,92 m. Cubren las bandas exteriores hasta el borde del terreno.
  Aterrizaje X=62,491 m: punto medio C015/C023 (ambas comparten Y=16,332 m).
  Baranda discreta con postes apoyados en peldaños, sin papel analítico.
- Dos mesas y seis sillas negras por costado: cuatro mesas/doce sillas en total.
- Ocho personas adicionales: cuatro en escaleras, dos junto a mesas, dos en cajas.
  Once figuras en total, escala esquemática y control opcional existente.
- Techo gris visual de 0,15 m en la caja delimitada por P2 V021/V041.
- Motoneta negra retro sobre el **pasto de la cota alta**, no en el pavimento,
  atendiendo a la petición adicional del usuario. Fuera del acceso y del camino.

La cubierta continua, el recorrido naranja C021→C012→V027, la plataforma de
llegada V020/V027, el camino transversal y las demás capas se conservan.
El sector bajo sin placas flotantes permanece libre. Todas las dimensiones de
contexto son de presentación, no una reconstrucción arquitectónica acotada.

## Validación

Main/Play y compilación en Unity 6000.6.0f1: PASS.
Menú `MCOC → Revisar arquitectura visual`: **42/42 PASS**, `CURRENT_VERIFIED`.
Capturas revisadas de ambas escaleras, mesas/sillas, techo y motoneta.

Prueba manual con arquitectura visible: selección por clic de E1-P4-V-119,
sección/material existentes y fuerzas N/V/T/My/Mz con unidades del caso R.
Gráfico My 2D, diagrama My 3D y deformada CURRENT activados/desactivados.
La arquitectura se despeja al ver resultados y se restaura después.
No se ejecutó OpenSees: solamente se leyeron resultados existentes.

117/117 archivos protegidos desktop byte-idénticos al baseline
`reports/repository_architecture_audit/migration_equivalence_desktop.json`.
Luis original permanece intacto. Sin cambios en model/, analysis/, results/,
config/, ar/, StreamingAssets, Main.unity, Packages, ProjectSettings, IDs,
crosswalks, tags ni capacidades. AR no abierto, probado ni regenerado.

Objetos en Ignore Raycast, sin ElementInfo ni colliders habilitados; el registro
estructural no cambia. Capa maestra y filtros existentes conservados. Mobiliario
exterior sigue la superficie de apoyo; personas interiores siguen sus pisos.

## Evidencia

- `QA.json`: 42 checks ejecutados en Play.
- `front_public_stair_and_seating.png` / `rear_public_stair_and_seating.png`:
  escaleras y mobiliario en ambos costados.
- `black_scooter.png`: moto apoyada sobre el pasto.
- `glazing_and_stairs.png`: conjunto y techo de caja baja.
- `roof_and_path_top.png`: cubierta continua y circulación.
- `right_access.png`: acceso elevado conservado.

Reproducir desde Main/Play con el menú indicado; genera evidencia nueva en
`viewer/unity/Temp/public_terrace_visual_review/`. No escribe datasets.
Estas escaleras/props no constituyen diseño constructivo ni validación normativa.
