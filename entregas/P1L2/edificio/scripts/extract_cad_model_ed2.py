"""Extrae EDIFICIO_2 (LT2, serie 2024_22) desde sus propios DXF.

Reutiliza la misma logica de extract_cad_model.py (transformacion de
coordenadas CAD cm -> m, categorias por capa, clustering de columnas,
viguetas/muros/losas/diafragmas) pero parametrizada para las laminas del
EDIFICIO_2.

Edificio_2 = ala secundaria (ejes A-D) del edificio de Ingenieria.
Laminas (2024_22):
    100 -> PLANTA FUNDACIONES (radier, N.R.=-8.12; NIVEL SUP RADIER -7.97)
    101 -> PLANTA CIELO 1SS a CIELO PISO 3 (superpuesta, N.O.G.=-5.945)
    102 -> PLANTA CIELO 4PISO (NIVEL SUP LOSA +11.83)

NOTA DE ALTURAS: fundacion/radier es nivel auxiliar, no piso. La lamina 100
declara NIVEL SUPERIOR RADIER -7.97 y la lamina 102 declara NIVEL SUPERIOR
LOSA +11.83 para Piso 4; el diferencial es 19.80 m, igual al z(P4) usado en
EDIFICIO_1. La lamina 101 superpone los cielos S1..P3 en una sola vista; se
mantienen cinco pisos reales canonicos S1/P1/P2/P3/P4.

Salidas (directorio edificio ed2):
    datos/building_2_master.json
    unity_export/model_2_viewer.json
    results/cad_model_2_floor_qc.png
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import ezdxf

from model_contract import EXPECTED_FLOORS, assert_expected_floors, canonicalize_viewer_model

REPO = Path(__file__).resolve().parents[4]
DXF_BASE = os.environ.get("MCOC_DXF_DIR", REPO / "recursos" / "planos" / "dxf_generated")
DXF_DIR = Path(DXF_BASE) / "2024_22"
EDIF_DIR = Path(__file__).resolve().parents[1]
DATOS_DIR = EDIF_DIR / "datos"
RESULTS_DIR = EDIF_DIR / "results"
UNITY_DIR = EDIF_DIR.parent / "unity_export"

BUILDING_ID = "EDIFICIO_2"

LEVEL_REVIEW = {
    "status": "SOURCE_ELEVATIONS_REVIEWED",
    "datum": {
        "level_kind": "FOUNDATION_LEVEL",
        "source_elevation_m": -7.97,
        "model_z_m": 0.0,
        "evidence": "2024_22-100: (NIVEL SUPERIOR RADIER -7.97); fundacion/radier no es piso.",
    },
    "floors": [
        {"floor_name": "S1", "source_elevation_m": -4.01, "model_z_m": 3.96,
         "evidence": "Inferido desde P4=+11.83 y datum radier=-7.97 con modulo 3.96 m; lamina 101 superpone cielos S1..P3 y no entrega valor individual legible."},
        {"floor_name": "P1", "source_elevation_m": -0.05, "model_z_m": 7.92,
         "evidence": "Inferido desde P4=+11.83 y datum radier=-7.97 con modulo 3.96 m; lamina 101 superpone cielos S1..P3."},
        {"floor_name": "P2", "source_elevation_m": 3.91, "model_z_m": 11.88,
         "evidence": "Inferido desde P4=+11.83 y datum radier=-7.97 con modulo 3.96 m; lamina 101 superpone cielos S1..P3."},
        {"floor_name": "P3", "source_elevation_m": 7.87, "model_z_m": 15.84,
         "evidence": "Inferido desde P4=+11.83 y datum radier=-7.97 con modulo 3.96 m; lamina 101 superpone cielos S1..P3."},
        {"floor_name": "P4", "source_elevation_m": 11.83, "model_z_m": 19.80,
         "evidence": "2024_22-102: (NIVEL SUPERIOR LOSA + 11.83); 11.83 - (-7.97) = 19.80 m."},
    ],
    "non_floor_level_notes": [
        "2024_22-100: N.R.=-8.12 y N.O.G.=-9.37 son cotas tecnicas de fundacion/terreno, no pisos.",
        "2024_22-101: N.O.G.=-5.945/VAR y N.S.M.=-3.23 aparecen como notas locales; no se usaron para crear pisos adicionales.",
    ],
}


@dataclass(frozen=True)
class FloorSpec:
    floor_id: str
    label: str
    dxf_name: str
    z_m: float
    bbox_cm: tuple[float, float, float, float]
    origin_x_cm: float
    origin_y_cm: float


# Laminas y regiones del EDIFICIO_2. Origen = interseccion eje A (x) x eje 1 (y)
# por lamina, de modo que eje A -> x=0 y eje 1 -> y=0 (misma convencion EDIFICIO_1).
FLOORS = [
    FloorSpec("base", "Fundaciones (radier)", "2024_22-100.dxf", 0.00,
              (500.0, 1000.0, 4400.0, 3300.0), 985.0, 2688.0),
    FloorSpec("1S", "Cielo 1SS..Piso 3 (superpuesto)", "2024_22-101.dxf", 3.96,
              (700.0, 600.0, 4600.0, 3200.0), 1485.0, 2708.0),
    FloorSpec("1", "Cielo piso 1 (lam 101)", "2024_22-101.dxf", 7.92,
              (700.0, 600.0, 4600.0, 3200.0), 1485.0, 2708.0),
    FloorSpec("2", "Cielo piso 2 (lam 101)", "2024_22-101.dxf", 11.88,
              (700.0, 600.0, 4600.0, 3200.0), 1485.0, 2708.0),
    FloorSpec("3", "Cielo piso 3 (lam 101)", "2024_22-101.dxf", 15.84,
              (700.0, 600.0, 4600.0, 3200.0), 1485.0, 2708.0),
    FloorSpec("4", "Cielo piso 4", "2024_22-102.dxf", 19.80,
              (700.0, 900.0, 4600.0, 3600.0), 1485.0, 3028.0),
]

LAYER_CATEGORIES = {
    "RLE-VIGA": "beam",
    "RLE-MURO": "wall",
    "RLE-PILAR": "column_plan",
    "RLE-LOSA": "slab_edge",
    "RLE-LOSAS": "slab_edge",
    "RLE-SOLID": "column_plan",
    "RLE-FUNDACION": "cad_reference",
    "RLE-EJES": "axis",
}

COLORS = {
    "beam": "#1f77b4", "wall": "#2ca02c", "column": "#ff7f0e",
    "column_plan": "#ff7f0e", "slab_edge": "#999999", "slab": "#8fb8ff",
    "slab_label": "#bbbbbb", "axis": "#d62728", "diaphragm": "#9467bd",
    "support": "#000000", "cad_reference": "#7d8794",
}


def point_inside_bbox(p, bbox):
    x0, y0, x1, y1 = bbox
    return x0 <= p[0] <= x1 and y0 <= p[1] <= y1


def segment_inside_bbox(points, bbox):
    if not points:
        return False
    inside = sum(1 for p in points if point_inside_bbox(p, bbox))
    return inside >= max(1, len(points) // 2)


def transform_point(p, floor):
    x_cm, y_cm = p
    return (x_cm - floor.origin_x_cm) / 100.0, (floor.origin_y_cm - y_cm) / 100.0, floor.z_m


def entity_segments(entity):
    et = entity.dxftype()
    if et == "LINE":
        yield [(entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y)]
    elif et == "LWPOLYLINE":
        pts = [(p[0], p[1]) for p in entity.get_points()]
        for a, b in zip(pts, pts[1:]):
            yield [a, b]
        if entity.closed and len(pts) > 2:
            yield [pts[-1], pts[0]]


def entity_text(entity):
    if entity.dxftype() == "TEXT":
        return entity.dxf.text
    if entity.dxftype() == "MTEXT":
        return entity.text
    return None


def text_category(text):
    up = text.upper().replace(" ", "")
    if up.startswith("V.M"):
        return "steel_beam_label"
    if up.startswith("V.") or up.startswith("+V.") or up.startswith("V.S") or up.startswith("V.I") or up.startswith("V.F"):
        return "beam_label"
    if up.startswith("P.") or up.startswith("P.M"):
        return "column_label"
    if up.startswith("M.H.A") or up.startswith("M.I"):
        return "wall_label"
    return None


def extract_labels(floor):
    doc = ezdxf.readfile(DXF_DIR / floor.dxf_name)
    labels = []
    idx = 1
    for e in doc.modelspace():
        if e.dxf.layer not in ("RLE-TEXTO-1",):
            continue
        raw = entity_text(e)
        if not raw:
            continue
        text = " ".join(raw.replace("\\P", " ").split())
        cat = text_category(text)
        if cat is None:
            continue
        ins = e.dxf.insert
        if not point_inside_bbox((ins.x, ins.y), floor.bbox_cm):
            continue
        x, y, z = transform_point((ins.x, ins.y), floor)
        labels.append({"labelTag": f"LBL2_{floor.floor_id}_{cat}_{idx:04d}", "floor": floor.floor_id,
                       "floor_label": floor.label, "source_dxf": floor.dxf_name, "source_layer": e.dxf.layer,
                       "category": cat, "text": text, "point": [x, y, z], "building": BUILDING_ID})
        idx += 1
    return labels


def extract_segments(floor):
    doc = ezdxf.readfile(DXF_DIR / floor.dxf_name)
    segments = []
    idx = 1
    for e in doc.modelspace():
        cat = LAYER_CATEGORIES.get(e.dxf.layer)
        if cat is None:
            continue
        for raw in entity_segments(e):
            if not segment_inside_bbox(raw, floor.bbox_cm):
                continue
            seg = [transform_point(p, floor) for p in raw]
            L = math.dist(seg[0], seg[1])
            if L < 0.05:
                continue
            segments.append({"elementTag": f"CAD2_{floor.floor_id}_{cat}_{idx:04d}", "floor": floor.floor_id,
                             "floor_label": floor.label, "source_dxf": floor.dxf_name, "source_layer": e.dxf.layer,
                             "category": cat, "points": seg, "length_m": L, "building": BUILDING_ID,
                             "confidence": "medium" if cat in {"beam", "wall", "column_plan"} else "low"})
            idx += 1
    return segments


def floor_diaphragms(segments):
    dias = []
    for f in FLOORS:
        if f.floor_id == "base":
            continue
        pts = [p for s in segments if s["floor"] == f.floor_id for p in s["points"]]
        if not pts:
            continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; z = f.z_m
        dias.append({"floor": f.floor_id, "category": "diaphragm", "points": [
            (min(xs), min(ys), z), (max(xs), min(ys), z), (max(xs), max(ys), z),
            (min(xs), max(ys), z), (min(xs), min(ys), z)]})
    return dias


def prev_z(fid):
    p = 0.0
    for f in FLOORS:
        if f.floor_id == fid:
            return p
        p = f.z_m
    return 0.0


def column_clusters(floor_id, segments):
    segs = [s for s in segments if s["floor"] == floor_id and s["category"] == "column_plan" and 0.08 <= s["length_m"] <= 1.50]
    clusters = []
    for s in segs:
        mx = (s["points"][0][0] + s["points"][1][0]) / 2
        my = (s["points"][0][1] + s["points"][1][1]) / 2
        cl = None
        for c in clusters:
            if math.hypot(mx - c["center"][0], my - c["center"][1]) <= 0.85:
                cl = c; break
        if cl is None:
            cl = {"segments": [], "points": [], "center": (mx, my)}
            clusters.append(cl)
        cl["segments"].append(s); cl["points"].extend([p[:2] for p in s["points"]])
        xs = [p[0] for p in cl["points"]]; ys = [p[1] for p in cl["points"]]
        cl["center"] = (sum(xs) / len(xs), sum(ys) / len(ys))
    out = []
    for c in clusters:
        xs = [p[0] for p in c["points"]]; ys = [p[1] for p in c["points"]]
        out.append({"center": c["center"], "width_m": min(max(max(xs) - min(xs), 0.35), 1.20),
                    "depth_m": min(max(max(ys) - min(ys), 0.35), 1.20), "segments": c["segments"]})
    return out


def nearest(c, clusters, tol=0.85):
    best, bd = None, tol
    for o in clusters:
        d = math.hypot(c[0] - o["center"][0], c[1] - o["center"][1])
        if d <= bd:
            best, bd = o, d
    return best


def infer_missing(clusters_by_floor):
    if not clusters_by_floor.get("1S") and clusters_by_floor.get("1"):
        clusters_by_floor["1S"] = [{**c, "confidence": "inferred_from_1"} for c in clusters_by_floor["1"]]
    ids = [f.floor_id for f in FLOORS if f.floor_id != "base"]
    for i in range(1, len(ids) - 1):
        prev = ids[i - 1]; cur = ids[i]; nxt = ids[i + 1]
        current = clusters_by_floor.setdefault(cur, [])
        for pc in clusters_by_floor.get(prev, []):
            if nearest(pc["center"], current):
                continue
            nc = nearest(pc["center"], clusters_by_floor.get(nxt, []))
            if nc is None:
                continue
            current.append({"center": ((pc["center"][0] + nc["center"][0]) / 2, (pc["center"][1] + nc["center"][1]) / 2),
                            "width_m": max(pc["width_m"], nc["width_m"]), "depth_m": max(pc["depth_m"], nc["depth_m"]),
                            "segments": pc["segments"], "confidence": f"inferred_{prev}_{nxt}"})
    for i in range(len(ids) - 1, 0, -1):
        cur_f = ids[i]; prv_f = ids[i - 1]
        prev = clusters_by_floor.setdefault(prv_f, [])
        for c in list(clusters_by_floor.get(cur_f, [])):
            if nearest(c["center"], prev):
                continue
            prev.append({**c, "confidence": f"inferred_from_above_{cur_f}"})


def generate_column_solids(segments):
    ids = [f.floor_id for f in FLOORS if f.floor_id != "base"]
    by = {fid: column_clusters(fid, segments) for fid in ids}
    infer_missing(by)
    solids = []
    for fid in ids:
        ztop = next(f.z_m for f in FLOORS if f.floor_id == fid)
        zbot = prev_z(fid); h = ztop - zbot
        for i, c in enumerate(by.get(fid, []), 1):
            solids.append({"solidTag": f"SOL2_{fid}_column_{i:04d}", "category": "column", "kind": "box",
                           "floor": fid, "center": [c["center"][0], c["center"][1], (zbot + ztop) / 2],
                           "width_m": c["width_m"], "depth_m": c["depth_m"], "height_m": h, "length_m": h,
                           "source_layer": "RLE-PILAR", "source_dxf": c["segments"][0]["source_dxf"] if c["segments"] else "inferred",
                           "sourceTags": [s["elementTag"] for s in c["segments"]],
                           "confidence": c.get("confidence", "medium"), "building": BUILDING_ID})
    return solids


def merged_walls(floor_id, segments):
    ws = [s for s in segments if s["floor"] == floor_id and s["category"] == "wall"]
    buckets = defaultdict(list); passthrough = []
    for s in ws:
        a, b = s["points"]
        dx = b[0] - a[0]; dy = b[1] - a[1]
        if abs(dx) <= 0.15:
            fx = round(((a[0] + b[0]) / 2) / 0.15) * 0.15
            lo, hi = sorted((a[1], b[1])); buckets[("V", fx)].append((lo, hi, s))
        elif abs(dy) <= 0.15:
            fy = round(((a[1] + b[1]) / 2) / 0.15) * 0.15
            lo, hi = sorted((a[0], b[0])); buckets[("H", fy)].append((lo, hi, s))
        else:
            passthrough.append(s)
    merged = []; mi = 1
    for (ori, fx), iv in buckets.items():
        iv.sort(key=lambda t: t[0])
        ca, cb, cs = iv[0]
        for a, b, s in iv[1:]:
            if a <= cb + 0.35:
                cb = max(cb, b); continue
            merged.append(mkg(floor_id, ori, fx, ca, cb, cs, mi)); mi += 1
            ca, cb, cs = a, b, s
        merged.append(mkg(floor_id, ori, fx, ca, cb, cs, mi)); mi += 1
    merged.extend(passthrough)
    return [m for m in merged if math.dist(m["points"][0], m["points"][1]) >= 0.35]


def mkg(floor_id, ori, fx, lo, hi, src, i):
    z = src["points"][0][2]
    pts = [(fx, lo, z), (fx, hi, z)] if ori == "V" else [(lo, fx, z), (hi, fx, z)]
    return {"elementTag": f"MG2_{floor_id}_wall_{i:04d}", "floor": floor_id,
            "source_dxf": src["source_dxf"], "source_layer": "RLE-MURO_merged", "category": "wall",
            "points": pts, "length_m": math.dist(pts[0], pts[1]), "confidence": "merged_from_RLE-MURO",
            "building": BUILDING_ID}


def generate_wall_solids(segments):
    solids = []; counter = 0
    for f in FLOORS:
        if f.floor_id == "base":
            continue
        zbot = prev_z(f.floor_id)
        for seg in merged_walls(f.floor_id, segments):
            a, b = seg["points"]; ztop = a[2]; counter += 1
            solids.append({"solidTag": f"SOL2_{f.floor_id}_wall_{counter:04d}", "category": "wall", "kind": "linear_prism",
                           "floor": f.floor_id, "start": [a[0], a[1], (zbot + ztop) / 2], "end": [b[0], b[1], (zbot + ztop) / 2],
                           "width_m": 0.22, "height_m": ztop - zbot, "length_m": math.dist(a, b),
                           "source_layer": "RLE-MURO", "source_dxf": seg["source_dxf"], "confidence": seg["confidence"],
                           "building": BUILDING_ID})
    return solids


def bottom_z(s):
    if "center" in s:
        return float(s["center"][2]) - float(s.get("height_m", 0)) / 2
    return float(s["start"][2]) - float(s.get("height_m", 0)) / 2


def generate_supports(solids):
    out = []; counter = 0
    for s in solids:
        if s["category"] not in ("column", "wall") or abs(bottom_z(s)) > 0.05:
            continue
        counter += 1
        if s["category"] == "column":
            cx, cy, _ = s["center"]
            out.append({"solidTag": f"SOL2_base_support_{counter:04d}", "category": "support", "kind": "box",
                        "floor": "base", "center": [cx, cy, -0.15], "width_m": max(float(s["width_m"]) * 1.8, 0.9),
                        "depth_m": max(float(s["depth_m"]) * 1.8, 0.9), "height_m": 0.3, "length_m": 0.3,
                        "source_layer": "generated_connected_support", "source_dxf": s.get("source_dxf"),
                        "sourceTags": [s["solidTag"]], "confidence": "qa_connected", "building": BUILDING_ID})
        else:
            st = tuple(s["start"]); en = tuple(s["end"])
            out.append({"solidTag": f"SOL2_base_support_{counter:04d}", "category": "support", "kind": "linear_prism",
                        "floor": "base", "start": [st[0], st[1], -0.15], "end": [en[0], en[1], -0.15],
                        "width_m": max(float(s["width_m"]) * 1.8, 0.45), "height_m": 0.3, "length_m": math.dist(st, en),
                        "source_layer": "generated_connected_support", "source_dxf": s.get("source_dxf"),
                        "sourceTags": [s["solidTag"]], "confidence": "qa_connected", "building": BUILDING_ID})
    return out


def generate_solids(segments, diaphragms):
    solids = []; cb = 0
    for seg in segments:
        f = seg["floor"]; cat = seg["category"]
        if seg["length_m"] < 0.35:
            continue
        a, b = seg["points"]
        if cat == "beam" and f != "base":
            cb += 1
            solids.append({"solidTag": f"SOL2_{f}_beam_{cb:04d}", "category": "beam", "kind": "linear_prism", "floor": f,
                           "start": [a[0], a[1], a[2] - 0.30], "end": [b[0], b[1], b[2] - 0.30], "width_m": 0.32,
                           "height_m": 0.60, "length_m": math.dist(a, b), "source_layer": seg["source_layer"],
                           "source_dxf": seg["source_dxf"], "sourceTag": seg["elementTag"], "confidence": seg["confidence"],
                           "building": BUILDING_ID})
    solids.extend(generate_wall_solids(segments))
    solids.extend(generate_column_solids(segments))
    solids.extend(generate_supports(solids))
    cs = 0
    for d in diaphragms:
        xs = [p[0] for p in d["points"]]; ys = [p[1] for p in d["points"]]; z = d["points"][0][2]; cs += 1
        solids.append({"solidTag": f"SOL2_{d['floor']}_slab_{cs:04d}", "category": "slab", "kind": "slab_box", "floor": d["floor"],
                       "center": [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, z - 0.04], "width_m": max(xs) - min(xs),
                       "depth_m": max(ys) - min(ys), "height_m": 0.08, "area_m2": (max(xs) - min(xs)) * (max(ys) - min(ys)),
                       "source_layer": "generated_diaphragm_bbox", "confidence": "low", "building": BUILDING_ID})
    return solids


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_qc(path, segments):
    fig, axes = plt.subplots(3, 2, figsize=(14, 16))
    flat = list(axes.flat)
    for ax, f in zip(flat, FLOORS):
        ax.set_title(f"{f.floor_id} - {f.label}"); ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]")
        for cat in ["axis", "slab_edge", "support", "wall", "column_plan", "beam"]:
            color = COLORS[cat]
            for s in segments:
                if s["floor"] != f.floor_id or s["category"] != cat:
                    continue
                pts = s["points"]; alpha = 0.25 if cat in ("axis", "slab_edge") else 0.9
                lw = 0.5 if cat in ("axis", "slab_edge") else 1.2
                ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=color, linewidth=lw, alpha=alpha)
        ax.grid(True, linewidth=0.3, alpha=0.4)
    for cat, color in COLORS.items():
        if cat in ("diaphragm", "slab_label"):
            continue
        flat[-1].plot([], [], color=color, label=cat)
    flat[-1].axis("off"); flat[-1].legend(loc="center")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(path, dpi=180); plt.close(fig)


def main():
    segments = []; labels = []
    for f in FLOORS:
        segments.extend(extract_segments(f))
        labels.extend(extract_labels(f))
    dias = floor_diaphragms(segments)
    solids = generate_solids(segments, dias)
    qc_segments = segments

    raw_payload = {"model": f"{BUILDING_ID} - Unity/web QA viewer", "units": "m",
                   "availableToggles": ["beam", "wall", "column", "support", "slab", "axis", "diaphragm", "cad_reference", "ids"],
                   "colors": COLORS, "solids": solids, "segments": segments, "labels": labels, "diaphragms": dias,
                   "notes": ["EDIFICIO_2 desde sus propios DXF 2024_22.",
                             "Viewer con pisos canonicos S1/P1/P2/P3/P4; fundacion/radier se marca como FOUNDATION_LEVEL asociado a S1.",
                             "Lam 101 superpone cielos S1..P3; se repite geometria por piso sin crear pisos extra."]}
    payload = canonicalize_viewer_model(raw_payload, building=BUILDING_ID)
    floor_report = assert_expected_floors(payload, str(UNITY_DIR / "model_2_viewer.json"))
    solids = payload["solids"]
    segments = payload["segments"]
    labels = payload["labels"]
    dias = payload["diaphragms"]

    summary = defaultdict(lambda: defaultdict(int))
    for s in segments:
        summary[s["floor"]][s["category"]] += 1
    summary = {k: dict(v) for k, v in summary.items()}

    master = {"building": BUILDING_ID, "note": "EDIFICIO_2 (LT2, 2024_22) - ala secundaria ejes A-D. Laminas 100/101/102. "
              "Pisos canonicos S1/P1/P2/P3/P4. Lamina 101 superpone S1/P1/P2/P3. Fundacion/radier es nivel auxiliar.",
              "units": "m", "coordinate_source": "DXF 2024_22; origen por lamina = interseccion eje A x eje 1.",
              "expected_floors": list(EXPECTED_FLOORS),
              "source_structural_levels": [{"source_floor": f.floor_id, "label": f.label, "dxf": f.dxf_name, "z_m": f.z_m} for f in FLOORS],
              "floor_validation": floor_report,
              "level_review": LEVEL_REVIEW,
              "summary": summary, "segments": segments, "labels": labels}

    UNITY_DIR.mkdir(parents=True, exist_ok=True)
    DATOS_DIR.mkdir(parents=True, exist_ok=True)
    (DATOS_DIR / "building_2_master.json").write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATOS_DIR / "edificio_2_levels_review.json").write_text(json.dumps(LEVEL_REVIEW, indent=2, ensure_ascii=False), encoding="utf-8")
    (UNITY_DIR / "model_2_viewer.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    plot_qc(RESULTS_DIR / "cad_model_2_floor_qc.png", qc_segments)

    print("EDIFICIO_2 model generado")
    print(f"  segmentos: {len(segments)}  labels: {len(labels)}  solidos: {len(solids)}  diafragmas: {len(dias)}")
    for floor_id in EXPECTED_FLOORS:
        print(f"  piso {floor_id}: {sum(1 for s in segments if s['floor'] == floor_id)} seg")
    print("  floor contract:", floor_report["status"], floor_report["actual_floors"])
    print("  ", DATOS_DIR / "building_2_master.json")
    print("  ", DATOS_DIR / "edificio_2_levels_review.json")
    print("  ", UNITY_DIR / "model_2_viewer.json")


if __name__ == "__main__":
    sys.exit(main())
