"""Extrae una primera geometria 3D desde DXF estructurales.

La salida es un modelo de inspeccion: mantiene trazabilidad a capas CAD y apila
plantas por nivel para usarlo como base de OpenSees y Unity.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[3]
DXF_DIR = Path(os.environ.get("MCOC_DXF_DIR", REPO_ROOT / "recursos" / "planos" / "dxf_generated" / "2017_67"))
ENTREGA_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ENTREGA_DIR / "results"
UNITY_EXPORT_DIR = ENTREGA_DIR / "unity_export"


@dataclass(frozen=True)
class FloorSpec:
    floor_id: str
    label: str
    dxf_name: str
    z_m: float
    bbox_cm: tuple[float, float, float, float]
    origin_x_cm: float
    origin_y_cm: float


FLOORS = [
    FloorSpec("base", "Fundaciones y apoyos", "2017_67-100.dxf", 0.00, (268.0, 3239.0, 5756.0, 8003.0), 802.07, 6329.79),
    FloorSpec("1S", "Cielo 1 subterraneo", "2017_67-101.dxf", 3.96, (571.0, 5260.0, 3890.0, 8496.0), 1061.32, 7183.28),
    FloorSpec("1", "Cielo piso 1", "2017_67-101.dxf", 7.92, (571.0, 487.0, 5972.0, 4904.0), 1061.32, 3558.02),
    FloorSpec("2", "Cielo piso 2", "2017_67-102.dxf", 11.88, (120.0, 5250.0, 5960.0, 8456.0), 893.24, 7903.06),
    FloorSpec("3", "Cielo piso 3", "2017_67-102.dxf", 15.84, (120.0, 1748.0, 5960.0, 4900.0), 534.98, 4278.48),
    FloorSpec("4", "Cielo piso 4", "2017_67-103.dxf", 19.80, (127.0, 3767.0, 5976.0, 6849.0), 490.34, 6297.31),
]


LAYER_CATEGORIES = {
    "RLE-VIGA": "beam",
    "RLE-MURO": "wall",
    "RLA-MURO INV DILATADO": "cad_reference",
    "RLE-PILAR": "column_plan",
    "RLE-FUNDACION": "cad_reference",
    "RLE-LOSA": "slab_edge",
    "RLA-LOSAS": "slab_label",
    "RLE-EJES": "axis",
}

CATEGORY_COLORS = {
    "beam": "#1f77b4",
    "wall": "#2ca02c",
    "column": "#ff7f0e",
    "column_plan": "#ff7f0e",
    "slab_edge": "#999999",
    "slab": "#8fb8ff",
    "slab_label": "#bbbbbb",
    "axis": "#d62728",
    "diaphragm": "#9467bd",
    "support": "#000000",
    "cad_reference": "#7d8794",
}


def point_inside_bbox(point: tuple[float, float], bbox: tuple[float, float, float, float]) -> bool:
    x_min, y_min, x_max, y_max = bbox
    x, y = point
    return x_min <= x <= x_max and y_min <= y <= y_max


def segment_inside_bbox(points: list[tuple[float, float]], bbox: tuple[float, float, float, float]) -> bool:
    if not points:
        return False
    inside_count = sum(1 for point in points if point_inside_bbox(point, bbox))
    return inside_count >= max(1, len(points) // 2)


def transform_point(point_cm: tuple[float, float], floor: FloorSpec) -> tuple[float, float, float]:
    x_cm, y_cm = point_cm
    x_m = (x_cm - floor.origin_x_cm) / 100.0
    y_m = (floor.origin_y_cm - y_cm) / 100.0
    return x_m, y_m, floor.z_m


def entity_segments(entity) -> Iterable[list[tuple[float, float]]]:
    entity_type = entity.dxftype()
    if entity_type == "LINE":
        start = entity.dxf.start
        end = entity.dxf.end
        yield [(start.x, start.y), (end.x, end.y)]
    elif entity_type == "LWPOLYLINE":
        points = [(point[0], point[1]) for point in entity.get_points()]
        for first, second in zip(points, points[1:]):
            yield [first, second]
        if entity.closed and len(points) > 2:
            yield [points[-1], points[0]]


def entity_text(entity) -> str | None:
    if entity.dxftype() == "TEXT":
        return entity.dxf.text
    if entity.dxftype() == "MTEXT":
        return entity.text
    return None


def text_category(text: str) -> str | None:
    upper = text.upper().replace(" ", "")
    if upper.startswith("V.M"):
        return "steel_beam_label"
    if upper.startswith("V.") or upper.startswith("+V.") or upper.startswith("V.S") or upper.startswith("V.I"):
        return "beam_label"
    if upper.startswith("P.") or upper.startswith("P.M"):
        return "column_label"
    if upper.startswith("M.H.A") or upper.startswith("M.I"):
        return "wall_label"
    return None


def extract_floor_labels(floor: FloorSpec) -> list[dict[str, object]]:
    doc = ezdxf.readfile(DXF_DIR / floor.dxf_name)
    labels: list[dict[str, object]] = []
    label_index = 1
    for entity in doc.modelspace():
        if entity.dxf.layer != "RLE-TEXTO-1":
            continue
        raw_text = entity_text(entity)
        if not raw_text:
            continue
        text = " ".join(raw_text.replace("\\P", " ").split())
        category = text_category(text)
        if category is None:
            continue
        insert = entity.dxf.insert
        point = (insert.x, insert.y)
        if not point_inside_bbox(point, floor.bbox_cm):
            continue
        x_m, y_m, z_m = transform_point(point, floor)
        labels.append(
            {
                "labelTag": f"LBL_{floor.floor_id}_{category}_{label_index:04d}",
                "floor": floor.floor_id,
                "floor_label": floor.label,
                "source_dxf": floor.dxf_name,
                "source_layer": entity.dxf.layer,
                "category": category,
                "text": text,
                "point": [x_m, y_m, z_m],
                "section_hint": normalize_section_hint(text),
            }
        )
        label_index += 1
    return labels


def normalize_section_hint(text: str) -> dict[str, object]:
    compact = text.upper().replace(" ", "")
    wall_match = re.search(r"E=([0-9]+)", compact)
    if wall_match:
        return {"kind": "wall", "thickness_m": int(wall_match.group(1)) / 100.0}
    rect_match = re.search(r"([0-9]+)[X/]([0-9]+)", compact)
    if rect_match:
        width_cm = int(rect_match.group(1))
        height_cm = int(rect_match.group(2))
        return {"kind": "rectangular", "width_m": width_cm / 100.0, "height_m": height_cm / 100.0}
    return {"kind": "unknown"}


def segment_length_m(segment: list[tuple[float, float, float]]) -> float:
    start, end = segment
    return math.dist(start, end)


def extract_floor_segments(floor: FloorSpec) -> list[dict[str, object]]:
    doc = ezdxf.readfile(DXF_DIR / floor.dxf_name)
    segments: list[dict[str, object]] = []
    element_index = 1
    for entity in doc.modelspace():
        layer = entity.dxf.layer
        category = LAYER_CATEGORIES.get(layer)
        if category is None:
            continue
        for raw_segment in entity_segments(entity):
            if not segment_inside_bbox(raw_segment, floor.bbox_cm):
                continue
            segment = [transform_point(point, floor) for point in raw_segment]
            length = segment_length_m(segment)
            if length < 0.05:
                continue
            segment_id = f"CAD_{floor.floor_id}_{category}_{element_index:04d}"
            segments.append(
                {
                    "elementTag": segment_id,
                    "floor": floor.floor_id,
                    "floor_label": floor.label,
                    "source_dxf": floor.dxf_name,
                    "source_layer": layer,
                    "category": category,
                    "points": segment,
                    "length_m": length,
                    "confidence": "medium" if category in {"beam", "wall", "column_plan"} else "low",
                }
            )
            element_index += 1
    return segments


def floor_diaphragms(segments: list[dict[str, object]]) -> list[dict[str, object]]:
    diaphragms = []
    for floor in FLOORS:
        if floor.floor_id == "base":
            continue
        floor_points = [point for segment in segments if segment["floor"] == floor.floor_id for point in segment["points"]]
        if not floor_points:
            continue
        xs = [point[0] for point in floor_points]
        ys = [point[1] for point in floor_points]
        z = floor.z_m
        polygon = [
            (min(xs), min(ys), z),
            (max(xs), min(ys), z),
            (max(xs), max(ys), z),
            (min(xs), max(ys), z),
            (min(xs), min(ys), z),
        ]
        diaphragms.append({"floor": floor.floor_id, "category": "diaphragm", "points": polygon})
    return diaphragms


def previous_floor_z(floor_id: str) -> float:
    previous = 0.0
    for floor in FLOORS:
        if floor.floor_id == floor_id:
            return previous
        previous = floor.z_m
    return 0.0


def make_linear_solid(
    tag: str,
    category: str,
    floor: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    width_m: float,
    height_m: float,
    z_center_m: float,
    source: dict[str, object],
) -> dict[str, object]:
    return {
        "solidTag": tag,
        "category": category,
        "kind": "linear_prism",
        "floor": floor,
        "sourceTag": source.get("elementTag"),
        "source_layer": source.get("source_layer"),
        "source_dxf": source.get("source_dxf"),
        "start": [start[0], start[1], z_center_m],
        "end": [end[0], end[1], z_center_m],
        "width_m": width_m,
        "height_m": height_m,
        "length_m": math.dist((start[0], start[1], 0.0), (end[0], end[1], 0.0)),
        "confidence": source.get("confidence", "medium"),
    }


def column_clusters_for_floor(floor_id: str, segments: list[dict[str, object]]) -> list[dict[str, object]]:
    column_segments = [
        segment
        for segment in segments
        if segment["floor"] == floor_id and segment["category"] == "column_plan" and 0.08 <= segment["length_m"] <= 1.50
    ]
    clusters: list[dict[str, object]] = []
    for segment in column_segments:
        points = segment["points"]
        mx = (points[0][0] + points[1][0]) / 2.0
        my = (points[0][1] + points[1][1]) / 2.0
        assigned = None
        for cluster in clusters:
            cx, cy = cluster["center"]
            if math.hypot(mx - cx, my - cy) <= 0.85:
                assigned = cluster
                break
        if assigned is None:
            assigned = {"segments": [], "points": [], "center": (mx, my)}
            clusters.append(assigned)
        assigned["segments"].append(segment)
        assigned["points"].extend(points)
        xs = [point[0] for point in assigned["points"]]
        ys = [point[1] for point in assigned["points"]]
        assigned["center"] = (sum(xs) / len(xs), sum(ys) / len(ys))

    clean_clusters = []
    for cluster in clusters:
        points = cluster["points"]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        clean_clusters.append(
            {
                "center": cluster["center"],
                "width_m": min(max(max(xs) - min(xs), 0.35), 1.20),
                "depth_m": min(max(max(ys) - min(ys), 0.35), 1.20),
                "segments": cluster["segments"],
                "confidence": "medium",
            }
        )
    return clean_clusters


def nearest_cluster(center: tuple[float, float], clusters: list[dict[str, object]], tolerance_m: float = 0.85) -> dict[str, object] | None:
    cx, cy = center
    nearest = None
    nearest_dist = tolerance_m
    for cluster in clusters:
        ox, oy = cluster["center"]
        dist = math.hypot(cx - ox, cy - oy)
        if dist <= nearest_dist:
            nearest = cluster
            nearest_dist = dist
    return nearest


def infer_missing_column_clusters(clusters_by_floor: dict[str, list[dict[str, object]]]) -> None:
    if not clusters_by_floor.get("1S") and clusters_by_floor.get("1"):
        clusters_by_floor["1S"] = [{**cluster, "confidence": "inferred_from_floor_1"} for cluster in clusters_by_floor["1"]]

    floor_ids = [floor.floor_id for floor in FLOORS if floor.floor_id != "base"]
    for index, floor_id in enumerate(floor_ids[1:-1], start=1):
        previous_floor = floor_ids[index - 1]
        next_floor = floor_ids[index + 1]
        current = clusters_by_floor.setdefault(floor_id, [])
        for previous_cluster in clusters_by_floor.get(previous_floor, []):
            if nearest_cluster(previous_cluster["center"], current):
                continue
            next_cluster = nearest_cluster(previous_cluster["center"], clusters_by_floor.get(next_floor, []))
            if next_cluster is None:
                continue
            px, py = previous_cluster["center"]
            nx, ny = next_cluster["center"]
            current.append(
                {
                    "center": ((px + nx) / 2.0, (py + ny) / 2.0),
                    "width_m": max(previous_cluster["width_m"], next_cluster["width_m"]),
                    "depth_m": max(previous_cluster["depth_m"], next_cluster["depth_m"]),
                    "segments": previous_cluster["segments"],
                    "confidence": f"inferred_between_{previous_floor}_{next_floor}",
                }
            )

    for index in range(len(floor_ids) - 1, 0, -1):
        current_floor = floor_ids[index]
        previous_floor = floor_ids[index - 1]
        previous = clusters_by_floor.setdefault(previous_floor, [])
        for cluster in list(clusters_by_floor.get(current_floor, [])):
            if nearest_cluster(cluster["center"], previous):
                continue
            previous.append({**cluster, "confidence": f"inferred_from_above_{current_floor}"})


def generate_column_solids(segments: list[dict[str, object]]) -> list[dict[str, object]]:
    floor_ids = [floor.floor_id for floor in FLOORS if floor.floor_id != "base"]
    clusters_by_floor = {floor_id: column_clusters_for_floor(floor_id, segments) for floor_id in floor_ids}
    infer_missing_column_clusters(clusters_by_floor)

    solids = []
    for floor_id in floor_ids:
        z_top = next(floor.z_m for floor in FLOORS if floor.floor_id == floor_id)
        z_bottom = previous_floor_z(floor_id)
        height = z_top - z_bottom
        for index, cluster in enumerate(clusters_by_floor.get(floor_id, []), start=1):
            cx, cy = cluster["center"]
            solids.append(
                {
                    "solidTag": f"SOL_{floor_id}_column_{index:04d}",
                    "category": "column",
                    "kind": "box",
                    "floor": floor_id,
                    "center": [cx, cy, (z_bottom + z_top) / 2.0],
                    "width_m": cluster["width_m"],
                    "depth_m": cluster["depth_m"],
                    "height_m": height,
                    "length_m": height,
                    "source_layer": "RLE-PILAR",
                    "source_dxf": cluster["segments"][0].get("source_dxf") if cluster["segments"] else "inferred",
                    "sourceTags": [segment.get("elementTag") for segment in cluster["segments"]],
                    "confidence": cluster.get("confidence", "medium"),
                }
            )
    return solids


def merged_wall_segments_for_floor(floor_id: str, segments: list[dict[str, object]]) -> list[dict[str, object]]:
    wall_segments = [segment for segment in segments if segment["floor"] == floor_id and segment["category"] == "wall"]
    buckets: dict[tuple[str, float], list[tuple[float, float, dict[str, object]]]] = defaultdict(list)
    passthrough: list[dict[str, object]] = []

    for segment in wall_segments:
        start, end = segment["points"]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if abs(dx) <= 0.15:
            fixed = round(((start[0] + end[0]) / 2.0) / 0.15) * 0.15
            a, b = sorted((start[1], end[1]))
            buckets[("V", fixed)].append((a, b, segment))
        elif abs(dy) <= 0.15:
            fixed = round(((start[1] + end[1]) / 2.0) / 0.15) * 0.15
            a, b = sorted((start[0], end[0]))
            buckets[("H", fixed)].append((a, b, segment))
        else:
            passthrough.append(segment)

    merged: list[dict[str, object]] = []
    merge_index = 1
    for (orientation, fixed), intervals in buckets.items():
        intervals.sort(key=lambda item: item[0])
        current_a, current_b, current_source = intervals[0]
        for a, b, source in intervals[1:]:
            if a <= current_b + 0.35:
                current_b = max(current_b, b)
                continue
            merged.append(make_merged_wall_segment(floor_id, orientation, fixed, current_a, current_b, current_source, merge_index))
            merge_index += 1
            current_a, current_b, current_source = a, b, source
        merged.append(make_merged_wall_segment(floor_id, orientation, fixed, current_a, current_b, current_source, merge_index))
        merge_index += 1

    merged.extend(passthrough)
    return [segment for segment in merged if segment_length_m(segment["points"]) >= 0.35]


def make_merged_wall_segment(
    floor_id: str,
    orientation: str,
    fixed: float,
    interval_start: float,
    interval_end: float,
    source: dict[str, object],
    index: int,
) -> dict[str, object]:
    z = source["points"][0][2]
    if orientation == "V":
        points = [(fixed, interval_start, z), (fixed, interval_end, z)]
    else:
        points = [(interval_start, fixed, z), (interval_end, fixed, z)]
    return {
        "elementTag": f"MERGED_{floor_id}_wall_{index:04d}",
        "floor": floor_id,
        "floor_label": source.get("floor_label"),
        "source_dxf": source.get("source_dxf"),
        "source_layer": "RLE-MURO_merged",
        "category": "wall",
        "points": points,
        "length_m": segment_length_m(points),
        "confidence": "merged_from_RLE-MURO",
    }


def generate_wall_solids(segments: list[dict[str, object]]) -> list[dict[str, object]]:
    solids = []
    counter = 0
    for floor in FLOORS:
        if floor.floor_id == "base":
            continue
        for segment in merged_wall_segments_for_floor(floor.floor_id, segments):
            start, end = segment["points"]
            z_bottom = previous_floor_z(floor.floor_id)
            z_top = start[2]
            counter += 1
            solids.append(
                make_linear_solid(
                    f"SOL_{floor.floor_id}_wall_{counter:04d}",
                    "wall",
                    floor.floor_id,
                    tuple(start),
                    tuple(end),
                    0.22,
                    z_top - z_bottom,
                    (z_bottom + z_top) / 2.0,
                    segment,
                )
            )
    return solids


def bottom_z(solid: dict[str, object]) -> float:
    center = solid.get("center")
    if center:
        return float(center[2]) - float(solid.get("height_m", 0.0)) / 2.0
    return float(solid.get("start", [0.0, 0.0, 0.0])[2]) - float(solid.get("height_m", 0.0)) / 2.0


def generate_support_solids(solids: list[dict[str, object]]) -> list[dict[str, object]]:
    supports = []
    counter = 0
    for solid in solids:
        if solid["category"] not in {"column", "wall"} or abs(bottom_z(solid)) > 0.05:
            continue
        counter += 1
        if solid["category"] == "column":
            cx, cy, _ = solid["center"]
            supports.append(
                {
                    "solidTag": f"SOL_base_support_{counter:04d}",
                    "category": "support",
                    "kind": "box",
                    "floor": "base",
                    "center": [cx, cy, -0.15],
                    "width_m": max(float(solid["width_m"]) * 1.8, 0.90),
                    "depth_m": max(float(solid["depth_m"]) * 1.8, 0.90),
                    "height_m": 0.30,
                    "length_m": 0.30,
                    "source_layer": "generated_connected_support",
                    "source_dxf": solid.get("source_dxf"),
                    "sourceTags": [solid.get("solidTag")],
                    "confidence": "qa_connected",
                }
            )
        else:
            start = tuple(solid["start"])
            end = tuple(solid["end"])
            supports.append(
                make_linear_solid(
                    f"SOL_base_support_{counter:04d}",
                    "support",
                    "base",
                    start,
                    end,
                    max(float(solid["width_m"]) * 1.8, 0.45),
                    0.30,
                    -0.15,
                    {"elementTag": solid.get("solidTag"), "source_layer": "generated_connected_support", "source_dxf": solid.get("source_dxf"), "confidence": "qa_connected"},
                )
            )
    return supports


def cluster_column_segments(floor_id: str, segments: list[dict[str, object]]) -> list[dict[str, object]]:
    return [solid for solid in generate_column_solids(segments) if solid["floor"] == floor_id]


def generate_solids(segments: list[dict[str, object]], diaphragms: list[dict[str, object]]) -> list[dict[str, object]]:
    solids: list[dict[str, object]] = []
    counters: dict[str, int] = {"beam": 0, "slab": 0}

    for segment in segments:
        floor = str(segment["floor"])
        category = str(segment["category"])
        if segment["length_m"] < 0.35:
            continue
        start, end = segment["points"]
        if category == "beam" and floor != "base":
            counters["beam"] += 1
            solids.append(
                make_linear_solid(
                    f"SOL_{floor}_beam_{counters['beam']:04d}",
                    "beam",
                    floor,
                    tuple(start),
                    tuple(end),
                    0.32,
                    0.60,
                    start[2] - 0.30,
                    segment,
                )
            )

    solids.extend(generate_wall_solids(segments))
    solids.extend(generate_column_solids(segments))
    solids.extend(generate_support_solids(solids))

    for diaphragm in diaphragms:
        points = diaphragm["points"]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        z = points[0][2]
        counters["slab"] += 1
        solids.append(
            {
                "solidTag": f"SOL_{diaphragm['floor']}_slab_{counters['slab']:04d}",
                "category": "slab",
                "kind": "slab_box",
                "floor": diaphragm["floor"],
                "center": [(min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, z - 0.04],
                "width_m": max(xs) - min(xs),
                "depth_m": max(ys) - min(ys),
                "height_m": 0.08,
                "area_m2": (max(xs) - min(xs)) * (max(ys) - min(ys)),
                "source_layer": "generated_diaphragm_bbox",
                "source_dxf": "generated",
                "confidence": "low",
            }
        )
    return solids


def write_model_json(path: Path, segments: list[dict[str, object]], labels: list[dict[str, object]], diaphragms: list[dict[str, object]], solids: list[dict[str, object]]) -> None:
    summary: dict[str, dict[str, int]] = {}
    for segment in segments:
        floor_summary = summary.setdefault(str(segment["floor"]), {})
        category = str(segment["category"])
        floor_summary[category] = floor_summary.get(category, 0) + 1
    payload = {
        "model": "P1L2 - edificio completo desde CAD",
        "units": "m",
        "coordinate_source": "DXF 2017_67 convertido desde DWG; coordenadas CAD en cm transformadas a m.",
        "floors": [floor.__dict__ for floor in FLOORS],
        "colors": CATEGORY_COLORS,
        "summary": summary,
        "segments": segments,
        "solids": solids,
        "labels": labels,
        "diaphragms": diaphragms,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_unity_export(path: Path, segments: list[dict[str, object]], labels: list[dict[str, object]], diaphragms: list[dict[str, object]], solids: list[dict[str, object]]) -> None:
    payload = {
        "model": "P1L2 - Unity/web QA viewer export",
        "units": "m",
        "availableToggles": ["beam", "wall", "column", "support", "slab", "axis", "diaphragm", "cad_reference", "ids"],
        "colors": CATEGORY_COLORS,
        "solids": solids,
        "segments": segments,
        "labels": labels,
        "diaphragms": diaphragms,
        "notes": [
            "Los segmentos vienen de capas CAD estructurales y ya estan apilados en Z por piso.",
            "Cada segmento tiene elementTag para inspeccion en Unity.",
            "Los CAD/DXF originales no se versionan en Git; este JSON si puede versionarse como contrato de datos."
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def plot_model(path: Path, segments: list[dict[str, object]], diaphragms: list[dict[str, object]]) -> None:
    fig = plt.figure(figsize=(15, 9))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("P1L2 - modelo 3D preliminar desde CAD")
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")

    draw_order = ["diaphragm", "axis", "slab_edge", "support", "wall", "column_plan", "beam"]
    for diaphragm in diaphragms:
        points = diaphragm["points"]
        ax.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            [point[2] for point in points],
            color=CATEGORY_COLORS["diaphragm"],
            linewidth=1.2,
            linestyle=":",
            alpha=0.8,
        )

    for category in draw_order:
        if category == "diaphragm":
            continue
        color = CATEGORY_COLORS[category]
        for segment in segments:
            if segment["category"] != category:
                continue
            points = segment["points"]
            alpha = 0.35 if category in {"axis", "slab_edge", "slab_label"} else 0.95
            linewidth = 0.7 if category in {"axis", "slab_edge", "slab_label"} else 1.8
            ax.plot(
                [points[0][0], points[1][0]],
                [points[0][1], points[1][1]],
                [points[0][2], points[1][2]],
                color=color,
                linewidth=linewidth,
                alpha=alpha,
            )

    for floor in FLOORS:
        ax.text(-7.0, -3.0, floor.z_m, floor.floor_id, fontsize=9, color="black")

    for category, color in CATEGORY_COLORS.items():
        ax.plot([], [], [], color=color, label=category)
    ax.legend(loc="upper left")
    ax.view_init(elev=24, azim=-58)
    ax.set_box_aspect((50, 18, 20))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_floor_qc(path: Path, segments: list[dict[str, object]]) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(14, 16))
    flat_axes = list(axes.flat)
    for ax, floor in zip(flat_axes, FLOORS):
        ax.set_title(f"{floor.floor_id} - {floor.label}")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        for category in ["axis", "slab_edge", "support", "wall", "column_plan", "beam"]:
            color = CATEGORY_COLORS[category]
            for segment in segments:
                if segment["floor"] != floor.floor_id or segment["category"] != category:
                    continue
                points = segment["points"]
                alpha = 0.25 if category in {"axis", "slab_edge"} else 0.9
                linewidth = 0.5 if category in {"axis", "slab_edge"} else 1.2
                ax.plot(
                    [points[0][0], points[1][0]],
                    [points[0][1], points[1][1]],
                    color=color,
                    linewidth=linewidth,
                    alpha=alpha,
                )
        ax.grid(True, linewidth=0.3, alpha=0.4)
    legend_axis = flat_axes[len(FLOORS)] if len(FLOORS) < len(flat_axes) else flat_axes[0]
    if len(FLOORS) < len(flat_axes):
        legend_axis.axis("off")
    for category, color in CATEGORY_COLORS.items():
        if category in {"diaphragm", "slab_label"}:
            continue
        legend_axis.plot([], [], color=color, label=category)
    legend_axis.legend(loc="upper right" if len(FLOORS) >= len(flat_axes) else "center")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    segments: list[dict[str, object]] = []
    labels: list[dict[str, object]] = []
    for floor in FLOORS:
        segments.extend(extract_floor_segments(floor))
        labels.extend(extract_floor_labels(floor))
    diaphragms = floor_diaphragms(segments)
    solids = generate_solids(segments, diaphragms)

    write_model_json(RESULTS_DIR / "cad_model_3d_segments.json", segments, labels, diaphragms, solids)
    write_unity_export(UNITY_EXPORT_DIR / "model_viewer.json", segments, labels, diaphragms, solids)
    plot_model(RESULTS_DIR / "cad_model_3d_colored.png", segments, diaphragms)
    plot_floor_qc(RESULTS_DIR / "cad_model_floor_qc.png", segments)

    print("Modelo CAD 3D preliminar generado")
    print(f"  segmentos: {len(segments)}")
    print(f"  solidos viewer: {len(solids)}")
    print(f"  etiquetas estructurales: {len(labels)}")
    for floor in FLOORS:
        count = sum(1 for segment in segments if segment["floor"] == floor.floor_id)
        print(f"  piso {floor.floor_id}: {count} segmentos")
    print(f"  {RESULTS_DIR / 'cad_model_3d_segments.json'}")
    print(f"  {UNITY_EXPORT_DIR / 'model_viewer.json'}")
    print(f"  {RESULTS_DIR / 'cad_model_3d_colored.png'}")
    print(f"  {RESULTS_DIR / 'cad_model_floor_qc.png'}")


if __name__ == "__main__":
    main()
