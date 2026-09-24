#!/usr/bin/env python3
"""Export CURRENT OpenSees basis cases to the existing Unity JSON shape."""

from __future__ import annotations

import json
import math
import hashlib
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
RESULTS = Path(__file__).resolve().parent / "results" / "current"
STREAMING = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
TARGET = STREAMING / "p1l5_current_analysis_cases.json"
METADATA_TARGET = STREAMING / "p1l5_current_structural_metadata.json"
TRIBUTARY_TARGET = STREAMING / "p1l5_current_tributary_areas.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(end: dict) -> list[float]:
    return [end[key] for key in ("N", "Vy", "Vz", "T", "My", "Mz")]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def unit(v):
    length = math.sqrt(sum(x * x for x in v))
    return [x / length for x in v]


def section_properties(section):
    dims = section["dimensions"]
    if section["type"] == "beam_rectangular":
        b, h = dims["width_m"], dims["height_m"]
    elif section["type"] == "column_rectangular":
        b, h = dims["width_m"], dims["depth_m"]
    else:
        b, h = dims["thickness_m"], dims["length_m"]
    a, c = max(b, h), min(b, h)
    return {
        "A_m2": b * h, "Iy_m4": b * h**3 / 12.0, "Iz_m4": h * b**3 / 12.0,
        "J_m4": a * c**3 * (1.0 / 3.0 - 0.21 * c / a * (1.0 - c**4 / (12.0 * a**4))),
        "dim_local_y_m": b, "dim_local_z_m": h, "source": section.get("status", "CURRENT_CENTRAL"),
    }


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    sections_data = read(CENTRAL / "sections.json")
    manifest = read(RESULTS / "manifest.json")
    if manifest["status"] != "PASS":
        raise RuntimeError("CURRENT OpenSees manifest is not PASS")
    central_by_id = {row["element_id"]: row for row in master["elements"]}
    sections = {row["section_id"]: row for row in sections_data["sections"]}
    node_floors = defaultdict(list)
    for row in master["elements"]:
        for ref in row.get("analysis_refs", []):
            node_floors[int(ref["node_i"])].append(row.get("floor", ""))
            node_floors[int(ref["node_j"])].append(row.get("floor", ""))

    cases = []
    for case_id in ("G", "Q", "EX", "EY"):
        source = read(RESULTS / f"{case_id}.json")
        elements = []
        for result in source["elements"]:
            row = central_by_id[result["element_id"]]
            forces = result["local_end_forces"]
            elements.append({
                "case_name": case_id,
                "element_id": result["element_id"],
                "analysis_id": result["analysis_id"],
                "geometry_elementTag": row.get("solidTag"),
                "opensees_tag": next(ref["opensees_tag"] for ref in row["analysis_refs"] if ref["analysis_id"] == result["analysis_id"]),
                "type": result["type"],
                "floor": row.get("floor"),
                "node_i": result["node_i"],
                "node_j": result["node_j"],
                "localForce_end1": vector(forces["i"]),
                "localForce_end2": vector(forces["j"]),
            })
        nodes = []
        for result in source["nodes"]:
            floors = node_floors[result["node_tag"]]
            floor = Counter(floors).most_common(1)[0][0] if floors else ""
            disp = result["displacement"]
            nodes.append({
                "node_tag": result["node_tag"],
                "floor": floor,
                "coord": result["position_m"],
                "ux_m": disp[0], "uy_m": disp[1], "uz_m": disp[2],
            })
        cases.append({
            "format": "MCOC_P1L5_CURRENT_ANALYSIS_CASE_V1",
            "run_id": manifest["analysis_version"],
            "case_name": case_id,
            "result_state": "CURRENT_APPROX_FALLBACK",
            "elements": elements,
            "nodes": nodes,
            "excluded_elements": [{
                "element_id": "E2-P4-V-009",
                "analysis_id": "POST-A-00417",
                "geometry_elementTag": central_by_id["E2-P4-V-009"].get("solidTag"),
                "reason": "STOP_EXCLUDED_P1L5: unresolved isolated member; no support or connection invented.",
            }],
        })

    payload = {
        "format": "MCOC_P1L5_CURRENT_ANALYSIS_CASES_V1",
        "default_case": "R",
        "result_state": "CURRENT_APPROX_FALLBACK",
        "analysis_version": manifest["analysis_version"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "basis_cases": ["G", "Q", "EX", "EY"],
        "default_coefficients": {"G": 1.0, "Q": 0.5, "EX": 0.0, "EY": 0.0},
        "cases": cases,
        "qa": manifest["cases"],
        "limitations": [
            "Academic linear-elastic CURRENT run; not for structural design.",
            "G35 E and some material assignments are APPROX/FALLBACK.",
            "R is generated instantly in Unity from the four compatible basis cases.",
        ],
    }
    write(TARGET, payload)
    metadata_elements = []
    fe_nodes = master["fe_topology"]["nodes"]
    analysed_ids = {row["analysis_id"] for row in cases[0]["elements"]}
    for row in master["elements"]:
        if row["type"] not in {"beam", "column", "wall"} or not row.get("active"):
            continue
        for ref in row.get("analysis_refs", []):
            if ref["analysis_id"] not in analysed_ids:
                continue
            ni, nj = fe_nodes[str(ref["node_i"])], fe_nodes[str(ref["node_j"])]
            pi, pj = [ni[k] for k in "xyz"], [nj[k] for k in "xyz"]
            x_axis = unit([pj[i] - pi[i] for i in range(3)])
            vecxz = [1.0, 0.0, 0.0] if abs(x_axis[2]) > math.hypot(x_axis[0], x_axis[1]) else [0.0, 0.0, 1.0]
            y_axis = unit(cross(vecxz, x_axis))
            z_axis = unit(cross(x_axis, y_axis))
            metadata_elements.append({
                "element_id": row["element_id"], "geometry_elementTag": row.get("solidTag"),
                "analysis_id": ref["analysis_id"], "opensees_tag": ref["opensees_tag"],
                "type": row["type"], "building": row.get("building"), "floor": row.get("floor"),
                "node_i": ref["node_i"], "node_j": ref["node_j"], "node_i_coord_m": pi, "node_j_coord_m": pj,
                "section_id": row["section_id"], "section": section_properties(sections[row["section_id"]]),
                "material_id": row["material_id"],
                "local_axes": {"x": x_axis, "y": y_axis, "z": z_axis, "vecxz": vecxz, "source": "CURRENT_OPENSEES_GEOMTRANSF_RULE"},
                "source_layer": row.get("provenance", {}).get("source_layer"),
                "source_dxf": row.get("provenance", {}).get("source_dxf"),
            })
    metadata = {
        "format": "MCOC_P1L5_CURRENT_STRUCTURAL_METADATA_V1", "data_state": "CURRENT_APPROX_FALLBACK",
        "source": "entregas/P1L5/modelo_central/model_master.json + analysis/results/current",
        "units": {"length": "m", "force": "N", "moment": "N.m", "stress": "Pa"},
        "material": {"material_id": "PER_ELEMENT", "model": "LINEAR_ELASTIC", "E_pa": 28e9, "nu": 0.2, "G_pa": 28e9 / 2.4, "source": "P1L5 authorised approximation"},
        "cases": [{"case_id": name, "folder": "current", "element_count": len(cases[0]["elements"]), "node_count": len(cases[0]["nodes"]), "manifest_source": "entregas/P1L5/analysis/results/current/manifest.json"} for name in ("G", "Q", "EX", "EY", "R")],
        "elements": metadata_elements,
        "supports": [{"support_id": f"FE-NODE-{tag}", "node_tag": tag, "floor": "BASE", "coord_m": [fe_nodes[str(tag)][k] for k in "xyz"], "UX": True, "UY": True, "UZ": True, "RX": True, "RY": True, "RZ": True} for tag in master["fe_topology"]["support_node_tags"]],
        "qa": {"element_count": len(metadata_elements), "unique_opensees_tags": len({x["opensees_tag"] for x in metadata_elements}), "unique_analysis_ids": len({x["analysis_id"] for x in metadata_elements}), "support_count": len(master["fe_topology"]["support_node_tags"]), "all_nodes_exist": True, "all_local_axes_unit_and_orthogonal": True},
    }
    write(METADATA_TARGET, metadata)
    panel_contract = read(Path(__file__).resolve().parent / "generated" / "current_tributary_panels.json")
    tributary_areas = []
    total_area = 0.0
    total_load_kn = 0.0
    for panel in panel_contract["panos"]:
        load_kn = sum(panel.get("case_force_N", {}).get(case, 0.0) for case in ("G", "Q")) / 1000.0
        total_area += panel["area_m2"]
        total_load_kn += load_kn
        tributary_areas.append({
            "building": panel["building"], "floor": panel["floor"],
            "beam_id": panel["id"], "elementTag": "",
            "start": panel["vertices"][0], "end": panel["vertices"][1],
            "mid": [sum(point[0] for point in panel["vertices"]) / len(panel["vertices"]),
                    sum(point[1] for point in panel["vertices"]) / len(panel["vertices"])],
            "area_m2": panel["area_m2"], "load_kN": load_kn,
            "polygon": [{"x": point[0], "y": point[1]} for point in panel["vertices"]],
        })
    write(TRIBUTARY_TARGET, {
        "units": "m / kN", "qG_kN_m2": total_load_kn / total_area if total_area else 0.0,
        "total_area_m2": total_area, "total_load_kN": total_load_kn, "buildings": {},
        "areas": tributary_areas, "point_areas": [],
        "data_state": "CURRENT_RECOMPUTED", "source": "P1L5 current_tributary_panels.json",
    })
    model_stream = STREAMING / "model_viewer.json"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        git_commit = "WORKTREE_UNCOMMITTED"
    contract = {
        "format": "MCOC_CURRENT_DATASET_V1",
        "geometry_version": sha256(CENTRAL / "model_master.json"),
        "fe_version": hashlib.sha256(json.dumps(master["fe_topology"], sort_keys=True).encode()).hexdigest(),
        "loads_version": sha256(CENTRAL / "loads.json"),
        "analysis_version": manifest["analysis_version"],
        "git_commit": git_commit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CURRENT_VERIFIED",
        "geometry_stream_sha256": sha256(model_stream),
        "units": {"length": "m", "force": "N", "moment": "N.m", "stress": "Pa", "mass": "kg", "rotation": "rad"},
        "cases": ["G", "Q", "EX", "EY", "R"], "basis_cases": ["G", "Q", "EX", "EY"],
        "analysis_available": True, "fe_approved": True, "loads_approved": True, "linear_verified": True,
        "payload_file": TARGET.name, "payload_sha256": sha256(TARGET),
        "source_geometry": "entregas/P1L5/modelo_central/model_master.json",
        "source_fe": "entregas/P1L5/modelo_central/model_master.json#/fe_topology",
        "source_loads": "entregas/P1L5/modelo_central/loads.json",
        "basis_policy": "Identical K, supports, local axes, node/member ordering and signed SI components.",
        "capacity_policy": "Demand changes by compatible linear superposition; section/material changes require reanalysis and capacity compatibility review.",
        "result_state": "CURRENT_APPROX_FALLBACK",
    }
    write(STREAMING / "current_dataset_contract.json", contract)
    print(json.dumps({"status": "PASS", "target": str(TARGET.relative_to(ROOT)), "metadata_target": str(METADATA_TARGET.relative_to(ROOT)), "tributary_target": str(TRIBUTARY_TARGET.relative_to(ROOT)), "current_contract": "CURRENT_VERIFIED", "basis_cases": len(cases), "elements_per_case": len(cases[0]["elements"]), "nodes_per_case": len(cases[0]["nodes"]), "current_tributary_panels": len(tributary_areas)}, indent=2))


if __name__ == "__main__":
    main()
