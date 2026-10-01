#!/usr/bin/env python3
"""Persist exact endpoint-derived dimensions in the canonical central model."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / "entregas/P1L5/modelo_central/model_master.json"
CONTRACT = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/current_dataset_contract.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    master = read(MASTER)
    updated = {"linear": 0, "column": 0}
    new_fields = 0
    for element in master["elements"]:
        geo = element["geometry"]
        if element["type"] in {"beam", "wall"}:
            a, b = geo["start_m"], geo["end_m"]
            vector = [b[i] - a[i] for i in range(3)]
            length = math.sqrt(sum(component * component for component in vector))
            if not math.isfinite(length) or length <= 0:
                raise ValueError(f"Invalid linear length: {element['element_id']}")
            expected = {
                "length_m": round(length, 6),
                "direction_unit": [round(component / length, 9) for component in vector],
                "orientation_deg_xy": round(math.degrees(math.atan2(vector[1], vector[0])), 6),
            }
            for key, value in expected.items():
                if key in geo and geo[key] != value:
                    raise ValueError(f"Existing {key} conflicts with endpoints for {element['element_id']}")
                new_fields += int(key not in geo)
                geo[key] = value
            updated["linear"] += 1
        elif element["type"] == "column":
            height = float(geo["z_top_m"]) - float(geo["z_bottom_m"])
            if not math.isfinite(height) or height <= 0:
                raise ValueError(f"Invalid column height: {element['element_id']}")
            value = round(height, 6)
            if "height_m" in geo and geo["height_m"] != value:
                raise ValueError(f"Existing height conflicts with levels for {element['element_id']}")
            new_fields += int("height_m" not in geo)
            geo["height_m"] = value
            updated["column"] += 1
    if new_fields == 0:
        print(json.dumps({"status": "NOOP_METADATA_ALREADY_COMPLETE", **updated}, indent=2))
        return
    # A source-field change invalidates a byte-versioned CURRENT contract even
    # when all physical coordinates remain identical.
    contract = read(CONTRACT)
    contract.update({"status": "CURRENT_GEOMETRY_STALE_REANALYSIS_REQUIRED",
                     "result_state": "STALE_REANALYSIS_REQUIRED", "analysis_available": False,
                     "loads_approved": False, "linear_verified": False,
                     "analysis_version": "NONE_REANALYSIS_REQUIRED", "payload_file": "", "payload_sha256": ""})
    write(CONTRACT, contract)
    master["sources"]["current_contract"].update({"status": "STALE_REANALYSIS_REQUIRED",
                                                   "analysis_version": "NONE_REANALYSIS_REQUIRED"})
    master["geometry_revision_history"].append({
        "revision": "P1L6_EXPLICIT_DIMENSION_METADATA", "status": "PHYSICAL_GEOMETRY_UNCHANGED",
        "linear_members": updated["linear"], "columns": updated["column"],
        "derivation": "ENDPOINT_DISTANCE_AND_LEVEL_DIFFERENCE",
    })
    write(MASTER, master)
    print(json.dumps({"status": "METADATA_COMPLETED_RESULTS_STALE", "new_fields": new_fields, **updated}, indent=2))


if __name__ == "__main__":
    main()
