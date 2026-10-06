#!/usr/bin/env python3
"""Audita si las lineas RLE-MURO del viewer son caras o muros fisicos.

El extractor historico fusiono segmentos colineales pero convirtio cada cara
paralela del contorno CAD en un prisma de 0.22 m. Esta auditoria empareja caras
del mismo paño, recupera centrolinea/espesor y deja los casos no emparejados
explicitamente separados. No modifica el modelo.
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
MODEL = REPO / "entregas" / "P1L2" / "unity_export" / "model_viewer.json"
DXF_DIR = REPO / "recursos" / "planos" / "dxf_full" / "2017_67"
OUT_DIR = REPO / "entregas" / "P1L2" / "edificio" / "validacion" / "ed1_walls"
OUT_JSON = OUT_DIR / "ed1_wall_face_audit.json"
OUT_MD = OUT_DIR / "REPORT.md"
FLOORS = ("S1", "P1", "P2", "P3", "P4")
STANDARD_THICKNESSES_M = (0.15, 0.20, 0.25, 0.30, 0.35)
CALCE_A_DX_M = 27.491
FLOOR_SOURCES = {
    "S1": ("2017_67-101.dxf", (571.0, 5260.0, 3890.0, 8496.0), (1061.32, 7183.28)),
    "P1": ("2017_67-101.dxf", (571.0, 487.0, 5972.0, 4904.0), (1061.32, 3558.02)),
    "P2": ("2017_67-102.dxf", (120.0, 5250.0, 5960.0, 8456.0), (893.24, 7903.06)),
    "P3": ("2017_67-102.dxf", (120.0, 1748.0, 5960.0, 4900.0), (534.98, 4278.48)),
    "P4": ("2017_67-103.dxf", (127.0, 3767.0, 5976.0, 6849.0), (490.34, 6297.31)),
}
LOCAL_TO_FLOOR = {"1S": "S1", "1": "P1", "2": "P2", "3": "P3", "4": "P4"}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_faces(floor: str) -> list[dict[str, object]]:
    file_name, bbox, origin = FLOOR_SOURCES[floor]
    x_min, y_min, x_max, y_max = bbox
    origin_x, origin_y = origin
    doc = ezdxf.readfile(DXF_DIR / file_name)
    rows = []
    counter = 0
    for entity in doc.modelspace():
        if entity.dxf.layer != "RLE-MURO":
            continue
        raw_segments = []
        if entity.dxftype() == "LINE":
            raw_segments.append(((entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y)))
        elif entity.dxftype() == "LWPOLYLINE":
            points = [(point[0], point[1]) for point in entity.get_points()]
            raw_segments.extend(zip(points, points[1:]))
            if entity.closed and len(points) > 2:
                raw_segments.append((points[-1], points[0]))
        for first, second in raw_segments:
            inside = sum(x_min <= point[0] <= x_max and y_min <= point[1] <= y_max for point in (first, second))
            if inside < 1:
                continue
            start = [(first[0] - origin_x) / 100.0 + CALCE_A_DX_M, (origin_y - first[1]) / 100.0, 0.0]
            end = [(second[0] - origin_x) / 100.0 + CALCE_A_DX_M, (origin_y - second[1]) / 100.0, 0.0]
            if math.dist(start, end) < 0.05:
                continue
            counter += 1
            rows.append(
                {
                    "id": f"{floor}-RLE-MURO-{counter:04d}",
                    "elementTag": f"{floor}-RLE-MURO-{counter:04d}",
                    "floor": floor,
                    "start": start,
                    "end": end,
                    "source_dxf": file_name,
                    "source_layer": "RLE-MURO",
                }
            )
    return rows


def orientation(wall: dict[str, object]) -> str:
    start, end = wall["start"], wall["end"]
    dx = abs(float(end[0]) - float(start[0]))
    dy = abs(float(end[1]) - float(start[1]))
    if dx <= 0.03 and dy > 0.03:
        return "V"
    if dy <= 0.03 and dx > 0.03:
        return "H"
    return "D"


def line_data(wall: dict[str, object]) -> tuple[str, float, float, float]:
    orient = orientation(wall)
    start, end = wall["start"], wall["end"]
    if orient == "V":
        return orient, (float(start[0]) + float(end[0])) / 2.0, *sorted((float(start[1]), float(end[1])))
    if orient == "H":
        return orient, (float(start[1]) + float(end[1])) / 2.0, *sorted((float(start[0]), float(end[0])))
    raise ValueError(f"Diagonal wall {wall.get('id')}")


def pair_candidate(first: dict[str, object], second: dict[str, object]) -> dict[str, float] | None:
    o1, f1, a1, b1 = line_data(first)
    o2, f2, a2, b2 = line_data(second)
    if o1 != o2 or o1 == "D":
        return None
    thickness = abs(f1 - f2)
    if not 0.12 <= thickness <= 0.36:
        return None
    overlap = min(b1, b2) - max(a1, a2)
    minimum_length = min(b1 - a1, b2 - a2)
    if overlap < 0.35 or overlap / max(minimum_length, 1e-9) < 0.55:
        return None
    nearest_standard = min(STANDARD_THICKNESSES_M, key=lambda value: abs(value - thickness))
    standard_residual = abs(thickness - nearest_standard)
    score = 100.0 * overlap / minimum_length + 2.0 * overlap - 20.0 * standard_residual
    return {
        "thickness_m": thickness,
        "overlap_m": overlap,
        "overlap_ratio": overlap / minimum_length,
        "standard_thickness_m": nearest_standard,
        "standard_residual_m": standard_residual,
        "score": score,
    }


def greedy_pairs(walls: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    by_id = {str(wall["id"]): wall for wall in walls}
    edges = {}
    adjacency = {wall_id: set() for wall_id in by_id}
    for index, first in enumerate(walls):
        for second in walls[index + 1 :]:
            metrics = pair_candidate(first, second)
            if metrics:
                a, b = sorted((str(first["id"]), str(second["id"])))
                edges[(a, b)] = metrics
                adjacency[a].add(b)
                adjacency[b].add(a)

    def solve(remaining: tuple[str, ...]) -> tuple[int, float, tuple[tuple[str, str], ...]]:
        if not remaining:
            return 0, 0.0, ()
        first = remaining[0]
        best = solve(remaining[1:])
        remainder_set = set(remaining[1:])
        for second in sorted(adjacency[first] & remainder_set):
            reduced = tuple(node for node in remaining[1:] if node != second)
            count, score, selected = solve(reduced)
            edge = tuple(sorted((first, second)))
            metrics = edges[edge]
            local_score = 100.0 - 10.0 * float(metrics["thickness_m"]) - 100.0 * float(metrics["standard_residual_m"])
            candidate = count + 1, score + local_score, selected + (edge,)
            if candidate[:2] > best[:2]:
                best = candidate
        return best

    # Se parte cada cara en intervalos atomicos. Asi una cara continua puede
    # emparejarse con dos caras separadas por una abertura, sin tender un muro
    # artificial a traves del vano.
    atoms = []
    used_intervals: defaultdict[str, list[tuple[float, float]]] = defaultdict(list)
    for orient in ("H", "V"):
        oriented = [wall for wall in walls if orientation(wall) == orient]
        endpoints = sorted({round(value, 6) for wall in oriented for value in line_data(wall)[2:]})
        for lo, hi in zip(endpoints, endpoints[1:]):
            if hi - lo < 0.05:
                continue
            midpoint = (lo + hi) / 2.0
            active = sorted(
                str(wall["id"])
                for wall in oriented
                if line_data(wall)[2] <= midpoint <= line_data(wall)[3]
            )
            if len(active) < 2:
                continue
            selected = solve(tuple(active))[2]
            for edge in selected:
                metrics = edges.get(edge)
                if not metrics:
                    continue
                atoms.append({"edge": edge, "orientation": orient, "lo": lo, "hi": hi, "metrics": metrics})
                used_intervals[edge[0]].append((lo, hi))
                used_intervals[edge[1]].append((lo, hi))

    grouped_atoms: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for atom in atoms:
        grouped_atoms[atom["edge"]].append(atom)

    strips = []
    for edge, edge_atoms in sorted(grouped_atoms.items()):
        edge_atoms.sort(key=lambda atom: float(atom["lo"]))
        current_lo = float(edge_atoms[0]["lo"])
        current_hi = float(edge_atoms[0]["hi"])
        for atom in edge_atoms[1:]:
            lo, hi = float(atom["lo"]), float(atom["hi"])
            if lo <= current_hi + 1e-5:
                current_hi = max(current_hi, hi)
            else:
                strips.append((edge, current_lo, current_hi, edge_atoms[0]["metrics"]))
                current_lo, current_hi = lo, hi
        strips.append((edge, current_lo, current_hi, edge_atoms[0]["metrics"]))

    pairs = []
    for first_second, lo, hi, metrics in strips:
        if hi - lo < 0.35:
            continue
        first_id, second_id = first_second
        first = by_id[first_id]
        second = by_id[second_id]
        o1, f1, _, _ = line_data(first)
        _, f2, _, _ = line_data(second)
        fixed = (f1 + f2) / 2.0
        if o1 == "V":
            start, end = [fixed, lo], [fixed, hi]
        else:
            start, end = [lo, fixed], [hi, fixed]
        pairs.append(
            {
                "pair_id": f"{first['floor']}-WP-{len(pairs) + 1:03d}",
                "floor": first["floor"],
                "orientation": o1,
                "face_ids": sorted([first["id"], second["id"]]),
                "source_tags": sorted([first.get("elementTag"), second.get("elementTag")]),
                "source_sheet": first.get("source_sheet") or first.get("source_dxf"),
                "centerline_start_xy_m": [round(value, 4) for value in start],
                "centerline_end_xy_m": [round(value, 4) for value in end],
                "length_m": round(math.dist(start, end), 4),
                "thickness_m": round(metrics["thickness_m"], 4),
                "standard_thickness_m": metrics["standard_thickness_m"],
                "standard_residual_m": round(metrics["standard_residual_m"], 4),
                "overlap_m": round(hi - lo, 4),
                "overlap_ratio": 1.0,
                "classification": "CONFIRMED_CONTOUR_PAIR" if metrics["standard_residual_m"] <= 0.021 else "REVIEW_THICKNESS",
            }
        )
    used = {wall_id for pair in pairs for wall_id in pair["face_ids"]}
    unmatched = [wall for wall in walls if wall["id"] not in used]
    residuals = []
    for wall in walls:
        _, _, start, end = line_data(wall)
        intervals = sorted(used_intervals.get(str(wall["id"]), []))
        covered = 0.0
        cursor = start
        gaps = []
        for lo, hi in intervals:
            lo, hi = max(start, lo), min(end, hi)
            if hi <= lo:
                continue
            if lo > cursor + 0.05:
                gaps.append([round(cursor, 4), round(lo, 4)])
            covered += max(0.0, hi - max(lo, cursor))
            cursor = max(cursor, hi)
        if cursor < end - 0.05:
            gaps.append([round(cursor, 4), round(end, 4)])
        residual_length = max(0.0, end - start - covered)
        if residual_length >= 0.05:
            residuals.append(
                {
                    "face_id": wall["id"],
                    "face_length_m": round(end - start, 4),
                    "paired_length_m": round(covered, 4),
                    "unpaired_length_m": round(residual_length, 4),
                    "unpaired_intervals": gaps,
                }
            )
    return pairs, unmatched, residuals


def segment_overlap(first: dict[str, object], second: dict[str, object], fixed_tolerance: float = 0.20) -> float:
    o1 = first["orientation"]
    o2 = second["orientation"]
    if o1 != o2:
        return 0.0
    if o1 == "V":
        f1 = first["centerline_start_xy_m"][0]
        f2 = second["centerline_start_xy_m"][0]
        a1, b1 = sorted([first["centerline_start_xy_m"][1], first["centerline_end_xy_m"][1]])
        a2, b2 = sorted([second["centerline_start_xy_m"][1], second["centerline_end_xy_m"][1]])
    else:
        f1 = first["centerline_start_xy_m"][1]
        f2 = second["centerline_start_xy_m"][1]
        a1, b1 = sorted([first["centerline_start_xy_m"][0], first["centerline_end_xy_m"][0]])
        a2, b2 = sorted([second["centerline_start_xy_m"][0], second["centerline_end_xy_m"][0]])
    if abs(float(f1) - float(f2)) > fixed_tolerance:
        return 0.0
    return max(0.0, min(float(b1), float(b2)) - max(float(a1), float(a2)))


def vertical_continuity(pairs_by_floor: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    for lower, upper in zip(FLOORS, FLOORS[1:]):
        for wall in pairs_by_floor[lower]:
            candidates = [(segment_overlap(wall, other), other) for other in pairs_by_floor[upper]]
            overlap, best = max(candidates, key=lambda item: item[0], default=(0.0, None))
            rows.append(
                {
                    "lower_floor": lower,
                    "upper_floor": upper,
                    "lower_pair_id": wall["pair_id"],
                    "upper_pair_id": best["pair_id"] if best and overlap >= 0.50 else None,
                    "overlap_m": round(overlap, 4),
                    "status": "CONTINUES" if best and overlap >= 0.50 else "TERMINATES_OR_REVIEW",
                }
            )
    return rows


def plot_floor(floor: str, walls: list[dict[str, object]], pairs: list[dict[str, object]], unmatched: list[dict[str, object]]) -> str:
    fig, ax = plt.subplots(figsize=(16, 8))
    for wall in walls:
        ax.plot([wall["start"][0], wall["end"][0]], [wall["start"][1], wall["end"][1]], color="#9aa0a6", linewidth=2.0, alpha=0.65)
    for pair in pairs:
        start, end = pair["centerline_start_xy_m"], pair["centerline_end_xy_m"]
        color = "#1a73e8" if pair["classification"] == "CONFIRMED_CONTOUR_PAIR" else "#f9ab00"
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=1.2)
    for wall in unmatched:
        ax.plot([wall["start"][0], wall["end"][0]], [wall["start"][1], wall["end"][1]], color="#d93025", linewidth=3.0)
    ax.set_title(f"EDIFICIO_1 {floor}: gris=caras DXF, azul=centrolinea emparejada, rojo=cierre de contorno")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.25, alpha=0.4)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    output = OUT_DIR / f"{floor.lower()}_wall_face_pairs.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = load(MODEL)
    current_walls = []
    for wall in model.get("solids", []):
        floor = LOCAL_TO_FLOOR.get(str(wall.get("floor")))
        if wall.get("category") != "wall" or floor is None:
            continue
        transformed = dict(wall)
        transformed["floor"] = floor
        transformed["start"] = [float(wall["start"][0]) + CALCE_A_DX_M, *wall["start"][1:]]
        transformed["end"] = [float(wall["end"][0]) + CALCE_A_DX_M, *wall["end"][1:]]
        current_walls.append(transformed)
    floors = {}
    pairs_by_floor = {}
    for floor in FLOORS:
        walls = source_faces(floor)
        current_floor_walls = [wall for wall in current_walls if wall["floor"] == floor]
        diagonal = [wall for wall in walls if orientation(wall) == "D"]
        axis_aligned = [wall for wall in walls if orientation(wall) != "D"]
        pairs, unmatched, residuals = greedy_pairs(axis_aligned)
        unmatched.extend(diagonal)
        unmatched_classification = []
        for wall in unmatched:
            length = math.dist(wall["start"][:2], wall["end"][:2])
            classification = "CONTOUR_CLOSING_EDGE_EXCLUDED" if length <= 0.76 else "REVIEW_REQUIRED"
            unmatched_classification.append(
                {
                    "face_id": wall["id"],
                    "length_m": round(length, 4),
                    "classification": classification,
                    "reason": "Tramo corto que cierra el contorno de espesor o el rectangulo de un pilar; no es una centrolinea resistente independiente." if classification != "REVIEW_REQUIRED" else "Cara sin opuesta y longitud incompatible con un simple cierre de contorno.",
                }
            )
        pairs_by_floor[floor] = pairs
        floors[floor] = {
            "source_contour_segments": len(walls),
            "current_wall_prisms": len(current_floor_walls),
            "confirmed_physical_walls": sum(pair["classification"] == "CONFIRMED_CONTOUR_PAIR" for pair in pairs),
            "review_thickness_pairs": sum(pair["classification"] == "REVIEW_THICKNESS" for pair in pairs),
            "paired_faces": 2 * len(pairs),
            "unmatched_faces": len(unmatched),
            "unmatched_ids": [wall["id"] for wall in unmatched],
            "unmatched_classification": unmatched_classification,
            "unresolved_unmatched_faces": sum(row["classification"] == "REVIEW_REQUIRED" for row in unmatched_classification),
            "partially_unpaired_faces": sum(0.0 < row["paired_length_m"] < row["face_length_m"] for row in residuals),
            "unpaired_face_length_m": round(sum(row["unpaired_length_m"] for row in residuals), 4),
            "face_residuals": residuals,
            "thicknesses_m": dict(sorted(Counter(str(pair["standard_thickness_m"]) for pair in pairs).items())),
            "pairs": pairs,
            "overlay": plot_floor(floor, walls, pairs, unmatched),
        }
    continuity = vertical_continuity(pairs_by_floor)
    totals = {
        "source_contour_segments": sum(row["source_contour_segments"] for row in floors.values()),
        "current_wall_prisms": len(current_walls),
        "paired_physical_walls": sum(len(value) for value in pairs_by_floor.values()),
        "confirmed_physical_walls": sum(row["confirmed_physical_walls"] for row in floors.values()),
        "review_thickness_pairs": sum(row["review_thickness_pairs"] for row in floors.values()),
        "unmatched_faces": sum(row["unmatched_faces"] for row in floors.values()),
        "unresolved_unmatched_faces": sum(row["unresolved_unmatched_faces"] for row in floors.values()),
        "unpaired_face_length_m": round(sum(row["unpaired_face_length_m"] for row in floors.values()), 4),
        "continuing_between_adjacent_floors": sum(row["status"] == "CONTINUES" for row in continuity),
        "terminates_or_review": sum(row["status"] != "CONTINUES" for row in continuity),
    }
    status = "PASS" if totals["unresolved_unmatched_faces"] == 0 and totals["review_thickness_pairs"] == 0 else "PASS_WITH_REVIEW_ITEMS"
    result = {
        "status": status,
        "scope": "GEO-WALL-E1-001_DIAGNOSTIC",
        "model": str(MODEL.relative_to(REPO)).replace("\\", "/"),
        "finding": "El modelo historico representa caras de contorno RLE-MURO como muros fisicos independientes de 0.22 m.",
        "policy": "Los pares directos del DXF definen centrolinea y espesor. Los cierres cortos sin cara opuesta se excluyen como geometria de contorno, no como muros fisicos.",
        "totals": totals,
        "floors": floors,
        "vertical_continuity": continuity,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Diagnostico de caras de muro EDIFICIO_1",
        "",
        f"Estado: `{status}`",
        "",
        "El extractor historico fusiono lineas colineales de `RLE-MURO`, pero luego dio 0.22 m de espesor a cada cara del contorno. Dos caras de un mismo muro quedaron por tanto como dos elementos resistentes. Esta revision vuelve a leer los DXF completos sin el redondeo historico de 0.15 m.",
        "",
        "| Piso | Segmentos fuente | Prismas actuales | Muros analiticos confirmados | Cierres excluidos | Sin resolver |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for floor in FLOORS:
        row = floors[floor]
        lines.append(f"| {floor} | {row['source_contour_segments']} | {row['current_wall_prisms']} | {row['confirmed_physical_walls']} | {row['unmatched_faces']} | {row['unresolved_unmatched_faces']} |")
    lines.extend(
        [
            "",
            f"Total actual: `{totals['current_wall_prisms']}` prismas. Segmentos analiticos recuperados desde pares: `{totals['paired_physical_walls']}`. Cierres cortos excluidos: `{totals['unmatched_faces']}`. Sin resolver: `{totals['unresolved_unmatched_faces']}`.",
            "",
            "## Decision",
            "",
            "Los pares confirmados deben reemplazarse por una sola centrolinea con el espesor medido directamente entre caras. Las caras no emparejadas son todas cierres de 0.15–0.70 m; se excluyen como geometria auxiliar del contorno y no se convierten en muros independientes.",
            "",
            "## QA pendiente antes de aplicar",
            "",
            "- revisar visualmente los overlays por piso;",
            "- conservar el registro de cada cierre excluido;",
            "- comprobar continuidad vertical y elevaciones estructurales;",
            "- regenerar ED1/combinado solo cuando no queden decisiones silenciosas.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_JSON)
    print(OUT_MD)
    print(status, totals)


if __name__ == "__main__":
    main()
