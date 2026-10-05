"""Panelizacion analitica de losas (panos) a partir de las vigas reales.

Los panos NO existen como poligonos cerrados en el modelo combinado: los
``slab`` son bboxes de diafragma (`generated_diaphragm_bbox`) y en los DXF la
capa RLE-LOSA no tiene poligonos cerrados. Se construyen panos rectangulares
analiticos a partir de las vigas reales:

  - por edificio y piso se agrupan las lineas de viga paralelas (eje) en
    "lineas de grilla" (clustering por proximidad, clust_tol). El valor de la
    linea es el promedio del cluster (las vigas reales suelen venir en pares
    +/-0.3 m alrededor del eje estructural).
  - las celdas entre lineas de grilla consecutivas son PANOS solo si sus 4
    bordes estan soportados por vigas reales (colineales dentro de beam_tol y
    con cobertura de union >= min_cover de la longitud del borde).
  - celdas con algun borde sin soporte, o con dimension menor a min_span, se
    EXCLUYEN (gap de cobertura documentado).

Esto garantiza que en el motor tributario cada borde de cada pano tenga al
menos una viga receptora -> conservacion exacta por construccion.

Si en el futuro el modelo entrega poligonos de losa reales, este modulo se
puede reemplazar sin tocar el resto del pipeline.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

from p1l3.rutas import COMBINED_VIEWER_JSON, BUILDING_SHORT, FLOORS

DIA = 1e-3


# ---------------------------------------------------------------------------
# Carga de modelo
# ---------------------------------------------------------------------------


def load_model(path=None):
    path = path or COMBINED_VIEWER_JSON
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _orient_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if dy < DIA:
        return "H"
    if dx < DIA:
        return "V"
    return None


def beam_lines(model) -> list[dict]:
    """Lista de vigas del modelo (solo linea en XY) con orientacion."""
    lines = []
    for s in model["solids"]:
        if s.get("category") != "beam":
            continue
        x1, y1, z1 = s["start"]
        x2, y2, z2 = s["end"]
        o = _orient_line(x1, y1, x2, y2)
        if o is None:
            continue
        lines.append(
            {
                "id": s.get("id"),
                "building": s.get("building"),
                "floor": s.get("floor"),
                "orient": o,
                "x1": x1, "y1": y1, "z1": z1,
                "x2": x2, "y2": y2, "z2": z2,
                "c": y1 if o == "H" else x1,
                "lo": min(x1, x2) if o == "H" else min(y1, y2),
                "hi": max(x1, x2) if o == "H" else max(y1, y2),
                "length": math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2),
            }
        )
    return lines


# ---------------------------------------------------------------------------
# Lineas de grilla (clustering de lineas de viga)
# ---------------------------------------------------------------------------


def cluster_lines(coords: list[float], clust_tol: float = 0.7) -> list[float]:
    """Agrupa coordenadas de lineas paralelas cercanas en una linea de grilla.

    Retorna la lista (ordenada) de los promedios de cada cluster.
    """
    if not coords:
        return []
    cs = sorted(coords)
    clusters = [[cs[0]]]
    for c in cs[1:]:
        if c - clusters[-1][-1] <= clust_tol:
            clusters[-1].append(c)
        else:
            clusters.append([c])
    return [sum(cl) / len(cl) for cl in clusters]


def grid_from_beams(lines, orient: str, clust_tol: float = 0.7) -> list[float]:
    """Lineas de grilla (ejes) para una orientacion a partir de lineas de viga."""
    coord_lines = defaultdict_lines(lines, orient)
    return cluster_lines(coord_lines, clust_tol)


def defaultdict_lines(lines, orient):
    return [ln["c"] for ln in lines if ln["orient"] == orient]


# ---------------------------------------------------------------------------
# Cobertura de bordes
# ---------------------------------------------------------------------------


def _union_cover(intervals: list[tuple[float, float]]) -> float:
    if not intervals:
        return 0.0
    ivs = sorted(intervals)
    lo, hi = ivs[0]
    total = 0.0
    for a, b in ivs[1:]:
        if a <= hi:
            hi = max(hi, b)
        else:
            total += hi - lo
            lo, hi = a, b
    total += hi - lo
    return total


def _overlap(a_lo, a_hi, b_lo, b_hi):
    return max(0.0, min(max(a_lo, a_hi), max(b_lo, b_hi)) - max(min(a_lo, a_hi), min(b_lo, b_hi)))


def edge_cover(lines, orient: str, c: float, a: float, b: float, tol: float = 0.35):
    """Cobertura (union de intervalos) de vigas colineales sobre un borde."""
    ivs = []
    lo, hi = min(a, b), max(a, b)
    for ln in lines:
        if ln["orient"] != orient:
            continue
        if abs(ln["c"] - c) > tol:
            continue
        s, e = max(ln["lo"], lo), min(ln["hi"], hi)
        if e > s:
            ivs.append((s, e))
    return _union_cover(ivs)


# ---------------------------------------------------------------------------
# Generacion de panos
# ---------------------------------------------------------------------------


@dataclass
class Pano:
    id: str
    building: str            # EDIFICIO_1 / EDIFICIO_2
    floor: str               # S1..P4
    xlo: float
    xhi: float
    ylo: float
    yhi: float
    vertices: list[tuple[float, float]] = field(default_factory=list)
    area_m2: float = 0.0
    edge_cover_frac: dict = field(default_factory=dict)


def _panel_id(building, floor, seq):
    return f"{BUILDING_SHORT[building]}-{floor}-P-{seq:03d}"


def build_panos(
    model,
    clust_tol=0.7,
    beam_tol=0.35,
    min_cover=0.9,
    min_span=0.8,
    beams_per_building_floor=None,
):
    """Genera panos validados por soporte de los 4 bordes. Ver docstring del modulo."""
    lines = beam_lines(model) if beams_per_building_floor is None else beams_per_building_floor
    by_key = {}
    for ln in lines:
        by_key.setdefault((ln["building"], ln["floor"]), []).append(ln)

    panos = []
    stats = {"cells": 0, "accepted": 0, "excluded_unsupported": 0, "excluded_span": 0}
    for bld in ("EDIFICIO_1", "EDIFICIO_2"):
        for fl in FLOORS:
            flines = by_key.get((bld, fl), [])
            gx = grid_from_beams(flines, "V", clust_tol)
            gy = grid_from_beams(flines, "H", clust_tol)
            for i in range(len(gx) - 1):
                for j in range(len(gy) - 1):
                    stats["cells"] += 1
                    xlo, xhi = gx[i], gx[i + 1]
                    ylo, yhi = gy[j], gy[j + 1]
                    if (xhi - xlo) < min_span or (yhi - ylo) < min_span:
                        stats["excluded_span"] += 1
                        continue
                    edges = {
                        "bottom": ("H", ylo, xlo, xhi),
                        "top": ("H", yhi, xlo, xhi),
                        "left": ("V", xlo, ylo, yhi),
                        "right": ("V", xhi, ylo, yhi),
                    }
                    covers = {}
                    ok = True
                    for name, (orient, c, a, b) in edges.items():
                        cov = edge_cover(flines, orient, c, a, b, tol=beam_tol)
                        frac = cov / (b - a) if (b - a) > 0 else 0.0
                        covers[name] = round(frac, 4)
                        if frac < min_cover - 1e-9:
                            ok = False
                    if not ok:
                        stats["excluded_unsupported"] += 1
                        continue
                    stats["accepted"] += 1
                    n = sum(1 for p in panos if p.building == bld and p.floor == fl) + 1
                    panos.append(
                        Pano(
                            id=_panel_id(bld, fl, n),
                            building=bld,
                            floor=fl,
                            xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi,
                            vertices=[(xlo, ylo), (xhi, ylo), (xhi, yhi), (xlo, yhi)],
                            area_m2=(xhi - xlo) * (yhi - ylo),
                            edge_cover_frac=covers,
                        )
                    )
    return panos, stats


# ---------------------------------------------------------------------------
# Asociacion viga <-> panos (slab_ids) con la misma logica del motor
# ---------------------------------------------------------------------------


def associate_beams_to_panos(model, panos, beam_tol=0.35):
    """Retorna {beam_id: [panel_ids]} usando colinealidad + solape.

    Misma regla que _find_beams_for_edge del motor tributario, para que el
    motor re-identifique exactamente los mismos bordes.
    """
    lines = beam_lines(model)
    assoc = {ln["id"]: [] for ln in lines}
    by_key = {}
    for ln in lines:
        by_key.setdefault((ln["building"], ln["floor"]), []).append(ln)

    for p in panos:
        edges = {
            "bottom": ("H", p.ylo, p.xlo, p.xhi),
            "top": ("H", p.yhi, p.xlo, p.xhi),
            "left": ("V", p.xlo, p.ylo, p.yhi),
            "right": ("V", p.xhi, p.ylo, p.yhi),
        }
        for orient, c, a, b in edges.values():
            for ln in by_key.get((p.building, p.floor), []):
                if ln["orient"] != orient:
                    continue
                if abs(ln["c"] - c) > beam_tol:
                    continue
                if _overlap(ln["lo"], ln["hi"], a, b) > 1e-6:
                    if p.id not in assoc[ln["id"]]:
                        assoc[ln["id"]].append(p.id)
    return assoc


# ---------------------------------------------------------------------------
# Metricas de cobertura
# ---------------------------------------------------------------------------


def coverage_report(model, panos):
    """Cobertura de panos vs bbox de diafragma y vs envolvente de grilla."""
    dia_areas = {}
    for d in model["diaphragms"]:
        pts = d["points"]
        xs = [pt[0] for pt in pts]
        ys = [pt[1] for pt in pts]
        key = (d["building"], d["floor"])
        dia_areas[key] = dia_areas.get(key, 0.0) + (max(xs) - min(xs)) * (max(ys) - min(ys))

    from collections import defaultdict
    pan_areas = defaultdict(float)

    for p in panos:
        pan_areas[(p.building, p.floor)] += p.area_m2

    rows = []
    for (bld, fl), adia in sorted(dia_areas.items()):
        apan = pan_areas.get((bld, fl), 0.0)
        rows.append(
            {
                "building": bld,
                "floor": fl,
                "diag_bbox_area_m2": round(adia, 2),
                "pano_area_m2": round(apan, 2),
                "coverage_frac_diag": round(apan / adia, 4) if adia > 0 else 0.0,
            }
        )
    return rows


def envelope_area(model, building, floor):
    """Area de la envolvente de la grilla de vigas (bbox de lineas de viga)."""
    lines = [ln for ln in beam_lines(model) if ln["building"] == building and ln["floor"] == floor]
    if not lines:
        return 0.0
    xs = [ln["x1"] for ln in lines] + [ln["x2"] for ln in lines]
    ys = [ln["y1"] for ln in lines] + [ln["y2"] for ln in lines]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))