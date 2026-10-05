#!/usr/bin/env python3
"""Complete the reviewed E2-P4 beam zone before the load audit.

Geometry and traceability only: loads, materials and OpenSees results are not
read or written.
"""

from __future__ import annotations

import copy
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "model_master.json"
OUT = HERE / "generated" / "e2_p4_zone_completion.json"
REVISION = "E2_P4_ZONE_COMPLETION"

MERGE_CANONICAL = "E2-P4-V-024"
MERGE_ABSORBED = ["E2-P4-V-030", "E2-P4-V-035"]

RECONNECTIONS = {
    "E2-P4-V-002": {"side": "end", "target": [-3.548, 4.116, 19.4], "references": ["E2-P3-V-001", "E2-P2-V-001"]},
    "E2-P4-V-004": {"side": "end", "target": [-3.548, 8.551, 19.4], "references": ["E2-P3-V-002", "E2-P2-V-002"]},
    "E2-P4-V-017": {"side": "end", "target": [0.002, 8.551, 19.4], "references": ["E2-P3-V-010", "E2-P2-V-010", "E2-P4-C-001"]},
    # V-020 keeps the historical reversed i->j orientation after its prior
    # merge, so the high-Y endpoint is geometry.start_m.
    "E2-P4-V-020": {"side": "start", "target": [0.002, 11.736, 19.4], "references": ["E2-P3-V-011", "E2-P2-V-011", "E2-P4-V-033"]},
    "E2-P4-V-008": {"side": "start", "target": [-3.548, 12.036, 19.4], "references": ["E2-P3-V-004", "E2-P2-V-004", "E2-P4-V-012"]},
    "E2-P4-V-042": {"side": "end", "target": [7.152, 0.001, 19.4], "references": ["E2-P3-V-022", "E2-P2-V-022", "E2-P4-C-002"]},
    "E2-P4-V-043": {"side": "end", "target": [7.152, 8.901, 19.4], "references": ["E2-P3-V-023", "E2-P2-V-023", "E2-P4-C-003"]},
}

EXPECTED_FREE_ENDS = [
    "E2-S1-V-043", "E2-S1-V-044",
    "E2-P1-V-043", "E2-P1-V-044",
    "E2-P2-V-043", "E2-P2-V-044",
    "E2-P3-V-043", "E2-P3-V-044",
    "E2-P4-V-085", "E2-P4-V-091",
]

REVIEW_REQUIRED_FREE_ENDS = ["E1-P3-V-101"]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_geometry(row: dict, start: list[float], end: list[float]) -> None:
    row["geometry"]["start_m"] = start
    row["geometry"]["end_m"] = end
    row["geometry"]["center_m"] = [round((a + b) / 2.0, 3) for a, b in zip(start, end)]


def main() -> None:
    master = read(MASTER_PATH)
    prior_revision = next(
        (row for row in master.get("geometry_revision_history", []) if row.get("revision") == REVISION),
        None,
    )
    if prior_revision is not None:
        # Keep the already-applied geometry immutable while allowing the audited
        # free-end classification to be synchronized idempotently.
        prior_revision["expected_cantilevers"] = EXPECTED_FREE_ENDS
        prior_revision["review_required"] = REVIEW_REQUIRED_FREE_ENDS
        write(MASTER_PATH, master)
        print(json.dumps({
            "status": "GEOMETRY_ALREADY_APPLIED_CLASSIFICATION_SYNCHRONIZED",
            "revision": REVISION,
            "expected_cantilevers": EXPECTED_FREE_ENDS,
            "review_required": REVIEW_REQUIRED_FREE_ENDS,
        }, ensure_ascii=False, indent=2))
        return
    by_id = {row["element_id"]: row for row in master["elements"]}
    timestamp = datetime.now(timezone.utc).isoformat()
    before_counts = Counter(row["type"] for row in master["elements"])

    merge_ids = [MERGE_CANONICAL, *MERGE_ABSORBED]
    rows = [by_id[element_id] for element_id in merge_ids]
    assert all(row["type"] == "beam" and row["active"] for row in rows)
    assert len({(row["building"], row["floor"], row["section_id"], row["material_id"]) for row in rows}) == 1
    ordered = sorted(rows, key=lambda row: min(row["geometry"]["start_m"][0], row["geometry"]["end_m"][0]))
    for left, right in zip(ordered, ordered[1:]):
        assert math.dist(left["geometry"]["end_m"], right["geometry"]["start_m"]) < 1e-6
    canonical = by_id[MERGE_CANONICAL]
    merge_before = {row["element_id"]: copy.deepcopy(row["geometry"]) for row in rows}
    update_geometry(canonical, copy.deepcopy(ordered[0]["geometry"]["start_m"]), copy.deepcopy(ordered[-1]["geometry"]["end_m"]))
    canonical["analysis_refs"] = [copy.deepcopy(ref) for row in rows for ref in row.get("analysis_refs", [])]
    canonical["merged_from"] = sorted(set(canonical.get("merged_from", []) + MERGE_ABSORBED + [x for row in rows[1:] for x in row.get("merged_from", [])]))
    canonical["aliases"] = sorted(set(canonical.get("aliases", []) + MERGE_ABSORBED + [x for row in rows[1:] for x in row.get("aliases", [])]))
    source_tags = sorted({tag for row in rows for tag in row.get("provenance", {}).get("sourceTags", [])})
    if source_tags:
        canonical.setdefault("provenance", {})["sourceTags"] = source_tags
    merge_history = {
        "type": "BEAM_MERGED", "reason": "ARTIFICIAL_BEAM_FRAGMENTATION; P4 chain equals the single P3/P2 beam in XY.",
        "source": "P4 geometry + E2-P3-V-013 + E2-P2-V-013", "historical_ids": merge_ids,
        "merged_from": MERGE_ABSORBED, "review_checkpoint": REVISION, "timestamp_utc": timestamp,
    }
    canonical.setdefault("merge_history", []).append(merge_history)
    for alias in MERGE_ABSORBED:
        master.setdefault("aliases", []).append({
            "alias": alias, "canonical_element_id": MERGE_CANONICAL, "alias_active_as_element": False,
            "canonical_exists_in_current": True, "reason": "ARTIFICIAL_BEAM_FRAGMENTATION",
            "review_checkpoint": REVISION,
        })

    changed = {}
    for element_id, instruction in RECONNECTIONS.items():
        row = by_id[element_id]
        old = copy.deepcopy(row["geometry"])
        start = copy.deepcopy(row["geometry"]["start_m"])
        end = copy.deepcopy(row["geometry"]["end_m"])
        if instruction["side"] == "start":
            start = instruction["target"][:]
        else:
            end = instruction["target"][:]
        update_geometry(row, start, end)
        row.setdefault("geometry_review", []).append({
            "type": "RECONNECT_HIGH_CONFIDENCE",
            "reason": "Repeated P3/P2 endpoint and P4 receiver footprint coincide; axis, section and Z preserved; no support invented.",
            "references": instruction["references"], "old_geometry": old,
            "new_geometry": copy.deepcopy(row["geometry"]), "review_checkpoint": REVISION,
        })
        changed[element_id] = {"classification": "RECONNECT_HIGH_CONFIDENCE", "old": old, "new": copy.deepcopy(row["geometry"]), **instruction}

    master["elements"] = [row for row in master["elements"] if row["element_id"] not in set(MERGE_ABSORBED)]

    # Resolve physical endpoint nodes after geometry changes. Exact existing
    # nodes are reused; otherwise a face node is created and the FE adapter will
    # connect it to the real column/beam footprint with a rigid joint arm.
    node_by_coord = {tuple(round(v, 3) for v in row["coord_m"]): row for row in master["nodes"]}
    next_node = max(int(row["node_id"].split("-")[-1]) for row in master["nodes"]) + 1
    for row in master["elements"]:
        if row["type"] not in {"beam", "wall"} or "start_m" not in row.get("geometry", {}):
            continue
        resolved = []
        for side, point in (("start", row["geometry"]["start_m"]), ("end", row["geometry"]["end_m"])):
            key = tuple(round(v, 3) for v in point)
            node = node_by_coord.get(key)
            if node is None:
                node = {"node_id": f"N-{next_node:05d}", "coord_m": list(key), "sources": []}
                next_node += 1
                master["nodes"].append(node)
                node_by_coord[key] = node
            source = {"reason": f"{row['type']}_{side}", "owner": row["element_id"]}
            if source not in node.setdefault("sources", []):
                node["sources"].append(source)
            resolved.append(node["node_id"])
        row["nodes"] = resolved
    used = {node for row in master["elements"] + master["supports"] for node in row.get("nodes", [])}
    master["nodes"] = [row for row in master["nodes"] if row["node_id"] in used]

    after_counts = Counter(row["type"] for row in master["elements"])
    identity = master["current_pre5_identity"]
    identity.update({
        "solid_count": len(master["elements"]) + len(master["supports"]),
        "category_counts": dict(after_counts | Counter({"support": len(master["supports"])})),
        "geometry_state": f"{REVISION}_APPLIED_FE_REBUILD_REQUIRED",
        "results_state": "STALE_REANALYSIS_REQUIRED",
    })
    master.setdefault("geometry_revision_history", []).append({
        "revision": REVISION, "timestamp_utc": timestamp, "merge": merge_history,
        "reconnections": sorted(RECONNECTIONS), "expected_cantilevers": EXPECTED_FREE_ENDS,
        "review_required": REVIEW_REQUIRED_FREE_ENDS, "loads_changed": False, "materials_changed": False,
        "opensees_results_changed": False,
    })
    write(MASTER_PATH, master)
    report = {
        "status": "GEOMETRY_APPLIED_FE_REBUILD_REQUIRED", "revision": REVISION,
        "before_counts": dict(before_counts), "after_counts": dict(after_counts),
        "merge": {"canonical": MERGE_CANONICAL, "absorbed": MERGE_ABSORBED, "before": merge_before, "new": canonical["geometry"]},
        "endpoints": changed,
        "classifications": {
            **{element_id: "RECONNECT_HIGH_CONFIDENCE" for element_id in RECONNECTIONS},
            **{element_id: "EXPECTED_CANTILEVER" for element_id in EXPECTED_FREE_ENDS},
        },
        "review_required": REVIEW_REQUIRED_FREE_ENDS, "loads_changed": False, "materials_changed": False,
        "opensees_results_changed": False,
    }
    write(OUT, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
