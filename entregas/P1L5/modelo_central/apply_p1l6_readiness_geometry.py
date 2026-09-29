#!/usr/bin/env python3
"""Apply the geometry corrections approved for the P1L6 readiness baseline.

This script only changes canonical geometry/properties and traceability.  It
does not calculate loads or analysis results.  Run the central FE rebuild and
the normal derivative builders after it.
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
SECTIONS_PATH = HERE / "sections.json"
REPORT_PATH = HERE / "generated" / "p1l6_readiness_geometry.json"
REVISION = "P1L6_READINESS_GEOMETRY"

COLUMN_ID = "E1-P1-C-023"
COLUMN_OLD_SECTION = "SEC_COLUMN_RECT_0.200x0.500"
COLUMN_NEW_SECTION = "SEC_COLUMN_RECT_0.700x0.700"

BEAM_EXTENSION_ID = "E1-P3-V-101"
BEAM_EXTENSION_START = [67.841, 16.331, 15.44]

MERGE_GROUPS = [
    ("E2-P4-V-063", ["E2-P4-V-066", "E2-P4-V-068"]),
    ("E2-P4-V-064", ["E2-P4-V-067", "E2-P4-V-069"]),
    ("E2-P4-V-074", ["E2-P4-V-077", "E2-P4-V-078"]),
    ("E2-P4-V-084", ["E2-P4-V-087", "E2-P4-V-089"]),
    ("E2-P4-V-086", ["E2-P4-V-088", "E2-P4-V-091"]),
]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pkey(point: list[float]) -> tuple[float, float, float]:
    return tuple(round(float(value), 3) for value in point)


def update_linear_geometry(row: dict, start: list[float], end: list[float]) -> None:
    row["geometry"]["start_m"] = [round(value, 3) for value in start]
    row["geometry"]["end_m"] = [round(value, 3) for value in end]
    row["geometry"]["center_m"] = [round((a + b) / 2.0, 3) for a, b in zip(start, end)]


def chain_endpoints(rows: list[dict]) -> tuple[list[float], list[float]]:
    points: dict[tuple[float, float, float], list[float]] = {}
    degree: Counter = Counter()
    for row in rows:
        for point in (row["geometry"]["start_m"], row["geometry"]["end_m"]):
            key = pkey(point)
            points[key] = list(key)
            degree[key] += 1
    ends = sorted((points[key] for key, count in degree.items() if count == 1), key=lambda p: (p[0], p[1], p[2]))
    if len(ends) != 2:
        raise AssertionError(f"Expected two physical chain endpoints, found {ends}")
    return ends[0], ends[1]


def validate_merge(rows: list[dict]) -> None:
    signatures = {
        (row["building"], row["floor"], row["section_id"], row["material_id"], row["geometry"]["z_bottom_m"], row["geometry"]["z_top_m"])
        for row in rows
    }
    if len(signatures) != 1:
        raise AssertionError(f"Merge group properties differ: {signatures}")
    vectors = []
    for row in rows:
        start, end = row["geometry"]["start_m"], row["geometry"]["end_m"]
        vectors.append((end[0] - start[0], end[1] - start[1]))
    base = vectors[0]
    for vector in vectors[1:]:
        cross = base[0] * vector[1] - base[1] * vector[0]
        if abs(cross) > 1e-6:
            raise AssertionError(f"Merge group is not collinear: {vectors}")
    chain_endpoints(rows)


def rebuild_physical_nodes(master: dict) -> None:
    node_by_coord = {pkey(row["coord_m"]): row for row in master["nodes"]}
    next_node = max(int(row["node_id"].split("-")[-1]) for row in master["nodes"]) + 1
    for row in master["elements"]:
        geometry = row.get("geometry", {})
        if row["type"] not in {"beam", "wall"} or "start_m" not in geometry:
            continue
        resolved = []
        for side, point in (("start", geometry["start_m"]), ("end", geometry["end_m"])):
            key = pkey(point)
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


def refresh_section_usage(master: dict, sections: dict) -> None:
    # The section catalogue also contains the visualization-only support
    # sections, so both physical elements and supports participate in its
    # usage counters.
    counts = Counter(
        row.get("section_id")
        for row in master["elements"] + master["supports"]
        if row.get("section_id")
    )
    for section in sections["sections"]:
        section["used_by_count"] = counts.get(section["section_id"], 0)
        examples = [row for row in section.get("provenance_examples", []) if row.get("element_id") != COLUMN_ID]
        if section["section_id"] == COLUMN_NEW_SECTION:
            examples.append({
                "element_id": COLUMN_ID,
                "building": "EDIFICIO_1",
                "floor": "P1",
                "source_dxf": "2017_67-101.dxf",
                "source_layer": "RLE-PILAR",
                "section_source": "VERTICAL_STACK_CONTINUITY_S1_P2_P3_P4",
                "section_confidence": "CONFIRMED_FROM_VERTICAL_STACK",
            })
        section["provenance_examples"] = examples


def main() -> None:
    master = read(MASTER_PATH)
    sections = read(SECTIONS_PATH)
    if any(row.get("revision") == REVISION for row in master.get("geometry_revision_history", [])):
        refresh_section_usage(master, sections)
        write(SECTIONS_PATH, sections)
        print(json.dumps({"status": "ALREADY_APPLIED", "revision": REVISION}, indent=2))
        return

    timestamp = datetime.now(timezone.utc).isoformat()
    by_id = {row["element_id"]: row for row in master["elements"]}
    before_counts = Counter(row["type"] for row in master["elements"])

    column = by_id[COLUMN_ID]
    if column["section_id"] != COLUMN_OLD_SECTION:
        raise AssertionError(f"Unexpected original section for {COLUMN_ID}: {column['section_id']}")
    column["section_id"] = COLUMN_NEW_SECTION
    column.setdefault("property_review", []).append({
        "type": "SECTION_UPDATED",
        "old_section_id": COLUMN_OLD_SECTION,
        "new_section_id": COLUMN_NEW_SECTION,
        "reason": "Vertical stack S1/P2/P3/P4 has the same XY and a continuous 0.70 x 0.70 m section.",
        "evidence": ["E1-S1-C-023", "E1-P2-C-023", "E1-P3-C-023", "E1-P4-C-023"],
        "review_checkpoint": REVISION,
        "timestamp_utc": timestamp,
    })

    extension = by_id[BEAM_EXTENSION_ID]
    old_extension_geometry = copy.deepcopy(extension["geometry"])
    if math.dist(extension["geometry"]["start_m"], BEAM_EXTENSION_START) > 1.0:
        raise AssertionError("Proposed beam extension is not local")
    update_linear_geometry(extension, BEAM_EXTENSION_START, extension["geometry"]["end_m"])
    extension.setdefault("geometry_review", []).append({
        "type": "RECONNECT_HIGH_CONFIDENCE",
        "side": "start",
        "old_geometry": old_extension_geometry,
        "new_geometry": copy.deepcopy(extension["geometry"]),
        "reason": "Beam axis reaches the existing exterior column face on the repeated structural line; no node or support is invented.",
        "references": ["E1-P3-C-023", "E1-P2 structural pattern", "2017_67-102.dxf"],
        "review_checkpoint": REVISION,
        "timestamp_utc": timestamp,
    })

    absorbed_ids: set[str] = set()
    merge_report = []
    for canonical_id, absorbed in MERGE_GROUPS:
        ids = [canonical_id, *absorbed]
        rows = [by_id[element_id] for element_id in ids]
        validate_merge(rows)
        start, end = chain_endpoints(rows)
        canonical = by_id[canonical_id]
        before = {row["element_id"]: copy.deepcopy(row["geometry"]) for row in rows}
        update_linear_geometry(canonical, start, end)
        canonical["analysis_refs"] = [copy.deepcopy(ref) for row in rows for ref in row.get("analysis_refs", [])]
        historical_ids = set(canonical.get("merged_from", []))
        aliases = set(canonical.get("aliases", []))
        source_tags = set(canonical.get("provenance", {}).get("sourceTags", []))
        for row in rows[1:]:
            historical_ids.add(row["element_id"])
            historical_ids.update(row.get("merged_from", []))
            aliases.add(row["element_id"])
            aliases.update(row.get("aliases", []))
            source_tags.update(row.get("provenance", {}).get("sourceTags", []))
        canonical["merged_from"] = sorted(historical_ids)
        canonical["aliases"] = sorted(aliases)
        canonical.setdefault("provenance", {})["sourceTags"] = sorted(source_tags)
        history = {
            "type": "BEAM_MERGED",
            "reason": "ARTIFICIAL_BEAM_FRAGMENTATION; one physical beam with unchanged section, material, axis and level.",
            "historical_ids": ids,
            "merged_from": absorbed,
            "review_checkpoint": REVISION,
            "timestamp_utc": timestamp,
        }
        canonical.setdefault("merge_history", []).append(history)
        for alias in absorbed:
            absorbed_ids.add(alias)
            master.setdefault("aliases", []).append({
                "alias": alias,
                "canonical_element_id": canonical_id,
                "alias_active_as_element": False,
                "canonical_exists_in_current": True,
                "reason": "ARTIFICIAL_BEAM_FRAGMENTATION",
                "review_checkpoint": REVISION,
            })
        merge_report.append({
            "canonical_element_id": canonical_id,
            "merged_from": absorbed,
            "historical_ids": ids,
            "before": before,
            "new_geometry": copy.deepcopy(canonical["geometry"]),
        })

    master["elements"] = [row for row in master["elements"] if row["element_id"] not in absorbed_ids]
    rebuild_physical_nodes(master)
    refresh_section_usage(master, sections)

    after_counts = Counter(row["type"] for row in master["elements"])
    identity = master["current_pre5_identity"]
    identity.update({
        "solid_count": len(master["elements"]) + len(master["supports"]),
        "category_counts": dict(after_counts | Counter({"support": len(master["supports"])})),
        "geometry_state": f"{REVISION}_APPLIED_FE_REBUILD_REQUIRED",
        "results_state": "STALE_REANALYSIS_REQUIRED",
    })
    revision = {
        "revision": REVISION,
        "timestamp_utc": timestamp,
        "column_section_update": {"element_id": COLUMN_ID, "from": COLUMN_OLD_SECTION, "to": COLUMN_NEW_SECTION},
        "beam_extension": {"element_id": BEAM_EXTENSION_ID, "old": old_extension_geometry, "new": extension["geometry"]},
        "beam_merges": merge_report,
        "loads_changed": False,
        "materials_changed": False,
        "opensees_results_changed": False,
    }
    master.setdefault("geometry_revision_history", []).append(revision)
    write(MASTER_PATH, master)
    write(SECTIONS_PATH, sections)
    report = {
        "status": "GEOMETRY_APPLIED_FE_REBUILD_REQUIRED",
        "revision": REVISION,
        "before_counts": dict(before_counts),
        "after_counts": dict(after_counts),
        "column_section_update": revision["column_section_update"],
        "beam_extension": revision["beam_extension"],
        "beam_merges": merge_report,
        "absorbed_element_count": len(absorbed_ids),
        "results_state": "STALE_REANALYSIS_REQUIRED",
    }
    write(REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
