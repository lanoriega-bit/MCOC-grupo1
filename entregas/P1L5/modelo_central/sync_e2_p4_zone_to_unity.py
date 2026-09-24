#!/usr/bin/env python3
"""Synchronize the reviewed E2-P4 zone to Unity geometry only."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STREAM = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
MODEL = STREAM / "model_viewer.json"
CONTRACT = STREAM / "current_dataset_contract.json"
CHANGES = STREAM / "current_review_changes.json"
CHANGED = {"E2-P4-V-024", "E2-P4-V-002", "E2-P4-V-004", "E2-P4-V-017", "E2-P4-V-020", "E2-P4-V-008", "E2-P4-V-042", "E2-P4-V-043"}
RETIRED = {"E2-P4-V-030", "E2-P4-V-035"}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    master_path = HERE / "model_master.json"
    master = read(master_path)
    central = {row["element_id"]: row for row in master["elements"]}
    viewer = read(MODEL)
    solids = {row.get("id", row.get("preserved_viewer_id")): row for row in viewer["solids"]}
    missing = CHANGED - set(solids)
    if missing:
        raise RuntimeError(f"Unity is missing changed IDs: {sorted(missing)}")
    for element_id in CHANGED:
        row, solid = central[element_id], solids[element_id]
        geometry = row["geometry"]
        solid["start"] = geometry["start_m"]
        solid["end"] = geometry["end_m"]
        solid["center"] = geometry["center_m"]
        solid["length_m"] = round(sum((a - b) ** 2 for a, b in zip(geometry["start_m"], geometry["end_m"])) ** 0.5, 6)
        solid["coordinates"] = {
            "start": geometry["start_m"], "end": geometry["end_m"], "center": geometry["center_m"],
            "z_bottom_m": geometry["z_bottom_m"], "z_top_m": geometry["z_top_m"],
        }
        solid["merged_from"] = row.get("merged_from", [])
        solid["central_geometry_state"] = "E2_P4_ZONE_COMPLETION"
        if row.get("merge_history") and row["merge_history"][-1].get("review_checkpoint") == "E2_P4_ZONE_COMPLETION":
            solid["post_p1l4_correction"] = row["merge_history"][-1]
        elif row.get("geometry_review"):
            solid["post_p1l4_correction"] = row["geometry_review"][-1]
    viewer["solids"] = [row for row in viewer["solids"] if row.get("id", row.get("preserved_viewer_id")) not in RETIRED]
    viewer["model"] = "POST_P1L4_CURRENT / E2_P4_ZONE_COMPLETION"
    viewer.setdefault("notes", []).append("E2-P4 zone geometry completed; loads and OpenSees results remain STALE / REANALYSIS REQUIRED.")
    viewer["central_sync"] = {
        "source": "entregas/P1L5/modelo_central/model_master.json", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "results_state": "STALE_REANALYSIS_REQUIRED", "solid_count": len(viewer["solids"]),
    }
    MODEL.write_text(json.dumps(viewer, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    contract = read(CONTRACT)
    contract.update({
        "geometry_version": sha(master_path), "geometry_stream_sha256": sha(MODEL),
        "timestamp": datetime.now(timezone.utc).isoformat(), "status": "BLOCKED_NOT_RUN",
        "analysis_available": False, "result_state": "STALE_REANALYSIS_REQUIRED",
    })
    write(CONTRACT, contract)

    report = read(HERE / "generated" / "e2_p4_zone_completion.json")
    changes = read(CHANGES)
    changes["rows"] = [row for row in changes.get("rows", []) if row.get("checkpoint") != "E2_P4_ZONE_COMPLETION"]
    changes["rows"].append({
        "id": "E2-P4-V-024", "type": "MERGED", "reason": "ARTIFICIAL_BEAM_FRAGMENTATION",
        "source": "P4 geometry + P3/P2 vertical comparison", "historical_ids": ["E2-P4-V-024", "E2-P4-V-030", "E2-P4-V-035"],
        "checkpoint": "E2_P4_ZONE_COMPLETION",
    })
    for element_id, row in report["endpoints"].items():
        changes["rows"].append({
            "id": element_id, "type": "RESIZED", "reason": "RECONNECT_HIGH_CONFIDENCE",
            "source": " + ".join(row["references"]), "historical_ids": [element_id], "checkpoint": "E2_P4_ZONE_COMPLETION",
        })
    changes["geometry_version"] = sha(master_path)
    changes["current_results"] = "STALE_REANALYSIS_REQUIRED"
    changes["summary"] = {
        "geometry_solids": len(viewer["solids"]), "beams": sum(row["category"] == "beam" for row in viewer["solids"]),
        "merge_groups": 1, "absorbed_ids": 2, "endpoints_reconnected": len(report["endpoints"]),
        "FE_members": master["current_pre5_identity"]["fe_total_segments"],
        "FE_nodes": master["current_pre5_identity"]["fe_candidate_nodes"],
        "FE_pending": 0, "FE_components": 0, "analysis_run": False,
    }
    write(CHANGES, changes)
    print(json.dumps({"status": "PASS", "unity_solids": len(viewer["solids"]), "unity_beams": changes["summary"]["beams"], "result_state": "STALE_REANALYSIS_REQUIRED"}, indent=2))


if __name__ == "__main__":
    main()
