"""Contrato de resultados de P1L3 Parte A.

Estructura: results/<run_id>/
  manifest.json    metadatos del run (run_id, formato, caso, config, resumen)
  nodes.json       nodos FE: tag -> {coord, floor, ux_m, uy_m, uz_m, rx_rad, ry_rad, rz_rad}
  elements.json    elementos FE: opensees_element_tag -> {element_id, analysis_id,
                   geometry_elementTag, type, floor, node_i, node_j, forces}
  reactions.json   reacciones en soportes: node_tag -> {Rx_N, Ry_N, Rz_N, Mx_Nm, My_Nm, Mz_Nm}

Convenciones:
  - unidades explicitas en cada archivo (m, N, Nm, rad);
  - el MISMO esquema sirve para G, Q, EX, EY y combinaciones (caso R);
  - los tags OpenSees se referencian vía el crosswalk de analysis_model.json.

No se versionan datos falsos como resultados reales: los runs reales solo
se generan por correr_caso/superposicion (ver opensees_mdl.py).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

FORMATO_RESULT = "P1L3_RESULT_v1"


def escribir_run(run_dir, run_id, caso, manifest_extra=None, nodes=None, elements=None, reactions=None):
    """Escribe results/<run_id>/{manifest,nodes,elements,reactions}.json."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "formato": FORMATO_RESULT,
        "run_id": run_id,
        "caso": caso,
        "creado_utc": datetime.now(timezone.utc).isoformat(),
        "unidades": {"length": "m", "force": "N", "moment": "N.m", "angle": "rad"},
    }
    if manifest_extra:
        manifest.update(manifest_extra)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "nodes.json").write_text(
        json.dumps(nodes or {}, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "elements.json").write_text(
        json.dumps(elements or {}, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "reactions.json").write_text(
        json.dumps(reactions or {}, indent=2, ensure_ascii=False), encoding="utf-8")
    return run_dir