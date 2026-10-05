# Auditoría de contexto físico POST-P1L3

Estado: `AUDITED_DIAGNOSTIC_ONLY`. Se detiene antes de modificar OpenSees.

## Resultado ejecutivo

- Casos pendientes reevaluados: **40**.
- Geometría física confirmada o explicada por contexto: **38**.
- Pendientes reales sin nueva evidencia: **2** (`E2-P4-V-050/051`).
- Duplicados inequívocos encontrados en el núcleo: **0**.
- Elementos eliminados: **0**.
- Conexiones/apoyos FE añadidos: **0**.
- G, Q, EX, EY, R, P-M y demanda-capacidad: **intactos**.

## 1. Cotas exteriores A/B/C/D

| Lado | Interpretación | Relación vertical | Confianza |
| --- | --- | --- | --- |
| A | Cota exterior continua no cerrada | No se afirma enterramiento uniforme | REVIEW_REQUIRED |
| B | Acceso exterior aproximadamente en P1 | S1 enterrado en gran parte | USER_CONFIRMED_PLUS_BUILDING_GEOMETRY |
| C | Cota exterior continua no cerrada | No se afirma enterramiento uniforme | REVIEW_REQUIRED |
| D | Terreno/radier variable próximo a P1 | S1 enterrado en gran parte | PLAN_AND_USER_CONFIRMED |

La lámina `2017_67-101` registra `RADIER SOBRE TERRENO`, N.O.G. `-1.90`, `-1.54`, `-0.95` y N.S.M. `+0.95`; por eso no corresponde imponer un único plano de terreno. Los niveles estructurales de control son S1 `-4.01`, P1 `-0.05`, P2 `+3.91`, P3 `+7.87` y P4 `+11.83` m. No se generó una superficie 3D continua: faltan cotas suficientes en A/C.

## 2. Acceso/escalera D

`E1-P1-M-016` y `E1-P1-M-023` son centrolineas de muros de 0.15 m confirmadas por pares de contorno `RLE-MURO`; no son caras duplicadas. Junto con M-020/021/022/024/035/036/037 delimitan el recinto exterior. V-068/072/098 son vigas profundas de 1.00–1.25 m asociadas a borde/descanso. La clasificación física se corrige a muro de contención/miembro de escalera, pero su apoyo y participación definitiva en el FE quedan para un hito posterior.

## 3. Acceso/escalera B

`E1-P1-C-016/017` son símbolos de pilar 0.35 x 0.35 m trazados directamente en `2017_67-101`, fuera del eje H. Se clasifican como apoyos de escalera exterior, no como columnas interiores flotantes. `E1-P2-V-055` y `V-075` forman una línea continua de 9.95 m y llegan por huella a las vigas transversales del borde; se clasifican como vigas de descanso/estructura secundaria. El algoritmo por centrolineas no capta ese contacto de huellas.

## 4. Núcleo de ascensores S1–P4

Los seis paños base de S1 reaparecen con iguales espesores, orientaciones y casi las mismas coordenadas en P2, P3 y P4. P1 conserva ambos cierres principales, con el corrimiento de 0.181 m de su propia planta. `E1-P4-M-007` es el cierre horizontal de 0.20 m del shaft sur, no una cara duplicada. Los laterales de 0.25/0.30 m son retornos. Cada muro consolidado ya proviene de un par de caras CAD; no se encontró `DUPLICATE_EXTRACTION` inequívoco.

## 5. Nueva clasificación de los 40 casos

| Elemento | Antes | Cluster | Geometría física | Soporte físico | FE principal |
| --- | --- | --- | --- | --- | --- |
| `E1-P1-C-016` | UNRESOLVED | STAIR_ACCESS_B | EXTERIOR_STAIR_SUPPORT | EXTERIOR_FOUNDATION_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-C-017` | UNRESOLVED | STAIR_ACCESS_B | EXTERIOR_STAIR_SUPPORT | EXTERIOR_FOUNDATION_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-004` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P1-M-010` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P1-M-016` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-020` | DISCONNECTED_ERROR | STAIR_ACCESS_D | EXTERIOR_STAIR_SUPPORT | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-021` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-022` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-023` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-024` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-031` | DISCONNECTED_ERROR | STAIR_ACCESS_D | EXTERIOR_STAIR_MEMBER | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-034` | DISCONNECTED_ERROR | STAIR_ACCESS_D | EXTERIOR_STAIR_MEMBER | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-035` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-036` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-M-037` | DISCONNECTED_ERROR | STAIR_ACCESS_D | RETAINING_WALL | TERRAIN_SUPPORTED_REVIEW | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-V-068` | UNRESOLVED | STAIR_ACCESS_D | LANDING_BEAM | MEMBER_FOOTPRINT_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-V-072` | UNRESOLVED | STAIR_ACCESS_D | LANDING_BEAM | MEMBER_FOOTPRINT_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P1-V-098` | UNRESOLVED | STAIR_ACCESS_D | LANDING_BEAM | MEMBER_FOOTPRINT_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P2-M-003` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-M-005` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-M-007` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-M-008` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-M-009` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-M-010` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P2-V-055` | UNRESOLVED | STAIR_ACCESS_B | LANDING_BEAM | MEMBER_FOOTPRINT_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P2-V-075` | UNRESOLVED | STAIR_ACCESS_B | LANDING_BEAM | MEMBER_FOOTPRINT_CONNECTION | SECONDARY_STRUCTURE_EXPECTED |
| `E1-P3-M-003` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P3-M-005` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P3-M-007` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P3-M-008` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P3-M-009` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P3-M-010` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-003` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-007` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-008` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | SHAFT_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-009` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-010` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E1-P4-M-012` | DISCONNECTED_ERROR | CORE_ELEVATOR_P1_P4 | RETURN_WALL | VERTICAL_CONTINUITY_CONFIRMED | PRIMARY_FE_REVIEW_REQUIRED |
| `E2-P4-V-050` | UNRESOLVED | ED2_REVIEW | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| `E2-P4-V-051` | UNRESOLVED | ED2_REVIEW | UNRESOLVED | UNRESOLVED | UNRESOLVED |

## 6. Impacto y recomendación FE posterior

- Núcleo: diseñar una conexión por intersección/solape y continuidad vertical que conserve un solo eje resistente por muro; validar rigidez y equilibrio antes de ejecutar.
- Escalera B: decidir explícitamente si la estructura secundaria entra al global. Si entra, conectar por huella real a las vigas transversales y documentar apoyos exteriores.
- Escalera D: identificar fundaciones/contención receptoras antes de agregar `fix()` o enlaces. La cercanía al terreno no autoriza apoyo automático.
- EDIFICIO_2: mantener V-050/051 como `UNRESOLVED_REAL` hasta revisar su planta fuente.
- Crear un dataset futuro `POST_P1L3 / P1L4_NEW_RUN`; nunca sobrescribir los 1312 miembros/resultados históricos P1L3.

## 7. Unity y overlays

Unity consume `p1l4_physical_context.json` como capa `CONTEXTO FÍSICO`, apagada por defecto y marcada `participates_in_FE=false`. Se muestran regiones, labels y marcadores de nivel; no se inventa terreno continuo.

- `cluster_stair_access_B.png`
- `cluster_stair_access_D.png`
- `cluster_core_elevator_S1_P4.png`
- `terrain_levels_A_B_C_D.png`

## Fuentes revisadas

`2017_67-100..103`, `2017_67-300..310`, `2017_67-500..503`, modelo consolidado, diagnóstico FE POST-P1L3 e información física aportada por el usuario. Los planos `2017_67` están emitidos para propuesta; las conclusiones se conservan con su nivel de confianza.
