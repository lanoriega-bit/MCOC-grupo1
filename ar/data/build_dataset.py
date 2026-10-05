#!/usr/bin/env python3
"""Build the precomputed CURRENT element dataset for the future P1L6 AR client."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CENTRAL = ROOT / "model"
PROJECT = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8-sig"))
STREAM = ROOT / PROJECT["paths"]["unity"] / "Assets" / "StreamingAssets"
STREAM_OUT = STREAM / "p1l6_current_ar_elements.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unity(point: list[float]) -> list[float]:
    # The Unity viewer rotates the model root -90 degrees around global X.
    return [round(point[0], 6), round(point[2], 6), round(-point[1], 6)]


def direction(start: list[float], end: list[float]) -> list[float]:
    delta = [end[i] - start[i] for i in range(3)]
    length = math.sqrt(sum(value * value for value in delta))
    return [round(value / length, 8) for value in delta] if length else [0.0, 0.0, 0.0]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combine(values: list[list[float]], coefficients: list[float]) -> list[float]:
    return [sum(coefficients[k] * values[k][i] for k in range(4)) for i in range(len(values[0]))]


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    sections = {row["section_id"]: row for row in read(CENTRAL / "sections.json")["sections"]}
    materials = {row["material_id"]: row for row in read(CENTRAL / "materials.json")["materials"]}
    cases = read(STREAM / "p1l5_current_analysis_cases.json")
    capacity = read(STREAM / "p1l6_current_capacity.json")
    loads = read(STREAM / "p1l5_current_loads_by_element.json")
    basis_names = ["G", "Q", "EX", "EY"]
    coefficients = [float(cases["default_coefficients"][name]) for name in basis_names]
    by_case = {row["case_name"]: row for row in cases["cases"]}
    force_by_case = {
        name: {row["analysis_id"]: row for row in by_case[name]["elements"]}
        for name in basis_names
    }
    node_by_case = {
        name: {int(row["node_tag"]): row for row in by_case[name]["nodes"]}
        for name in basis_names
    }
    capacity_by_id = {row["element_id"]: row for row in capacity["elements"]}
    loads_by_id = {row["element_id"]: row for row in loads["elements"]}
    fe_coords = {
        int(tag): [float(coord["x"]), float(coord["y"]), float(coord["z"])]
        for tag, coord in master["fe_topology"]["nodes"].items()
    }

    results_by_element = defaultdict(list)
    for element in master["elements"]:
        for ref in element.get("analysis_refs", []):
            if not all(ref["analysis_id"] in force_by_case[name] for name in basis_names):
                continue
            rows = [force_by_case[name][ref["analysis_id"]] for name in basis_names]
            results_by_element[element["element_id"]].append({
                "analysis_id": ref["analysis_id"],
                "opensees_tag": ref["opensees_tag"],
                "node_i": ref["node_i"], "node_j": ref["node_j"],
                "localForce_end1_N_Nm": combine([row["localForce_end1"] for row in rows], coefficients),
                "localForce_end2_N_Nm": combine([row["localForce_end2"] for row in rows], coefficients),
            })

    records = []
    for row in master["elements"] + master["supports"]:
        geometry = row["geometry"]
        start = geometry.get("start_m")
        end = geometry.get("end_m")
        center = geometry.get("center_m")
        if start is None and center is not None and "z_bottom_m" in geometry:
            start = [center[0], center[1], geometry["z_bottom_m"]]
            end = [center[0], center[1], geometry["z_top_m"]]
        refs = row.get("analysis_refs", [])
        fe_tags = sorted({int(ref[key]) for ref in refs for key in ("node_i", "node_j")})
        displacement_rows = []
        for tag in fe_tags:
            if not all(tag in node_by_case[name] for name in basis_names):
                continue
            vectors = [[node_by_case[name][tag][key] for key in ("ux_m", "uy_m", "uz_m")] for name in basis_names]
            disp = combine(vectors, coefficients)
            displacement_rows.append({
                "node_tag": tag, "model_coord_m": fe_coords.get(tag), "unity_coord_m": unity(fe_coords[tag]) if tag in fe_coords else None,
                "displacement_model_m": disp, "displacement_unity_m": unity(disp),
                "magnitude_m": math.sqrt(sum(value * value for value in disp)),
            })
        record = {
            "element_id": row["element_id"],
            "elementTag": row["element_id"],
            "solidTag": row.get("solidTag"),
            "opensees_tags": [ref["opensees_tag"] for ref in refs],
            "future_ar_elementTag": row["element_id"],
            "type": row["type"], "building": row.get("building"), "floor": row.get("floor"),
            "physical_nodes": row.get("nodes", []), "fe_node_tags": fe_tags,
            "model_coordinates_m": {"start": start, "end": end, "center": center},
            "unity_coordinates_m": {
                "start": unity(start) if start else None,
                "end": unity(end) if end else None,
                "center": unity(center) if center else None,
            },
            "orientation_model": direction(start, end) if start and end else [0.0, 0.0, 1.0],
            "orientation_unity": direction(unity(start), unity(end)) if start and end else [0.0, 1.0, 0.0],
            "length_m": math.dist(start, end) if start and end else max(0.0, geometry.get("z_top_m", 0) - geometry.get("z_bottom_m", 0)),
            "geometry": geometry,
            "dimensions": sections.get(row.get("section_id"), {}).get("dimensions", {}),
            "geometry_measure_note": "Physical axis endpoints: wall length is its plan axis, not the height of its equivalent FE column. FE coordinates are separate in current_result_R.node_displacements.",
            "section": sections.get(row.get("section_id")),
            "material": materials.get(row.get("material_id")),
            "current_result_R": {
                "coefficients": dict(zip(basis_names, coefficients)),
                "segments": results_by_element.get(row["element_id"], []),
                "node_displacements": displacement_rows,
            },
            "capacity": capacity_by_id.get(row["element_id"]),
            "load_and_tributary": loads_by_id.get(row["element_id"]),
            "aliases": row.get("aliases", []), "merged_from": row.get("merged_from", []),
            "data_state": "CURRENT_VERIFIED" if refs else "CURRENT_GEOMETRY_NO_FE_RESULT",
        }
        records.append(record)

    demos = []
    for element_id, purpose in (
        ("E2-P1-C-002", "Columna 70x70 con P-M My/Mz y demanda CURRENT"),
        ("E2-P1-V-032", "Viga con P/V/M, tributaria/carga y capacidad My/Mz/Vy/Vz"),
    ):
        record = next(row for row in records if row["element_id"] == element_id)
        demos.append({
            "element_id": element_id, "purpose": purpose,
            "has_results": bool(record["current_result_R"]["segments"]),
            "has_capacity": record["capacity"] is not None,
            "has_load_contract": record["load_and_tributary"] is not None,
        })

    output = {
        "format": "MCOC_P1L6_AR_CURRENT_ELEMENTS_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY_PRECOMPUTED_PHONE_DOES_NOT_RUN_OPENSEES",
        "units": {"length": "m", "force": "N", "moment": "N.m", "rotation": "rad"},
        "identity_chain": "element_id -> solidTag -> OpenSees opensees_tag(s) -> future_ar_elementTag",
        "coordinate_transform": {
            "model_to_unity": "[x,y,z] -> [x,z,-y] (root rotation Rx=-90deg)",
            "unity_to_model": "[X,Y,Z] -> [X,-Z,Y]",
            "unity_to_ar": "p_AR = T_anchor * S_calibration * p_Unity; pose/anchor is solved on phone",
        },
        "sources": {
            "geometry": "entregas/P1L5/modelo_central/model_master.json",
            "analysis": "p1l5_current_analysis_cases.json",
            "capacity": "p1l6_current_capacity.json",
            "loads": "p1l5_current_loads_by_element.json",
        },
        "hashes": {
            "model_master_sha256": sha(CENTRAL / "model_master.json"),
            "analysis_sha256": sha(STREAM / "p1l5_current_analysis_cases.json"),
            "capacity_sha256": sha(STREAM / "p1l6_current_capacity.json"),
            "loads_sha256": sha(STREAM / "p1l5_current_loads_by_element.json"),
        },
        "demo_elements": demos,
        "summary": {"records": len(records), "with_fe_results": sum(bool(row["current_result_R"]["segments"]) for row in records), "with_capacity": sum(row["capacity"] is not None for row in records)},
        "elements": records,
    }
    write(STREAM_OUT, output)
    print(json.dumps({"status": output["status"], "summary": output["summary"], "demo_elements": demos}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
