#!/usr/bin/env python3
"""Recompute CURRENT tributary panels and route audited loads to FE nodes.

Surface-zone loads are clipped against CURRENT panels.  Each rectangular
panel is distributed to its four supported edges with the classical 45-degree
tributary split, then to overlapping beam segments.  Physical beam totals are
converted to end-node loads (P/2), matching the documented P1L3 FE convention.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import Polygon, shape


ROOT = Path(__file__).resolve().parents[3]
P1L3 = ROOT / "entregas" / "P1L3"
sys.path.insert(0, str(P1L3))

from p1l3.panos import beam_lines, build_panos, load_model  # noqa: E402


CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
MASTER_PATH = CENTRAL / "model_master.json"
LOADS_PATH = CENTRAL / "loads.json"
CURRENT_GEOMETRY = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
OUT = Path(__file__).resolve().parent / "generated"
PP_THICKNESS_FALLBACK_M = 0.15
EPS = 1e-8


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(max(a0, a1), max(b0, b1)) - max(min(a0, a1), min(b0, b1)))


def panel_edge_areas(panel) -> dict[str, float]:
    dx, dy = panel.xhi - panel.xlo, panel.yhi - panel.ylo
    if dx >= dy:
        long_edge = dx * dy / 2.0 - dy * dy / 4.0
        short_edge = dy * dy / 4.0
        result = {"bottom": long_edge, "top": long_edge, "left": short_edge, "right": short_edge}
    else:
        long_edge = dx * dy / 2.0 - dx * dx / 4.0
        short_edge = dx * dx / 4.0
        result = {"left": long_edge, "right": long_edge, "bottom": short_edge, "top": short_edge}
    if abs(sum(result.values()) - panel.area_m2) > 1e-7:
        raise RuntimeError(f"Tributary split does not conserve panel {panel.id}")
    return result


def edge_receivers(panel, lines: list[dict], tol: float = 0.35) -> dict[str, list[tuple[str, float]]]:
    edges = {
        "bottom": ("H", panel.ylo, panel.xlo, panel.xhi),
        "top": ("H", panel.yhi, panel.xlo, panel.xhi),
        "left": ("V", panel.xlo, panel.ylo, panel.yhi),
        "right": ("V", panel.xhi, panel.ylo, panel.yhi),
    }
    result = {}
    for name, (orient, c, lo, hi) in edges.items():
        hits = []
        for line in lines:
            if line["building"] != panel.building or line["floor"] != panel.floor:
                continue
            if line["orient"] != orient or abs(line["c"] - c) > tol:
                continue
            length = overlap(line["lo"], line["hi"], lo, hi)
            if length > EPS:
                hits.append((line["id"], length))
        result[name] = hits
    return result


def node_for_endpoint(row: dict, endpoint: list[float], fe_nodes: dict[str, list[float]]) -> int:
    candidates = {
        int(ref[key])
        for ref in row.get("analysis_refs", [])
        for key in ("node_i", "node_j")
    }
    if not candidates:
        raise RuntimeError(f"No FE nodes for {row['element_id']}")
    def coord(tag: int) -> list[float]:
        node = fe_nodes[str(tag)]
        return [node["x"], node["y"], node["z"]] if isinstance(node, dict) else node
    return min(candidates, key=lambda tag: math.dist(coord(tag), endpoint))


def main() -> None:
    master = read(MASTER_PATH)
    loads = read(LOADS_PATH)
    model = load_model(CURRENT_GEOMETRY)
    panels, stats = build_panos(model, clust_tol=0.7, beam_tol=0.35, min_cover=0.5, min_span=0.8)
    lines = beam_lines(model)
    line_by_id = {line["id"]: line for line in lines}
    central_by_id = {row["element_id"]: row for row in master["elements"]}
    fe_nodes = master["fe_topology"]["nodes"]

    entries = loads["audited_load_catalog"]["entries"]
    q_intensity_scale = float(loads.get("p1l5_modifications", {}).get("q_intensity_scale", 1.0))
    surfaces = [row for row in entries if row["load_type"] in {"SC_SURFACE", "PM_ADIC_SURFACE"}]
    surfaces_by_key = defaultdict(list)
    for row in surfaces:
        surfaces_by_key[(row["building"], row["floor"], row["load_type"])].append((row, shape(row["geometry"])))

    beam_loads = {"G": defaultdict(float), "Q": defaultdict(float)}
    panel_rows = []
    applied_load_ids = set()
    surface_expected = {"G": 0.0, "Q": 0.0}
    pp_expected = 0.0

    for panel in panels:
        polygon = Polygon(panel.vertices)
        contributions = {"G": [], "Q": []}
        totals = {"G": 0.0, "Q": 0.0}
        for load_type, case in (("SC_SURFACE", "Q"), ("PM_ADIC_SURFACE", "G")):
            for entry, zone in surfaces_by_key[(panel.building, panel.floor, load_type)]:
                area = polygon.intersection(zone).area
                if area <= EPS:
                    continue
                scale = q_intensity_scale if case == "Q" else 1.0
                force_n = entry["SI_value"] * 1000.0 * area * scale
                totals[case] += force_n
                surface_expected[case] += force_n
                applied_load_ids.add(entry["load_id"])
                contributions[case].append({
                    "load_id": entry["load_id"],
                    "intersection_area_m2": round(area, 6),
                    "q_kN_m2": entry["SI_value"] * scale,
                    "force_N": round(force_n, 3),
                    "status": "CURRENT_RECOMPUTED",
                })

        pp_q_n_m2 = 24.516625 * 1000.0 * PP_THICKNESS_FALLBACK_M
        pp_force = pp_q_n_m2 * panel.area_m2
        totals["G"] += pp_force
        pp_expected += pp_force
        pp_id = f"{panel.building}-{panel.floor}-PP_LOSA"
        contributions["G"].append({
            "load_id": pp_id,
            "intersection_area_m2": round(panel.area_m2, 6),
            "q_kN_m2": round(pp_q_n_m2 / 1000.0, 6),
            "force_N": round(pp_force, 3),
            "status": "HISTORICAL_FALLBACK",
            "fallback_thickness_m": PP_THICKNESS_FALLBACK_M,
        })
        applied_load_ids.add(pp_id)

        edge_areas = panel_edge_areas(panel)
        receivers = edge_receivers(panel, lines)
        unresolved_edges = []
        for edge, area_share in edge_areas.items():
            hits = [(beam_id, length) for beam_id, length in receivers[edge] if central_by_id.get(beam_id, {}).get("active")]
            length_sum = sum(length for _, length in hits)
            if length_sum <= EPS:
                unresolved_edges.append(edge)
                continue
            for case in ("G", "Q"):
                if totals[case] <= 0:
                    continue
                edge_force = totals[case] * area_share / panel.area_m2
                for beam_id, length in hits:
                    beam_loads[case][beam_id] += edge_force * length / length_sum

        panel_rows.append({
            "id": panel.id,
            "building": panel.building,
            "floor": panel.floor,
            "vertices": [[round(x, 6), round(y, 6)] for x, y in panel.vertices],
            "area_m2": round(panel.area_m2, 6),
            "classification": "CURRENT_RECOMPUTED" if not unresolved_edges else "UNRESOLVED",
            "edge_cover_frac": panel.edge_cover_frac,
            "unresolved_edges": unresolved_edges,
            "zone_contributions": contributions,
            "case_force_N": {key: round(value, 3) for key, value in totals.items()},
        })

    # Apply the one audited line-load pair with documented LIKELY receivers.
    line_expected = {"G": 0.0, "Q": 0.0}
    for entry in entries:
        if entry["load_type"] not in {"SC_LINE", "PM_ADIC_LINE"}:
            continue
        receiver = entry.get("receiver") or {}
        hits = [
            item for item in receiver.get("elements", [])
            if central_by_id.get(item["element_id"], {}).get("active")
        ]
        if entry.get("application_status") != "READY_SPATIAL_NOT_APPLIED" or not hits:
            entry["current_application"] = {"status": "UNRESOLVED", "applied": False}
            continue
        case = "Q" if entry["load_type"] == "SC_LINE" else "G"
        total_overlap = sum(item["parallel_overlap_m"] for item in hits)
        for item in hits:
            scale = q_intensity_scale if case == "Q" else 1.0
            force = entry["SI_value"] * 1000.0 * item["parallel_overlap_m"] * scale
            beam_loads[case][item["element_id"]] += force
            line_expected[case] += force
        applied_load_ids.add(entry["load_id"])
        entry["current_application"] = {
            "status": "APPLIED_CURRENT_LIKELY_RECEIVER",
            "applied": True,
            "receiver_count": len(hits),
            "total_overlap_m": round(total_overlap, 6),
        }

    nodal = {"G": defaultdict(float), "Q": defaultdict(float)}
    physical_rows = {"G": [], "Q": []}
    for case in ("G", "Q"):
        for beam_id, force in sorted(beam_loads[case].items()):
            row = central_by_id.get(beam_id)
            line = line_by_id.get(beam_id)
            if not row or not line or not row.get("active") or force <= EPS:
                continue
            node_i = node_for_endpoint(row, row["geometry"]["start_m"], fe_nodes)
            node_j = node_for_endpoint(row, row["geometry"]["end_m"], fe_nodes)
            nodal[case][node_i] -= force / 2.0
            nodal[case][node_j] -= force / 2.0
            physical_rows[case].append({
                "element_id": beam_id,
                "node_i": node_i,
                "node_j": node_j,
                "P_N": round(force, 3),
                "end_load_N": round(force / 2.0, 3),
                "representation": "TRIBUTARY_TO_PHYSICAL_BEAM_THEN_P_OVER_2_TO_FE_END_NODES",
            })

    expected = {
        "G": surface_expected["G"] + pp_expected + line_expected["G"],
        "Q": surface_expected["Q"] + line_expected["Q"],
    }
    conservation = {}
    for case in ("G", "Q"):
        transferred = -sum(nodal[case].values())
        diff = transferred - expected[case]
        conservation[case] = {
            "expected_N": round(expected[case], 3),
            "transferred_N": round(transferred, 3),
            "difference_N": round(diff, 6),
            "relative_error": round(diff / expected[case], 12) if expected[case] else 0.0,
            "status": "PASS" if abs(diff) <= max(1e-3, expected[case] * 1e-9) else "FAIL",
        }

    for entry in entries:
        if entry["load_type"].endswith("SURFACE"):
            entry["current_application"] = {
                "status": "APPLIED_CURRENT_INTERSECTION" if entry["load_id"] in applied_load_ids else "UNMAPPED_CURRENT",
                "applied": entry["load_id"] in applied_load_ids,
            }
        elif entry["load_type"] == "PP_LOSA":
            entry["current_application"] = {
                "status": "APPLIED_HISTORICAL_THICKNESS_FALLBACK",
                "applied": True,
                "thickness_m": PP_THICKNESS_FALLBACK_M,
            }
        elif entry["load_type"].endswith("POINT"):
            entry["current_application"] = {"status": "UNRESOLVED_NO_APPLICATION_POSITION", "applied": False}

    unresolved = [row["load_id"] for row in entries if not row.get("current_application", {}).get("applied")]
    now = datetime.now(timezone.utc).isoformat()
    loads["generated_utc"] = now
    loads["current_status"] = "CURRENT_LOAD_VECTORS_READY_WITH_DOCUMENTED_UNRESOLVED"
    loads["audited_load_catalog"]["status"] = "CURRENT_PARTIAL_WITH_DOCUMENTED_UNRESOLVED"
    loads["tributary_areas"] = {
        "status": "CURRENT_WITH_DOCUMENTED_FALLBACKS",
        "source": "CURRENT central geometry; historical 0.15 m slab thickness fallback only",
        "panos": panel_rows,
        "coverage": stats,
        "parameters": {
            "clust_tol_m": 0.7, "beam_tol_m": 0.35, "min_cover": 0.5, "min_span_m": 0.8,
            "distribution": "RECTANGULAR_45_DEGREE_EDGE_AREAS",
        },
        "classification_counts": dict(Counter(row["classification"] for row in panel_rows)),
    }
    loads["current_load_application"] = {
        "status": "PASS_WITH_DOCUMENTED_UNRESOLVED" if all(x["status"] == "PASS" for x in conservation.values()) else "FAIL",
        "generated_utc": now,
        "basis": "CURRENT_RECOMPUTED_TRIBUTARIES",
        "approximations": [
            "PP_LOSA uses the documented historical 0.15 m uniform thickness fallback.",
            "Audited LIKELY P4 line receiver is applied; unresolved ED2 line and three point-load pairs are not invented.",
            "Panel loads are converted to physical-beam totals and P/2 nodal end loads.",
        ],
        "q_intensity_scale": q_intensity_scale,
        "unresolved_load_ids": unresolved,
        "conservation": conservation,
        "physical_beam_loads": physical_rows,
        "nodal_loads": {
            case: [{"node_tag": tag, "Fz_N": round(value, 3)} for tag, value in sorted(values.items())]
            for case, values in nodal.items()
        },
    }
    for case in loads["base_cases"]:
        if case["case_id"] in {"G", "Q"}:
            case["status"] = "CURRENT_READY"

    write(LOADS_PATH, loads)
    write(OUT / "current_tributary_loads.json", loads["current_load_application"])
    write(OUT / "current_tributary_panels.json", loads["tributary_areas"])
    print(json.dumps({
        "status": loads["current_load_application"]["status"],
        "current_panels": len(panel_rows),
        "panel_classifications": loads["tributary_areas"]["classification_counts"],
        "unresolved_load_entries": len(unresolved),
        "unresolved_load_ids": unresolved,
        "conservation": conservation,
    }, ensure_ascii=False, indent=2))
    if loads["current_load_application"]["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
