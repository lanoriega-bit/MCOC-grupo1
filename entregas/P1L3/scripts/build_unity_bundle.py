"""Construye el paquete P1L3 que consume Unity desde las fuentes vigentes.

No recalcula OpenSees. Conserva los resultados originales y genera adaptadores
planos que ``JsonUtility`` puede leer sin diccionarios con claves dinamicas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
P1L3 = ROOT / "entregas" / "P1L3"
UNITY = P1L3 / "José" / "viewer_unity"
STREAMING = UNITY / "Assets" / "StreamingAssets"

GEOMETRY = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
ANALYSIS_MODEL = P1L3 / "results" / "a3a4" / "analysis_model.json"
FE_CANDIDATE = P1L3 / "results" / "post_p1l3_candidate" / "analysis_model_post_p1l3_candidate.json"
CONNECTIVITY_AUDIT = (
    ROOT
    / "entregas"
    / "P1L2"
    / "edificio"
    / "validacion"
    / "fe_connectivity_post_geometry"
    / "connectivity_comparison.json"
)
RUN_DIR = P1L3 / "results" / "a5" / "superposicion_gq_v1"
A5_REPORT = P1L3 / "results" / "a5" / "a5_report.json"
A7_DIR = P1L3 / "results" / "a7"
A7_REPORT = A7_DIR / "a7_report.json"
SEISMIC = P1L3 / "José" / "results" / "seismic_ex_ey.json"
CAPACITY_DIR = P1L3 / "capacidad_ha"
ARCHITECTURE = P1L3 / "arquitectura" / "architectural_visual_model.json"
LEGACY_P1 = ROOT / "entregas" / "P1L2" / "edificio" / "datos" / "piso_01.json"


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_compact_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str):
    if value in (None, ""):
        return None
    if value in ("True", "False"):
        return value == "True"
    try:
        return float(value)
    except ValueError:
        return value


def typed_rows(rows: list[dict]) -> list[dict]:
    return [{key: number(value) for key, value in row.items()} for row in rows]


def pm_rows(rows: list[dict]) -> list[dict]:
    converted = typed_rows(rows)
    for row in converted:
        row["case_name"] = row.pop("case")
    return converted


def validate_geometry(model: dict) -> None:
    floors = set(model.get("expectedFloors", []))
    assert floors == {"S1", "P1", "P2", "P3", "P4"}, floors
    solids = model.get("solids", [])
    assert solids, "La geometria vigente no contiene solidos"
    ids = [item.get("id") for item in solids]
    assert all(ids), "Hay solidos sin id publico"
    assert len(ids) == len(set(ids)), "IDs publicos duplicados"
    assert {item.get("building") for item in solids} == {"EDIFICIO_1", "EDIFICIO_2"}
    assert {item.get("category") for item in solids} >= {
        "beam", "column", "wall", "support", "slab"
    }


def visual_lines_for_unity(model: dict) -> dict:
    """Crea un adaptador pequeno para las listas anidadas que JsonUtility no admite."""
    data = {"format": "P1L3_UNITY_VISUAL_LINES_v1", "units": model.get("units", "m")}
    for collection in ("segments", "diaphragms"):
        data[collection] = []
        for source in model.get(collection, []):
            item = {key: value for key, value in source.items() if key != "points"}
            item["points_flat"] = [coordinate for point in source.get("points", []) for coordinate in point]
            data[collection].append(item)
    return data


def build_fe_diagnostic(candidate: dict, audit: dict) -> dict:
    """Adapta el candidato topologico a listas planas legibles por JsonUtility.

    No decide conectividad nueva: transporta la validacion del candidato, el
    diagnostico previo y el crosswalk 1:N a la interfaz.
    """
    validation_by_id = {
        row["element_id"]: row for row in candidate["connectivity_validation"]
    }
    audit_by_id = {
        row["element_id"]: row
        for row in audit["current_floating_classification"]["elements"]
    }
    crosswalk_by_id: dict[str, list[dict]] = {}
    for row in candidate["crosswalk"]:
        crosswalk_by_id.setdefault(row["element_id"], []).append(row)
    component_by_id = {}
    for component in candidate["floating_excluded"]["components"]:
        for element_id in component["geometry_element_ids"]:
            component_by_id[element_id] = component["component_id"]
    connection_by_id: dict[str, list[dict]] = {}
    for connection in candidate["junction_connections"]:
        for element_id in (connection.get("geometry_a"), connection.get("geometry_b")):
            if element_id:
                connection_by_id.setdefault(element_id, []).append(connection)

    expectation_by_type = {
        "wall": "interseccion/solape fisico con muro o viga del mismo edificio y nivel",
        "beam": "incidencia fisica con viga, columna o muro; un extremo libre solo si es voladizo real",
        "column": "continuidad vertical o transferencia demostrada hacia viga/muro",
    }
    elements = []
    for element_id in sorted(crosswalk_by_id):
        mapped = crosswalk_by_id[element_id][0]
        row = validation_by_id.get(element_id, {
            "element_id": element_id,
            "type": mapped["type"],
            "building": mapped["building"],
            "floor": mapped["floor"],
            "structural_classification": "NOT_IN_FOCUS",
            "validation": "NOT_IN_FOCUS",
            "connected_in_candidate": element_id not in component_by_id,
        })
        audit_row = audit_by_id.get(element_id, {})
        links = connection_by_id.get(element_id, [])
        link_types = sorted({item.get("type", "") for item in links if item.get("type")})
        evidence = sorted({item.get("evidence", "") for item in links if item.get("evidence")})
        validation = row["validation"]
        if validation == "CONNECTED_EXPECTED":
            motive = "El adaptador candidato recupera la trayectoria esperada mediante encuentros fisicos."
        elif validation == "FREE_END_EXPECTED":
            motive = "La geometria confirma un voladizo real: un extremo libre es intencional."
        elif validation == "DISCONNECTED_ERROR":
            motive = "La geometria esta confirmada, pero el candidato aun no obtiene trayectoria a apoyo."
        elif validation == "UNRESOLVED":
            motive = "La interpretacion estructural sigue pendiente; no se crea una conexion artificial."
        else:
            motive = "Elemento fuera del foco de 72 casos heredados; se muestra para inspeccionar la malla candidata."
        elements.append(
            {
                **row,
                "diagnostic_focus": element_id in validation_by_id,
                "component_id": component_by_id.get(element_id, "SUPPORTED_COMPONENT"),
                "motive": motive,
                "expected_connection": expectation_by_type.get(row["type"], "conexion estructural demostrada"),
                "evidence": "; ".join(evidence) if evidence else audit_row.get("geometry_confidence", "sin evidencia adicional"),
                "connection_types": link_types,
                "source_dxf": audit_row.get("source_dxf", ""),
                "source_layer": audit_row.get("source_layer", ""),
                "prior_diagnosis": audit_row.get("preliminary_diagnosis", ""),
                "crosswalk": sorted(
                    crosswalk_by_id.get(element_id, []),
                    key=lambda item: item["geometry_segment_index"],
                ),
            }
        )

    nodes = candidate["nodes"]
    members = []
    for member in candidate["elements"]:
        diagnostic = validation_by_id.get(member["element_id"])
        ni = nodes[str(member["node_i"])]
        nj = nodes[str(member["node_j"])]
        members.append(
            {
                **member,
                "diagnostic_focus": diagnostic is not None,
                "validation": diagnostic["validation"] if diagnostic else "NOT_IN_FOCUS",
                "start": [ni["x"], ni["y"], ni["z"]],
                "end": [nj["x"], nj["y"], nj["z"]],
            }
        )

    return {
        "format": "POST_P1L3_UNITY_FE_DIAGNOSTIC_v1",
        "status": candidate["status"],
        "source_candidate": str(FE_CANDIDATE.relative_to(ROOT)).replace("\\", "/"),
        "summary": {
            **candidate["qa"],
            "focus_elements": len(validation_by_id),
            "mapped_geometry_elements": len(elements),
        },
        "elements": elements,
        "members": members,
    }


def build_analysis_results(analysis: dict, run_dir: Path) -> dict:
    manifest = load_json(run_dir / "manifest.json")
    elements = load_json(run_dir / "elements.json")
    nodes = load_json(run_dir / "nodes.json")
    excluded_block = analysis.get("floating_excluded", {})
    excluded_rows = excluded_block.get("elementos", []) if isinstance(excluded_block, dict) else excluded_block
    crosswalk_by_id = {
        item.get("element_id"): item
        for item in analysis.get("crosswalk", [])
        if item.get("element_id")
    }
    excluded = {
        item.get("element_id"): item
        for item in excluded_rows
        if item.get("element_id")
    }
    rows = []
    for opensees_tag, result in elements.items():
        rows.append(
            {
                "case_name": manifest["caso"],
                "element_id": result.get("element_id"),
                "analysis_id": result.get("analysis_id"),
                "geometry_elementTag": result.get("geometry_elementTag"),
                "opensees_tag": int(opensees_tag),
                "type": result.get("type"),
                "floor": result.get("floor"),
                "node_i": result.get("node_i"),
                "node_j": result.get("node_j"),
                "localForce_end1": result.get("localForce_end1", []),
                "localForce_end2": result.get("localForce_end2", []),
            }
        )

    return {
        "format": "P1L3_UNITY_ANALYSIS_v1",
        "run_id": manifest["run_id"],
        "case_name": manifest["caso"],
        "units": manifest["unidades"],
        "elements": rows,
        "nodes": [
            {
                "node_tag": int(tag),
                "floor": result.get("floor"),
                "coord": result.get("coord", []),
                "ux_m": result.get("ux_m", 0.0),
                "uy_m": result.get("uy_m", 0.0),
                "uz_m": result.get("uz_m", 0.0),
            }
            for tag, result in nodes.items()
        ],
        "excluded_elements": [
            {
                "element_id": key,
                "analysis_id": value.get("analysis_id"),
                "geometry_elementTag": crosswalk_by_id.get(key, {}).get("geometry_elementTag"),
                "reason": excluded_block.get("motivo", "componente sin trayectoria a apoyo")
                if isinstance(excluded_block, dict)
                else "componente sin trayectoria a apoyo",
            }
            for key, value in sorted(excluded.items())
        ],
    }


def build_analysis_cases(analysis: dict) -> dict:
    return {
        "format": "P1L3_UNITY_ANALYSIS_CASES_v1",
        "default_case": "R",
        "cases": [
            build_analysis_results(analysis, A7_DIR / "cases" / case_name)
            for case_name in ("G", "Q", "EX", "EY", "R")
        ],
    }


def _find_legacy(root, wanted_id):
    if isinstance(root, dict):
        if root.get("id") == wanted_id:
            return root
        for value in root.values():
            found = _find_legacy(value, wanted_id)
            if found is not None:
                return found
    elif isinstance(root, list):
        for value in root:
            found = _find_legacy(value, wanted_id)
            if found is not None:
                return found
    return None


def build_capacity(geometry_model: dict, analysis: dict) -> dict:
    section = load_json(CAPACITY_DIR / "datos" / "seccion_estudio.json")
    column = section["building_column"]["json_id"]
    geometry = section["geometry"]
    reinforcement = section["reinforcement"]
    materials = section["materials"]
    fibers = section["fiber_discretization"]
    legacy = _find_legacy(load_json(LEGACY_P1), column["value"])
    if legacy is None:
        raise RuntimeError(f"No se encontro columna historica {column['value']}")
    legacy_center = legacy["centro"]
    candidates = [
        solid
        for solid in geometry_model["solids"]
        if solid.get("building") == "EDIFICIO_2"
        and solid.get("floor") == "P1"
        and solid.get("category") == "column"
        and abs(float(solid.get("width_m", 0.0)) - float(geometry["b_m"]["value"])) <= 0.02
        and abs(float(solid.get("depth_m", 0.0)) - float(geometry["h_m"]["value"])) <= 0.02
    ]
    mapped = min(
        candidates,
        key=lambda solid: (
            (solid["center"][0] - legacy_center[0]) ** 2
            + (solid["center"][1] - legacy_center[1]) ** 2
        ),
    )
    mapping_distance = (
        (mapped["center"][0] - legacy_center[0]) ** 2
        + (mapped["center"][1] - legacy_center[1]) ** 2
    ) ** 0.5
    crosswalk = next(
        item for item in analysis["crosswalk"] if item["element_id"] == mapped["id"]
    )
    return {
        "format": "P1L3_UNITY_CAPACITY_v1",
        "section_id": section["section_id"],
        "building_column_id": column["value"],
        "building_column_origin": column["origin"],
        "mapped_element_id": mapped["id"],
        "mapped_analysis_id": crosswalk["analysis_id"],
        "mapping_distance_m": mapping_distance,
        "mapping_status": "MATCHED_BY_SOURCE_FLOOR_SECTION_AND_COORDINATE",
        "mapping_note": (
            "C_P2_01_0001 (2024_22-101, centro historico 7.607/0.118 m) "
            f"se vincula a {mapped['id']} (ejes {mapped.get('axis_x')}/{mapped.get('axis_y')})."
        ),
        "b_m": geometry["b_m"]["value"],
        "h_m": geometry["h_m"]["value"],
        "cover_m": geometry["cover_m"]["value"],
        "num_bars": reinforcement["num_bars"]["value"],
        "bar_diameter_m": reinforcement["bar_diameter_m"]["value"],
        "fc_pa": materials["concrete"]["fc_pa"]["value"],
        "fy_pa": materials["steel"]["fy_pa"]["value"],
        "Es_pa": materials["steel"]["Es_pa"]["value"],
        "num_fibers_y": fibers["num_fibers_y"]["value"],
        "num_fibers_z": fibers["num_fibers_z"]["value"],
        "moment_curvature": typed_rows(
            read_csv(CAPACITY_DIR / "results" / "moment_curvature.csv")
        ),
        "pm_interaction": pm_rows(
            read_csv(CAPACITY_DIR / "results" / "pm_interaction.csv")
        ),
        "disclaimer": (
            "Geometria 0.70 x 0.70 m, f'c y fy confirmados para LT2. Armadura, "
            "recubrimiento y parametros constitutivos son hipotesis de laboratorio."
        ),
    }


def build_delivery_summary(a7: dict) -> dict:
    gravity = a7["gravity"]
    seismic = a7["seismic"]
    superposition = a7["superposition"]
    cases = []
    for name in ("G", "Q", "EX", "EY", "R"):
        item = a7["cases"][name]
        displacement = item["max_displacement"]
        reactions = item["sum_reactions"]
        cases.append({
            "case_name": name,
            "max_displacement_m": displacement["magnitude_m"],
            "max_node_tag": displacement["node_tag"],
            "max_floor": displacement["floor"],
            "ux_m": displacement["vector_m"][0],
            "uy_m": displacement["vector_m"][1],
            "uz_m": displacement["vector_m"][2],
            "sum_Rx_kN": reactions["Rx_N"] / 1000.0,
            "sum_Ry_kN": reactions["Ry_N"] / 1000.0,
            "sum_Rz_kN": reactions["Rz_N"] / 1000.0,
        })
    return {
        "format": "P1L3_UNITY_DELIVERY_v1",
        "status": a7["status"],
        "limitations": a7["limitations"],
        "gravity": {
            "panel_count": gravity["panel_count"],
            "G_transferred_kN": gravity["G_transferred_N"] / 1000.0,
            "Q_transferred_kN": gravity["Q_transferred_N"] / 1000.0,
            "Q_expected_kN": gravity["Q_expected_N"] / 1000.0,
            "Q_conservation_rel_error": gravity["Q_conservation_rel_error"],
            "status": "PASS" if gravity["Q_conservation_rel_error"] <= 1.0e-9 else "FAIL",
        },
        "seismic": {
            "base_shear_coefficient": seismic["base_shear_coefficient"],
            "total_EX_kN": seismic["applied_total_EX_kN"],
            "total_EY_kN": seismic["applied_total_EY_kN"],
            "base_shear_EX_kN": seismic["reaction_base_shear_EX_kN"],
            "base_shear_EY_kN": seismic["reaction_base_shear_EY_kN"],
            "EX_rel_error": seismic["EX_base_shear_rel_error"],
            "EY_rel_error": seismic["EY_base_shear_rel_error"],
            "EX_deformed_status": seismic["EX_deformed_shape"]["status"],
            "EY_deformed_status": seismic["EY_deformed_shape"]["status"],
            "max_application_point_error_m": seismic["max_application_point_error_m"],
            "status": "PASS" if max(seismic["EX_base_shear_rel_error"], seismic["EY_base_shear_rel_error"]) <= 1.0e-9 else "FAIL",
        },
        "superposition": {
            "lambda_G": superposition["lambdas"]["G"],
            "lambda_Q": superposition["lambdas"]["Q"],
            "lambda_EX": superposition["lambdas"]["EX"],
            "lambda_EY": superposition["lambdas"]["EY"],
            "displacement_rel_error": superposition["desplazamientos_rel_error"],
            "reaction_rel_error": superposition["reacciones_rel_error"],
            "internal_force_rel_error": superposition["fuerzas_internas_rel_error"],
            "status": superposition["status"],
        },
        "cases": cases,
    }


def main() -> None:
    required = [
        GEOMETRY,
        ANALYSIS_MODEL,
        FE_CANDIDATE,
        CONNECTIVITY_AUDIT,
        A5_REPORT,
        A7_REPORT,
        SEISMIC,
        LEGACY_P1,
        CAPACITY_DIR / "datos" / "seccion_estudio.json",
        CAPACITY_DIR / "results" / "moment_curvature.csv",
        CAPACITY_DIR / "results" / "pm_interaction.csv",
        CAPACITY_DIR / "results" / "fiber_section.png",
        CAPACITY_DIR / "results" / "moment_curvature.png",
        CAPACITY_DIR / "results" / "pm_interaction.png",
        ARCHITECTURE,
        *[
            A7_DIR / "cases" / case_name / file_name
            for case_name in ("G", "Q", "EX", "EY", "R")
            for file_name in ("manifest.json", "elements.json", "nodes.json")
        ],
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Faltan fuentes:\n" + "\n".join(missing))

    geometry = load_json(GEOMETRY)
    validate_geometry(geometry)
    analysis = load_json(ANALYSIS_MODEL)
    fe_candidate = load_json(FE_CANDIDATE)
    connectivity_audit = load_json(CONNECTIVITY_AUDIT)
    seismic = load_json(SEISMIC)
    a7 = load_json(A7_REPORT)
    architecture = load_json(ARCHITECTURE)
    assert architecture.get("scope") == "EDIFICIO_1 / P4 solamente"
    assert architecture.get("participates_in_FE") is False
    assert architecture.get("objects")
    assert all(
        item.get("building") == "EDIFICIO_1"
        and item.get("floor") == "P4"
        and item.get("participates_in_FE") is False
        for item in architecture["objects"]
    )

    STREAMING.mkdir(parents=True, exist_ok=True)
    write_compact_json(STREAMING / "model_viewer.json", geometry)
    write_compact_json(STREAMING / "visual_lines.json", visual_lines_for_unity(geometry))
    shutil.copyfile(ARCHITECTURE, STREAMING / "architectural_visual_model.json")
    shutil.copyfile(SEISMIC, STREAMING / "seismic_ex_ey.json")
    analysis_cases = build_analysis_cases(analysis)
    default_analysis = next(case for case in analysis_cases["cases"] if case["case_name"] == "CASE_R")
    write_json(STREAMING / "analysis_results.json", default_analysis)
    write_json(STREAMING / "analysis_cases.json", analysis_cases)
    write_compact_json(
        STREAMING / "post_p1l3_fe_diagnostic.json",
        build_fe_diagnostic(fe_candidate, connectivity_audit),
    )
    write_json(STREAMING / "p1l3_delivery.json", build_delivery_summary(a7))
    write_json(STREAMING / "capacity_ha.json", build_capacity(geometry, analysis))
    for image_name in ("fiber_section.png", "moment_curvature.png", "pm_interaction.png"):
        shutil.copyfile(CAPACITY_DIR / "results" / image_name, STREAMING / image_name)

    a5 = load_json(A5_REPORT)
    deficit_g = abs(a5["equilibrio"]["eq_G_err_N"]) / a5["equilibrio"]["P_aplicado_G_N"]
    manifest = {
        "format": "POST_P1L3_UNITY_BUNDLE_v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "data_state": {
            "geometry": "POST_P1L4_STRUCTURAL_AUDIT_EXT4",
            "fe_diagnosis": "POST_P1L3_CANDIDATE_NOT_RUN",
            "analysis_results": "P1L3_DELIVERED_HISTORICAL",
            "loads": "P1L3_DELIVERED_HISTORICAL",
            "capacity": "P1L3_DELIVERED_HISTORICAL",
            "compatibility_warning": "GEOMETRIA_POST_P1L4; RESULTADOS_P1L4_HISTORICOS_NO_RECALCULADOS",
        },
        "source_of_truth": {
            "geometry": str(GEOMETRY.relative_to(ROOT)).replace("\\", "/"),
            "delivered_analysis_model": str(ANALYSIS_MODEL.relative_to(ROOT)).replace("\\", "/"),
            "post_p1l3_fe_candidate": str(FE_CANDIDATE.relative_to(ROOT)).replace("\\", "/"),
            "analysis_run": str(RUN_DIR.relative_to(ROOT)).replace("\\", "/"),
            "integrated_run": str(A7_DIR.relative_to(ROOT)).replace("\\", "/"),
            "seismic": str(SEISMIC.relative_to(ROOT)).replace("\\", "/"),
            "capacity": str(CAPACITY_DIR.relative_to(ROOT)).replace("\\", "/"),
            "architecture_visual": str(ARCHITECTURE.relative_to(ROOT)).replace("\\", "/"),
        },
        "files": [
            {"name": name, "sha256": sha256(STREAMING / name)}
            for name in (
                "model_viewer.json", "seismic_ex_ey.json", "analysis_results.json",
                "analysis_cases.json", "p1l3_delivery.json", "capacity_ha.json",
                "fiber_section.png", "moment_curvature.png", "pm_interaction.png",
                "architectural_visual_model.json",
                "visual_lines.json",
                "post_p1l3_fe_diagnostic.json",
            )
        ],
        "validation": {
            "geometry_solids": len(geometry["solids"]),
            "geometry_floors": geometry["expectedFloors"],
            "analysis_elements": len(analysis["elements"]),
            "floating_excluded": len(
                analysis.get("floating_excluded", {}).get("elementos", [])
                if isinstance(analysis.get("floating_excluded", {}), dict)
                else analysis.get("floating_excluded", [])
            ),
            "superposition_status": a7["superposition"]["status"],
            "gravity_reaction_deficit_percent": round(100.0 * deficit_g, 6),
            "seismic_is_applied_to_opensees": True,
            "capacity_uses_lab_assumptions": True,
            "architecture_visual_objects": len(architecture["objects"]),
            "architecture_participates_in_FE": False,
            "fe_candidate_status": fe_candidate["status"],
            "fe_candidate_members": len(fe_candidate["elements"]),
            "fe_diagnostic_focus_elements": len(fe_candidate["connectivity_validation"]),
            "fe_candidate_was_run": fe_candidate["run_policy"]["opensees_run"],
        },
    }
    write_json(STREAMING / "integration_manifest.json", manifest)
    print(json.dumps(manifest["validation"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
