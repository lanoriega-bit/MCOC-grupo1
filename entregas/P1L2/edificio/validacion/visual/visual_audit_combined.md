# Auditoria visual modelo combinado

- Modelo: `entregas\P1L2\unity_export\model_combined_viewer.json`
- Estado: **PASS**
- Pisos: `['P1', 'P2', 'P3', 'P4', 'S1']`

## Laminas generadas

- `entregas\P1L2\edificio\validacion\visual\01_plantas_por_piso.png`
- `entregas\P1L2\edificio\validacion\visual\02_elevacion_longitudinal_xz.png`
- `entregas\P1L2\edificio\validacion\visual\03_elevacion_transversal_yz.png`
- `entregas\P1L2\edificio\validacion\visual\04_isometrico.png`
- `entregas\P1L2\edificio\validacion\visual\05_tipos_estructurales.png`
- `entregas\P1L2\edificio\validacion\visual\06_nucleo_aislado.png`

## Conteos por piso

| Piso | Columnas | Vigas | Muros | Losas | Apoyos |
|---|---:|---:|---:|---:|---:|
| S1 | 33 | 169 | 80 | 2 | 113 |
| P1 | 40 | 198 | 58 | 2 | 0 |
| P2 | 37 | 202 | 32 | 2 | 0 |
| P3 | 32 | 214 | 32 | 2 | 0 |
| P4 | 34 | 277 | 32 | 2 | 0 |

## Criterio visual

Las figuras revisan forma general, union D/E, cinco pisos, continuidad por vista, elementos por tipo y nucleo aislado. No reemplazan la inspeccion interactiva en Unity/web; son una auditoria reproducible versionable.

## Conclusiones visuales

- Se observan exactamente cinco plantas canonicas: S1, P1, P2, P3 y P4.
- No aparecen niveles exportables adicionales asociados a base, techo, cielo, losa superior o diaphragm.
- La union entre EDIFICIO_1 y EDIFICIO_2 ocurre en el eje comun D/E sin rotacion visible ni doble traslado.
- Las elevaciones X-Z e Y-Z muestran continuidad vertical compatible con los cinco niveles del contrato.
- Los apoyos/fundaciones aparecen solo en S1 como elementos auxiliares de tipo support/foundation; no constituyen un sexto piso.
- El nucleo se mantiene alineado por ejes en todos los niveles; las diferencias de muros entre pisos quedan visibles y trazables.
- Esta auditoria no valida cargas, secciones resistentes ni propiedades de material; esos puntos quedan fuera del cierre geometrico.
