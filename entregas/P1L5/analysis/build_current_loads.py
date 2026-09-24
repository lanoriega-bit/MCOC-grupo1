#!/usr/bin/env python3
"""Build traceable CURRENT G/Q loads from the frozen central geometry.

Audited CAD load-zone polygons are the load footprint and their holes remain
empty. Area is assigned to the nearest active physical beam on a fine grid,
the numerical form of an equal-distance (approximately 45-degree) tributary
boundary. Every clipped cell is assigned exactly once.

Member self-weight is computed separately from section, FE length and density.
Slab self-weight remains the documented 0.15 m academic fallback. The open
7600/800 line-load unit conflict is not applied.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import LineString, Polygon, box, mapping, shape


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
MASTER_PATH = CENTRAL / "model_master.json"
LOADS_PATH = CENTRAL / "loads.json"
SECTIONS_PATH = CENTRAL / "sections.json"
MATERIALS_PATH = CENTRAL / "materials.json"
OUT = Path(__file__).resolve().parent / "generated"

G_ACCEL = 9.80665
CONCRETE_UNIT_WEIGHT_KN_M3 = 24.516625
PP_THICKNESS_FALLBACK_M = 0.15
TRIBUTARY_GRID_M = 0.50
EPS = 1e-8
STRUCTURAL_TYPES = {"beam", "column", "wall"}
CONFLICT_IDS = {
    "L700-P4-LINE-SC-800-SC_LINE",
    "L700-P4-LINE-SC-800-PM_ADIC_LINE",
}
LT_MAP = {"EDIFICIO_1": "LT1", "EDIFICIO_2": "LT2"}
ETABS = {
    "LT1": {"CM_N": 47_140_276.0, "CV_N": 11_620_380.0},
    "LT2": {"CM_N": 34_723_194.0, "CV_N": 11_096_777.0},
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def section_area(section: dict) -> float:
    dims = section["dimensions"]
    if section["type"] == "beam_rectangular":
        return float(dims["width_m"]) * float(dims["height_m"])
    if section["type"] == "column_rectangular":
        return float(dims["width_m"]) * float(dims["depth_m"])
    if section["type"] == "wall_equivalent_rectangular":
        return float(dims["thickness_m"]) * float(dims["length_m"])
    raise ValueError(f"Unsupported self-weight section {section['section_id']}")


def node_xyz(node: dict) -> list[float]:
    return [float(node[axis]) for axis in "xyz"]


def endpoint_node(row: dict, point: list[float], fe_nodes: dict) -> int:
    candidates = {
        int(ref[key])
        for ref in row.get("analysis_refs", [])
        for key in ("node_i", "node_j")
    }
    if not candidates:
        raise RuntimeError(f"No FE nodes for {row['element_id']}")
    return min(candidates, key=lambda tag: math.dist(node_xyz(fe_nodes[str(tag)]), point))


def active_beam_lines(master: dict) -> dict[tuple[str, str], list[dict]]:
    result = defaultdict(list)
    for row in master["elements"]:
        if row["type"] != "beam" or not row.get("active"):
            continue
        start, end = row["geometry"]["start_m"], row["geometry"]["end_m"]
        line = LineString([(start[0], start[1]), (end[0], end[1])])
        if line.length <= EPS:
            continue
        result[(row["building"], row["floor"])].append({
            "element_id": row["element_id"], "line": line,
            "length_m": line.length, "merged_from": row.get("merged_from", []),
        })
    return result


def assign_polygon_to_beams(polygon, receivers: list[dict]) -> tuple[dict[str, float], float]:
    """Allocate every clipped grid cell to its nearest physical beam."""
    if polygon.is_empty or polygon.area <= EPS or not receivers:
        return {}, polygon.area
    assigned = defaultdict(float)
    minx, miny, maxx, maxy = polygon.bounds
    ix0, iy0 = math.floor(minx / TRIBUTARY_GRID_M), math.floor(miny / TRIBUTARY_GRID_M)
    ix1, iy1 = math.ceil(maxx / TRIBUTARY_GRID_M), math.ceil(maxy / TRIBUTARY_GRID_M)
    for ix in range(ix0, ix1):
        for iy in range(iy0, iy1):
            clipped = polygon.intersection(box(
                ix * TRIBUTARY_GRID_M, iy * TRIBUTARY_GRID_M,
                (ix + 1) * TRIBUTARY_GRID_M, (iy + 1) * TRIBUTARY_GRID_M,
            ))
            area = clipped.area
            if area <= EPS:
                continue
            point = clipped.representative_point()
            receiver = min(receivers, key=lambda item: item["line"].distance(point))
            assigned[receiver["element_id"]] += area
    residual = polygon.area - sum(assigned.values())
    if assigned and abs(residual) > EPS:
        assigned[max(assigned, key=assigned.get)] += residual
    return dict(assigned), 0.0 if assigned else polygon.area


def match_pair(entries_by_id: dict, sc_entry: dict) -> dict | None:
    return entries_by_id.get(sc_entry["load_id"].replace("-SC_SURFACE", "-PM_ADIC_SURFACE"))


def add_node_load(target: dict[str, defaultdict], case: str, tag: int, value: float) -> None:
    target[case][int(tag)] += float(value)


def hole_area(geometry) -> float:
    components = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    return sum(Polygon(ring).area for component in components for ring in component.interiors)


def main() -> None:
    master = read(MASTER_PATH)
    loads = read(LOADS_PATH)
    sections = {row["section_id"]: row for row in read(SECTIONS_PATH)["sections"]}
    materials = {row["material_id"]: row for row in read(MATERIALS_PATH)["materials"]}
    elements = {row["element_id"]: row for row in master["elements"]}
    fe_nodes = master["fe_topology"]["nodes"]
    entries = loads["audited_load_catalog"]["entries"]
    entries_by_id = {row["load_id"]: row for row in entries}
    beam_lines = active_beam_lines(master)
    q_scale = float(loads.get("p1l5_modifications", {}).get("q_intensity_scale", 1.0))
    now = datetime.now(timezone.utc).isoformat()

    nodal = {"G": defaultdict(float), "Q": defaultdict(float)}
    receiver_data = defaultdict(lambda: {
        "area_m2": 0.0, "Q_surface_N": 0.0,
        "G_superimposed_N": 0.0, "G_slab_N": 0.0,
        "sources": set(), "zones": set(),
    })
    panels = []
    floor_summary = defaultdict(lambda: {
        "area_total_m2": 0.0, "area_with_Q_m2": 0.0, "area_without_Q_m2": 0.0,
        "Q_N": 0.0, "G_superimposed_N": 0.0, "G_slab_N": 0.0,
        "interior_hole_area_m2": 0.0, "panels": 0,
    })
    surface_ids = set()

    sc_entries = [row for row in entries if row["load_type"] == "SC_SURFACE"]
    for sc in sorted(sc_entries, key=lambda row: row["load_id"]):
        pm = match_pair(entries_by_id, sc)
        if pm is None:
            raise RuntimeError(f"Missing PM_ADIC pair for {sc['load_id']}")
        polygon = shape(sc["geometry"])
        candidates = beam_lines[(sc["building"], sc["floor"])]
        assigned, unresolved_area = assign_polygon_to_beams(polygon, candidates)
        area = polygon.area
        q_q = float(sc["SI_value"]) * q_scale
        q_pm = float(pm["SI_value"])
        q_pp = CONCRETE_UNIT_WEIGHT_KN_M3 * PP_THICKNESS_FALLBACK_M
        forces = {
            "Q": q_q * 1000.0 * area,
            "G_superimposed": q_pm * 1000.0 * area,
            "G_slab": q_pp * 1000.0 * area,
        }
        key = (sc["building"], sc["floor"])
        summary = floor_summary[key]
        summary["area_total_m2"] += area
        summary["area_with_Q_m2"] += area if q_q > 0 else 0.0
        summary["area_without_Q_m2"] += area if q_q <= 0 else 0.0
        summary["Q_N"] += forces["Q"]
        summary["G_superimposed_N"] += forces["G_superimposed"]
        summary["G_slab_N"] += forces["G_slab"]
        summary["interior_hole_area_m2"] += hole_area(polygon)
        summary["panels"] += 1

        receiver_rows = []
        for element_id, receiver_area in sorted(assigned.items()):
            row = elements[element_id]
            share = receiver_area / area if area else 0.0
            values = receiver_data[element_id]
            values["area_m2"] += receiver_area
            values["Q_surface_N"] += forces["Q"] * share
            values["G_superimposed_N"] += forces["G_superimposed"] * share
            values["G_slab_N"] += forces["G_slab"] * share
            values["sources"].update((sc["load_id"], pm["load_id"]))
            values["zones"].add(sc["load_id"])
            line_length = next(item["length_m"] for item in candidates if item["element_id"] == element_id)
            receiver_rows.append({
                "element_id": element_id, "merged_from": row.get("merged_from", []),
                "fraction": round(share, 9), "tributary_area_m2": round(receiver_area, 6),
                "equivalent_width_m": round(receiver_area / line_length, 6),
                "Q_force_N": round(forces["Q"] * share, 3),
                "G_superimposed_force_N": round(forces["G_superimposed"] * share, 3),
                "G_slab_force_N": round(forces["G_slab"] * share, 3),
            })
        panel_id = sc["load_id"].replace("-SC_SURFACE", "")
        panels.append({
            "id": panel_id, "building": sc["building"], "lt_block": LT_MAP[sc["building"]],
            "floor": sc["floor"], "geometry": mapping(polygon), "polygon": mapping(polygon),
            "area_m2": round(area, 6), "usage_zone": panel_id,
            "qG_superimposed_kN_m2": q_pm, "qG_slab_kN_m2": round(q_pp, 6),
            "qQ_kN_m2": q_q,
            "case_force_N": {"G": round(forces["G_superimposed"] + forces["G_slab"], 3), "Q": round(forces["Q"], 3)},
            "source_load_ids": [sc["load_id"], pm["load_id"]], "source_sheet": sc["source_sheet"],
            "classification": "CURRENT_RECOMPUTED" if unresolved_area <= EPS else "UNRESOLVED",
            "method": "NEAREST_ACTIVE_BEAM_EQUAL_DISTANCE_GRID_0.50M",
            "receivers": receiver_rows,
            "receiver_fraction_sum": round(sum(row["fraction"] for row in receiver_rows), 9),
            "unresolved_area_m2": round(unresolved_area, 9),
        })
        surface_ids.update((sc["load_id"], pm["load_id"]))

    physical_rows = {"G": [], "Q": []}
    for element_id, values in sorted(receiver_data.items()):
        row = elements[element_id]
        node_i = endpoint_node(row, row["geometry"]["start_m"], fe_nodes)
        node_j = endpoint_node(row, row["geometry"]["end_m"], fe_nodes)
        g_force = values["G_superimposed_N"] + values["G_slab_N"]
        q_force = values["Q_surface_N"]
        for case, force in (("G", g_force), ("Q", q_force)):
            add_node_load(nodal, case, node_i, -force / 2.0)
            add_node_load(nodal, case, node_j, -force / 2.0)
            physical_rows[case].append({
                "element_id": element_id, "node_i": node_i, "node_j": node_j,
                "P_N": round(force, 3), "end_load_N": round(force / 2.0, 3),
                "representation": "TRIBUTARY_AREA_TO_PHYSICAL_BEAM_THEN_P_OVER_2_TO_FE_END_NODES",
            })

    self_rows = []
    self_by_floor = defaultdict(float)
    self_by_building = defaultdict(float)
    for row in master["elements"]:
        if row["type"] not in STRUCTURAL_TYPES or not row.get("active"):
            continue
        section = sections[row["section_id"]]
        material = materials[row["material_id"]]
        density = float(material["elastic"]["density_kg_m3"]["value"])
        area = section_area(section)
        total = 0.0
        segments = []
        for ref in row.get("analysis_refs", []):
            ni, nj = int(ref["node_i"]), int(ref["node_j"])
            length = math.dist(node_xyz(fe_nodes[str(ni)]), node_xyz(fe_nodes[str(nj)]))
            force = area * length * density * G_ACCEL
            total += force
            add_node_load(nodal, "G", ni, -force / 2.0)
            add_node_load(nodal, "G", nj, -force / 2.0)
            segments.append({"analysis_id": ref["analysis_id"], "length_m": round(length, 6), "weight_N": round(force, 3)})
        self_rows.append({
            "element_id": row["element_id"], "building": row["building"], "lt_block": LT_MAP[row["building"]],
            "floor": row["floor"], "type": row["type"], "section_id": row["section_id"],
            "material_id": row["material_id"], "density_kg_m3": density,
            "weight_N": round(total, 3), "segments": segments,
            "status": "CURRENT_COMPUTED_FROM_SECTION_LENGTH_DENSITY",
        })
        self_by_floor[(row["building"], row["floor"])] += total
        self_by_building[row["building"]] += total

    for key, summary in floor_summary.items():
        summary["G_self_weight_N"] = self_by_floor[key]
        summary["G_total_N"] = summary["G_self_weight_N"] + summary["G_superimposed_N"] + summary["G_slab_N"]

    for entry in entries:
        if entry["load_id"] in surface_ids:
            entry["current_application"] = {"status": "CURRENT_RECONSTRUCTED", "applied": True, "method": "AUDITED_ZONE_POLYGON_TO_CURRENT_BEAM_TRIBUTARIES"}
        elif entry["load_type"] == "PP_LOSA":
            entry["current_application"] = {"status": "HISTORICAL_FALLBACK", "applied": True, "thickness_m": PP_THICKNESS_FALLBACK_M}
        elif entry["load_id"] in CONFLICT_IDS:
            entry["current_application"] = {"status": "UNIT_CONFLICT_UNRESOLVED", "applied": False, "reason": "PM.ADIC=7600 / SC=800 unit/type conflict; excluded without treating unknown as zero."}
        elif entry["load_type"].endswith("POINT"):
            entry["current_application"] = {"status": "UNRESOLVED", "applied": False, "reason": "Application position and receiver are not uniquely evidenced."}
        elif entry["load_type"].endswith("LINE"):
            entry["current_application"] = {"status": "UNRESOLVED", "applied": False, "reason": "Line-load receiver/type is not sufficiently evidenced for CURRENT application."}

    generated = {
        "Q": sum(row["Q_N"] for row in floor_summary.values()),
        "G_superimposed": sum(row["G_superimposed_N"] + row["G_slab_N"] for row in floor_summary.values()),
        "G_self_weight": sum(row["weight_N"] for row in self_rows),
    }
    generated["G"] = generated["G_superimposed"] + generated["G_self_weight"]
    conservation = {}
    for case in ("G", "Q"):
        transferred = -sum(nodal[case].values())
        residual = transferred - generated[case]
        conservation[case] = {
            "generated_N": round(generated[case], 3), "transferred_N": round(transferred, 3),
            "residual_N": round(residual, 6),
            "residual_percent": round(100.0 * residual / generated[case], 12) if generated[case] else 0.0,
            "status": "PASS" if abs(residual) <= max(1e-3, generated[case] * 1e-9) else "FAIL",
        }

    by_building = {}
    for building, lt_block in LT_MAP.items():
        rows = [value for (bld, _), value in floor_summary.items() if bld == building]
        q = sum(row["Q_N"] for row in rows)
        g_add = sum(row["G_superimposed_N"] + row["G_slab_N"] for row in rows)
        g_self = self_by_building[building]
        by_building[building] = {
            "lt_block": lt_block, "Q_N": round(q, 3), "G_self_weight_N": round(g_self, 3),
            "G_superimposed_dead_N": round(g_add, 3), "G_total_N": round(g_self + g_add, 3),
            "etabs_CV_N": ETABS[lt_block]["CV_N"], "etabs_CM_N": ETABS[lt_block]["CM_N"],
            "Q_difference_percent": round(100.0 * (q - ETABS[lt_block]["CV_N"]) / ETABS[lt_block]["CV_N"], 3),
            "G_difference_percent": round(100.0 * (g_self + g_add - ETABS[lt_block]["CM_N"]) / ETABS[lt_block]["CM_N"], 3),
        }

    coverage_rows = []
    for (building, floor), row in sorted(floor_summary.items()):
        coverage_rows.append({
            "building": building, "lt_block": LT_MAP[building], "floor": floor,
            **{key: round(value, 3) if isinstance(value, float) else value for key, value in row.items()},
        })

    status_counts = Counter(row["current_application"]["status"] for row in entries)
    unresolved = [row["load_id"] for row in entries if not row["current_application"]["applied"]]
    panel_status = "CURRENT_RECOMPUTED" if all(row["classification"] == "CURRENT_RECOMPUTED" for row in panels) else "CURRENT_WITH_UNRESOLVED"
    loads["generated_utc"] = now
    loads["current_status"] = "CURRENT_LOADS_RECONSTRUCTED_READY_FOR_OPENSEES"
    loads["building_correspondence"] = {
        "EDIFICIO_1": {"benchmark": "LT1", "description": "parte antigua", "status": "CONFIRMED_BY_GEOMETRY_AND_ETABS_Q_MAGNITUDE"},
        "EDIFICIO_2": {"benchmark": "LT2", "description": "parte nueva", "status": "CONFIRMED_BY_GEOMETRY_AND_ETABS_Q_MAGNITUDE"},
        "previous_Q_N": 11_259_193.078, "previous_scope": "PARTIAL_BOTH_BUILDINGS_ED1_DOMINANT",
    }
    loads["audited_load_catalog"]["status"] = "CURRENT_RECONSTRUCTED_WITH_EXPLICIT_UNRESOLVED"
    loads["audited_load_catalog"]["current_status_counts"] = dict(status_counts)
    loads["tributary_areas"] = {
        "status": panel_status, "source": "Audited CAD load-zone polygons on frozen CURRENT geometry",
        "method": "NEAREST_ACTIVE_BEAM_EQUAL_DISTANCE_GRID_APPROX_45_DEGREE", "grid_m": TRIBUTARY_GRID_M,
        "panos": panels, "coverage_by_floor": coverage_rows,
        "classification_counts": dict(Counter(row["classification"] for row in panels)),
        "conservation_note": "Every clipped cell is assigned once; holes remain excluded.",
    }

    element_loads = []
    self_by_id = {row["element_id"]: row for row in self_rows}
    for element_id in sorted(set(receiver_data) | set(self_by_id)):
        row = elements[element_id]
        values = receiver_data.get(element_id, {})
        area = float(values.get("area_m2", 0.0))
        length = LineString([row["geometry"]["start_m"][:2], row["geometry"]["end_m"][:2]]).length if row["type"] == "beam" else 0.0
        q_force = float(values.get("Q_surface_N", 0.0))
        g_add = float(values.get("G_superimposed_N", 0.0)) + float(values.get("G_slab_N", 0.0))
        self_force = float(self_by_id.get(element_id, {}).get("weight_N", 0.0))
        element_loads.append({
            "element_id": element_id, "building": row["building"], "lt_block": LT_MAP[row["building"]],
            "floor": row["floor"], "type": row["type"],
            "Q": {
                "tributary_area_m2": round(area, 6), "equivalent_width_m": round(area / length, 6) if length > EPS else None,
                "surface_force_N": round(q_force, 3), "equivalent_line_load_N_m": round(q_force / length, 3) if length > EPS else None,
                "zone_ids": sorted(values.get("zones", set())), "status": "CURRENT_RECOMPUTED" if area > 0 else "NO_DATA",
            },
            "G": {"self_weight_N": round(self_force, 3), "tributary_dead_N": round(g_add, 3), "total_associated_N": round(self_force + g_add, 3), "status": "CURRENT_COMPUTED"},
            "source_load_ids": sorted(values.get("sources", set())),
        })

    loads["current_load_application"] = {
        "status": "PASS_WITH_EXPLICIT_UNRESOLVED" if all(row["status"] == "PASS" for row in conservation.values()) else "FAIL",
        "generated_utc": now, "basis": "CURRENT_AUDITED_ZONE_POLYGONS_AND_COMPUTED_MEMBER_SELF_WEIGHT",
        "q_intensity_scale": q_scale, "unresolved_load_ids": unresolved, "unit_conflicts": sorted(CONFLICT_IDS),
        "catalog_status_counts": dict(status_counts), "conservation": conservation,
        "totals": {"Q_N": round(generated["Q"], 3), "G_self_weight_N": round(generated["G_self_weight"], 3), "G_superimposed_dead_N": round(generated["G_superimposed"], 3), "G_total_N": round(generated["G"], 3)},
        "by_building": by_building, "by_floor": coverage_rows,
        "physical_beam_loads": physical_rows, "element_loads": element_loads,
        "self_weight_by_element": self_rows,
        "nodal_loads": {case: [{"node_tag": tag, "Fz_N": round(value, 3)} for tag, value in sorted(values.items())] for case, values in nodal.items()},
        "approximations": [
            "Slab thickness is the documented 0.15 m HISTORICAL_FALLBACK.",
            "Tributary boundaries use a 0.50 m nearest-beam grid approximation to equal-distance/45-degree transfer.",
            "Unresolved point and line loads are excluded explicitly and are not interpreted as zero.",
        ],
    }
    for case in loads["base_cases"]:
        if case["case_id"] in {"G", "Q"}:
            case["status"] = "CURRENT_READY"

    write(LOADS_PATH, loads)
    write(OUT / "current_tributary_loads.json", loads["current_load_application"])
    write(OUT / "current_tributary_panels.json", loads["tributary_areas"])
    write(OUT / "current_loads_by_element.json", {"format": "MCOC_P1L5_CURRENT_ELEMENT_LOADS_V1", "generated_utc": now, "data_state": "CURRENT_RECOMPUTED", "elements": element_loads})
    result = {
        "status": loads["current_load_application"]["status"], "panels": len(panels),
        "catalog_status_counts": dict(status_counts), "unresolved": unresolved,
        "conservation": conservation, "totals": loads["current_load_application"]["totals"], "by_building": by_building,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if loads["current_load_application"]["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
