# Losas CURRENT — checkpoint de saneamiento

Rama `codex/current-slab-reconstruction`, desde el visual aprobado `21aa110`.
Estado: **CHECKPOINT_FUNCTIONAL / REVIEW_REQUIRED_PHYSICAL_BOUNDARIES**.
No es una certificación de todos los perímetros físicos. `main` y entregas históricas intactos.

## Correcciones implementadas

- Exclusión explícita aprobada por el usuario: sector sur ED1-S1, **227,099392 m²**.
  Se retira del sólido físico y del catálogo activo: H04/H05, SC y PM.ADIC
  (cuatro entradas; dos paños). Historia recuperable en `APPROVED_CLEANUP.json`
  y en `geometry_review` del modelo central.
- Diez losas poligonales antes y después. Ninguna caja provisional activa.
  Retriangulación restringida, sin triángulos degenerados, conservando vacíos
  previos y componentes. Las cajas históricas se consultaron, no se copiaron.
- Se separa `geometry.physical_polygon` del contrato de paños de carga.
  Los contornos retenidos todavía tienen origen histórico en zonas de carga;
  almacenarlos por separado **no** los confirma contra planos.
- Franja lineal E2-P4: el generador recorría SC y PM.ADIC como dos superficies
  y permutaba sus intensidades. Ahora una franja equivalente de 3,119991 m²,
  Q=3059,665 N, con PM.ADIC emparejada. No se convierte en losa física.
- Export tributario con triángulos restringidos que respetan huecos y
  `receiver_ids` reales. `beam_id` histórico de este export identifica el paño,
  no un receptor individual; no debe usarse como crosswalk estructural.
- Panel Modelo controla categoría `slab`, no el piloto arquitectónico P4.
  El piloto histórico ya no se construye encima de las losas CURRENT.
  Losas blancas alpha 0,18, OFF al inicio. Interfaz/materiales estructurales preservados.

## Cobertura geométrica retenida

| Edificio | Piso | Área m² | Huecos retenidos | Componentes | Estado físico |
|---|---|---:|---:|---:|---|
| ED1 | S1 | 160,764 | 2 | 1 | Exclusión sur confirmada; resto REVIEW_REQUIRED |
| ED1 | P1 | 997,042 | 1 | 2 | REVIEW_REQUIRED, extensiones norte/sur |
| ED1 | P2 | 843,914 | 2 | 2 | REVIEW_REQUIRED, contorno/outboard |
| ED1 | P3 | 956,721 | 3 | 1 | REVIEW_REQUIRED, contorno/vacíos |
| ED1 | P4 | 934,561 | 0 | 2 | REVIEW_REQUIRED, núcleo y borde |
| ED2 | S1 | 557,894 | 1 | 1 | REVIEW_REQUIRED, cierre CAD/vacío |
| ED2 | P1 | 557,894 | 1 | 1 | REVIEW_REQUIRED, cierre CAD/vacío |
| ED2 | P2 | 557,894 | 1 | 1 | REVIEW_REQUIRED, cierre CAD/vacío |
| ED2 | P3 | 557,894 | 1 | 1 | REVIEW_REQUIRED, cierre CAD/vacío |
| ED2 | P4 | 535,620 | 6 | 1 | REVIEW_REQUIRED, seis vacíos de origen carga |

Fuente de cada piso, hash del DXF, RLE-LOSA, paños, hull estructural diagnóstico
y solapes: [auditoría posterior](after/SLAB_SOURCE_AUDIT.json).
Los huecos existentes se conservan, no se declaran automáticamente huecos CAD confirmados.
Hull convexo ≠ perímetro físico; no se recortan voladizos con ese criterio.

## Física regenerada

STALE antes de modificar; después cargas → G/Q/EX/EY → capacidad/D-C → export CURRENT.
G=80.517.133,308 N, Q=23.477.156,839 N. Antes G=82.034.948,587 N,
Q=24.636.593,938 N. La diferencia corresponde a exclusión S1 y franja duplicada;
no es calibración ETABS. LT1 Q: +5,610%; LT2 Q: +0,974% frente al benchmark.

- Equilibrio G/Q/EX/EY: PASS; máximo residual relativo 7,41e−14.
- 43 paños (antes 46); 48 componentes visuales (antes 51).
- Receptores huérfanos: 0; referencias reparadas por alias: 0, no se necesitaban.
- FE idéntico: 1170 nodos topológicos, 677 segmentos; 673 analizados,
  1165 nodos utilizados, 44 tags fijos. Ningún miembro estructural alterado.
- 669 registros de capacidad actualizados. Seis entradas puntuales unresolved
  excluidas explícitamente; los supuestos académicos de materiales/espesores continúan.
- QA numérico: [SLAB_CLEANUP_QA.json](SLAB_CLEANUP_QA.json).
- QA contratos: [CURRENT_PIPELINE_QA](../current_cleanup/CURRENT_PIPELINE_QA.md).

## Contraste externo, solo lectura

Santiago `394a437`: 169 paños rectangulares delimitados por vigas.
Cáceres `7aeadd4`: 656 polígonos manuales. Se reutilizan las transformaciones
auditadas únicamente para comparación; agrupación por edificio externa requiere
prudencia en polígonos que abarcan alas. No se adopta geometría externa.
No certifican huecos ni cierres pendientes. [Informe](EXTERNAL_SLAB_CONTRAST.json).

## Pendientes que impiden cerrar completamente la reconstrucción física

1. Confirmar extensiones ED1-P1 norte (X≈61–73, Y≈16,5–28,7) y sur
   (X≈61–73, Y≈−10,7–−1,1): no hay respaldo inequívoco para recortarlas.
2. Cierres RLE-LOSA de S1/P1 y outboard ED1; no extrapolar perímetros entre pisos.
3. Clasificar vacíos físicos independientemente de huecos de carga: especialmente
   ED1-P4 sin vacío y ED2-P4 con seis. Los otros repos no resuelven esta contradicción.

## Reproducir

Usar Python del entorno `.venv-p1l5` para física/QA; `.venv` para auditoría con matplotlib.
Orden: `apply_confirmed_cleanup.py` (idempotente) → `build_current_loads.py` →
`validate_central_model.py` → `build_central_derivatives.py` →
`sync_current_model_to_viewers.py` → `run_current_opensees.py` →
`build_current_capacity.py` → `export_current_to_unity.py` → `main.py validar` →
`audit_slabs.py --after` → `validate_slab_cleanup.py`.
Los scripts físicos están en `entregas/P1L5/analysis/`; centrales en `modelo_central/`.

Unity: proyecto `entregas/P1L3/José/viewer_unity`, `Assets/Main.unity`, Play.
Modelo → Losas CURRENT. Filtros edificio/piso. `MCOC → Validar losas CURRENT`
genera diez capturas TOP y prueba selección, casos, gráficos, deformada y capacidad.
La revisión visual y sus límites se registran separadamente; compile no confirma geometría.
