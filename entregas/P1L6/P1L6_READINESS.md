# P1L6 readiness

Fecha: 2026-09-29  
Rama: `codex/p1l5-integration`

## Estado final

| Componente | Estado | Evidencia |
|---|---|---|
| Geometría canónica | PASS | 625 elementos: 442 vigas, 143 columnas, 30 muros y 10 losas |
| Fusiones físicas | PASS | cinco cadenas E2-P4 consolidadas con `merged_from`; crosswalk FE 1:N preservado |
| `E1-P1-C-023` | PASS | sección corregida a 0,70×0,70 m por continuidad vertical |
| `E1-P3-V-101` | PASS | extendida a la cara/nodo estructural existente |
| Losas | PASS | 10 polígonos CURRENT, 6.887,299 m², 18 huecos, espesor 0,15 m, 0 shells FE |
| Apoyos | PASS | 33 visuales = 33 FE; fijos en 6 GDL; 13 extras archivados |
| FE | PASS | 1.100 nodos, 623 segmentos físicos, 1.225 restricciones, 0 componentes desconectados |
| Cargas | PASS_WITH_NOTE | 44 paños; 10 cargas especiales siguen explícitamente unresolved |
| Conservación G | PASS | residual 0,027 N (3,62×10⁻⁸ %) |
| Conservación Q | PASS | residual numérico ≈ 0 N |
| OpenSees G/Q/EX/EY | PASS | finito y equilibrio relativo ≤ 3,58×10⁻¹⁴ |
| Superposición R | PASS | misma K, apoyos, ejes y orden; combinación lineal en Unity |
| Capacidad | PASS_WITH_NOTE | 615/615 miembros; 16 firmas; armaduras/recubrimientos `APPROX / ASSUMED_FOR_LAB` |
| Flujo CURRENT | PASS | hashes de geometría, payload y cargas; fallback histórico bloqueado |
| Unity compile | PASS | Unity 6000.6.0f1 sin errores C# |
| Dataset AR | PASS | 658 registros; 615 con resultados y capacidad |
| Referencia Luis | PASS | `entregas/P1L2/unity_export/model_viewer.json` sin modificar |

## Resultados CURRENT

- G total: **75.803,505 kN**.
- Q total: **24.349,143 kN**.
- G propio: **32.945,738 kN**.
- G sobrecarga permanente: **42.857,767 kN**.
- segmentos exportados por caso: 619; cuatro segmentos redundantes dentro de
  clusters rígidos se omiten para evitar lazos de deformación nula.

## Capacidad

La capacidad es un cribado académico separado del FE lineal global. `f'c` y
`fy` se toman de planos cuando su alcance aplica; las cuantías, recubrimiento y
factores se declaran en cada `capacity_signature`. Unity muestra demanda,
capacidad, D/C y estado. No debe presentarse como verificación normativa.

## Preparación AR

`preparation/current_ar_elements.json` contiene identidad, coordenadas de
modelo/Unity, orientación, longitud, sección, material, resultados R,
desplazamientos, capacidad y carga/tributaria. La primera demostración debe usar
`E2-P1-C-002` y `E2-P1-V-032`.

| Requisito P1L6 | Estado | Alcance actual |
|---|---|---|
| Image tracking preparado | NOT READY | Se implementa en P1L6; falta escoger/cargar la imagen física de referencia y activar AR Foundation |
| Registro espacial preparado | READY | contrato de ejes y `ArCoordinateTransform.cs`; falta medir la pose del ancla en terreno |
| `elementTag` consistente | READY | 658 identidades únicas con crosswalk a `solidTag` y tags OpenSees |
| Resultado estructural disponible | READY | 615 miembros con G/Q/EX/EY, R derivado y capacidad |
| Coordenadas documentadas | READY | modelo ↔ Unity ↔ matriz de ancla AR |
| Dataset AR preparado | READY | 658 registros CURRENT y dos candidatos de demo |

## Pendientes que no bloquean P1L6

Las 10 cargas especiales sin receptor o unidad inequívoca siguen
`UNRESOLVED`; no se sustituyen por cero ni se inventan receptores. La capacidad
usa hipótesis de laboratorio visibles. Estos puntos son limitaciones declaradas,
no inconsistencias ocultas del contrato CURRENT.
