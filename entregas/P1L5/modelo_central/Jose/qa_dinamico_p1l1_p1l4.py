#!/usr/bin/env python3
"""Portable retrospective QA for Jose's delivered P1L4 bundle.

This script intentionally never labels the bundle as CURRENT. Current geometry,
FE and load readiness are read from modelo_central and reported separately.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
CENTRAL = HERE.parent
ROOT = CENTRAL.parents[2]
UNITY = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
HISTORICAL = UNITY / "p1l4_jose"
CASES = ["G", "Q", "EX", "EY", "R"]


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def rows(data: dict, *keys: str) -> list:
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict) and isinstance(value.get("elements"), list):
            return value["elements"]
    return []


def main() -> None:
    master = load(CENTRAL / "model_master.json")
    forces = {}
    displacements = {}
    missing = []
    for case in CASES:
        force_path = HISTORICAL / "fuerzas_internas" / f"{case}.json"
        displacement_path = HISTORICAL / "desplazamientos" / f"{case}.json"
        if not force_path.exists() or not displacement_path.exists():
            missing.append(case)
            continue
        forces[case] = len(rows(load(force_path), "elements", "fuerzas_internas"))
        displacements[case] = len(rows(load(displacement_path), "nodes", "displacements", "elements"))

    support_path = HISTORICAL / "apoyos.json"
    support_count = len(rows(load(support_path), "apoyos", "supports", "elements")) if support_path.exists() else 0
    force_counts = set(forces.values())
    displacement_counts = set(displacements.values())
    historical_consistent = not missing and len(force_counts) == 1 and len(displacement_counts) == 1 and support_count > 0
    current = master["current_pre5_identity"]
    result = {
        "schema": "P1L1_P1L4_RETROSPECTIVE_QA_v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_status": "HISTORICAL_P1L4_DELIVERED",
        "rule": "This QA validates internal completeness of the delivered bundle only; it never certifies CURRENT.",
        "historical_bundle": {
            "path": HISTORICAL.relative_to(ROOT).as_posix(),
            "forces_per_case": forces,
            "displacement_nodes_per_case": displacements,
            "supports": support_count,
            "status": "PASS" if historical_consistent else "FAIL",
            "missing_cases": missing,
        },
        "current_central_model": {
            "solid_count": current["solid_count"],
            "fe_candidate_members": current["fe_candidate_members"],
            "pending_case": current["pending_case"]["element_id"],
            "results_status": "NONE_CURRENT",
        },
        "deliveries": {
            "P1L1": "STILL_VALID_METHOD_INDEPENDENT_BENCHMARK",
            "P1L2": "GEOMETRY_SUPERSEDED_BY_CURRENT_CENTRAL",
            "P1L3": "STILL_VALID_METHOD_SUPERSEDED_INPUT",
            "P1L4": "STILL_VALID_UI_HISTORICAL_DATASET",
        },
    }
    (HERE / "QA_DINAMICO_P1L1_P1L4.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# QA retrospectivo P1L1–P1L4 (José)", "",
        "Este control es portable y valida el bundle **histórico entregado**. No lo presenta como resultado CURRENT.", "",
        "| Dataset | Estado | Alcance |", "|---|---|---|",
        f"| P1L4 entregado | {'PASS' if historical_consistent else 'FAIL'} | {forces}; apoyos={support_count} |",
        f"| Modelo central actual | BLOCKED | {current['fe_candidate_members']} segmentos FE candidatos; resultados NONE_CURRENT |", "",
        "La geometría vigente debe reanalizarse antes de reemplazar los resultados históricos.",
    ]
    (HERE / "QA_DINAMICO_P1L1_P1L4.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"historical": result["historical_bundle"]["status"], "current_results": "NONE_CURRENT"}))


if __name__ == "__main__":
    main()
