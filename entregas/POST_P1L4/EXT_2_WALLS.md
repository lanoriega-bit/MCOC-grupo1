# EXT-2 — Auditoría completa de muros

> Los repos externos son pistas secundarias. Toda corrección aplicada se confirmó en 2017_67 o 2024_22.

## Resultado

- Muros físicos auditados: `122` (`68` EDIFICIO_1 + `54` EDIFICIO_2).
- EDIFICIO_2 corregido: `100` prismas de caras → `54` centrolineas físicas; `46` caras/cierres redundantes retirados.
- OpenSees, cargas, masas, EX/EY, R y capacidad: **no recalculados**.

| Clasificación geométrica | Cantidad |
|---|---:|
| CONFIRMED_ALL_THREE | 62 |
| CONFIRMED_OURS_PLUS_ONE | 32 |
| GEOMETRY_MISMATCH | 9 |
| OURS_ONLY | 19 |

## Métricas por edificio y piso

| Edificio | Piso | Auditados | 3/3 | 2/3 | Solo nuestro | Geom. mismatch | Espesor mismatch |
|---|---|---:|---:|---:|---:|---:|---:|
| EDIFICIO_1 | S1 | 22 | 4 | 10 | 7 | 1 | 2 |
| EDIFICIO_1 | P1 | 25 | 2 | 8 | 12 | 3 | 2 |
| EDIFICIO_1 | P2 | 7 | 4 | 3 | 0 | 0 | 2 |
| EDIFICIO_1 | P3 | 7 | 4 | 3 | 0 | 0 | 2 |
| EDIFICIO_1 | P4 | 7 | 4 | 3 | 0 | 0 | 2 |
| EDIFICIO_2 | S1 | 11 | 9 | 1 | 0 | 1 | 0 |
| EDIFICIO_2 | P1 | 11 | 9 | 1 | 0 | 1 | 0 |
| EDIFICIO_2 | P2 | 11 | 9 | 1 | 0 | 1 | 0 |
| EDIFICIO_2 | P3 | 11 | 9 | 1 | 0 | 1 | 0 |
| EDIFICIO_2 | P4 | 10 | 8 | 1 | 0 | 1 | 0 |

## Balance de correcciones

- Muros faltantes confirmados en fuente primaria: `0`.
- Muros sobrantes: `46` prismas de caras/cierres EDIFICIO_2 retirados.
- Duplicados reales: las caras opuestas no eran dos muros; quedaron fusionadas por centrolinea.
- Fragmentaciones incorrectas confirmadas: `0`; un patrón externo 1:N queda solo como pista.
- Espesores corregidos/trazados: `54` muros EDIFICIO_2.
- Unresolved externos: `4` sin respaldo primario; no se incorporaron.

## Decisiones especiales

- `E1-P4-M-007`: se mantiene como muro real de shaft. La continuidad S1→P4 y el espesor quedan respaldados por `2017_67`; no apareció duplicado inequívoco.
- `E1-P1-M-016` y `E1-P1-M-023`: permanecen como muros reales vinculados al contexto de contención/escalera; la topografía explica su lectura física.
- EDIFICIO_2 P4: `10` muros físicos confirmados desde `2024_22-102`; no se crearon conexiones FE artificiales.
- Diferencias de espesor externas se registran, pero no sustituyen espesores medidos en los planos.

Elementos externos sin match: `4` ({'EXTERNAL_ONE_ONLY': 4}); todos quedan `REVIEW_REQUIRED_EXTERNAL_ONLY` y no fueron agregados.

## Artefactos

- `STRUCTURAL_CROSS_REPO_COMPARISON.json`: registro muro por muro.
- `ed2_walls/ed2_wall_face_audit.json`: prueba primaria de pares de caras, cierres y espesores.
- `ed2_walls/ed2_wall_resolution.json`: crosswalk de la corrección.
- `overlays/walls_*.png`: 10 overlays por edificio/piso.
