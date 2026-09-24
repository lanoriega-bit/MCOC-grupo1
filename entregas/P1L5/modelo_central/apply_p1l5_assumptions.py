#!/usr/bin/env python3
"""Apply the explicitly authorised P1L5 academic assumptions.

This is an idempotent migration of the central source.  It does not touch any
historical delivery/tag and records every approximation in the affected row.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "model_master.json"
MATERIALS_PATH = HERE / "materials.json"
STRUCTURAL_TYPES = {"beam", "column", "wall"}
STOP_ID = "E2-P4-V-009"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    master = load(MASTER_PATH)
    materials = load(MATERIALS_PATH)
    now = datetime.now(timezone.utc).isoformat()

    valid_counts = Counter(
        row["material_id"]
        for row in master["elements"]
        if row["type"] in STRUCTURAL_TYPES and row["material_id"] != "MAT_UNKNOWN"
    )
    if not valid_counts:
        raise RuntimeError("No valid structural material exists for the authorised fallback.")
    fallback_id, fallback_count = valid_counts.most_common(1)[0]

    reassigned = []
    traced_fallbacks = []
    stopped = []
    for row in master["elements"]:
        if row["element_id"] == STOP_ID:
            row["active"] = False
            row["analysis_status"] = "STOP_EXCLUDED_P1L5"
            row.setdefault("p1l5_assumptions", {})["stop_exclusion"] = {
                "status": "AUTHORISED",
                "reason": "Isolated unresolved beam excluded so it does not block the academic CURRENT run.",
                "no_support_or_connection_invented": True,
                "authorised_utc": now,
            }
            for ref in row.get("analysis_refs", []):
                ref["status"] = "STOP_EXCLUDED_P1L5_NOT_ANALYSED"
            stopped.append(row["element_id"])

        if row["type"] in STRUCTURAL_TYPES and row["material_id"] == "MAT_UNKNOWN":
            row["material_id_previous"] = "MAT_UNKNOWN"
            row["material_id"] = fallback_id
            row.setdefault("p1l5_assumptions", {})["material_fallback"] = {
                "status": "APPROX_FALLBACK",
                "rule": "MOST_FREQUENT_VALID_STRUCTURAL_MATERIAL",
                "assigned_material_id": fallback_id,
                "valid_material_use_counts_before_assignment": dict(valid_counts),
                "authorised_utc": now,
            }
            reassigned.append(row["element_id"])

        if row.get("material_id_previous") == "MAT_UNKNOWN" and row["type"] in STRUCTURAL_TYPES:
            fallback = row.setdefault("p1l5_assumptions", {}).setdefault("material_fallback", {})
            fallback["status"] = "INFERRED_MATERIAL_FALLBACK"
            fallback["confirmed_by_plan"] = False
            fallback["reason"] = "Predominant compatible structural material; retained as an explicit academic inference."
            traced_fallbacks.append(row["element_id"])

    for material in materials["materials"]:
        if material["material_id"].startswith("MAT_G35_10_"):
            material["elastic"]["E_pa"] = {
                "value": 28_000_000_000.0,
                "unit": "Pa",
                "status": "APPROX_P1L5_AUTHORIZED",
                "source": "Academic P1L5 assumption authorised by the project owner for G35 concrete.",
            }
            material["elastic"]["nu"] = {
                "value": 0.2,
                "unit": "1",
                "status": "APPROX_P1L5_AUTHORIZED",
                "source": "Conventional linear-elastic concrete Poisson ratio adopted for P1L5.",
            }
            material["elastic"]["density_kg_m3"] = {
                "value": 2500.0,
                "unit": "kg/m3",
                "status": "APPROX_P1L5_AUTHORIZED",
                "source": "Conventional reinforced-concrete density adopted for P1L5 gravity/mass bookkeeping.",
            }

    topology = master["fe_topology"]
    topology["status"] = "APPROVED_FOR_P1L5_WITH_STOP_EXCLUSIONS"
    topology["run_policy"] = {
        "status": "APPROVED_ACADEMIC_EXPERIMENTAL",
        "active_only": True,
        "stop_element_ids": stopped,
        "no_invented_supports": True,
        "authorised_utc": now,
    }
    identity = master["current_pre5_identity"]
    identity["fe_total_segments"] = sum(
        len(row.get("analysis_refs", [])) for row in master["elements"] if row["type"] in STRUCTURAL_TYPES
    )
    identity["fe_active_segments"] = sum(
        len(row.get("analysis_refs", []))
        for row in master["elements"]
        if row["type"] in STRUCTURAL_TYPES and row["active"]
    )
    if isinstance(identity.get("pending_case"), dict):
        identity["pending_case"].update({
            "status": "STOP_EXCLUDED_P1L5",
            "blocks_analysis": False,
            "active": False,
        })
    master["p1l5_analysis_policy"] = {
        "status": "APPROVED_ACADEMIC_EXPERIMENTAL",
        "applied_utc": now,
        "stop_element_ids": stopped,
        "structural_material_fallback": {
            "material_id": fallback_id,
            "valid_use_count_before_assignment": fallback_count,
            "all_valid_counts": dict(valid_counts),
            "assigned_element_count": len(traced_fallbacks),
            "assigned_element_ids": traced_fallbacks,
            "status": "INFERRED_MATERIAL_FALLBACK",
        },
        "slabs": "GEOMETRY_AND_TRIBUTARY_ONLY_NOT_FE",
        "g35_elastic_modulus_pa": 28_000_000_000.0,
        "limitations": [
            "Not intended for structural design.",
            "Fallback material assignments and approximate elastic properties must remain visible in downstream results.",
        ],
    }
    master["sources"]["current_contract"]["status"] = "P1L5_ASSUMPTIONS_APPLIED_PENDING_RUN"
    master["generated_utc"] = now
    materials["generated_utc"] = now

    write(MASTER_PATH, master)
    write(MATERIALS_PATH, materials)
    print(json.dumps({
        "status": "PASS",
        "fallback_material": fallback_id,
        "valid_counts": valid_counts,
        "reassigned_structural_elements": len(reassigned),
        "total_inferred_material_fallbacks": len(traced_fallbacks),
        "slabs_left_unknown": sum(
            1 for row in master["elements"] if row["type"] == "slab" and row["material_id"] == "MAT_UNKNOWN"
        ),
        "stop_elements": stopped,
        "active_fe_segments": identity["fe_active_segments"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
