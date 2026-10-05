#!/usr/bin/env python3
"""Evalua candidatos de perimetro ED1 sin aplicarlos al modelo."""

from __future__ import annotations

import json
import math
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon

import audit_slab_topology_all as slab_audit
from propose_ed2_slab_outlines import evidence_for_edge, sha256


REPO = Path(__file__).resolve().parents[4]
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/slabs/ed1_outline_proposal"
OUT_JSON = OUT_DIR / "ed1_slab_outline_proposal.json"
OUT_MD = OUT_DIR / "REPORT.md"

CANDIDATES = {
    "P2": [
        [27.140857, -0.968476],
        [72.840861, -0.968476],
        [72.840861, 16.681524],
        [27.140857, 16.681524],
    ],
    "P3": [
        [27.140863, -0.968514],
        [78.640835, -0.968514],
        [78.640835, 17.481471],
        [72.140835, 17.481471],
        [72.140835, 16.681508],
        [27.140863, 16.681508],
    ],
}


def structural_rows(floor: str) -> tuple[Path, list[dict[str, object]]]:
    path, bbox, origin = slab_audit.source_spec("EDIFICIO_1", floor)
    doc = ezdxf.readfile(path)
    rows = []
    for entity in doc.modelspace():
        if entity.dxf.layer not in {"RLE-VIGA", "RLE-MURO"}:
            continue
        for index, (first, second) in enumerate(slab_audit.raw_segments(entity)):
            if not (slab_audit.inside(first, bbox) or slab_audit.inside(second, bbox)):
                continue
            start = slab_audit.transform(first, origin, "EDIFICIO_1")
            end = slab_audit.transform(second, origin, "EDIFICIO_1")
            if math.dist(start, end) >= 0.02:
                rows.append({"handle": str(entity.dxf.handle), "segment_index": index, "layer": str(entity.dxf.layer), "start": start, "end": end})
    return path, rows


def classify(floor: str, outline: list[list[float]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], Path]:
    path, slab_rows = slab_audit.segments_for("EDIFICIO_1", floor)
    _path, structure = structural_rows(floor)
    edges = []
    for index, start in enumerate(outline):
        end = outline[(index + 1) % len(outline)]
        edge = LineString([start, end])
        direct = evidence_for_edge(edge, slab_rows, 0.035)
        context = evidence_for_edge(edge, structure, 0.20)
        if direct["coverage_ratio"] >= 0.95:
            confidence = "CONFIRMED_RLE_LOSA"
        elif direct["coverage_ratio"] + context["coverage_ratio"] >= 0.90:
            confidence = "LIKELY_RLE_PLUS_STRUCTURE"
        elif context["coverage_ratio"] >= 0.75:
            confidence = "LIKELY_STRUCTURAL_CLOSURE"
        else:
            confidence = "REVIEW_REQUIRED"
        edges.append({"edge_index": index, "start": start, "end": end, "length_m": round(edge.length, 6), "confidence": confidence, "rle_losa": direct, "structural_context": context})
    return edges, slab_rows, structure, path


def render(floor: str, outline: list[list[float]], edges: list[dict[str, object]], slabs: list[dict[str, object]], structure: list[dict[str, object]]) -> str:
    fig, ax = plt.subplots(figsize=(14, 7))
    for row in structure:
        color = "#9aa0a6" if row["layer"] == "RLE-VIGA" else "#c7a26b"
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color=color, linewidth=0.45, alpha=0.45)
    for row in slabs:
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color="#5f6368", linewidth=1.0)
    colors = {"CONFIRMED_RLE_LOSA": "#188038", "LIKELY_RLE_PLUS_STRUCTURE": "#f29900", "LIKELY_STRUCTURAL_CLOSURE": "#f29900", "REVIEW_REQUIRED": "#d93025"}
    for edge in edges:
        ax.plot([edge["start"][0], edge["end"][0]], [edge["start"][1], edge["end"][1]], color=colors[edge["confidence"]], linewidth=3.0)
        ax.text((edge["start"][0] + edge["end"][0]) / 2, (edge["start"][1] + edge["end"][1]) / 2, str(edge["edge_index"]), fontsize=8, bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"})
    polygon = Polygon(outline)
    x, y = polygon.exterior.xy
    ax.fill(x, y, color="#4cc9f0", alpha=0.14)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    ax.set_title(f"EDIFICIO_1 {floor}: candidato de perimetro (sin aplicar)")
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    output = OUT_DIR / f"edificio_1_{floor.lower()}_outline_candidate.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def render_context_only(floor: str) -> str:
    _path, slabs = slab_audit.segments_for("EDIFICIO_1", floor)
    _path, structure = structural_rows(floor)
    fig, ax = plt.subplots(figsize=(14, 7))
    for row in structure:
        color = "#9aa0a6" if row["layer"] == "RLE-VIGA" else "#c7a26b"
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color=color, linewidth=0.55, alpha=0.55)
    for row in slabs:
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color="#202124", linewidth=1.5)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    ax.set_title(f"EDIFICIO_1 {floor}: contexto para resolver perimetro")
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    output = OUT_DIR / f"edificio_1_{floor.lower()}_unresolved_context.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "PARTIAL_PROPOSAL_NOT_APPLIED",
        "building": "EDIFICIO_1",
        "participates_in_FE": False,
        "floors": {
            "S1": {"status": "UNRESOLVED_OUTER_PERIMETER", "reason": "RLE-LOSA contiene solo ocho trazos locales y no dibuja el borde exterior."},
            "P1": {"status": "UNRESOLVED_OUTBOARD_TRANSITION", "reason": "El borde base y los trazos outboard norte no forman una unica cadena; requiere clasificacion contra arquitectura/elevaciones."},
            "P4": {"status": "FROZEN_APPROVED_PILOT", "area_m2": 958.39275, "source": "entregas/P1L3/arquitectura/architectural_visual_model.json"},
        },
        "inputs": {},
    }
    payload["floors"]["S1"]["overlay"] = render_context_only("S1")
    payload["floors"]["P1"]["overlay"] = render_context_only("P1")
    report = ["# Propuesta parcial de perímetros — EDIFICIO_1", "", "Estado: `PARTIAL_PROPOSAL_NOT_APPLIED`. No modifica superficies, FE, cargas ni resultados.", "", "| Piso | Estado | Área candidata | Bordes directos | Bordes probables | Revisión |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    report.append("| S1 | UNRESOLVED_OUTER_PERIMETER | — | — | — | borde exterior ausente |")
    report.append("| P1 | UNRESOLVED_OUTBOARD_TRANSITION | — | — | — | transición norte/outboard |")
    for floor, outline in CANDIDATES.items():
        polygon = Polygon(outline)
        edges, slabs, structure, path = classify(floor, outline)
        counts = {name: sum(edge["confidence"] == name for edge in edges) for name in {edge["confidence"] for edge in edges}}
        payload["floors"][floor] = {"status": "CANDIDATE", "source_sheet": path.name, "source_sha256": sha256(path), "outline_xy": outline, "area_m2": round(polygon.area, 6), "perimeter_m": round(polygon.length, 6), "edge_evidence": edges, "confidence_counts": counts, "internal_features": "NOT_CLASSIFIED_AS_HOLES", "overlay": render(floor, outline, edges, slabs, structure)}
        payload["inputs"][str(path.relative_to(REPO)).replace("\\", "/")] = sha256(path)
        probable = counts.get("LIKELY_RLE_PLUS_STRUCTURE", 0) + counts.get("LIKELY_STRUCTURAL_CLOSURE", 0)
        report.append(f"| {floor} | CANDIDATE | {polygon.area:.3f} m² | {counts.get('CONFIRMED_RLE_LOSA', 0)} | {probable} | {counts.get('REVIEW_REQUIRED', 0)} |")
    report.append("| P4 | FROZEN_APPROVED_PILOT | 958.393 m² | — | — | 0 |")
    report.extend(["", "P2/P3 son candidatos de auditoría, no superficies aprobadas. Los rasgos interiores no se descuentan hasta clasificarlos."])
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("ED1_SLAB_OUTLINE_PROPOSAL: PARTIAL_NOT_APPLIED")
    for floor in ("P2", "P3"):
        row = payload["floors"][floor]
        print(floor, row["area_m2"], row["confidence_counts"])


if __name__ == "__main__":
    main()
