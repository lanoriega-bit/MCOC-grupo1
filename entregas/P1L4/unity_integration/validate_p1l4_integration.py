"""Valida contratos que alimentan el postprocesador Unity P1L4."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STREAM = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
OUT_JSON = ROOT / "entregas" / "P1L4" / "P1L4_INTEGRATION_QA.json"
OUT_MD = ROOT / "entregas" / "P1L4" / "P1L4_INTEGRATION_QA.md"
LOAD_CATALOG = ROOT / "entregas" / "P1L3" / "results" / "a1a2" / "load_zones_700_completion" / "load_catalog_700.json"


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> None:
    geometry = load(STREAM / "model_viewer.json")
    metadata = load(STREAM / "p1l4_structural_metadata.json")
    cases = load(STREAM / "analysis_cases.json")
    diagnostic = load(STREAM / "post_p1l3_fe_diagnostic.json")
    demand_capacity = load(STREAM / "demanda_capacidad.json")
    tributaries = load(STREAM / "tributary_areas.json")
    loads = load(LOAD_CATALOG)
    unity_loads = load(STREAM / "p1l4_load_catalog.json")
    physical_context = load(STREAM / "p1l4_physical_context.json")
    integration_manifest = load(STREAM / "p1l4_integration_manifest.json")

    geometry_ids = {item["id"] for item in geometry["solids"] if item.get("id")}
    metadata_ids = {item["element_id"] for item in metadata["elements"]}
    tags = [item["opensees_tag"] for item in metadata["elements"]]
    analysis_ids = [item["analysis_id"] for item in metadata["elements"]]
    node_pairs_valid = all(
        len(item.get("node_i_coord_m", [])) == 3 and len(item.get("node_j_coord_m", [])) == 3
        for item in metadata["elements"]
    )
    sections_valid = all(
        item.get("section")
        and item["section"].get("A_m2", 0) > 0
        and item["section"].get("dim_local_y_m", 0) > 0
        and item["section"].get("dim_local_z_m", 0) > 0
        for item in metadata["elements"]
    )
    axes_valid = all(
        item.get("local_axes")
        and all(len(item["local_axes"].get(axis, [])) == 3 for axis in ("x", "y", "z"))
        for item in metadata["elements"]
    )
    case_ids = [item["case_name"] for item in cases["cases"]]
    result_components_valid = all(
        len(row.get("localForce_end1", [])) == 6 and len(row.get("localForce_end2", [])) == 6
        for case in cases["cases"] for row in case.get("elements", [])
    )
    result_tags = {
        row["opensees_tag"]
        for case in cases["cases"] if case["case_name"] == "CASE_R"
        for row in case.get("elements", [])
    }

    mappings_per_geometry = Counter()
    for item in diagnostic.get("elements", []):
        mappings_per_geometry[item["element_id"]] += len(item.get("crosswalk", []))
    one_to_many = sum(count > 1 for count in mappings_per_geometry.values())

    dc_checks = []
    for item in demand_capacity["elements"]:
        valid_points = [point for point in item["capacity"]["points"] if point.get("valid")]
        invalid_points = [point for point in item["capacity"]["points"] if not point.get("valid")]
        dc_checks.append({
            "element_id": item["element_id"],
            "opensees_tag": item["opensees_tag"],
            "geometry_id_exists": item["element_id"] in geometry_ids,
            "metadata_id_exists": item["element_id"] in metadata_ids,
            "result_tag_exists_in_CASE_R": item["opensees_tag"] in result_tags,
            "valid_pm_points": len(valid_points),
            "invalid_pm_points_retained": len(invalid_points),
            "demand_readable": all(key in item["demand_capacity"] for key in ("P_kN", "M_kNm", "pm_axis", "inside_envelope")),
        })

    supports_valid = all(
        isinstance(item.get("node_tag"), int)
        and len(item.get("coord_m", [])) == 3
        and all(isinstance(item.get(key), bool) for key in ("UX", "UY", "UZ", "RX", "RY", "RZ"))
        for item in metadata["supports"]
    )
    tributaries_valid = bool(tributaries.get("areas")) and all(
        isinstance(item.get("area_m2"), (int, float))
        and isinstance(item.get("load_kN"), (int, float))
        and item.get("area_m2", -1) >= 0
        for item in tributaries["areas"]
    )
    tributary_polygons_missing = sum(not item.get("polygon") for item in tributaries["areas"])
    tributary_zero_areas = sum(item.get("area_m2") == 0 for item in tributaries["areas"])
    allowed_load_types = set(loads["allowed_load_types"])
    loads_valid = all(
        item.get("load_type") in allowed_load_types
        and item.get("SI_unit")
        and isinstance(item.get("SI_value"), (int, float))
        and item.get("application_status")
        for item in loads["entries"]
    )
    drawable_loads = [
        item for item in unity_loads.get("entries", [])
        if item.get("geometry_type") in ("Polygon", "LineString")
        and len(item.get("coordinates_xy_flat", [])) >= (6 if item.get("geometry_type") == "Polygon" else 4)
    ]
    unity_loads_valid = (
        unity_loads.get("data_state") == "AUDITADO_NOT_APPLIED"
        and unity_loads.get("is_structurally_applied") is False
        and unity_loads.get("entry_count") == len(loads["entries"])
        and unity_loads.get("drawable_entry_count") == len(drawable_loads)
    )
    context_ids = [item["element_id"] for item in physical_context.get("classifications", [])]
    physical_context_valid = (
        physical_context.get("status") == "AUDITED_DIAGNOSTIC_ONLY"
        and physical_context.get("participates_in_FE") is False
        and physical_context.get("opensees_changed") is False
        and physical_context.get("historical_results_changed") is False
        and physical_context.get("terrain_surface_generated") is False
        and len(context_ids) == 40
        and len(set(context_ids)) == 40
        and len(physical_context.get("clusters", [])) == 3
        and all(item.get("participates_in_FE") is False for item in physical_context.get("clusters", []))
    )
    context_manifest_entry = next(
        (item for item in integration_manifest.get("files", []) if item.get("name") == "p1l4_physical_context.json"),
        None,
    )
    physical_context_manifest_valid = (
        context_manifest_entry is not None
        and integration_manifest.get("data_state", {}).get("physical_context") == "POST_P1L3_AUDITED_DIAGNOSTIC_ONLY"
        and integration_manifest.get("qa", {}).get("physical_context_classifications") == 40
        and integration_manifest.get("qa", {}).get("physical_context_participates_in_FE") is False
    )

    overlap = len(geometry_ids & metadata_ids)
    report = {
        "status": "PASS_WITH_NOTES",
        "baseline": "aa6bc4b7a207dde4ddac2f3deef1eee54e042f5f",
        "checks": {
            "unity_geometry_ids_unique": len(geometry_ids) == len(geometry["solids"]),
            "opensees_tags_unique": len(tags) == len(set(tags)),
            "analysis_ids_unique": len(analysis_ids) == len(set(analysis_ids)),
            "nodes_exist_and_have_coordinates": node_pairs_valid,
            "sections_readable": sections_valid,
            "material_readable": metadata.get("material", {}).get("E_pa", 0) > 0,
            "local_axes_readable": axes_valid,
            "result_components_exist": result_components_valid,
            "case_ids_valid": case_ids == ["CASE_G", "CASE_Q", "CASE_EX", "CASE_EY", "CASE_R"],
            "supports_readable": supports_valid,
            "tributary_areas_readable": tributaries_valid,
            "loads_readable": loads_valid,
            "unity_load_catalog_readable_and_not_applied": unity_loads_valid,
            "physical_context_readable_visual_only": physical_context_valid,
            "physical_context_manifest_traced": physical_context_manifest_valid,
            "demand_capacity_readable": all(
                row["geometry_id_exists"] and row["metadata_id_exists"]
                and row["result_tag_exists_in_CASE_R"] and row["valid_pm_points"] >= 2
                and row["demand_readable"] for row in dc_checks
            ),
        },
        "counts": {
            "unity_geometry_ids": len(geometry_ids),
            "historical_analysis_geometry_ids": len(metadata_ids),
            "geometry_ids_with_historical_results": overlap,
            "current_geometry_ids_without_historical_results": len(geometry_ids - metadata_ids),
            "historical_result_ids_without_current_geometry": len(metadata_ids - geometry_ids),
            "opensees_elements": len(tags),
            "supports": len(metadata["supports"]),
            "tributary_areas": len(tributaries.get("areas", [])),
            "tributary_point_areas": len(tributaries.get("point_areas", [])),
            "tributary_areas_without_display_polygon": tributary_polygons_missing,
            "tributary_zero_area_records": tributary_zero_areas,
            "load_catalog_entries": len(loads["entries"]),
            "load_catalog_drawable_entries": len(drawable_loads),
            "crosswalk_1_to_many_geometry_ids": one_to_many,
            "physical_context_classifications": len(context_ids),
            "physical_context_clusters": len(physical_context.get("clusters", [])),
        },
        "demand_capacity": dc_checks,
        "notes": [
            "La geometria Unity es POST-P1L3; los resultados OpenSees disponibles son el snapshot P1L3 entregado.",
            "Las diferencias de IDs se muestran como N/A y no se rellenan ni remapean por proximidad.",
            "El catalogo 700 es legible pero sigue READY_FOR_Q_REVIEW_NOT_APPLIED; no reemplaza las cargas historicas.",
            f"Hay {tributary_polygons_missing} tributarias historicas con area/carga legible pero sin poligono de visualizacion; se reportan, no se inventa su huella.",
            f"Hay {tributary_zero_areas} registros historicos con area y carga explicitamente iguales a cero; no se reinterpretan como datos ausentes.",
            "El FE post-P1L3 sigue CANDIDATE_NOT_APPROVED_NOT_RUN.",
            "La capa CONTEXTO FÍSICO solo reclasifica y dibuja regiones/marcadores; no cambia apoyos, elementos ni resultados.",
        ],
    }
    if not all(report["checks"].values()):
        report["status"] = "FAIL"

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# QA de integración P1L4",
        "",
        f"Estado: `{report['status']}`",
        "",
        "## Comprobaciones",
        "",
        "| Comprobación | Resultado |",
        "| --- | --- |",
    ]
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | {'PASS' if value else 'FAIL'} |")
    lines += ["", "## Cobertura y contratos", ""]
    for key, value in report["counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Demanda-capacidad", ""]
    for item in dc_checks:
        lines.append(
            f"- `{item['element_id']}` / tag `{item['opensees_tag']}`: "
            f"geometría, metadata y CASE_R presentes; {item['valid_pm_points']} puntos válidos y "
            f"{item['invalid_pm_points_retained']} inválidos retenidos sin usarlos como frontera."
        )
    lines += ["", "## Notas de alcance", ""]
    lines += [f"- {note}" for note in report["notes"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], **report["counts"]}, ensure_ascii=False, indent=2))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
