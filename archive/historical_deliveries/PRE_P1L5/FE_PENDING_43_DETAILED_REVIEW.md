# Pendientes FE: revisión individual antes de corregir

Total regenerado: 43. Componentes sin camino a apoyos: 22. No se ejecutó OpenSees ni se cambiaron geometría, cargas, resultados o referencias históricas.

Las distancias XY son medidas del modelo actual, no cotas primarias. Huella solapada no equivale a unión resistente. Los tags/nodos son del CANDIDATO. Localización SOBRE EJE exige diferencia < 0.000001 m; se conservan offsets pequeños. Los cortes se recomiendan por eje cercano, no se certifica que atraviesen el elemento. La lista de preguntas no certifica errores reales del edificio.

## Tabla maestra

| Nº | ID | Tipo | Edificio | Piso | Ejes | Problema | Prioridad | Plano | Estado |
|---|---|---|---|---|---|---|---|---|---|
| 01/43 | E1-P1-M-004 | MURO | EDIFICIO_1 | P1 | X Eb–Ec (Eb +1.4000 m) / Y 1''–2 (1'' +0.0001 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-101 | REVIEW_REQUIRED |
| 02/43 | E1-P1-M-010 | MURO | EDIFICIO_1 | P1 | X Eb–Ec (Ec -1.4000 m) / Y 2a–3 (2a +0.0001 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-101 | REVIEW_REQUIRED |
| 03/43 | E1-P2-M-003 | MURO | EDIFICIO_1 | P2 | X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; FE_ADAPTER_ERROR | A | 2017_67-102 | REVIEW_REQUIRED |
| 04/43 | E1-P2-M-010 | MURO | EDIFICIO_1 | P2 | X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; FE_ADAPTER_ERROR | A | 2017_67-102 | REVIEW_REQUIRED |
| 05/43 | E1-P2-M-007 | MURO | EDIFICIO_1 | P2 | X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 06/43 | E1-P2-M-008 | MURO | EDIFICIO_1 | P2 | X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 07/43 | E1-P2-M-009 | MURO | EDIFICIO_1 | P2 | X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; FE_ADAPTER_ERROR | A | 2017_67-102 | REVIEW_REQUIRED |
| 08/43 | E1-P2-M-005 | MURO | EDIFICIO_1 | P2 | X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; FE_ADAPTER_ERROR | A | 2017_67-102 | REVIEW_REQUIRED |
| 09/43 | E1-P3-M-003 | MURO | EDIFICIO_1 | P3 | X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 10/43 | E1-P3-M-010 | MURO | EDIFICIO_1 | P3 | X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 11/43 | E1-P3-M-007 | MURO | EDIFICIO_1 | P3 | X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 12/43 | E1-P3-M-008 | MURO | EDIFICIO_1 | P3 | X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 13/43 | E1-P3-M-009 | MURO | EDIFICIO_1 | P3 | X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 14/43 | E1-P3-M-005 | MURO | EDIFICIO_1 | P3 | X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-102 | REVIEW_REQUIRED |
| 15/43 | E1-P4-M-003 | MURO | EDIFICIO_1 | P4 | X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 16/43 | E1-P4-M-009 | MURO | EDIFICIO_1 | P4 | X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 17/43 | E1-P4-M-007 | MURO | EDIFICIO_1 | P4 | X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 18/43 | E1-P4-M-008 | MURO | EDIFICIO_1 | P4 | X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 19/43 | E1-P4-M-010 | MURO | EDIFICIO_1 | P4 | X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 20/43 | E1-P4-M-012 | MURO | EDIFICIO_1 | P4 | X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m) | Sin camino a apoyos; UNRESOLVED_REAL | A | 2017_67-103 | REVIEW_REQUIRED |
| 21/43 | E1-P1-C-016 | COLUMNA | EDIFICIO_1 | P1 | X H–H1 (H +0.0271 m) / Y OUTBOARD >3 (3 +2.6926 m) | Sin camino a apoyos; STAIR_STRUCTURE | B | 2017_67-101 | REVIEW_REQUIRED |
| 22/43 | E1-P1-C-017 | COLUMNA | EDIFICIO_1 | P1 | X H–H1 (H +0.0271 m) / Y OUTBOARD >3 (3 +10.0256 m) | Sin camino a apoyos; STAIR_STRUCTURE | B | 2017_67-101 | REVIEW_REQUIRED |
| 23/43 | E1-P1-M-016 | MURO | EDIFICIO_1 | P1 | X H'–H2 (H2 -1.8169 m) / Y OUTBOARD <1 (1 -3.5749 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 24/43 | E1-P1-M-024 | MURO | EDIFICIO_1 | P1 | X H'–H2 (H2 -1.8000 m) / Y OUTBOARD <1 (1 -0.5249 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 25/43 | E1-P1-M-023 | MURO | EDIFICIO_1 | P1 | X H'–H2 (H2 -1.0419 m) / Y OUTBOARD <1 (1 -6.2249 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 26/43 | E1-P1-M-020 | MURO | EDIFICIO_1 | P1 | X SOBRE EJE H2 (H2 +0.0000 m) / Y OUTBOARD <1 (1 -2.0499 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 27/43 | E1-P1-M-022 | MURO | EDIFICIO_1 | P1 | X I–IA (IA -1.0750 m) / Y OUTBOARD <1 (1 -6.2249 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 28/43 | E1-P1-M-021 | MURO | EDIFICIO_1 | P1 | X I–IA (IA -1.0750 m) / Y OUTBOARD <1 (1 -0.5249 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 29/43 | E1-P1-M-031 | MURO | EDIFICIO_1 | P1 | X SOBRE EJE IA (IA -0.0000 m) / Y OUTBOARD <1 (1 -11.1362 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 30/43 | E1-P1-M-034 | MURO | EDIFICIO_1 | P1 | X SOBRE EJE IA (IA -0.0000 m) / Y OUTBOARD <1 (1 -10.3310 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 31/43 | E1-P1-M-036 | MURO | EDIFICIO_1 | P1 | X IA–I' (I' -1.0172 m) / Y OUTBOARD <1 (1 -10.6970 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 32/43 | E1-P1-M-035 | MURO | EDIFICIO_1 | P1 | X IA–I' (I' -1.0172 m) / Y OUTBOARD <1 (1 -0.5249 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 33/43 | E1-P1-M-037 | MURO | EDIFICIO_1 | P1 | X I'–IB (I' +0.3953 m) / Y OUTBOARD <1 (1 -5.9627 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 34/43 | E1-P1-V-068 | VIGA | EDIFICIO_1 | P1 | X SOBRE EJE H1 (H1 +0.0000 m) / Y OUTBOARD <1 (1 -2.0499 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 35/43 | E1-P1-V-072 | VIGA | EDIFICIO_1 | P1 | X H'–H2 (H' +0.1061 m) / Y OUTBOARD <1 (1 -3.5749 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 36/43 | E1-P1-V-098 | VIGA | EDIFICIO_1 | P1 | X I–IA (IA -0.5274 m) / Y OUTBOARD <1 (1 -3.5749 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2017_67-101 | REVIEW_REQUIRED |
| 37/43 | E1-P2-V-055 | VIGA | EDIFICIO_1 | P2 | X Ga–H (Ga +0.7499 m) / Y OUTBOARD >3 (3 +2.6414 m) | Sin camino a apoyos; STAIR_STRUCTURE | B | 2017_67-102 | REVIEW_REQUIRED |
| 38/43 | E1-P2-V-075 | VIGA | EDIFICIO_1 | P2 | X Ga–H (H -2.8251 m) / Y OUTBOARD >3 (3 +2.6414 m) | Sin camino a apoyos; STAIR_STRUCTURE | B | 2017_67-102 | REVIEW_REQUIRED |
| 39/43 | E2-P4-V-004 | VIGA | EDIFICIO_2 | P4 | X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -3.2916 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2024_22-102 | REVIEW_REQUIRED |
| 40/43 | E2-P4-V-005 | VIGA | EDIFICIO_2 | P4 | X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -1.7239 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2024_22-102 | REVIEW_REQUIRED |
| 41/43 | E2-P4-V-006 | VIGA | EDIFICIO_2 | P4 | X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -0.9489 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2024_22-102 | REVIEW_REQUIRED |
| 42/43 | E2-P4-V-007 | VIGA | EDIFICIO_2 | P4 | X OUTBOARD <A (A -3.5480 m) / Y 2–3 (2 +1.5932 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2024_22-102 | REVIEW_REQUIRED |
| 43/43 | E2-P4-V-009 | VIGA | EDIFICIO_2 | P4 | X OUTBOARD <A (A -2.7322 m) / Y 2–3 (3 -0.2993 m) | Sin camino a apoyos; UNRESOLVED_REAL | B | 2024_22-102 | REVIEW_REQUIRED |

## 01/43 — E1-P1-M-004

MURO · EDIFICIO_1 · P1 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_1_wall_0071`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00231 | 10231 | 333 | 334 | (32.491, 3.9, 3.96) | (32.491, 3.9, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.4000 m) | 1''–2 (1'' +0.0001 m) |
| i | Eb–Ec (Eb +0.1000 m) | 1''–2 (1'' +0.0001 m) |
| j | Eb–Ec (Ec -0.1000 m) | 1''–2 (1'' +0.0001 m) |

### COORDENADAS GLOBALES (m)

- center: 32.491000, 3.900100, 5.940000 m.
- i: 31.191000, 3.900100, 5.940000 m.
- j: 33.791000, 3.900100, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-004 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-026: distancia entre ejes XY 0.1813 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-004, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X Eb–Ec (Eb +1.4000 m) / Y 1''–2 (1'' +0.0001 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-004 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-026: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-001 | 5.375948 | 4.808920 | 0.000000 |
| nearest_wall | E1-P1-M-012 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-S1-M-026 | 0.181300 | 0.000000 | 0.000000 |
| above | E1-P2-M-007 | 0.181400 | 0.000000 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-004.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-012 | 0.180278 | 0.100000 |
| j | E1-P1-M-025 | 0.180278 | 0.100000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-17", "start_xy_m": [30.77, 4.08], "end_xy_m": [34.17, 4.08], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.1799, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 0.8, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1002", "start_xy_m": [27.24, 4.08], "end_xy_m": [33.89, 4.08], "length_m": 6.65, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.1799, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 4.05, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0015, P1-RLE-MURO-0016
- source_label: M.H.A. e= 20
- source_label_tag: LBL_1_wall_label_0041
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0015", "P1-RLE-MURO-0016"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00231: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-004 y E1-S1-M-026, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 02/43 — E1-P1-M-010

MURO · EDIFICIO_1 · P1 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_1_wall_0061`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00229 | 10229 | 329 | 330 | (32.491, 13.845, 3.96) | (32.491, 13.845, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Ec -1.4000 m) | 2a–3 (2a +0.0001 m) |
| i | Ea–Eb (Ea +0.1000 m) | 2a–3 (2a +0.0001 m) |
| j | Ec–Ed (Ed -0.1000 m) | 2a–3 (2a +0.0001 m) |

### COORDENADAS GLOBALES (m)

- center: 32.491000, 13.845100, 5.940000 m.
- i: 30.891000, 13.845100, 5.940000 m.
- j: 34.091000, 13.845100, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-003 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-005: distancia entre ejes XY 0.1250 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-003, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X Eb–Ec (Ec -1.4000 m) / Y 2a–3 (2a +0.0001 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ec y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-010 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-005: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-003 | 4.087008 | 3.548467 | 0.000000 |
| nearest_wall | E1-P1-M-002 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-S1-M-005 | 0.125000 | 0.000000 | 0.000000 |
| above | E1-P2-M-005 | 0.124900 | 0.000000 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-010.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P2-M-003 | 0.125100 | 0.000100 |
| j | E1-P2-M-005 | 0.124900 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-2", "start_xy_m": [30.77, 14.025], "end_xy_m": [34.17, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.1799, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1402", "start_xy_m": [30.79, 14.025], "end_xy_m": [34.19, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.1799, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0001, P1-RLE-MURO-0002
- source_label: M.H.A. e= 20
- source_label_tag: LBL_1_wall_label_0035
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0001", "P1-RLE-MURO-0002"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00229: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-010 y E1-S1-M-005, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 03/43 — E1-P2-M-003

MURO · EDIFICIO_1 · P2 · Prioridad A · FE_ADAPTER_ERROR

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0101`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00252 | 10252 | 375 | 376 | (30.766, 13.187, 7.92) | (30.766, 13.187, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | E–Ea (Ea -0.0251 m) | 2–2a (2a -0.6579 m) |
| i | E–Ea (Ea -0.0251 m) | 2–2a (2a -1.3973 m) |
| j | E–Ea (Ea -0.0251 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 30.765900, 13.187100, 9.900000 m.
- i: 30.765900, 12.447700, 9.900000 m.
- j: 30.765900, 13.926500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-013 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-002: distancia entre ejes XY 0.0001 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m. La auditoría previa detectó sensibilidad a redondeo de 0.1 mm; eso no autoriza unirlo sin revisar el encuentro.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-013, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ea y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-003 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-002: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-003 | 4.063252 | 3.473232 | 0.000000 |
| nearest_wall | E1-P2-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P1-M-002 | 0.000100 | 0.000000 | 0.000000 |
| above | E1-P3-M-003 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-003.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-003, E1-P3-M-003, E1-P4-M-003.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-003 | 0.000000 | 0.000000 |
| j | E1-P3-M-003 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-13", "start_xy_m": [30.77, 14.025], "end_xy_m": [30.77, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0041, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1503", "start_xy_m": [30.79, 14.025], "end_xy_m": [30.79, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0241, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0003, P2-RLE-MURO-0005
- source_label: M.H.A. e= 25
- source_label_tag: LBL_2_wall_label_0034
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0003", "P2-RLE-MURO-0005"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00252: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-003 y E1-P1-M-002, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 04/43 — E1-P2-M-010

MURO · EDIFICIO_1 · P2 · Prioridad A · FE_ADAPTER_ERROR

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0104`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00254 | 10254 | 379 | 380 | (31.041, 5.256, 7.92) | (31.041, 5.256, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +1.3565 m) |
| i | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +0.2815 m) |
| j | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 31.040900, 5.256500, 9.900000 m.
- i: 31.040900, 4.181500, 9.900000 m.
- j: 31.040900, 6.331500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-015 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-012: distancia entre ejes XY 0.0001 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m. La auditoría previa detectó sensibilidad a redondeo de 0.1 mm; eso no autoriza unirlo sin revisar el encuentro.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-015, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-010 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-012: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-002 | 4.490489 | 3.880986 | 0.000000 |
| nearest_wall | E1-P2-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P1-M-012 | 0.000100 | 0.000000 | 0.000000 |
| above | E1-P3-M-010 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-010.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-010, E1-P3-M-010, E1-P4-M-009.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-010 | 0.000000 | 0.000000 |
| j | E1-P3-M-010 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-28", "start_xy_m": [30.77, 4.08], "end_xy_m": [30.77, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2709, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1103", "start_xy_m": [31.09, 6.33], "end_xy_m": [31.09, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0491, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0009, P2-RLE-MURO-0010
- source_label: M.H.A. e= 30
- source_label_tag: LBL_2_wall_label_0037
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0009", "P2-RLE-MURO-0010"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00254: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-010 y E1-P1-M-012, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 05/43 — E1-P2-M-007

MURO · EDIFICIO_1 · P2 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0100`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00255 | 10255 | 381 | 382 | (32.491, 4.082, 7.92) | (32.491, 4.082, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 1''–2 (1'' +0.1815 m) |
| i | Eb–Ec (Eb +0.0999 m) | 1''–2 (1'' +0.1815 m) |
| j | Eb–Ec (Ec -0.1001 m) | 1''–2 (1'' +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 4.081500, 9.900000 m.
- i: 31.190900, 4.081500, 9.900000 m.
- j: 33.790900, 4.081500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-016 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-012: distancia entre ejes XY 0.1499 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-016, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-007 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-012: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-005 | 5.375949 | 4.808921 | 0.000000 |
| nearest_wall | E1-P2-M-009 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P1-M-012 | 0.149900 | 0.000000 | 0.000000 |
| above | E1-P3-M-007 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-007.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-007, E1-P3-M-007, E1-P4-M-007.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-007 | 0.000000 | 0.000000 |
| j | E1-P3-M-007 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-18", "start_xy_m": [30.77, 4.08], "end_xy_m": [34.17, 4.08], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 0.8, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1003", "start_xy_m": [27.24, 4.08], "end_xy_m": [33.89, 4.08], "length_m": 6.65, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 4.05, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0015, P2-RLE-MURO-0016
- source_label: M.H.A. e= 20
- source_label_tag: LBL_2_wall_label_0039
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0015", "P2-RLE-MURO-0016"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00255: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-007 y E1-P1-M-012, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 06/43 — E1-P2-M-008

MURO · EDIFICIO_1 · P2 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0099`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00253 | 10253 | 377 | 378 | (32.491, 14.027, 7.92) | (32.491, 14.027, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 2a–3 (2a +0.1815 m) |
| i | Ea–Eb (Ea +0.0999 m) | 2a–3 (2a +0.1815 m) |
| j | Ec–Ed (Ed -0.1001 m) | 2a–3 (2a +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 14.026500, 9.900000 m.
- i: 30.890900, 14.026500, 9.900000 m.
- j: 34.090900, 14.026500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-014 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-010: distancia entre ejes XY 0.1814 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-014, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-008 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-010: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-003 | 4.107724 | 3.569853 | 0.000000 |
| nearest_wall | E1-P2-M-003 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P1-M-010 | 0.181400 | 0.000000 | 0.000000 |
| above | E1-P3-M-008 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-008.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-008, E1-P3-M-008, E1-P4-M-008.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-008 | 0.000000 | 0.000000 |
| j | E1-P3-M-008 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-3", "start_xy_m": [30.77, 14.025], "end_xy_m": [34.17, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1403", "start_xy_m": [30.79, 14.025], "end_xy_m": [34.19, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0001, P2-RLE-MURO-0002
- source_label: M.H.A. e= 20
- source_label_tag: LBL_2_wall_label_0033
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0001", "P2-RLE-MURO-0002"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00253: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-008 y E1-P1-M-010, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 07/43 — E1-P2-M-009

MURO · EDIFICIO_1 · P2 · Prioridad A · FE_ADAPTER_ERROR

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0108`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00256 | 10256 | 383 | 384 | (33.941, 5.256, 7.92) | (33.941, 5.256, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +1.3565 m) |
| i | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +0.2815 m) |
| j | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 33.940900, 5.256500, 9.900000 m.
- i: 33.940900, 4.181500, 9.900000 m.
- j: 33.940900, 6.331500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-017 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-025: distancia entre ejes XY 0.0001 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m. La auditoría previa detectó sensibilidad a redondeo de 0.1 mm; eso no autoriza unirlo sin revisar el encuentro.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-017, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ec y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-009 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-025: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-006 | 4.490428 | 3.880925 | 0.000000 |
| nearest_wall | E1-P2-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P1-M-025 | 0.000100 | 0.000000 | 0.000000 |
| above | E1-P3-M-009 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-009.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-009, E1-P3-M-009, E1-P4-M-010.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-009 | 0.000000 | 0.000000 |
| j | E1-P3-M-009 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-23", "start_xy_m": [34.17, 4.08], "end_xy_m": [34.17, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2291, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1203", "start_xy_m": [33.89, 6.33], "end_xy_m": [33.89, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0509, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0012, P2-RLE-MURO-0013
- source_label: M.H.A. e= 30
- source_label_tag: LBL_2_wall_label_0038
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0012", "P2-RLE-MURO-0013"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00256: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-009 y E1-P1-M-025, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 08/43 — E1-P2-M-005

MURO · EDIFICIO_1 · P2 · Prioridad A · FE_ADAPTER_ERROR

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_2_wall_0103`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00257 | 10257 | 385 | 386 | (34.216, 13.187, 7.92) | (34.216, 13.187, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ed–F (Ed +0.0249 m) | 2–2a (2a -0.6579 m) |
| i | Ed–F (Ed +0.0249 m) | 2–2a (2a -1.3973 m) |
| j | Ed–F (Ed +0.0249 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 34.215900, 13.187100, 9.900000 m.
- i: 34.215900, 12.447700, 9.900000 m.
- j: 34.215900, 13.926500, 9.900000 m.
- z_bottom: 7.920000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-018 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-026: distancia entre ejes XY 0.0001 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m. La auditoría previa detectó sensibilidad a redondeo de 0.1 mm; eso no autoriza unirlo sin revisar el encuentro.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-018, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ed y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-M-005 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-026: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-004 | 4.132693 | 3.542827 | 0.000000 |
| nearest_wall | E1-P2-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P1-M-026 | 0.000100 | 0.000000 | 0.000000 |
| above | E1-P3-M-005 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P3-M-005.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-005, E1-P3-M-005, E1-P4-M-012.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P3-M-005 | 0.000000 | 0.000000 |
| j | E1-P3-M-005 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-8", "start_xy_m": [34.17, 14.025], "end_xy_m": [34.17, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0459, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1603", "start_xy_m": [34.19, 14.025], "end_xy_m": [34.19, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0259, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P2-RLE-MURO-0006, P2-RLE-MURO-0008
- source_label: M.H.A. e= 25
- source_label_tag: LBL_2_wall_label_0035
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P2-RLE-MURO-0006", "P2-RLE-MURO-0008"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00257: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P2-M-005 y E1-P1-M-026, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 09/43 — E1-P3-M-003

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0113`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00259 | 10259 | 376 | 388 | (30.766, 13.187, 11.88) | (30.766, 13.187, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | E–Ea (Ea -0.0251 m) | 2–2a (2a -0.6579 m) |
| i | E–Ea (Ea -0.0251 m) | 2–2a (2a -1.3973 m) |
| j | E–Ea (Ea -0.0251 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 30.765900, 13.187100, 13.860000 m.
- i: 30.765900, 12.447700, 13.860000 m.
- j: 30.765900, 13.926500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-013 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-003: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-013, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ea y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-003 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-003: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-003 | 4.063238 | 3.473218 | 0.000000 |
| nearest_wall | E1-P3-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P2-M-003 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-003 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-003, E1-P4-M-003.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-003, E1-P3-M-003, E1-P4-M-003.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-003 | 0.000000 | 0.000000 |
| j | E1-P4-M-003 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-14", "start_xy_m": [30.77, 14.025], "end_xy_m": [30.77, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0041, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1504", "start_xy_m": [30.79, 14.025], "end_xy_m": [30.79, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0241, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0003, P3-RLE-MURO-0005
- source_label: M.H.A. e= 25
- source_label_tag: LBL_3_wall_label_0033
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0003", "P3-RLE-MURO-0005"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00259: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-003 y E1-P2-M-003, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 10/43 — E1-P3-M-010

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0116`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00261 | 10261 | 380 | 390 | (31.041, 5.256, 11.88) | (31.041, 5.256, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +1.3565 m) |
| i | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +0.2815 m) |
| j | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 31.040900, 5.256500, 13.860000 m.
- i: 31.040900, 4.181500, 13.860000 m.
- j: 31.040900, 6.331500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-015 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-010: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-015, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-010 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-010: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-002 | 4.490474 | 3.880971 | 0.000000 |
| nearest_wall | E1-P3-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P2-M-010 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-009 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-010, E1-P4-M-009.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-010, E1-P3-M-010, E1-P4-M-009.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-009 | 0.000000 | 0.000000 |
| j | E1-P4-M-009 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-29", "start_xy_m": [30.77, 4.08], "end_xy_m": [30.77, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2709, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1104", "start_xy_m": [31.09, 6.33], "end_xy_m": [31.09, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0491, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0009, P3-RLE-MURO-0010
- source_label: M.H.A. e= 30
- source_label_tag: LBL_3_wall_label_0036
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0009", "P3-RLE-MURO-0010"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00261: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-010 y E1-P2-M-010, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 11/43 — E1-P3-M-007

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0112`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00262 | 10262 | 382 | 391 | (32.491, 4.082, 11.88) | (32.491, 4.082, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 1''–2 (1'' +0.1815 m) |
| i | Eb–Ec (Eb +0.0999 m) | 1''–2 (1'' +0.1815 m) |
| j | Eb–Ec (Ec -0.1001 m) | 1''–2 (1'' +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 4.081500, 13.860000 m.
- i: 31.190900, 4.081500, 13.860000 m.
- j: 33.790900, 4.081500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-016 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-007: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-016, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-007 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-007: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-004 | 5.375965 | 4.808937 | 0.000000 |
| nearest_wall | E1-P3-M-009 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P2-M-007 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-007 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-007, E1-P4-M-007.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-007, E1-P3-M-007, E1-P4-M-007.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-007 | 0.000000 | 0.000000 |
| j | E1-P4-M-007 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-19", "start_xy_m": [30.77, 4.08], "end_xy_m": [34.17, 4.08], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 0.8, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1004", "start_xy_m": [27.24, 4.08], "end_xy_m": [33.89, 4.08], "length_m": 6.65, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 4.05, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0015, P3-RLE-MURO-0016
- source_label: M.H.A. e= 20
- source_label_tag: LBL_3_wall_label_0038
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0015", "P3-RLE-MURO-0016"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00262: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-007 y E1-P2-M-007, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 12/43 — E1-P3-M-008

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0111`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00260 | 10260 | 378 | 389 | (32.491, 14.027, 11.88) | (32.491, 14.027, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 2a–3 (2a +0.1815 m) |
| i | Ea–Eb (Ea +0.0999 m) | 2a–3 (2a +0.1815 m) |
| j | Ec–Ed (Ed -0.1001 m) | 2a–3 (2a +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 14.026500, 13.860000 m.
- i: 30.890900, 14.026500, 13.860000 m.
- j: 34.090900, 14.026500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-014 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-008: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-014, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-008 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-008: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-006 | 4.107656 | 3.569784 | 0.000000 |
| nearest_wall | E1-P3-M-003 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P2-M-008 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-008 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-008, E1-P4-M-008.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-008, E1-P3-M-008, E1-P4-M-008.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-008 | 0.000000 | 0.000000 |
| j | E1-P4-M-008 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-4", "start_xy_m": [30.77, 14.025], "end_xy_m": [34.17, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1404", "start_xy_m": [30.79, 14.025], "end_xy_m": [34.19, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0001, P3-RLE-MURO-0002
- source_label: M.H.A. e= 20
- source_label_tag: LBL_3_wall_label_0032
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0001", "P3-RLE-MURO-0002"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00260: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-008 y E1-P2-M-008, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 13/43 — E1-P3-M-009

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0120`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00263 | 10263 | 384 | 392 | (33.941, 5.256, 11.88) | (33.941, 5.256, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +1.3565 m) |
| i | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +0.2815 m) |
| j | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 33.940900, 5.256500, 13.860000 m.
- i: 33.940900, 4.181500, 13.860000 m.
- j: 33.940900, 6.331500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-017 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-009: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-017, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ec y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-009 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-009: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-005 | 4.490423 | 3.880920 | 0.000000 |
| nearest_wall | E1-P3-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P2-M-009 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-010 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-009, E1-P4-M-010.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-009, E1-P3-M-009, E1-P4-M-010.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-010 | 0.000000 | 0.000000 |
| j | E1-P4-M-010 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-24", "start_xy_m": [34.17, 4.08], "end_xy_m": [34.17, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2291, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1204", "start_xy_m": [33.89, 6.33], "end_xy_m": [33.89, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0509, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0012, P3-RLE-MURO-0013
- source_label: M.H.A. e= 30
- source_label_tag: LBL_3_wall_label_0037
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0012", "P3-RLE-MURO-0013"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00263: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-009 y E1-P2-M-009, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 14/43 — E1-P3-M-005

MURO · EDIFICIO_1 · P3 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_3_wall_0115`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00264 | 10264 | 386 | 393 | (34.216, 13.187, 11.88) | (34.216, 13.187, 15.84) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ed–F (Ed +0.0249 m) | 2–2a (2a -0.6579 m) |
| i | Ed–F (Ed +0.0249 m) | 2–2a (2a -1.3973 m) |
| j | Ed–F (Ed +0.0249 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 34.215900, 13.187100, 13.860000 m.
- i: 34.215900, 12.447700, 13.860000 m.
- j: 34.215900, 13.926500, 13.860000 m.
- z_bottom: 11.880000 m.
- z_top: 15.840000 m.

### NIVEL Y ELEVACIÓN

Nivel P3: Z modelo **15.84 m**; elevación fuente **+7.87 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-018 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-005: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-018, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.959999999999999 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P3. Buscar X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ed y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P3-M-005 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-005: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P3-C-006 | 4.063185 | 3.473165 | 0.000000 |
| nearest_wall | E1-P3-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P2-M-005 | 0.000000 | 0.000000 | 0.000000 |
| above | E1-P4-M-012 | 0.000000 | 0.000000 | 0.000000 |

- Encuentros del candidato: E1-P2-M-005, E1-P4-M-012.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-005, E1-P3-M-005, E1-P4-M-012.
- Paneles visuales del mismo piso: E1-P3-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-012 | 0.000000 | 0.000000 |
| j | E1-P4-M-012 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-9", "start_xy_m": [34.17, 14.025], "end_xy_m": [34.17, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0459, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1604", "start_xy_m": [34.19, 14.025], "end_xy_m": [34.19, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0259, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P3-RLE-MURO-0006, P3-RLE-MURO-0008
- source_label: M.H.A. e= 25
- source_label_tag: LBL_3_wall_label_0034
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P3-RLE-MURO-0006", "P3-RLE-MURO-0008"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00264: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P3-M-005 y E1-P2-M-005, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 15/43 — E1-P4-M-003

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0125`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00266 | 10266 | 388 | 395 | (30.766, 13.187, 15.84) | (30.766, 13.187, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | E–Ea (Ea -0.0251 m) | 2–2a (2a -0.6579 m) |
| i | E–Ea (Ea -0.0251 m) | 2–2a (2a -1.3973 m) |
| j | E–Ea (Ea -0.0251 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 30.765900, 13.187100, 17.820000 m.
- i: 30.765900, 12.447700, 17.820000 m.
- j: 30.765900, 13.926500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-013 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-003: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-013, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X E–Ea (Ea -0.0251 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ea y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-003 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-003: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-003 | 4.063215 | 3.473195 | 0.000000 |
| nearest_wall | E1-P4-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P3-M-003 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-003.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-003, E1-P3-M-003, E1-P4-M-003.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-008 | 1.583741 | 1.484074 |
| j | E1-P4-M-008 | 0.160078 | 0.125000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-15", "start_xy_m": [30.77, 14.025], "end_xy_m": [30.77, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0041, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1505", "start_xy_m": [30.79, 14.025], "end_xy_m": [30.79, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0241, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0003, P4-RLE-MURO-0005
- source_label: M.H.A. e= 25
- source_label_tag: LBL_4_wall_label_0033
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0003", "P4-RLE-MURO-0005"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00266: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-003 y E1-P3-M-003, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 16/43 — E1-P4-M-009

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0132`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00268 | 10268 | 390 | 397 | (31.041, 5.256, 15.84) | (31.041, 5.256, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +1.3565 m) |
| i | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +0.2815 m) |
| j | Ea–Eb (Eb -0.0501 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 31.040900, 5.256500, 17.820000 m.
- i: 31.040900, 4.181500, 17.820000 m.
- j: 31.040900, 6.331500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-015 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-010: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-015, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X Ea–Eb (Eb -0.0501 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-009 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-010: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-002 | 4.490451 | 3.880948 | 0.000000 |
| nearest_wall | E1-P4-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P3-M-010 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-010.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-010, E1-P3-M-010, E1-P4-M-009.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-007 | 0.180278 | 0.150000 |
| j | E1-P4-M-007 | 2.254994 | 2.155226 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-30", "start_xy_m": [30.77, 4.08], "end_xy_m": [30.77, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2709, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1105", "start_xy_m": [31.09, 6.33], "end_xy_m": [31.09, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0491, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0009, P4-RLE-MURO-0010
- source_label: M.H.A. e= 30
- source_label_tag: LBL_4_wall_label_0036
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0009", "P4-RLE-MURO-0010"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00268: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-009 y E1-P3-M-010, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 17/43 — E1-P4-M-007

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0124`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00269 | 10269 | 391 | 398 | (32.491, 4.082, 15.84) | (32.491, 4.082, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 1''–2 (1'' +0.1815 m) |
| i | Eb–Ec (Eb +0.0999 m) | 1''–2 (1'' +0.1815 m) |
| j | Eb–Ec (Ec -0.1001 m) | 1''–2 (1'' +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 4.081500, 17.820000 m.
- i: 31.190900, 4.081500, 17.820000 m.
- j: 33.790900, 4.081500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-016 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-007: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-016, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X Eb–Ec (Eb +1.3999 m) / Y 1''–2 (1'' +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-007 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-007: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-004 | 5.375989 | 4.808961 | 0.000000 |
| nearest_wall | E1-P4-M-010 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P3-M-007 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-007.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-007, E1-P3-M-007, E1-P4-M-007.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-009 | 0.180278 | 0.100000 |
| j | E1-P4-M-010 | 0.180278 | 0.100000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-20", "start_xy_m": [30.77, 4.08], "end_xy_m": [34.17, 4.08], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 0.8, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1005", "start_xy_m": [27.24, 4.08], "end_xy_m": [33.89, 4.08], "length_m": 6.65, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 2.6, "overlap_ratio": 1.0, "length_delta_m": 4.05, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0015, P4-RLE-MURO-0016
- source_label: M.H.A. e= 20
- source_label_tag: LBL_4_wall_label_0038
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0015", "P4-RLE-MURO-0016"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00269: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-007 y E1-P3-M-007, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 18/43 — E1-P4-M-008

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0123`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00267 | 10267 | 389 | 396 | (32.491, 14.027, 15.84) | (32.491, 14.027, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Eb–Ec (Eb +1.3999 m) | 2a–3 (2a +0.1815 m) |
| i | Ea–Eb (Ea +0.0999 m) | 2a–3 (2a +0.1815 m) |
| j | Ec–Ed (Ed -0.1001 m) | 2a–3 (2a +0.1815 m) |

### COORDENADAS GLOBALES (m)

- center: 32.490900, 14.026500, 17.820000 m.
- i: 30.890900, 14.026500, 17.820000 m.
- j: 34.090900, 14.026500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-014 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-008: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-014, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: SHAFT_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X Eb–Ec (Eb +1.3999 m) / Y 2a–3 (2a +0.1815 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Eb y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-008 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-008: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-006 | 4.107656 | 3.569784 | 0.000000 |
| nearest_wall | E1-P4-M-003 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P3-M-008 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-008.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-008, E1-P3-M-008, E1-P4-M-008.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-003 | 0.160078 | 0.100000 |
| j | E1-P4-M-012 | 0.160078 | 0.100000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-5", "start_xy_m": [30.77, 14.025], "end_xy_m": [34.17, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1405", "start_xy_m": [30.79, 14.025], "end_xy_m": [34.19, 14.025], "length_m": 3.4, "thickness_m": 0.2, "match": {"perpendicular_distance_m": 0.0015, "angle_delta_deg": 0.0, "overlap_m": 3.2, "overlap_ratio": 1.0, "length_delta_m": 0.2, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0001, P4-RLE-MURO-0002
- source_label: M.H.A. e= 20
- source_label_tag: LBL_4_wall_label_0032
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0001", "P4-RLE-MURO-0002"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): SHAFT_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00267: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-008 y E1-P3-M-008, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 19/43 — E1-P4-M-010

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0128`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00270 | 10270 | 392 | 399 | (33.941, 5.256, 15.84) | (33.941, 5.256, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +1.3565 m) |
| i | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +0.2815 m) |
| j | Ec–Ed (Ec +0.0499 m) | 1''–2 (1'' +2.4315 m) |

### COORDENADAS GLOBALES (m)

- center: 33.940900, 5.256500, 17.820000 m.
- i: 33.940900, 4.181500, 17.820000 m.
- j: 33.940900, 6.331500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-017 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-009: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-017, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X Ec–Ed (Ec +0.0499 m) / Y 1''–2 (1'' +1.3565 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ec y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-010 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-009: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-005 | 4.490421 | 3.880918 | 0.000000 |
| nearest_wall | E1-P4-M-007 | 0.180278 | 0.000000 | 0.000000 |
| below | E1-P3-M-009 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-009.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-009, E1-P3-M-009, E1-P4-M-010.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-007 | 0.180278 | 0.150000 |
| j | E1-P4-M-007 | 2.254994 | 2.155226 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-25", "start_xy_m": [34.17, 4.08], "end_xy_m": [34.17, 5.655], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.2291, "angle_delta_deg": 0.0, "overlap_m": 1.4735, "overlap_ratio": 0.9356, "length_delta_m": 0.575, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1205", "start_xy_m": [33.89, 6.33], "end_xy_m": [33.89, 4.08], "length_m": 2.25, "thickness_m": 0.3, "match": {"perpendicular_distance_m": 0.0509, "angle_delta_deg": 0.0, "overlap_m": 2.1485, "overlap_ratio": 0.9993, "length_delta_m": 0.1, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0012, P4-RLE-MURO-0013
- source_label: M.H.A. e= 30
- source_label_tag: LBL_4_wall_label_0037
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0012", "P4-RLE-MURO-0013"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00270: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-010 y E1-P3-M-009, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 20/43 — E1-P4-M-012

MURO · EDIFICIO_1 · P4 · Prioridad A · UNRESOLVED_REAL

Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.

Geometry tag: `SOL_4_wall_0130`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00271 | 10271 | 393 | 400 | (34.216, 13.187, 15.84) | (34.216, 13.187, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ed–F (Ed +0.0249 m) | 2–2a (2a -0.6579 m) |
| i | Ed–F (Ed +0.0249 m) | 2–2a (2a -1.3973 m) |
| j | Ed–F (Ed +0.0249 m) | 2a–3 (2a +0.0815 m) |

### COORDENADAS GLOBALES (m)

- center: 34.215900, 13.187100, 17.820000 m.
- i: 34.215900, 12.447700, 17.820000 m.
- j: 34.215900, 13.926500, 17.820000 m.
- z_bottom: 15.840000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-018 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P3-M-005: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-103.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-018, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.25 m; altura visible 3.960000000000001 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: MEDIA como candidato de revisión.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETURN_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-103** — Planta fuente del elemento P4. Buscar X Ed–F (Ed +0.0249 m) / Y 2–2a (2a -0.6579 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-103.dxf`.
- **2017_67-304** — Elevaciones: localizar el eje Ed y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-304.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P4-M-012 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P3-M-005: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P4-C-006 | 4.063184 | 3.473164 | 0.000000 |
| nearest_wall | E1-P4-M-008 | 0.160078 | 0.000000 | 0.000000 |
| below | E1-P3-M-005 | 0.000000 | 0.000000 | 0.000000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E1-P3-M-005.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P2-M-005, E1-P3-M-005, E1-P4-M-012.
- Paneles visuales del mismo piso: E1-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P4-M-008 | 1.583741 | 1.484074 |
| j | E1-P4-M-008 | 0.160078 | 0.125000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "S-W-10", "start_xy_m": [34.17, 14.025], "end_xy_m": [34.17, 12.45], "length_m": 1.575, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0459, "angle_delta_deg": 0.0, "overlap_m": 1.4765, "overlap_ratio": 0.9984, "length_delta_m": 0.0962, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-W-1605", "start_xy_m": [34.19, 14.025], "end_xy_m": [34.19, 12.445], "length_m": 1.58, "thickness_m": 0.25, "match": {"perpendicular_distance_m": 0.0259, "angle_delta_deg": 0.0, "overlap_m": 1.4788, "overlap_ratio": 1.0, "length_delta_m": 0.1012, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-103.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P4-RLE-MURO-0006, P4-RLE-MURO-0008
- source_label: M.H.A. e= 25
- source_label_tag: LBL_4_wall_label_0034
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: TEXT_LABEL
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P4-RLE-MURO-0006", "P4-RLE-MURO-0008"], "thickness_m": 0.25}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETURN_WALL. Alcance FE: PRIMARY_FE_REVIEW_REQUIRED.

### EJES LOCALES

- POST-A-00271: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P4-M-012 y E1-P3-M-005, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 21/43 — E1-P1-C-016

COLUMNA · EDIFICIO_1 · P1 · Prioridad B · STAIR_STRUCTURE

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_column_0022`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00135 | 10135 | 179 | 180 | (57.518, 18.843, 3.96) | (57.518, 18.843, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +2.6926 m) |
| i | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +2.6926 m) |
| j | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +2.6926 m) |

### COORDENADAS GLOBALES (m)

- center: 57.518062, 18.842590, 5.940000 m.
- i: 57.518062, 18.842590, 3.960000 m.
- j: 57.518062, 18.842590, 7.920000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este columna en POST-FLOAT-001 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-C-013: distancia entre ejes XY 2.6927 m, separación entre huellas 2.1676 m y separación vertical 0.0000 m. Pertenece al contexto de escalera B; su apoyo y alcance FE siguen sin aprobar.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-PILAR.
- HECHO: regeneración reproduce POST-FLOAT-001, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.35 m; altura visible 3.96 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS el detalle de apoyo exterior ni su vínculo resistente con el edificio principal; SECONDARY_STRUCTURE_EXPECTED no equivale a una exclusión FE aprobada.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: EXTERIOR_STAIR_SUPPORT En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: MEDIA para contexto escalera; BAJA para vínculo resistente.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: La entidad está conservada en el modelo auditado; desconexión sola no prueba error. Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H–H1 (H +0.0271 m) / Y OUTBOARD >3 (3 +2.6926 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-308** — Elevaciones: localizar el eje H y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-308.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-C-016 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-C-013: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-015 | 2.692589 | 2.167454 | 0.000000 |
| nearest_wall | E1-P1-M-027 | 10.122938 | 9.797938 | 0.000000 |
| below | E1-S1-C-013 | 2.692726 | 2.167590 | 0.000000 |
| above | E1-P2-C-015 | 2.511213 | 1.986066 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-C-016.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-027 | 10.122938 | 9.972938 |
| j | E1-P1-M-027 | 10.122938 | 9.972938 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-PILAR
- sourceTags: CAD_1_column_plan_0293
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_GEOMETRY_RLE-PILAR
- section_confidence: CAD_GEOMETRY
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: "NO ENCONTRADA"
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): EXTERIOR_STAIR_SUPPORT. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00135: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿Qué detalle muestra el apoyo real de E1-P1-C-016 en escalera B y su conexión o independencia respecto del edificio?

## 22/43 — E1-P1-C-017

COLUMNA · EDIFICIO_1 · P1 · Prioridad B · STAIR_STRUCTURE

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_column_0023`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00136 | 10136 | 181 | 182 | (57.518, 26.176, 3.96) | (57.518, 26.176, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +10.0256 m) |
| i | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +10.0256 m) |
| j | H–H1 (H +0.0271 m) | OUTBOARD >3 (3 +10.0256 m) |

### COORDENADAS GLOBALES (m)

- center: 57.518062, 26.175583, 5.940000 m.
- i: 57.518062, 26.175583, 3.960000 m.
- j: 57.518062, 26.175583, 7.920000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este columna en POST-FLOAT-002 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-C-013: distancia entre ejes XY 10.0256 m, separación entre huellas 9.5006 m y separación vertical 0.0000 m. Pertenece al contexto de escalera B; su apoyo y alcance FE siguen sin aprobar.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-PILAR.
- HECHO: regeneración reproduce POST-FLOAT-002, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.35 m; altura visible 3.96 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS el detalle de apoyo exterior ni su vínculo resistente con el edificio principal; SECONDARY_STRUCTURE_EXPECTED no equivale a una exclusión FE aprobada.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: EXTERIOR_STAIR_SUPPORT En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: MEDIA para contexto escalera; BAJA para vínculo resistente.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: La entidad está conservada en el modelo auditado; desconexión sola no prueba error. Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H–H1 (H +0.0271 m) / Y OUTBOARD >3 (3 +10.0256 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-308** — Elevaciones: localizar el eje H y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-308.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-C-017 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-C-013: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-020 | 4.947060 | 4.482252 | 0.000000 |
| nearest_wall | E1-P1-M-027 | 10.122938 | 9.797938 | 0.000000 |
| below | E1-S1-C-013 | 10.025619 | 9.500583 | 0.000000 |
| above | E1-P2-C-015 | 9.844096 | 9.319058 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-C-017.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-027 | 10.122938 | 9.972938 |
| j | E1-P1-M-027 | 10.122938 | 9.972938 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-PILAR
- sourceTags: CAD_1_column_plan_0295
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_GEOMETRY_RLE-PILAR
- section_confidence: CAD_GEOMETRY
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: "NO ENCONTRADA"
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): EXTERIOR_STAIR_SUPPORT. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00136: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿Qué detalle muestra el apoyo real de E1-P1-C-017 en escalera B y su conexión o independencia respecto del edificio?

## 23/43 — E1-P1-M-016

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0083`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00237 | 10237 | 345 | 346 | (64.499, -3.575, 3.96) | (64.499, -3.575, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H'–H2 (H2 -1.8169 m) | OUTBOARD <1 (1 -3.5749 m) |
| i | H'–H2 (H' +0.7893 m) | OUTBOARD <1 (1 -3.5749 m) |
| j | H'–H2 (H2 -0.0750 m) | OUTBOARD <1 (1 -3.5749 m) |

### COORDENADAS GLOBALES (m)

- center: 64.499150, -3.574900, 5.940000 m.
- i: 62.757300, -3.574900, 5.940000 m.
- j: 66.241000, -3.574900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 13.8663 m, separación entre huellas 13.7163 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H'–H2 (H2 -1.8169 m) / Y OUTBOARD <1 (1 -3.5749 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-306** — Elevaciones: localizar el eje H2 y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-306.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-016 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 3.844200 | 3.336776 | 0.000000 |
| nearest_wall | E1-P1-M-020 | 0.106066 | 0.000000 | 0.000000 |
| below | E1-S1-M-060 | 13.866300 | 13.716300 | 0.000000 |
| above | E1-P2-M-009 | 29.842028 | 29.677709 | 0.000000 |

- Encuentros del candidato: E1-P1-V-072, E1-P1-V-098.
- Vigas con encuentro candidato: E1-P1-V-072, E1-P1-V-098.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-023 | 2.650000 | 2.575000 |
| j | E1-P1-M-020 | 0.106066 | 0.075000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0048, P1-RLE-MURO-0049
- source_label: M.H.A. e=15
- source_label_tag: LBL_1_wall_label_0099
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0048", "P1-RLE-MURO-0049"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00237: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-016 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 24/43 — E1-P1-M-024

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0097`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00235 | 10235 | 341 | 342 | (64.516, -0.525, 3.96) | (64.516, -0.525, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H'–H2 (H2 -1.8000 m) | OUTBOARD <1 (1 -0.5249 m) |
| i | H–H1 (H1 -0.0750 m) | OUTBOARD <1 (1 -0.5249 m) |
| j | I–IA (I +0.3000 m) | OUTBOARD <1 (1 -0.5249 m) |

### COORDENADAS GLOBALES (m)

- center: 64.516000, -0.524900, 5.940000 m.
- i: 61.241000, -0.524900, 5.940000 m.
- j: 67.791000, -0.524900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 12.3501 m, separación entre huellas 12.2000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H'–H2 (H2 -1.8000 m) / Y OUTBOARD <1 (1 -0.5249 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-306** — Elevaciones: localizar el eje H2 y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-306.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-024 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 0.600037 | 0.175037 | 0.000000 |
| nearest_wall | E1-P1-M-021 | 0.050000 | 0.050000 | 0.000000 |
| below | E1-S1-M-060 | 12.350078 | 12.200000 | 0.000000 |
| above | E1-P2-M-009 | 27.702810 | 27.542291 | 0.000000 |

- Encuentros del candidato: E1-P1-V-068.
- Vigas con encuentro candidato: E1-P1-V-068.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-015 | 0.325000 | 0.175000 |
| j | E1-P1-M-021 | 0.050000 | 0.050000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0050, P1-RLE-MURO-0052
- source_label: M.H.A. e=15
- source_label_tag: LBL_1_wall_label_0106
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0050", "P1-RLE-MURO-0052"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00235: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-024 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 25/43 — E1-P1-M-023

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0098`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00236 | 10236 | 343 | 344 | (65.274, -6.225, 3.96) | (65.274, -6.225, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H'–H2 (H2 -1.0419 m) | OUTBOARD <1 (1 -6.2249 m) |
| i | H'–H2 (H' +0.7893 m) | OUTBOARD <1 (1 -6.2249 m) |
| j | I–IA (I +0.3000 m) | OUTBOARD <1 (1 -6.2249 m) |

### COORDENADAS GLOBALES (m)

- center: 65.274150, -6.224900, 5.940000 m.
- i: 62.757300, -6.224900, 5.940000 m.
- j: 67.791000, -6.224900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-005 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 13.8663 m, separación entre huellas 13.7163 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-005, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H'–H2 (H2 -1.0419 m) / Y OUTBOARD <1 (1 -6.2249 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-306** — Elevaciones: localizar el eje H2 y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-306.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-023 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 6.300037 | 5.875037 | 0.000000 |
| nearest_wall | E1-P1-M-022 | 0.050000 | 0.050000 | 0.000000 |
| below | E1-S1-M-060 | 13.866300 | 13.716300 | 0.000000 |
| above | E1-P2-M-009 | 30.637854 | 30.471303 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-023.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-016 | 2.650000 | 2.575000 |
| j | E1-P1-M-022 | 0.050000 | 0.050000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0044, P1-RLE-MURO-0046
- source_label: M.H.A. e= 15
- source_label_tag: LBL_1_wall_label_0098
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0044", "P1-RLE-MURO-0046"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00236: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-023 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 26/43 — E1-P1-M-020

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0092`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00238 | 10238 | 347 | 348 | (66.316, -2.05, 3.96) | (66.316, -2.05, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | SOBRE EJE H2 (H2 +0.0000 m) | OUTBOARD <1 (1 -2.0499 m) |
| i | SOBRE EJE H2 (H2 +0.0000 m) | OUTBOARD <1 (1 -3.4999 m) |
| j | SOBRE EJE H2 (H2 +0.0000 m) | OUTBOARD <1 (1 -0.5999 m) |

### COORDENADAS GLOBALES (m)

- center: 66.316000, -2.049900, 5.940000 m.
- i: 66.316000, -3.499900, 5.940000 m.
- j: 66.316000, -0.599900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 17.4250 m, separación entre huellas 17.2000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: EXTERIOR_STAIR_SUPPORT En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X SOBRE EJE H2 (H2 +0.0000 m) / Y OUTBOARD <1 (1 -2.0499 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-306** — Elevaciones: localizar el eje H2 y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-306.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-020 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 1.317370 | 0.777481 | 0.000000 |
| nearest_wall | E1-P1-M-024 | 0.075000 | 0.000000 | 0.000000 |
| below | E1-S1-M-060 | 17.425000 | 17.200000 | 0.000000 |
| above | E1-P2-M-009 | 32.726272 | 32.503703 | 0.000000 |

- Encuentros del candidato: E1-P1-V-098.
- Vigas con encuentro candidato: E1-P1-V-098.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-016 | 0.106066 | 0.075000 |
| j | E1-P1-M-024 | 0.075000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0042, P1-RLE-MURO-0043
- source_label: M.H.A. e=15
- source_label_tag: LBL_1_wall_label_0093
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0042", "P1-RLE-MURO-0043"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): EXTERIOR_STAIR_SUPPORT. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00238: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-020 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 27/43 — E1-P1-M-022

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0094`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00242 | 10242 | 355 | 356 | (69.016, -6.225, 3.96) | (69.016, -6.225, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | I–IA (IA -1.0750 m) | OUTBOARD <1 (1 -6.2249 m) |
| i | I–IA (I +0.3500 m) | OUTBOARD <1 (1 -6.2249 m) |
| j | IA–I' (IA +0.1000 m) | OUTBOARD <1 (1 -6.2249 m) |

### COORDENADAS GLOBALES (m)

- center: 69.016000, -6.224900, 5.940000 m.
- i: 67.841000, -6.224900, 5.940000 m.
- j: 70.191000, -6.224900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-006 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 18.9500 m, separación entre huellas 18.8000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-006, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X I–IA (IA -1.0750 m) / Y OUTBOARD <1 (1 -6.2249 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje IA y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-022 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 6.312327 | 5.875199 | 0.000000 |
| nearest_wall | E1-P1-M-023 | 0.050000 | 0.050000 | 0.000000 |
| below | E1-S1-M-060 | 18.950000 | 18.800000 | 0.000000 |
| above | E1-P2-M-009 | 35.461387 | 35.295992 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-022.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-023 | 0.050000 | 0.050000 |
| j | E1-P1-M-023 | 2.400000 | 2.400000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0044, P1-RLE-MURO-0046
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0044", "P1-RLE-MURO-0046"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00242: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-022 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 28/43 — E1-P1-M-021

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0093`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00243 | 10243 | 357 | 358 | (69.016, -0.525, 3.96) | (69.016, -0.525, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | I–IA (IA -1.0750 m) | OUTBOARD <1 (1 -0.5249 m) |
| i | I–IA (I +0.3500 m) | OUTBOARD <1 (1 -0.5249 m) |
| j | IA–I' (IA +0.1000 m) | OUTBOARD <1 (1 -0.5249 m) |

### COORDENADAS GLOBALES (m)

- center: 69.016000, -0.524900, 5.940000 m.
- i: 67.841000, -0.524900, 5.940000 m.
- j: 70.191000, -0.524900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-007 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 18.9501 m, separación entre huellas 18.8000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-007, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X I–IA (IA -1.0750 m) / Y OUTBOARD <1 (1 -0.5249 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje IA y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-021 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-022 | 0.717678 | 0.180415 | 0.000000 |
| nearest_wall | E1-P1-M-035 | 0.020300 | 0.020300 | 0.000000 |
| below | E1-S1-M-060 | 18.950051 | 18.800000 | 0.000000 |
| above | E1-P2-M-009 | 34.225239 | 34.066393 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-021.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-024 | 0.050000 | 0.050000 |
| j | E1-P1-M-035 | 0.020300 | 0.020300 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0050, P1-RLE-MURO-0052
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0050", "P1-RLE-MURO-0052"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00243: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-021 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 29/43 — E1-P1-M-031

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0088`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00245 | 10245 | 361 | 362 | (70.091, -11.136, 3.96) | (70.091, -11.136, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -11.1362 m) |
| i | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -11.4754 m) |
| j | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -10.7970 m) |

### COORDENADAS GLOBALES (m)

- center: 70.091000, -11.136200, 5.940000 m.
- i: 70.091000, -11.475400, 5.940000 m.
- j: 70.091000, -10.797000, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-008 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 21.3386 m, separación entre huellas 21.0903 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-008, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: EXTERIOR_STAIR_MEMBER En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X SOBRE EJE IA (IA -0.0000 m) / Y OUTBOARD <1 (1 -11.1362 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje IA y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-031 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 11.097274 | 10.664437 | 0.000000 |
| nearest_wall | E1-P1-M-036 | 0.156436 | 0.020300 | 0.000000 |
| below | E1-S1-M-060 | 21.338630 | 21.090273 | 0.000000 |
| above | E1-P2-M-009 | 39.130362 | 38.899520 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-031.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-036 | 0.787641 | 0.688984 |
| j | E1-P1-M-036 | 0.156436 | 0.120300 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0038, P1-RLE-MURO-0039
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0038", "P1-RLE-MURO-0039"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): EXTERIOR_STAIR_MEMBER. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00245: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-031 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 30/43 — E1-P1-M-034

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0085`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00246 | 10246 | 363 | 364 | (70.091, -10.331, 3.96) | (70.091, -10.331, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -10.3310 m) |
| i | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -10.5970 m) |
| j | SOBRE EJE IA (IA -0.0000 m) | OUTBOARD <1 (1 -10.0651 m) |

### COORDENADAS GLOBALES (m)

- center: 70.091000, -10.331050, 5.940000 m.
- i: 70.091000, -10.597000, 5.940000 m.
- j: 70.091000, -10.065100, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-009 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 21.2678 m, separación entre huellas 21.0186 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-009, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: EXTERIOR_STAIR_MEMBER En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X SOBRE EJE IA (IA -0.0000 m) / Y OUTBOARD <1 (1 -10.3310 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje IA y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-034 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 10.383902 | 9.945777 | 0.000000 |
| nearest_wall | E1-P1-M-036 | 0.156436 | 0.020300 | 0.000000 |
| below | E1-S1-M-060 | 21.267772 | 21.018578 | 0.000000 |
| above | E1-P2-M-009 | 38.856085 | 38.623604 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-034.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-036 | 0.156436 | 0.120300 |
| j | E1-P1-M-036 | 0.643249 | 0.545334 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0035, P1-RLE-MURO-0039
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0035", "P1-RLE-MURO-0039"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): EXTERIOR_STAIR_MEMBER. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00246: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-034 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 31/43 — E1-P1-M-036

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0086`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00247 | 10247 | 365 | 366 | (71.474, -10.697, 3.96) | (71.474, -10.697, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | IA–I' (I' -1.0172 m) | OUTBOARD <1 (1 -10.6970 m) |
| i | IA–I' (IA +0.1203 m) | OUTBOARD <1 (1 -10.6970 m) |
| j | I'–IB (I' +0.2453 m) | OUTBOARD <1 (1 -10.6970 m) |

### COORDENADAS GLOBALES (m)

- center: 71.473800, -10.697000, 5.940000 m.
- i: 70.211300, -10.697000, 5.940000 m.
- j: 72.736300, -10.697000, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-010 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 21.4471 m, separación entre huellas 21.2873 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-010, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X IA–I' (I' -1.0172 m) / Y OUTBOARD <1 (1 -10.6970 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje I' y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-036 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 10.734637 | 10.284637 | 0.000000 |
| nearest_wall | E1-P1-M-037 | 0.150000 | 0.000000 | 0.000000 |
| below | E1-S1-M-060 | 21.447066 | 21.287258 | 0.000000 |
| above | E1-P2-M-009 | 39.203465 | 39.026752 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-036.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-034 | 0.156436 | 0.102040 |
| j | E1-P1-M-037 | 0.150000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0036, P1-RLE-MURO-0037
- source_label: M.H.A. e=20
- source_label_tag: LBL_1_wall_label_0092
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0036", "P1-RLE-MURO-0037"], "thickness_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00247: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-036 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 32/43 — E1-P1-M-035

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0087`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00248 | 10248 | 367 | 368 | (71.474, -0.525, 3.96) | (71.474, -0.525, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | IA–I' (I' -1.0172 m) | OUTBOARD <1 (1 -0.5249 m) |
| i | IA–I' (IA +0.1203 m) | OUTBOARD <1 (1 -0.5249 m) |
| j | I'–IB (I' +0.2453 m) | OUTBOARD <1 (1 -0.5249 m) |

### COORDENADAS GLOBALES (m)

- center: 71.473800, -0.524900, 5.940000 m.
- i: 70.211300, -0.524900, 5.940000 m.
- j: 72.736300, -0.524900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-011 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 21.3203 m, separación entre huellas 21.1703 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-011, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X IA–I' (I' -1.0172 m) / Y OUTBOARD <1 (1 -0.5249 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje I' y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-035 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 0.562537 | 0.137537 | 0.000000 |
| nearest_wall | E1-P1-M-021 | 0.020300 | 0.020300 | 0.000000 |
| below | E1-S1-M-060 | 21.320345 | 21.170300 | 0.000000 |
| above | E1-P2-M-009 | 36.574474 | 36.416111 | 0.000000 |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-035.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-021 | 0.020300 | 0.020300 |
| j | E1-P1-M-037 | 0.150000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0050, P1-RLE-MURO-0052
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0050", "P1-RLE-MURO-0052"], "thickness_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00248: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-035 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 33/43 — E1-P1-M-037

MURO · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_wall_0090`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00250 | 10250 | 371 | 372 | (72.886, -5.963, 3.96) | (72.886, -5.963, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | I'–IB (I' +0.3953 m) | OUTBOARD <1 (1 -5.9627 m) |
| i | I'–IB (I' +0.3953 m) | OUTBOARD <1 (1 -11.4754 m) |
| j | I'–IB (I' +0.3953 m) | OUTBOARD <1 (1 -0.4499 m) |

### COORDENADAS GLOBALES (m)

- center: 72.886300, -5.962650, 5.940000 m.
- i: 72.886300, -11.475400, 5.940000 m.
- j: 72.886300, -0.449900, 5.940000 m.
- z_bottom: 3.960000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este muro en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-S1-M-060: distancia entre ejes XY 23.9953 m, separación entre huellas 23.6953 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-MURO_CONTOUR_PAIR.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 3.9599999999999995 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: RETAINING_WALL En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_CONTOUR_PAIR Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X I'–IB (I' +0.3953 m) / Y OUTBOARD <1 (1 -5.9627 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje I' y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-M-037 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-S1-M-060: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 0.627640 | 0.137537 | 0.000000 |
| nearest_wall | E1-P1-M-036 | 0.150000 | 0.000000 | 0.000000 |
| below | E1-S1-M-060 | 23.995300 | 23.695300 | 0.000000 |
| above | E1-P2-M-009 | 39.219817 | 38.921932 | 0.000000 |

- Encuentros del candidato: E1-P1-V-098.
- Vigas con encuentro candidato: E1-P1-V-098.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-036 | 0.792721 | 0.694785 |
| j | E1-P1-M-035 | 0.167705 | 0.150000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-MURO_CONTOUR_PAIR
- sourceTags: P1-RLE-MURO-0040, P1-RLE-MURO-0041
- source_label: M.H.A. e=30
- source_label_tag: LBL_1_wall_label_0097
- section_source: NO ENCONTRADA
- section_confidence: NO ENCONTRADA
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_CONTOUR_PAIR", "audit_file": "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json", "face_ids": ["P1-RLE-MURO-0040", "P1-RLE-MURO-0041"], "thickness_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): RETAINING_WALL. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00250: dirección geométrica i→j, global XYZ = [0.0, 0.0, 1.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-M-037 y E1-S1-M-060, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 34/43 — E1-P1-V-068

VIGA · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_beam_0185`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00664 | 10664 | 1212 | 519 | (61.316, -3.5, 7.92) | (61.316, -0.6, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | SOBRE EJE H1 (H1 +0.0000 m) | OUTBOARD <1 (1 -2.0499 m) |
| i | SOBRE EJE H1 (H1 +0.0000 m) | OUTBOARD <1 (1 -3.4999 m) |
| j | SOBRE EJE H1 (H1 +0.0000 m) | OUTBOARD <1 (1 -0.5999 m) |

### COORDENADAS GLOBALES (m)

- center: 61.316000, -2.049900, 7.420000 m.
- i: 61.316000, -3.499900, 7.420000 m.
- j: 61.316000, -0.599900, 7.420000 m.
- z_bottom: 6.920000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-024: distancia entre ejes XY 0.0750 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 1.0 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: LANDING_BEAM En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X SOBRE EJE H1 (H1 +0.0000 m) / Y OUTBOARD <1 (1 -2.0499 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-306** — Elevaciones: localizar el eje H1 y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-306.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-V-068 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-024: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-013 | 3.877740 | 3.412110 | 0.000000 |
| nearest_wall | E1-P1-M-024 | 0.075000 | 0.000000 | 0.000000 |
| below | E1-S1-V-079 | 13.419104 | 13.211045 | 2.960000 |
| above | E1-P2-V-089 | 0.781300 | 0.481300 | 3.160000 |

- Encuentros del candidato: E1-P1-M-024, E1-P1-V-072.
- Vigas con encuentro candidato: E1-P1-V-072.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-016 | 1.443250 | 1.441300 |
| j | E1-P1-M-024 | 0.075000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P1-VB-0106, P1-VB-0109
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_GEOMETRY_AND_LABEL
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "proposal_file": "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json", "face_ids": ["P1-VB-0106", "P1-VB-0109"], "width_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): LANDING_BEAM. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00664: dirección geométrica i→j, global XYZ = [0.0, 1.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-V-068 y E1-P1-M-024, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 35/43 — E1-P1-V-072

VIGA · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_beam_0186`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00665 | 10665 | 1213 | 521 | (61.391, -3.575, 7.92) | (62.757, -3.575, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | H'–H2 (H' +0.1061 m) | OUTBOARD <1 (1 -3.5749 m) |
| i | H1–H' (H1 +0.0750 m) | OUTBOARD <1 (1 -3.5749 m) |
| j | H'–H2 (H' +0.7893 m) | OUTBOARD <1 (1 -3.5749 m) |

### COORDENADAS GLOBALES (m)

- center: 62.074150, -3.574900, 7.420000 m.
- i: 61.391000, -3.574900, 7.420000 m.
- j: 62.757300, -3.574900, 7.420000 m.
- z_bottom: 6.920000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-016: distancia entre ejes XY 0.0000 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 1.0 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: LANDING_BEAM En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_RESIDUAL_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X H'–H2 (H' +0.1061 m) / Y OUTBOARD <1 (1 -3.5749 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-305** — Elevaciones: localizar el eje H' y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-305.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-V-072 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-016: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-013 | 5.316033 | 4.771027 | 0.000000 |
| nearest_wall | E1-P1-M-016 | 0.000000 | 0.000000 | 0.000000 |
| below | E1-S1-V-079 | 13.460574 | 13.293461 | 2.960000 |
| above | E1-P2-V-089 | 3.756300 | 3.381300 | 3.160000 |

- Encuentros del candidato: E1-P1-M-016, E1-P1-V-068.
- Vigas con encuentro candidato: E1-P1-V-068.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-016 | 1.366300 | 1.366300 |
| j | E1-P1-M-016 | 0.000000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P1-VB-0110, P1-VB-0111
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_GEOMETRY_AND_LABEL
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_RESIDUAL_LABEL_WIDTH", "proposal_file": "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json", "face_ids": ["P1-VB-0110", "P1-VB-0111"], "width_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): LANDING_BEAM. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00665: dirección geométrica i→j, global XYZ = [1.0, 0.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-V-072 y E1-P1-M-016, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 36/43 — E1-P1-V-098

VIGA · EDIFICIO_1 · P1 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_1_beam_0181`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00663 | 10663 | 520 | 547 | (66.391, -3.575, 7.92) | (72.736, -3.575, 7.92) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | I–IA (IA -0.5274 m) | OUTBOARD <1 (1 -3.5749 m) |
| i | H2–I (H2 +0.0750 m) | OUTBOARD <1 (1 -3.5749 m) |
| j | I'–IB (I' +0.2453 m) | OUTBOARD <1 (1 -3.5749 m) |

### COORDENADAS GLOBALES (m)

- center: 69.563650, -3.574900, 7.295000 m.
- i: 66.391000, -3.574900, 7.295000 m.
- j: 72.736300, -3.574900, 7.295000 m.
- z_bottom: 6.670000 m.
- z_top: 7.920000 m.

### NIVEL Y ELEVACIÓN

Nivel P1: Z modelo **7.92 m**; elevación fuente **-0.05 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-012 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P1-M-020: distancia entre ejes XY 0.1061 m, separación entre huellas 0.0000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-101.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-012, 7 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.15 m; altura visible 1.25 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: LANDING_BEAM En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-101** — Planta fuente del elemento P1. Buscar X I–IA (IA -0.5274 m) / Y OUTBOARD <1 (1 -3.5749 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-101.dxf`.
- **2017_67-310** — Elevaciones: localizar el eje IA y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-310.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P1-V-098 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P1-M-020: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P1-C-024 | 3.612537 | 3.187537 | 0.000000 |
| nearest_wall | E1-P1-M-020 | 0.106066 | 0.000000 | 0.000000 |
| below | E1-S1-V-079 | 18.198545 | 18.033749 | 2.710000 |
| above | E1-P2-V-093 | 3.756300 | 3.381300 | 3.160000 |

- Encuentros del candidato: E1-P1-M-016, E1-P1-M-020, E1-P1-M-037.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E1-P1-M-016, E1-P1-M-020, E1-P1-M-024, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098.
- Paneles visuales del mismo piso: E1-P1-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P1-M-020 | 0.106066 | 0.075000 |
| j | E1-P1-M-037 | 0.150000 | 0.000000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.
- **CACERES:** Sin match registrado. Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-101.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P1-VB-0105, P1-VB-0107
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_GEOMETRY_AND_LABEL
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "proposal_file": "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json", "face_ids": ["P1-VB-0105", "P1-VB-0107"], "width_m": 0.15}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): LANDING_BEAM. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00663: dirección geométrica i→j, global XYZ = [1.0, 0.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E1-P1-V-098 y E1-P1-M-020, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 37/43 — E1-P2-V-055

VIGA · EDIFICIO_1 · P2 · Prioridad B · STAIR_STRUCTURE

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_2_beam_0289`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00729 | 10729 | 1330 | 1328 | (47.191, 18.791, 11.88) | (52.191, 18.791, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ga–H (Ga +0.7499 m) | OUTBOARD >3 (3 +2.6414 m) |
| i | F–G (G -0.3001 m) | OUTBOARD >3 (3 +2.6414 m) |
| j | Ga–H (Ga +3.2499 m) | OUTBOARD >3 (3 +2.6414 m) |

### COORDENADAS GLOBALES (m)

- center: 49.690900, 18.791400, 11.655000 m.
- i: 47.190900, 18.791400, 11.655000 m.
- j: 52.190900, 18.791400, 11.655000 m.
- z_bottom: 11.430000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-022 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-005: distancia entre ejes XY 13.8571 m, separación entre huellas 13.6877 m y separación vertical 0.0000 m. Pertenece al contexto de escalera B; su apoyo y alcance FE siguen sin aprobar.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-022, 2 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 0.45 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS el detalle de apoyo exterior ni su vínculo resistente con el edificio principal; SECONDARY_STRUCTURE_EXPECTED no equivale a una exclusión FE aprobada.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: LANDING_BEAM En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: MEDIA para contexto escalera; BAJA para vínculo resistente.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Ga–H (Ga +0.7499 m) / Y OUTBOARD >3 (3 +2.6414 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-305** — Elevaciones: localizar el eje Ga y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-305.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-V-055 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-005: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-010 | 2.343209 | 1.843209 | 0.000000 |
| nearest_wall | E1-P2-M-005 | 13.857052 | 13.687687 | 0.000000 |
| below | E1-P1-V-034 | 2.209900 | 1.909900 | 3.510000 |
| above | E1-P3-V-052 | 0.000000 | 0.000000 | 3.160000 |

- Encuentros del candidato: E1-P2-V-075.
- Vigas con encuentro candidato: E1-P2-V-075.
- Componente compartido con: E1-P2-V-055, E1-P2-V-075.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P2-M-005 | 13.857052 | 13.740078 |
| j | E1-P2-M-005 | 18.621704 | 18.501074 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "E1_221", "start_xy_m": [47.47, 18.79], "end_xy_m": [57.47, 18.79], "length_m": 10.0, "width_m": 0.6, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.0014, "angle_delta_deg": 0.0, "overlap_m": 4.7209, "overlap_ratio": 0.9442, "length_delta_m": 5.0, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-245", "start_xy_m": [47.49, 18.79], "end_xy_m": [52.49, 18.79], "length_m": 5.0, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.0014, "angle_delta_deg": 0.0, "overlap_m": 4.7009, "overlap_ratio": 0.9402, "length_delta_m": 0.0, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P2-VB-0102, P2-VB-0103
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_GEOMETRY_AND_LABEL
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "proposal_file": "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json", "face_ids": ["P2-VB-0102", "P2-VB-0103"], "width_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): LANDING_BEAM. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00729: dirección geométrica i→j, global XYZ = [1.0, 0.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿Qué detalle muestra el apoyo real de E1-P2-V-055 en escalera B y su conexión o independencia respecto del edificio?

## 38/43 — E1-P2-V-075

VIGA · EDIFICIO_1 · P2 · Prioridad B · STAIR_STRUCTURE

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL_2_beam_0287`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00728 | 10728 | 1328 | 1329 | (52.191, 18.791, 11.88) | (57.141, 18.791, 11.88) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | Ga–H (H -2.8251 m) | OUTBOARD >3 (3 +2.6414 m) |
| i | Ga–H (Ga +3.2499 m) | OUTBOARD >3 (3 +2.6414 m) |
| j | Ga–H (H -0.3501 m) | OUTBOARD >3 (3 +2.6414 m) |

### COORDENADAS GLOBALES (m)

- center: 54.665900, 18.791400, 11.655000 m.
- i: 52.190900, 18.791400, 11.655000 m.
- j: 57.140900, 18.791400, 11.655000 m.
- z_bottom: 11.430000 m.
- z_top: 11.880000 m.

### NIVEL Y ELEVACIÓN

Nivel P2: Z modelo **11.88 m**; elevación fuente **+3.91 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-022 sin camino de conectividad a los apoyos de fundación. Respecto de E1-P2-M-005: distancia entre ejes XY 18.6217 m, separación entre huellas 18.4622 m y separación vertical 0.0000 m. Pertenece al contexto de escalera B; su apoyo y alcance FE siguen sin aprobar.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2017_67-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-022, 2 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.3 m; altura visible 0.45 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.
- NO SABEMOS el detalle de apoyo exterior ni su vínculo resistente con el edificio principal; SECONDARY_STRUCTURE_EXPECTED no equivale a una exclusión FE aprobada.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: LANDING_BEAM En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: MEDIA para contexto escalera; BAJA para vínculo resistente.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2017_67-102** — Planta fuente del elemento P2. Buscar X Ga–H (H -2.8251 m) / Y OUTBOARD >3 (3 +2.6414 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-102.dxf`.
- **2017_67-308** — Elevaciones: localizar el eje H y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje. Archivo: `recursos/planos/dxf_full/2017_67/2017_67-308.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E1-P2-V-075 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E1-P2-M-005: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E1-P2-C-015 | 2.484645 | 1.959876 | 0.000000 |
| nearest_wall | E1-P2-M-005 | 18.621704 | 18.462199 | 0.000000 |
| below | E1-P1-V-053 | 2.641400 | 2.191400 | 3.510000 |
| above | E1-P3-V-074 | 0.350000 | 0.050000 | 3.160000 |

- Encuentros del candidato: E1-P2-V-055.
- Vigas con encuentro candidato: E1-P2-V-055.
- Componente compartido con: E1-P2-V-055, E1-P2-V-075.
- Paneles visuales del mismo piso: E1-P2-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E1-P2-M-005 | 18.621704 | 18.501074 |
| j | E1-P2-M-005 | 23.435505 | 23.313242 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "E1_221", "start_xy_m": [47.47, 18.79], "end_xy_m": [57.47, 18.79], "length_m": 10.0, "width_m": 0.6, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.0014, "angle_delta_deg": 0.0, "overlap_m": 4.95, "overlap_ratio": 1.0, "length_delta_m": 5.05, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-246", "start_xy_m": [52.49, 18.79], "end_xy_m": [57.49, 18.79], "length_m": 5.0, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.0014, "angle_delta_deg": 0.0, "overlap_m": 4.6509, "overlap_ratio": 0.9396, "length_delta_m": 0.05, "strong": true}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2017_67-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P2-VB-0098, P2-VB-0101
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_GEOMETRY_AND_LABEL
- material_source: 2017_67-100.dxf / MTEXT 1E116 / Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "proposal_file": "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json", "face_ids": ["P2-VB-0098", "P2-VB-0101"], "width_m": 0.3}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): LANDING_BEAM. Alcance FE: SECONDARY_STRUCTURE_EXPECTED.

### EJES LOCALES

- POST-A-00728: dirección geométrica i→j, global XYZ = [1.0, 0.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿Qué detalle muestra el apoyo real de E1-P2-V-075 en escalera B y su conexión o independencia respecto del edificio?

## 39/43 — E2-P4-V-004

VIGA · EDIFICIO_2 · P4 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL2_4_beam_0461`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00503 | 10503 | 983 | 980 | (-3.548, 4.416, 19.8) | (-3.548, 6.801, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -3.2916 m) |
| i | OUTBOARD <A (A -3.5480 m) | 1–2 (1 +4.4157 m) |
| j | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -2.0989 m) |

### COORDENADAS GLOBALES (m)

- center: -3.548000, 5.608400, 19.400000 m.
- i: -3.548000, 4.415700, 19.400000 m.
- j: -3.548000, 6.801100, 19.400000 m.
- z_bottom: 19.000000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-020 sin camino de conectividad a los apoyos de fundación. Respecto de E2-P4-M-002: distancia entre ejes XY 2.5919 m, separación entre huellas 2.5900 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2024_22-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-020, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.4 m; altura visible 0.8 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado. En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2024_22-102** — Planta fuente del elemento P4. Buscar X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -3.2916 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-102.dxf`.
- **2024_22-303** — ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-303.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E2-P4-V-004 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E2-P4-M-002: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E2-P4-C-001 | 4.124398 | 3.472890 | 0.000000 |
| nearest_wall | E2-P4-M-002 | 2.591930 | 2.590000 | 0.000000 |
| below | E2-P3-V-002 | 0.000000 | 0.000000 | 3.160000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E2-P4-V-005.
- Vigas con encuentro candidato: E2-P4-V-005.
- Componente compartido con: E2-P4-V-004, E2-P4-V-005, E2-P4-V-006.
- Paneles visuales del mismo piso: E2-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E2-P4-M-002 | 2.591930 | 2.590000 |
| j | E2-P4-M-002 | 4.976405 | 4.975400 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "B3085_V40/80", "start_xy_m": [-3.745, 0.0], "end_xy_m": [-3.745, 16.15], "length_m": 16.15, "width_m": 0.4, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.197, "angle_delta_deg": 0.0, "overlap_m": 2.3854, "overlap_ratio": 1.0, "length_delta_m": 13.7646, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-603", "start_xy_m": [-3.75, 11.885], "end_xy_m": [-3.75, 4.265], "length_m": 7.62, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.202, "angle_delta_deg": 0.0, "overlap_m": 2.3854, "overlap_ratio": 1.0, "length_delta_m": 5.2346, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2024_22-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P4-E2-VB-0103, P4-E2-VB-0106
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_PLAN
- material_source: 2024_22-100.dxf / MTEXT 53994 / Main ED2 through cielo P4; excludes slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "audit_file": "entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json", "face_ids": ["P4-E2-VB-0103", "P4-E2-VB-0106"], "width_m": 0.4}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): NO ENCONTRADA. Alcance FE: NO SABEMOS.

### EJES LOCALES

- POST-A-00503: dirección geométrica i→j, global XYZ = [0.0, 1.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E2-P4-V-004 y E2-P4-M-002, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 40/43 — E2-P4-V-005

VIGA · EDIFICIO_2 · P4 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL2_4_beam_0464`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00501 | 10501 | 980 | 978 | (-3.548, 6.801, 19.8) | (-3.548, 7.551, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -1.7239 m) |
| i | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -2.0989 m) |
| j | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -1.3489 m) |

### COORDENADAS GLOBALES (m)

- center: -3.548000, 7.176100, 19.400000 m.
- i: -3.548000, 6.801100, 19.400000 m.
- j: -3.548000, 7.551100, 19.400000 m.
- z_bottom: 19.000000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-020 sin camino de conectividad a los apoyos de fundación. Respecto de E2-P4-M-002: distancia entre ejes XY 4.9764 m, separación entre huellas 4.9754 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2024_22-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-020, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.4 m; altura visible 0.8 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado. En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2024_22-102** — Planta fuente del elemento P4. Buscar X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -1.7239 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-102.dxf`.
- **2024_22-303** — ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-303.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E2-P4-V-005 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E2-P4-M-002: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E2-P4-C-001 | 3.797869 | 3.162138 | 0.000000 |
| nearest_wall | E2-P4-M-002 | 4.976405 | 4.975400 | 0.000000 |
| below | E2-P3-V-002 | 0.000000 | 0.000000 | 3.160000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E2-P4-V-004, E2-P4-V-006.
- Vigas con encuentro candidato: E2-P4-V-004, E2-P4-V-006.
- Componente compartido con: E2-P4-V-004, E2-P4-V-005, E2-P4-V-006.
- Paneles visuales del mismo piso: E2-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E2-P4-M-002 | 4.976405 | 4.975400 |
| j | E2-P4-M-002 | 5.726273 | 5.725400 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "B3085_V40/80", "start_xy_m": [-3.745, 0.0], "end_xy_m": [-3.745, 16.15], "length_m": 16.15, "width_m": 0.4, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.197, "angle_delta_deg": 0.0, "overlap_m": 0.75, "overlap_ratio": 1.0, "length_delta_m": 15.4, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-603", "start_xy_m": [-3.75, 11.885], "end_xy_m": [-3.75, 4.265], "length_m": 7.62, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.202, "angle_delta_deg": 0.0, "overlap_m": 0.75, "overlap_ratio": 1.0, "length_delta_m": 6.87, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2024_22-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P4-E2-VB-0101, P4-E2-VB-0106
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_PLAN
- material_source: 2024_22-100.dxf / MTEXT 53994 / Main ED2 through cielo P4; excludes slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "audit_file": "entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json", "face_ids": ["P4-E2-VB-0101", "P4-E2-VB-0106"], "width_m": 0.4}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): NO ENCONTRADA. Alcance FE: NO SABEMOS.

### EJES LOCALES

- POST-A-00501: dirección geométrica i→j, global XYZ = [0.0, 1.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E2-P4-V-005 y E2-P4-M-002, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 41/43 — E2-P4-V-006

VIGA · EDIFICIO_2 · P4 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL2_4_beam_0459`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00500 | 10500 | 978 | 979 | (-3.548, 7.551, 19.8) | (-3.548, 8.351, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -0.9489 m) |
| i | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -1.3489 m) |
| j | OUTBOARD <A (A -3.5480 m) | 1–2 (2 -0.5489 m) |

### COORDENADAS GLOBALES (m)

- center: -3.548000, 7.951100, 19.400000 m.
- i: -3.548000, 7.551100, 19.400000 m.
- j: -3.548000, 8.351100, 19.400000 m.
- z_bottom: 19.000000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-020 sin camino de conectividad a los apoyos de fundación. Respecto de E2-P4-M-002: distancia entre ejes XY 5.7263 m, separación entre huellas 5.7254 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2024_22-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-020, 3 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.4 m; altura visible 0.8 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado. En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2024_22-102** — Planta fuente del elemento P4. Buscar X OUTBOARD <A (A -3.5480 m) / Y 1–2 (2 -0.9489 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-102.dxf`.
- **2024_22-303** — ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-303.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E2-P4-V-006 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E2-P4-M-002: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E2-P4-C-001 | 3.592283 | 3.006627 | 0.000000 |
| nearest_wall | E2-P4-M-002 | 5.726273 | 5.725400 | 0.000000 |
| below | E2-P3-V-002 | 0.000000 | 0.000000 | 3.160000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: E2-P4-V-005.
- Vigas con encuentro candidato: E2-P4-V-005.
- Componente compartido con: E2-P4-V-004, E2-P4-V-005, E2-P4-V-006.
- Paneles visuales del mismo piso: E2-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E2-P4-M-002 | 5.726273 | 5.725400 |
| j | E2-P4-M-003 | 5.975437 | 5.974600 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "B3085_V40/80", "start_xy_m": [-3.745, 0.0], "end_xy_m": [-3.745, 16.15], "length_m": 16.15, "width_m": 0.4, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.197, "angle_delta_deg": 0.0, "overlap_m": 0.8, "overlap_ratio": 1.0, "length_delta_m": 15.35, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-603", "start_xy_m": [-3.75, 11.885], "end_xy_m": [-3.75, 4.265], "length_m": 7.62, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.202, "angle_delta_deg": 0.0, "overlap_m": 0.8, "overlap_ratio": 1.0, "length_delta_m": 6.82, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2024_22-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P4-E2-VB-0101, P4-E2-VB-0104
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_PLAN
- material_source: 2024_22-100.dxf / MTEXT 53994 / Main ED2 through cielo P4; excludes slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "audit_file": "entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json", "face_ids": ["P4-E2-VB-0101", "P4-E2-VB-0104"], "width_m": 0.4}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): NO ENCONTRADA. Alcance FE: NO SABEMOS.

### EJES LOCALES

- POST-A-00500: dirección geométrica i→j, global XYZ = [0.0, 1.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E2-P4-V-006 y E2-P4-M-002, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 42/43 — E2-P4-V-007

VIGA · EDIFICIO_2 · P4 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL2_4_beam_0460`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00502 | 10502 | 981 | 982 | (-3.548, 9.251, 19.8) | (-3.548, 11.736, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | OUTBOARD <A (A -3.5480 m) | 2–3 (2 +1.5932 m) |
| i | OUTBOARD <A (A -3.5480 m) | 2–3 (2 +0.3507 m) |
| j | OUTBOARD <A (A -3.5480 m) | 2–3 (2 +2.8357 m) |

### COORDENADAS GLOBALES (m)

- center: -3.548000, 10.493200, 19.400000 m.
- i: -3.548000, 9.250700, 19.400000 m.
- j: -3.548000, 11.735700, 19.400000 m.
- z_bottom: 19.000000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-019 sin camino de conectividad a los apoyos de fundación. Respecto de E2-P4-M-003: distancia entre ejes XY 2.5919 m, separación entre huellas 2.5900 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2024_22-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-019, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.4 m; altura visible 0.8 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado. En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_LABEL_WIDTH Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2024_22-102** — Planta fuente del elemento P4. Buscar X OUTBOARD <A (A -3.5480 m) / Y 2–3 (2 +1.5932 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-102.dxf`.
- **2024_22-303** — ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-303.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E2-P4-V-007 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E2-P4-M-003: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E2-P4-C-001 | 3.567211 | 2.999996 | 0.000000 |
| nearest_wall | E2-P4-M-003 | 2.591930 | 2.590000 | 0.000000 |
| below | E2-P3-V-003 | 0.000000 | 0.000000 | 3.160000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E2-P4-V-007.
- Paneles visuales del mismo piso: E2-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E2-P4-M-003 | 5.075985 | 5.075000 |
| j | E2-P4-M-003 | 2.591930 | 2.590000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "B3085_V40/80", "start_xy_m": [-3.745, 0.0], "end_xy_m": [-3.745, 16.15], "length_m": 16.15, "width_m": 0.4, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.197, "angle_delta_deg": 0.0, "overlap_m": 2.485, "overlap_ratio": 1.0, "length_delta_m": 13.665, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-603", "start_xy_m": [-3.75, 11.885], "end_xy_m": [-3.75, 4.265], "length_m": 7.62, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.202, "angle_delta_deg": 0.0, "overlap_m": 2.485, "overlap_ratio": 1.0, "length_delta_m": 5.135, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2024_22-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P4-E2-VB-0102, P4-E2-VB-0105
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_PLAN
- material_source: 2024_22-100.dxf / MTEXT 53994 / Main ED2 through cielo P4; excludes slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_LABEL_WIDTH", "audit_file": "entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json", "face_ids": ["P4-E2-VB-0102", "P4-E2-VB-0105"], "width_m": 0.4}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): NO ENCONTRADA. Alcance FE: NO SABEMOS.

### EJES LOCALES

- POST-A-00502: dirección geométrica i→j, global XYZ = [0.0, 1.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E2-P4-V-007 y E2-P4-M-003, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## 43/43 — E2-P4-V-009

VIGA · EDIFICIO_2 · P4 · Prioridad B · UNRESOLVED_REAL

Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.

Geometry tag: `SOL2_4_beam_0507`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.

### IDENTIFICACIÓN CANDIDATA

| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |
|---|---|---|---|---|---|
| POST-A-00537 | 10537 | 1033 | 1034 | (-3.182, 15.851, 19.8) | (-2.282, 15.851, 19.8) |

### UBICACIÓN EN PLANO

| Punto | Ejes X / offset | Ejes Y / offset |
|---|---|---|
| center | OUTBOARD <A (A -2.7322 m) | 2–3 (3 -0.2993 m) |
| i | OUTBOARD <A (A -3.1822 m) | 2–3 (3 -0.2993 m) |
| j | OUTBOARD <A (A -2.2822 m) | 2–3 (3 -0.2993 m) |

### COORDENADAS GLOBALES (m)

- center: -2.732200, 15.850700, 19.350000 m.
- i: -3.182200, 15.850700, 19.350000 m.
- j: -2.282200, 15.850700, 19.350000 m.
- z_bottom: 18.900000 m.
- z_top: 19.800000 m.

### NIVEL Y ELEVACIÓN

Nivel P4: Z modelo **19.80 m**; elevación fuente **+11.83 m**.

niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente. El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.

### PROBLEMA

El candidato sitúa este viga en POST-FLOAT-021 sin camino de conectividad a los apoyos de fundación. Respecto de E2-P4-M-006: distancia entre ejes XY 0.4500 m, separación entre huellas 0.2000 m y separación vertical 0.0000 m.

### QUÉ SABEMOS

- HECHO: geometría actual desde 2024_22-102.dxf, layer RLE-VIGA_CONTOUR_CENTERLINE.
- HECHO: regeneración reproduce POST-FLOAT-021, 1 segmentos FE sin camino al sistema apoyado.
- HECHO: geometría y resultados no modificados. Ancho/espesor 0.2 m; altura visible 0.9 m (no confundir con sección resistente).

### QUÉ NO SABEMOS

- NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.
- NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.

### HIPÓTESIS — NO DECISIONES

- **H1: Falta representar un encuentro físico en el adaptador FE.** A favor: La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos. En contra: Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink. Confianza: BAJA.
- **H2: El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.** A favor: Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado. En contra: No se ha establecido un camino resistente completo ni una exclusión FE aprobada. Confianza: BAJA.
- **H3: El alcance, nivel o interpretación de una entidad CAD requiere revisión.** A favor: La desconexión continúa en la regeneración actual. En contra: CONFIRMED_SINGLE_CENTERLINE_BY_LABEL Confianza: BAJA; no borrar ni mover automáticamente.

### PLANOS RECOMENDADOS

- **2024_22-102** — Planta fuente del elemento P4. Buscar X OUTBOARD <A (A -2.7322 m) / Y 2–3 (3 -0.2993 m); revisar las entidades y la correspondencia cielo/piso, no solo el título. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-102.dxf`.
- **2024_22-303** — ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard. Archivo: `recursos/planos/dxf_full/2024_22/2024_22-303.dxf`.
- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.

### QUÉ BUSCAR MANUALMENTE

- Localizar E2-P4-V-009 por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).
- Comparar con E2-P4-M-006: verificar contacto de caras, nivel de arranque y continuidad del hormigón.
- Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.
- Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.

### VECINOS — NO RECEPTORES AUTOMÁTICOS

| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |
|---|---|---|---|---|
| nearest_column | E2-P4-C-001 | 7.315770 | 6.781705 | 0.000000 |
| nearest_wall | E2-P4-M-006 | 0.450000 | 0.200000 | 0.000000 |
| below | E2-P3-V-008 | 0.487452 | 0.384200 | 3.060000 |
| above | NO ENCONTRADA | — | — | — |

- Encuentros del candidato: ninguno registrado.
- Vigas con encuentro candidato: ninguna registrada.
- Componente compartido con: E2-P4-V-009.
- Paneles visuales del mismo piso: E2-P4-D-001. NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.

### DISTANCIAS DE EXTREMOS (m)

| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |
|---|---|---|---|
| i | E2-P4-M-006 | 0.450000 | 0.300000 |
| j | E2-P4-M-006 | 0.450000 | 0.300000 |

Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.

### PISTAS EXTERNAS

- **SANTIAGO:** {"id": "B3089_V60/80", "start_xy_m": [-3.745, 16.15], "end_xy_m": [7.505, 16.15], "length_m": 11.25, "width_m": 0.6, "height_m": 0.8, "match": {"perpendicular_distance_m": 0.2993, "angle_delta_deg": 0.0, "overlap_m": 0.9, "overlap_ratio": 1.0, "length_delta_m": 10.35, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.
- **CACERES:** {"id": "C-B-315", "start_xy_m": [-3.75, 16.15], "end_xy_m": [-1.9, 16.15], "length_m": 1.85, "width_m": null, "height_m": null, "match": {"perpendicular_distance_m": 0.2993, "angle_delta_deg": 0.0, "overlap_m": 0.9, "overlap_ratio": 1.0, "length_delta_m": 0.95, "strong": false}}. Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.

### EVIDENCIA PRIMARIA Y AUDITORÍAS

- source_dxf: 2024_22-102.dxf
- source_layer: RLE-VIGA_CONTOUR_CENTERLINE
- sourceTags: P4-E2-VB-0151
- source_label: NO ENCONTRADA
- source_label_tag: NO ENCONTRADA
- section_source: CAD_CONTOUR_WIDTH+TEXT_LABEL
- section_confidence: CONFIRMED_FROM_PLAN
- material_source: 2024_22-100.dxf / MTEXT 53994 / Main ED2 through cielo P4; excludes slabs and radier
- CAD_handle: NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.
- joint_detail: NO ENCONTRADA inequívoca
- dimension_joint: NO ENCONTRADA inequívoca
- Auditoría geométrica previa: {"status": "CONFIRMED_SINGLE_CENTERLINE_BY_LABEL", "audit_file": "entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json", "face_ids": ["P4-E2-VB-0151"], "width_m": 0.2}
- Interpretación del contexto en auditoría previa (no nuevo detalle primario): NO ENCONTRADA. Alcance FE: NO SABEMOS.

### EJES LOCALES

- POST-A-00537: dirección geométrica i→j, global XYZ = [1.0, 0.0, 0.0]. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.

### IMPACTO POTENCIAL

Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.

### PREGUNTA PARA MATÍAS

¿La planta y el corte muestran una unión resistente entre E2-P4-V-009 y E2-P4-M-006, o un apoyo/transferencia diferente? Indica la llamada del detalle.

## Totales y límites

```json
{
  "total": 43,
  "priority": {
    "A": 20,
    "B": 23,
    "C": 0
  },
  "type": {
    "MURO": 31,
    "COLUMNA": 2,
    "VIGA": 10
  },
  "building": {
    "EDIFICIO_1": 38,
    "EDIFICIO_2": 5
  },
  "requires_plan": 43,
  "requires_cut": 43,
  "requires_joint_detail": 43,
  "previous_FE_ADAPTER_ERROR": 4,
  "physical_cause_unresolved": 43,
  "confirmed_real_structural_errors": 0
}
```

Planta/corte/detalle son necesidades de revisión no excluyentes. Los 4 candidatos de adaptador no equivalen a 4 problemas físicos resueltos. C = 0: no se reduce prioridad por apariencia secundaria. Los 43 tienen causa física por revisar; 0 errores estructurales reales confirmados por este expediente.
