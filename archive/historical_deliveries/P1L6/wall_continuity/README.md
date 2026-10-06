# CURRENT — núcleos de muros, columnas P4 y Viewer

Rama: `codex/p1l6-wall-continuity-correction`. Base: `ba889a7`.
Estado: **CURRENT_VERIFIED / PASS_WITH_EXPLICIT_NOTES**.

## Correcciones

- 30 muros recuperados desde sus IDs originales y pares de caras CAD.
- Cuatro muros ED1-S1 registrados contra ejes primarios: M-005, M-026,
  M-029 y M-049. El desplazamiento de aproximadamente −0,1813 m corrige
  el origen usado para estos núcleos, no desplaza el edificio entero.
- Tres conjuntos en C, cada uno formado por tres paños independientes,
  completos S1–P4. La tabla por piso está en `WALL_CONTINUITY_AFTER.md`.
- El muro largo ED2 permanece en X=27,727 m: el CAD no respalda invertirlo.
  Esta decisión sigue la aclaración del usuario únicamente para ese caso.
- E2-P4-C-004/C-007: sección 20×20→70×70 cm, reutilizada de P3.
  Centro XY, altura 3,96 m, orientación, material e IDs conservados.

La sección cuadrada nueva tiene A=0,49 m², Iy=Iz=0,02000833 m⁴,
J=0,03381408 m⁴ (aproximación rectangular del solver). Antes: A=0,04 m²,
Iy=Iz=0,00013333 m⁴, J=0,00022533 m⁴. OpenSees consume estas propiedades
recalculadas, no las de 20×20. Peso y capacidades se regeneran.

## Validación

`CURRENT_PIPELINE_QA.json`: identidad de geometría/FE/cargas/resultados/
capacidad/Unity, hashes, conservación y control manual de superposición PASS.
Muros duplicados=0; solapes de huella=0; componentes sin apoyo=0; NaN/Inf=0.
442 vigas, 143 columnas, 84 muros, 10 losas no-FE; 669 miembros físicos.
FE: 1170 nodos topológicos, 677 segmentos, 1240 restricciones, 44 apoyos.
OpenSees usa 1165 nodos y 673 segmentos tras excluir cuatro redundantes rígidos.
No se añadieron conectores para hacer coincidir artificialmente los resultados.
La base fija de S1 mantiene la idealización existente de laboratorio; no se
declara una nueva verificación detallada de cimentaciones.

OpenSees G/Q/EX/EY converge y pasa equilibrio (máximo residual relativo
5,08e−14). Desplazamientos y reacciones se documentan en el informe de antes/
después. Q total permanece 24,636594 MN; G cambia 80,184104→82,034949 MN
por el peso de los muros y las dos columnas corregidas.

## Unity

Proyecto: `entregas/P1L3/José/viewer_unity`; escena `Assets/Main.unity`.
Arranque: vigas/columnas/muros/nodos ON; losas y mapa de capacidad/falla OFF.
Los nodos corresponden a la capa `node` / Avanzado → Nodos geométricos:
son marcadores visuales existentes, no una modificación de topología.
Resultados incluye explicación G/Q/EX/EY/R y coeficientes adimensionales.

Compilación: PASS; consola sin errores tras corregir la captura de QA.
Persisten advertencias previas de APIs obsoletas y listas JSON anidadas.
Play real: `UNITY_RUNTIME_QA.json`, 76 controles PASS. Comprueba filtros
de pisos y edificios, selección de viga/columnas/muros nuevos, cinco casos,
ayuda de casos y recuperación exacta de colores tras activar/apagar D/C.
Las vistas se capturaron desde el framebuffer real de Unity, no son renders
sintéticos. El control se puede repetir en Play desde:
`MCOC → Validar núcleos CURRENT y capturar vistas`.

- `unity_Iso.png`: edificio actual completo.
- `unity_Planta.png`: tres C visibles en planta.
- `unity_Frente.png`: continuidad hasta P4.
- `unity_Lateral.png`: vista RIGHT / eje global X.
- `before_cores_*.png`: contraste anterior con snapshots externos normalizados.
- `after_cores_*.png`: planta corregida con IDs. Los externos no son fuente métrica.

## Límites que NO se ocultan

- 38 candidatos antiguos de muros siguen fuera del modelo; no se restauran
  por simple repetición o consenso externo.
- 85 miembros activos ED1-P4 conservan G35 como supuesto material de laboratorio,
  no como confirmación primaria nueva para ese piso.
- Armaduras, curvas P–M y D/C mantienen `ASSUMED_FOR_LAB`; no son diseño normativo.
- Seis registros de cargas puntuales siguen sin receptor y excluidos.
- Losas no-FE: MAT_UNKNOWN y espesor académico 0,15 m.
- Una C geométrica no equivale a una sección C monolítica en el FE de barras.
- ED2 M-009 inferior termina antes de P4 según las caras CAD auditadas;
  no se extrapola un muro adicional. Las otras 16 líneas son CONTINUOUS
  dentro de tolerancia 2 mm / espesor 1 mm.

## Regeneración y trazabilidad

Fuentes únicas: `entregas/P1L5/modelo_central/model_master.json`, `sections.json`,
`materials.json`, `loads.json`. Derivados de análisis en
`entregas/P1L5/analysis/results/current/`; contratos Unity en StreamingAssets.
No modificar Luis original, tags P1L2/P1L3/P1L4 ni benchmarks históricos.

Auditoría previa: `audit_wall_continuity.py` (solo repetir sobre la base indicada).
Preparación aislada: `prepare_core_candidate.py`; QA aislado existente:
`current_cleanup/validate_wall_candidate.py` y
`current_cleanup/validate_supported_wall_pipeline.py` con `--candidate-dir`.
Promoción y columnas: scripts separados de este directorio. No ejecutarlos
contra otra base sin revisar el manifiesto; son migraciones del checkpoint.

Verificación del estado final: `validate_corrected_cores.py` (entorno `.venv`).
Pipeline de análisis: build_current_loads → run_current_opensees →
build_current_capacity → export_current_to_unity (entorno `.venv-p1l5`).

## Commits por hito

| Hito | Commit |
|---|---|
| Auditoría de ejes, núcleos y columnas | `441d8e9` |
| Recuperar núcleos CAD / conservar lado correcto | `cdbf970` |
| Columnas P4 por continuidad con P3 | `43553a6` |
| Cargas y OpenSees CURRENT | `ee45ee8` |
| Capacidades y firmas con orientación | `91d3d22` |
| Defaults del Viewer | `41b90ea` |
| Ayuda de G/Q/EX/EY/R | `3dd4eac` |

El commit posterior de QA integra el informe, controles reproducibles y capturas.
