# Resumen 3D — Edificio generado desde building_master.json

Fecha: 2026-09-03
Fuente de verdad: `entregas/P1L2/edificio/datos/building_master.json` (calce A confirmado)
Generador: `entregas/P1L2/edificio/scripts/phase6_build_3d.py`
Salida 3D: `entregas/P1L2/unity_export/model_viewer_candidate.json`
Visor: `entregas/P1L2/viewer/index.html?model=model_viewer_candidate.json`

## Contenido 3D generado

| Tipo | category 3D | Conteo | Nota |
|---|---|---|---|
| Columnas | column | 139 | seccion P.70x70 (datos master) |
| Vigas | beam | 1241 | seccion confirmada V.60/80 (0.60 x 0.80 m) |
| Muros | wall | 600 | espesor 0.22 m (datos master) |
| Bordes de losa | slab_edge | 382 | e = 0.15 m (borde perimetral) |
| Fundaciones | support | 314 | tiras de apoyo nominales (NEEDS_REVIEW) |
| Relleno de losa (ref.) | slab | 45 | caja envolvente por bucle (referencia visual) |
| Ejes (lineas CAD) | axis | 395 | ejes reales del DXF |
| **Total solids** | | **2721** | (+ 395 lineas axis) |

## Conteos por piso (3D)

| Piso | Columnas | Vigas | Muros | Borde losa | Fundaciones | Slab fill |
|---|---:|---:|---:|---:|---:|---:|
| Fundaciones (base) | 14 | 169 | 210 | 21 | 314 | 3 |
| 1S | 8 | 177 | 136 | 56 | 0 | 5 |
| Piso 1 | 28 | 195 | 86 | 64 | 0 | 6 |
| Piso 2 | 29 | 205 | 61 | 66 | 0 | 6 |
| Piso 3 | 26 | 213 | 61 | 70 | 0 | 6 |
| Piso 4 | 34 | 282 | 46 | 105 | 0 | 19 |
| **TOTAL** | **139** | **1241** | **600** | **382** | **314** | 45 |

## Comparativa building_master vs 3D

| Tipo | building_master (modelable) | 3D | Dif |
|---|---:|---:|---:|
| columna | 139 | 139 | 0 |
| viga | 1241 | 1241 | 0 |
| muro | 600 | 600 | 0 |
| perimetro_losa | 382 | 382 | 0 |
| fundacion | 314 | 314 | 0 |
| eje_grafico | 395 | 395 | 0 |
| **Total** | **3071** | **3071** | **0** |

Validacion automatica (`phase7_validate_3d.py`):
- MATCH = 3071
- MISSING_IN_3D = 0
- GEOMETRY_MISMATCH = 0
- METADATA_MISMATCH = 0
- EXTRA_IN_3D = 0 (sin contar slab fill = esperado)

## Continuidad vertical (phase8_validate_3d.py)

- 8 relaciones continuas Fundacion -> Piso 4 (nucleo central).
- 19 relaciones "con hueco": corresponden a columnas que nacen/mueren por los
  repliegues reales del edificio (P2/P3 menos area que P1/P4) y a duplicados de
  zona parte_1/parte_2 en regiones solapadas. No son errores del 3D: el modelo
  3D representa fielmente cada columna de building_master en su piso.
- 41 columnas fuera de las 27 relaciones: columnas legitimas de piso (p.ej.
  perimetros de repliegue P2, columnas solo de fundacion, etc.).

## Elementos POSIBLE modelados

Se modelaron todos los elementos activos de building_master, incluidos los de
revision `POSIBLE`/`FRAGMENTADO`/`NEEDS_REVIEW` que tienen `modelable_3d=True`:
- Vigas POSIBLE/FRAGMENTADA: modeladas con trazabilidad `estado_revision`.
- Muros POSIBLE/FRAGMENTADO: modelados.
- Fundaciones (todas NEEDS_REVIEW): modeladas como tiras nominales.

Los elementos con `FALSO_POSITIVO` o `modelable_3d=False` (columnas de detalle
CAD superior, vanos, ejes no estructurales) NO se modelaron como solidos.

## Problemas menores / pendientes

1. Relleno de losa por caja envolvente de bucle (slab fill): referencia visual;
   el relleno poligonal real de cada losa es refinamiento posterior.
2. Seccion de vigas: se usa la seccion confirmada V.60/80; el 3D no distingue
   automaticamente la viga especial 30x45 (requiere enlazar etiqueta->viga).
3. Espesor de muros: 0.22 m sin refinar por muro; las etiquetas M.H.A. del DXF
   muestran e=15/20/25/30.
4. Fundaciones con seccion nominal (NEEDS_REVIEW).
5. Columnas duplicadas en regiones solapadas parte_1/parte_2 (misma columna
   cerca de x~27.5). Proviene de building_master; se conservan sin fusionar.
