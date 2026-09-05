# E1 FORCE EXTRACTION AUDIT — FINAL

Edificio 1 (E1) · Semana 2 (gravedad) · OpenSees → Unity
Fecha de cierre de auditoría: 2026-09-03
No commit · No push · Solo repositorio `MCOC-grupo1-e1-momentos`

---

## 1. EXTRACTION

| Item | Valor |
|---|---|
| Tipo de elemento OpenSees | `elasticBeamColumn` (3D, 12 DOF) |
| Respuesta utilizada finalmente | `ops.eleResponse(tag, "localForce")` |
| Respuesta descartada (bug) | `ops.eleForce()` — devuelve el vector **GLOBAL** (`getResistingForce`), NO miembro-local |
| Orden confirmado (por extremo) | `[N, Vy, Vz, T, My, Mz]` (i = extremo 1, j = extremo 2) |
| Unidades | N, Vy, Vz = **kN**; T, My, Mz = **kN·m**; m, rad; Pa base |
| Conversión implementada | raw N → `/1000` → kN; raw N·m → `/1000` → kN·m |
| Fijado de extracción SI/NO | **SI** (`modelo_opensees_candidate.py:775`) |
| Checker fix SI/NO | **SI** (bug del script de auditoría, no del modelo) |

### 1.1 Bug del checker encontrado y corregido

El checker de auditoría reportaba falsos fallos de equilibrio (88/99 y 231/325)
por un **bug del script**: en el bucle agregado se usaba `L = e['L_m']` con una
variable `e` **residual** del bucle anterior, dividiendo por el largo de un
elemento distinto. Corregido a `L = ef[eid]['L_m']`. El modelo y los resultados
OpenSees **no fueron modificados** por esta auditoría.

---

## 2. VERIFICACIÓN DE EXTRACCIÓN (model-wide)

### 2.1 Equilibrio de beams load-free

- Beams **load-free** (sin carga distribuida y sin carga puntual): **99**
- Todos satisfacen la relación de miembro (elemento en equilibrio interno):
  `Vz1 = -(My1+My2)/L`
- **99/99 PASS** (peor error relativo **7.1e-6**; la mayoría ~1e-8 a 1e-16).
- Simetría de miembros load-free: `|T1+T2| = |N1+N2| = 0` en todos.

### 2.2 Comprobación de rigidez / rotaciones

Para un beam completo y rígido (`SOL_1S_logical_0001`, E=25 GPa, sección
0.60 × 0.80 m → EI≈6.4e5 kN·m², L=10 m):

- Predicción por extremos (rotaciones) ≈ **My 2418 / 2595 kN·m**
- Valor almacenado (localForce) = **My1 -2194 / My2 -2371 kN·m**
- Concordancia **~8–10%** (misma escala y signo). El término de desplazamiento
  vertical es pequeño (~220 kN·m); el término dominante es la **rotación de extremo**
  (θ≈0.006 rad) actuando sobre un beam muy rígido.

**Conclusión de extracción:** el orden `[N, Vy, Vz, T, My, Mz]` es **CORRECTO**
en todo el modelo; los My grandes de beams completos son **respuesta de frame real**
(reproducible desde la matriz de rigidez y las rotaciones impuestas por el pórtico),
NO un error de extracción y NO una contaminación de la zona flotante.

---

## 3. STUBS DE SEGMENTACIÓN

### 3.1 Criterio (metadata + longitud, NO solo longitud)

Un beam FE es `SEGMENTATION_STUB_ARTIFACT` si cumple **TODAS**:

1. es un **hijo de segmentación** (`parent_beam_id` presente, `id` contiene `_seg`); **y**
2. **no** corresponde a ninguna viga visual (`visual_beam_id is None`); **y**
3. su **longitud < 0.60 m** (pieza residual de esquina del logical beam).

### 3.2 Cuantificación (demostrada con datos)

| Métrica | Stubs | Physical |
|---|---|---|
| Count | **103** | **134** |
| L min / mediana / max | 0.169 / ~0.29 / 0.600 m | — |
| Max \|My\| | **17 792 kN·m** (`SOL_1_logical_0017_seg05`) | **16 679 kN·m** (beam completo real) |
| Max \|T\| | 1 357.64 kN·m | 1 357.64 kN·m |
| Max \|Vz\| | **3 806 kN** | 3 581 kN |
| # stubs que exceden el máx físico de My | 24 / 103 | — |

**Outlier concentration confirmada: SI.** La amplificación de los stubs es la
combinación de **EI/L** (un stub de 0.38 m tiene `2EI/L = 3.36e6 kN·m/rad`) con
rotaciones de extremo moderadas (θ≈0.04–0.05 rad en los extremos segmentados),
concentrando momentos enormes en miembros de cms–dms que no son elementos
estructurales independientes.

### 3.3 Manejo

- se mantiene la **geometría** (conectividad / visualización);
- **NO** se presentan sus My/V/T como resultado estructural defendible;
- **NO** entran en máximos/mínimos físicos del edificio;
- **NO** se usan para escalar diagramas;
- el inspector muestra: *"Short reconciliation stub. Internal-force magnitude is
  affected by EI/L idealization and is excluded from physical member interpretation."*

---

## 4. ACCOUNTING DE ELEMENTOS

La volumetría openSees declarada el modelo **no fue re-escrita**; se reconcilia
documentalmente:

| Contador | Valor | Origen |
|---|---|---|
| `num_logical_beams` | **239** | `len(self.logical_beams)` tras segmentación (`:809`) |
| `num_beams_analyzed` | **237** | `len(self.created_beam_ids)` (`:810`) |

Reconstrucción determinista de los 239 (preprocesamiento del modelo, sin solve):

- **2 beams degenerados de longitud 0** se omiten en materialización por
  `if L < 0.05: continue` (`modelo_opensees_candidate.py:609`):
  - `SOL_3_logical_0095` — floor 3, endpoints coincidentes `[57.486, 8.959, 15.84]`
  - `SOL_4_logical_0145` — floor 4, endpoints coincidentes `[67.443, 8.96, 19.8]`
    (parent = None, visual = None; no son miembros físicos válidos)
- Los **237** restantes se materializan vía `ops.element(...)`.

```
FE beam total:                  237
PHYSICAL_MEMBER:                134
SEGMENTATION_STUB_ARTIFACT:     103
OTHER (no materialized, L=0):     2  (SOL_3_logical_0095, SOL_4_logical_0145)
sum check: 134 + 103 = 237 = FE beams   PASS
```

**Ningún beam FE queda sin clasificar.**

---

## 5. MÁXIMOS DE FUERZA (por grupo, |·| sobre extremos i/j)

Unidades: N, Vy, Vz = **kN**; T, My, Mz = **kN·m**.

### A. VERIFIED PHYSICAL (stub=PHYSICAL_MEMBER y status=VERIFIED_CONNECTED_RESPONSE) — count 5

| Comp | max \|·\| | Element | end | vis | floor | L (m) |
|---|---|---|---|---|---|---|
| N | 0.00 | SOL_1S_logical_0001 | i | — | 1S | 10.00 |
| Vy | 0.00 | SOL_1S_logical_0001 | i | — | 1S | 10.00 |
| Vz | 480.86 | SOL_1S_logical_0007 | i | — | 1S | 10.00 |
| T | 114.05 | SOL_1S_logical_0003 | i | — | 1S | 7.25 |
| My | 2408.63 | SOL_1S_logical_0007 | i | — | 1S | 10.00 |
| Mz | 0.00 | SOL_1S_logical_0001 | i | — | 1S | 10.00 |

### B. RECONCILED SCOPING (stub=PHYSICAL_MEMBER y status=RECONCILED_SCOPING_RESPONSE) — count 86

| Comp | max \|·\| | Element | end | vis | floor | L (m) |
|---|---|---|---|---|---|---|
| N | 0.00 | SOL_1S_logical_0008_seg02 | i | B0038 | 1S | 8.20 |
| Vy | 0.00 | SOL_1S_logical_0008_seg02 | i | B0038 | 1S | 8.20 |
| Vz | 3580.71 | SOL_2_logical_0061_seg02 | i | B0052 | 2 | 1.86 |
| T | 1357.64 | SOL_1_logical_0027_seg02 | i | B0022 | 1 | 8.20 |
| My | 16679.41 | SOL_1_logical_0017_seg04 | j | B0011 | 1 | 4.35 |
| Mz | 0.00 | SOL_1S_logical_0008_seg02 | i | B0038 | 1S | 8.20 |

### C. ARTIFACT / BLOCKED / NON-VERIFIABLE (stubs + FLOATING + UNMATCHED) — count 146

| Comp | max num \|·\| | Element | end | reason excl. |
|---|---|---|---|---|
| N | 0.00 | SOL_1S_logical_0008_seg01 | i | stub |
| Vy | 0.00 | SOL_1S_logical_0008_seg01 | i | stub |
| Vz | 3806.17 | SOL_2_logical_0061_seg01 | i | stub |
| T | 1357.64 | SOL_1_logical_0027_seg01 | i | stub |
| My | 17792.25 | SOL_1_logical_0017_seg05 | j | stub (EI/L) |
| Mz | 0.00 | SOL_1S_logical_0008_seg01 | i | stub |

> Los máximos físicos que Unity usa como **escala global** provienen de los grupos
> **A y B**, NUNCA del grupo C (un stub de 0.38 m con My≈17 800 kN·m no escala la vista).

---

## 6. B0022 (E1_F01_B0022)

- **stub_status**: `PHYSICAL_MEMBER`
- **analysis_status**: `RECONCILED_SCOPING_RESPONSE` (no se promueve a VERIFIED)
- **Elemento FE**: `SOL_1_logical_0027_seg02`, L_FE ≈ 8.199889 m (L visual 8.199889 m)
- Datos de control: Atrib=16.0 m² · qG=6.080123 kN/m² · P=97.281968 kN · w=11.863815 kN/m

### 6.1 Fuerzas finales correctas (localForce, EN kN / kN·m)

| Comp | Extremo i | Extremo j |
|---|---|---|
| N | 0.000 | 0.000 |
| Vy | 0.000 | 0.000 |
| Vz | 569.268 | -471.986 |
| T | 1357.638 | -1357.638 |
| My | -2471.025 | -1798.060 |
| Mz | 0.000 | 0.000 |

> **Corrección crítica:** el mapeo antiguo `eleForce → local` intercambiaba
> T↔My. Con `localForce` el **T real** = ±1357.64 kN·m (torsión) y el **My real**
> (flexión por gravedad) = -2471 / -1798 kN·m. Los valores correctos provienen de
> `localForce`; **NO** se vuelve al mapeo antiguo.

### 6.2 Equilibrio de B0022 (convención de signos local)

Geometría: B0022 rige según el eje **Y global** (local x=(0,1,0)); `geomTransf`
referencia rel = (0,0,1) → **local z = (0,0,1)**. La gravedad global (0,0,-1) actúa
por tanto a lo largo de **local -z**.

Carga distribuida aplicada: `ops.eleLoad(..., "-beamUniform", 0.0, -w, 0.0)` con
w = 11.863815·1000 N/m → resultante total |W_local| = w·L = **97.2820 kN** según
**local -z** (W_local = -97.28 kN en ejes locales).

Equilibrio de miembro (convención localForce de OpenSees):

```
Vz_i + Vz_j + W_local = 0
(+569.268) + (-471.986) + (-97.282) = 0.000
```

→ **EQUILIBRIO PASS** (`|Σ|=97.2819 vs |W_local|=97.2820`, diff ≈ 1e-4 kN).

---

## 7. GLOBAL QA

| Métrica | Valor |
|---|---|
| Applied gravity | ≈ 21 189.36 kN |
| ΣRz (base) | ≈ 21 189.36 kN |
| Residual Fz | ≈ 0 (2e-6 kN) |
| Equilibrium error | 1e-8 % |
| **Estado** | **PASS** |
| Verified max displacement (universo interpretable) | **0.01800 m** (nodo 56, floor 4) |
| Numerical global max (floating, NO verified) | 4.297 m — `INVALID_FOR_PHYSICAL_INTERPRETATION` (bloqueo P1 far-east) |

No se cambió gravedad ni tributarias.

---

## 8. LIMITACIONES

- **Soporte / reacciones:** 8 reacciones FE (base) vs 94 símbolos visuales de
  apoyo (zapatas/muros del plano). Solo 4 visuales mapean a nodos FE
  (`1,13,19,25`); el resto son pie de plano no-FE o apoyos no materializados.
  Clasificación de soportes: mapeado/documentado, no se promueve a físico.
- **Zona flotante (P1 far-east):** columnas `STK_0072-0074` etc. sin camino de
  carga a fundación → desplazamientos verticales numéricos de hasta ~4.3 m
  `INVALID_FOR_PHYSICAL_INTERPRETATION`. No contaminan los beams verificados
  (uz de la planta 1S ≤ 5 mm).
- **L101:** `GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY` (documentado).

---

## 9. UNITY Y JSON

- `stub_status` (`PHYSICAL_MEMBER` / `SEGMENTATION_STUB_ARTIFACT`) añadido a cada
  response de beam.
- Inspector: A/B muestran valores y diagramas según status; stubs muestran
  warning y no dibujan el diagrama como resultado físico por defecto;
  FLOATING mantiene warning; L101 mantiene blocker documentado.
- Validación de JSON: sin NaN, sin inf, statuses consistentes, orden `localForce`
  correcto, unidades kN / kN·m.

---

## 10. PENDIENTE

- Sync a Windows TEST (`E1_UNITY_ANALISIS_TEST`) y verificación SHA256.
