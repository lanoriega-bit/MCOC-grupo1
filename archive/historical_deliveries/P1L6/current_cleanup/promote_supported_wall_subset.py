#!/usr/bin/env python3
"""Promote isolated supported walls, loads and FE; keep results fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
ANALYSIS_GENERATED = ROOT / "entregas/P1L5/analysis/generated"
HERE = Path(__file__).resolve().parent
DEFER_IDS = {
    "E1-P1-M-002", "E1-P1-M-026", "E1-P2-M-003",
    "E1-P2-M-005", "E1-P3-M-003", "E1-P3-M-005",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", required=True, type=Path)
    args = parser.parse_args()
    folder = args.candidate_dir.resolve()
    qa = read(folder / "candidate_qa.json")
    analysis = read(folder / "results/current/manifest.json")
    manifest = read(folder / "restoration_manifest.json")
    candidate = read(folder / "model_master.json")
    live = read(CENTRAL / "model_master.json")
    if (manifest["status"] != "SUPPORTED_SUBSET_NOT_PROMOTED" or
            set(manifest["deferred_ids"]) != DEFER_IDS or
            qa["status"] != "PASS" or qa["floating_components"] or
            qa["fe_components_without_support"] or analysis["status"] != "PASS"):
        raise SystemExit("Supported subset has not passed isolated FE/OpenSees checks")
    old = {r["element_id"]: r for r in live["elements"]}
    new = {r["element_id"]: r for r in candidate["elements"]}
    if set(old) - set(new) != DEFER_IDS or set(new) - set(old):
        raise SystemExit("Candidate changes unexpected physical IDs")
    if any(old[eid]["geometry"] != row["geometry"] or old[eid]["section_id"] != row["section_id"]
           or old[eid]["material_id"] != row["material_id"] for eid, row in new.items()):
        raise SystemExit("Candidate changes an existing element property")
    luis = ROOT / "entregas/P1L2/unity_export/model_viewer.json"
    luis_sha = hashlib.sha256(luis.read_bytes()).hexdigest()
    candidate["sources"]["current_contract"].update({"status": "STALE_REANALYSIS_REQUIRED",
                                                       "analysis_version": "NONE_REANALYSIS_REQUIRED"})
    write(CENTRAL / "model_master.json", candidate)
    write(CENTRAL / "sections.json", read(folder / "sections.json"))
    write(CENTRAL / "loads.json", read(folder / "loads.json"))
    for name in ("current_tributary_loads.json", "current_tributary_panels.json", "current_loads_by_element.json"):
        write(ANALYSIS_GENERATED / name, read(folder / "generated" / name))
    for name in ("validate_central_model.py", "build_central_derivatives.py", "sync_current_model_to_viewers.py"):
        subprocess.run([sys.executable, str(CENTRAL / name)], cwd=ROOT, check=True)
    if hashlib.sha256(luis.read_bytes()).hexdigest() != luis_sha:
        raise RuntimeError("Luis reference changed")
    prior = read(HERE / "promoted_walls_manifest.json")
    prior.update({"status": "PARTIAL_PROMOTION_24_ACTIVE_6_DEFERRED_RESULTS_STALE",
                  "deferred_after_support_graph_qa": sorted(DEFER_IDS),
                  "active_restored_wall_count": 24,
                  "model_master_sha256": hashlib.sha256((CENTRAL / "model_master.json").read_bytes()).hexdigest(),
                  "loads_rebuilt": True, "opensees_executed": False, "unity_results_current": False})
    write(HERE / "promoted_walls_manifest.json", prior)
    print(json.dumps({"status": prior["status"], "active_walls": 54,
                      "deferred": sorted(DEFER_IDS), "openSees_candidate_passed": True,
                      "unity_results_current": False}, indent=2))


if __name__ == "__main__":
    main()
