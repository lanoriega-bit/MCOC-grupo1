# Exclusión lateral P1 y explicación de cargas — CURRENT

Rama: `codex/current-slab-reconstruction`. Base histórica intacta: `d81514d`.
El commit evaluable es el que contiene este documento, sin reescribir tags entregados.

## Superficies excluidas

| Edificio / piso | Superficie | Área original m² | Cargas / tributarias |
|---|---|---:|---|
| ED1 / P1 | Norte, L700-E1-P1-H08 | 100,849974 | SC y PM.ADIC retiradas |
| ED1 / P1 | Sur, L700-E1-P1-H10 + H12 | 70,422256 | SC y PM.ADIC retiradas |

Exclusión solicitada por el usuario de dos superficies sin soporte coherente:
seis entradas SC/PM retiradas del catálogo activo, tres paños tributarios eliminados.
Geometría anterior y cargas originales recuperables en `P1_LATERAL_EXCLUSION.json`
y en Git; no se borran fuentes CAD. No se eliminan receptores estructurales válidos:
se reconstruyen sus contribuciones. **Receptores huérfanos = 0**.
H13 es otra extensión con vigas, se conserva. No se recorta por proximidad ni por hull.
ED1-P1 pasa de 997,042426 a 825,770177 m²; mantiene su hueco.
La diferencia ~0,000019 m² entre suma de zonas y recorte físico proviene de precisión
geométrica micrométrica, no de una carga adicional.

## Análisis regenerado

Los resultados se invalidaron antes de cambiar los inputs y se regeneraron:
geometría → cargas → FE → G/Q/EX/EY → capacidades y demanda/capacidad → Unity.
Ahora el contrato es `CURRENT_VERIFIED`; no se reutiliza una corrida vieja.
FE, secciones, materiales y miembros estructurales no cambian.

| Magnitud kN | Antes | Ahora | Cambio |
|---|---:|---:|---:|
| G | 80.517,133 | 78.716,059 | −1.801,074 |
| Q | 23.477,157 | 22.637,353 | −839,803 |
| G + 0,5 Q global | 92.255,712 | 90.034,736 | −2.220,976 |
| Peso usado por grupos sísmicos | 89.989,992 | 87.769,017 | −2.220,976 |
| Acción lateral / corte basal EX o EY | 17.997,998 | 17.553,803 | −444,195 |

El peso global y el de los grupos sísmicos no son idénticos: el segundo corresponde
a `seismic_floor_loads`, no a todos los pesos gravitacionales. Se conserva la
formulación existente y se informa la diferencia, no se cambia silenciosamente.
Reacción vertical total G/Q disminuye por los mismos valores respectivos.
Reacción basal X/Y en su caso disminuye en magnitud 444,195 kN.

| Caso | Máxima traslación anterior mm | Actual mm | Equilibrio |
|---|---:|---:|---|
| G | 11,060 | 11,039 | PASS |
| Q | 2,385 | 2,376 | PASS |
| EX | 68,101 | 66,198 | PASS |
| EY | 98,693 | 96,232 | PASS |

Todos los vectores de reacción/deltas sin redondeo: `P1_LATERAL_QA.json`.
Capacidad/D-C regenerados: 669 registros; seis cargas puntuales unresolved
siguen excluidas explícitamente, no interpretadas como cero confirmado.

## Unity

- Modelo → **Losas**, OFF al iniciar; diez superficies blancas transparentes.
- Bordes de losa CAD, Referencias CAD y Ejes CAD: controles retirados y segmentos
  CAD no construidos en el Viewer. La evidencia sigue disponible para auditoría.
- Seleccionar viga → Ficha estructural → **CARGAS**: Q base, área, ancho, wQ,
  Q transferida, λQ y equivalencia en R. G/EX/EY siguen la misma explicación.
- Tooltip: λ=1 usa la respuesta del caso base, λ=2 aporta el doble, λ=0 la omite.
  No reejecuta OpenSees ni cambia la formulación. qQ es media ponderada multizona;
  ancho = A/L y wQ = Q/L son equivalencias; FE conserva las cargas nodales.
- R y los cuatro λ están visibles en Resultados. Información detallada solo
  en la ficha desplegable; fuentes extensas en tooltip.
- Columnas ladrillo, vigas metálicas, muros hormigón, cyan de selección,
  nodos ON y mapa de capacidad OFF se mantienen.

## Tres vigas revisadas

| ID | qQ kN/m² | A m² | Ancho m | wQ kN/m | Q kN |
|---|---:|---:|---:|---:|---:|
| E1-P1-V-002 | 4,123947 | 21,230775 | 2,589119 | 10,677389 | 87,554587 |
| E1-P2-V-041 | 4,886238 | 5,208903 | 1,501125 | 7,334852 | 25,451938 |
| E2-P3-V-001 | 3,365985 | 6,740049 | 2,943253 | 9,906944 | 22,686903 |

Prueba Play: λQ 0/1/2 compara las doce componentes firmadas de extremos de cada
segmento con 0/Q/2Q; tolerancia absoluta 1e−6 en unidades SI. qQ, ancho y wQ
se verifican contra el contrato y la longitud física, conservando su redondeo.

## QA y límites

- Central: PASS, 679 elementos físicos (442 vigas, 143 columnas, 84 muros, 10 losas).
- FE intacto: 677 segmentos candidatos; 673 analizados, 1.165 nodos analizados.
- Cargas: conservación G/Q PASS; tres paños retirados, 40 paños activos y
  45 componentes visuales. Sin solapes de carga, sin duplicados ni receptores huérfanos.
- Malla: sin triángulos degenerados, huecos existentes conservados.
- Unity: compile/Play; 29 checks Q, 44 losas, 83 de regresión visual.
  Evidencia: `p1_lateral_qa/UNITY_Q_QA.json`, `UNITY_SLAB_QA.json`,
  `UNITY_VISUAL_RUNTIME_QA.json`, diez capturas `EDIFICIO_*_TOP.png` y tres `_Q.png`.
- Regresión cubre filtros, selección/ficha, casos, R/sliders, diagramas, gráficos,
  deformada, capacidad, D/C, failure visualization y restauración de materiales.
- El antiguo auto-chequeo de V-041 usaba nodos históricos; ahora valida metadatos
  contra los resultados realmente analizados, no contra tags pre-adaptador.
- Luis original, entregas y tags históricos permanecen intactos.

**PASS funcional/numerical no certifica todos los contornos físicos.** Las dos
extensiones aprobadas sí están excluidas y verificadas en TOP. Persisten pendientes
de perímetros/voids ya documentados, especialmente S1/P1, ED1-P4 y ED2-P4.
El chequeo espacial por hull está en `p1_lateral_after/SLAB_SOURCE_AUDIT.json`:
hay áreas exteriores al hull (offsets/voladizos/sectores todavía en revisión).
Eso no prueba que sean residuos ni autoriza otra eliminación automática.
No se afirma que todas las losas restantes estén certificadas desde planos.

## Reproducir

Aplicar `apply_p1_lateral_exclusion.py` (idempotente). Ejecutar el pipeline físico
documentado en README; `main.py validar`; auditoría `audit_slabs.py --p1-lateral`
con `.venv`, `validate_slab_cleanup.py` y `validate_p1_lateral.py`.
En `entregas/P1L3/José/viewer_unity`: abrir `Assets/Main.unity`, Play,
menú **MCOC → Validar losas y cargas Q**. El QA termina en ISO, caso R,
Modelo abierto, losas OFF y nodos ON.
