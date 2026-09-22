# EXT-6 — Cobertura técnica entre grupos

Fecha: 2026-09-22. Revisión de código/datos/documentación; no se ejecutaron
scripts ni Unity externos, ni se certifica su funcionamiento por leerlos.
Repos externos READ ONLY / push deshabilitado en clones de contraste.

Snapshots: Santiago `c1f434b99b4156d6d0932b55f6f764d981518126`;
Cáceres P1L4 `b4a7bd8`, contraste reciente
`93fba4a524193404d63a21e7696db135097d9678`. Su geometría manual y carpeta data
no cambian entre esos dos snapshots. Las adiciones recientes SQ4/carga móvil
pertenecen a una etapa futura y no se integran aquí.

“Mejor” significa ventaja concreta observable, no mayor validez estructural.
Los requisitos se reconstruyen de informes y código; no se dispone de una
pauta externa independiente adicional. Consenso no sustituye planos.

| Requisito / función | Nuestro grupo | Santiago | Cáceres | Ventaja observada | Clasificación / acción |
|---|---|---|---|---|---|
| P1L2 columnas | 150 con IDs/ejes y auditoría | Geometría exportada CAD | Modelo manual por ejes | Nuestro QA fuente-elemento | ALREADY_HAVE_BETTER: conservar |
| P1L2 vigas | 567 físicas; 19 alturas pendientes | Barras/secciones exportadas | 612 barras exportadas; secciones equivalentes VAR | Comparación ofrece pistas, no alturas probadas | USEFUL_NEEDS_ADAPTATION: relectura de etiquetas/cortes |
| P1L2 muros | 122 físicos; ED2 54 | 75 muros del modelo P1L4 | 24 padres / 82 segmentos de piso | Cáceres conserva jerarquía padre/piso | USEFUL_NEEDS_ADAPTATION: conservar procedencia sin copiar discretización |
| Pisos/ejes/calce | Ejes canónicos y residuales | Unificación de edificios | Coordenadas manuales | Nuestro contrato explícito | ALREADY_HAVE_BETTER |
| Losas/huecos | Provisionales, S1/P1 abiertos | 226 paños | 652 paños; resta explícita de vacíos | Cáceres: balance área bruta/neta | USEFUL_NEEDS_ADAPTATION: pista, no cerrar nuestros perímetros |
| Tributarias | Conservación y multizona | Consulta por losa/viga | Regiones de cargas y transferencia por paño | Complementarios | KEEP; no sustituir por geometría externa |
| Q / cargas 700 | Catálogo trazable, faltan decisiones | Intensidades por paño | Cargas_losas + conversión | Cáceres: separación región/void | USEFUL_NEEDS_ADAPTATION; no copiar magnitudes sin lámina |
| G / PP.LOSA | Histórico vs catálogo separados | Peso propio + sobrecarga | PP/SC/PMAD por región | Trazabilidad por origen | Mantener separación G/Q y unidades |
| EX/EY y masas | Históricos G+0.5Q, verificaciones | F=0.20W y consultas | Casos y reporte estructural | No ventaja que justifique reemplazo | ALREADY_HAVE_BETTER / DOCUMENT_ONLY |
| Superposición | Corrida explícita y error por respuesta | Casos y lambdas | Casos y combinaciones | Método común | STILL_VALID_METHOD, inputs actuales requieren recálculo |
| FE / apoyos | 856 candidato, no correr aún | Fija componentes aislados | Shells y vínculos frame-shell | Ningún atajo resuelve nuestros apoyos | Rechazar fijaciones ficticias; no importar shell sin QA |
| Restricciones | 1482 brazos; cadenas/multi-maestro | Modelo simplificado | equalDOF / penalización | Necesitamos validación propia | FE-2: propuesta algebraica separada, no aplicada |
| Materiales | UNKNOWN / M.H.A. no es resistencia | H30/fc25 inconsistente | fc35 y acero420 documentados | Pista Cáceres → releer notas 100 | USEFUL_NEEDS_ADAPTATION: confirmar fuente primaria |
| Armaduras | Capacidad ASUMIDO_LAB | Sección 8Ø25 / simplificaciones | Tablas por eje/piso; 16Ø22 ejemplo | Cáceres ofrece detalle adicional | Investigar; conflicto H/V en tabla impide copiar globalmente |
| Fiber / M-phi | Análisis HA separado | M-phi aproximado y PM simplificado | Compatibilidad deformaciones | Comparar hipótesis, no mezclar curvas | No regenerar capacidades históricas |
| P-M muro | Supuestos explícitos | Visualización de capacidad | Resultantes de shells por piso | Cáceres: demanda agrupada por muro | USEFUL_NEEDS_ADAPTATION; exige FE equivalente aprobado |
| P-M varios casos | Caso activo | Varias combinaciones sobre curva | Envolventes y casos | Santiago: comparación didáctica | USEFUL_NEEDS_ADAPTATION; no añadir demandas CURRENT inexistentes |
| Diagramas N/V/M | End actions etiquetadas | Recta + parábola auxiliar | Convención corte normal +x | Cáceres: signos/equilibrio explícitos | ADOPTADO QA local; rechazar parábola sin element load |
| Deformada | Histórica con aviso | Deformada por nodos | Hermite con seis DOF | Cáceres: curvatura de barra | USEFUL_NEEDS_ADAPTATION; no adoptada en esta etapa |
| Ejes locales | Geométricos actuales vs FE históricos | Ejes en viewer | Triada exportada y probada | Cáceres: test ortonormalidad/orientación | ADOPTADO test propio a 1312 triadas |
| QA fuerzas | QA global + ejemplo manual | QA por entrega | Equilibrio de todas las barras/casos | Cáceres: cobertura exhaustiva | ADOPTADO 6560 checks sin recalcular |
| JSON | Hashes, datasets, crosswalk 1:N | Export unificado enriquecido | Resultados y provenance por barra | Nuestro aislamiento histórico/actual | ALREADY_HAVE_BETTER; reforzar metadata |
| Unity / filtros | UI semántica, filtros, modo limpio | Inspector/casos/PM | Inspector/diagramas/resultados | Complementarios; sin test externo en vivo | Mantener Unity canónico |
| Historia de entregas | ENTREGAS + evolución por Git | README por entrega | Documentación organizada | Nuevo panel propio | ADOPTADO HIST-1, sin copiar código |
| Contexto/escaleras | Capa visual separada de FE | Parcial | Geometría manual parcial | No prueba para topografía métrica | NOT_RELEVANT para apoyos FE |
| Documentación | Históricos + backlog/current | Menús/ejemplos explicativos | Métodos y pruebas separados | Ambos útiles didácticamente | ADOPTADO auditoría retrospectiva propia |
| Carga móvil SQ4 | No iniciada | Fuera de esta revisión | Implementada en commits recientes | Función futura | NOT_RELEVANT: no implementar P1L5 |

Fuentes y decisiones concretas: informes separados Santiago/Cáceres. No se
importaron scripts externos completos ni resultados externos a nuestro Unity.
La revisión no equivale a una auditoría de seguridad ni a ejecutar cada ruta
de sus aplicaciones. Las diferencias geométricas por elemento siguen en los
crosswalks EXT-1/2/3, no se reemplazan por esta matriz funcional.
