#!/usr/bin/env python3
"""Retire the 13 approved visual/historical support solids from CURRENT.

The 33 actual FE support nodes remain fixed in all six DOF.  Retired visual
objects are archived with full traceability and do not alter FE constraints.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "model_master.json"
SECTIONS_PATH = HERE / "sections.json"
ARCHIVE_PATH = HERE / "archive" / "p1l6_retired_visual_supports.json"
REVISION = "P1L6_VISUAL_SUPPORT_CLEANUP"
RETIRE = {
    "E1-S1-A-002", "E1-S1-A-019", "E1-S1-A-022", "E1-S1-A-033",
    "E1-S1-A-034", "E1-S1-A-042", "E1-S1-A-056", "E1-S1-A-080",
    "E2-S1-A-014", "E2-S1-A-015", "E2-S1-A-017", "E2-S1-A-018", "E2-S1-A-019",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    master = read(MASTER_PATH)
    sections = read(SECTIONS_PATH)
    if any(row.get("revision") == REVISION for row in master.get("geometry_revision_history", [])):
        print(json.dumps({"status": "ALREADY_APPLIED", "revision": REVISION}, indent=2))
        return
    by_id = {row["element_id"]: row for row in master["supports"]}
    missing = sorted(RETIRE - set(by_id))
    if missing:
        raise AssertionError(f"Approved visual supports missing: {missing}")
    if len(master["fe_topology"]["support_node_tags"]) != 33:
        raise AssertionError("FE support contract changed before visual cleanup")
    fixed_before = list(master["fe_topology"]["support_node_tags"])
    retired = [by_id[element_id] for element_id in sorted(RETIRE)]
    master["supports"] = [row for row in master["supports"] if row["element_id"] not in RETIRE]
    used = {node for row in master["elements"] + master["supports"] for node in row.get("nodes", [])}
    master["nodes"] = [row for row in master["nodes"] if row["node_id"] in used]
    if master["fe_topology"]["support_node_tags"] != fixed_before:
        raise AssertionError("Visual cleanup altered FE support nodes")

    counts = Counter(
        row.get("section_id") for row in master["elements"] + master["supports"] if row.get("section_id")
    )
    for section in sections["sections"]:
        section["used_by_count"] = counts.get(section["section_id"], 0)

    identity = master["current_pre5_identity"]
    category_counts = Counter(row["type"] for row in master["elements"])
    category_counts["support"] = len(master["supports"])
    identity.update({
        "solid_count": len(master["elements"]) + len(master["supports"]),
        "category_counts": dict(category_counts),
        "visual_supports": len(master["supports"]),
        "fe_supports": 33,
        "support_state": "33_FIXED_6DOF_CURRENT_VISUAL_MATCH",
        "results_state": "STALE_REANALYSIS_REQUIRED",
    })
    timestamp = datetime.now(timezone.utc).isoformat()
    master.setdefault("geometry_revision_history", []).append({
        "revision": REVISION, "timestamp_utc": timestamp,
        "retired_visual_support_ids": sorted(RETIRE),
        "visual_supports_before": 46, "visual_supports_after": len(master["supports"]),
        "fe_supports_before": 33, "fe_supports_after": len(master["fe_topology"]["support_node_tags"]),
        "constraint_assumption": "All 33 FE base nodes fixed in UX, UY, UZ, RX, RY, RZ.",
        "opensees_results_changed": False,
    })
    write(MASTER_PATH, master)
    write(SECTIONS_PATH, sections)
    write(ARCHIVE_PATH, {
        "format": "MCOC_P1L6_RETIRED_VISUAL_SUPPORTS_V1", "timestamp_utc": timestamp,
        "reason": "Approved visual/historical extras; not FE restraints in CURRENT.",
        "fe_supports_preserved": 33, "fixed_dofs": [1, 1, 1, 1, 1, 1],
        "retired_supports": retired,
    })
    print(json.dumps({
        "status": "PASS", "retired_visual_supports": len(retired),
        "current_visual_supports": len(master["supports"]), "fe_supports": 33,
        "fixed_dofs": [1, 1, 1, 1, 1, 1],
    }, indent=2))


if __name__ == "__main__":
    main()
