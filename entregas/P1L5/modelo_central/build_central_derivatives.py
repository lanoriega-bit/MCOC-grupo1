#!/usr/bin/env python3
"""Build fail-closed derivatives from the P1L5 central model.

Outputs are written only to entregas/P1L5/modelo_central/generated.
No historical file is used as a fallback.  OpenSees execution is enabled only
after geometry, topology, material and load gates are all ready.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def by_id(rows: list[dict], key: str) -> dict[str, dict]:
    return {row[key]: row for row in rows}


def build_viewer_preview(master: dict, sections: dict, materials: dict) -> dict:
    solids = []
    for row in master["elements"] + master["supports"]:
        section = sections[row["section_id"]]
        material = materials[row["material_id"]]
        geometry = row["geometry"]
        solid = {
            "id": row["element_id"],
            "solidTag": row.get("solidTag"),
            "category": row["type"],
            "building": row.get("building"),
            "floor": row.get("floor"),
            "kind": geometry.get("kind"),
            "coordinates": {},
            "section_id": row["section_id"],
            "material_id": row["material_id"],
            "material": material.get("name"),
            "active": row["active"],
            "merged_from": row.get("merged_from", []),
            "source_dxf": row.get("provenance", {}).get("source_dxf"),
            "source_layer": row.get("provenance", {}).get("source_layer"),
        }
        dims = section.get("dimensions", {})
        if "start_m" in geometry:
            solid["start"] = geometry["start_m"]
            solid["end"] = geometry["end_m"]
            solid["coordinates"].update({
                "start": geometry["start_m"],
                "end": geometry["end_m"],
                "center": geometry["center_m"],
                "z_bottom_m": geometry.get("z_bottom_m"),
                "z_top_m": geometry.get("z_top_m"),
            })
        else:
            solid["center"] = geometry["center_m"]
            solid["coordinates"].update({
                "center": geometry["center_m"],
                "z_bottom_m": geometry.get("z_bottom_m"),
                "z_top_m": geometry.get("z_top_m"),
            })
        if row["type"] == "beam":
            solid["width_m"] = dims.get("width_m")
            solid["height_m"] = dims.get("height_m")
        elif row["type"] == "column":
            solid["width_m"] = dims.get("width_m")
            solid["depth_m"] = dims.get("depth_m")
            solid["height_m"] = geometry.get("z_top_m", 0) - geometry.get("z_bottom_m", 0)
        elif row["type"] == "wall":
            solid["width_m"] = dims.get("thickness_m")
            solid["length_m"] = dims.get("length_m")
            solid["height_m"] = geometry.get("z_top_m", 0) - geometry.get("z_bottom_m", 0)
        elif row["type"] == "support":
            solid["width_m"] = dims.get("width_m")
            solid["height_m"] = dims.get("height_m")
        elif row["type"] == "slab":
            solid["height_m"] = dims.get("thickness_m")
        solids.append(solid)
    return {
        "format": "MCOC_P1L5_VIEWER_PREVIEW_FROM_CENTRAL_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": rel(HERE / "model_master.json"),
        "units": master.get("units", {}).get("length", "m"),
        "note": "Preview only. Production Unity still consumes existing StreamingAssets until an explicit migration step.",
        "solids": sorted(solids, key=lambda row: row["id"]),
        "summary": {"solid_count": len(solids), "category_counts": dict(Counter(row["category"] for row in solids))},
    }


def build_opensees_preview(master: dict, sections: dict, materials: dict, loads: dict) -> dict:
    topology = master.get("fe_topology", {})
    fe_elements = []
    for row in master["elements"]:
        if row["type"] not in {"beam", "column", "wall"}:
            continue
        for ref in row.get("analysis_refs", []):
            fe_elements.append({
                "analysis_id": ref["analysis_id"],
                "opensees_element_tag": ref["opensees_tag"],
                "element_id": row["element_id"],
                "geometry_segment_index": ref.get("geometry_segment_index", 0),
                "type": row["type"],
                "active": row["active"],
                "opensees_node_i": ref["node_i"],
                "opensees_node_j": ref["node_j"],
                "section_id": row["section_id"],
                "section": sections[row["section_id"]],
                "material_id": row["material_id"],
                "material": materials[row["material_id"]],
                "requires_reanalysis_if_modified": ["active", "nodes", "section_id", "material_id"],
            })

    structural_material_ids = {
        row["material_id"]
        for row in master["elements"]
        if row["type"] in {"beam", "column", "wall"} and row.get("active")
    }
    missing_elastic = sorted(
        material_id for material_id in structural_material_ids
        if materials[material_id].get("elastic", {}).get("E_pa", {}).get("value") is None
    )
    disconnected = topology.get("floating_excluded", {}).get("components", [])
    load_status = loads.get("audited_load_catalog", {}).get("status")
    blockers = []
    if topology.get("status") != "APPROVED_FOR_ANALYSIS":
        blockers.append("FE topology is CANDIDATE_NOT_APPROVED_NOT_RUN")
    if disconnected:
        blockers.append("Disconnected FE component remains: E2-P4-V-009")
    if missing_elastic:
        blockers.append("Missing current elastic modulus for: " + ", ".join(missing_elastic))
    if load_status != "APPLIED_CURRENT":
        blockers.append(f"Current loads are not applied ({load_status})")
    return {
        "format": "MCOC_P1L5_OPENSEES_PREVIEW_FROM_CENTRAL_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": rel(HERE / "model_master.json"),
        "status": "BLOCKED" if blockers else "READY_TO_RUN",
        "run_policy": {"opensees_run": False, "production_files_written": False, "blockers": blockers},
        "nodes": topology.get("nodes", {}),
        "elements": fe_elements,
        "constraints": topology.get("constraints", []),
        "support_node_tags": topology.get("support_node_tags", []),
        "visual_supports_excluded_from_boundary_conditions": len(master["supports"]),
        "modification_policy": master["modification_policy"],
        "summary": {
            "nodes": len(topology.get("nodes", {})),
            "elements": len(fe_elements),
            "supports": len(topology.get("support_node_tags", [])),
            "constraints": len(topology.get("constraints", [])),
            "physical_structural_elements": sum(1 for row in master["elements"] if row["type"] in {"beam", "column", "wall"}),
            "fe_segments": len(fe_elements),
        },
    }


def main() -> None:
    master = load(HERE / "model_master.json")
    sections_data = load(HERE / "sections.json")
    materials_data = load(HERE / "materials.json")
    loads = load(HERE / "loads.json")
    sections = by_id(sections_data["sections"], "section_id")
    materials = by_id(materials_data["materials"], "material_id")
    viewer = build_viewer_preview(master, sections, materials)
    opensees = build_opensees_preview(master, sections, materials, loads)
    manifest = {
        "format": "MCOC_P1L5_CENTRAL_DERIVATIVES_MANIFEST_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": opensees["status"],
        "files": [
            {"path": rel(OUT / "viewer_model_preview.json"), "purpose": "Unity/viewer shape preview"},
            {"path": rel(OUT / "opensees_model_preview.json"), "purpose": "Exact current FE candidate contract; fail-closed and not executed"},
        ],
        "production_files_written": False,
    }
    write(OUT / "viewer_model_preview.json", viewer)
    write(OUT / "opensees_model_preview.json", opensees)
    write(OUT / "manifest.json", manifest)
    print(json.dumps({"generated": [item["path"] for item in manifest["files"]], "status": manifest["status"]}, indent=2))


if __name__ == "__main__":
    main()
