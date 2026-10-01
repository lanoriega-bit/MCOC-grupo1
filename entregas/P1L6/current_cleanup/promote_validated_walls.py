#!/usr/bin/env python3
"""Promote a QA-passing wall candidate and fail-close the Unity result gate.

Only the canonical central model and derived geometry are touched. Loads and
analysis results are not silently reused; separate rebuild steps must follow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
CONTRACT = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/current_dataset_contract.json"
LUIS_REFERENCE = ROOT / "entregas/P1L2/unity_export/model_viewer.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def signature(element: dict) -> tuple:
    return (element["element_id"], element["solidTag"], element["type"], element["building"],
            element["floor"], json.dumps(element["geometry"], sort_keys=True),
            element["section_id"], element["material_id"], element["active"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", required=True, type=Path)
    args = parser.parse_args()
    folder = args.candidate_dir.resolve()
    candidate = read(folder / "model_master.json")
    candidate_sections = read(folder / "sections.json")
    manifest = read(folder / "restoration_manifest.json")
    qa = read(folder / "candidate_qa.json")
    live = read(CENTRAL / "model_master.json")
    live_sections = read(CENTRAL / "sections.json")
    if manifest["status"] != "CANDIDATE_NOT_PROMOTED" or manifest.get("exploratory_ids"):
        raise SystemExit("Exploratory wall candidate cannot be promoted")
    if qa["status"] != "PASS" or qa["errors"] or qa["floating_components"] != 0:
        raise SystemExit("Wall candidate has not passed topology and model QA")
    restored_ids = {r["element_id"] for r in manifest["restored"]}
    if len(restored_ids) != manifest["restored_count"] or len(restored_ids) != 30:
        raise SystemExit("Wall manifest count/IDs changed unexpectedly")
    prior = {r["element_id"]: signature(r) for r in live["elements"]}
    after = {r["element_id"]: signature(r) for r in candidate["elements"]}
    if any(after.get(key) != value for key, value in prior.items()):
        raise SystemExit("Candidate changes an existing physical element")
    if set(after) - set(prior) != restored_ids:
        raise SystemExit("Added candidate IDs differ from manifest")
    before_sections = {r["section_id"]: r["dimensions"] for r in live_sections["sections"]}
    after_sections = {r["section_id"]: r["dimensions"] for r in candidate_sections["sections"]}
    if any(after_sections.get(key) != value for key, value in before_sections.items()):
        raise SystemExit("Candidate changes an existing section dimension")
    luis_before = hashlib.sha256(LUIS_REFERENCE.read_bytes()).hexdigest()

    # Disable historical CURRENT results *before* publishing new geometry.
    contract = read(CONTRACT)
    contract.update({"status": "CURRENT_GEOMETRY_STALE_REANALYSIS_REQUIRED",
                     "result_state": "STALE_REANALYSIS_REQUIRED", "analysis_available": False,
                     "loads_approved": False, "linear_verified": False,
                     "analysis_version": "NONE_REANALYSIS_REQUIRED", "payload_file": "", "payload_sha256": ""})
    write(CONTRACT, contract)
    write(CENTRAL / "model_master.json", candidate)
    write(CENTRAL / "sections.json", candidate_sections)
    python = sys.executable
    for script in ("validate_central_model.py", "build_central_derivatives.py", "sync_current_model_to_viewers.py"):
        subprocess.run([python, str(CENTRAL / script)], cwd=ROOT, check=True)
    if hashlib.sha256(LUIS_REFERENCE.read_bytes()).hexdigest() != luis_before:
        raise RuntimeError("Luis reference unexpectedly changed")
    model_sha = hashlib.sha256((CENTRAL / "model_master.json").read_bytes()).hexdigest()
    write(ROOT / "entregas/P1L6/current_cleanup/promoted_walls_manifest.json",
          {**manifest, "status": "PROMOTED_GEOMETRY_RESULTS_STALE", "model_master_sha256": model_sha,
           "loads_rebuilt": False, "opensees_executed": False, "unity_results_current": False})
    print(json.dumps({"status": "PROMOTED_GEOMETRY_RESULTS_STALE", "walls_restored": len(restored_ids),
                      "central_model_sha256": model_sha, "luis_reference_modified": False}, indent=2))


if __name__ == "__main__":
    main()
