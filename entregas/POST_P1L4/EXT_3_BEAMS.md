# EXT-3 — Auditoría exhaustiva de vigas

Estado: `PASS_WITH_CONNECTIVITY_REVIEW`

Los repos de Santiago y Cáceres se usaron únicamente como contraste. Las
correcciones aplicadas provienen de `2017_67-101/102/103` y
`2024_22-101/102`; una coincidencia externa sin evidencia primaria no genera
una viga nueva ni elimina una existente.

## Resultado canónico

| Edificio | Fuente CAD auditada | Representación anterior | Vigas físicas | Acción |
|---|---|---:|---:|---|
| EDIFICIO_1 | 553 segmentos `RLE-VIGA` | 545 prismas históricos | 300 | Revalidado, sin cambios nuevos |
| EDIFICIO_2 | 520 segmentos `RLE-VIGA` | 515 prismas históricos | 267 | 248 caras/cierres consolidados |
| **Total** | | | **567** | |

EDIFICIO_1 conserva por piso `53/69/64/60/54`. La reconstrucción vuelve a
confirmar 46 cierres cortos y 4 detalles interiores excluidos; no son vigas
resistentes. EDIFICIO_2 queda `44/44/44/44/91`; sus 267 vigas tienen ancho y
altura de sección trazables al plano.

## Comparación entre los tres modelos

| Clasificación | Cantidad |
|---|---:|
| `CONFIRMED_ALL_THREE` | 457 |
| `CONFIRMED_OURS_PLUS_ONE` | 3 |
| `GEOMETRY_MISMATCH` | 58 |
| `OURS_ONLY` | 49 |
| `POSSIBLE_FRAGMENT_EXTERNAL` | 11 |
| `SECTION_MISMATCH` | 10 |

Los 60 candidatos `EXTERNAL_ONE_ONLY` permanecen
`REVIEW_REQUIRED_EXTERNAL_ONLY`; no se incorporaron. Las diferencias se
explican principalmente por discretización, tramos fusionados/fragmentados y
secciones genéricas de los contratos externos. Ninguna reemplazó una sección
medida en nuestros planos.

## Métricas por piso

| Edificio | Piso | Auditadas | 3/3 | 2/3 | Mismatch | Solo nuestro |
|---|---|---:|---:|---:|---:|---:|
| EDIFICIO_1 | S1 | 53 | 8 | 0 | 5 | 40 |
| EDIFICIO_1 | P1 | 69 | 31 | 1 | 28 | 9 |
| EDIFICIO_1 | P2 | 64 | 63 | 1 | 0 | 0 |
| EDIFICIO_1 | P3 | 60 | 59 | 1 | 0 | 0 |
| EDIFICIO_1 | P4 | 54 | 54 | 0 | 0 | 0 |
| EDIFICIO_2 | S1 | 44 | 40 | 0 | 4 | 0 |
| EDIFICIO_2 | P1 | 44 | 40 | 0 | 4 | 0 |
| EDIFICIO_2 | P2 | 44 | 40 | 0 | 4 | 0 |
| EDIFICIO_2 | P3 | 44 | 40 | 0 | 4 | 0 |
| EDIFICIO_2 | P4 | 91 | 82 | 0 | 9 | 0 |

## Casos especiales

### `E1-P2-V-075` — escalera B

- Veredicto: `LANDING_BEAM_CONFIRMED_STAIR_B`.
- Fuente primaria: `2017_67-102`, eje físico de 4.95 m y sección 0.30 × 0.45 m.
- Santiago representa la línea completa de 10.00 m; Cáceres la divide en dos
  tramos de 5.00 m. Nuestro par `E1-P2-V-055` + `E1-P2-V-075` reproduce esa
  continuidad sin perder el cambio de tramo respaldado por el plano.
- La sección genérica V60/80 de Santiago no sustituye la etiqueta primaria.

### `E2-P4-V-050` / `E2-P4-V-051`

- Veredicto: `TWO_FACES_OF_ONE_REAL_BEAM_V60x80`.
- Las dos líneas paralelas están separadas 0.60 m y en `2024_22-102` la llamada
  `V.60/80` confirma que son caras de una única viga.
- Eje físico resultante: `P4-VP-085`, actualmente `E2-P4-V-029`, longitud
  0.80 m, sección 0.60 × 0.80 m.
- Ambos repos externos muestran una sola línea longitudinal; esto es una pista
  secundaria, no la base de la corrección.

## Conectividad geométrica

| Clasificación | Cantidad |
|---|---:|
| `SUPPORTED_BOTH_ENDS_GEOMETRIC` | 247 |
| `SUPPORTED_ONE_END_REVIEW_CANTILEVER_OR_BOUNDARY` | 259 |
| `LANDING_BEAM_CONFIRMED_STAIR_B` | 1 |
| `REVIEW_REQUIRED_CONNECTIVITY` | 60 |

La clasificación usa proximidad a columnas, muros y otras vigas del mismo
piso. No crea nodos ni conexiones artificiales. Los 259 casos de un extremo
incluyen bordes, voladizos y encuentro con tramos cuya segmentación debe ser
resuelta por el adaptador FE. Los 60 casos sin apoyo geométrico automático se
conservan porque su geometría primaria está confirmada; pasan a EXT-5 para
decidir participación FE, no para borrarlos por heurística.

## Secciones y propiedades

- EDIFICIO_2: `267/267` anchos y alturas `CONFIRMED_FROM_PLAN`.
- EDIFICIO_1: `281/300` alturas conocidas y `19` alturas siguen `UNKNOWN`.
  No se inventó una altura estándar para cerrar el conteo.
- Diez discrepancias externas de sección se documentan como pista. Los
  contratos externos frecuentemente usan una sección genérica y no son fuente
  suficiente para modificar propiedades.

## Unity y resultados

El modelo canónico y el bundle de Unity se regeneran con 567 vigas físicas.
Cada viga corregida incluye `post_p1l4_correction`, fuente primaria,
confianza y advertencia de compatibilidad. Los resultados `G/Q/EX/EY/R` y
P-M siguen siendo **P1L4 históricos** y no fueron recalculados.

La compilación Unity 6000.6.0f1 y la prueba automática en Play pasan. El
runtime cargó `909` sólidos y confirmó capas/pisos, diagnóstico, metadatos,
apoyos, casos, diagramas 2D y la secuencia de demostración P1L4. Solo aparecen
advertencias conocidas de serialización y campos no usados; no hay errores C#.

## Artefactos

- `STRUCTURAL_CROSS_REPO_COMPARISON.json`: comparación elemento por elemento.
- `ed2_beams/ed2_beam_centerline_proposal.json`: resolución primaria.
- `ed2_beams/ed2_beam_resolution.json`: crosswalk y preservación de IDs.
- `ed2_beams/VALIDATION.json`: QA reproducible.
- `overlays/beams_*.png`: diez overlays por edificio/piso.
