#!/usr/bin/env python3
"""Diagnostico geometrico reproducible de las lineas RLE-VIGA de EDIFICIO_1.

Esta fase no corrige el modelo. Cuantifica duplicados, fragmentos colineales,
posibles pares de caras, cruces sin nodo y conectividad de extremos usando los
DXF completos y el modelo combinado vigente.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO = Path(__file__).resolve().parents[4]
DXF_DIR = REPO / "recursos/planos/dxf_full/2017_67"
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/ed1_beams"
OUT_JSON = OUT_DIR / "ed1_beam_diagnostic.json"
OUT_MD = OUT_DIR / "REPORT.md"
CALCE_A_DX_M = 27.491
FLOOR_SOURCES = {
    "S1": ("2017_67-101.dxf", (571.0, 5260.0, 3890.0, 8496.0), (1061.32, 7183.28)),
    "P1": ("2017_67-101.dxf", (571.0, 487.0, 5972.0, 4904.0), (1061.32, 3558.02)),
    "P2": ("2017_67-102.dxf", (120.0, 5250.0, 5960.0, 8456.0), (893.24, 7903.06)),
    "P3": ("2017_67-102.dxf", (120.0, 1748.0, 5960.0, 4900.0), (534.98, 4278.48)),
    "P4": ("2017_67-103.dxf", (127.0, 3767.0, 5976.0, 6849.0), (490.34, 6297.31)),
}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def transform(point: tuple[float, float], origin: tuple[float, float]) -> list[float]:
    return [(point[0] - origin[0]) / 100.0 + CALCE_A_DX_M, (origin[1] - point[1]) / 100.0]


def raw_segments(entity) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    if entity.dxftype() == "LINE":
        return [((entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y))]
    if entity.dxftype() == "LWPOLYLINE":
        points = [(point[0], point[1]) for point in entity.get_points()]
        rows = list(zip(points, points[1:]))
        if entity.closed and len(points) > 2:
            rows.append((points[-1], points[0]))
        return rows
    return []


def source_beams(floor: str) -> list[dict[str, object]]:
    file_name, bbox, origin = FLOOR_SOURCES[floor]
    x0, y0, x1, y1 = bbox
    doc = ezdxf.readfile(DXF_DIR / file_name)
    rows = []
    for entity in doc.modelspace():
        if entity.dxf.layer != "RLE-VIGA":
            continue
        for segment_index, (first, second) in enumerate(raw_segments(entity)):
            if sum(x0 <= point[0] <= x1 and y0 <= point[1] <= y1 for point in (first, second)) < 1:
                continue
            start, end = transform(first, origin), transform(second, origin)
            length = math.dist(start, end)
            if length < 0.05:
                continue
            rows.append(
                {
                    "id": f"{floor}-VB-{len(rows) + 1:04d}",
                    "floor": floor,
                    "source_dxf": file_name,
                    "entity_handle": str(entity.dxf.handle),
                    "entity_type": entity.dxftype(),
                    "segment_index": segment_index,
                    "start": start,
                    "end": end,
                    "length_m": length,
                }
            )
    return rows


def orientation(item: dict[str, object]) -> str:
    dx = abs(float(item["end"][0]) - float(item["start"][0]))
    dy = abs(float(item["end"][1]) - float(item["start"][1]))
    if dx <= 0.03 and dy > 0.03:
        return "V"
    if dy <= 0.03 and dx > 0.03:
        return "H"
    return "D"


def line_data(item: dict[str, object]) -> tuple[str, float, float, float]:
    orient = orientation(item)
    if orient == "H":
        return orient, (item["start"][1] + item["end"][1]) / 2.0, *sorted((item["start"][0], item["end"][0]))
    if orient == "V":
        return orient, (item["start"][0] + item["end"][0]) / 2.0, *sorted((item["start"][1], item["end"][1]))
    return orient, 0.0, 0.0, float(item["length_m"])


def canonical(item: dict[str, object], tolerance: float = 0.002) -> tuple[object, ...]:
    start = tuple(round(float(value) / tolerance) for value in item["start"])
    end = tuple(round(float(value) / tolerance) for value in item["end"])
    return (item["floor"],) + tuple(sorted((start, end)))


def parallel_candidates(items: list[dict[str, object]]) -> tuple[dict[str, list[dict[str, object]]], Counter[str]]:
    candidates: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    widths: Counter[str] = Counter()
    for index, first in enumerate(items):
        o1, f1, a1, b1 = line_data(first)
        if o1 == "D":
            continue
        for second in items[index + 1 :]:
            o2, f2, a2, b2 = line_data(second)
            if o1 != o2:
                continue
            separation = abs(f1 - f2)
            overlap = min(b1, b2) - max(a1, a2)
            shorter = min(b1 - a1, b2 - a2)
            if not 0.12 <= separation <= 0.85 or overlap < 0.35 or overlap / max(shorter, 1e-9) < 0.60:
                continue
            row = {
                "other": second["id"],
                "separation_m": round(separation, 4),
                "overlap_m": round(overlap, 4),
                "overlap_ratio": round(overlap / shorter, 4),
            }
            candidates[str(first["id"])].append(row)
            candidates[str(second["id"])].append({**row, "other": first["id"]})
            widths[f"{separation:.2f}"] += 1
    for rows in candidates.values():
        rows.sort(key=lambda row: (-float(row["overlap_ratio"]), float(row["separation_m"]), str(row["other"])))
    return dict(candidates), widths


def collinear_groups(items: list[dict[str, object]]) -> list[dict[str, object]]:
    buckets: defaultdict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for item in items:
        orient, fixed, _start, _end = line_data(item)
        if orient != "D":
            buckets[(orient, round(fixed / 0.03))].append(item)
    groups = []
    for (orient, _), rows in buckets.items():
        rows.sort(key=lambda item: line_data(item)[2])
        current = []
        current_end = -math.inf
        for item in rows:
            _o, _f, start, end = line_data(item)
            if current and start > current_end + 0.08:
                if len(current) > 1:
                    groups.append({"orientation": orient, "ids": [row["id"] for row in current]})
                current = []
            current.append(item)
            current_end = max(current_end, end)
        if len(current) > 1:
            groups.append({"orientation": orient, "ids": [row["id"] for row in current]})
    return groups


def point_segment_distance(point: list[float], item: dict[str, object]) -> float:
    ax, ay = item["start"][:2]
    bx, by = item["end"][:2]
    vx, vy = bx - ax, by - ay
    length2 = vx * vx + vy * vy
    if length2 == 0:
        return math.dist(point, [ax, ay])
    t = max(0.0, min(1.0, ((point[0] - ax) * vx + (point[1] - ay) * vy) / length2))
    return math.dist(point, [ax + t * vx, ay + t * vy])


def endpoint_connectivity(items: list[dict[str, object]], structural: list[dict[str, object]]) -> dict[str, object]:
    unsupported = []
    connected = 0
    for item in items:
        for endpoint_name in ("start", "end"):
            endpoint = item[endpoint_name]
            candidates = [other for other in structural if other is not item and point_segment_distance(endpoint, other) <= 0.18]
            if candidates:
                connected += 1
            else:
                unsupported.append({"beam_id": item["id"], "endpoint": endpoint_name, "point": [round(v, 4) for v in endpoint]})
    return {"connected_endpoints": connected, "unconnected_endpoints": len(unsupported), "unconnected": unsupported}


def unsplit_crossings(items: list[dict[str, object]]) -> list[dict[str, object]]:
    horizontal = [item for item in items if orientation(item) == "H"]
    vertical = [item for item in items if orientation(item) == "V"]
    rows = []
    for first in horizontal:
        _, fy, ax, bx = line_data(first)
        for second in vertical:
            _, fx, ay, by = line_data(second)
            if ax + 0.08 < fx < bx - 0.08 and ay + 0.08 < fy < by - 0.08:
                rows.append({"horizontal": first["id"], "vertical": second["id"], "point": [round(fx, 4), round(fy, 4)]})
    return rows


def plot_floor(floor: str, items: list[dict[str, object]], candidates: dict[str, list[dict[str, object]]], unsupported_ids: set[str]) -> str:
    fig, ax = plt.subplots(figsize=(17, 9))
    for item in items:
        count = len(candidates.get(str(item["id"]), []))
        color = "#d93025" if item["id"] in unsupported_ids else "#f9ab00" if count > 1 else "#1a73e8" if count == 1 else "#5f6368"
        ax.plot([item["start"][0], item["end"][0]], [item["start"][1], item["end"][1]], color=color, linewidth=1.4)
    ax.set_title(f"EDIFICIO_1 {floor}: azul=un par posible, amarillo=ambiguo, gris=sin par, rojo=extremo aislado")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.25, alpha=0.4)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    output = OUT_DIR / f"{floor.lower()}_beam_diagnostic.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = load(MODEL)
    floors = {}
    totals = Counter()
    for floor in FLOOR_SOURCES:
        items = source_beams(floor)
        current_beams = [
            solid for solid in model["solids"]
            if solid.get("building") == "EDIFICIO_1" and solid.get("floor") == floor and solid.get("category") == "beam"
        ]
        beam_labels = [
            label for label in model.get("labels", [])
            if label.get("building") == "EDIFICIO_1"
            and label.get("floor") == floor
            and label.get("level_kind") == "FLOOR"
            and label.get("category") == "beam_label"
            and label.get("section_hint", {}).get("kind") == "rectangular"
        ]
        candidates, width_histogram = parallel_candidates(items)
        duplicate_counts = Counter(canonical(item) for item in items)
        duplicate_groups = [count for count in duplicate_counts.values() if count > 1]
        fragments = collinear_groups(items)
        contextual = [
            solid for solid in model["solids"]
            if solid.get("building") == "EDIFICIO_1" and solid.get("floor") == floor and solid.get("category") in {"wall", "column"}
        ]
        structural = items + [
            {"id": solid["id"], "start": solid.get("start", solid.get("center")), "end": solid.get("end", solid.get("center"))}
            for solid in contextual
        ]
        connectivity = endpoint_connectivity(items, structural)
        crossings = unsplit_crossings(items)
        candidate_degree = Counter(len(candidates.get(str(item["id"]), [])) for item in items)
        unsupported_ids = {row["beam_id"] for row in connectivity["unconnected"]}
        row = {
            "source_segments": len(items),
            "current_beam_prisms": len(current_beams),
            "axis_aligned": sum(orientation(item) != "D" for item in items),
            "diagonal": sum(orientation(item) == "D" for item in items),
            "shorter_than_0_75_m": sum(float(item["length_m"]) < 0.75 for item in items),
            "exact_duplicate_groups": len(duplicate_groups),
            "exact_duplicate_extra_segments": sum(count - 1 for count in duplicate_groups),
            "collinear_fragment_groups": len(fragments),
            "parallel_candidate_degree": dict(sorted((str(key), value) for key, value in candidate_degree.items())),
            "candidate_width_histogram_m": dict(sorted(width_histogram.items())),
            "labelled_sections_m": dict(sorted(Counter(
                f"{float(label['section_hint']['width_m']):.2f}x{float(label['section_hint']['height_m']):.2f}"
                for label in beam_labels
            ).items())),
            "endpoint_connectivity": connectivity,
            "unsplit_orthogonal_crossings": crossings,
            "collinear_groups": fragments,
            "parallel_candidates": candidates,
            "overlay": plot_floor(floor, items, candidates, unsupported_ids),
        }
        floors[floor] = row
        totals.update(
            source_segments=len(items),
            current_beam_prisms=len(current_beams),
            diagonal=row["diagonal"],
            short=row["shorter_than_0_75_m"],
            duplicate_extra=row["exact_duplicate_extra_segments"],
            fragment_groups=row["collinear_fragment_groups"],
            unconnected_endpoints=connectivity["unconnected_endpoints"],
            unsplit_crossings=len(crossings),
        )
    result = {
        "status": "DIAGNOSTIC_COMPLETE_NO_GEOMETRY_CHANGE",
        "scope": "GEO-BEAM-E1-001",
        "source": "direct_full_DXF_RLE-VIGA",
        "totals": dict(totals),
        "floors": floors,
        "interpretation": "Los pares paralelos son candidatos, no correcciones automaticas. Deben cruzarse con etiquetas, apoyos y continuidad antes de consolidar.",
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Diagnostico inicial de vigas EDIFICIO_1",
        "",
        "Estado: `DIAGNOSTIC_COMPLETE_NO_GEOMETRY_CHANGE`",
        "",
        "| Piso | Segmentos DXF | Prismas actuales | Un par posible | Pareo ambiguo | Diagonales | Cortos <0.75 m | Grupos colineales | Extremos aislados |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for floor, row in floors.items():
        degree = row["parallel_candidate_degree"]
        ambiguous = sum(int(count) for candidates, count in degree.items() if int(candidates) > 1)
        lines.append(f"| {floor} | {row['source_segments']} | {row['current_beam_prisms']} | {degree.get('1', 0)} | {ambiguous} | {row['diagonal']} | {row['shorter_than_0_75_m']} | {row['collinear_fragment_groups']} | {row['endpoint_connectivity']['unconnected_endpoints']} |")
    lines.extend(
        [
            "",
            "## Alcance de este paso",
            "",
            "No se modifico ninguna viga. El diagnostico separa defectos seguros (duplicados exactos) de candidatos que requieren evidencia adicional (caras paralelas, fragmentos, extremos y cruces).",
            "",
            "La coincidencia dominante entre separacion de caras y ancho rotulado (0.20/0.30/0.40/0.60 m) indica que `RLE-VIGA` contiene contornos. Los casos ambiguos, diagonales y extremos aislados deben resolverse antes de crear centrolineas.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ED1_BEAM_DIAGNOSTIC: COMPLETE_NO_GEOMETRY_CHANGE")
    print(dict(totals))
    print(f"Reportes: {OUT_JSON} {OUT_MD}")


if __name__ == "__main__":
    main()
