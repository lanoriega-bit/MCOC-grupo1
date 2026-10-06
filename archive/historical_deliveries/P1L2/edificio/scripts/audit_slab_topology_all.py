#!/usr/bin/env python3
"""Diagnostico reproducible de bordes RLE-LOSA para ED1 y ED2, por piso.

No reconstruye superficies ni modifica modelos. Cuantifica topologia cruda,
componentes, lazos cerrados y extremos abiertos desde los DXF completos.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely import get_parts
from shapely.geometry import LineString
from shapely.ops import polygonize_full, unary_union

import audit_ed1_beams as ed1


REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "recursos/planos/dxf_full"
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/slabs"
OUT_JSON = OUT_DIR / "slab_topology_diagnostic.json"
OUT_MD = OUT_DIR / "SLAB_TOPOLOGY_DIAGNOSTIC.md"
FLOORS = ("S1", "P1", "P2", "P3", "P4")
ED2 = {
    "S1": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P1": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P2": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P3": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P4": ("2024_22-102.dxf", (700.0, 900.0, 4600.0, 3600.0), (1485.0, 3028.0)),
}
DOC_CACHE: dict[Path, object] = {}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_segments(entity) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    return ed1.raw_segments(entity) if entity.dxftype() in {"LINE", "LWPOLYLINE"} else []


def inside(point: tuple[float, float], bbox: tuple[float, float, float, float]) -> bool:
    return bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]


def transform(point: tuple[float, float], origin: tuple[float, float], building: str) -> list[float]:
    x = (point[0] - origin[0]) / 100.0
    y = (origin[1] - point[1]) / 100.0
    return [x + (27.491 if building == "EDIFICIO_1" else 0.0), y]


def source_spec(building: str, floor: str) -> tuple[Path, tuple[float, float, float, float], tuple[float, float]]:
    if building == "EDIFICIO_1":
        name, bbox, origin = ed1.FLOOR_SOURCES[floor]
        return SOURCE / "2017_67" / name, bbox, origin
    name, bbox, origin = ED2[floor]
    return SOURCE / "2024_22" / name, bbox, origin


def segments_for(building: str, floor: str) -> tuple[Path, list[dict[str, object]]]:
    path, bbox, origin = source_spec(building, floor)
    doc = DOC_CACHE.setdefault(path, ezdxf.readfile(path)) if path not in DOC_CACHE else DOC_CACHE[path]
    rows = []
    for entity in doc.modelspace():
        if entity.dxf.layer not in {"RLE-LOSA", "RLE-LOSAS"}:
            continue
        for index, (first, second) in enumerate(raw_segments(entity)):
            if not (inside(first, bbox) or inside(second, bbox)):
                continue
            start, end = transform(first, origin, building), transform(second, origin, building)
            length = math.dist(start, end)
            if length < 0.02:
                continue
            rows.append({"handle": str(entity.dxf.handle), "segment_index": index, "layer": str(entity.dxf.layer), "start": start, "end": end, "length_m": length})
    return path, rows


def structural_context(building: str, floor: str) -> dict[str, object]:
    path, bbox, origin = source_spec(building, floor)
    doc = DOC_CACHE.setdefault(path, ezdxf.readfile(path)) if path not in DOC_CACHE else DOC_CACHE[path]
    lines = []
    counts = Counter()
    for entity in doc.modelspace():
        if entity.dxf.layer not in {"RLE-LOSA", "RLE-LOSAS", "RLE-VIGA", "RLE-MURO"}:
            continue
        for first, second in raw_segments(entity):
            if not (inside(first, bbox) or inside(second, bbox)):
                continue
            start, end = transform(first, origin, building), transform(second, origin, building)
            if math.dist(start, end) < 0.02:
                continue
            lines.append(LineString([start, end]))
            counts[str(entity.dxf.layer)] += 1
    polygons, _cuts, _dangles, invalid = polygonize_full(unary_union(lines))
    polygon_rows = sorted(
        ({"area_m2": round(poly.area, 6), "bounds_m": [round(value, 6) for value in poly.bounds]} for poly in get_parts(polygons)),
        key=lambda item: item["area_m2"], reverse=True,
    )
    return {
        "segment_counts_by_layer": dict(sorted(counts.items())),
        "polygon_count": len(polygon_rows),
        "largest_polygons": polygon_rows[:20],
        "total_polygonized_area_m2": round(sum(row["area_m2"] for row in polygon_rows), 6),
        "invalid_ring_count": len(list(get_parts(invalid))),
        "interpretation": "CONTEXT_ONLY_NOT_AUTOMATIC_SLAB_SURFACE",
    }


def endpoint_key(point: list[float], tolerance: float = 0.01) -> tuple[int, int]:
    return round(point[0] / tolerance), round(point[1] / tolerance)


def component_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    adjacency: defaultdict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    edge_rows = []
    for row in rows:
        a, b = endpoint_key(row["start"]), endpoint_key(row["end"])
        adjacency[a].add(b)
        adjacency[b].add(a)
        edge_rows.append((a, b, row))
    seen = set()
    result = []
    for root in adjacency:
        if root in seen:
            continue
        stack, nodes = [root], set()
        while stack:
            node = stack.pop()
            if node in nodes:
                continue
            nodes.add(node)
            seen.add(node)
            stack.extend(adjacency[node] - nodes)
        members = [row for a, b, row in edge_rows if a in nodes and b in nodes]
        points = [point for row in members for point in (row["start"], row["end"])]
        degrees = Counter()
        for a, b, _row in edge_rows:
            if a in nodes and b in nodes:
                degrees.update((a, b))
        result.append(
            {
                "segment_count": len(members),
                "total_length_m": round(sum(float(row["length_m"]) for row in members), 6),
                "closed_by_endpoint_graph": bool(nodes) and all(value == 2 for value in degrees.values()),
                "open_node_count": sum(value == 1 for value in degrees.values()),
                "junction_node_count": sum(value > 2 for value in degrees.values()),
                "bounds_m": [round(min(p[0] for p in points), 6), round(min(p[1] for p in points), 6), round(max(p[0] for p in points), 6), round(max(p[1] for p in points), 6)],
                "handles": sorted({str(row["handle"]) for row in members}),
            }
        )
    return sorted(result, key=lambda item: (-item["total_length_m"], item["bounds_m"]))


def collinear_closures(rows: list[dict[str, object]], max_gap_m: float) -> list[dict[str, object]]:
    counts = Counter(endpoint_key(point) for row in rows for point in (row["start"], row["end"]))
    point_by_key = {endpoint_key(point): point for row in rows for point in (row["start"], row["end"])}
    open_points = [(key, point_by_key[key]) for key, count in counts.items() if count == 1]
    candidates = []
    for index, (first_key, first) in enumerate(open_points):
        for second_key, second in open_points[index + 1 :]:
            gap = math.dist(first, second)
            alignment = "V" if abs(first[0] - second[0]) <= 0.03 else "H" if abs(first[1] - second[1]) <= 0.03 else None
            if alignment and 0.02 < gap <= max_gap_m:
                candidates.append((gap, first_key, second_key, first, second, alignment))
    used = set()
    result = []
    for gap, first_key, second_key, first, second, alignment in sorted(candidates):
        if first_key in used or second_key in used:
            continue
        used.update((first_key, second_key))
        result.append({"start": first, "end": second, "length_m": round(gap, 6), "alignment": alignment, "classification": "INFERRED_COLLINEAR_GAP_CANDIDATE"})
    return result


def bridge_trials(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    trials = []
    for threshold in (0.25, 0.75, 1.50):
        closures = collinear_closures(rows, threshold)
        lines = [LineString([row["start"], row["end"]]) for row in rows]
        lines.extend(LineString([row["start"], row["end"]]) for row in closures)
        polygons, _cuts, _dangles, invalid = polygonize_full(unary_union(lines))
        polygon_rows = sorted(
            ({"area_m2": round(poly.area, 6), "bounds_m": [round(value, 6) for value in poly.bounds]} for poly in get_parts(polygons)),
            key=lambda item: item["area_m2"], reverse=True,
        )
        trials.append({"max_gap_m": threshold, "closure_count": len(closures), "closures": closures, "polygon_count": len(polygon_rows), "polygons": polygon_rows, "invalid_ring_count": len(list(get_parts(invalid)))})
    return trials


def topology(rows: list[dict[str, object]]) -> dict[str, object]:
    lines = [LineString([row["start"], row["end"]]) for row in rows]
    endpoints = Counter(endpoint_key(point) for row in rows for point in (row["start"], row["end"]))
    polygons, cuts, dangles, invalid = polygonize_full(unary_union(lines))
    polygon_rows = sorted(
        ({"area_m2": round(poly.area, 6), "perimeter_m": round(poly.length, 6), "bounds_m": [round(value, 6) for value in poly.bounds], "hole_count": len(poly.interiors)} for poly in get_parts(polygons)),
        key=lambda item: item["area_m2"], reverse=True,
    )
    return {
        "segment_count": len(rows),
        "total_length_m": round(sum(float(row["length_m"]) for row in rows), 6),
        "open_endpoint_count_0_01m": sum(value == 1 for value in endpoints.values()),
        "junction_count_0_01m": sum(value > 2 for value in endpoints.values()),
        "polygon_count": len(polygon_rows),
        "polygons": polygon_rows,
        "cut_count": len(list(get_parts(cuts))),
        "dangle_count": len(list(get_parts(dangles))),
        "invalid_ring_count": len(list(get_parts(invalid))),
        "components": component_summary(rows),
        "collinear_bridge_trials": bridge_trials(rows),
    }


def plot(building: str, floor: str, rows: list[dict[str, object]], topo: dict[str, object]) -> str:
    fig, ax = plt.subplots(figsize=(13, 7))
    for row in rows:
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color="#5f6368", linewidth=1.1)
    for polygon in topo["polygons"]:
        x0, y0, x1, y1 = polygon["bounds_m"]
        ax.text((x0 + x1) / 2.0, (y0 + y1) / 2.0, f"loop {polygon['area_m2']:.2f} m2", color="#9334e6", fontsize=7, ha="center")
    endpoint_counts = Counter(endpoint_key(point) for row in rows for point in (row["start"], row["end"]))
    open_points = [[key[0] * 0.01, key[1] * 0.01] for key, count in endpoint_counts.items() if count == 1]
    if open_points:
        ax.scatter([p[0] for p in open_points], [p[1] for p in open_points], color="#d93025", s=12, label="extremo abierto")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.3, alpha=0.4)
    ax.set_title(f"{building} {floor}: topologia cruda RLE-LOSA")
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    if open_points:
        ax.legend()
    output = OUT_DIR / f"{building.lower()}_{floor.lower()}_slab_topology.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = load(MODEL)
    result = {
        "status": "DIAGNOSTIC_COMPLETE_NO_SURFACE_CHANGE",
        "source_priority": "DIRECT_FULL_DXF_RLE_LOSA",
        "buildings": {},
        "ed2_common_s1_p3": {
            "status": "CONFIRMED_COMMON_PLAN",
            "source_sheet": "2024_22-101.dxf",
            "title": "PLANTA CIELO 1º SUBTERRANEO A CIELO PISO 3º",
            "interpretation": "La misma geometria de borde aplica a S1/P1/P2/P3 por titulo explicito de lamina, no por extrapolacion.",
            "direct_region_segment_count": 22,
            "derived_json_segment_count": 25,
            "excluded_outside_region_detail_segments": 3,
        },
        "inputs": {str(MODEL.relative_to(REPO)).replace("\\", "/"): sha256(MODEL)},
    }
    for building in ("EDIFICIO_1", "EDIFICIO_2"):
        result["buildings"][building] = {}
        for floor in FLOORS:
            path, rows = segments_for(building, floor)
            topo = topology(rows)
            provisional = [item for item in model["solids"] if item.get("building") == building and item.get("floor") == floor and item.get("category") == "slab"]
            topo["source_sheet"] = path.name
            topo["source_sha256"] = sha256(path)
            topo["provisional_slab_count"] = len(provisional)
            topo["provisional_bbox_area_m2"] = round(sum(float(item.get("width_m", 0.0)) * float(item.get("depth_m", 0.0)) for item in provisional), 6)
            topo["structural_context_polygonization"] = structural_context(building, floor)
            topo["overlay"] = plot(building, floor, rows, topo)
            topo["interpretation"] = "RAW_EDGES_REQUIRE_PERIMETER_AND_HOLE_CLASSIFICATION"
            result["buildings"][building][floor] = topo
            result["inputs"][str(path.relative_to(REPO)).replace("\\", "/")] = sha256(path)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FASE 5 — diagnóstico de topología de losas",
        "",
        "Estado: `DIAGNOSTIC_COMPLETE_NO_SURFACE_CHANGE`",
        "",
        "Los conteos provienen directamente de `RLE-LOSA/RLE-LOSAS`. Los lazos cerrados no se consideran huecos automáticamente y los extremos abiertos no se rellenan en este paso.",
        "",
        "La lámina 2024_22-101 declara una planta común desde cielo S1 hasta cielo P3; por eso esos cuatro niveles comparten 22 segmentos directos. Los 25 del JSON derivado incluyen tres trazos de detalle fuera de la región aprobada y no se usan.",
        "",
        "| Edificio | Piso | Segmentos | Extremos abiertos | Lazos crudos | Componentes | Área bbox provisional |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for building, floors in result["buildings"].items():
        for floor, row in floors.items():
            lines.append(f"| {building} | {floor} | {row['segment_count']} | {row['open_endpoint_count_0_01m']} | {row['polygon_count']} | {len(row['components'])} | {row['provisional_bbox_area_m2']:.3f} m² |")
    lines.extend([
        "",
        "Los cierres automáticos solo colineales no reconstruyen el perímetro principal: se necesita evidencia adicional de vigas y notas en esquinas/cambios de nivel.",
        "",
        "Siguiente paso: clasificar perímetro exterior, huecos reales y cierres respaldados por vigas/notas para cada piso. No se modificó FE ni el modelo combinado.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("SLAB_TOPOLOGY_DIAGNOSTIC: COMPLETE_NO_SURFACE_CHANGE")
    for building, floors in result["buildings"].items():
        print(building, {floor: {"segments": row["segment_count"], "open": row["open_endpoint_count_0_01m"], "loops": row["polygon_count"], "components": len(row["components"])} for floor, row in floors.items()})


if __name__ == "__main__":
    main()
