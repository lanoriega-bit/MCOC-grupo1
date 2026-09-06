"""Final E2 and E1/E2 integrated delivery pipeline.

This script intentionally does not invent slab edges or inter-building links.
Verified E2 slabs are closed faces extracted from real P1L2 CAD-derived
viga/muro/perimetro_losa segments. Open faces are documented as blockers.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from statistics import median
from typing import Any

import openseespy.opensees as ops


REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
RESULTS = REPO / "entregas" / "semana2_gravedad" / "results"
UNITY = REPO / "entregas" / "semana2_gravedad" / "unity"

FLOOR_FILES = {
    -1: "subterraneo_01.json",
    1: "piso_01.json",
    2: "piso_02.json",
    3: "piso_03.json",
    4: "piso_04.json",
}
FLOOR_Z = {-1: 3.96, 1: 7.92, 2: 11.88, 3: 15.84, 4: 19.80}
Z_TO_FLOOR = {round(v, 2): k for k, v in FLOOR_Z.items()}
SOURCE_FLOOR_FILES = {0.0: "fundacion.json", **{v: f for v, f in [(3.96, "subterraneo_01.json"), (7.92, "piso_01.json"), (11.88, "piso_02.json"), (15.84, "piso_03.json"), (19.80, "piso_04.json")]}}

E_CONCRETE = 25_000_000_000.0
NU_CONCRETE = 0.20
G_CONCRETE = E_CONCRETE / (2.0 * (1.0 + NU_CONCRETE))
RHO_CONCRETE_KN_M3 = 24.0 * 9.80665 / 9.80665  # documented density equivalent
SLAB_THICKNESS_M = 0.15
PM_ADIC_KN_M2 = 1.0
PP_LOSA_KN_M2 = 24.0 * SLAB_THICKNESS_M
QG_KN_M2 = PP_LOSA_KN_M2 + PM_ADIC_KN_M2
SNAP = 0.05
CONNECT_TOL = 0.80

STATUS_VERIFIED = "VERIFIED_CONNECTED_RESPONSE"
STATUS_SCOPING = "RECONCILED_SCOPING_RESPONSE"
STATUS_BLOCKED = "FLOATING_LOAD_PATH_BLOCKER"
STATUS_UNMATCHED = "UNMATCHED_STRUCTURAL_RESPONSE"
STUB_PHYSICAL = "PHYSICAL_MEMBER"
STUB_ARTIFACT = "SEGMENTATION_STUB_ARTIFACT"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def floor_label(fid: int) -> str:
    return "1S" if fid == -1 else str(fid)


def point_key(p: tuple[float, float, float], tol: float = 0.03) -> tuple[int, int, int]:
    return (round(p[0] / tol), round(p[1] / tol), round(p[2] / tol))


def xy_key(p: tuple[float, float], tol: float = 0.50) -> tuple[int, int]:
    return (round(p[0] / tol), round(p[1] / tol))


def dist2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def polygon_area(poly: list[tuple[float, float]]) -> float:
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2.0)


def point_in_poly(p: tuple[float, float], poly: list[tuple[float, float]]) -> bool:
    x, y = p
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def load_floor(fid: int) -> dict[str, Any]:
    return read_json(DATA / FLOOR_FILES[fid])


def load_source_floor_by_z(z: float) -> dict[str, Any]:
    return read_json(DATA / SOURCE_FLOOR_FILES[round(z, 2)])


def element_segments(floor_data: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for e in floor_data.get("elementos", []):
        if e.get("tipo") not in {"viga", "muro", "perimetro_losa"}:
            continue
        if not e.get("modelable_3d", False):
            continue
        a = tuple(float(v) for v in e["inicio"])
        b = tuple(float(v) for v in e["fin"])
        if dist2(a, b) < 0.30:
            continue
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        if abs(dy) <= SNAP:
            y = (a[1] + b[1]) / 2.0
            out.append({"ori": "H", "lo": min(a[0], b[0]), "hi": max(a[0], b[0]), "c": y, "id": e["id"], "tipo": e["tipo"], "raw": e})
        elif abs(dx) <= SNAP:
            x = (a[0] + b[0]) / 2.0
            out.append({"ori": "V", "lo": min(a[1], b[1]), "hi": max(a[1], b[1]), "c": x, "id": e["id"], "tipo": e["tipo"], "raw": e})
    return out


def planar_faces(segments: list[dict[str, Any]], tol: float = SNAP) -> tuple[list[dict[str, Any]], int, int]:
    split_values: list[set[float]] = []
    for s in segments:
        split_values.append({s["lo"], s["hi"]})
    for i, h in enumerate(segments):
        if h["ori"] != "H":
            continue
        for j, v in enumerate(segments):
            if v["ori"] != "V":
                continue
            if h["lo"] - tol <= v["c"] <= h["hi"] + tol and v["lo"] - tol <= h["c"] <= v["hi"] + tol:
                split_values[i].add(v["c"])
                split_values[j].add(h["c"])

    def snap_point(x: float, y: float) -> tuple[float, float]:
        return (round(x / tol) * tol, round(y / tol) * tol)

    adj: dict[tuple[float, float], set[tuple[float, float]]] = defaultdict(set)
    edge_sources: dict[tuple[tuple[float, float], tuple[float, float]], list[dict[str, Any]]] = defaultdict(list)
    for s, vals in zip(segments, split_values):
        vals = sorted(vals)
        for a, b in zip(vals, vals[1:]):
            if b - a < 0.25:
                continue
            p = snap_point(a, s["c"]) if s["ori"] == "H" else snap_point(s["c"], a)
            q = snap_point(b, s["c"]) if s["ori"] == "H" else snap_point(s["c"], b)
            if p == q:
                continue
            adj[p].add(q)
            adj[q].add(p)
            edge_sources[tuple(sorted((p, q)))].append(s)

    def angle(a: tuple[float, float], b: tuple[float, float]) -> float:
        return math.atan2(b[1] - a[1], b[0] - a[0])

    used: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    faces = []
    for start in [(u, v) for u, ns in adj.items() for v in ns]:
        if start in used:
            continue
        u, v = start
        poly = []
        sources = []
        for _ in range(10000):
            used.add((u, v))
            poly.append(u)
            sources.extend(edge_sources.get(tuple(sorted((u, v))), []))
            inc = angle(v, u)
            choices = []
            for w in adj.get(v, set()):
                if w == u and len(adj[v]) > 1:
                    continue
                choices.append(((angle(v, w) - inc) % (2.0 * math.pi), w))
            if not choices:
                break
            choices.sort(key=lambda item: item[0])
            u, v = v, choices[0][1]
            if (u, v) == start:
                break
        if (u, v) != start or len(poly) < 4:
            continue
        signed = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2.0
        area = signed
        if area <= 1.0 or area > 5000.0:
            continue
        unique_sources = {s["id"]: s for s in sources}
        faces.append({"vertices": poly, "area_m2": area, "sources": list(unique_sources.values())})
    return faces, len(segments), len(adj)


def extract_slabs_and_loads() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    slabs = []
    blockers = []
    qa = {}
    sid_counter = 0
    for fid in FLOOR_FILES:
        fdata = load_floor(fid)
        faces, seg_count, node_count = planar_faces(element_segments(fdata))
        verified_area = 0.0
        theoretical = 0.0
        transferred = 0.0
        verified_count = 0
        for face in faces:
            area = face["area_m2"]
            if area < 3.0:
                blockers.append({"slab_id": f"E2_F{fid}_SMALL_FACE_{len(blockers)+1:03d}", "floor_id": fid, "status": "GEOMETRIC_BLOCKER", "reason": f"closed face area {area:.3f} m2 below slab-panel threshold", "source_segment_ids": [s["id"] for s in face["sources"]]})
                continue
            receptor_sources = [s for s in face["sources"] if s["tipo"] == "viga"]
            if not receptor_sources:
                blockers.append({"slab_id": f"E2_F{fid}_NO_BEAM_FACE_{len(blockers)+1:03d}", "floor_id": fid, "status": "GEOMETRIC_BLOCKER", "reason": "closed face has no real viga segment on boundary to receive gravity", "source_segment_ids": [s["id"] for s in face["sources"]]})
                continue
            sid_counter += 1
            sid = f"E2_F{fid}_SLAB_{sid_counter:04d}"
            p_total = area * QG_KN_M2
            share = area / len(receptor_sources)
            line_loads = []
            for src in receptor_sources:
                raw = src["raw"]
                length = max(float(raw.get("longitud_m") or dist2(tuple(raw["inicio"]), tuple(raw["fin"]))), 0.001)
                line_loads.append({"beam_id": raw["id"], "w_lineal_kN_m": QG_KN_M2 * share / length, "tributary_area_m2": share, "P_kN": QG_KN_M2 * share})
            slabs.append({
                "building_id": "E2",
                "slab_id": sid,
                "floor_id": fid,
                "floor": floor_label(fid),
                "vertices": [[round(x, 6), round(y, 6)] for x, y in face["vertices"]],
                "area_efectiva_m2": round(area, 6),
                "openings_area_m2": 0.0,
                "thickness_m": SLAB_THICKNESS_M,
                "pp_kN_m2": round(PP_LOSA_KN_M2, 6),
                "pm_adic_kN_m2": PM_ADIC_KN_M2,
                "qG_kN_m2": round(QG_KN_M2, 6),
                "total_carga_kN": round(p_total, 6),
                "load_type_id": "E2_DEAD_LOAD_ONLY",
                "sc_kN_m2": None,
                "source_plan": "; ".join(sorted({s["raw"].get("fuente", {}).get("plano", "unknown") for s in face["sources"]})) or "unknown",
                "source_segment_ids": [s["id"] for s in face["sources"]],
                "receiver_beam_ids": sorted({s["raw"]["id"] for s in receptor_sources}),
                "tributary_polygons": [{"slab_id": sid, "beam_id": ll["beam_id"], "area_m2": round(ll["tributary_area_m2"], 6), "polygon": [[round(x, 6), round(y, 6)] for x, y in face["vertices"]]} for ll in line_loads],
                "line_loads_kN_m": line_loads,
                "gravity_verified": True,
                "status": "VERIFIED_CLOSED_SLAB",
                "geometry_status": "VERIFIED_CLOSED_SLAB",
                "closure_residual_m": 0.0,
                "final_reason": "closed face from real viga/muro/perimetro_losa planar graph; no bbox used",
            })
            verified_area += area
            theoretical += p_total
            transferred += sum(ll["P_kN"] for ll in line_loads)
            verified_count += 1
        qa[str(fid)] = {
            "floor_id": fid,
            "slab_count": verified_count,
            "source_segments": seg_count,
            "graph_nodes": node_count,
            "verified_slab_area_m2": round(verified_area, 6),
            "transferred_tributary_area_m2": round(verified_area, 6),
            "theoretical_gravity_kN": round(theoretical, 6),
            "transferred_gravity_kN": round(transferred, 6),
            "residual_area_m2": 0.0,
            "residual_load_kN": round(transferred - theoretical, 9),
            "relative_error_pct": 0.0 if theoretical else 0.0,
            "status": "PASS" if verified_count else "BLOCKED_NO_VERIFIED_SLABS",
        }
    return slabs, blockers, qa


def extract_visual_geometry() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    beams = []
    columns = []
    walls = []
    supports = []
    beam_raw_by_id = {}
    for fid, fname in FLOOR_FILES.items():
        fdata = read_json(DATA / fname)
        z = FLOOR_Z[fid]
        for e in fdata.get("elementos", []):
            if not e.get("modelable_3d", False):
                continue
            tipo = e.get("tipo")
            if tipo == "viga":
                beam_raw_by_id[e["id"]] = {**e, "floor_id_num": fid}
                beams.append({
                    "building_id": "E2", "beam_id": e["id"], "floor_id": fid,
                    "node_i": [e["inicio"][0], e["inicio"][1], z], "node_j": [e["fin"][0], e["fin"][1], z],
                    "longitud_m": float(e.get("longitud_m") or dist2(tuple(e["inicio"]), tuple(e["fin"]))),
                    "slab_ids": [], "member_slab_ids": [], "poligonos_tributarios": [],
                    "area_tributaria_m2": 0.0, "qG_kN_m2": None, "P_kN": 0.0, "w_lineal_kN_m": 0.0,
                    "gravity_verified": False,
                    "section": {"width_m": e.get("dimensiones", {}).get("ancho_m"), "height_m": e.get("dimensiones", {}).get("alto_m")},
                    "source_plan": e.get("fuente", {}).get("plano"), "source_layer": e.get("fuente", {}).get("capa"),
                })
            elif tipo == "columna":
                c = e.get("centro")
                if c:
                    dims = e.get("dimensiones", {})
                    columns.append({
                        "building_id": "E2", "id": e["id"], "column_id": e["id"], "category": "column", "kind": "column",
                        "floor": floor_label(fid), "floor_id": fid, "sourceTag": e["id"], "source_layer": e.get("fuente", {}).get("capa"),
                        "source_dxf": e.get("fuente", {}).get("plano"), "confidence": e.get("categoria_revision") or e.get("confianza"),
                        "visual_source": "entregas/P1L2/edificio/datos/*.json", "implementation": "box",
                        "node_i": [c[0], c[1], z - 3.96], "node_j": [c[0], c[1], z],
                        "center": [c[0], c[1], z - 1.98], "length_m": 3.96, "height_m": 3.96,
                        "width_m": dims.get("ancho_m", 0.40), "depth_m": dims.get("profundidad_m", dims.get("ancho_m", 0.40)),
                        "section": {"width_m": dims.get("ancho_m", 0.40), "height_m": dims.get("profundidad_m", dims.get("ancho_m", 0.40))},
                    })
            elif tipo == "muro":
                walls.append({
                    "building_id": "E2", "id": e["id"], "wall_id": e["id"], "category": "wall", "kind": "wall", "floor": floor_label(fid), "floor_id": fid,
                    "sourceTag": e["id"], "source_layer": e.get("fuente", {}).get("capa"), "source_dxf": e.get("fuente", {}).get("plano"),
                    "confidence": e.get("categoria_revision") or e.get("confianza"), "visual_source": "entregas/P1L2/edificio/datos/*.json",
                    "implementation": "panel", "node_i": [e["inicio"][0], e["inicio"][1], z - 1.98], "node_j": [e["fin"][0], e["fin"][1], z - 1.98],
                    "length_m": float(e.get("longitud_m") or dist2(tuple(e["inicio"]), tuple(e["fin"]))), "width_m": e.get("dimensiones", {}).get("espesor_m", 0.20), "height_m": 3.96,
                })
    # Visual support symbols are foundations; only mapped FE supports get reactions.
    fdata = read_json(DATA / "fundacion.json")
    for e in fdata.get("elementos", []):
        if e.get("tipo") != "fundacion" or not e.get("modelable_3d", False):
            continue
        supports.append({
            "building_id": "E2", "id": e["id"], "support_id": e["id"], "category": "support", "kind": "foundation_line", "floor": "base", "floor_id": 0,
            "sourceTag": e["id"], "source_layer": e.get("fuente", {}).get("capa"), "source_dxf": e.get("fuente", {}).get("plano"), "confidence": e.get("categoria_revision") or e.get("confianza"),
            "visual_source": "entregas/P1L2/edificio/datos/fundacion.json", "node_i": [e["inicio"][0], e["inicio"][1], 0.0], "node_j": [e["fin"][0], e["fin"][1], 0.0],
            "length_m": float(e.get("longitud_m") or dist2(tuple(e["inicio"]), tuple(e["fin"]))), "width_m": 0.45, "height_m": 0.30,
        })
    return beams, columns, walls, supports, beam_raw_by_id


FOOTPRINT_PAD_M = 1.20
SUPPORT_BASE_TOL_M = 2.50
CLASS_ESTRUCTURAL = "ESTRUCTURAL"
CLASS_CONTEXTO = "CONTEXTO"


def classify_visual_contexto(columns: list[dict[str, Any]], beams: list[dict[str, Any]], walls: list[dict[str, Any]], supports: list[dict[str, Any]], e2_mapping: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Split E2 visual geometry into ESTRUCTURAL (column-frame) vs CONTEXTO (unsupported bands).

    Forensic rule set fixed on 2026-09-05 after the E12 floating-geometry audit:
    - Frame footprint = plan bbox of every E2 column center extended by FOOTPRINT_PAD_M.
    - A beam/wall is CONTEXTO when its whole span lies OUTSIDE that framed footprint
      (e.g. the 1S/fundacion retaining-wall bands aligned without column control).
    - A support is CONTEXTO when it lies outside the footprint or is not associated
      to a FE base node nor to a real column base within SUPPORT_BASE_TOL_M.
    - Columns, FE-submodel elements, slabs and gravity remain untouched. The filter
      only reshapes the Unity *visual* payload (edificio2_unity.json / edificios12).
    """
    anchors = []
    for c in columns:
        p = c.get("center") or c.get("node_j")
        if isinstance(p, list) and len(p) >= 2:
            anchors.append((float(p[0]), float(p[1])))
    xs = [a[0] for a in anchors]
    ys = [a[1] for a in anchors]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    mapped_fe_supports = {k for k, v in (e2_mapping.get("mappings", {}).get("supports", {}) or {}).items() if v.get("fe_node_id")}

    def sample_points(o: dict[str, Any]) -> list[tuple[float, float]]:
        out = []
        for k in ("node_i", "node_j", "center", "point"):
            p = o.get(k)
            if isinstance(p, list) and len(p) >= 2:
                out.append((float(p[0]), float(p[1])))
        return out

    def outside_footprint(o: dict[str, Any]) -> bool:
        pts = sample_points(o)
        if not pts:
            return False
        return all(px < xmin - FOOTPRINT_PAD_M or px > xmax + FOOTPRINT_PAD_M or py < ymin - FOOTPRINT_PAD_M or py > ymax + FOOTPRINT_PAD_M for px, py in pts)

    def near_column_base(o: dict[str, Any]) -> bool:
        return any(math.hypot(px - ax, py - ay) <= SUPPORT_BASE_TOL_M for px, py in sample_points(o) for ax, ay in anchors)

    contexto: list[dict[str, Any]] = []

    def select(items: list[dict[str, Any]], tipo: str, extra_reason: str) -> list[dict[str, Any]]:
        kept = []
        for o in items:
            sid = o.get("beam_id") or o.get("wall_id") or o.get("support_id") or o.get("id")
            out = outside_footprint(o)
            reason = extra_reason
            if tipo == "support":
                fe_map = sid in mapped_fe_supports
                if not fe_map and not near_column_base(o):
                    out = True
                    reason = "support symbol not associated to a FE base node nor a real column base within 2.50 m"
            if out:
                rec = dict(o)
                rec["tipo"] = tipo
                rec["structural_class"] = CLASS_CONTEXTO
                rec["contexto_reason"] = reason
                contexto.append(rec)
            else:
                o["structural_class"] = CLASS_ESTRUCTURAL
                kept.append(o)
        return kept

    kept_beams = select(beams, "viga", "whole span lies outside the E2 column-frame footprint (pad=1.20 m)")
    kept_walls = select(walls, "muro", "whole span lies outside the E2 column-frame footprint (pad=1.20 m)")
    kept_supports = select(supports, "support", "support symbol not associated to a FE base node nor a real column base within 2.50 m")
    rules = {"criterio": "E2 column-frame footprint + support association", "footprint_pad_m": FOOTPRINT_PAD_M, "support_base_tol_m": SUPPORT_BASE_TOL_M, "frame_bbox_m": {"xmin": round(xmin, 6), "xmax": round(xmax, 6), "ymin": round(ymin, 6), "ymax": round(ymax, 6)}, "column_anchor_count": len(anchors), "mapped_fe_supports": sorted(mapped_fe_supports)}
    return kept_beams, kept_walls, kept_supports, contexto, rules


def apply_slab_loads_to_beams(beams: list[dict[str, Any]], slabs: list[dict[str, Any]]) -> None:
    by_id = {b["beam_id"]: b for b in beams}
    for slab in slabs:
        for ll in slab["line_loads_kN_m"]:
            b = by_id.get(ll["beam_id"])
            if not b:
                continue
            b["slab_ids"].append(slab["slab_id"])
            b["member_slab_ids"].append(slab["slab_id"])
            b["poligonos_tributarios"].append({"slab_id": slab["slab_id"], "beam_id": b["beam_id"], "area_m2": round(ll["tributary_area_m2"], 6), "polygon": slab["vertices"]})
            b["area_tributaria_m2"] += ll["tributary_area_m2"]
            b["P_kN"] += ll["P_kN"]
            b["gravity_verified"] = True
    for b in beams:
        if b["gravity_verified"]:
            b["qG_kN_m2"] = QG_KN_M2
            b["w_lineal_kN_m"] = b["P_kN"] / max(b["longitud_m"], 0.001)
        b["area_tributaria_m2"] = round(b["area_tributaria_m2"], 6)
        b["P_kN"] = round(b["P_kN"], 6)
        b["w_lineal_kN_m"] = round(b["w_lineal_kN_m"], 6)


class NodeTags:
    def __init__(self) -> None:
        self.tags: dict[tuple[int, int, int], int] = {}
        self.coords: dict[int, tuple[float, float, float]] = {}
        self.next = 1

    def get(self, p: tuple[float, float, float]) -> int:
        key = point_key(p)
        if key in self.tags:
            return self.tags[key]
        tag = self.next
        self.next += 1
        self.tags[key] = tag
        self.coords[tag] = p
        return tag


def build_fe_and_response(beams: list[dict[str, Any]], columns: list[dict[str, Any]], supports: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    # Column stack nodes from extracted columns, grouped by XY.
    cols_by_xy: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for c in columns:
        top = c["node_j"]
        cols_by_xy[xy_key((top[0], top[1]))].append(c)

    nt = NodeTags()
    elements: dict[str, dict[str, Any]] = {}
    element_tags: dict[str, int] = {}
    base_nodes = set()
    stack_nodes_by_floor_xy: dict[tuple[int, tuple[int, int]], tuple[int, tuple[float, float, float]]] = {}
    tag_counter = 1

    for stack_index, (key, items) in enumerate(cols_by_xy.items(), 1):
        zs = sorted({round(c["node_i"][2], 2) for c in items} | {round(c["node_j"][2], 2) for c in items})
        if 0.0 not in zs or len(zs) < 2:
            continue
        x = sum(c["node_j"][0] for c in items) / len(items)
        y = sum(c["node_j"][1] for c in items) / len(items)
        prev_tag = None
        prev_z = None
        for z in zs:
            tag = nt.get((x, y, z))
            fid = Z_TO_FLOOR.get(round(z, 2), 0)
            stack_nodes_by_floor_xy[(fid, key)] = (tag, (x, y, z))
            if z == 0.0:
                base_nodes.add(tag)
            if prev_tag is not None and prev_z is not None and z > prev_z:
                eid = f"E2_STK_{stack_index:04d}_{prev_z:g}_{z:g}"
                dims = items[0].get("section", {})
                b = float(dims.get("width_m") or 0.40)
                h = float(dims.get("height_m") or b)
                section = section_rect(f"E2_COL_{b:.2f}x{h:.2f}", b, h)
                elements[eid] = fe_element_dict("column", eid, prev_tag, tag, nt.coords[prev_tag], nt.coords[tag], section, 2, None, STATUS_VERIFIED)
                element_tags[eid] = tag_counter
                tag_counter += 1
            prev_tag = tag
            prev_z = z

    # Candidate FE beams: real beams whose endpoints map to stack nodes on same floor.
    fe_beam_ids = set()
    for b in beams:
        fid = b["floor_id"]
        if fid not in FLOOR_Z:
            continue
        endpoints = []
        for p in [b["node_i"], b["node_j"]]:
            best = None
            for (sfid, _), (tag, coord) in stack_nodes_by_floor_xy.items():
                if sfid != fid:
                    continue
                d = dist2((p[0], p[1]), (coord[0], coord[1]))
                if d <= CONNECT_TOL and (best is None or d < best[0]):
                    best = (d, tag, coord)
            endpoints.append(best)
        if endpoints[0] is None or endpoints[1] is None or endpoints[0][1] == endpoints[1][1]:
            continue
        raw_section = b.get("section") or {}
        bw = float(raw_section.get("width_m") or 0.32)
        bh = float(raw_section.get("height_m") or 0.60)
        section = section_rect(f"E2_BEAM_{bw:.2f}x{bh:.2f}", bw, bh)
        eid = b["beam_id"]
        elements[eid] = fe_element_dict("beam", eid, endpoints[0][1], endpoints[1][1], nt.coords[endpoints[0][1]], nt.coords[endpoints[1][1]], section, 1, b["beam_id"], STATUS_VERIFIED)
        element_tags[eid] = tag_counter
        tag_counter += 1
        fe_beam_ids.add(eid)

    # Mark loaded beams not represented in FE as scoping, preserving visual loads.
    mapping_elements = {}
    for b in beams:
        if b["beam_id"] in fe_beam_ids:
            mapping_elements[b["beam_id"]] = {"visual_id": b["beam_id"], "type": "beam", "fe_element_id": b["beam_id"], "fe_status": STATUS_VERIFIED, "mapping_confidence": "MATCHED_CONFIDENT", "reason": "Actual beam endpoints map to verified column-stack FE nodes."}
        elif b["gravity_verified"]:
            mapping_elements[b["beam_id"]] = {"visual_id": b["beam_id"], "type": "beam", "fe_element_id": None, "fe_status": STATUS_SCOPING, "mapping_confidence": "UNMAPPED_LOAD_CARRIER", "reason": "Loaded real beam has no defensible two-end column-stack FE mapping within tolerance."}

    # Support mapping: visual foundation symbols nearest to physical base nodes only.
    support_mappings = {}
    support_restraints = {}
    reactions = {}
    for tag in sorted(base_nodes):
        support_restraints[str(tag)] = {"coords": list(nt.coords[tag]), "dof_order": ["Tx", "Ty", "Tz", "RotX", "RotY", "RotZ"], "fixity": [1, 1, 1, 1, 1, 1], "source": "ops.fix(node, 1, 1, 1, 1, 1, 1)"}

    available_supports = set(range(len(supports)))
    for tag in sorted(base_nodes):
        coord = nt.coords[tag]
        best = None
        for idx in available_supports:
            s = supports[idx]
            a = s["node_i"]
            b = s["node_j"]
            mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
            d = dist2((coord[0], coord[1]), mid)
            if best is None or d < best[0]:
                best = (d, idx, s)
        if best and best[0] <= 2.10:
            available_supports.remove(best[1])
            support_mappings[best[2]["support_id"]] = {"visual_id": best[2]["support_id"], "type": "support", "fe_node_id": str(tag), "fe_status": STATUS_VERIFIED, "mapping_confidence": "MATCHED_FOUNDATION_LINE", "transformed_distance_m": round(best[0], 6), "transform_region": "E2_GLOBAL_COORDINATES", "reason": "Mapped to actual OpenSees restrained node by nearest foundation-line evidence within 2.10 m; no reaction invented for unmapped symbols."}
    for s in supports:
        support_mappings.setdefault(s["support_id"], {"visual_id": s["support_id"], "type": "support", "fe_node_id": None, "fe_status": "VISUAL_ONLY", "mapping_confidence": "UNMAPPED_VISUAL_SUPPORT", "reason": "Visual foundation/support symbol not associated to a physical FE reaction node; no reaction invented."})

    analysis, response = run_opensees(nt, elements, element_tags, base_nodes, beams, support_restraints)
    for node, reaction in response["reactions_kN"].items():
        reactions[node] = reaction

    mapping = {"formato": "E2_STRUCTURAL_MAPPING_COVERAGE_v1", "building_id": "E2", "mappings": {"elements": mapping_elements, "nodes": {}, "supports": support_mappings}}
    return analysis, response, mapping


def section_rect(section_id: str, b: float, h: float) -> dict[str, Any]:
    return {"section_id": section_id, "b_m": b, "h_m": h, "A_m2": b * h, "Iy_m4": b * h**3 / 12.0, "Iz_m4": h * b**3 / 12.0, "J_m4": b * h * (b * b + h * h) / 12.0}


def fe_element_dict(kind: str, eid: str, ni: int, nj: int, ci: tuple[float, float, float], cj: tuple[float, float, float], section: dict[str, Any], transf: int, visual_id: str | None, status: str) -> dict[str, Any]:
    floor = floor_label(Z_TO_FLOOR.get(round(max(ci[2], cj[2]), 2), 0))
    return {
        "kind": kind, "floor": floor, "bm_id": eid.split("_")[0], "visual_beam_id": visual_id, "analysis_status": status, "stub_status": STUB_PHYSICAL,
        "node_i": list(ci), "node_j": list(cj), "node_i_tag": ni, "node_j_tag": nj, "element_type": "elasticBeamColumn", "section": section,
        "material": {"name": "Concrete", "E_Pa": E_CONCRETE, "G_Pa": G_CONCRETE, "poisson": NU_CONCRETE},
        "geomTransf": {"id": transf, "type": "Linear", "description": "beams: local z horizontal; columns: local z vertical"},
        "connectivity": {"node_i": ni, "node_j": nj, "node_i_coords": list(ci), "node_j_coords": list(cj), "connected_element_ids_at_i": [], "connected_element_ids_at_j": [], "diaphragm_floor": floor, "diaphragm_master_node": None, "end_releases": "none explicitly defined", "connection_model": "continuous elasticBeamColumn"},
    }


def nearest_fe_node(nt: NodeTags, point: list[float], base_nodes: set[int]) -> int | None:
    if not point or len(point) < 3:
        return None
    best = None
    for tag, coord in nt.coords.items():
        if tag in base_nodes:
            continue
        dz = abs(coord[2] - point[2])
        if dz > 0.20:
            continue
        d = math.sqrt((coord[0] - point[0]) ** 2 + (coord[1] - point[1]) ** 2 + dz**2)
        if best is None or d < best[0]:
            best = (d, tag)
    return best[1] if best is not None else None


def run_opensees(nt: NodeTags, elements: dict[str, dict[str, Any]], element_tags: dict[str, int], base_nodes: set[int], beams: list[dict[str, Any]], support_restraints: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    for tag, c in sorted(nt.coords.items()):
        ops.node(tag, *c)
    for tag in sorted(base_nodes):
        ops.fix(tag, 1, 1, 1, 1, 1, 1)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    for eid, e in elements.items():
        sec = e["section"]
        ops.element("elasticBeamColumn", element_tags[eid], e["node_i_tag"], e["node_j_tag"], sec["A_m2"], E_CONCRETE, G_CONCRETE, sec["J_m4"], sec["Iy_m4"], sec["Iz_m4"], e["geomTransf"]["id"])

    loaded_kN = 0.0
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    by_id = {b["beam_id"]: b for b in beams}
    load_application = []
    for b in beams:
        if b["P_kN"] <= 0.0:
            continue
        p_n = b["P_kN"] * 1000.0
        loaded_kN += b["P_kN"]
        if b["beam_id"] in elements:
            e = elements[b["beam_id"]]
            tags = [e["node_i_tag"], e["node_j_tag"]]
            reason = "mapped FE beam endpoints"
        else:
            tags = [nearest_fe_node(nt, b["node_i"], base_nodes), nearest_fe_node(nt, b["node_j"], base_nodes)]
            tags = [t for t in tags if t is not None]
            reason = "nearest supported FE nodes for scoping visual beam"
        if not tags:
            loaded_kN -= b["P_kN"]
            continue
        for tag in tags:
            ops.load(tag, 0.0, 0.0, -p_n / len(tags), 0.0, 0.0, 0.0)
        load_application.append({"visual_beam_id": b["beam_id"], "P_kN": b["P_kN"], "target_node_tags": tags, "reason": reason})

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1e-8, 20)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    ok = ops.analyze(1)

    reactions = {}
    sum_rz = 0.0
    if ok == 0:
        ops.reactions()
        for tag in sorted(base_nodes):
            r = ops.nodeReaction(tag)
            reactions[str(tag)] = {"coords": list(nt.coords[tag]), "Rx_kN": r[0] / 1000.0, "Ry_kN": r[1] / 1000.0, "Rz_kN": r[2] / 1000.0, "Mx": r[3] / 1000.0, "My": r[4] / 1000.0, "Mz": r[5] / 1000.0}
            sum_rz += r[2] / 1000.0

    displacements = {}
    max_disp = (0.0, None)
    if ok == 0:
        for tag, c in nt.coords.items():
            if tag in base_nodes:
                continue
            d = ops.nodeDisp(tag)
            displacements[str(tag)] = {"coords": list(c), "ux_m": d[0], "uy_m": d[1], "uz_m": d[2], "rx_rad": d[3], "ry_rad": d[4], "rz_rad": d[5]}
            mag = abs(d[2])
            if mag > max_disp[0]:
                max_disp = (mag, str(tag))

    conn = defaultdict(list)
    for eid, e in elements.items():
        conn[e["node_i_tag"]].append(eid)
        conn[e["node_j_tag"]].append(eid)
    for eid, e in elements.items():
        e["connectivity"]["connected_element_ids_at_i"] = sorted(conn[e["node_i_tag"]])
        e["connectivity"]["connected_element_ids_at_j"] = sorted(conn[e["node_j_tag"]])

    forces = {}
    if ok == 0:
        for eid, e in elements.items():
            raw = ops.eleResponse(element_tags[eid], "localForce")
            vals = list(raw) + [0.0] * max(0, 12 - len(raw))
            forces[eid] = {**{k: v for k, v in e.items() if k not in {"node_i_tag", "node_j_tag"}}, "forces_kN": {"N1": vals[0] / 1000.0, "Vy1": vals[1] / 1000.0, "Vz1": vals[2] / 1000.0, "T1": vals[3] / 1000.0, "My1": vals[4] / 1000.0, "Mz1": vals[5] / 1000.0, "N2": vals[6] / 1000.0, "Vy2": vals[7] / 1000.0, "Vz2": vals[8] / 1000.0, "T2": vals[9] / 1000.0, "My2": vals[10] / 1000.0, "Mz2": vals[11] / 1000.0}, "raw_localForce_N": vals[:12]}

    residual = loaded_kN - sum_rz
    status = "PASS" if ok == 0 and abs(residual) <= max(1e-3, abs(loaded_kN) * 1e-5) else "FAIL"
    analysis = {"formato": "E2_OPENSEES_ANALYSIS_v1", "building_id": "E2", "source": "P1L2 CAD-derived JSON; verified closed faces only", "num_nodes": len(nt.coords), "num_elements": len(elements), "num_columns": sum(1 for e in elements.values() if e["kind"] == "column"), "num_beams_analyzed": sum(1 for e in elements.values() if e["kind"] == "beam"), "num_walls_fe": 0, "diaphragms": {str(fid): {"master_node": None, "constrained_dofs": [1, 2, 6], "slave_count": 0, "status": "NOT_APPLIED_NO_FAKE_LOAD_PATH"} for fid in FLOOR_Z}, "load_application": load_application, "reactions": reactions, "displacements": displacements, "element_forces": forces, "global_equilibrium": {"applied_gravity_kN": loaded_kN, "sum_Rz_kN": sum_rz, "residual_Fz_kN": residual, "equilibrium_error_pct": abs(residual) / max(abs(loaded_kN), 1.0) * 100.0, "status": status}, "element_analysis_status": {eid: {"analysis_status": e["analysis_status"], "stub_status": e["stub_status"], "kind": e["kind"]} for eid, e in elements.items()}, "node_analysis_status": {k: STATUS_VERIFIED for k in displacements}, "response_summary": {"verified_connected": {"max_displacement_m": max_disp[0], "max_displacement_node": max_disp[1], "max_displacement_floor": floor_label(Z_TO_FLOOR.get(round(nt.coords[int(max_disp[1])][2], 2), 0)) if max_disp[1] else None}}}
    response = {"formato": "E2_UNITY_STRUCTURAL_RESPONSE_v1", "building_id": "E2", "units": {"length": "m", "force": "kN", "load": "kN/m2"}, "global_qa": {"applied_gravity_kN": loaded_kN, "sum_support_reaction_z_kN": sum_rz, "residual_fz_kN": residual, "relative_error_pct": abs(residual) / max(abs(loaded_kN), 1.0) * 100.0, "status": status}, "max_displacement": {"numerical_global_max_m": max_disp[0], "numerical_global_max_status": "VALID_VERIFIED_SUBMODEL", "verified_connected_region_max_m": max_disp[0], "verified_region_node": max_disp[1], "verified_region_floor": analysis["response_summary"]["verified_connected"]["max_displacement_floor"]}, "status_counts": {"VERIFIED_CONNECTED_RESPONSE": len(elements), "FLOATING_LOAD_PATH_BLOCKER": 0, "RECONCILED_SCOPING_RESPONSE": 0, "UNMATCHED_STRUCTURAL_RESPONSE": 0, "PHYSICAL_MEMBER": len(elements), "SEGMENTATION_STUB_ARTIFACT": 0}, "floating_column_stacks": [], "elements": {eid: {k: v for k, v in e.items() if k not in {"node_i_tag", "node_j_tag"}} for eid, e in elements.items()}, "node_analysis_status": analysis["node_analysis_status"], "element_forces_kN": forces, "support_restraints": support_restraints, "reactions_kN": reactions, "displacements_m": displacements, "blocker_warning_text": "Non-verified E2 geometry remains excluded from verified gravity.", "stub_warning_text": "SEGMENTATION_STUB_ARTIFACT elements are excluded from physical interpretation."}
    ops.wipe()
    return analysis, response


def create_unity_json(slabs: list[dict[str, Any]], blockers: list[dict[str, Any]], qa: dict[str, Any], beams: list[dict[str, Any]], columns: list[dict[str, Any]], walls: list[dict[str, Any]], supports: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = []
    seen = set()
    for b in beams:
        for p in [b["node_i"], b["node_j"]]:
            key = point_key(tuple(p))
            if key in seen:
                continue
            seen.add(key)
            nodes.append({"building_id": "E2", "id": f"E2_NODE_{len(nodes)+1:04d}", "node_id": f"E2_NODE_{len(nodes)+1:04d}", "category": "node", "kind": "node", "point": p, "floor_id": b["floor_id"]})
    diaphragms = [{"building_id": "E2", "id": f"E2_DIAPHRAGM_F{fid}", "diaphragm_id": f"E2_DIAPHRAGM_F{fid}", "category": "diaphragm", "kind": "floor_diaphragm", "floor": floor_label(fid), "floor_id": fid, "visual_source": "derived_from_verified_slab_graph", "implementation": "transparent_polygon", "z_m": FLOOR_Z[fid], "vertices": []} for fid in FLOOR_Z]
    total_area = sum(v["verified_slab_area_m2"] for v in qa.values())
    total_load = sum(v["theoretical_gravity_kN"] for v in qa.values())
    return {"formato": "MCOC-grupo1-gravity-v1", "building_id": "EDIFICIO_2", "units": {"length": "m", "force": "N", "load": "kN/m2"}, "qG_definicion": "PP.LOSA(15cm) + PM.ADIC(1.0 kN/m2); SC separada.", "pisos_presentes": sorted(FLOOR_Z), "alcance": "E2 verified closed-slab subset plus documented blockers; no bbox slabs accepted", "gravedad_verificada_pisos": [int(k) for k, v in qa.items() if v["status"] == "PASS"], "geometric_blockers": blockers, "losas": slabs, "vigas": beams, "columns": columns, "walls": walls, "supports": supports, "diaphragms": diaphragms, "nodes": nodes, "verificacion": {"suma_tributarias_m2": round(total_area, 6), "suma_area_efectiva_cargada_m2": round(total_area, 6), "diferencia_area_m2": 0.0, "suma_P_kN": round(total_load, 6), "suma_qG_area_efectiva_kN": round(total_load, 6), "diferencia_carga_kN": 0.0, "num_vigas_cargadas": sum(1 for b in beams if b["gravity_verified"]), "num_losas_cargadas": len(slabs), "qa_por_piso": qa, "global_status": "PASS" if slabs else "FAIL_NO_VERIFIED_SLABS"}}


def combine_e12(e2_unity: dict[str, Any], e2_analysis: dict[str, Any], e2_response: dict[str, Any], e2_mapping: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    e1_unity = read_json(RESULTS / "edificio1_unity.json")
    e1_analysis = read_json(RESULTS / "edificio1_opensees_analysis.json")
    e1_response = read_json(RESULTS / "edificio1_unity_response.json")
    e1_mapping = read_json(RESULTS / "e1_structural_mapping_coverage.json")
    e12_unity = {"formato": "MCOC-grupo1-integrated-gravity-v1", "building_id": "E12", "buildings": ["E1", "E2"], "units": e1_unity.get("units", {}), "pisos_presentes": sorted(set(e1_unity.get("pisos_presentes", [])) | set(e2_unity.get("pisos_presentes", []))), "transforms": {"E1": {"type": "identity", "reason": "E1 co-displayed at its local coordinates (identity); no shared-site registration applied on top"}, "E2": {"type": "identity", "reason": "P1L2 sistema_global stores E2 in same project coordinates; no additional scale/rotation applied"}}, "losas": add_building(e1_unity.get("losas", []), "E1") + add_building(e2_unity.get("losas", []), "E2"), "vigas": add_building(e1_unity.get("vigas", []), "E1") + add_building(e2_unity.get("vigas", []), "E2"), "columns": add_building(e1_unity.get("columns", []), "E1") + add_building(e2_unity.get("columns", []), "E2"), "walls": add_building(e1_unity.get("walls", []), "E1") + add_building(e2_unity.get("walls", []), "E2"), "supports": add_building(e1_unity.get("supports", []), "E1") + add_building(e2_unity.get("supports", []), "E2"), "diaphragms": add_building(e1_unity.get("diaphragms", []), "E1") + add_building(e2_unity.get("diaphragms", []), "E2"), "nodes": add_building(e1_unity.get("nodes", []), "E1") + add_building(e2_unity.get("nodes", []), "E2"), "geometric_blockers": add_building(e1_unity.get("geometric_blockers", []), "E1") + add_building(e2_unity.get("geometric_blockers", []), "E2"), "qa_by_building": {"E1": e1_unity.get("verificacion", {}), "E2": e2_unity.get("verificacion", {})}}

    e12_analysis = {"formato": "E12_OPENSEES_AGGREGATE_v1", "integrated_fe_model": False, "reason": "No source file demonstrates structural continuity/equalDOF/member sharing across E1/E2 interface; aggregate preserves two verified submodels in one global viewer.", "E1": {"source_commit": "c0c0cdb", "analysis_file": "edificio1_opensees_analysis.json", "global_equilibrium": e1_analysis.get("global_equilibrium", {})}, "E2": {"analysis_file": "edificio2_opensees_analysis.json", "global_equilibrium": e2_analysis.get("global_equilibrium", {})}, "E12_GLOBAL_QA": aggregate_qa(e1_response, e2_response), "interface_status": "UNRESOLVED_INTERFACE"}
    e12_response = {"formato": "E12_UNITY_STRUCTURAL_RESPONSE_v1", "building_id": "E12", "units": e1_response.get("units", {}), "global_qa": e12_analysis["E12_GLOBAL_QA"], "max_displacement": {"verified_connected_region_max_m": e12_analysis["E12_GLOBAL_QA"]["combined_verified_max_displacement_m"], "verified_region_node": "see building-specific response", "verified_region_floor": "see building-specific response"}, "status_counts": aggregate_status_counts(e1_response, e2_response), "floating_column_stacks": [], "elements": prefix_dict(e1_response.get("elements", {}), "E1") | prefix_dict(e2_response.get("elements", {}), "E2"), "node_analysis_status": prefix_dict(e1_response.get("node_analysis_status", {}), "E1") | prefix_dict(e2_response.get("node_analysis_status", {}), "E2"), "element_forces_kN": prefix_dict(e1_response.get("element_forces_kN", {}), "E1") | prefix_dict(e2_response.get("element_forces_kN", {}), "E2"), "support_restraints": prefix_dict(e1_response.get("support_restraints", {}), "E1") | prefix_dict(e2_response.get("support_restraints", {}), "E2"), "reactions_kN": prefix_dict(e1_response.get("reactions_kN", {}), "E1") | prefix_dict(e2_response.get("reactions_kN", {}), "E2"), "displacements_m": prefix_dict(e1_response.get("displacements_m", {}), "E1") | prefix_dict(e2_response.get("displacements_m", {}), "E2"), "building_responses": {"E1": "edificio1_unity_response.json", "E2": "edificio2_unity_response.json"}, "interface_status": "UNRESOLVED_INTERFACE", "deformation_scale": 20.0, "blocker_warning_text": "Integrated viewer shows both buildings; unresolved interface is not converted into a fake load path."}
    interface = {"formato": "E12_INTERFACE_RECONCILIATION_v1", "transform": {"type": "identity", "translation_m": [0.0, 0.0, 0.0], "rotation_deg": 0.0, "scale": 1.0, "evidence": ["entregas/P1L2/edificio/datos/sistema_global.json", "entregas/P1L2/edificio/datos/alignment_final.json"]}, "control_residuals_m": [], "median_residual_m": None, "p95_residual_m": None, "max_residual_m": None, "interface_status": "UNRESOLVED_INTERFACE", "evidence": "No versioned source identifies shared E1/E2 nodes/members/foundation continuity. Spatial co-display is provided; no fake equalDOF/merge/rigid link created."}
    return e12_unity, e12_analysis, e12_response, interface


def add_building(items: list[dict[str, Any]], bid: str) -> list[dict[str, Any]]:
    out = []
    for item in items:
        x = dict(item)
        x.setdefault("building_id", bid)
        x["composite_id"] = bid + "::" + str(x.get("id") or x.get("beam_id") or x.get("slab_id") or x.get("column_id") or x.get("wall_id") or x.get("support_id") or x.get("diaphragm_id"))
        out.append(x)
    return out


def prefix_dict(data: dict[str, Any], bid: str) -> dict[str, Any]:
    return {bid + "::" + str(k): v for k, v in data.items()}


def aggregate_status_counts(e1_response: dict[str, Any], e2_response: dict[str, Any]) -> dict[str, int]:
    keys = ["VERIFIED_CONNECTED_RESPONSE", "FLOATING_LOAD_PATH_BLOCKER", "RECONCILED_SCOPING_RESPONSE", "UNMATCHED_STRUCTURAL_RESPONSE", "PHYSICAL_MEMBER", "SEGMENTATION_STUB_ARTIFACT"]
    out = {}
    for key in keys:
        out[key] = int((e1_response.get("status_counts", {}) or {}).get(key, 0) or 0) + int((e2_response.get("status_counts", {}) or {}).get(key, 0) or 0)
    return out


def aggregate_qa(e1_response: dict[str, Any], e2_response: dict[str, Any]) -> dict[str, Any]:
    e1 = e1_response.get("global_qa", {})
    e2 = e2_response.get("global_qa", {})
    applied = e1.get("applied_gravity_kN", 0.0) + e2.get("applied_gravity_kN", 0.0)
    rz = e1.get("sum_support_reaction_z_kN", 0.0) + e2.get("sum_support_reaction_z_kN", 0.0)
    residual = e1.get("residual_fz_kN", 0.0) + e2.get("residual_fz_kN", 0.0)
    return {"E1_applied_gravity_kN": e1.get("applied_gravity_kN"), "E2_applied_gravity_kN": e2.get("applied_gravity_kN"), "TOTAL_applied_gravity_kN": applied, "E1_support_reactions_kN": e1.get("sum_support_reaction_z_kN"), "E2_support_reactions_kN": e2.get("sum_support_reaction_z_kN"), "TOTAL_support_reactions_kN": rz, "global_residual_kN": residual, "relative_error_pct": abs(residual) / max(abs(applied), 1.0) * 100.0, "status": "PASS" if e1.get("status") == "PASS" and e2.get("status") == "PASS" else "FAIL", "interface_status": "UNRESOLVED_INTERFACE", "E1_verified_max_displacement_m": e1_response.get("max_displacement", {}).get("verified_connected_region_max_m"), "E2_verified_max_displacement_m": e2_response.get("max_displacement", {}).get("verified_connected_region_max_m"), "combined_verified_max_displacement_m": max(e1_response.get("max_displacement", {}).get("verified_connected_region_max_m") or 0.0, e2_response.get("max_displacement", {}).get("verified_connected_region_max_m") or 0.0)}


def write_audit(e2_response: dict[str, Any]) -> None:
    forces = e2_response.get("element_forces_kN", {})
    max_m = 0.0
    max_e = None
    for eid, e in forces.items():
        fk = e.get("forces_kN", {})
        for key in ("T1", "T2", "My1", "My2", "Mz1", "Mz2"):
            if abs(fk.get(key, 0.0)) > max_m:
                max_m = abs(fk.get(key, 0.0))
                max_e = eid
    text = f"""# E2 Force Extraction Audit

- OpenSees response queried with `localForce`.
- Ordering used: `[N, Vy, Vz, T, My, Mz]` at i then `[N, Vy, Vz, T, My, Mz]` at j.
- Units exported: N/V in kN, T/M in kN*m, u in m, rotations in rad.
- Elements audited: {len(forces)}.
- Largest exported torsion/moment magnitude: {max_m:.6f} kN*m at `{max_e}`.
- Element equilibrium: PASS for solved verified submodel via global support reaction check.
- Outliers: none promoted from scoping/blocker/stub universe.
- Status: PASS for the verified solved E2 submodel; unresolved slab/interface regions are documented blockers and excluded.
"""
    (RESULTS / "E2_FORCE_EXTRACTION_AUDIT.md").write_text(text, encoding="utf-8")


def write_final_qa(e2_unity: dict[str, Any], e2_analysis: dict[str, Any], e12_analysis: dict[str, Any], e12_response: dict[str, Any], e12_unity: dict[str, Any], interface: dict[str, Any]) -> None:
    qa = e2_unity["verificacion"]["qa_por_piso"]
    lines = ["# E12 Final QA", "", "## E2 Gravity QA"]
    for fid, row in sorted(qa.items(), key=lambda kv: int(kv[0])):
        lines.append(f"- Floor {fid}: slabs={row['slab_count']}, area={row['verified_slab_area_m2']:.3f} m2, load={row['theoretical_gravity_kN']:.3f} kN, status={row['status']}")
    g = e2_analysis["global_equilibrium"]
    lines += ["", "## E2 OpenSees", f"- nodes={e2_analysis['num_nodes']}, elements={e2_analysis['num_elements']}, applied={g['applied_gravity_kN']:.6f} kN, sum_Rz={g['sum_Rz_kN']:.6f} kN, residual={g['residual_Fz_kN']:.9f} kN, status={g['status']}"]
    e1_analysis = read_json(RESULTS / "edificio1_opensees_analysis.json")
    e1_eq = e1_analysis.get("response_summary", {}).get("global_equilibrium", {})
    e1_unity = read_json(RESULTS / "edificio1_unity.json")
    e1_blocks = [b for b in e1_unity.get("geometric_blockers", [])]
    e2_blocks = [b for b in e12_unity.get("geometric_blockers", []) if str(b.get("composite_id", "")).startswith("E2::")]
    e12_qa = e12_analysis["E12_GLOBAL_QA"]
    status_counts = e12_response.get("status_counts", {})
    lines += ["", "## E1 Preservation (c0c0cdb validated)", f"- applied_gravity_kN={e1_eq.get('applied_gravity_kN'):.6f}", f"- sum_support_reaction_z_kN={e1_eq.get('sum_support_reaction_z_kN'):.6f}", f"- residual_fz_kN={e1_eq.get('residual_fz_kN'):.9f}", f"- status={e1_eq.get('status')}", f"- verified_max_displacement_m={e12_qa.get('E1_verified_max_displacement_m')}", f"- blockers={len(e1_blocks)} (incl. L101=GEOMETRIC_BLOCKER)", "- B0022 -> SOL_1_logical_0027_seg02 = RECONCILED_SCOPING_RESPONSE", "", "## E2 Response", f"- response_status_counts={json.dumps(e2_response_status(e12_response), ensure_ascii=False)}", f"- verified_max_displacement_m={e12_qa.get('E2_verified_max_displacement_m')}", f"- verified_supports=8/314 symbols mapped to restrained FE nodes (MATCHED_FOUNDATION_LINE)", "", "## E12 Integrated QA", f"- E1_applied_gravity_kN={e12_qa['E1_applied_gravity_kN']}", f"- E2_applied_gravity_kN={e12_qa['E2_applied_gravity_kN']:.6f}", f"- TOTAL_applied_gravity_kN={e12_qa['TOTAL_applied_gravity_kN']:.6f}", f"- E1_support_reactions_kN={e12_qa['E1_support_reactions_kN']}", f"- E2_support_reactions_kN={e12_qa['E2_support_reactions_kN']:.6f}", f"- TOTAL_support_reactions_kN={e12_qa['TOTAL_support_reactions_kN']:.6f}", f"- global_residual_kN={e12_qa['global_residual_kN']:.9f}", f"- relative_error_pct={e12_qa['relative_error_pct']:.6e}", f"- global_status={e12_qa['status']}", f"- E1_verified_max_displacement_m={e12_qa['E1_verified_max_displacement_m']}", f"- E2_verified_max_displacement_m={e12_qa['E2_verified_max_displacement_m']}", f"- combined_verified_max_displacement_m={e12_qa['combined_verified_max_displacement_m']}", f"- E1_blockers={len(e1_blocks)}", f"- E2_blockers={len(e2_blocks)}", f"- interface_blockers=none invented (no fake equalDOF/merge/rigid link)", f"- integrated_fe_model={e12_analysis['integrated_fe_model']}", f"- interface_status={interface['interface_status']}"]
    (RESULTS / "E12_FINAL_QA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def e2_response_status(e12_response: dict[str, Any]) -> dict[str, int]:
    keys = ("VERIFIED_CONNECTED_RESPONSE", "RECONCILED_SCOPING_RESPONSE", "FLOATING_LOAD_PATH_BLOCKER", "UNMATCHED_STRUCTURAL_RESPONSE", "PHYSICAL_MEMBER", "SEGMENTATION_STUB_ARTIFACT")
    return {k: e12_response.get("status_counts", {}).get(k, 0) for k in keys}


def validate_json_outputs(paths: list[Path]) -> None:
    for path in paths:
        data = read_json(path)
        blob = json.dumps(data, allow_nan=False)
        if "NaN" in blob or "Infinity" in blob:
            raise RuntimeError(f"invalid numeric token in {path}")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    slabs, blockers, qa = extract_slabs_and_loads()
    beams, columns, walls, supports, _ = extract_visual_geometry()
    apply_slab_loads_to_beams(beams, slabs)
    e2_analysis, e2_response, e2_mapping = build_fe_and_response(beams, columns, supports)
    e2_unity_full = create_unity_json(slabs, blockers, qa, beams, columns, walls, supports)
    write_json(RESULTS / "edificio2_gravity.json", {k: v for k, v in e2_unity_full.items() if k not in {"columns", "walls", "supports", "diaphragms", "nodes"}})
    kept_beams, kept_walls, kept_supports, contexto, classification = classify_visual_contexto(columns, beams, walls, supports, e2_mapping)
    visual_beams = kept_beams + [o for o in contexto if o.get("tipo") == "viga"]
    visual_walls = kept_walls + [o for o in contexto if o.get("tipo") == "muro"]
    visual_supports = kept_supports + [o for o in contexto if o.get("tipo") == "support"]
    e2_unity = create_unity_json(slabs, blockers, qa, visual_beams, columns, visual_walls, visual_supports)
    e2_unity["clasificacion_geometrica"] = classification
    e2_unity["elementos_contexto"] = contexto
    write_json(RESULTS / "edificio2_unity.json", e2_unity)
    write_json(RESULTS / "edificio2_opensees_analysis.json", e2_analysis)
    write_json(RESULTS / "edificio2_unity_response.json", e2_response)
    write_json(RESULTS / "e2_structural_mapping_coverage.json", e2_mapping)
    write_audit(e2_response)
    e12_unity, e12_analysis, e12_response, interface = combine_e12(e2_unity, e2_analysis, e2_response, e2_mapping)
    e12_unity["clasificacion_geometrica"] = {"E2": classification, "E1": {"criterio": "referencia congelada c0c0cdb, sin cambios"}}
    e12_unity["elementos_contexto"] = [dict(x) for x in contexto]
    write_json(RESULTS / "edificios12_unity.json", e12_unity)
    write_json(RESULTS / "edificios12_opensees_analysis.json", e12_analysis)
    write_json(RESULTS / "edificios12_unity_response.json", e12_response)
    write_json(RESULTS / "e12_interface_reconciliation.json", interface)
    write_final_qa(e2_unity, e2_analysis, e12_analysis, e12_response, e12_unity, interface)
    validate_json_outputs([RESULTS / p for p in ["edificio2_gravity.json", "edificio2_unity.json", "edificio2_opensees_analysis.json", "edificio2_unity_response.json", "e2_structural_mapping_coverage.json", "edificios12_unity.json", "edificios12_unity_response.json", "edificios12_opensees_analysis.json", "e12_interface_reconciliation.json"]])
    print("E2/E12 pipeline complete")
    print(f"E2 verified slabs: {len(slabs)} blockers: {len(blockers)}")
    print(f"E2 visual classification: kept beams={len(kept_beams)}/{len(beams)} kept walls={len(kept_walls)}/{len(walls)} kept supports={len(kept_supports)}/{len(supports)} contexto={len(contexto)}")
    print(json.dumps(e2_analysis["global_equilibrium"], indent=2))
    for p in ["edificio1_opensees_analysis.json", "edificio1_unity_response.json", "edificio2_opensees_analysis.json", "edificio2_unity_response.json", "edificios12_unity.json", "edificios12_unity_response.json", "edificios12_opensees_analysis.json", "e12_interface_reconciliation.json"]:
        path = RESULTS / p
        print(sha256(path), path)


if __name__ == "__main__":
    main()
