#!/usr/bin/env python3
"""Prepare an isolated central-model candidate for evidence-backed wall restoration.

This deliberately does not edit the live model or historical exclusion register.
Use the returned files for FE/connectivity validation before promotion.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
EXCLUSIONS = ROOT / "entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json"
MATERIAL_BY_BUILDING = {
    "EDIFICIO_1": "MAT_G35_10_2017_67_100_1E116",
    "EDIFICIO_2": "MAT_G35_10_2024_22_100_53994",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(master: dict, sections: dict, candidates: dict, exclusions: dict,
            only_ids: set[str] | None = None) -> tuple[dict, dict, dict]:
    master, sections = copy.deepcopy(master), copy.deepcopy(sections)
    selected = [r for r in candidates["candidates"] if r["decision"] == "CONFIRMED_REINTEGRATE"]
    if only_ids is not None:
        unknown = only_ids - {r["candidate_id"] for r in selected}
        if unknown:
            raise ValueError(f"Requested IDs are not confirmed: {sorted(unknown)}")
        selected = [r for r in selected if r["candidate_id"] in only_ids]
    by_id = {r["element_id"]: r for r in exclusions["exclusions"]}
    active_ids = {r["element_id"] for r in master["elements"]}
    solid_tags = {r["solidTag"] for r in master["elements"] + master["supports"]}
    section_rows = {r["section_id"]: r for r in sections["sections"]}
    material_ids = {r["material_id"] for r in read(CENTRAL / "materials.json")["materials"]}
    node_by_coord = {tuple(round(v, 4) for v in n["coord_m"]): n["node_id"] for n in master["nodes"]}
    if len(node_by_coord) != len(master["nodes"]):
        raise ValueError("Existing physical node coordinates are duplicated")
    next_node = max(int(n["node_id"].split("-")[-1]) for n in master["nodes"]) + 1
    restored = []
    for candidate in selected:
        identifier = candidate["candidate_id"]
        if identifier in active_ids or identifier not in by_id:
            raise ValueError(f"Unexpected active/missing exclusion: {identifier}")
        source = by_id[identifier]["before"]
        primary = candidate["primary_pair_audit"]
        if not primary["confirmed_pair"] or primary["pair_count"] != 1:
            raise ValueError(f"No unique primary CAD face pair: {identifier}")
        if not all(candidate[k] and candidate[k]["strong"] for k in ("santiago", "caceres")):
            raise ValueError(f"External geometry check changed: {identifier}")
        if candidate["active_duplicate"]:
            raise ValueError(f"Active duplicate: {identifier}")
        if source["solidTag"] in solid_tags:
            raise ValueError(f"Duplicate solidTag: {identifier}")
        building, floor = candidate["building"], candidate["floor"]
        if building == "EDIFICIO_1" and floor == "P4":
            raise ValueError(f"ED1/P4 material scope unresolved: {identifier}")
        if building == "EDIFICIO_2" and floor == "P4":
            raise ValueError(f"E2/P4 prior user scope conflict: {identifier}")
        material_id = MATERIAL_BY_BUILDING[building]
        if material_id not in material_ids:
            raise ValueError(f"Missing material catalog entry: {material_id}")
        start = [float(x) for x in source["coordinates"]["start"]]
        end = [float(x) for x in source["coordinates"]["end"]]
        if len(start) != 3 or len(end) != 3 or abs(start[2] - end[2]) > 1e-4:
            raise ValueError(f"Invalid wall endpoints: {identifier}")
        length = math.dist(start[:2], end[:2])
        thickness = float(candidate["geometry"]["thickness_m"])
        bottom = float(source["coordinates"]["z_bottom_m"])
        top = float(source["coordinates"]["z_top_m"])
        if min(length, thickness, top - bottom) <= 0:
            raise ValueError(f"Nonpositive wall dimension: {identifier}")
        if abs(length - float(source["length_m"])) > 0.02:
            raise ValueError(f"Length differs from original CAD audit: {identifier}")
        section_id = f"SEC_WALL_{thickness:.3f}x{length:.3f}"
        if section_id in section_rows:
            dims = section_rows[section_id]["dimensions"]
            if abs(dims["thickness_m"] - thickness) > 0.001 or abs(dims["length_m"] - length) > 0.002:
                raise ValueError(f"Section ID collision: {identifier}")
            section_rows[section_id]["used_by_count"] += 1
        else:
            section = {
                "section_id": section_id,
                "type": "wall_equivalent_rectangular",
                "units": "m",
                "dimensions": {"thickness_m": thickness, "length_m": round(length, 4)},
                "status": "GEOMETRY_DERIVED_LENGTH",
                "provenance": {"source_dxf": source["source_dxf"], "source_layer": source["source_layer"],
                               "source_tags": source["sourceTags"], "primary_pair_audit": primary},
                "used_by_count": 1,
                "provenance_examples": [{"element_id": identifier, "building": building, "floor": floor,
                                         "source_dxf": source["source_dxf"], "source_layer": source["source_layer"]}],
            }
            sections["sections"].append(section)
            section_rows[section_id] = section
        node_ids = []
        for point in (start, end):
            key = tuple(round(v, 4) for v in point)
            node_id = node_by_coord.get(key)
            if node_id is None:
                node_id = f"N-{next_node:05d}"
                next_node += 1
                node_by_coord[key] = node_id
                master["nodes"].append({"node_id": node_id, "coord_m": list(key),
                                        "sources": [{"reason": "restored_wall_endpoint", "owner": identifier}]})
            node_ids.append(node_id)
        element = {
            "element_id": identifier, "solidTag": source["solidTag"], "type": "wall",
            "building": building, "floor": floor, "nodes": node_ids,
            "geometry": {"kind": "linear_prism", "start_m": start, "end_m": end,
                         "center_m": [(start[i] + end[i]) / 2 for i in range(3)],
                         "z_bottom_m": bottom, "z_top_m": top},
            "section_id": section_id, "material_id": material_id, "active": True,
            "analysis_id": None, "opensees_tag": None, "analysis_refs": [],
            "aliases": [], "merged_from": [],
            "provenance": {"source_file": EXCLUSIONS.relative_to(ROOT).as_posix(),
                           "source_dxf": source["source_dxf"], "source_layer": source["source_layer"],
                           "sourceTags": source["sourceTags"], "confidence": source["confidence"],
                           "primary_pair_audit": primary,
                           "external_repo_clue": [candidate["santiago"]["id"], candidate["caceres"]["id"]],
                           "prior_exclusion_reason": candidate["previous_removal_reason"]},
            "merge_history": [], "analysis_status": "STALE_REANALYSIS_REQUIRED",
        }
        master["elements"].append(element)
        active_ids.add(identifier)
        solid_tags.add(source["solidTag"])
        restored.append({"element_id": identifier, "building": building, "floor": floor,
                         "start_m": start, "end_m": end, "length_m": round(length, 4),
                         "thickness_m": thickness, "section_id": section_id,
                         "material_id": material_id, "nodes": node_ids,
                         "primary_source": source["source_dxf"], "primary_face_tags": source["sourceTags"]})
    master.setdefault("geometry_revision_history", []).append({
        "revision": "P1L6_WALL_RESTORATION_CANDIDATE", "status": "STALE_REANALYSIS_REQUIRED",
        "restored_ids": [r["element_id"] for r in restored],
        "source_audit": (HERE / "removed_wall_candidates.json").relative_to(ROOT).as_posix(),
    })
    manifest = {"status": "CANDIDATE_NOT_PROMOTED", "restored_count": len(restored),
                "by_building_floor": {str(k): v for k, v in Counter((r["building"], r["floor"]) for r in restored).items()},
                "restored": restored,
                "excluded_review_required": [r["candidate_id"] for r in candidates["candidates"] if r["decision"].startswith("REVIEW_REQUIRED")]}
    return master, sections, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--only-ids", type=Path, help="JSON array of confirmed IDs to prepare as a subset")
    parser.add_argument("--exclude-floating-from", type=Path,
                        help="Isolated FE candidate QA whose floating IDs remain deferred")
    args = parser.parse_args()
    only_ids = set(read(args.only_ids)) if args.only_ids else None
    if args.exclude_floating_from:
        eligible = {r["candidate_id"] for r in read(HERE / "removed_wall_candidates.json")["candidates"]
                    if r["decision"] == "CONFIRMED_REINTEGRATE"}
        floating = set(read(args.exclude_floating_from)["floating_ids"])
        only_ids = eligible - floating if only_ids is None else only_ids - floating
    master, sections, manifest = prepare(
        read(CENTRAL / "model_master.json"), read(CENTRAL / "sections.json"),
        read(HERE / "removed_wall_candidates.json"), read(EXCLUSIONS), only_ids,
    )
    write(args.output_dir / "model_master.json", master)
    write(args.output_dir / "sections.json", sections)
    write(args.output_dir / "restoration_manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "restored_count": manifest["restored_count"],
                      "new_nodes": len(master["nodes"]), "new_sections": len(sections["sections"])}, indent=2))


if __name__ == "__main__":
    main()
