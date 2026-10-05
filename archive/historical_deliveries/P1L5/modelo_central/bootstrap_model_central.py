#!/usr/bin/env python3
"""Bootstrap the first P1L5 central model from the current PRE5 sources.

This script only writes inside entregas/P1L5/modelo_central. It does not touch
P1L2/P1L3 production files, StreamingAssets, or OpenSees results.

Bootstrap only: do not use this script to overwrite future manual edits to the
central canonical inputs.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

GEOMETRY = ROOT / "entregas/P1L2/unity_export/model_combined_viewer.json"
FE_CANDIDATE = ROOT / "entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json"
LOAD_CATALOG = ROOT / "entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json"
PANOS = ROOT / "entregas/P1L3/results/a1a2/panos.json"
A7_REPORT = ROOT / "entregas/P1L3/results/a7/a7_report.json"
MATERIAL_CATALOG = ROOT / "entregas/PRE_P1L5/primary_material_catalog.json"
EXCLUSIONS = ROOT / "entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json"
READINESS = ROOT / "entregas/PRE_P1L5/current_readiness/structural_readiness.json"
CURRENT_CONTRACT = ROOT / "entregas/PRE_P1L5/current_readiness/current_dataset_contract.json"


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def slug(value: object, fallback: str = "MISSING") -> str:
    text = str(value or fallback).upper()
    text = re.sub(r"[^A-Z0-9]+", "_", text).strip("_")
    return text or fallback


def rounded(value: float) -> float:
    return round(float(value), 6)


def point(values) -> list[float]:
    return [rounded(values[0]), rounded(values[1]), rounded(values[2])]


def node_key(coord) -> tuple[float, float, float]:
    return (round(float(coord[0]), 3), round(float(coord[1]), 3), round(float(coord[2]), 3))


def build_indexes(fe: dict, exclusions: dict) -> tuple[dict[str, list[dict]], dict[str, list[str]], dict[str, list[dict]]]:
    fe_by_id: dict[str, list[dict]] = defaultdict(list)
    for row in fe.get("elements", []):
        fe_by_id[row["element_id"]].append(row)

    aliases_by_canonical: dict[str, list[str]] = defaultdict(list)
    for alias, canonical in exclusions.get("merged_id_aliases", {}).items():
        aliases_by_canonical[canonical].append(alias)

    merge_history_by_id: dict[str, list[dict]] = defaultdict(list)
    for row in exclusions.get("merge_history", []):
        merge_history_by_id[row.get("id", "")].append(row)

    return fe_by_id, aliases_by_canonical, merge_history_by_id


def material_id_for(solid: dict) -> str:
    material = solid.get("material") or "UNKNOWN"
    if material == "UNKNOWN":
        return "MAT_UNKNOWN"
    source = solid.get("property_correction", {}).get("primary_source") or solid.get("material_source") or "NO_SOURCE"
    handle = solid.get("property_correction", {}).get("handle") or "NO_HANDLE"
    return f"MAT_{slug(material)}_{slug(Path(str(source)).stem)}_{slug(handle)}"


def section_payload(solid: dict) -> tuple[str, dict]:
    category = solid.get("category")
    source = {
        "source_dxf": solid.get("source_dxf"),
        "source_layer": solid.get("source_layer"),
        "section_source": solid.get("section_source"),
        "section_confidence": solid.get("section_confidence"),
    }
    if category == "beam":
        width = solid.get("section_width_m") or solid.get("width_m")
        height = solid.get("section_height_m") or solid.get("height_m")
        if width is None or height is None:
            sid = f"SEC_BEAM_MISSING_{solid['id']}"
            dims = {"width_m": None, "height_m": None}
            status = "MISSING_REVIEW_REQUIRED"
        else:
            sid = f"SEC_BEAM_RECT_{rounded(width):.3f}x{rounded(height):.3f}"
            dims = {"width_m": rounded(width), "height_m": rounded(height)}
            status = "CONFIRMED_OR_CURRENT_SOURCE"
        return sid, {"section_id": sid, "type": "beam_rectangular", "units": "m", "dimensions": dims, "status": status, "provenance": source}
    if category == "column":
        width = solid.get("section_width_m") or solid.get("width_m")
        depth = solid.get("section_depth_m") or solid.get("depth_m") or solid.get("section_height_m")
        if width is None or depth is None:
            sid = f"SEC_COLUMN_MISSING_{solid['id']}"
            dims = {"width_m": None, "depth_m": None}
            status = "MISSING_REVIEW_REQUIRED"
        else:
            sid = f"SEC_COLUMN_RECT_{rounded(width):.3f}x{rounded(depth):.3f}"
            dims = {"width_m": rounded(width), "depth_m": rounded(depth)}
            status = "CONFIRMED_OR_CURRENT_SOURCE"
        return sid, {"section_id": sid, "type": "column_rectangular", "units": "m", "dimensions": dims, "status": status, "provenance": source}
    if category == "wall":
        thickness = solid.get("width_m")
        length = solid.get("length_m")
        if thickness is None or length is None:
            sid = f"SEC_WALL_MISSING_{solid['id']}"
            dims = {"thickness_m": thickness, "length_m": length}
            status = "MISSING_REVIEW_REQUIRED"
        else:
            sid = f"SEC_WALL_{rounded(thickness):.3f}x{rounded(length):.3f}"
            dims = {"thickness_m": rounded(thickness), "length_m": rounded(length)}
            status = "GEOMETRY_DERIVED_LENGTH"
        return sid, {"section_id": sid, "type": "wall_equivalent_rectangular", "units": "m", "dimensions": dims, "status": status, "provenance": source}
    if category == "support":
        width = solid.get("width_m")
        height = solid.get("height_m")
        sid = f"SEC_SUPPORT_VISUAL_{rounded(width or 0):.3f}x{rounded(height or 0):.3f}"
        return sid, {"section_id": sid, "type": "support_visual_prism", "units": "m", "dimensions": {"width_m": width, "height_m": height}, "status": "VISUAL_SUPPORT_GEOMETRY", "provenance": source}
    if category == "slab":
        thickness = solid.get("height_m")
        sid = f"SEC_SLAB_VISUAL_{rounded(thickness or 0):.3f}"
        return sid, {"section_id": sid, "type": "slab_visual_bbox", "units": "m", "dimensions": {"thickness_m": thickness}, "status": "VISUAL_NOT_FE_MODELED", "provenance": source}
    sid = f"SEC_UNKNOWN_{slug(category)}"
    return sid, {"section_id": sid, "type": "unknown", "units": "m", "dimensions": {}, "status": "UNKNOWN", "provenance": source}


def geometry_for(solid: dict) -> dict:
    category = solid.get("category")
    coords = solid.get("coordinates", {})
    if category in {"beam", "wall"} or (category == "support" and (coords.get("start") or solid.get("start")) and (coords.get("end") or solid.get("end"))):
        return {
            "kind": solid.get("kind"),
            "start_m": point(coords.get("start", solid.get("start"))),
            "end_m": point(coords.get("end", solid.get("end"))),
            "center_m": point(coords.get("center", [(solid["start"][0] + solid["end"][0]) / 2, (solid["start"][1] + solid["end"][1]) / 2, (solid["start"][2] + solid["end"][2]) / 2])),
            "z_bottom_m": rounded(coords.get("z_bottom_m", min(solid.get("start", [0, 0, 0])[2], solid.get("end", [0, 0, 0])[2]))),
            "z_top_m": rounded(coords.get("z_top_m", max(solid.get("start", [0, 0, 0])[2], solid.get("end", [0, 0, 0])[2]))),
        }
    center = coords.get("center", solid.get("center"))
    return {
        "kind": solid.get("kind"),
        "center_m": point(center),
        "z_bottom_m": rounded(coords.get("z_bottom_m", center[2] - float(solid.get("height_m", 0)) / 2)),
        "z_top_m": rounded(coords.get("z_top_m", center[2] + float(solid.get("height_m", 0)) / 2)),
    }


def build_central() -> None:
    model = load_json(GEOMETRY)
    fe = load_json(FE_CANDIDATE)
    load_catalog = load_json(LOAD_CATALOG)
    panos = load_json(PANOS)
    a7 = load_json(A7_REPORT)
    material_catalog = load_json(MATERIAL_CATALOG)
    exclusions = load_json(EXCLUSIONS)
    readiness = load_json(READINESS)
    current_contract = load_json(CURRENT_CONTRACT)

    fe_by_id, aliases_by_canonical, merge_history_by_id = build_indexes(fe, exclusions)
    sections: dict[str, dict] = {}
    materials: dict[str, dict] = {}
    nodes: dict[tuple[float, float, float], str] = {}
    node_rows: list[dict] = []

    def ensure_node(coord, reason: str, owner: str) -> str:
        key = node_key(coord)
        if key not in nodes:
            node_id = f"N-{len(nodes) + 1:05d}"
            nodes[key] = node_id
            node_rows.append({"node_id": node_id, "coord_m": list(key), "sources": []})
        node_id = nodes[key]
        for row in node_rows:
            if row["node_id"] == node_id:
                item = {"reason": reason, "owner": owner}
                if item not in row["sources"]:
                    row["sources"].append(item)
                break
        return node_id

    elements = []
    supports = []
    all_solids = model.get("solids", [])
    active_ids = {solid.get("id") for solid in all_solids if solid.get("id")}

    for solid in all_solids:
        sid, section = section_payload(solid)
        if sid not in sections:
            section["used_by_count"] = 0
            section["provenance_examples"] = []
            sections[sid] = section
        sections[sid]["used_by_count"] += 1
        example = {
            "element_id": solid.get("id"),
            "building": solid.get("building"),
            "floor": solid.get("floor"),
            "source_dxf": solid.get("source_dxf"),
            "source_layer": solid.get("source_layer"),
            "section_source": solid.get("section_source"),
            "section_confidence": solid.get("section_confidence"),
        }
        if example not in sections[sid]["provenance_examples"] and len(sections[sid]["provenance_examples"]) < 20:
            sections[sid]["provenance_examples"].append(example)

        material_id = material_id_for(solid)
        if material_id not in materials:
            correction = solid.get("property_correction", {})
            materials[material_id] = {
                "material_id": material_id,
                "name": solid.get("material") or "UNKNOWN",
                "scope": solid.get("material_scope_note") or solid.get("material_source") or "No material confirmed in CURRENT PRE5.",
                "elastic": {
                    "E_pa": {"value": None, "unit": "Pa", "status": "MISSING", "source": "Not inferred by PRE5."},
                    "nu": {"value": None, "unit": "1", "status": "MISSING", "source": "Not inferred by PRE5."},
                    "density_kg_m3": {"value": None, "unit": "kg/m3", "status": "MISSING", "source": "Not inferred by PRE5."},
                },
                "resistance": {
                    "concrete_fc_pa": {"value": solid.get("concrete_fc_pa"), "unit": "Pa", "status": "CONFIRMED" if solid.get("concrete_fc_pa") else "MISSING", "source": solid.get("material_source")},
                    "reinforcement_fy_pa": {"value": solid.get("reinforcement_fy_pa"), "unit": "Pa", "status": "CONFIRMED" if solid.get("reinforcement_fy_pa") else "MISSING", "source": solid.get("material_source")},
                    "reinforcement_grade": {"value": solid.get("reinforcement_grade"), "unit": "", "status": "CONFIRMED" if solid.get("reinforcement_grade") else "MISSING", "source": solid.get("material_source")},
                },
                "provenance": {
                    "material_source": solid.get("material_source"),
                    "material_confidence": solid.get("material_confidence"),
                    "primary_source": correction.get("primary_source"),
                    "handle": correction.get("handle"),
                    "source_sha256": correction.get("source_sha256"),
                },
            }

        geometry = geometry_for(solid)
        category = solid.get("category")
        owner = solid.get("id")
        if category in {"beam", "support"} and "start_m" in geometry:
            element_nodes = [
                ensure_node(geometry["start_m"], f"{category}_start", owner),
                ensure_node(geometry["end_m"], f"{category}_end", owner),
            ]
        elif category == "wall":
            element_nodes = [
                ensure_node(geometry["center_m"][:2] + [geometry["z_bottom_m"]], "wall_bottom_centroid", owner),
                ensure_node(geometry["center_m"][:2] + [geometry["z_top_m"]], "wall_top_centroid", owner),
            ]
        else:
            element_nodes = [
                ensure_node([geometry["center_m"][0], geometry["center_m"][1], geometry["z_bottom_m"]], f"{category}_bottom", owner),
                ensure_node([geometry["center_m"][0], geometry["center_m"][1], geometry["z_top_m"]], f"{category}_top", owner),
            ]

        analysis_refs = []
        for ref in fe_by_id.get(owner, []):
            analysis_refs.append({
                "analysis_id": ref.get("analysis_id"),
                "opensees_tag": ref.get("opensees_element_tag"),
                "node_i": ref.get("node_i"),
                "node_j": ref.get("node_j"),
                "geometry_segment_index": ref.get("geometry_segment_index", 0),
                "source": rel(FE_CANDIDATE),
                "status": "CANDIDATE_NOT_APPROVED_NOT_RUN",
            })

        common = {
            "element_id": owner,
            "solidTag": solid.get("solidTag"),
            "type": category,
            "building": solid.get("building"),
            "floor": solid.get("floor"),
            "nodes": element_nodes,
            "geometry": geometry,
            "section_id": sid,
            "material_id": material_id,
            "active": True,
            "analysis_id": analysis_refs[0]["analysis_id"] if len(analysis_refs) == 1 else None,
            "opensees_tag": analysis_refs[0]["opensees_tag"] if len(analysis_refs) == 1 else None,
            "analysis_refs": analysis_refs,
            "aliases": sorted(set(aliases_by_canonical.get(owner, []))),
            "merged_from": sorted(set(solid.get("merged_from", []) + aliases_by_canonical.get(owner, []))),
            "provenance": {
                "source_file": rel(GEOMETRY),
                "source_dxf": solid.get("source_dxf"),
                "source_layer": solid.get("source_layer"),
                "sourceTags": solid.get("sourceTags"),
                "confidence": solid.get("confidence"),
                "location_description": solid.get("location_description"),
                "axis_x": solid.get("axis_x"),
                "axis_y": solid.get("axis_y"),
            },
            "merge_history": [
                {
                    "type": item.get("type"),
                    "reason": item.get("reason"),
                    "source": item.get("source"),
                    "historical_ids": item.get("historical_ids"),
                    "gap_m": item.get("gap_m"),
                }
                for item in merge_history_by_id.get(owner, [])
            ],
        }
        if category == "support":
            common.update({
                "support_id": owner,
                "fixity": {"UX": True, "UY": True, "UZ": True, "RX": True, "RY": True, "RZ": True},
                "status": "GEOMETRIC_SUPPORT_CURRENT_PRE5; FE candidate supports are separate generated node constraints.",
            })
            supports.append(common)
        else:
            elements.append(common)

    # Preserve aliases and exclusions as non-editing traceability, not active elements.
    alias_rows = []
    for alias, canonical in sorted(exclusions.get("merged_id_aliases", {}).items()):
        alias_rows.append({
            "alias": alias,
            "canonical_element_id": canonical,
            "alias_active_as_element": alias in active_ids,
            "canonical_exists_in_current": canonical in active_ids,
            "source": rel(EXCLUSIONS),
        })

    pending = [row for row in readiness.get("pending_elements", []) if row.get("element_id") == "E2-P4-V-009"]
    pending_status = pending[0] if pending else None

    model_master = {
        "format": "MCOC_P1L5_MODEL_MASTER_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "CENTRAL_CANONICAL_INPUT_PROTOTYPE_DO_NOT_OVERWRITE_PRODUCTION",
        "units": {"length": "m", "force": "N", "stress": "Pa", "moment": "N.m", "rotation": "rad"},
        "sources": {
            "geometry_current_pre5": {"path": rel(GEOMETRY), "sha256": sha256(GEOMETRY)},
            "fe_candidate_not_run": {"path": rel(FE_CANDIDATE), "sha256": sha256(FE_CANDIDATE)},
            "current_contract": {"path": rel(CURRENT_CONTRACT), "status": current_contract.get("status"), "analysis_version": current_contract.get("analysis_version")},
            "exclusions_aliases": {"path": rel(EXCLUSIONS), "sha256": sha256(EXCLUSIONS)},
        },
        "modification_policy": {
            "no_reanalysis_required": [
                "Change linear combination coefficients of already analysed compatible basis cases.",
                "Move superposition sliders over existing verified results.",
                "Change visualization, layers, selection, filters, labels or camera.",
            ],
            "reanalysis_required": [
                "Change section_id or section properties.",
                "Change material_id or elastic material properties.",
                "Change support fixity or constraints.",
                "Activate or deactivate a structural element.",
                "Change nodes, connectivity or topology.",
                "Change physical load magnitudes, receivers or tributary areas.",
            ],
            "warning": "Changing a result-combination coefficient is not the same as changing the physical load model.",
        },
        "nodes": sorted(node_rows, key=lambda row: row["node_id"]),
        "elements": sorted(elements, key=lambda row: row["element_id"]),
        "supports": sorted(supports, key=lambda row: row["support_id"]),
        "aliases": alias_rows,
        "inactive_historical_exclusions": [
            {
                "element_id": row.get("element_id"),
                "reason": row.get("reason"),
                "removed_from_current_geometry": row.get("removed_from_current_geometry"),
                "removed_from_FE": row.get("removed_from_FE"),
                "source": rel(EXCLUSIONS),
            }
            for row in exclusions.get("exclusions", [])
        ],
        "current_pre5_identity": {
            "solid_count": len(all_solids),
            "category_counts": dict(Counter(s.get("category") for s in all_solids)),
            "fe_candidate_members": len(fe.get("elements", [])),
            "fe_candidate_nodes": len(fe.get("nodes", {})),
            "fe_candidate_supports": len(fe.get("supports", [])),
            "pending_case": {
                "element_id": "E2-P4-V-009",
                "status": "PENDING_FE_PATH_CURRENT_PRE5",
                "readiness_record": pending_status,
            },
        },
    }

    materials["MAT_FE_LINEAR_ELASTIC_P1L3_HISTORICAL"] = {
        "material_id": "MAT_FE_LINEAR_ELASTIC_P1L3_HISTORICAL",
        "name": "LINEAR_ELASTIC_FE_GLOBAL",
        "scope": "Historical P1L3/P1L4 results only; not CURRENT PRE5 material assignment.",
        "elastic": {
            "E_pa": {"value": 25.0e9, "unit": "Pa", "status": "HISTORICAL", "source": "entregas/P1L3/results/a3a4/analysis_model.json"},
            "nu": {"value": 0.20, "unit": "1", "status": "HISTORICAL", "source": "entregas/P1L3/results/a3a4/analysis_model.json"},
            "density_kg_m3": {"value": None, "unit": "kg/m3", "status": "MISSING", "source": "Not stored in FE material."},
        },
        "resistance": {},
        "provenance": {"status": "HISTORICAL_NOT_CURRENT"},
    }

    sections_json = {
        "format": "MCOC_P1L5_SECTIONS_V1",
        "generated_utc": model_master["generated_utc"],
        "source_geometry": rel(GEOMETRY),
        "sections": sorted(sections.values(), key=lambda row: row["section_id"]),
    }
    materials_json = {
        "format": "MCOC_P1L5_MATERIALS_V1",
        "generated_utc": model_master["generated_utc"],
        "source_catalog": rel(MATERIAL_CATALOG),
        "catalog_notes": material_catalog.get("notes", []),
        "materials": sorted(materials.values(), key=lambda row: row["material_id"]),
    }
    loads_json = {
        "format": "MCOC_P1L5_LOADS_V1",
        "generated_utc": model_master["generated_utc"],
        "current_status": "NO_CURRENT_APPLIED_LOAD_VECTOR",
        "base_cases": [
            {"case_id": "G", "description": "Permanent loads", "status": "HISTORICAL_BASE_EXISTS_NOT_CURRENT"},
            {"case_id": "Q", "description": "Live loads", "status": "HISTORICAL_BASE_EXISTS_NOT_CURRENT"},
            {"case_id": "EX", "description": "Pseudo-static earthquake X", "status": "HISTORICAL_BASE_EXISTS_NOT_CURRENT"},
            {"case_id": "EY", "description": "Pseudo-static earthquake Y", "status": "HISTORICAL_BASE_EXISTS_NOT_CURRENT"},
            {"case_id": "R", "description": "Linear combination", "status": "HISTORICAL_EXPLICIT_AND_SUPERPOSED"},
        ],
        "combinations": [{"combination_id": "R_P1L3_HISTORICAL", "status": "HISTORICAL", "coefficients": {"G": 1.2, "Q": 0.5, "EX": 1.0, "EY": 0.3}}],
        "audited_load_catalog": {
            "status": "AUDITED_NOT_APPLIED",
            "source": rel(LOAD_CATALOG),
            "source_status": load_catalog.get("status"),
            "entries": load_catalog.get("entries", []),
        },
        "tributary_areas": {
            "status": "HISTORICAL",
            "source": rel(PANOS),
            "panos": panos.get("panos", []),
            "coverage": panos.get("cobertura_por_piso", []),
            "parameters": panos.get("parametros", {}),
        },
        "historical_results_summary": {
            "status": "HISTORICAL_NOT_CURRENT",
            "source": rel(A7_REPORT),
            "gravity": a7.get("gravity"),
            "limitations": a7.get("limitations", []),
        },
        "modification_policy": model_master["modification_policy"],
    }

    write_json(HERE / "model_master.json", model_master)
    write_json(HERE / "sections.json", sections_json)
    write_json(HERE / "materials.json", materials_json)
    write_json(HERE / "loads.json", loads_json)
    print(json.dumps({
        "model_master": rel(HERE / "model_master.json"),
        "nodes": len(model_master["nodes"]),
        "elements": len(model_master["elements"]),
        "supports": len(model_master["supports"]),
        "sections": len(sections_json["sections"]),
        "materials": len(materials_json["materials"]),
        "load_entries": len(loads_json["audited_load_catalog"]["entries"]),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    build_central()
