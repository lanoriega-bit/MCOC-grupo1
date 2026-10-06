#!/usr/bin/env python3
"""Publish exact endpoint-derived metadata without changing physical geometry/results."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
UNITY = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
FILES = (
    UNITY / "model_viewer.json",
    ROOT / "entregas/P1L2/unity_export/model_combined_viewer.json",
    ROOT / "entregas/P1L2/unity_export/model_1_audited_corrected.json",
)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_points(a, b) -> bool:
    return isinstance(a, list) and len(a) == 3 and all(abs(x - y) < 1e-8 for x, y in zip(a, b))


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    central = {e["element_id"]: e for e in master["elements"] + master["supports"]}
    sections = {e["section_id"]: e for e in read(CENTRAL / "sections.json")["sections"]}
    contract_path = UNITY / "current_dataset_contract.json"
    contract = read(contract_path)
    if contract.get("status") != "CURRENT_VERIFIED":
        raise ValueError("CURRENT contract not verified before metadata-only synchronization")
    if contract.get("geometry_version") != sha(CENTRAL / "model_master.json"):
        raise ValueError("Central geometry version differs from CURRENT contract")
    stats = {}
    outputs = {}
    for path in FILES:
        viewer = read(path)
        updated = 0
        for solid in viewer["solids"]:
            eid = solid.get("id")
            element = central.get(eid)
            if element is None:
                raise ValueError(f"Viewer ID not in central model: {eid}")
            if solid.get("section_id") != element["section_id"] or solid.get("material_id") != element["material_id"]:
                raise ValueError(f"Viewer property differs from central model: {eid}")
            geo = element["geometry"]
            if "start_m" not in geo:
                continue
            if not same_points(solid.get("start"), geo["start_m"]) or not same_points(solid.get("end"), geo["end_m"]):
                raise ValueError(f"Viewer endpoints differ from central model: {eid}")
            vec = [b - a for a, b in zip(geo["start_m"], geo["end_m"])]
            length = math.sqrt(sum(x * x for x in vec))
            if not math.isfinite(length) or length <= 0:
                raise ValueError(f"Invalid length: {eid}")
            if element["type"] == "wall":
                section_length = sections[element["section_id"]]["dimensions"].get("length_m")
                if not section_length or abs(section_length - length) > 0.02:
                    raise ValueError(f"Wall section/geometric length mismatch: {eid}")
            solid["length_m"] = round(length, 6)
            solid["direction_unit"] = [round(x / length, 9) for x in vec]
            solid["orientation_deg_xy"] = round(math.degrees(math.atan2(vec[1], vec[0])), 6)
            updated += 1
        # Preserve all existing geometry and results; only add endpoint-derived metadata.
        outputs[path] = viewer
        stats[path.relative_to(ROOT).as_posix()] = updated
    for path, viewer in outputs.items():
        if path == UNITY / "model_viewer.json":
            encoded = json.dumps(viewer, ensure_ascii=False, separators=(",", ":"))
        else:
            encoded = json.dumps(viewer, ensure_ascii=False, indent=2)
        path.write_text(encoded + "\n", encoding="utf-8")
    contract["geometry_stream_sha256"] = sha(UNITY / "model_viewer.json")
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_METADATA_ONLY", "updated_linear_solids": stats, "results_changed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
