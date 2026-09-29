#!/usr/bin/env python3
"""Machine-readable validation for the P1L6 starting baseline."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
STREAM = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
OUT = Path(__file__).resolve().parent / "P1L6_READINESS_QA.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value) -> bool:
    if isinstance(value, dict): return all(finite(item) for item in value.values())
    if isinstance(value, list): return all(finite(item) for item in value)
    return not isinstance(value, float) or math.isfinite(value)


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    loads = read(CENTRAL / "loads.json")
    contract = read(STREAM / "current_dataset_contract.json")
    capacity = read(STREAM / "p1l6_current_capacity.json")
    ar = read(Path(__file__).resolve().parent / "current_ar_elements.json")
    manifest = read(ROOT / "entregas" / "P1L5" / "analysis" / "results" / "current" / "manifest.json")
    structural = [row for row in master["elements"] if row["type"] in {"beam", "column", "wall"} and row.get("active")]
    slabs = [row for row in master["elements"] if row["type"] == "slab"]
    checks = {
        "central_counts": len(master["elements"]) == 625 and len(master["supports"]) == 33,
        "fe_counts": len(master["fe_topology"]["nodes"]) == 1100 and master["current_pre5_identity"]["fe_active_segments"] == 623,
        "supports_fixed_6dof": len(master["fe_topology"]["support_node_tags"]) == 33,
        "no_disconnected_components": master["current_pre5_identity"].get("fe_pending_elements", 0) in (0, None),
        "slab_polygons_015": len(slabs) == 10 and all(row["geometry"].get("kind") == "slab_polygon" and abs(row["geometry"].get("thickness_m", 0) - 0.15) < 1e-9 for row in slabs),
        "slab_holes_preserved": sum(row["geometry"].get("hole_count", 0) for row in slabs) == 18,
        "capacity_full_coverage": len(capacity["elements"]) == len(structural) == 615,
        "ar_identity_unique": len(ar["elements"]) == len({row["element_id"] for row in ar["elements"]}) == 658,
        "ar_results_and_capacity": ar["summary"]["with_fe_results"] == 615 and ar["summary"]["with_capacity"] == 615,
        "opensees_cases_pass": manifest["status"] == "PASS" and all(row["status"] == "PASS" for row in manifest["cases"].values()),
        "opensees_finite": finite(manifest),
        "linear_superposition": manifest["linear_superposition_compatible"] is True,
        "load_conservation_G": loads["current_load_application"]["conservation"]["G"]["status"] == "PASS",
        "load_conservation_Q": loads["current_load_application"]["conservation"]["Q"]["status"] == "PASS",
        "unity_geometry_hash": contract["geometry_stream_sha256"] == sha(STREAM / "model_viewer.json"),
        "unity_payload_hash": contract["payload_sha256"] == sha(STREAM / contract["payload_file"]),
        "unity_load_hash": contract["current_element_loads_sha256"] == sha(STREAM / contract["current_element_loads_file"]),
        "current_verified": contract["status"] == "CURRENT_VERIFIED" and contract["analysis_available"] is True,
    }
    output = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "solids": len(master["elements"]) + len(master["supports"]),
            "elements": len(master["elements"]), "supports": len(master["supports"]),
            "fe_nodes": len(master["fe_topology"]["nodes"]),
            "fe_segments": master["current_pre5_identity"]["fe_active_segments"],
            "constraints": len(master["fe_topology"]["constraints"]),
            "capacity_elements": len(capacity["elements"]), "ar_records": len(ar["elements"]),
        },
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__":
    main()
