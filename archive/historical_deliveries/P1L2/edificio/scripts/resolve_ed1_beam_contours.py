#!/usr/bin/env python3
"""Propone centrolineas de viga ED1 sin modificar el modelo canónico."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import audit_ed1_beams as base


REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/ed1_beams"
OUT_JSON = OUT_DIR / "ed1_beam_centerline_proposal.json"
OUT_MD = OUT_DIR / "CENTERLINE_PROPOSAL.md"
STANDARD_WIDTHS_M = (0.15, 0.20, 0.30, 0.40, 0.60)
MIN_FACE_LENGTH_M = 0.75


def point_segment_distance(point: list[float], start: list[float], end: list[float]) -> float:
    vx, vy = end[0] - start[0], end[1] - start[1]
    length2 = vx * vx + vy * vy
    if length2 <= 1e-12:
        return math.dist(point[:2], start[:2])
    t = max(0.0, min(1.0, ((point[0] - start[0]) * vx + (point[1] - start[1]) * vy) / length2))
    return math.dist(point[:2], [start[0] + t * vx, start[1] + t * vy])


def floor_labels(model: dict[str, object], floor: str) -> list[dict[str, object]]:
    return [
        label for label in model.get("labels", [])
        if label.get("building") == "EDIFICIO_1"
        and label.get("floor") == floor
        and label.get("level_kind") == "FLOOR"
        and label.get("category") == "beam_label"
        and label.get("section_hint", {}).get("kind") == "rectangular"
    ]


def closure_count(
    first: dict[str, object], second: dict[str, object], lo: float, hi: float, items: list[dict[str, object]]
) -> int:
    orient, f1, _a1, _b1 = base.line_data(first)
    _orient, f2, _a2, _b2 = base.line_data(second)
    low_fixed, high_fixed = sorted((f1, f2))
    opposite = "V" if orient == "H" else "H"
    count = 0
    for boundary in (lo, hi):
        for item in items:
            other_orient, fixed, start, end = base.line_data(item)
            if other_orient != opposite or abs(fixed - boundary) > 0.04:
                continue
            if start <= low_fixed + 0.05 and end >= high_fixed - 0.05 and end - start <= high_fixed - low_fixed + 0.12:
                count += 1
                break
    return count


def candidate_evidence(
    first: dict[str, object], second: dict[str, object], lo: float, hi: float,
    items: list[dict[str, object]], labels: list[dict[str, object]],
) -> dict[str, object] | None:
    orient, f1, _a1, _b1 = base.line_data(first)
    other_orient, f2, _a2, _b2 = base.line_data(second)
    if orient != other_orient or orient == "D":
        return None
    width = abs(f1 - f2)
    standard = min(STANDARD_WIDTHS_M, key=lambda value: abs(value - width))
    residual = abs(width - standard)
    if residual > 0.021:
        return None
    fixed = (f1 + f2) / 2.0
    start = [lo, fixed] if orient == "H" else [fixed, lo]
    end = [hi, fixed] if orient == "H" else [fixed, hi]
    nearest = None
    nearest_matching = None
    for label in labels:
        distance = point_segment_distance(label["point"], start, end)
        if nearest is None or distance < nearest[0]:
            nearest = (distance, label)
        candidate_width = float(label["section_hint"]["width_m"])
        if abs(candidate_width - width) <= 0.021 and (nearest_matching is None or distance < nearest_matching[0]):
            nearest_matching = (distance, label)
    label_distance = nearest[0] if nearest else None
    label_width = float(nearest[1]["section_hint"]["width_m"]) if nearest else None
    label_match = nearest_matching is not None and nearest_matching[0] <= 2.0
    label_conflict = not label_match and label_distance is not None and label_distance <= 0.75 and abs(label_width - width) > 0.021
    closures = closure_count(first, second, lo, hi, items)
    score = 1000.0 * int(label_match) + 160.0 * closures - 600.0 * int(label_conflict) - 200.0 * residual + (hi - lo)
    return {
        "width_m": round(width, 4),
        "standard_width_m": standard,
        "standard_residual_m": round(residual, 4),
        "label_match": label_match,
        "label_conflict": label_conflict,
        "nearest_label": (nearest_matching or nearest)[1]["labelTag"] if (nearest_matching or nearest) else None,
        "nearest_label_text": (nearest_matching or nearest)[1]["text"] if (nearest_matching or nearest) else None,
        "nearest_label_width_m": float((nearest_matching or nearest)[1]["section_hint"]["width_m"]) if (nearest_matching or nearest) else None,
        "nearest_label_height_m": float((nearest_matching or nearest)[1]["section_hint"]["height_m"]) if (nearest_matching or nearest) else None,
        "nearest_label_distance_m": round((nearest_matching or nearest)[0], 4) if (nearest_matching or nearest) else None,
        "closure_count": closures,
        "score": score,
    }


def solve_atom(
    active: tuple[str, ...], edge_evidence: dict[tuple[str, str], dict[str, object]]
) -> tuple[int, float, tuple[tuple[str, str], ...]]:
    @lru_cache(maxsize=None)
    def solve(remaining: tuple[str, ...]) -> tuple[int, float, tuple[tuple[str, str], ...]]:
        if not remaining:
            return 0, 0.0, ()
        first = remaining[0]
        best = solve(remaining[1:])
        for second in remaining[1:]:
            edge = tuple(sorted((first, second)))
            if edge not in edge_evidence:
                continue
            reduced = tuple(item for item in remaining[1:] if item != second)
            count, score, selected = solve(reduced)
            candidate = count + 1, score + float(edge_evidence[edge]["score"]), selected + (edge,)
            if candidate[:2] > best[:2]:
                best = candidate
        return best

    return solve(active)


def resolve_axis_aligned(
    floor: str, items: list[dict[str, object]], labels: list[dict[str, object]]
) -> tuple[list[dict[str, object]], dict[str, list[tuple[float, float]]]]:
    eligible = [item for item in items if base.orientation(item) in {"H", "V"} and float(item["length_m"]) >= MIN_FACE_LENGTH_M]
    by_id = {str(item["id"]): item for item in eligible}
    atoms = []
    used: defaultdict[str, list[tuple[float, float]]] = defaultdict(list)
    for orient in ("H", "V"):
        oriented = [item for item in eligible if base.orientation(item) == orient]
        boundaries = sorted({round(value, 6) for item in oriented for value in base.line_data(item)[2:]})
        for lo, hi in zip(boundaries, boundaries[1:]):
            if hi - lo < 0.20:
                continue
            midpoint = (lo + hi) / 2.0
            active_items = [item for item in oriented if base.line_data(item)[2] <= midpoint <= base.line_data(item)[3]]
            edges = {}
            for index, first in enumerate(active_items):
                for second in active_items[index + 1 :]:
                    evidence = candidate_evidence(first, second, lo, hi, items, labels)
                    if evidence is not None:
                        edges[tuple(sorted((str(first["id"]), str(second["id"]))))] = evidence
            selected = solve_atom(tuple(sorted(str(item["id"]) for item in active_items)), edges)[2]
            for edge in selected:
                evidence = edges[edge]
                atoms.append({"edge": edge, "orientation": orient, "lo": lo, "hi": hi, "evidence": evidence})
                used[edge[0]].append((lo, hi))
                used[edge[1]].append((lo, hi))

    grouped: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for atom in atoms:
        grouped[atom["edge"]].append(atom)
    strips = []
    for edge, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: row["lo"])
        lo, hi = rows[0]["lo"], rows[0]["hi"]
        evidence_rows = [rows[0]["evidence"]]
        chunks = []
        for row in rows[1:]:
            if row["lo"] <= hi + 1e-5:
                hi = max(hi, row["hi"])
                evidence_rows.append(row["evidence"])
            else:
                chunks.append((lo, hi, evidence_rows))
                lo, hi, evidence_rows = row["lo"], row["hi"], [row["evidence"]]
        chunks.append((lo, hi, evidence_rows))
        for lo, hi, evidence_rows in chunks:
            if hi - lo < MIN_FACE_LENGTH_M:
                continue
            first, second = by_id[edge[0]], by_id[edge[1]]
            orient, f1, _a, _b = base.line_data(first)
            _o, f2, _c, _d = base.line_data(second)
            fixed = (f1 + f2) / 2.0
            start = [lo, fixed] if orient == "H" else [fixed, lo]
            end = [hi, fixed] if orient == "H" else [fixed, hi]
            label_match = any(row["label_match"] for row in evidence_rows)
            label_conflict = any(row["label_conflict"] for row in evidence_rows)
            closures = max(int(row["closure_count"]) for row in evidence_rows)
            classification = "CONFIRMED_LABEL_WIDTH" if label_match and not label_conflict else "CONFIRMED_CLOSED_CONTOUR" if closures else "REVIEW_GEOMETRY_ONLY"
            strips.append(
                {
                    "proposal_id": f"{floor}-VP-{len(strips) + 1:03d}",
                    "floor": floor,
                    "orientation": orient,
                    "face_ids": list(edge),
                    "start": [round(value, 4) for value in start],
                    "end": [round(value, 4) for value in end],
                    "length_m": round(hi - lo, 4),
                    "width_m": evidence_rows[0]["width_m"],
                    "classification": classification,
                    "label_match": label_match,
                    "label_conflict": label_conflict,
                    "closure_count": closures,
                    "evidence_samples": evidence_rows[:3],
                }
            )
    return strips, dict(used)


def plot(floor: str, items: list[dict[str, object]], strips: list[dict[str, object]], review_faces: set[str]) -> str:
    fig, ax = plt.subplots(figsize=(17, 9))
    for item in items:
        color = "#d93025" if item["id"] in review_faces else "#bdc1c6"
        ax.plot([item["start"][0], item["end"][0]], [item["start"][1], item["end"][1]], color=color, linewidth=1.0)
    colors = {
        "CONFIRMED_LABEL_WIDTH": "#188038",
        "CONFIRMED_CLOSED_CONTOUR": "#1a73e8",
        "CONFIRMED_REPEATED_PLAN_GEOMETRY": "#1a73e8",
        "CONFIRMED_RESIDUAL_LABEL_WIDTH": "#0b8043",
        "CONFIRMED_SINGLE_CENTERLINE_BY_LABEL": "#9334e6",
        "CONFIRMED_CONNECTED_SECTION_FAMILY": "#185abc",
        "CONFIRMED_CONTOUR_PAIR_GEOMETRY": "#1a73e8",
        "REVIEW_GEOMETRY_ONLY": "#f9ab00",
    }
    for strip in strips:
        ax.plot([strip["start"][0], strip["end"][0]], [strip["start"][1], strip["end"][1]], color=colors[strip["classification"]], linewidth=2.0)
    ax.set_title(f"EDIFICIO_1 {floor}: verde=ancho rotulado, azul=contorno cerrado, amarillo=solo geometria, rojo=cara larga sin resolver")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linewidth=0.25, alpha=0.4)
    output = OUT_DIR / f"{floor.lower()}_beam_centerline_proposal.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def plot_review_detail(
    floor: str, items: list[dict[str, object]], strips: list[dict[str, object]], labels: list[dict[str, object]]
) -> str | None:
    review = [strip for strip in strips if strip["classification"] == "REVIEW_GEOMETRY_ONLY"]
    if not review:
        stale_output = OUT_DIR / f"{floor.lower()}_beam_review_detail.png"
        if stale_output.exists():
            stale_output.unlink()
        return None
    xs = [value for strip in review for value in (strip["start"][0], strip["end"][0])]
    ys = [value for strip in review for value in (strip["start"][1], strip["end"][1])]
    bounds = (min(xs) - 2.0, max(xs) + 2.0, min(ys) - 2.0, max(ys) + 2.0)
    fig, ax = plt.subplots(figsize=(17, 9))
    for item in items:
        ax.plot([item["start"][0], item["end"][0]], [item["start"][1], item["end"][1]], color="#bdc1c6", linewidth=1.0)
    for strip in strips:
        color = "#f9ab00" if strip["classification"] == "REVIEW_GEOMETRY_ONLY" else "#188038"
        width = 2.5 if strip["classification"] == "REVIEW_GEOMETRY_ONLY" else 1.0
        ax.plot([strip["start"][0], strip["end"][0]], [strip["start"][1], strip["end"][1]], color=color, linewidth=width)
    for label in labels:
        x, y = label["point"][:2]
        if bounds[0] - 2 <= x <= bounds[1] + 2 and bounds[2] - 2 <= y <= bounds[3] + 2:
            ax.scatter([x], [y], s=12, color="#9334e6")
            ax.text(x + 0.08, y + 0.08, str(label["text"]), fontsize=7, color="#5f259f")
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_title(f"EDIFICIO_1 {floor}: detalle de centrolineas en revisión y rótulos")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.25, alpha=0.4)
    output = OUT_DIR / f"{floor.lower()}_beam_review_detail.png"
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def repeated_plan_match(first: dict[str, object], second: dict[str, object]) -> bool:
    if first["floor"] == second["floor"] or first["orientation"] != second["orientation"]:
        return False
    if abs(float(first["width_m"]) - float(second["width_m"])) > 0.021:
        return False
    if first["orientation"] == "H":
        fixed_first, fixed_second = first["start"][1], second["start"][1]
        a1, b1 = sorted((first["start"][0], first["end"][0]))
        a2, b2 = sorted((second["start"][0], second["end"][0]))
    else:
        fixed_first, fixed_second = first["start"][0], second["start"][0]
        a1, b1 = sorted((first["start"][1], first["end"][1]))
        a2, b2 = sorted((second["start"][1], second["end"][1]))
    overlap = max(0.0, min(b1, b2) - max(a1, a2))
    return abs(float(fixed_first) - float(fixed_second)) <= 0.05 and overlap >= 0.75 and overlap / max(min(b1 - a1, b2 - a2), 1e-9) >= 0.50


def nested_inside_confirmed(detail: dict[str, object], main: dict[str, object]) -> bool:
    if detail["floor"] != main["floor"] or detail["orientation"] != main["orientation"] or detail["orientation"] == "D":
        return False
    if float(main["width_m"]) <= float(detail["width_m"]) + 0.05:
        return False
    if detail["orientation"] == "H":
        fixed_detail, fixed_main = detail["start"][1], main["start"][1]
        a1, b1 = sorted((detail["start"][0], detail["end"][0]))
        a2, b2 = sorted((main["start"][0], main["end"][0]))
    else:
        fixed_detail, fixed_main = detail["start"][0], main["start"][0]
        a1, b1 = sorted((detail["start"][1], detail["end"][1]))
        a2, b2 = sorted((main["start"][1], main["end"][1]))
    overlap = max(0.0, min(b1, b2) - max(a1, a2))
    return abs(float(fixed_detail) - float(fixed_main)) <= 0.03 and overlap / max(b1 - a1, 1e-9) >= 0.95


def proposals_touch(first: dict[str, object], second: dict[str, object], tolerance: float = 0.45) -> bool:
    return min(
        point_segment_distance(first["start"], second["start"], second["end"]),
        point_segment_distance(first["end"], second["start"], second["end"]),
        point_segment_distance(second["start"], first["start"], first["end"]),
        point_segment_distance(second["end"], first["start"], first["end"]),
    ) <= tolerance


def promote_connected_section_families(proposals: list[dict[str, object]]) -> None:
    seed_classes = {
        "CONFIRMED_LABEL_WIDTH",
        "CONFIRMED_RESIDUAL_LABEL_WIDTH",
        "CONFIRMED_SINGLE_CENTERLINE_BY_LABEL",
    }
    by_width: defaultdict[float, list[dict[str, object]]] = defaultdict(list)
    for proposal in proposals:
        by_width[round(float(proposal["width_m"]), 2)].append(proposal)
    for rows in by_width.values():
        adjacency = {str(row["proposal_id"]): set() for row in rows}
        by_id = {str(row["proposal_id"]): row for row in rows}
        for index, first in enumerate(rows):
            for second in rows[index + 1 :]:
                if proposals_touch(first, second):
                    adjacency[str(first["proposal_id"])].add(str(second["proposal_id"]))
                    adjacency[str(second["proposal_id"])].add(str(first["proposal_id"]))
        visited = set()
        for start_id in adjacency:
            if start_id in visited:
                continue
            component = set()
            stack = [start_id]
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(adjacency[current] - component)
            visited.update(component)
            seeds = [by_id[item] for item in component if by_id[item]["classification"] in seed_classes]
            if not seeds:
                continue
            for item in component:
                proposal = by_id[item]
                if proposal["classification"] == "REVIEW_GEOMETRY_ONLY":
                    proposal["classification"] = "CONFIRMED_CONNECTED_SECTION_FAMILY"
                    proposal["component_label_evidence"] = sorted(str(seed["proposal_id"]) for seed in seeds)


def nearest_matching_label(
    start: list[float], end: list[float], width: float, labels: list[dict[str, object]]
) -> tuple[float, dict[str, object]] | None:
    rows = [
        (point_segment_distance(label["point"], start, end), label)
        for label in labels
        if abs(float(label["section_hint"]["width_m"]) - width) <= 0.021
    ]
    return min(rows, key=lambda row: row[0], default=None)


def residual_pair_geometry(first: dict[str, object], second: dict[str, object]) -> dict[str, object] | None:
    o1, o2 = base.orientation(first), base.orientation(second)
    if o1 in {"H", "V"} and o1 == o2:
        _o, f1, a1, b1 = base.line_data(first)
        _o, f2, a2, b2 = base.line_data(second)
        lo, hi = max(a1, a2), min(b1, b2)
        width = abs(f1 - f2)
        if hi - lo < MIN_FACE_LENGTH_M:
            return None
        fixed = (f1 + f2) / 2.0
        start = [lo, fixed] if o1 == "H" else [fixed, lo]
        end = [hi, fixed] if o1 == "H" else [fixed, hi]
        return {"orientation": o1, "start": start, "end": end, "width_m": width, "length_m": hi - lo}
    if o1 != "D" or o2 != "D":
        return None
    dx = first["end"][0] - first["start"][0]
    dy = first["end"][1] - first["start"][1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    dx2 = second["end"][0] - second["start"][0]
    dy2 = second["end"][1] - second["start"][1]
    length2 = math.hypot(dx2, dy2)
    if abs(ux * (dy2 / length2) - uy * (dx2 / length2)) > 0.02:
        return None
    nx, ny = -uy, ux
    interval1 = sorted((first["start"][0] * ux + first["start"][1] * uy, first["end"][0] * ux + first["end"][1] * uy))
    interval2 = sorted((second["start"][0] * ux + second["start"][1] * uy, second["end"][0] * ux + second["end"][1] * uy))
    lo, hi = max(interval1[0], interval2[0]), min(interval1[1], interval2[1])
    fixed1 = first["start"][0] * nx + first["start"][1] * ny
    fixed2 = second["start"][0] * nx + second["start"][1] * ny
    width = abs(fixed1 - fixed2)
    if hi - lo < MIN_FACE_LENGTH_M:
        return None
    fixed = (fixed1 + fixed2) / 2.0
    return {
        "orientation": "D",
        "start": [lo * ux + fixed * nx, lo * uy + fixed * ny],
        "end": [hi * ux + fixed * nx, hi * uy + fixed * ny],
        "width_m": width,
        "length_m": hi - lo,
    }


def resolve_residuals(
    floor: str, items: list[dict[str, object]], used_ids: set[str], labels: list[dict[str, object]], start_index: int
) -> tuple[list[dict[str, object]], set[str]]:
    remaining = [item for item in items if float(item["length_m"]) >= MIN_FACE_LENGTH_M and item["id"] not in used_ids]
    candidates = []
    for index, first in enumerate(remaining):
        for second in remaining[index + 1 :]:
            geometry = residual_pair_geometry(first, second)
            if geometry is None:
                continue
            width = float(geometry["width_m"])
            standard = min(STANDARD_WIDTHS_M, key=lambda value: abs(value - width))
            if abs(width - standard) > 0.021:
                continue
            label = nearest_matching_label(geometry["start"], geometry["end"], width, labels)
            if label is None or label[0] > 0.75:
                continue
            candidates.append((label[0], -float(geometry["length_m"]), first, second, geometry, label[1]))
    proposals = []
    newly_used = set()
    for distance, _negative_length, first, second, geometry, label in sorted(candidates, key=lambda row: (row[0], row[1], row[2]["id"], row[3]["id"])):
        if first["id"] in newly_used or second["id"] in newly_used:
            continue
        newly_used.update((str(first["id"]), str(second["id"])))
        proposals.append(
            {
                "proposal_id": f"{floor}-VP-{start_index + len(proposals):03d}",
                "floor": floor,
                "orientation": geometry["orientation"],
                "face_ids": [first["id"], second["id"]],
                "start": [round(value, 4) for value in geometry["start"]],
                "end": [round(value, 4) for value in geometry["end"]],
                "length_m": round(float(geometry["length_m"]), 4),
                "width_m": round(float(geometry["width_m"]), 4),
                "height_m": float(label["section_hint"]["height_m"]),
                "classification": "CONFIRMED_RESIDUAL_LABEL_WIDTH",
                "source_label": label["labelTag"],
                "source_label_text": label["text"],
                "source_label_distance_m": round(distance, 4),
            }
        )
    return proposals, newly_used


def resolve_labelled_single_lines(
    floor: str, items: list[dict[str, object]], used_ids: set[str], labels: list[dict[str, object]], start_index: int
) -> tuple[list[dict[str, object]], set[str]]:
    proposals = []
    newly_used = set()
    for item in items:
        if float(item["length_m"]) < MIN_FACE_LENGTH_M or item["id"] in used_ids:
            continue
        matches = sorted((point_segment_distance(label["point"], item["start"], item["end"]), label) for label in labels)
        if not matches or matches[0][0] > 0.60:
            continue
        distance, label = matches[0]
        proposals.append(
            {
                "proposal_id": f"{floor}-VP-{start_index + len(proposals):03d}",
                "floor": floor,
                "orientation": base.orientation(item),
                "face_ids": [item["id"]],
                "start": [round(value, 4) for value in item["start"]],
                "end": [round(value, 4) for value in item["end"]],
                "length_m": round(float(item["length_m"]), 4),
                "width_m": float(label["section_hint"]["width_m"]),
                "height_m": float(label["section_hint"]["height_m"]),
                "classification": "CONFIRMED_SINGLE_CENTERLINE_BY_LABEL",
                "source_label": label["labelTag"],
                "source_label_text": label["text"],
                "source_label_distance_m": round(distance, 4),
            }
        )
        newly_used.add(str(item["id"]))
    return proposals, newly_used


def main() -> None:
    model = base.load(MODEL)
    floors = {}
    total_classes = Counter()
    for floor in base.FLOOR_SOURCES:
        items = base.source_beams(floor)
        labels = floor_labels(model, floor)
        strips, used = resolve_axis_aligned(floor, items, labels)
        used_ids = {item for strip in strips for item in strip["face_ids"]}
        residual_pairs, residual_ids = resolve_residuals(floor, items, used_ids, labels, len(strips) + 1)
        strips.extend(residual_pairs)
        used_ids.update(residual_ids)
        labelled_singles, single_ids = resolve_labelled_single_lines(floor, items, used_ids, labels, len(strips) + 1)
        strips.extend(labelled_singles)
        used_ids.update(single_ids)
        short_closures = [item for item in items if float(item["length_m"]) < MIN_FACE_LENGTH_M]
        long_unresolved = [item for item in items if float(item["length_m"]) >= MIN_FACE_LENGTH_M and item["id"] not in used_ids]
        diagonal = [item for item in long_unresolved if base.orientation(item) == "D"]
        review_faces = {str(item["id"]) for item in long_unresolved}
        classes = Counter(strip["classification"] for strip in strips)
        total_classes.update(classes)
        floors[floor] = {
            "source_segments": len(items),
            "proposed_centerlines": len(strips),
            "classifications": dict(classes),
            "short_contour_edges_excluded": len(short_closures),
            "long_unresolved_faces": len(long_unresolved),
            "diagonal_unresolved_faces": len(diagonal),
            "long_unresolved": long_unresolved,
            "short_contour_edges": short_closures,
            "proposals": strips,
            "overlay": None,
            "_plot_items": items,
            "_review_faces": sorted(review_faces),
            "_labels": labels,
        }
    all_proposals = [proposal for row in floors.values() for proposal in row["proposals"]]
    for proposal in all_proposals:
        if proposal["classification"] != "REVIEW_GEOMETRY_ONLY":
            continue
        matches = [
            other for other in all_proposals
            if other["classification"] == "CONFIRMED_LABEL_WIDTH" and repeated_plan_match(proposal, other)
        ]
        if matches:
            proposal["classification"] = "CONFIRMED_REPEATED_PLAN_GEOMETRY"
            proposal["repeat_evidence"] = sorted(str(other["proposal_id"]) for other in matches)
    for floor, row in floors.items():
        confirmed = [proposal for proposal in row["proposals"] if proposal["classification"] != "REVIEW_GEOMETRY_ONLY"]
        interior_details = []
        retained = []
        for proposal in row["proposals"]:
            parents = [main for main in confirmed if nested_inside_confirmed(proposal, main)]
            if proposal["classification"] == "REVIEW_GEOMETRY_ONLY" and parents:
                interior_details.append({**proposal, "classification": "INTERIOR_DETAIL_EXCLUDED", "parent_proposals": [main["proposal_id"] for main in parents]})
            else:
                retained.append(proposal)
        row["proposals"] = retained
        row["interior_detail_excluded"] = interior_details
        row["proposed_centerlines"] = len(retained)
        promote_connected_section_families(row["proposals"])
        for proposal in row["proposals"]:
            if proposal["classification"] != "REVIEW_GEOMETRY_ONLY":
                continue
            evidence = proposal.get("evidence_samples", [])
            if evidence and all(
                float(sample["standard_residual_m"]) <= 0.021
                and not sample["label_conflict"]
                for sample in evidence
            ):
                proposal["classification"] = "CONFIRMED_CONTOUR_PAIR_GEOMETRY"
    for floor, row in floors.items():
        row["classifications"] = dict(Counter(proposal["classification"] for proposal in row["proposals"]))
        plot_items = row.pop("_plot_items")
        plot_labels = row.pop("_labels")
        row["overlay"] = plot(floor, plot_items, row["proposals"], set(row.pop("_review_faces")))
        row["review_detail_overlay"] = plot_review_detail(floor, plot_items, row["proposals"], plot_labels)
    total_classes = Counter(proposal["classification"] for row in floors.values() for proposal in row["proposals"])
    totals = {
        "source_segments": sum(row["source_segments"] for row in floors.values()),
        "proposed_centerlines": sum(row["proposed_centerlines"] for row in floors.values()),
        "classifications": dict(total_classes),
        "short_contour_edges_excluded": sum(row["short_contour_edges_excluded"] for row in floors.values()),
        "long_unresolved_faces": sum(row["long_unresolved_faces"] for row in floors.values()),
        "diagonal_unresolved_faces": sum(row["diagonal_unresolved_faces"] for row in floors.values()),
        "interior_detail_excluded": sum(len(row["interior_detail_excluded"]) for row in floors.values()),
    }
    status = "PROPOSAL_REQUIRES_REVIEW" if totals["long_unresolved_faces"] or total_classes["REVIEW_GEOMETRY_ONLY"] else "PROPOSAL_READY"
    result = {"status": status, "scope": "GEO-BEAM-E1-001_CENTERLINE_PROPOSAL", "totals": totals, "floors": floors}
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Propuesta de centrolineas de vigas EDIFICIO_1",
        "",
        f"Estado: `{status}`",
        "",
        "| Piso | Centrolineas | Contorno+etiqueta | Residual+etiqueta | Línea simple+etiqueta | Familia conectada | Repetida en otro piso | Contorno geométrico | Solo geometria | Detalle interior excluido | Cierres cortos | Sin resolver |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for floor, row in floors.items():
        classes = row["classifications"]
        lines.append(f"| {floor} | {row['proposed_centerlines']} | {classes.get('CONFIRMED_LABEL_WIDTH', 0)} | {classes.get('CONFIRMED_RESIDUAL_LABEL_WIDTH', 0)} | {classes.get('CONFIRMED_SINGLE_CENTERLINE_BY_LABEL', 0)} | {classes.get('CONFIRMED_CONNECTED_SECTION_FAMILY', 0)} | {classes.get('CONFIRMED_REPEATED_PLAN_GEOMETRY', 0)} | {classes.get('CONFIRMED_CONTOUR_PAIR_GEOMETRY', 0)} | {classes.get('REVIEW_GEOMETRY_ONLY', 0)} | {len(row['interior_detail_excluded'])} | {row['short_contour_edges_excluded']} | {row['long_unresolved_faces']} |")
    lines.extend(["", "No se modifica el modelo. `CONFIRMED_CONTOUR_PAIR_GEOMETRY` confirma la existencia y el ancho por dos caras RLE-VIGA a separación normalizada sin conflicto de etiqueta; no inventa una altura de sección."])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ED1_BEAM_CENTERLINE_PROPOSAL: {status}")
    print(totals)
    print(f"Reportes: {OUT_JSON} {OUT_MD}")


if __name__ == "__main__":
    main()
