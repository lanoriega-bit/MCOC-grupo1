# E12 SOURCE COVERAGE AUDIT — FINAL

- Fecha: 2026-09-05
- Solo auditoría. Sin cambios de geometría, sin regeneración, sin commit. Verdict entregado.
- Fuentes reales auditadas: `building_master.json`, `piso_01..04.json`, `subterraneo_01.json`, `fundacion.json`, `niveles.json`, `sistema_global.json`, `alignment_final.json`, `calibration_offsets.json`, `region_specs.json`, `planos_index.json`, `dxf_region_analysis.json`, `reextraction_summary.json`, `conflicts_global.json`, `building_to_3d_map.json`, `relaciones_verticales.json`.

## SOURCE COUNTS

`building_master.json` (= consolida los piso/fundacion files; elementos=3255, modelables_3d=2676):

- beams (viga): **1251**
- columns (columna): **142**
- walls (muro): **603**
- foundations (fundacion/ápoyo): **314**
- slab/perimeter (perimetro_losa): **388**
- (+ ejes_CAD `eje_grafico` 395, vanos `vano` 162 — nunca se renderizan)

## SOURCE → OUTPUT = STRUCTURAL + CONTEXTO + EXCLUDED(reason)

Todo elemento del `building_master` existe en las fuentes y el cierre es EXACTO:

| tipo | SOURCE | ESTRUCTURAL (render) | CONTEXTO | EXCLUDED (motivo explícito) |
|---|---|---|---|---|
| viga | 1251 | 999 | 73 | 179 = 169 fundacion (fuera del loop de pisos: líneas de cimentación bajo placa) + 10 piso1 `modelable_3d=false` (`detalle_cad_superior_no_planta_principal`) |
| columna | 142 | 125 | 0 | 17 = 14 fundacion pedestales (no leídas del loop de pisos) + 3 piso1 `modelable_3d=false` (detalle) |
| muro | 603 | 211 | 179 | 213 = 210 fundacion (muros bajo placa/cimentación, fuera del loop) + 3 piso1 `modelable_3d=false` |
| support/fundacion | 314 | 201 | 113 | 0 |
| perimetro_losa | 388 | (361 modelables → caras de losa; 60 losas renderizadas) | 0 como elemento | 27 = 21 fundacion + 6 piso1 non-modelable |
| eje_grafico | 395 | 0 | 0 | 395 (ejes/anotación CAD, nunca renderizados) |
| vano | 162 | 0 | 0 | 162 (vanos = espacio negativo, nunca renderizados) |

Cierre verificado: 1251=999+73+179; 142=125+0+17; 603=211+179+213; 314=201+113+0. **No hay elementos perdidos sin explicación.**

## CURRENT RENDER COUNTS

E2: 125 columnas, 999 vigas, 211 muros, 201 apoyos, 60 losas. (Los 365 CONTEXTO y los EXCLUDED siguen EN el proyecto/datos, sólo no se dibujan.)

## CONTEXT COUNTS

- 365 = 73 viga + 179 muro + 113 support.
- Por piso: -1:82, 0:113, 1:50, 2:40, 3:40, 4:40.
- Por banda (detección geométrica, ver `e12_source_coverage_audit.json`):
  - **NORTH_1S** parte_1, F-1, y[21.97,49.04]: 42 (37 muro/5 viga) — zona `2017_67-101_s1` (PLANTA CIELO 1º SUBTERRANEO, ventana y 4400–9000).
  - **SOUTH_P2** parte_2, F-1..3, y[-10.70,-0.0]: 72 (56 muro/16 viga) — zona `2024_22-101_1S/1/2/3`.
  - **WEST_P2** parte_2, x[-3.85,-1.25], F-1..4: 128 (80 muro/48 viga) — `2024_22-101` y `2024_22-102` (ala/fachada oeste).
  - **P1_SE** parte_1, F1, x[61.24,72.74] y[-6.30,-3.50]: 10 — `2017_67-101_p1` (ala sur del edificio viejo en piso 1).
  - **SUPPORT** F0, parte_1 (77) y parte_2 (36): 113 — `2017_67-100` + `2024_22-100`, y[-11.71,29.02] y x[-4.04,27.96] (zapatas/cimientos de las alas y bandas).

Los 365 IDs existen como elementos en `building_master`/piso files **y** tienen sólido 3D en `building_to_3d_map.json` (365/365) → la geometría "completa" de esas regiones sí está en las fuentes.

## REAL_BUILDING_CONTEXT

- **count: 323** = SOUTH_P2 72 + WEST_P2 128 + P1_SE 10 + SUPPORT 113.
- IDs/grupos: ver grupos en `e12_source_coverage_audit.json` (IDs completos).
- Razones de ser geometría real (no ruido):
  - Provienen de planos reales titulados (`PLANTA CIELO 1ºSUBTERRANEO a CIELO PISO 3º`, `PLANTA FUNDACIONES`, `PLANTA CIELO PISO 1º`) con ventanas de región confirmadas (`planos_index.json`, `region_specs.json`, confidence MEDIUM/HIGH).
  - La zona parte_2 tiene **control por columnas** (8/8 por piso + 32 pilares en `2024_22-101`) → posición confiable.
  - Mantienen contragravidad verificada/P de losa (payload intacto) y continuidad espacial con muros/vigas ESTRUCTURAL del mismo piso.
  - Los 113 support corresponden a zapatas RLE-FUNDACION dibujadas de esas alas/bandas (no hay muro sin zapata).
- Clasificación propuesta: mostrar como **VISUAL_ONLY** (REAL_VISUAL_ONLY), SIN respuesta FE (no inventada).

## CAD_DETAIL_ONLY

- **count: 593** = 395 ejes_CAD + 162 vanos + 22 detalle piso1 non-modelable (10 viga/3 muro/3 col/6 perim, `detalle_cad_superior_no_planta_principal`, low conflict) + 14 pedestales de fundacion.
- Nunca renderizados por diseño. No afectan la completitud visual del cuerpo del edificio.
- Nota: de los 365 CONTEXTO, 21 muestran categoría `FALSO_POSITIVO` en la fuente (1 NORTH + 12 SOUTH + 5 WEST + 3 P1_SE). Son fragmentos de cortes de ventana/hoja, NO ruido puro: conservan continuidad con la misma banda. Recomendación: mantenerlos como VISUAL_ONLY con flag de baja confianza, o excluirlos opcionalmente sin afectar completitud.

## UNRESOLVED

- **count: 42** = banda NORTH_1S parte_1 (y[21.97,49.04], `2017_67-101_s1`).
- Contenido = plan real del subterráneo del edificio viejo; confianza media (categorías fuente: 30 POSIBLE, 11 FRAGMENTADO, 1 FALSO_POSITIVO).
- **Problema de ALINEACIÓN, no de geometría**: la región no tiene columnas (0 RLE-PILAR; conflicto documentado `1S_parte_1_sin_columnas_control` → `modelado_como_POSIBLE`; `dxf_region_analysis` confirma pilares sólo y[709,3593]=ventana P1). Su posición Y es la normalización de ventana (dy del CALCE), no verificable por columnas.
- No es CAD detail (es plan real) ni tiene FE. No eliminar; si se muestra, marcar como ALIGNMENT_UNVERIFIED.

## FLOOR COVERAGE (5 m cells, E2)

| floor | SOURCE cells | RENDERED cells | coverage | regiones faltantes |
|---|---|---|---|---|
| -1 | 63 | 49 | 78% | banda N (1S parte_1) + ala S parte_2 |
| 1 | 80 | 77 | 91% | ala S parte_2 (+2 cel. SE) |
| 2 | 79 | 73 | 91% | ala S parte_2 |
| 3 | 76 | 73 | 93% | ala S parte_2 |
| 4 | 83 | 85 | 99% | (completo; el exceso son celdas de grid de columnas) |

SOURCE footprint por piso (bbox de muros+vigas+columnas+perímetros modelables): F-1 x[-5,75] y[-15,45]; F1 x[-5,75] y[-15,20]; F2 x[-5,70] y[-15,25]; F3 x[-5,70] y[-15,20]; F4 x[-5,80] y[-5,25].

## MISSING VISUAL REGIONS

1. **Ala SUR parte_2** (y<0), F-1..3 — 72 elems. Fuente: `2024_22-101_{1S,1,2,3}`. Estado: **CONTEXTO** hoy. Existe en fuente. Puede renderizarse como VISUAL_ONLY (posición confiable).
2. **Ala/fachada OESTE parte_2** (x<0), F-1..4 — 128 elems. Fuente: `2024_22-101`+`2024_22-102`. Estado: **CONTEXTO**. Existe. VISUAL_ONLY.
3. **Banda N 1S parte_1** (y 22–49), F-1 — 42 elems. Fuente: `2017_67-101_s1`. Estado: **CONTEXTO**. Existe. VISUAL_ONLY con flag ALIGNMENT_UNVERIFIED.
4. **Zapatas de las alas/bandas** — 113 support. Fuente: `2017_67-100`+`2024_22-100`. Estado: **CONTEXTO**. Existe. VISUAL_ONLY.
5. **Detalle CAD superior piso1** (y 21.9–28.3) — 22 elems `modelable_3d=false`. Fuente: `2017_67-101_p1`. Estado: **EXCLUDED** (razón documentada). No reponer como estructura; opcional visual si se quiere el cornizo.

## E1/E2 VISUAL INTERFACE

- **Geometría presente: SI** (tanto en E1 como en E2).
- **Fuentes**: la unión física del sitio es UNA losa continua. E2 (generación actual, frame global) ya contiene el sitio completo: parte_2 x[0.1,27.6] + parte_1 x[27.5,77.5]; la junta queda en x≈27.491 (Eje A-1 de Parte2). E1 (`edificio1_unity.json`, generación P1L2) es el edificio viejo en **coordenadas locales** x[0,50] y con interpretación anterior (1S con 34 columnas aunque la reextracción dio 0).
- **Problema**: E12 (vista "Both") combina E1 local + E2 global **sin reconciliar** → el edificio viejo se dibuja 2 veces: 83/125 columnas E2 caen dentro del bbox de E1 y 143/149 columnas E1 dentro del bbox de E2. La zona de unión coincide con la banda SOUTH_P2/WEST_P2 que hoy está filtrando como CONTEXTO.
- No inventar conexión FE; el puente visual de la unión es la geometría E2 global (existe). Requiere decisión de composición E12 (E1 en global o usar sólo E2 como sitio completo), no de geometría.

## FINAL VERDICT

### **A — FULL VISUAL GEOMETRY RECOVERABLE FROM EXISTING SOURCES**

Toda la geometría del edificio (muros, vigas, columnas, zapatas, perímetros de losa de todos los pisos) **existe en las fuentes**. La vista "incompleta/amputada" se debe al FILTRO (no a datos faltantes): se ocultaron bandas que son geometría REAL de planos. No hace falta inventar nada.

Elementos que deben volver al viewer como **REAL_VISUAL_ONLY** (323):
- SOUTH_P2 72 + WEST_P2 128 + P1_SE 10 (muros/vigas de las alas sur y oeste, parte_2 y piso1 parte_1) — `2024_22-101/−102`, `2017_67-101_p1`.
- SUPPORT 113 (zapatas de esas alas/bandas) — `2017_67-100`, `2024_22-100`.

Opcional (42) con flag **ALIGNMENT_UNVERIFIED**:
- NORTH_1S parte_1 (subterráneo del edificio viejo, plano real, posición no controlada por columnas).

Permanecer ocultos (CAD_DETAIL_ONLY, no afectan completitud): eje_grafico 395, vano 162, detalle piso1 22, pedestales 14. Los 21 fragmentos FALSO_POSITIVO de las bandas reales se mantienen con flag opcional de baja confianza.

Trabajo pendiente (no de geometría): decidir composición E12 para E1+E2 evitando duplicar el edificio viejo (E1 local vs E2 global) y, si se recupera NORTH_1S, rotular su alineación como no verificada. Ninguna respuesta FE se inventa para estas zonas.

Archivos de apoyo: `e12_source_coverage_audit.json` (grupos + IDs + coords), `E12_GEOMETRY_DIAGNOSTIC.md`, `E12_FLOATING_GEOMETRY_AUDIT.md`.