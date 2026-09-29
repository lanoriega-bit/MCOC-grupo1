#!/usr/bin/env python3
"""Publish the central CURRENT geometry to derived viewer contracts.

Luis's original entregas/P1L2/unity_export/model_viewer.json is deliberately
read-only.  The combined/audited derivatives and Unity StreamingAssets receive
the CURRENT solids.  Analysis is fail-closed until a fresh OpenSees run rewrites
the CURRENT dataset contract.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENERATED = HERE / "generated" / "viewer_model_preview.json"
UNITY_STREAM = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
UNITY_MODEL = UNITY_STREAM / "model_viewer.json"
UNITY_CONTRACT = UNITY_STREAM / "current_dataset_contract.json"
COMBINED = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
ED1_AUDITED = ROOT / "entregas" / "P1L2" / "unity_export" / "model_1_audited_corrected.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict, compact: bool = False) -> None:
    if compact:
        path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_value(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def replace_solids(path: Path, solids: list[dict], label: str, compact: bool = False) -> None:
    model = read(path)
    model["solids"] = solids
    model["model"] = label
    model["central_sync"] = {
        "source": "entregas/P1L5/modelo_central/model_master.json",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "geometry_state": "P1L6_CURRENT_SLAB_POLYGONS",
        "results_state": "STALE_REANALYSIS_REQUIRED",
        "solid_count": len(solids),
    }
    write(path, model, compact=compact)


def main() -> None:
    preview = read(GENERATED)
    master = read(HERE / "model_master.json")
    solids = preview["solids"]
    if len(solids) != len(master["elements"]) + len(master["supports"]):
        raise AssertionError("Viewer derivative does not cover every CURRENT solid")

    replace_solids(UNITY_MODEL, solids, "POST_P1L5_CURRENT / P1L6 READINESS", compact=True)
    replace_solids(COMBINED, solids, "MODEL_COMBINED_CURRENT / P1L6 READINESS")
    ed1 = [row for row in solids if row.get("building") == "EDIFICIO_1"]
    replace_solids(ED1_AUDITED, ed1, "EDIFICIO_1_AUDITED_CURRENT / P1L6 READINESS")

    contract = read(UNITY_CONTRACT)
    contract.update({
        "geometry_version": sha_file(HERE / "model_master.json"),
        "fe_version": sha_value(master.get("fe_topology", {})),
        "analysis_version": "NONE_REANALYSIS_REQUIRED",
        "git_commit": "WORKTREE_P1L6_READINESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CURRENT_GEOMETRY_STALE_REANALYSIS_REQUIRED",
        "geometry_stream_sha256": sha_file(UNITY_MODEL),
        "analysis_available": False,
        "fe_approved": True,
        "loads_approved": False,
        "linear_verified": False,
        "payload_file": "",
        "payload_sha256": "",
        "source_geometry": "entregas/P1L5/modelo_central/model_master.json",
        "source_fe": "entregas/P1L5/modelo_central/model_master.json#/fe_topology",
        "result_state": "STALE_REANALYSIS_REQUIRED",
    })
    write(UNITY_CONTRACT, contract)
    print(json.dumps({
        "status": "PASS_STALE_FAIL_CLOSED",
        "unity_solids": len(solids),
        "ed1_solids": len(ed1),
        "slab_polygons": sum(row.get("kind") == "slab_polygon" for row in solids),
        "results_state": contract["result_state"],
        "luis_reference_modified": False,
    }, indent=2))


if __name__ == "__main__":
    main()
