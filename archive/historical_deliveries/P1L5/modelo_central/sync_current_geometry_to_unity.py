#!/usr/bin/env python3
"""Propagate central geometry to Unity without touching analysis result payloads."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STREAM = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
MODEL = STREAM / "model_viewer.json"
CONTRACT = STREAM / "current_dataset_contract.json"
CHANGES = STREAM / "current_review_changes.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    master_path = HERE / "model_master.json"
    master = read(master_path)
    sections = {row["section_id"]: row for row in read(HERE / "sections.json")["sections"]}
    if "--from-head" in sys.argv:
        relative = MODEL.relative_to(ROOT).as_posix()
        viewer = json.loads(subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT, text=True, encoding="utf-8"))
    else:
        viewer = read(MODEL)
    current = {row["element_id"]: row for row in master["elements"] + master["supports"]}
    existing = {row.get("id", row.get("preserved_viewer_id")): row for row in viewer["solids"]}
    review = read(HERE / "generated" / "final_beam_geometry_review.json")
    changed_ids = {row["canonical"] for row in review["merge_groups"]} | {"E2-P4-V-013", "E1-P1-V-066", "E1-P1-V-067"}
    retired_ids = {element_id for row in review["merge_groups"] for element_id in row["absorbed"]} | {"E2-P4-V-009"}
    missing = sorted(changed_ids - set(existing))
    if missing:
        raise RuntimeError(f"Unity bridge is missing changed central IDs: {missing}")

    for element_id in changed_ids:
        central = current[element_id]
        solid = existing[element_id]
        geometry = central["geometry"]
        dims = sections[central["section_id"]]["dimensions"]
        solid["merged_from"] = central.get("merged_from", [])
        solid["coordinates"] = {
            "center": geometry["center_m"], "z_bottom_m": geometry.get("z_bottom_m"),
            "z_top_m": geometry.get("z_top_m"),
        }
        if "start_m" in geometry:
            solid["start"] = geometry["start_m"]
            solid["end"] = geometry["end_m"]
            solid["center"] = geometry["center_m"]
            solid["coordinates"].update({"start": geometry["start_m"], "end": geometry["end_m"]})
            solid["length_m"] = round(sum((a - b) ** 2 for a, b in zip(geometry["start_m"], geometry["end_m"])) ** 0.5, 6)
        if central["type"] == "beam":
            solid.update(width_m=dims["width_m"], height_m=dims["height_m"], section_width_m=dims["width_m"], section_height_m=dims["height_m"])
        solid["central_geometry_state"] = "FINAL_BEAM_GEOMETRY_REVIEW"
        if central.get("merge_history"):
            solid["post_p1l4_correction"] = central["merge_history"][-1]
        elif central.get("geometry_review"):
            solid["post_p1l4_correction"] = central["geometry_review"][-1]
    viewer["solids"] = [row for row in viewer["solids"] if row.get("id", row.get("preserved_viewer_id")) not in retired_ids]
    viewer["model"] = "POST_P1L4_CURRENT / FINAL_BEAM_GEOMETRY_REVIEW"
    viewer.setdefault("notes", []).append("Geometría sincronizada desde modelo_central; resultados P1L5 no recalculados en esta revisión.")
    viewer["central_sync"] = {
        "source": "entregas/P1L5/modelo_central/model_master.json",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "results_state": "P1L5_RESULTS_HISTORICAL_NOT_RECALCULATED",
        "solid_count": len(viewer["solids"]),
    }
    # Keep the production geometry stream compact; this avoids a multi-hundred-
    # thousand-line formatting-only diff in the Unity asset.
    MODEL.write_text(json.dumps(viewer, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    contract = read(CONTRACT)
    contract.update({
        "geometry_version": sha(master_path),
        "geometry_stream_sha256": sha(MODEL),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CURRENT_GEOMETRY_RESULTS_REQUIRE_REANALYSIS",
        "analysis_available": False,
        "result_state": "P1L5_RESULTS_HISTORICAL_NOT_RECALCULATED",
        "source_geometry": "entregas/P1L5/modelo_central/model_master.json",
    })
    write(CONTRACT, contract)

    changes = read(CHANGES)
    changes["rows"] = [row for row in changes.get("rows", []) if row.get("checkpoint") != "FINAL_BEAM_GEOMETRY_REVIEW"]
    for group in review["merge_groups"]:
        changes["rows"].append({
            "id": group["canonical"], "type": "MERGED", "reason": group["reason"],
            "source": group["source"], "historical_ids": group["historical_ids"],
            "checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
        })
    changes["rows"].extend([
        {"id": "E2-P4-V-009", "type": "REMOVED", "reason": "REMOVED_BY_STRUCTURAL_REVIEW", "source": "user structural review", "historical_ids": ["E2-P4-V-009"], "checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW"},
        {"id": "E2-P4-V-013", "type": "MOVED", "reason": "P3/P2 geometry projected to P4", "source": "E2-P3-V-008 + E2-P2-V-008", "historical_ids": ["E2-P4-V-013"], "checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW"},
        {"id": "E1-P1-V-066", "type": "RESIZED", "reason": "Endpoint extended to repeated-floor transverse beam footprint", "source": "P2/P3/P4 repetition", "historical_ids": ["E1-P1-V-066"], "checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW"},
        {"id": "E1-P1-V-067", "type": "RESIZED", "reason": "Endpoint extended to repeated-floor transverse beam footprint", "source": "P2/P3/P4 repetition", "historical_ids": ["E1-P1-V-067"], "checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW"},
    ])
    changes["geometry_version"] = sha(master_path)
    changes["current_results"] = "P1L5_RESULTS_HISTORICAL_NOT_RECALCULATED"
    changes["summary"] = {
        "geometry_solids": len(viewer["solids"]), "beams": sum(row["category"] == "beam" for row in viewer["solids"]),
        "merge_groups": len(review["merge_groups"]), "absorbed_ids": sum(len(row["absorbed"]) for row in review["merge_groups"]),
        "beams_removed": 1, "endpoints_reconnected": len(review["endpoint_reconnections"]),
        "FE_members": master["current_pre5_identity"]["fe_total_segments"],
        "FE_nodes": master["current_pre5_identity"]["fe_candidate_nodes"],
        "FE_pending": 0, "FE_components": 0, "analysis_run": False,
    }
    write(CHANGES, changes)
    print(json.dumps({"status": "PASS", "unity_solids": len(viewer["solids"]), "unity_beams": changes["summary"]["beams"], "results_changed": False}, indent=2))


if __name__ == "__main__":
    main()
