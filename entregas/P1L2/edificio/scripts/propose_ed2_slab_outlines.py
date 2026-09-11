#!/usr/bin/env python3
"""Propone, sin aplicar, los perimetros de losa de EDIFICIO_2.

Los vertices se obtienen de los tramos exteriores RLE-LOSA de 2024_22-101/102.
Cada lado se contrasta con RLE-LOSA y con el contexto RLE-VIGA/RLE-MURO. La
salida es evidencia de revision; no modifica geometria, FE, cargas o resultados.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import ezdxf
from ezdxf import bbox as ezbbox
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point, Polygon

import audit_slab_topology_all as slab_audit


REPO = Path(__file__).resolve().parents[4]
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/slabs/ed2_outline_proposal"
OUT_JSON = OUT_DIR / "ed2_slab_outline_proposal.json"
OUT_MD = OUT_DIR / "REPORT.md"
FLOORS = ("S1", "P1", "P2", "P3", "P4")

# 101 dibuja una planta comun S1-P3. El pequeno resalto noroeste se cierra
# contra los muros perimetrales que llegan al borde superior RLE-LOSA.
COMMON_S1_P3 = [
    [-4.148008, -1.149332],
    [27.851994, -1.149332],
    [27.851994, 16.500668],
    [-3.348008, 16.500668],
    [-3.348008, 17.240668],
    [-4.148008, 17.240668],
]

# 102 muestra directamente el escalon superior hasta x=-1.898.
P4_OUTLINE = [
    [-4.148008, -1.149332],
    [27.851994, -1.149332],
    [27.851994, 16.500668],
    [-1.898008, 16.500668],
    [-1.898008, 17.240668],
    [-4.148008, 17.240668],
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structural_segments(floor: str) -> tuple[Path, list[dict[str, object]]]:
    path, bbox, origin = slab_audit.source_spec("EDIFICIO_2", floor)
    doc = ezdxf.readfile(path)
    rows: list[dict[str, object]] = []
    for entity in doc.modelspace():
        if entity.dxf.layer not in {"RLE-VIGA", "RLE-MURO"}:
            continue
        for index, (first, second) in enumerate(slab_audit.raw_segments(entity)):
            if not (slab_audit.inside(first, bbox) or slab_audit.inside(second, bbox)):
                continue
            start = slab_audit.transform(first, origin, "EDIFICIO_2")
            end = slab_audit.transform(second, origin, "EDIFICIO_2")
            if math.dist(start, end) < 0.02:
                continue
            rows.append(
                {
                    "handle": str(entity.dxf.handle),
                    "segment_index": index,
                    "layer": str(entity.dxf.layer),
                    "start": start,
                    "end": end,
                }
            )
    return path, rows


def entity_text(entity) -> str:
    if entity.dxftype() == "TEXT":
        return str(entity.dxf.text)
    if entity.dxftype() == "MTEXT":
        return str(entity.plain_text())
    return ""


def text_rows(floor: str) -> list[dict[str, object]]:
    path, bbox, origin = slab_audit.source_spec("EDIFICIO_2", floor)
    doc = ezdxf.readfile(path)
    rows = []
    for entity in doc.modelspace():
        if entity.dxftype() not in {"TEXT", "MTEXT"}:
            continue
        text = re.sub(r"\s+", " ", entity_text(entity)).strip()
        if not text:
            continue
        insert = entity.dxf.insert
        point = (float(insert.x), float(insert.y))
        if not slab_audit.inside(point, bbox):
            continue
        rows.append(
            {
                "handle": str(entity.dxf.handle),
                "layer": str(entity.dxf.layer),
                "text": text,
                "point": slab_audit.transform(point, origin, "EDIFICIO_2"),
            }
        )
    return rows


def slab_note_markers(floor: str) -> list[dict[str, object]]:
    path, bbox, origin = slab_audit.source_spec("EDIFICIO_2", floor)
    doc = ezdxf.readfile(path)
    rows = []
    for entity in doc.modelspace().query("INSERT"):
        name = str(entity.dxf.name)
        if "LOSA-NE" not in name.upper():
            continue
        insert = entity.dxf.insert
        point = (float(insert.x), float(insert.y))
        if slab_audit.inside(point, bbox):
            extents = ezbbox.extents([entity])
            marker_bounds = None
            if extents.has_data:
                corners = [
                    (float(extents.extmin.x), float(extents.extmin.y)),
                    (float(extents.extmax.x), float(extents.extmax.y)),
                ]
                transformed = [slab_audit.transform(corner, origin, "EDIFICIO_2") for corner in corners]
                marker_bounds = [
                    min(point[0] for point in transformed),
                    min(point[1] for point in transformed),
                    max(point[0] for point in transformed),
                    max(point[1] for point in transformed),
                ]
            rows.append(
                {
                    "handle": str(entity.dxf.handle),
                    "block": name,
                    "point": slab_audit.transform(point, origin, "EDIFICIO_2"),
                    "bounds_m": marker_bounds,
                }
            )
    return rows


def distance_to_bounds(point: list[float], bounds: list[float]) -> float:
    x, y = point
    x0, y0, x1, y1 = bounds
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def internal_feature_audit(floor: str, outline: list[list[float]], slab_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    polygon = Polygon(outline)
    texts = text_rows(floor)
    markers = slab_note_markers(floor)
    features = []
    for component in slab_audit.component_summary(slab_rows):
        x0, y0, x1, y1 = component["bounds_m"]
        center = [(x0 + x1) / 2.0, (y0 + y1) / 2.0]
        if not polygon.buffer(-0.05).contains(Point(center)):
            continue
        # Los componentes extensos que tocan el contorno son parte del borde exterior.
        if x0 <= polygon.bounds[0] + 0.10 or y0 <= polygon.bounds[1] + 0.10 or x1 >= polygon.bounds[2] - 0.10 or y1 >= polygon.bounds[3] - 0.10:
            continue
        nearby = [
            {**row, "distance_to_feature_m": round(distance_to_bounds(row["point"], component["bounds_m"]), 6)}
            for row in texts
            if distance_to_bounds(row["point"], component["bounds_m"]) <= 2.0
        ]
        nearby_markers = [
            {**row, "distance_to_feature_m": round(distance_to_bounds(row["point"], component["bounds_m"]), 6)}
            for row in markers
            if distance_to_bounds(row["point"], component["bounds_m"]) <= 1.0
        ]
        features.append(
            {
                "bounds_m": component["bounds_m"],
                "segment_count": component["segment_count"],
                "open_node_count": component["open_node_count"],
                "closed_by_endpoint_graph": component["closed_by_endpoint_graph"],
                "handles": component["handles"],
                "nearby_texts": sorted(nearby, key=lambda row: (row["distance_to_feature_m"], row["text"])),
                "nearby_losa_ne_markers": sorted(nearby_markers, key=lambda row: row["distance_to_feature_m"]),
                "classification": "REVIEW_REQUIRED_HOLE_OR_PANEL_EDGE",
                "marker_interpretation": "losa-ne aparece una vez por numerosos panos; no significa por si solo ausencia de losa",
            }
        )
    return features


def parallel(first: LineString, second: LineString, tolerance: float = 0.015) -> bool:
    (ax, ay), (bx, by) = first.coords
    (cx, cy), (dx, dy) = second.coords
    ux, uy = bx - ax, by - ay
    vx, vy = dx - cx, dy - cy
    denominator = max(first.length * second.length, 1.0e-12)
    return abs(ux * vy - uy * vx) / denominator <= tolerance


def evidence_for_edge(edge: LineString, rows: list[dict[str, object]], tolerance: float) -> dict[str, object]:
    matches = []
    intervals = []
    for row in rows:
        candidate = LineString([row["start"], row["end"]])
        if not parallel(edge, candidate) or edge.distance(candidate) > tolerance:
            continue
        overlap = edge.buffer(tolerance, cap_style=2).intersection(candidate).length
        if overlap <= 0.02:
            continue
        first = max(0.0, min(edge.length, edge.project(Point(candidate.coords[0]))))
        second = max(0.0, min(edge.length, edge.project(Point(candidate.coords[-1]))))
        if second < first:
            first, second = second, first
        if second - first > 0.02:
            intervals.append((first, second))
        matches.append(
            {
                "handle": row["handle"],
                "segment_index": row["segment_index"],
                "layer": row["layer"],
                "distance_m": round(edge.distance(candidate), 6),
                "overlap_m": round(min(overlap, edge.length), 6),
            }
        )
    merged = []
    for first, second in sorted(intervals):
        if not merged or first > merged[-1][1] + tolerance:
            merged.append([first, second])
        else:
            merged[-1][1] = max(merged[-1][1], second)
    union_length = sum(second - first for first, second in merged)
    return {
        "coverage_ratio": round(union_length / edge.length, 6),
        "matches": sorted(matches, key=lambda item: (item["distance_m"], -item["overlap_m"], item["handle"])),
    }


def classify_edges(floor: str, outline: list[list[float]]) -> tuple[list[dict[str, object]], list[dict[str, object]], Path]:
    path, slab_rows = slab_audit.segments_for("EDIFICIO_2", floor)
    _same_path, structural_rows = structural_segments(floor)
    edges = []
    for index, start in enumerate(outline):
        end = outline[(index + 1) % len(outline)]
        edge = LineString([start, end])
        direct = evidence_for_edge(edge, slab_rows, 0.035)
        context = evidence_for_edge(edge, structural_rows, 0.20)
        if direct["coverage_ratio"] >= 0.95:
            confidence = "CONFIRMED_RLE_LOSA"
        elif direct["coverage_ratio"] + context["coverage_ratio"] >= 0.90:
            confidence = "LIKELY_RLE_PLUS_STRUCTURE"
        elif context["coverage_ratio"] >= 0.75:
            confidence = "LIKELY_STRUCTURAL_CLOSURE"
        else:
            confidence = "REVIEW_REQUIRED"
        edges.append(
            {
                "edge_index": index,
                "start": start,
                "end": end,
                "length_m": round(edge.length, 6),
                "confidence": confidence,
                "rle_losa": direct,
                "structural_context": context,
            }
        )
    return edges, slab_rows, path


def render(floor: str, outline: list[list[float]], edges: list[dict[str, object]], slab_rows: list[dict[str, object]]) -> str:
    path, structural_rows = structural_segments(floor)
    _ = path
    fig, ax = plt.subplots(figsize=(13, 7))
    for row in structural_rows:
        color = "#9aa0a6" if row["layer"] == "RLE-VIGA" else "#c7a26b"
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color=color, linewidth=0.45, alpha=0.45)
    for row in slab_rows:
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color="#5f6368", linewidth=1.0)
    colors = {
        "CONFIRMED_RLE_LOSA": "#188038",
        "LIKELY_RLE_PLUS_STRUCTURE": "#f29900",
        "LIKELY_STRUCTURAL_CLOSURE": "#f29900",
        "REVIEW_REQUIRED": "#d93025",
    }
    for edge in edges:
        ax.plot([edge["start"][0], edge["end"][0]], [edge["start"][1], edge["end"][1]], color=colors[edge["confidence"]], linewidth=3.0)
        x = (edge["start"][0] + edge["end"][0]) / 2.0
        y = (edge["start"][1] + edge["end"][1]) / 2.0
        ax.text(x, y, str(edge["edge_index"]), fontsize=8, color="#202124", bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"})
    poly = Polygon(outline)
    x, y = poly.exterior.xy
    ax.fill(x, y, color="#4cc9f0", alpha=0.14)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    ax.set_title(f"EDIFICIO_2 {floor}: propuesta de perimetro (sin aplicar)")
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    output = OUT_DIR / f"edificio_2_{floor.lower()}_outline_proposal.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "status": "PROPOSAL_ONLY_NOT_APPLIED",
        "building": "EDIFICIO_2",
        "participates_in_FE": False,
        "source_priority": "2024_22 RLE-LOSA > RLE-VIGA/RLE-MURO > inference",
        "common_plan_s1_p3": "CONFIRMED_BY_2024_22-101_TITLE",
        "floors": {},
        "inputs": {},
    }
    report = [
        "# Propuesta de perímetros de losa — EDIFICIO_2",
        "",
        "Estado: `PROPOSAL_ONLY_NOT_APPLIED`. No modifica modelo visual, FE, cargas ni resultados.",
        "",
        "La planta 2024_22-101 aplica explícitamente desde cielo S1 hasta cielo P3. P4 usa 2024_22-102 y muestra un resalto noroeste mayor.",
        "",
        "| Piso | Área propuesta | Bordes directos | Bordes probables | Revisión requerida |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for floor in FLOORS:
        outline = P4_OUTLINE if floor == "P4" else COMMON_S1_P3
        polygon = Polygon(outline)
        if not polygon.is_valid or polygon.area <= 0:
            raise RuntimeError(f"Contorno invalido para {floor}")
        edges, slab_rows, source_path = classify_edges(floor, outline)
        counts = {name: sum(edge["confidence"] == name for edge in edges) for name in {edge["confidence"] for edge in edges}}
        overlay = render(floor, outline, edges, slab_rows)
        internal_features = internal_feature_audit(floor, outline, slab_rows)
        payload["floors"][floor] = {
            "source_sheet": source_path.name,
            "source_sha256": sha256(source_path),
            "outline_xy": outline,
            "area_m2": round(polygon.area, 6),
            "perimeter_m": round(polygon.length, 6),
            "edge_evidence": edges,
            "confidence_counts": counts,
            "internal_rle_features": internal_features,
            "internal_feature_policy": "NOT_CLASSIFIED_AS_HOLES",
            "losa_ne_markers": slab_note_markers(floor),
            "overlay": overlay,
        }
        payload["inputs"][str(source_path.relative_to(REPO)).replace("\\", "/")] = sha256(source_path)
        direct = counts.get("CONFIRMED_RLE_LOSA", 0)
        probable = counts.get("LIKELY_RLE_PLUS_STRUCTURE", 0) + counts.get("LIKELY_STRUCTURAL_CLOSURE", 0)
        review = counts.get("REVIEW_REQUIRED", 0)
        report.append(f"| {floor} | {polygon.area:.3f} m² | {direct} | {probable} | {review} |")
    report.extend(
        [
            "",
            "Los trazos interiores no se descuentan todavía: no hay una etiqueta inequívoca que permita distinguir huecos de bordes de paño interrumpidos por vigas.",
            "",
            "Los lados rojos de los overlays deben resolverse antes de aplicar la superficie. Verde es borde RLE-LOSA directo y naranja es cierre respaldado por estructura.",
        ]
    )
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("ED2_SLAB_OUTLINE_PROPOSAL: COMPLETE_NOT_APPLIED")
    for floor, row in payload["floors"].items():
        print(floor, row["area_m2"], row["confidence_counts"])


if __name__ == "__main__":
    main()
