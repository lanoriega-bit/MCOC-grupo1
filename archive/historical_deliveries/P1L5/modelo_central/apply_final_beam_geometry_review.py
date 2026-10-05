#!/usr/bin/env python3
"""Apply the authorised final beam geometry review to the central model.

This script changes geometry and traceability only.  It deliberately does not
read or write loads, materials, capacities, or OpenSees result files.
"""

from __future__ import annotations

import copy
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "model_master.json"
OUT = HERE / "generated" / "final_beam_geometry_review.json"

GROUPS = [
    ("E2-P4-V-017", ["E2-P4-V-018"]),
    ("E2-P4-V-020", ["E2-P4-V-019"]),
    ("E2-P4-V-021", ["E2-P4-V-022", "E2-P4-V-023"]),
    ("E2-P4-V-002", ["E2-P4-V-003"]),
    ("E2-P4-V-004", ["E2-P4-V-005", "E2-P4-V-006"]),
    ("E2-P4-V-047", ["E2-P4-V-045", "E2-P4-V-044"]),
    ("E2-P4-V-034", ["E2-P4-V-029", "E2-P4-V-028"]),
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def distance(a: list[float], b: list[float]) -> float:
    return math.dist(a, b)


def longest_pair(points: list[list[float]]) -> tuple[list[float], list[float]]:
    a, b = max(combinations(points, 2), key=lambda pair: distance(*pair))
    return (copy.deepcopy(a), copy.deepcopy(b))


def update_linear_geometry(row: dict, start: list[float], end: list[float]) -> None:
    row["geometry"]["start_m"] = [round(x, 3) for x in start]
    row["geometry"]["end_m"] = [round(x, 3) for x in end]
    row["geometry"]["center_m"] = [round((a + b) / 2.0, 3) for a, b in zip(start, end)]


def main() -> None:
    master = load(MASTER_PATH)
    by_id = {row["element_id"]: row for row in master["elements"]}
    if any(alias.get("review_checkpoint") == "FINAL_BEAM_GEOMETRY_REVIEW" for alias in master.get("aliases", [])):
        raise RuntimeError("FINAL_BEAM_GEOMETRY_REVIEW was already applied")

    before_counts = Counter(row["type"] for row in master["elements"])
    merge_rows = []
    absorbed_ids: set[str] = set()
    timestamp = datetime.now(timezone.utc).isoformat()

    for canonical_id, absorbed in GROUPS:
        ids = [canonical_id, *absorbed]
        rows = [by_id[element_id] for element_id in ids]
        base = rows[0]
        assert all(row["type"] == "beam" and row["active"] for row in rows)
        assert len({row["building"] for row in rows}) == 1
        assert len({row["floor"] for row in rows}) == 1
        assert len({row["section_id"] for row in rows}) == 1
        assert len({row["material_id"] for row in rows}) == 1
        points = [point for row in rows for point in (row["geometry"]["start_m"], row["geometry"]["end_m"])]
        start, end = longest_pair(points)
        # Keep the canonical orientation when choosing which outer point is i/j.
        if distance(start, base["geometry"]["start_m"]) > distance(end, base["geometry"]["start_m"]):
            start, end = end, start
        vectors = []
        for row in rows:
            a, b = row["geometry"]["start_m"], row["geometry"]["end_m"]
            vectors.append((b[0] - a[0], b[1] - a[1]))
        cross_max = max(abs(a[0] * b[1] - a[1] * b[0]) for a, b in combinations(vectors, 2)) if len(vectors) > 1 else 0.0
        assert cross_max < 1e-6, ids
        z_values = {round(point[2], 3) for point in points}
        assert len(z_values) == 1, ids

        old_length = sum(distance(row["geometry"]["start_m"], row["geometry"]["end_m"]) for row in rows)
        new_length = distance(start, end)
        update_linear_geometry(base, start, end)
        base["nodes"] = [rows[points.index(start) // 2]["nodes"][points.index(start) % 2], rows[points.index(end) // 2]["nodes"][points.index(end) % 2]]
        base["merged_from"] = sorted(set(base.get("merged_from", []) + absorbed + [x for row in rows[1:] for x in row.get("merged_from", [])]))
        base["aliases"] = sorted(set(base.get("aliases", []) + absorbed + [x for row in rows[1:] for x in row.get("aliases", [])]))
        base["analysis_refs"] = [copy.deepcopy(ref) for row in rows for ref in row.get("analysis_refs", [])]
        source_tags = sorted({tag for row in rows for tag in row.get("provenance", {}).get("sourceTags", [])})
        if source_tags:
            base.setdefault("provenance", {})["sourceTags"] = source_tags
        history = {
            "type": "BEAM_MERGED",
            "reason": "ARTIFICIAL_BEAM_FRAGMENTATION; user-confirmed continuous physical beam; same floor, line, Z, section and material.",
            "source": "P2/P3 repetition + current geometry + user structural review",
            "historical_ids": ids,
            "merged_from": absorbed,
            "old_total_length_m": round(old_length, 4),
            "canonical_length_m": round(new_length, 4),
            "overlap_or_gap_m": round(new_length - old_length, 4),
            "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
            "timestamp_utc": timestamp,
        }
        base.setdefault("merge_history", []).append(history)
        merge_rows.append({"canonical": canonical_id, "absorbed": absorbed, **history})
        absorbed_ids.update(absorbed)
        for alias in absorbed:
            master.setdefault("aliases", []).append({
                "alias": alias,
                "canonical_element_id": canonical_id,
                "alias_active_as_element": False,
                "canonical_exists_in_current": True,
                "reason": "ARTIFICIAL_BEAM_FRAGMENTATION",
                "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
            })

    # Remove V-009 from the current geometry/FE scope, retaining an explicit record.
    removed_id = "E2-P4-V-009"
    removed = copy.deepcopy(by_id[removed_id])
    master.setdefault("inactive_historical_exclusions", []).append({
        "element_id": removed_id,
        "reason": "REMOVED_BY_STRUCTURAL_REVIEW",
        "removed_from_current_geometry": True,
        "removed_from_FE": True,
        "no_replacement_support": True,
        "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
        "timestamp_utc": timestamp,
        "historical_element": removed,
    })

    # Project the P3 reference XY to the P4 beam elevation, preserving P4 properties.
    p4 = by_id["E2-P4-V-013"]
    p3 = by_id["E2-P3-V-008"]
    old_v013 = copy.deepcopy(p4["geometry"])
    p4_z = p4["geometry"]["center_m"][2]
    v013_start = [p3["geometry"]["start_m"][0], p3["geometry"]["start_m"][1], p4_z]
    v013_end = [p3["geometry"]["end_m"][0], p3["geometry"]["end_m"][1], p4_z]
    update_linear_geometry(p4, v013_start, v013_end)
    p4["nodes"] = [p4["nodes"][0], p4["nodes"][1]]
    p4.setdefault("geometry_review", []).append({
        "type": "LOWER_FLOOR_PATTERN_PROJECTION",
        "reference": "E2-P3-V-008",
        "secondary_reference": "E2-P2-V-008",
        "old_geometry": old_v013,
        "new_geometry": copy.deepcopy(p4["geometry"]),
        "properties_preserved": ["section_id", "material_id"],
        "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
    })

    # E1-P1-V-066 and V-067 were trimmed 0.95 m short of the repeated
    # P2/P3/P4 face.
    # The corrected x=62.191 m is the left face of the 0.60 m transverse beam
    # centred at x=62.491 m; it is not an invented support.
    v067 = by_id["E1-P1-V-067"]
    old_v067 = copy.deepcopy(v067["geometry"])
    v067_start = copy.deepcopy(v067["geometry"]["start_m"])
    v067_end = [62.191, 16.15, v067_start[2]]
    update_linear_geometry(v067, v067_start, v067_end)
    v067.setdefault("geometry_review", []).append({
        "type": "BEAM_ENDPOINT_RECONNECTED",
        "reason": "High-confidence repeated-floor alignment to transverse beam footprint; no support created.",
        "references": ["E1-P2-V-090", "E1-P3-V-083", "E1-P4-V-072", "E1-P1-V-077"],
        "old_geometry": old_v067,
        "new_geometry": copy.deepcopy(v067["geometry"]),
        "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
    })
    v066 = by_id["E1-P1-V-066"]
    old_v066 = copy.deepcopy(v066["geometry"])
    v066_start = copy.deepcopy(v066["geometry"]["start_m"])
    v066_end = [62.191, 8.9, v066_start[2]]
    update_linear_geometry(v066, v066_start, v066_end)
    v066.setdefault("geometry_review", []).append({
        "type": "BEAM_ENDPOINT_RECONNECTED",
        "reason": "High-confidence repeated-floor alignment to transverse beam footprint; no support created.",
        "references": ["E1-P2-V-084", "E1-P3-V-077", "E1-P4-V-066"],
        "old_geometry": old_v066,
        "new_geometry": copy.deepcopy(v066["geometry"]),
        "review_checkpoint": "FINAL_BEAM_GEOMETRY_REVIEW",
    })

    # Remove absorbed and explicitly removed rows.
    retired = absorbed_ids | {removed_id}
    master["elements"] = [row for row in master["elements"] if row["element_id"] not in retired]

    # Update/create physical endpoint nodes and then prune only nodes unused by any
    # remaining element/support.  Internal FE nodes are rebuilt separately.
    node_by_coord = {(tuple(round(v, 3) for v in row["coord_m"])): row for row in master["nodes"]}
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
    used_nodes = {node for row in master["elements"] + master["supports"] for node in row.get("nodes", [])}
    master["nodes"] = [row for row in master["nodes"] if row["node_id"] in used_nodes]

    after_counts = Counter(row["type"] for row in master["elements"])
    identity = master.setdefault("current_pre5_identity", {})
    identity["solid_count"] = len(master["elements"]) + len(master["supports"])
    identity["category_counts"] = dict(after_counts | Counter({"support": len(master["supports"])}))
    identity["pending_case"] = None
    identity["geometry_state"] = "FINAL_BEAM_GEOMETRY_REVIEW_APPLIED_FE_REBUILD_REQUIRED"
    master.setdefault("geometry_revision_history", []).append({
        "revision": "FINAL_BEAM_GEOMETRY_REVIEW",
        "timestamp_utc": timestamp,
        "merge_groups": merge_rows,
        "removed": [{"element_id": removed_id, "reason": "REMOVED_BY_STRUCTURAL_REVIEW"}],
        "modified": ["E2-P4-V-013", "E1-P1-V-066", "E1-P1-V-067"],
        "loads_changed": False,
        "materials_changed": False,
        "opensees_results_changed": False,
    })
    write(MASTER_PATH, master)
    report = {
        "status": "GEOMETRY_APPLIED_FE_REBUILD_REQUIRED",
        "timestamp_utc": timestamp,
        "before_counts": dict(before_counts),
        "after_counts": dict(after_counts),
        "merge_groups": merge_rows,
        "removed": [removed_id],
        "lower_floor_projection": {"element_id": "E2-P4-V-013", "reference": "E2-P3-V-008", "old": old_v013, "new": p4["geometry"]},
        "endpoint_reconnections": {
            "E1-P1-V-066": {"old": old_v066, "new": v066["geometry"]},
            "E1-P1-V-067": {"old": old_v067, "new": v067["geometry"]},
        },
        "unused_physical_nodes_pruned": True,
        "loads_changed": False,
        "materials_changed": False,
        "opensees_results_changed": False,
    }
    write(OUT, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
