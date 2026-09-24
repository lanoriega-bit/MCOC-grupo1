#!/usr/bin/env python3
"""Audita las caras RLE-MURO de EDIFICIO_2 contra 2024_22.

El script es diagnostico: recupera centrolineas desde pares de caras del DXF,
clasifica cierres de contorno y contrasta el espesor geometrico con textos M.H.A.
No modifica el modelo canonico.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf
from PIL import Image, ImageDraw


REPO = Path(__file__).resolve().parents[3]
DXF_DIR = REPO / "recursos/planos/dxf_full/2024_22"
OUT_DIR = REPO / "entregas/POST_P1L4/ed2_walls"
OUT_JSON = OUT_DIR / "ed2_wall_face_audit.json"
OUT_MD = OUT_DIR / "REPORT.md"
FLOORS = ("S1", "P1", "P2", "P3", "P4")
STANDARD_THICKNESSES_M = (0.20, 0.25, 0.30, 0.60)
FLOOR_SOURCES = {
    "S1": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P1": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P2": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P3": ("2024_22-101.dxf", (700.0, 600.0, 4600.0, 3200.0), (1485.0, 2708.0)),
    "P4": ("2024_22-102.dxf", (700.0, 900.0, 4600.0, 3600.0), (1485.0, 3028.0)),
}


def inside(point, bbox):
    return bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]


def transform(point, origin):
    return [(point[0] - origin[0]) / 100.0, (origin[1] - point[1]) / 100.0]


def entity_text(entity):
    if entity.dxftype() == "TEXT":
        return entity.dxf.text
    if entity.dxftype() == "MTEXT":
        return entity.text
    return None


def parse_thickness(text):
    clean = text.upper().replace("\\P", " ").replace(",", ".")
    if "M.H.A" not in clean and "MHA" not in clean:
        return None
    match = re.search(r"E\s*=\s*(\d+(?:\.\d+)?)", clean)
    if not match:
        return None
    value = float(match.group(1))
    return value / 100.0 if value > 2.0 else value


def read_source(floor):
    filename, bbox, origin = FLOOR_SOURCES[floor]
    doc = ezdxf.readfile(DXF_DIR / filename)
    faces, labels = [], []
    for entity in doc.modelspace():
        raw_text = entity_text(entity)
        if raw_text and entity.dxf.layer == "RLE-TEXTO-1":
            insertion = entity.dxf.insert
            raw_point = (float(insertion.x), float(insertion.y))
            thickness = parse_thickness(raw_text)
            if thickness and inside(raw_point, bbox):
                labels.append({"text": " ".join(raw_text.replace("\\P", " ").split()), "xy_m": transform(raw_point, origin), "thickness_m": thickness})
        if entity.dxf.layer != "RLE-MURO":
            continue
        segments = []
        if entity.dxftype() == "LINE":
            segments = [((entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y))]
        elif entity.dxftype() == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            segments = list(zip(points, points[1:]))
            if entity.closed and len(points) > 2:
                segments.append((points[-1], points[0]))
        for first, second in segments:
            if not (inside(first, bbox) or inside(second, bbox)):
                continue
            start, end = transform(first, origin), transform(second, origin)
            if math.dist(start, end) < 0.05:
                continue
            faces.append({"id": f"{floor}-RLE-MURO-{len(faces)+1:04d}", "floor": floor, "start": start, "end": end, "source_dxf": filename})
    return faces, labels


def line_data(face):
    a, b = face["start"], face["end"]
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    if dx <= 0.03 and dy > 0.03:
        return "V", (a[0] + b[0]) / 2.0, *sorted((a[1], b[1]))
    if dy <= 0.03 and dx > 0.03:
        return "H", (a[1] + b[1]) / 2.0, *sorted((a[0], b[0]))
    return "D", 0.0, 0.0, math.dist(a, b)


def candidate(first, second):
    o1, f1, a1, b1 = line_data(first)
    o2, f2, a2, b2 = line_data(second)
    if o1 != o2 or o1 == "D":
        return None
    thickness = abs(f1 - f2)
    standard = min(STANDARD_THICKNESSES_M, key=lambda value: abs(value - thickness))
    residual = abs(thickness - standard)
    if residual > 0.031:
        return None
    overlap = min(b1, b2) - max(a1, a2)
    minimum = min(b1 - a1, b2 - a2)
    if overlap < 0.35 or overlap / max(minimum, 1e-9) < 0.55:
        return None
    return {"thickness_m": thickness, "standard_thickness_m": standard, "standard_residual_m": residual, "overlap_m": overlap, "overlap_ratio": overlap / minimum}


def recover_pairs(faces):
    axis_faces = [face for face in faces if line_data(face)[0] != "D"]
    by_id = {face["id"]: face for face in axis_faces}
    edges = {}
    for index, first in enumerate(axis_faces):
        for second in axis_faces[index + 1:]:
            metrics = candidate(first, second)
            if metrics:
                edges[tuple(sorted((first["id"], second["id"])))] = metrics
    atoms = defaultdict(list)
    for orientation in ("H", "V"):
        oriented = [face for face in axis_faces if line_data(face)[0] == orientation]
        breakpoints = sorted({round(value, 6) for face in oriented for value in line_data(face)[2:]})
        for lo, hi in zip(breakpoints, breakpoints[1:]):
            if hi - lo < 0.05:
                continue
            mid = (lo + hi) / 2.0
            active = [face["id"] for face in oriented if line_data(face)[2] <= mid <= line_data(face)[3]]
            candidates = []
            for index, first in enumerate(active):
                for second in active[index + 1:]:
                    key = tuple(sorted((first, second)))
                    if key in edges:
                        metric = edges[key]
                        candidates.append((metric["standard_residual_m"], -metric["overlap_ratio"], key))
            used = set()
            for _, _, key in sorted(candidates):
                if key[0] in used or key[1] in used:
                    continue
                used.update(key)
                atoms[key].append((lo, hi))
    pairs = []
    for key, intervals in sorted(atoms.items()):
        intervals.sort()
        merged = []
        for lo, hi in intervals:
            if merged and lo <= merged[-1][1] + 1e-5:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        first, second = by_id[key[0]], by_id[key[1]]
        orient, fixed1, _, _ = line_data(first)
        _, fixed2, _, _ = line_data(second)
        fixed = (fixed1 + fixed2) / 2.0
        for lo, hi in merged:
            if hi - lo < 0.35:
                continue
            start, end = ([fixed, lo], [fixed, hi]) if orient == "V" else ([lo, fixed], [hi, fixed])
            metric = edges[key]
            pairs.append({
                "pair_id": f"{first['floor']}-E2-WP-{len(pairs)+1:03d}", "floor": first["floor"], "orientation": orient,
                "face_ids": list(key), "centerline_start_xy_m": [round(v, 4) for v in start], "centerline_end_xy_m": [round(v, 4) for v in end],
                "length_m": round(hi-lo, 4), "thickness_m": round(metric["standard_thickness_m"], 4),
                "measured_face_separation_m": round(metric["thickness_m"], 4), "standard_residual_m": round(metric["standard_residual_m"], 4),
                "source_sheet": first["source_dxf"], "classification": "CONFIRMED_CONTOUR_PAIR",
            })
    used = {face_id for pair in pairs for face_id in pair["face_ids"]}
    unmatched = [face for face in faces if face["id"] not in used]
    return pairs, unmatched


def point_segment_distance(point, start, end):
    vx, vy = end[0]-start[0], end[1]-start[1]
    length2 = vx*vx + vy*vy
    if length2 == 0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0]-start[0])*vx + (point[1]-start[1])*vy)/length2))
    return math.hypot(point[0]-(start[0]+t*vx), point[1]-(start[1]+t*vy))


def attach_labels(pairs, labels):
    for pair in pairs:
        ranked = sorted((point_segment_distance(label["xy_m"], pair["centerline_start_xy_m"], pair["centerline_end_xy_m"]), label) for label in labels)
        distance, label = ranked[0] if ranked else (math.inf, None)
        if label and distance <= 2.5:
            agrees = abs(label["thickness_m"] - pair["thickness_m"]) <= 0.031
            pair["nearest_wall_label"] = {**label, "distance_m": round(distance, 4), "agrees_with_geometry": agrees}
            pair["thickness_source"] = "CAD_CONTOUR_PAIR+TEXT_LABEL" if agrees else "CAD_CONTOUR_PAIR_LABEL_CONFLICT_REVIEW"
        else:
            pair["nearest_wall_label"] = None
            pair["thickness_source"] = "CAD_CONTOUR_PAIR"


def segment_overlap(first, second, fixed_tolerance=0.08):
    if first["orientation"] != second["orientation"]:
        return 0.0
    if first["orientation"] == "V":
        f1, f2 = first["centerline_start_xy_m"][0], second["centerline_start_xy_m"][0]
        a1, b1 = sorted((first["centerline_start_xy_m"][1], first["centerline_end_xy_m"][1]))
        a2, b2 = sorted((second["centerline_start_xy_m"][1], second["centerline_end_xy_m"][1]))
    else:
        f1, f2 = first["centerline_start_xy_m"][1], second["centerline_start_xy_m"][1]
        a1, b1 = sorted((first["centerline_start_xy_m"][0], first["centerline_end_xy_m"][0]))
        a2, b2 = sorted((second["centerline_start_xy_m"][0], second["centerline_end_xy_m"][0]))
    return max(0.0, min(b1,b2)-max(a1,a2)) if abs(f1-f2) <= fixed_tolerance else 0.0


def draw_overlay(path, floor, faces, pairs, unmatched):
    points = [p for face in faces for p in (face["start"], face["end"])]
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    width, height, margin = 1200, 760, 60
    scale = min((width-2*margin)/max(xmax-xmin,1), (height-2*margin)/max(ymax-ymin,1))
    xy = lambda p: (margin+(p[0]-xmin)*scale, height-margin-(p[1]-ymin)*scale)
    image = Image.new("RGB", (width,height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((35,20), f"EDIFICIO_2 {floor}: gris=caras 2024_22, azul=centrolinea, rojo=cierre/revision", fill="#111")
    for face in faces:
        draw.line((*xy(face["start"]), *xy(face["end"])), fill="#a0a0a0", width=3)
    for pair in pairs:
        color = "#f0a000" if "CONFLICT" in pair["thickness_source"] else "#1677d2"
        draw.line((*xy(pair["centerline_start_xy_m"]), *xy(pair["centerline_end_xy_m"])), fill=color, width=4)
    for face in unmatched:
        draw.line((*xy(face["start"]), *xy(face["end"])), fill="#d93025", width=5)
    image.save(path)


def main():
    if len(sys.argv) > 1:
        global DXF_DIR
        DXF_DIR = Path(sys.argv[1])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    floor_rows, all_pairs = {}, {}
    for floor in FLOORS:
        faces, labels = read_source(floor)
        pairs, unmatched = recover_pairs(faces)
        attach_labels(pairs, labels)
        all_pairs[floor] = pairs
        unmatched_rows = []
        for face in unmatched:
            length = round(math.dist(face["start"], face["end"]),4)
            classification = "CONTOUR_CLOSING_EDGE_EXCLUDED" if length <= 0.66 else "REVIEW_REQUIRED"
            unmatched_rows.append({"face_id":face["id"],"length_m":length,"classification":classification})
        overlay = OUT_DIR / f"{floor.lower()}_wall_face_pairs.png"
        draw_overlay(overlay, floor, faces, pairs, unmatched)
        floor_rows[floor] = {
            "source_contour_segments": len(faces), "confirmed_physical_walls": len(pairs),
            "unmatched_faces": len(unmatched), "unresolved_unmatched_faces": sum(r["classification"]=="REVIEW_REQUIRED" for r in unmatched_rows),
            "label_conflicts": sum("CONFLICT" in p["thickness_source"] for p in pairs),
            "thicknesses_m": dict(Counter(str(p["thickness_m"]) for p in pairs)),
            "unmatched_classification": unmatched_rows, "pairs": pairs,
            "overlay": str(overlay.relative_to(REPO)).replace("\\","/"),
        }
    continuity = []
    for lower, upper in zip(FLOORS,FLOORS[1:]):
        for wall in all_pairs[lower]:
            candidates = [(segment_overlap(wall, other),other) for other in all_pairs[upper]]
            overlap,best = max(candidates,key=lambda x:x[0],default=(0,None))
            continuity.append({"lower_floor":lower,"upper_floor":upper,"lower_pair_id":wall["pair_id"],"upper_pair_id":best["pair_id"] if best and overlap>=0.35 else None,"overlap_m":round(overlap,4),"status":"CONTINUOUS" if best and overlap>=0.35 else "TERMINATES_VALIDLY_OR_REVIEW"})
    totals = {
        "source_contour_segments": sum(r["source_contour_segments"] for r in floor_rows.values()),
        "confirmed_physical_walls": sum(r["confirmed_physical_walls"] for r in floor_rows.values()),
        "unmatched_faces": sum(r["unmatched_faces"] for r in floor_rows.values()),
        "unresolved_unmatched_faces": sum(r["unresolved_unmatched_faces"] for r in floor_rows.values()),
        "label_conflicts": sum(r["label_conflicts"] for r in floor_rows.values()),
        "continuous_between_adjacent_floors": sum(r["status"]=="CONTINUOUS" for r in continuity),
    }
    status = "PASS" if totals["unresolved_unmatched_faces"]==0 and totals["label_conflicts"]==0 else "PASS_WITH_REVIEW_ITEMS"
    payload = {"status":status,"scope":"EXT-2_ED2_WALL_PRIMARY_AUDIT","primary_source":"2024_22-101/102 full DXF","policy":"paired opposite RLE-MURO contour faces define one physical wall centerline; short closures are not independent walls","totals":totals,"floors":floor_rows,"vertical_continuity":continuity}
    OUT_JSON.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Auditoria primaria de muros EDIFICIO_2","",f"Estado: `{status}`","","> Fuente primaria: `2024_22-101/102` (DXF completo). Las coincidencias externas solo se usan como pista.","","| Piso | Caras DXF | Muros físicos | Cierres | Sin resolver | Conflictos etiqueta |","|---|---:|---:|---:|---:|---:|"]
    for floor,row in floor_rows.items():
        lines.append(f"| {floor} | {row['source_contour_segments']} | {row['confirmed_physical_walls']} | {row['unmatched_faces']-row['unresolved_unmatched_faces']} | {row['unresolved_unmatched_faces']} | {row['label_conflicts']} |")
    lines += ["","La geometría vigente de EDIFICIO_2 contiene 20 prismas por piso porque conserva ambas caras y cierres. Este diagnóstico recupera una centrolinea por par de caras; cualquier conflicto de etiqueta queda bloqueado para corrección automática."]
    OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"totals":totals,"by_floor":{k:{x:v for x,v in r.items() if x in ('source_contour_segments','confirmed_physical_walls','unmatched_faces','unresolved_unmatched_faces','label_conflicts','thicknesses_m')} for k,r in floor_rows.items()}},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
