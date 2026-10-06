# QA final — Viewer CURRENT visual/UX

Fecha: 2026-10-01. Rama: `codex/unity-visual-ux`.
Base protegida: `d3ee850`. Escena: Unity 6000.6.0f1, `Assets/Main.unity`.

## Alcance

Solo presentación. El estilo ladrillo/acero/hormigón distingue categorías:
no declara nuevos materiales resistentes. No se regeneró ni ejecutó OpenSees.
Se conserva la geometría, secciones, cargas, capacidades, D/C, IDs y JSON CURRENT.

## Evidencia y resultados

| Verificación | Estado | Evidencia |
| --- | --- | --- |
| Compilación de scripts y shader | PASS | Editor recompilado; sin `error CS` ni `Shader error`; Play real |
| Play Main / contrato CURRENT | PASS | `UNITY_VISUAL_RUNTIME_QA.json` |
| Materiales y transparencia | PASS | Shader soportado, patrones por categoría, alpha 0,18 |
| Selección viga/columna/muro cyan | PASS | PropertyBlock contrastado con color de selección |
| Filtros tipo, piso y edificio | PASS | Activación y ocultación de objetos comprobadas |
| ISO/TOP/FRONT/RIGHT | PASS | Cámaras/vistas válidas en Play |
| G/Q/EX/EY/R | PASS | Resultados disponibles para tres tipos de elemento |
| Sliders / combinación R | PASS | My de R comparado con suma independiente de cuatro casos |
| Deformada / diagramas 3D y 2D | PASS | Objetos activos para seis componentes |
| Ficha | PASS | Sección y datos; tabla N/Vy/Vz/T/My/Mz, unidades y detalle completo |
| Capacidad / D/C / P-M | PASS | Evaluador existente y gráfico con demanda; `capacity.png` |
| Estados de falla / restauración | PASS | Colores sintéticos visuales y restauración de miembros físicos |
| Defaults | PASS | Nodos ON, losas OFF, mapa OFF al iniciar |
| Ayuda contextual | PASS | Caso G pulsado en UI: tooltip compacto; desaparece al salir; textos de los cinco casos verificados |
| Paneles / legibilidad | PASS | `default.png`, `inspector.png`; diagramas en dos filas sin desbordar |
| Integridad estructural e histórica | PASS | `VISUAL_SCOPE_QA.json`; seis controles protegidos |
| QA central / pipeline | PASS_WITH_NOTE | `main.py validar`: PASS y PASS_WITH_EXPLICIT_NOTES previos |
| Cargas en ficha / tributarias | PASS | Consumidores CURRENT conservados; capa tributaria comprobada |
| Overlays heredados 3D de carga | PASS_WITH_NOTE | Sin catálogo CURRENT al inicio; NO DATA/deshabilitados, no fallback histórico |
| Cobertura de losas | PASS_WITH_NOTE | Toggle/material responden; cobertura incompleta previa no corregida |

La comprobación de restauración excluye la malla FE de diagnóstico: no forma
parte del dominio del visualizador de capacidad. No se alteró esa malla para
hacer pasar la prueba. La altura de columna en la ficha se lee de `height_m`
del sólido actual, no del campo de longitud de vigas.

Regresión final ejecutada: **83 comprobaciones, 83 PASS, 0 FAIL**.
Comprobación manual adicional: H oculta paneles; R restaura la presentación.

## Limitaciones mantenidas

- Las losas son referencias visuales parciales, no placas FE ni cobertura aprobada.
- Las zonas/líneas de carga heredadas no tienen overlay CURRENT inicial.
  Sus controles explicitan NO DATA. Las cargas del elemento siguen en la ficha.
- Continúan los supuestos académicos de capacidad/material y seis cargas
  puntuales unresolved del proyecto base. Esta revisión no los valida de nuevo.
- Los diagramas mantienen su convención/datos previos: la interpolación no
  se convierte en un diagrama interno exacto por cambiar su apariencia.
- Persisten avisos previos del Editor sobre API obsoleta/serialización; no
  impiden compilar ni ejecutar Main. No se modificó configuración AR ni licencia.

## Reproducir

Abrir el proyecto Unity canónico, `Assets/Main.unity`, Play, Game Scale 1x.
Con los defaults de inicio, ejecutar **MCOC → Validar UX visual CURRENT**.
Se sobrescriben únicamente el informe y tres capturas de esta carpeta.
La prueba termina en ISO, R, colores normales, sin recalcular física.

## Checkpoints

1. `e578e47`: materiales y selección.
2. `e592fff`: layout y controles.
3. `c312451`: ayuda contextual.
4. `d3ad939`: ficha por bloques.
5. Commit de cierre: título `Validate redesigned CURRENT viewer`; incluye
   correcciones de legibilidad, prueba reproducible, evidencias y documentación.
