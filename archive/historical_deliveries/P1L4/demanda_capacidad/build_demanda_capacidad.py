"""Genera el contrato P1L4 de demanda-capacidad desde resultados existentes.

No recalcula OpenSees y no modifica resultados historicos P1L3. La demanda se
extrae desde CASE_R para los tags definidos en elementos_estudio.json.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

ELEMENTS_STUDY = HERE / "elementos_estudio.json"
OUTPUT = HERE / "demanda_capacidad.json"

ANALYSIS_MODEL = ROOT / "entregas" / "P1L3" / "results" / "a3a4" / "analysis_model.json"
CASE_R_DIR = ROOT / "entregas" / "P1L3" / "results" / "a7" / "cases" / "R"
CASE_R_ELEMENTS = CASE_R_DIR / "elements.json"
CASE_R_MANIFEST = CASE_R_DIR / "manifest.json"
CAPACITY_DIR = ROOT / "entregas" / "P1L3" / "capacidad_ha"
COLUMN_PM = CAPACITY_DIR / "results" / "pm_interaction.csv"
WALL_SECTION_CONFIG = HERE / "datos" / "wall_section_estudio.json"
WALL_PM = HERE / "results" / "wall_pm_interaction.csv"

EXPECTED_CASE = "CASE_R"
FORCE_KEYS = ("P", "Vy", "Vz", "T", "My", "Mz")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"No existe fuente requerida: {rel(path)}")
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def as_number(value: str) -> Any:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return value


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"No existe CSV requerido: {rel(path)}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: as_number(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value == "True":
            return True
        if value == "False":
            return False
    raise ValueError(f"Valor booleano invalido: {value!r}")


def valid_capacity_status(status: str) -> bool:
    return status == "PASS" or status == "AXIAL_ONLY_PASS"


def column_pm_points(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = []
    for row in rows:
        status = str(row["status"])
        points.append({
            "point_id": str(row["case"]),
            "P_kN": float(row["axial_load_kN"]),
            "compression_magnitude_kN": float(row["compression_magnitude_kN"]),
            "M_kNm": float(row["max_moment_kNm"]),
            "curvature_at_M_1_per_m": float(row["curvature_at_max_1_per_m"]),
            "converged_steps": int(float(row["converged_steps"])),
            "valid": valid_capacity_status(status),
            "status": status,
        })
    return points


def wall_pm_points(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = []
    for row in rows:
        points.append({
            "point_id": str(row["point_id"]),
            "P_kN": float(row["P_kN"]),
            "compression_magnitude_kN": float(row["compression_magnitude_kN"]),
            "M_kNm": float(row["M_kNm"]),
            "curvature_at_M_1_per_m": float(row["curvature_at_M_1_per_m"]),
            "converged_steps": int(float(row["converged_steps"])),
            "requested_steps": int(float(row["requested_steps"])),
            "valid": parse_bool(row["valid"]),
            "status": str(row["status"]),
        })
    return points


def unwrap(item: Any) -> Any:
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    return item


def nested_value(config: dict[str, Any], *keys: str) -> Any:
    item: Any = config
    for key in keys:
        item = item[key]
    return unwrap(item)


def study_value(element: dict[str, Any], key: str) -> Any:
    if key not in element:
        raise KeyError(f"Elemento de estudio sin campo requerido: {key}")
    return unwrap(element[key])


def find_analysis_element(analysis_model: dict[str, Any], tag: int, element_id: str) -> dict[str, Any]:
    matches = [item for item in analysis_model["elements"] if int(item["opensees_element_tag"]) == tag]
    if len(matches) != 1:
        raise RuntimeError(f"Se esperaba exactamente un elemento con OpenSees tag {tag} en analysis_model.json; encontrados {len(matches)}")
    item = matches[0]
    if item["element_id"] != element_id:
        raise RuntimeError(f"Tag {tag} corresponde a {item['element_id']} en analysis_model.json, no a {element_id}")
    return item


def find_case_result(case_elements: dict[str, Any], tag: int, element_id: str) -> dict[str, Any]:
    tag_key = str(tag)
    matches = [key for key in case_elements if int(key) == tag]
    if len(matches) != 1:
        raise RuntimeError(f"Se esperaba exactamente el tag {tag} en CASE_R/elements.json; encontrados {len(matches)}")
    if matches[0] != tag_key:
        raise RuntimeError(f"Tag {tag} encontrado con clave inesperada {matches[0]}")
    row = case_elements[tag_key]
    if row.get("element_id") != element_id:
        raise RuntimeError(f"Tag {tag} en CASE_R corresponde a {row.get('element_id')}, no a {element_id}")
    for field in ("localForce_end1", "localForce_end2"):
        values = row.get(field)
        if not isinstance(values, list) or len(values) != 6:
            raise RuntimeError(f"{element_id} tag {tag} no tiene {field} con 6 componentes")
        if not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in values):
            raise RuntimeError(f"{element_id} tag {tag} contiene valores no finitos en {field}")
    return row


def force_dict(values: list[float]) -> dict[str, float]:
    return {key: float(value) for key, value in zip(FORCE_KEYS, values)}


def scaled_force_dict(values: dict[str, float]) -> dict[str, float]:
    return {
        "P_kN": values["P"] / 1000.0,
        "Vy_kN": values["Vy"] / 1000.0,
        "Vz_kN": values["Vz"] / 1000.0,
        "T_kNm": values["T"] / 1000.0,
        "My_kNm": values["My"] / 1000.0,
        "Mz_kNm": values["Mz"] / 1000.0,
    }


def envelope_abs(end1: dict[str, float], end2: dict[str, float]) -> dict[str, float]:
    return {key: max(abs(end1[key]), abs(end2[key])) for key in FORCE_KEYS}


def selected_end_for_pm(end1: dict[str, float], end2: dict[str, float], pm_component: str) -> str:
    if pm_component not in ("My", "Mz"):
        raise RuntimeError(f"pm_component invalido: {pm_component}")
    return "end1" if abs(end1[pm_component]) >= abs(end2[pm_component]) else "end2"


def interpolated_capacity_moment(points: list[dict[str, Any]], compression_kN: float) -> float | None:
    valid = sorted([point for point in points if point["valid"]], key=lambda point: point["compression_magnitude_kN"])
    if len(valid) < 2:
        return None
    if compression_kN < valid[0]["compression_magnitude_kN"] or compression_kN > valid[-1]["compression_magnitude_kN"]:
        return None
    for left, right in zip(valid, valid[1:]):
        p1 = left["compression_magnitude_kN"]
        p2 = right["compression_magnitude_kN"]
        if p1 <= compression_kN <= p2:
            if p2 == p1:
                return min(abs(left["M_kNm"]), abs(right["M_kNm"]))
            ratio = (compression_kN - p1) / (p2 - p1)
            return abs(left["M_kNm"]) + ratio * (abs(right["M_kNm"]) - abs(left["M_kNm"]))
    return None


def build_demand_capacity(demand: dict[str, Any], points: list[dict[str, Any]], pm_axis: str) -> dict[str, Any]:
    p_kN = float(demand["P_kN"])
    m_kNm = float(demand[f"{pm_axis}_kNm"])
    compression = abs(p_kN)
    demand_m_abs = abs(m_kNm)
    capacity_m = interpolated_capacity_moment(points, compression)
    inside = None if capacity_m is None else demand_m_abs <= capacity_m + 1.0e-9
    return {
        "case": demand["case_name"],
        "P_kN": p_kN,
        "compression_magnitude_kN": compression,
        "M_kNm": m_kNm,
        "M_abs_kNm": demand_m_abs,
        "pm_axis": pm_axis,
        "inside_envelope": inside,
        "interpolated_capacity_M_abs_kNm": capacity_m,
        "method": "Piecewise linear interpolation in |P|-M using only capacity points with valid=true; null if demand |P| is outside valid curve range.",
    }


def build_demand(case_row: dict[str, Any], case_name: str, pm_component: str) -> dict[str, Any]:
    end1_n = force_dict(case_row["localForce_end1"])
    end2_n = force_dict(case_row["localForce_end2"])
    selected = selected_end_for_pm(end1_n, end2_n, pm_component)
    selected_n = end1_n if selected == "end1" else end2_n
    env_n = envelope_abs(end1_n, end2_n)
    return {
        "case_name": case_name,
        "source_file": rel(CASE_R_ELEMENTS),
        "components_order": ["P", "Vy", "Vz", "T", "My", "Mz"],
        "selection_rule": f"selected end has maximum absolute {pm_component} for P-M demand display; both end forces are retained",
        "selected_end": selected,
        **scaled_force_dict(selected_n),
        "selected_end_forces_N_Nm": selected_n,
        "end_forces_N_Nm": {
            "end1": end1_n,
            "end2": end2_n,
        },
        "end_forces_kN_kNm": {
            "end1": scaled_force_dict(end1_n),
            "end2": scaled_force_dict(end2_n),
        },
        "envelope_abs_N_Nm": env_n,
        "envelope_abs_kN_kNm": scaled_force_dict(env_n),
        "pm_component": pm_component,
    }


def build_element(
    study_element: dict[str, Any],
    analysis_element: dict[str, Any],
    case_row: dict[str, Any],
    case_name: str,
    column_points: list[dict[str, Any]],
    wall_points: list[dict[str, Any]],
    wall_config: dict[str, Any],
) -> dict[str, Any]:
    element_id = study_value(study_element, "element_id")
    element_type = study_value(study_element, "type")
    tag = int(study_value(study_element, "opensees_tag"))
    nodes = list(study_value(study_element, "nodes"))
    capacity_info = study_element["capacity"]
    if element_type == "wall":
        pm_component = str(nested_value(wall_config, "geometry", "pm_axis"))
        points = wall_points
        capacity_source = rel(WALL_PM)
        capacity_status = "GENERATED_P1L4"
        capacity_note = "Curva P-M generada en P1L4 con geometria derivada y armadura ASUMIDO_LAB centralizada en wall_section_estudio.json."
        section_id = wall_config["section_id"]
        material = wall_config["materials"]
        reinforcement = wall_config["reinforcement"]
        capacity_origin = "DERIVADO"
    else:
        pm_component = "My"
        points = column_points
        capacity_source = capacity_info.get("source")
        capacity_status = capacity_info["status"]
        capacity_note = capacity_info.get("note")
        section_id = capacity_info.get("section_id") or f"{element_id}_capacity_missing"
        material = study_element["material"]
        reinforcement = study_element.get("reinforcement")
        capacity_origin = capacity_info["origin"]

    if case_row.get("node_i") != nodes[0] or case_row.get("node_j") != nodes[1]:
        raise RuntimeError(f"Nodos CASE_R de {element_id} no coinciden con elementos_estudio.json")
    if analysis_element.get("node_i") != nodes[0] or analysis_element.get("node_j") != nodes[1]:
        raise RuntimeError(f"Nodos analysis_model de {element_id} no coinciden con elementos_estudio.json")

    demand = build_demand(case_row, case_name, pm_component)
    demand_capacity = build_demand_capacity(demand, points, pm_component)

    return {
        "element_id": element_id,
        "structural_id": study_value(study_element, "structural_id"),
        "type": element_type,
        "opensees_tag": tag,
        "geometry_elementTag": study_value(study_element, "geometry_elementTag"),
        "analysis_id": study_value(study_element, "analysis_id"),
        "nodes": nodes,
        "node_coordinates": unwrap(study_element["node_coordinates"]),
        "section_id": section_id,
        "geometry": study_element["geometry"],
        "material": material,
        "reinforcement": reinforcement,
        "demand": demand,
        "capacity": {
            "status": capacity_status,
            "pm_axis": pm_component,
            "source": capacity_source,
            "note": capacity_note,
            "points": points,
            "invalid_points_note": "Los puntos con valid=false se conservan por trazabilidad y no se usan para interpolar la envolvente.",
        },
        "demand_capacity": demand_capacity,
        "capacity_section_input": wall_config if element_type == "wall" else None,
        "traceability": {
            "geometry_source": study_element["geometry_elementTag"]["source"],
            "analysis_source": rel(ANALYSIS_MODEL),
            "demand_source": rel(CASE_R_ELEMENTS),
            "capacity_source": capacity_source,
            "capacity_section_config": rel(WALL_SECTION_CONFIG) if element_type == "wall" else "entregas/P1L3/capacidad_ha/datos/seccion_estudio.json",
            "case_manifest": rel(CASE_R_MANIFEST),
        },
        "data_origins": {
            "element_id": study_element["element_id"]["origin"],
            "opensees_tag": study_element["opensees_tag"]["origin"],
            "geometry": "CONFIRMADO/DERIVADO segun campo en geometry",
            "material": "CONFIRMADO/DERIVADO/ASUMIDO_LAB segun campo en material",
            "capacity": capacity_origin,
            "demand": "DERIVADO",
        },
    }


def main() -> None:
    study = load_json(ELEMENTS_STUDY)
    analysis_model = load_json(ANALYSIS_MODEL)
    case_manifest = load_json(CASE_R_MANIFEST)
    case_elements = load_json(CASE_R_ELEMENTS)
    wall_config = load_json(WALL_SECTION_CONFIG)

    case_name = case_manifest.get("caso")
    if case_name != EXPECTED_CASE:
        raise RuntimeError(f"Se esperaba manifest caso {EXPECTED_CASE}; se obtuvo {case_name}")
    if unwrap(study.get("active_case")) != EXPECTED_CASE:
        raise RuntimeError(f"elementos_estudio.json no declara active_case {EXPECTED_CASE}")

    column_points = column_pm_points(read_csv_rows(COLUMN_PM))
    wall_points = wall_pm_points(read_csv_rows(WALL_PM))
    if not any(point["valid"] for point in wall_points):
        raise RuntimeError("La curva P-M del muro no tiene puntos validos")
    column_partial_points = [point for point in column_points if "PARTIAL" in point["status"] or "FAIL" in point["status"]]
    if not all(not point["valid"] for point in column_partial_points):
        raise RuntimeError("Hay puntos parciales/fallidos de columna marcados como validos")
    column_partial_status = "PASS"
    output_elements = []
    validations = []
    for study_element in study["elements"]:
        element_id = study_value(study_element, "element_id")
        tag = int(study_value(study_element, "opensees_tag"))
        analysis_element = find_analysis_element(analysis_model, tag, element_id)
        case_row = find_case_result(case_elements, tag, element_id)
        output_elements.append(build_element(study_element, analysis_element, case_row, case_name, column_points, wall_points, wall_config))
        validations.append({
            "element_id": element_id,
            "opensees_tag": tag,
            "analysis_model_unique_tag": "PASS",
            "case_result_unique_tag": "PASS",
            "case_result_available": "PASS",
            "force_components_available": "PASS",
            "nodes_match_study": "PASS",
        })

    expected_tags = {10009, 10171}
    actual_tags = {item["opensees_tag"] for item in output_elements}
    if actual_tags != expected_tags:
        raise RuntimeError(f"Tags generados {sorted(actual_tags)} no coinciden con esperados {sorted(expected_tags)}")

    bundle = {
        "format": "P1L4_UNITY_DEMAND_CAPACITY_v1",
        "active_case": EXPECTED_CASE,
        "units": {
            "length": "m",
            "force": "kN",
            "moment": "kN.m",
            "source_force": "N",
            "source_moment": "N.m"
        },
        "source_of_truth": {
            "elements_study": rel(ELEMENTS_STUDY),
            "analysis_model": rel(ANALYSIS_MODEL),
            "case_manifest": rel(CASE_R_MANIFEST),
            "case_results": rel(CASE_R_ELEMENTS),
            "column_capacity_pm": rel(COLUMN_PM),
            "wall_section_config": rel(WALL_SECTION_CONFIG),
            "wall_capacity_pm": rel(WALL_PM),
        },
        "validation": {
            "status": "PASS",
            "required_tags": sorted(expected_tags),
            "column_partial_points_marked_invalid": column_partial_status,
            "wall_valid_pm_points": len([point for point in wall_points if point["valid"]]),
            "wall_invalid_pm_points": len([point for point in wall_points if not point["valid"]]),
            "checks": validations,
        },
        "elements": output_elements,
    }
    write_json(OUTPUT, bundle)

    print("VALIDATION: PASS")
    print(f"Output: {rel(OUTPUT)}")
    for element in output_elements:
        demand = element["demand"]
        print(
            f"{element['type']} {element['opensees_tag']} {element['element_id']} "
            f"case={demand['case_name']} selected={demand['selected_end']} "
            f"P={demand['P_kN']:.6f} kN My={demand['My_kNm']:.6f} kNm Mz={demand['Mz_kNm']:.6f} kNm "
            f"pm_axis={element['capacity']['pm_axis']} inside={element['demand_capacity']['inside_envelope']} "
            f"source={demand['source_file']}"
        )


if __name__ == "__main__":
    main()
