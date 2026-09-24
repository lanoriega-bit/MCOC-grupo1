#!/usr/bin/env python3
"""Rebuild the FE topology from model_master.json without running OpenSees.

The proven PRE5 topology builder is reused as a geometry algorithm through an
explicit central-model adapter.  Its output is migrated back into the central
contract and stable analysis IDs/tags are retained whenever possible.
"""

from __future__ import annotations

import importlib.util
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "model_master.json"
SECTIONS_PATH = HERE / "sections.json"
ADAPTER_PATH = HERE / "generated" / "current_geometry_for_fe.json"
CANDIDATE_PATH = HERE / "generated" / "rebuilt_fe_topology.json"
CANDIDATE_REPORT = HERE / "generated" / "rebuilt_fe_topology.md"
LEGACY_BUILDER = ROOT / "entregas" / "P1L3" / "scripts" / "build_post_p1l3_topology_candidate.py"
PRIOR_AUDIT = ROOT / "entregas" / "P1L2" / "edificio" / "validacion" / "fe_connectivity_post_geometry" / "connectivity_comparison.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def adapted_solids(master: dict, sections: dict[str, dict]) -> list[dict]:
    solids = []
    for row in master["elements"]:
        if not row.get("active") or row["type"] not in {"beam", "column", "wall"}:
            continue
        geometry = row["geometry"]
        dims = sections[row["section_id"]]["dimensions"]
        solid = {
            "id": row["element_id"], "solidTag": row["solidTag"], "category": row["type"],
            "building": row["building"], "floor": row["floor"], "coordinates": {
                "center": geometry["center_m"], "z_bottom_m": geometry["z_bottom_m"],
                "z_top_m": geometry["z_top_m"],
            },
        }
        if row["type"] in {"beam", "wall"}:
            solid["start"] = geometry["start_m"]
            solid["end"] = geometry["end_m"]
            solid["coordinates"]["start"] = geometry["start_m"]
            solid["coordinates"]["end"] = geometry["end_m"]
        if row["type"] == "beam":
            solid["width_m"] = dims["width_m"]
            solid["height_m"] = dims["height_m"]
        elif row["type"] == "column":
            solid["width_m"] = dims["width_m"]
            solid["depth_m"] = dims["depth_m"]
            solid["section_width_m"] = dims["width_m"]
            solid["section_depth_m"] = dims["depth_m"]
        else:
            solid["width_m"] = dims["thickness_m"]
            solid["length_m"] = dims["length_m"]
        solids.append(solid)
    return solids


def coords(nodes: dict, ref: dict) -> tuple[tuple[float, ...], tuple[float, ...]]:
    def point(tag):
        row = nodes[str(tag)]
        return (float(row["x"]), float(row["y"]), float(row["z"]))
    return point(ref["node_i"]), point(ref["node_j"])


def segment_distance(a, b) -> float:
    direct = math.dist(a[0], b[0]) + math.dist(a[1], b[1])
    reverse = math.dist(a[0], b[1]) + math.dist(a[1], b[0])
    return min(direct, reverse)


def main() -> None:
    master = read(MASTER_PATH)
    sections_data = read(SECTIONS_PATH)
    sections = {row["section_id"]: row for row in sections_data["sections"]}
    old_topology = master["fe_topology"]
    old_refs = defaultdict(list)
    max_tag = 10000
    for row in master["elements"]:
        for ref in row.get("analysis_refs", []):
            max_tag = max(max_tag, int(ref["opensees_tag"]))
            old_refs[row["element_id"]].append({**ref, "coords": coords(old_topology["nodes"], ref), "used": False})

    adapter = {
        "model": "P1L5_CURRENT_CENTRAL_FE_ADAPTER",
        "units": "m",
        "solids": adapted_solids(master, sections),
    }
    write(ADAPTER_PATH, adapter)

    spec = importlib.util.spec_from_file_location("central_legacy_topology_builder", LEGACY_BUILDER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    level_z = {}
    for row in master["elements"]:
        if row["type"] == "beam" and row.get("active"):
            level_z[row["floor"]] = float(row["geometry"]["z_top_m"])
    module.COMBINED_VIEWER_JSON = ADAPTER_PATH
    module.OUT_DIR = CANDIDATE_PATH.parent
    module.OUT_JSON = CANDIDATE_PATH
    module.OUT_REPORT = CANDIDATE_REPORT
    module.AUDIT = PRIOR_AUDIT
    module.LEVELS_Z_M = level_z
    module.main()
    candidate = read(CANDIDATE_PATH)

    new_nodes = candidate["nodes"]
    new_by_geometry = defaultdict(list)
    for element in candidate["elements"]:
        new_by_geometry[element["element_id"]].append(element)

    # Preserve stable analysis identities by nearest segment within the same
    # physical element.  New identities are allocated only for genuinely new
    # segmentation created by the rebuilt topology.
    assigned = {}
    new_ref_total = 0
    for row in master["elements"]:
        refs = []
        for index, element in enumerate(sorted(new_by_geometry.get(row["element_id"], []), key=lambda x: x["geometry_segment_index"])):
            new_segment = coords(new_nodes, element)
            available = [ref for ref in old_refs[row["element_id"]] if not ref["used"]]
            chosen = min(available, key=lambda ref: segment_distance(ref["coords"], new_segment)) if available else None
            if chosen is not None:
                chosen["used"] = True
                analysis_id = chosen["analysis_id"]
                tag = int(chosen["opensees_tag"])
            else:
                max_tag += 1
                tag = max_tag
                analysis_id = f"POST-A-{tag - 10000:05d}"
            ref = {
                "analysis_id": analysis_id,
                "opensees_tag": tag,
                "node_i": element["node_i"],
                "node_j": element["node_j"],
                "geometry_segment_index": index,
                "source": "entregas/P1L5/modelo_central/model_master.json / rebuilt central FE topology",
                "status": "CURRENT_GEOMETRY_NOT_RUN",
            }
            if analysis_id in assigned:
                raise RuntimeError(f"Duplicate stable analysis ID: {analysis_id}")
            assigned[analysis_id] = row["element_id"]
            refs.append(ref)
            new_ref_total += 1
        row["analysis_refs"] = refs
        row["analysis_id"] = refs[0]["analysis_id"] if len(refs) == 1 else None
        row["opensees_tag"] = refs[0]["opensees_tag"] if len(refs) == 1 else None
        if row["type"] in {"beam", "column", "wall"}:
            row["analysis_status"] = "CURRENT_GEOMETRY_NOT_RUN"

    floating = candidate["floating_excluded"]
    timestamp = datetime.now(timezone.utc).isoformat()
    master["fe_topology"] = {
        "status": "APPROVED_FOR_ANALYSIS",
        "migrated_utc": timestamp,
        "provenance": {
            "source": "entregas/P1L5/modelo_central/model_master.json",
            "method": "central adapter + audited PRE5 physical-footprint topology algorithm",
            "legacy_algorithm": LEGACY_BUILDER.relative_to(ROOT).as_posix(),
            "opensees_executed": False,
        },
        "units": candidate["units"],
        "nodes": candidate["nodes"],
        "constraints": candidate["constraints"],
        "support_node_tags": candidate["supports"],
        "junction_connections": candidate["junction_connections"],
        "connectivity_validation": candidate["connectivity_validation"],
        "floating_excluded": floating,
        "qa": {**candidate["qa"], "stable_analysis_ids_reused": sum(ref["used"] for refs in old_refs.values() for ref in refs)},
        "run_policy": {
            "status": "GEOMETRY_APPROVED_RESULTS_NOT_RECALCULATED",
            "active_only": True,
            "stop_element_ids": [],
            "no_invented_supports": True,
            "opensees_run": False,
            "loads_changed": False,
            "results_changed": False,
            "authorised_utc": timestamp,
        },
    }
    identity = master["current_pre5_identity"]
    type_counts = Counter(row["type"] for row in master["elements"])
    identity.update({
        "solid_count": len(master["elements"]) + len(master["supports"]),
        "category_counts": dict(type_counts | Counter({"support": len(master["supports"])})),
        "fe_total_segments": new_ref_total,
        "fe_candidate_members": new_ref_total,
        "fe_active_segments": new_ref_total,
        "fe_candidate_nodes": len(candidate["nodes"]),
        "fe_candidate_supports": len(candidate["supports"]),
        "pending_case": None,
        "geometry_state": "FINAL_BEAM_GEOMETRY_REVIEW_FE_REBUILT",
        "results_state": "P1L5_RESULTS_HISTORICAL_NOT_RECALCULATED",
    })
    write(MASTER_PATH, master)
    summary = {
        "status": "PASS" if not floating["components"] else "PASS_WITH_NOTE",
        "fe_nodes": len(candidate["nodes"]),
        "fe_segments": new_ref_total,
        "constraints": len(candidate["constraints"]),
        "supports": len(candidate["supports"]),
        "floating_components": floating["n_componentes"],
        "floating_geometry_elements": floating["n_geometry_elements"],
        "floating_ids": sorted({x for component in floating["components"] for x in component["geometry_element_ids"]}),
        "stable_analysis_ids_reused": master["fe_topology"]["qa"]["stable_analysis_ids_reused"],
        "opensees_run": False,
        "loads_changed": False,
        "results_changed": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
