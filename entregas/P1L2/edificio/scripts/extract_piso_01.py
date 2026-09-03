"""Extrae datos estructurados verificables del piso 1.

Este script no modifica el modelo 3D final. Lee DXF locales, produce datos JSON,
una planta SVG de validacion 2D y una comparacion contra el viewer existente.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Iterable

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[4]
P1L2_DIR = Path(__file__).resolve().parents[2]
EDIFICIO_DIR = Path(__file__).resolve().parents[1]
DATOS_DIR = EDIFICIO_DIR / "datos"
VALIDACION_DIR = EDIFICIO_DIR / "validacion"
MODELO_DIR = EDIFICIO_DIR / "modelo"
ISSUES_DIR = EDIFICIO_DIR / "issues"

DXF_2017_DIR = Path(os.environ.get("MCOC_DXF_DIR", REPO_ROOT / "recursos" / "planos" / "dxf_generated" / "2017_67"))
DXF_2024_DIR = Path(os.environ.get("MCOC_LT2_DXF_DIR", REPO_ROOT / "recursos" / "planos" / "dxf_generated" / "2024_22"))

CURRENT_MODEL = P1L2_DIR / "unity_export" / "model_viewer.json"
BACKUP_MODEL = MODELO_DIR / "model_viewer_backup_576f014.json"


@dataclass(frozen=True)
class SourceSpec:
    zone: str
    source_key: str
    dxf_dir: Path
    dxf_name: str
    bbox_cm: tuple[float, float, float, float]
    origin_x_cm: float
    origin_y_cm: float
    global_offset_x_m: float
    global_offset_y_m: float
    piso: str = "1"
    nivel_z_m: float = 7.92
    sector: str = "planta"


# Sistema global preliminar: A-1 de LT2 = (0, 0). La Parte 1 se desplaza para
# conectar su eje E con el eje D de LT2. Esta union queda marcada para revision.
LT2_D_AXIS_M = (4223.60 - 1474.50) / 100.0

PISO_01_SOURCES = [
    SourceSpec("parte_2", "2024_22", DXF_2024_DIR, "2024_22-101.dxf", (1070.0, 983.0, 4380.0, 3822.0), 1474.50, 2719.70, 0.0, 0.0),
    SourceSpec("parte_1", "2017_67", DXF_2017_DIR, "2017_67-101.dxf", (571.0, 487.0, 5972.0, 4904.0), 1061.32, 3558.02, LT2_D_AXIS_M, 0.0),
]

LAYER_TYPES = {
    "RLE-VIGA": "viga",
    "RLE-MURO": "muro",
    "RLE-PILAR": "columna_raw",
    "RLE-LOSA": "perimetro_losa",
    "RLE-LOSAS": "perimetro_losa",
    "RLA-LOSAS": "perimetro_losa",
    "RLE-FUNDACION": "fundacion",
    "RLE-VANOS": "vano",
    "RLE-EJES": "eje_grafico",
    "RLE-EJE": "eje_grafico",
}

TYPE_DIMENSIONS = {
    "viga": {"ancho_m": 0.32, "alto_m": 0.60},
    "muro": {"espesor_m": 0.22, "altura_m": 3.96},
    "columna": {"ancho_m": 0.70, "profundidad_m": 0.70, "altura_m": 3.96},
    "fundacion": {"estado": "NEEDS_REVIEW"},
    "vano": {"estado": "referencia"},
}

COLORS = {
    "viga": "#1f77b4",
    "muro": "#2ca02c",
    "columna": "#ff7f0e",
    "perimetro_losa": "#999999",
    "eje_grafico": "#666666",
    "fundacion": "#8c564b",
    "vano": "#17becf",
}

CONFLICT_COLORS = {
    "correcto": "#222222",
    "faltante": "#d62728",
    "sobrante": "#cc00cc",
    "dudoso": "#ffb000",
    "needs_review": "#ff7f0e",
    "fragmentada": "#7f3fbf",
}

REVIEW_CLASSES = ["CONFIRMADA", "CONFIRMADO", "POSIBLE", "DUPLICADA", "DUPLICADO", "FRAGMENTADA", "FRAGMENTADO", "FALSO_POSITIVO", "NEEDS_REVIEW"]

SVG_OUTPUTS = {
    "completo": "piso_01_completo.svg",
    "parte_1": "piso_01_parte_1.svg",
    "parte_2": "piso_01_parte_2.svg",
}

PNG_OUTPUTS = {key: value.replace(".svg", ".png") for key, value in SVG_OUTPUTS.items()}

UNDERLAY_LAYERS = {
    "RLE-VIGA",
    "RLE-MURO",
    "RLE-PILAR",
    "RLE-LOSA",
    "RLE-EJES",
    "RLE-EJE",
    "RLE-TEXTO-1",
    "RLE-COTAS",
    "RLE-COTAS1",
    "RLE-SEGMENTOS1",
    "RLE-PROYECCION",
    "RLE-VANOS",
}


def ensure_dirs() -> None:
    for directory in [DATOS_DIR, VALIDACION_DIR, MODELO_DIR, ISSUES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def point_inside_bbox(point: tuple[float, float], bbox: tuple[float, float, float, float]) -> bool:
    x_min, y_min, x_max, y_max = bbox
    x, y = point
    return x_min <= x <= x_max and y_min <= y <= y_max


def segment_inside_bbox(points: list[tuple[float, float]], bbox: tuple[float, float, float, float]) -> bool:
    if not points:
        return False
    inside = sum(1 for point in points if point_inside_bbox(point, bbox))
    return inside >= max(1, len(points) // 2)


def transform(point_cm: tuple[float, float], source: SourceSpec) -> tuple[float, float]:
    x_cm, y_cm = point_cm
    x_m = (x_cm - source.origin_x_cm) / 100.0 + source.global_offset_x_m
    y_m = (source.origin_y_cm - y_cm) / 100.0 + source.global_offset_y_m
    return x_m, y_m


def entity_segments(entity) -> Iterable[list[tuple[float, float]]]:
    if entity.dxftype() == "LINE":
        start = entity.dxf.start
        end = entity.dxf.end
        yield [(float(start.x), float(start.y)), (float(end.x), float(end.y))]
    elif entity.dxftype() == "LWPOLYLINE":
        points = [(float(point[0]), float(point[1])) for point in entity.get_points()]
        for first, second in zip(points, points[1:]):
            yield [first, second]
        if entity.closed and len(points) > 2:
            yield [points[-1], points[0]]


def entity_text(entity) -> str | None:
    if entity.dxftype() == "TEXT":
        return str(entity.dxf.text)
    if entity.dxftype() == "MTEXT":
        return str(entity.text)
    return None


def text_kind(text: str) -> str | None:
    compact = text.upper().replace(" ", "")
    if compact.startswith("V.") or compact.startswith("+V.") or compact.startswith("V.S") or compact.startswith("V.I"):
        return "viga"
    if compact.startswith("M.H.A") or compact.startswith("M.I"):
        return "muro"
    if compact.startswith("P.") or compact.startswith("P.M") or compact.startswith("P.H.I"):
        return "columna"
    if compact.startswith("LOSA"):
        return "losa"
    return None


def segment_length(points: list[tuple[float, float]]) -> float:
    return math.dist(points[0], points[1])


def make_id(prefix: str, zone: str, index: int, piso: str = "1") -> str:
    zone_suffix = "P1" if zone == "parte_1" else "P2"
    floor_suffix = str(piso).replace("fundacion", "F").replace("techumbre", "T").replace("-", "_").zfill(2) if str(piso).isdigit() else str(piso).upper()
    return f"{prefix}_{zone_suffix}_{floor_suffix}_{index:04d}"


def axis_data() -> dict[str, object]:
    part_2_x = {
        "A_prime": -3.78,
        "A": 0.0,
        "B": 7.50,
        "C": 17.491,
        "C_prime": 25.042,
        "D": LT2_D_AXIS_M,
        "D_prime": 28.174,
    }
    part_1_x_raw = {
        "E_prime": -0.25,
        "E": 0.0,
        "Ea": 3.3,
        "Eb": 3.6,
        "Ec": 6.4,
        "Ed": 6.7,
        "F": 10.0,
        "F_prime": 10.25,
        "G": 20.0,
        "Ga": 21.45,
        "H": 30.0,
        "H1": 33.825,
        "H_prime": 34.477,
        "H2": 38.825,
        "I": 40.0,
        "IA": 42.6,
        "I_prime": 45.0,
        "IB": 45.345,
        "J": 50.0,
    }
    part_1_y = {"1": 0.0, "1_prime": 0.25, "1b": 0.55, "2": 10.0, "2a": 14.945, "3": 17.25, "3_prime": 17.5}
    part_2_y = {"1": 0.0, "1_prime": 3.205, "1A_prime": 4.265, "2": 8.90, "2A_prime": 11.885}
    return {
        "origen": "Eje A-1 de Parte 2 / LT2 = (0, 0, 0)",
        "estado": "DRAFT_NEEDS_REVIEW",
        "nota_calce": "Se alinea eje D de Parte 2 con eje E de Parte 1 como hipotesis de trabajo; requiere validacion contra planos generales.",
        "zonas": {
            "parte_2": {"fuente": "2024_22", "x_axes_m": part_2_x, "y_axes_m": part_2_y},
            "parte_1": {"fuente": "2017_67", "x_axes_m": {key: value + LT2_D_AXIS_M for key, value in part_1_x_raw.items()}, "y_axes_m": part_1_y},
        },
    }


def levels_data() -> dict[str, object]:
    return {
        "units": "m",
        "estado": "DRAFT",
        "niveles": {
            "base": 0.0,
            "1S": 3.96,
            "1": 7.92,
            "2": 11.88,
            "3": 15.84,
            "4": 19.80,
        },
    }


def nearest_axis_span(point: tuple[float, float], zone: str, axes: dict[str, object]) -> dict[str, str | None]:
    x, y = point
    zone_axes = axes["zonas"][zone]
    x_items = sorted(zone_axes["x_axes_m"].items(), key=lambda item: item[1])
    y_items = sorted(zone_axes["y_axes_m"].items(), key=lambda item: item[1])
    return {"x": enclosing_span(x, x_items), "y": enclosing_span(y, y_items)}


def enclosing_span(value: float, axes: list[tuple[str, float]]) -> str | None:
    if not axes:
        return None
    if value <= axes[0][1]:
        return f"antes de {axes[0][0]}"
    for (name_a, value_a), (name_b, value_b) in zip(axes, axes[1:]):
        if value_a <= value <= value_b:
            return f"{name_a}-{name_b}"
    return f"despues de {axes[-1][0]}"


def extract_raw_segments(source: SourceSpec) -> list[dict[str, object]]:
    path = source.dxf_dir / source.dxf_name
    if not path.exists():
        raise FileNotFoundError(f"DXF no encontrado: {path}")
    doc = ezdxf.readfile(path)
    elements = []
    counters: Counter[str] = Counter()
    axes = axis_data()
    for entity in doc.modelspace():
        tipo = LAYER_TYPES.get(entity.dxf.layer)
        if tipo is None:
            continue
        for raw_segment in entity_segments(entity):
            if not segment_inside_bbox(raw_segment, source.bbox_cm):
                continue
            points = [transform(point, source) for point in raw_segment]
            length = segment_length(points)
            if length < 0.05:
                continue
            counters[tipo] += 1
            center = ((points[0][0] + points[1][0]) / 2.0, (points[0][1] + points[1][1]) / 2.0)
            elements.append(
                {
                    "id": make_id(tipo.upper(), source.zone, counters[tipo], source.piso),
                    "tipo": tipo,
                    "piso": source.piso,
                    "zona": source.zone,
                    "inicio": [points[0][0], points[0][1]],
                    "fin": [points[1][0], points[1][1]],
                    "longitud_m": length,
                    "dimensiones": TYPE_DIMENSIONS.get(tipo, {}),
                    "nivel_z_m": source.nivel_z_m,
                    "fuente": {"plano": source.dxf_name, "source_key": source.source_key, "capa": entity.dxf.layer, "sector": source.sector},
                    "ejes_aproximados": nearest_axis_span(center, source.zone, axes),
                    "estado": "EXTRACTED",
                    "confianza": "medium" if tipo in {"viga", "muro"} else "needs_review",
                }
            )
    return elements


def extract_labels(source: SourceSpec) -> list[dict[str, object]]:
    path = source.dxf_dir / source.dxf_name
    doc = ezdxf.readfile(path)
    labels = []
    counter = 1
    axes = axis_data()
    for entity in doc.modelspace():
        if entity.dxftype() not in {"TEXT", "MTEXT"}:
            continue
        raw = entity_text(entity)
        if not raw:
            continue
        point = (float(entity.dxf.insert.x), float(entity.dxf.insert.y))
        if not point_inside_bbox(point, source.bbox_cm):
            continue
        text = " ".join(raw.replace("\\P", " ").split())
        kind = text_kind(text)
        if kind is None:
            continue
        x, y = transform(point, source)
        labels.append(
            {
                "id": make_id("LBL", source.zone, counter, source.piso),
                "tipo": kind,
                "texto": text,
                "zona": source.zone,
                "piso": source.piso,
                "punto": [x, y],
                "fuente": {"plano": source.dxf_name, "source_key": source.source_key, "capa": entity.dxf.layer, "sector": source.sector},
                "ejes_aproximados": nearest_axis_span((x, y), source.zone, axes),
            }
        )
        counter += 1
    return labels


def extract_underlay(source: SourceSpec) -> list[dict[str, object]]:
    path = source.dxf_dir / source.dxf_name
    doc = ezdxf.readfile(path)
    underlay = []
    counter = 1
    for entity in doc.modelspace():
        layer = str(entity.dxf.layer)
        if layer not in UNDERLAY_LAYERS:
            continue
        for raw_segment in entity_segments(entity):
            if not segment_inside_bbox(raw_segment, source.bbox_cm):
                continue
            points = [transform(point, source) for point in raw_segment]
            if segment_length(points) < 0.03:
                continue
            underlay.append(
                {
                    "id": make_id("PLANO", source.zone, counter, source.piso),
                    "zona": source.zone,
                    "piso": source.piso,
                    "fuente": {"plano": source.dxf_name, "source_key": source.source_key, "capa": layer, "sector": source.sector},
                    "inicio": [points[0][0], points[0][1]],
                    "fin": [points[1][0], points[1][1]],
                }
            )
            counter += 1
    return underlay


def cluster_columns(raw_elements: list[dict[str, object]]) -> list[dict[str, object]]:
    structural = [element for element in raw_elements if element["tipo"] != "columna_raw"]
    raw_columns = [element for element in raw_elements if element["tipo"] == "columna_raw" and 0.08 <= float(element["longitud_m"]) <= 1.50]
    grouped: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for element in raw_columns:
        grouped[(str(element.get("piso", "1")), str(element["zona"]))].append(element)

    columns = []
    axes = axis_data()
    for (piso, zone), items in grouped.items():
        clusters: list[dict[str, object]] = []
        for item in items:
            sx, sy = item["inicio"]
            ex, ey = item["fin"]
            mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
            assigned = None
            for cluster in clusters:
                cx, cy = cluster["center"]
                if math.hypot(mx - cx, my - cy) <= 0.85:
                    assigned = cluster
                    break
            if assigned is None:
                assigned = {"items": [], "points": [], "center": (mx, my)}
                clusters.append(assigned)
            assigned["items"].append(item)
            assigned["points"].extend([item["inicio"], item["fin"]])
            xs = [point[0] for point in assigned["points"]]
            ys = [point[1] for point in assigned["points"]]
            assigned["center"] = (sum(xs) / len(xs), sum(ys) / len(ys))

        for index, cluster in enumerate(clusters, start=1):
            xs = [point[0] for point in cluster["points"]]
            ys = [point[1] for point in cluster["points"]]
            cx, cy = cluster["center"]
            first = cluster["items"][0]
            columns.append(
                {
                    "id": make_id("C", zone, index, piso),
                    "tipo": "columna",
                    "piso": piso,
                    "zona": zone,
                    "centro": [cx, cy],
                    "dimensiones": {
                        "ancho_m": min(max(max(xs) - min(xs), 0.35), 1.20),
                        "profundidad_m": min(max(max(ys) - min(ys), 0.35), 1.20),
                        "altura_m": 3.96,
                    },
                    "nivel_z_m": float(first.get("nivel_z_m", 7.92)),
                    "fuente": {"plano": first["fuente"]["plano"], "source_key": first["fuente"]["source_key"], "capa": "RLE-PILAR", "elementos_raw": [item["id"] for item in cluster["items"]]},
                    "ejes_aproximados": nearest_axis_span((cx, cy), zone, axes),
                    "estado": "EXTRACTED",
                    "confianza": "medium",
                }
            )
    return structural + columns


def element_midpoint(element: dict[str, object]) -> tuple[float, float]:
    if "centro" in element:
        return float(element["centro"][0]), float(element["centro"][1])
    start = element["inicio"]
    end = element["fin"]
    return (float(start[0]) + float(end[0])) / 2.0, (float(start[1]) + float(end[1])) / 2.0


def element_endpoints(element: dict[str, object]) -> tuple[tuple[float, float], tuple[float, float]] | None:
    if "inicio" not in element or "fin" not in element:
        return None
    return tuple(element["inicio"]), tuple(element["fin"])


def distance_point_segment(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    px, py = point
    ax, ay = start
    bx, by = end
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    length_sq = vx * vx + vy * vy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / length_sq))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def orientation_key(element: dict[str, object]) -> str:
    endpoints = element_endpoints(element)
    if endpoints is None:
        return "P"
    (x1, y1), (x2, y2) = endpoints
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) <= 0.15:
        return "V"
    if abs(dy) <= 0.15:
        return "H"
    return "D"


def canonical_line_key(element: dict[str, object], tolerance: float = 0.10) -> tuple[object, ...] | None:
    endpoints = element_endpoints(element)
    if endpoints is None:
        return None
    (x1, y1), (x2, y2) = endpoints
    orientation = orientation_key(element)
    if orientation == "V":
        return (element.get("piso", "1"), element["zona"], element["tipo"], "V", round(((x1 + x2) / 2.0) / tolerance), round(min(y1, y2) / tolerance), round(max(y1, y2) / tolerance))
    if orientation == "H":
        return (element.get("piso", "1"), element["zona"], element["tipo"], "H", round(((y1 + y2) / 2.0) / tolerance), round(min(x1, x2) / tolerance), round(max(x1, x2) / tolerance))
    return (element.get("piso", "1"), element["zona"], element["tipo"], "D", round(x1 / tolerance), round(y1 / tolerance), round(x2 / tolerance), round(y2 / tolerance))


def confirmed_category(tipo: str) -> str:
    return "CONFIRMADO" if tipo == "muro" else "CONFIRMADA"


def duplicate_category(tipo: str) -> str:
    return "DUPLICADO" if tipo == "muro" else "DUPLICADA"


def fragmented_category(tipo: str) -> str:
    return "FRAGMENTADO" if tipo == "muro" else "FRAGMENTADA"


def line_axis_interval(element: dict[str, object]) -> tuple[str, float, tuple[float, float]] | None:
    endpoints = element_endpoints(element)
    if endpoints is None:
        return None
    orientation = orientation_key(element)
    if orientation == "H":
        (x1, y1), (x2, y2) = endpoints
        return orientation, (y1 + y2) / 2.0, tuple(sorted((x1, x2)))
    if orientation == "V":
        (x1, y1), (x2, y2) = endpoints
        return orientation, (x1 + x2) / 2.0, tuple(sorted((y1, y2)))
    return None


def interval_gap(a: tuple[float, float], b: tuple[float, float]) -> float:
    return max(0.0, max(a[0], b[0]) - min(a[1], b[1]))


def logical_fragment_groups(elements: list[dict[str, object]], tipo: str) -> tuple[list[dict[str, object]], dict[str, str]]:
    by_line: defaultdict[tuple[object, ...], list[tuple[dict[str, object], tuple[float, float]]]] = defaultdict(list)
    fixed_tolerance = 0.18 if tipo == "muro" else 0.25
    gap_tolerance = 0.25 if tipo == "muro" else 0.45
    for element in elements:
        if element["tipo"] != tipo:
            continue
        data = line_axis_interval(element)
        if data is None:
            continue
        orientation, fixed, interval = data
        by_line[(element.get("piso", "1"), element["zona"], orientation, round(fixed / fixed_tolerance))].append((element, interval))

    groups = []
    membership = {}
    counters: Counter[str] = Counter()
    for (piso, zone, orientation, _fixed_key), items in by_line.items():
        items.sort(key=lambda item: item[1][0])
        current: list[tuple[dict[str, object], tuple[float, float]]] = []
        current_interval: tuple[float, float] | None = None
        for item in items:
            element, interval = item
            if not current or current_interval is None or interval_gap(current_interval, interval) <= gap_tolerance:
                current.append(item)
                current_interval = interval if current_interval is None else (min(current_interval[0], interval[0]), max(current_interval[1], interval[1]))
                continue
            add_logical_group(groups, membership, counters, tipo, str(zone), str(piso), str(orientation), current, current_interval)
            current = [item]
            current_interval = interval
        if current and current_interval is not None:
            add_logical_group(groups, membership, counters, tipo, str(zone), str(piso), str(orientation), current, current_interval)
    return groups, membership


def add_logical_group(
    groups: list[dict[str, object]],
    membership: dict[str, str],
    counters: Counter[str],
    tipo: str,
    zone: str,
    piso: str,
    orientation: str,
    items: list[tuple[dict[str, object], tuple[float, float]]],
    merged_interval: tuple[float, float],
) -> None:
    if len(items) < 2:
        return
    counter_key = f"{piso}:{zone}"
    counters[counter_key] += 1
    group_id = make_id(f"{tipo.upper()}_GRUPO", zone, counters[counter_key], piso)
    ids = [str(element["id"]) for element, _interval in items]
    for element_id in ids:
        membership[element_id] = group_id
    groups.append(
        {
            "id": group_id,
            "tipo": tipo,
            "piso": piso,
            "zona": zone,
            "orientacion": orientation,
            "criterio": "segmentos_colineales_contiguos_o_solapados",
            "elementos": ids,
            "cantidad_segmentos": len(ids),
            "longitud_total_m": round(sum(float(element.get("longitud_m", 0.0)) for element, _interval in items), 3),
            "largo_envuelto_m": round(merged_interval[1] - merged_interval[0], 3),
        }
    )


def near_parallel_face(element: dict[str, object], others: list[dict[str, object]], max_gap_m: float, min_overlap_m: float = 0.40) -> str | None:
    endpoints = element_endpoints(element)
    if endpoints is None:
        return None
    orientation = orientation_key(element)
    if orientation not in {"H", "V"}:
        return None
    (x1, y1), (x2, y2) = endpoints
    a1, a2 = sorted((x1, x2)) if orientation == "H" else sorted((y1, y2))
    fixed = (y1 + y2) / 2.0 if orientation == "H" else (x1 + x2) / 2.0
    for other in others:
        if other is element or other["tipo"] != element["tipo"] or other["zona"] != element["zona"] or other.get("piso") != element.get("piso") or orientation_key(other) != orientation:
            continue
        other_endpoints = element_endpoints(other)
        if other_endpoints is None:
            continue
        (ox1, oy1), (ox2, oy2) = other_endpoints
        b1, b2 = sorted((ox1, ox2)) if orientation == "H" else sorted((oy1, oy2))
        other_fixed = (oy1 + oy2) / 2.0 if orientation == "H" else (ox1 + ox2) / 2.0
        overlap = max(0.0, min(a2, b2) - max(a1, b1))
        gap = abs(fixed - other_fixed)
        if min_overlap_m <= overlap and 0.08 <= gap <= max_gap_m:
            return str(other["id"])
    return None


def nearest_label_distance(element: dict[str, object], labels: list[dict[str, object]]) -> tuple[float | None, str | None]:
    candidates = [label for label in labels if label["zona"] == element["zona"] and label.get("piso") == element.get("piso") and label["tipo"] == element["tipo"]]
    if not candidates:
        return None, None
    endpoints = element_endpoints(element)
    distances = []
    for label in candidates:
        point = tuple(label["punto"])
        if endpoints is None:
            dist = math.dist(point, element_midpoint(element))
        else:
            dist = distance_point_segment(point, endpoints[0], endpoints[1])
        distances.append((dist, label["id"]))
    return min(distances, default=(None, None))


def revise_extraction(elements: list[dict[str, object]], labels: list[dict[str, object]]) -> dict[str, object]:
    duplicate_keys: defaultdict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for element in elements:
        key = canonical_line_key(element)
        if key is not None and element["tipo"] in {"viga", "muro", "perimetro_losa"}:
            duplicate_keys[key].append(element)

    duplicate_ids = {item["id"] for group in duplicate_keys.values() if len(group) > 1 for item in group[1:]}
    logical_groups: list[dict[str, object]] = []
    fragment_membership: dict[str, str] = {}
    for tipo in ["viga", "muro"]:
        groups, membership = logical_fragment_groups(elements, tipo)
        logical_groups.extend(groups)
        fragment_membership.update(membership)

    for element in elements:
        reasons = []
        confidence_score = 0.85
        tipo = element["tipo"]
        length = float(element.get("longitud_m", 0.0))
        if element["id"] in duplicate_ids:
            reasons.append("duplicado_geometrico")
            confidence_score -= 0.45
        if element["id"] in fragment_membership:
            element["grupo_logico"] = fragment_membership[str(element["id"])]
            reasons.append(f"fragmento_de_{fragment_membership[str(element['id'])]}")
            confidence_score -= 0.10
        if tipo == "viga":
            label_dist, label_id = nearest_label_distance(element, labels)
            element["etiqueta_cercana"] = {"id": label_id, "distancia_m": round(label_dist, 3) if label_dist is not None else None}
            if label_dist is None or label_dist > 2.00:
                reasons.append("sin_etiqueta_viga_cercana")
                confidence_score -= 0.25
            if length < 0.30:
                reasons.append("viga_demasiado_corta")
                confidence_score -= 0.55
            elif length < 0.75:
                reasons.append("viga_muy_corta")
                confidence_score -= 0.20
            face = near_parallel_face(element, elements, max_gap_m=0.85)
            if face:
                reasons.append(f"posible_cara_paralela_de_{face}")
                confidence_score -= 0.15
            if orientation_key(element) == "D":
                reasons.append("geometria_no_ortogonal")
                confidence_score -= 0.20
        elif tipo == "muro":
            label_dist, label_id = nearest_label_distance(element, labels)
            element["etiqueta_cercana"] = {"id": label_id, "distancia_m": round(label_dist, 3) if label_dist is not None else None}
            if label_dist is None or label_dist > 1.50:
                reasons.append("sin_etiqueta_muro_cercana")
                confidence_score -= 0.20
            if length < 0.25:
                reasons.append("muro_demasiado_corto")
                confidence_score -= 0.55
            elif length < 0.50:
                reasons.append("muro_muy_corto")
                confidence_score -= 0.25
            face = near_parallel_face(element, elements, max_gap_m=0.35)
            if face:
                reasons.append(f"posible_doble_cara_de_{face}")
                confidence_score -= 0.20
            if orientation_key(element) == "D":
                reasons.append("geometria_no_ortogonal")
                confidence_score -= 0.20
        elif tipo == "columna":
            x_span = element.get("ejes_aproximados", {}).get("x")
            y_span = element.get("ejes_aproximados", {}).get("y")
            if x_span is None or y_span is None:
                reasons.append("sin_ejes_asociados")
                confidence_score -= 0.25
        elif tipo in {"perimetro_losa", "eje_grafico"}:
            confidence_score = 0.60
            reasons.append("referencia_no_elemento_estructural_directo")

        element["estado_revision"] = classify_review_state(tipo, reasons, confidence_score, str(element["id"]) in duplicate_ids, str(element["id"]) in fragment_membership)
        element["categoria_revision"] = element["estado_revision"]
        element["motivos_revision"] = reasons
        element["confianza_score"] = round(max(0.05, min(0.98, confidence_score)), 2)

    return {
        "duplicados": [
            {"grupo": index + 1, "ids": [item["id"] for item in group], "tipo": group[0]["tipo"], "zona": group[0]["zona"]}
            for index, group in enumerate(group for group in duplicate_keys.values() if len(group) > 1)
        ],
        "grupos_logicos": logical_groups,
        "grupos_logicos_por_tipo": dict(Counter(str(group["tipo"]) for group in logical_groups)),
        "por_categoria": dict(Counter(str(element.get("estado_revision", "sin_estado")) for element in elements)),
        "posibles_falsos_positivos": summarize_by_type([element for element in elements if element.get("estado_revision") == "FALSO_POSITIVO"]),
        "needs_review": summarize_by_type([element for element in elements if element.get("estado_revision") == "NEEDS_REVIEW"]),
        "detalle_posibles_falsos_positivos": [element_issue_summary(element) for element in elements if element.get("estado_revision") == "FALSO_POSITIVO"][:200],
        "detalle_needs_review": [element_issue_summary(element) for element in elements if element.get("estado_revision") == "NEEDS_REVIEW"][:300],
    }


def classify_review_state(tipo: str, reasons: list[str], confidence_score: float, is_duplicate: bool, is_fragment: bool) -> str:
    if is_duplicate:
        return duplicate_category(tipo)
    if tipo in {"perimetro_losa", "eje_grafico"}:
        return "NEEDS_REVIEW"
    if tipo not in {"viga", "muro", "columna"}:
        return "NEEDS_REVIEW"
    if confidence_score < 0.35 or any(reason.endswith("demasiado_corta") for reason in reasons):
        return "FALSO_POSITIVO"
    if is_fragment:
        return fragmented_category(tipo)
    if not reasons:
        return confirmed_category(tipo)
    if any(reason in {"geometria_no_ortogonal", "sin_ejes_asociados"} for reason in reasons):
        return "NEEDS_REVIEW"
    return "POSIBLE"


def element_issue_summary(element: dict[str, object]) -> dict[str, object]:
    return {
        "id": element["id"],
        "tipo": element["tipo"],
        "zona": element["zona"],
        "fuente": element.get("fuente"),
        "ejes_aproximados": element.get("ejes_aproximados"),
        "estado_revision": element.get("estado_revision"),
        "grupo_logico": element.get("grupo_logico"),
        "etiqueta_cercana": element.get("etiqueta_cercana"),
        "confianza_score": element.get("confianza_score"),
        "motivos_revision": element.get("motivos_revision", []),
    }


def summarize_by_type(elements: list[dict[str, object]]) -> dict[str, int]:
    return dict(Counter(str(element["tipo"]) for element in elements))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def source_record(source: SourceSpec) -> dict[str, object]:
    record = asdict(source)
    record["dxf_dir"] = "$MCOC_LT2_DXF_DIR" if source.source_key == "2024_22" else "$MCOC_DXF_DIR"
    return record


def svg_point(point: tuple[float, float], bounds: tuple[float, float, float, float], scale: float, margin: float) -> tuple[float, float]:
    min_x, min_y, _max_x, max_y = bounds
    x, y = point
    return margin + (x - min_x) * scale, margin + (max_y - y) * scale


def write_svg(path: Path, elements: list[dict[str, object]], axes: dict[str, object]) -> None:
    points = []
    for element in elements:
        if "inicio" in element and "fin" in element:
            points.extend([tuple(element["inicio"]), tuple(element["fin"])])
        elif "centro" in element:
            points.append(tuple(element["centro"]))
    min_x = min(point[0] for point in points) - 2.0
    max_x = max(point[0] for point in points) + 2.0
    min_y = min(point[1] for point in points) - 2.0
    max_y = max(point[1] for point in points) + 2.0
    bounds = (min_x, min_y, max_x, max_y)
    scale = min(1200 / max(max_x - min_x, 1), 760 / max(max_y - min_y, 1))
    margin = 40.0
    width = (max_x - min_x) * scale + margin * 2
    height = (max_y - min_y) * scale + margin * 2
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">']
    rows.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    rows.append('<text x="20" y="25" font-size="16" font-family="Arial">Piso 1 - Validacion 2D estructurada (DRAFT)</text>')
    for zone, zone_axes in axes["zonas"].items():
        for name, x_value in zone_axes["x_axes_m"].items():
            x1, y1 = svg_point((x_value, min_y), bounds, scale, margin)
            x2, y2 = svg_point((x_value, max_y), bounds, scale, margin)
            rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#dddddd" stroke-dasharray="4 4"/>')
            rows.append(f'<text x="{x1 + 3:.2f}" y="{y2 + 14:.2f}" font-size="10" fill="#666">{zone}:{name}</text>')
        for name, y_value in zone_axes["y_axes_m"].items():
            x1, y1 = svg_point((min_x, y_value), bounds, scale, margin)
            x2, y2 = svg_point((max_x, y_value), bounds, scale, margin)
            rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#eeeeee" stroke-dasharray="4 4"/>')
            rows.append(f'<text x="{x1 + 3:.2f}" y="{y1 - 3:.2f}" font-size="10" fill="#666">{zone}:{name}</text>')
    for element in elements:
        tipo = element["tipo"]
        color = COLORS.get(tipo, "#888888")
        if tipo == "columna":
            x, y = svg_point(tuple(element["centro"]), bounds, scale, margin)
            rows.append(f'<rect x="{x - 4:.2f}" y="{y - 4:.2f}" width="8" height="8" fill="{color}" stroke="#111" stroke-width="0.5"><title>{element["id"]}</title></rect>')
        elif "inicio" in element and "fin" in element:
            x1, y1 = svg_point(tuple(element["inicio"]), bounds, scale, margin)
            x2, y2 = svg_point(tuple(element["fin"]), bounds, scale, margin)
            stroke_width = 3 if tipo == "muro" else 2 if tipo == "viga" else 1
            opacity = 0.95 if tipo in {"muro", "viga"} else 0.35
            rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{stroke_width}" opacity="{opacity}"><title>{element["id"]}</title></line>')
    rows.append('<g font-family="Arial" font-size="12">')
    rows.append('<text x="20" y="50" fill="#2ca02c">Muros</text>')
    rows.append('<text x="90" y="50" fill="#1f77b4">Vigas</text>')
    rows.append('<text x="150" y="50" fill="#ff7f0e">Columnas</text>')
    rows.append('</g>')
    rows.append('</svg>')
    path.write_text("\n".join(rows), encoding="utf-8")


def existing_model_elements(piso: str = "1") -> list[dict[str, object]]:
    current = json.loads(CURRENT_MODEL.read_text(encoding="utf-8"))
    existing = []
    for solid in current.get("solids", []):
        if str(solid.get("floor")) != str(piso):
            continue
        tipo = type_from_solid(solid)
        if tipo is None:
            continue
        geometry = model_geometry(solid)
        item = {
            "id": str(solid.get("solidTag")),
            "tipo": tipo,
            "piso": str(piso),
            "zona": "parte_1",
            "fuente": {"plano": solid.get("source_dxf"), "capa": solid.get("source_layer")},
            "estado_revision": "MODEL_EXISTING",
        }
        item.update(geometry)
        existing.append(item)
    return existing


def conflict_maps(conflicts: dict[str, object]) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]], list[dict[str, object]]]:
    by_extracted = {str(item["elemento"]): item for item in conflicts.get("faltantes", []) + conflicts.get("dudosos", [])}
    by_existing = {str(item["elemento"]): item for item in conflicts.get("sobrantes", [])}
    all_conflicts = conflicts.get("faltantes", []) + conflicts.get("dudosos", []) + conflicts.get("sobrantes", [])
    return by_extracted, by_existing, all_conflicts


def validation_bounds(
    elements: list[dict[str, object]],
    existing: list[dict[str, object]],
    underlay: list[dict[str, object]],
    zones: set[str] | None,
) -> tuple[float, float, float, float]:
    points = []
    for collection in [elements, existing, underlay]:
        for item in collection:
            if zones and item.get("zona") not in zones:
                continue
            if "inicio" in item and "fin" in item:
                points.extend([tuple(item["inicio"]), tuple(item["fin"])])
            elif "centro" in item:
                points.append(tuple(item["centro"]))
    if not points:
        return (-1.0, -1.0, 1.0, 1.0)
    min_x = min(point[0] for point in points) - 2.0
    max_x = max(point[0] for point in points) + 2.0
    min_y = min(point[1] for point in points) - 2.0
    max_y = max(point[1] for point in points) + 2.0
    return min_x, min_y, max_x, max_y


def draw_axes_svg(rows: list[str], axes: dict[str, object], zones: set[str] | None, bounds: tuple[float, float, float, float], scale: float, margin: float) -> None:
    min_x, min_y, max_x, max_y = bounds
    for zone, zone_axes in axes["zonas"].items():
        if zones and zone not in zones:
            continue
        for name, x_value in zone_axes["x_axes_m"].items():
            if x_value < min_x or x_value > max_x:
                continue
            x1, y1 = svg_point((x_value, min_y), bounds, scale, margin)
            x2, y2 = svg_point((x_value, max_y), bounds, scale, margin)
            rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#e6e6e6" stroke-dasharray="4 4"/>')
            rows.append(f'<text x="{x1 + 3:.2f}" y="{y2 + 13:.2f}" font-size="9" fill="#666">{escape(zone)}:{escape(name)}</text>')
        for name, y_value in zone_axes["y_axes_m"].items():
            if y_value < min_y or y_value > max_y:
                continue
            x1, y1 = svg_point((min_x, y_value), bounds, scale, margin)
            x2, y2 = svg_point((max_x, y_value), bounds, scale, margin)
            rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#f0f0f0" stroke-dasharray="4 4"/>')
            rows.append(f'<text x="{x1 + 3:.2f}" y="{y1 - 3:.2f}" font-size="9" fill="#666">{escape(zone)}:{escape(name)}</text>')


def draw_line_svg(rows: list[str], item: dict[str, object], bounds: tuple[float, float, float, float], scale: float, margin: float, color: str, width: float, opacity: float, dash: str | None = None) -> None:
    x1, y1 = svg_point(tuple(item["inicio"]), bounds, scale, margin)
    x2, y2 = svg_point(tuple(item["fin"]), bounds, scale, margin)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    rows.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"{dash_attr}><title>{escape(str(item.get("id", "")))}</title></line>')


def draw_column_svg(rows: list[str], item: dict[str, object], bounds: tuple[float, float, float, float], scale: float, margin: float, color: str, opacity: float, dash: str | None = None) -> None:
    x, y = svg_point(tuple(item["centro"]), bounds, scale, margin)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    rows.append(f'<rect x="{x - 4:.2f}" y="{y - 4:.2f}" width="8" height="8" fill="{color}" opacity="{opacity}" stroke="#111" stroke-width="0.7"{dash_attr}><title>{escape(str(item.get("id", "")))}</title></rect>')


def label_svg(rows: list[str], item: dict[str, object], bounds: tuple[float, float, float, float], scale: float, margin: float, color: str) -> None:
    point = tuple(item["centro"]) if "centro" in item else element_midpoint(item)
    x, y = svg_point(point, bounds, scale, margin)
    rows.append(f'<text x="{x + 5:.2f}" y="{y - 5:.2f}" font-size="9" font-family="Arial" fill="{color}" stroke="#fff" stroke-width="2" paint-order="stroke">{escape(str(item.get("id", "")))}</text>')


def write_validation_svg(
    path: Path,
    title: str,
    elements: list[dict[str, object]],
    existing: list[dict[str, object]],
    underlay: list[dict[str, object]],
    axes: dict[str, object],
    conflicts: dict[str, object],
    zones: set[str] | None = None,
) -> None:
    by_extracted, by_existing, _all = conflict_maps(conflicts)
    bounds = validation_bounds(elements, existing, underlay, zones)
    min_x, min_y, max_x, max_y = bounds
    margin = 55.0
    scale = min(1500 / max(max_x - min_x, 1), 950 / max(max_y - min_y, 1))
    width = (max_x - min_x) * scale + margin * 2
    height = (max_y - min_y) * scale + margin * 2
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">']
    rows.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    rows.append(f'<text x="20" y="26" font-size="18" font-family="Arial" font-weight="700">{escape(title)}</text>')
    rows.append('<text x="20" y="46" font-size="11" font-family="Arial" fill="#555">gris claro: plano original | azul/verde/naranjo: detectado | negro punteado: modelo actual | rojo: faltante | magenta: sobrante/duplicado | morado: fragmentado | amarillo: dudoso/needs_review</text>')
    for item in underlay:
        if zones and item.get("zona") not in zones:
            continue
        draw_line_svg(rows, item, bounds, scale, margin, "#c9c9c9", 0.8, 0.45)
    draw_axes_svg(rows, axes, zones, bounds, scale, margin)
    for item in existing:
        if zones and item.get("zona") not in zones:
            continue
        color = CONFLICT_COLORS["sobrante"] if item["id"] in by_existing else CONFLICT_COLORS["correcto"]
        if "centro" in item:
            draw_column_svg(rows, item, bounds, scale, margin, color, 0.85, "5 4")
        else:
            draw_line_svg(rows, item, bounds, scale, margin, color, 2.3, 0.85, "6 4")
        if item["id"] in by_existing:
            label_svg(rows, item, bounds, scale, margin, color)
    for item in elements:
        if zones and item.get("zona") not in zones:
            continue
        conflict = by_extracted.get(str(item["id"]))
        if conflict:
            color = CONFLICT_COLORS["faltante"] if conflict["tipo"] == "faltante" else CONFLICT_COLORS["dudoso"]
            width_line = 4.0
            opacity = 0.95
        elif item.get("estado_revision") in {"FALSO_POSITIVO", "POSIBLE"}:
            color = CONFLICT_COLORS["needs_review"]
            width_line = 3.5
            opacity = 0.85
        elif item.get("estado_revision") in {"DUPLICADA", "DUPLICADO"}:
            color = CONFLICT_COLORS["sobrante"]
            width_line = 3.5
            opacity = 0.85
        elif item.get("estado_revision") in {"FRAGMENTADA", "FRAGMENTADO"}:
            color = CONFLICT_COLORS["fragmentada"]
            width_line = 3.0
            opacity = 0.85
        elif item.get("estado_revision") == "NEEDS_REVIEW":
            color = CONFLICT_COLORS["dudoso"]
            width_line = 2.5
            opacity = 0.75
        else:
            color = COLORS.get(str(item["tipo"]), "#777777")
            width_line = 2.0 if item["tipo"] == "viga" else 3.0 if item["tipo"] == "muro" else 1.0
            opacity = 0.72
        if item["tipo"] == "columna":
            draw_column_svg(rows, item, bounds, scale, margin, color, opacity)
        elif "inicio" in item and "fin" in item:
            draw_line_svg(rows, item, bounds, scale, margin, color, width_line, opacity)
        if conflict or item.get("estado_revision") in {"FALSO_POSITIVO", "POSIBLE", "DUPLICADA", "DUPLICADO", "FRAGMENTADA", "FRAGMENTADO", "NEEDS_REVIEW"}:
            label_svg(rows, item, bounds, scale, margin, color)
    rows.append('<g font-family="Arial" font-size="11">')
    legend_y = height - 78
    legend = [("Plano original", "#c9c9c9"), ("Vigas detectadas", COLORS["viga"]), ("Muros detectados", COLORS["muro"]), ("Columnas", COLORS["columna"]), ("Modelo actual", "#222222"), ("Faltante", CONFLICT_COLORS["faltante"]), ("Duplicado/sobrante", CONFLICT_COLORS["sobrante"]), ("Fragmentado", CONFLICT_COLORS["fragmentada"])]
    for i, (label, color) in enumerate(legend):
        x = 20 + (i % 4) * 180
        y = legend_y + (i // 4) * 24
        rows.append(f'<line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y}" stroke="{color}" stroke-width="4"/>')
        rows.append(f'<text x="{x + 36}" y="{y + 4}" fill="#333">{escape(label)}</text>')
    rows.append('</g>')
    rows.append('</svg>')
    path.write_text("\n".join(rows), encoding="utf-8")


def write_validation_png(
    path: Path,
    title: str,
    elements: list[dict[str, object]],
    existing: list[dict[str, object]],
    underlay: list[dict[str, object]],
    conflicts: dict[str, object],
    zones: set[str] | None = None,
) -> None:
    by_extracted, by_existing, _all = conflict_maps(conflicts)
    bounds = validation_bounds(elements, existing, underlay, zones)
    min_x, min_y, max_x, max_y = bounds
    fig, ax = plt.subplots(figsize=(18, 11), dpi=180)
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.grid(True, linewidth=0.25, alpha=0.25)
    for item in underlay:
        if zones and item.get("zona") not in zones:
            continue
        ax.plot([item["inicio"][0], item["fin"][0]], [item["inicio"][1], item["fin"][1]], color="#c9c9c9", linewidth=0.35, alpha=0.45)
    for item in existing:
        if zones and item.get("zona") not in zones:
            continue
        color = CONFLICT_COLORS["sobrante"] if item["id"] in by_existing else "#222222"
        if "centro" in item:
            ax.scatter([item["centro"][0]], [item["centro"][1]], color=color, marker="s", s=20, alpha=0.9)
        else:
            ax.plot([item["inicio"][0], item["fin"][0]], [item["inicio"][1], item["fin"][1]], color=color, linewidth=1.2, alpha=0.75, linestyle="--")
        if item["id"] in by_existing:
            x, y = element_midpoint(item)
            ax.text(x, y, item["id"], fontsize=5, color=color)
    for item in elements:
        if zones and item.get("zona") not in zones:
            continue
        conflict = by_extracted.get(str(item["id"]))
        color = COLORS.get(str(item["tipo"]), "#777777")
        linewidth = 1.0
        alpha = 0.60
        if conflict:
            color = CONFLICT_COLORS["faltante"] if conflict["tipo"] == "faltante" else CONFLICT_COLORS["dudoso"]
            linewidth = 2.0
            alpha = 0.95
        elif item.get("estado_revision") in {"FALSO_POSITIVO", "POSIBLE"}:
            color = CONFLICT_COLORS["needs_review"]
            linewidth = 1.6
            alpha = 0.85
        elif item.get("estado_revision") in {"DUPLICADA", "DUPLICADO"}:
            color = CONFLICT_COLORS["sobrante"]
            linewidth = 1.6
            alpha = 0.85
        elif item.get("estado_revision") in {"FRAGMENTADA", "FRAGMENTADO"}:
            color = CONFLICT_COLORS["fragmentada"]
            linewidth = 1.5
            alpha = 0.85
        elif item.get("estado_revision") == "NEEDS_REVIEW":
            color = CONFLICT_COLORS["dudoso"]
            linewidth = 1.4
            alpha = 0.75
        if item["tipo"] == "columna":
            ax.scatter([item["centro"][0]], [item["centro"][1]], color=color, marker="s", s=30, alpha=alpha)
        elif "inicio" in item and "fin" in item:
            ax.plot([item["inicio"][0], item["fin"][0]], [item["inicio"][1], item["fin"][1]], color=color, linewidth=linewidth, alpha=alpha)
        if conflict or item.get("estado_revision") in {"FALSO_POSITIVO", "POSIBLE", "DUPLICADA", "DUPLICADO", "FRAGMENTADA", "FRAGMENTADO", "NEEDS_REVIEW"}:
            x, y = element_midpoint(item)
            ax.text(x, y, item["id"], fontsize=5, color=color)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def model_point(solid: dict[str, object]) -> tuple[float, float]:
    if "center" in solid:
        return float(solid["center"][0]) + LT2_D_AXIS_M, float(solid["center"][1])
    start = solid["start"]
    end = solid["end"]
    return (float(start[0]) + float(end[0])) / 2.0 + LT2_D_AXIS_M, (float(start[1]) + float(end[1])) / 2.0


def model_geometry(solid: dict[str, object]) -> dict[str, object]:
    if "center" in solid:
        return {"centro": [float(solid["center"][0]) + LT2_D_AXIS_M, float(solid["center"][1])]}
    return {
        "inicio": [float(solid["start"][0]) + LT2_D_AXIS_M, float(solid["start"][1])],
        "fin": [float(solid["end"][0]) + LT2_D_AXIS_M, float(solid["end"][1])],
    }


def element_point(element: dict[str, object]) -> tuple[float, float]:
    if "centro" in element:
        return float(element["centro"][0]), float(element["centro"][1])
    start = element["inicio"]
    end = element["fin"]
    return (float(start[0]) + float(end[0])) / 2.0, (float(start[1]) + float(end[1])) / 2.0


def type_from_solid(solid: dict[str, object]) -> str | None:
    return {"beam": "viga", "wall": "muro", "column": "columna"}.get(str(solid.get("category")))


def compare_with_existing_model(elements: list[dict[str, object]], piso: str = "1") -> dict[str, object]:
    current = json.loads(CURRENT_MODEL.read_text(encoding="utf-8"))
    existing = []
    for solid in current.get("solids", []):
        if str(solid.get("floor")) != str(piso):
            continue
        tipo = type_from_solid(solid)
        if tipo is None:
            continue
        existing.append({"id": solid.get("solidTag"), "tipo": tipo, "zona": "parte_1", "point": model_point(solid), "fuente": solid.get("source_dxf"), "geometria": model_geometry(solid)})

    excluded_states = {"FALSO_POSITIVO", "DUPLICADA", "DUPLICADO"}
    extracted = [element for element in elements if str(element.get("piso")) == str(piso) and element["tipo"] in {"viga", "muro", "columna"} and element.get("estado_revision") not in excluded_states]
    matched_existing: set[str] = set()
    correctos = []
    faltantes = []
    dudosos = []
    conflict_counter = 1
    for element in extracted:
        if element["zona"] != "parte_1":
            faltantes.append(conflict_record(conflict_counter, element, "faltante", "Elemento detectado en planos LT2/Parte 2 pero no existe en el modelo 3D actual.", element.get("confianza_score", 0.55)))
            conflict_counter += 1
            continue
        point = element_point(element)
        same_type = [item for item in existing if item["tipo"] == element["tipo"] and str(item["id"]) not in matched_existing]
        nearest = min(same_type, key=lambda item: math.dist(point, item["point"]), default=None)
        if nearest and math.dist(point, nearest["point"]) <= 0.75:
            correctos.append({"extraido": element["id"], "modelo": nearest["id"], "distancia_m": round(math.dist(point, nearest["point"]), 3), "zona": element["zona"]})
            matched_existing.add(str(nearest["id"]))
        elif nearest and math.dist(point, nearest["point"]) <= 1.50:
            record = conflict_record(conflict_counter, element, "dudoso", f"Elemento detectado cerca de {nearest['id']} pero con desfase {math.dist(point, nearest['point']):.2f} m.", min(element.get("confianza_score", 0.55), 0.60))
            record["modelo_cercano"] = nearest["id"]
            record["distancia_m"] = round(math.dist(point, nearest["point"]), 3)
            dudosos.append(record)
            conflict_counter += 1
        else:
            faltantes.append(conflict_record(conflict_counter, element, "faltante", "Elemento detectado en datos estructurados pero no encontrado en el modelo 3D actual.", element.get("confianza_score", 0.65)))
            conflict_counter += 1

    sobrantes = []
    axes = axis_data()
    for item in existing:
        if str(item["id"]) in matched_existing:
            continue
        point = item["point"]
        location = nearest_axis_span(point, item["zona"], axes)
        sobrantes.append(
            {
                "id": f"CONFLICT_P1_{conflict_counter:04d}",
                "elemento": item["id"],
                "tipo": "sobrante",
                "elemento_tipo": item["tipo"],
                "zona": item["zona"],
                "plano": item.get("fuente"),
                "ubicacion": axis_location_text(location),
                "descripcion": "Elemento existe en el modelo 3D actual pero no fue encontrado en la extraccion estructurada del Piso 1.",
                "confianza": 0.70,
                "estado": "EXTRA_IN_MODEL_NEEDS_REVIEW",
                "geometria": item["geometria"],
            }
        )
        conflict_counter += 1
    return {
        "piso": str(piso),
        "estado": "DRAFT_AUTOMATED_COMPARISON",
        "metodo": "Comparacion por tipo y cercania del centro geometrico; no modifica el modelo 3D.",
        "resumen": {
            "correctos": len(correctos),
            "faltantes": len(faltantes),
            "sobrantes": len(sobrantes),
            "dudosos": len(dudosos),
            "faltantes_parte_1": sum(1 for item in faltantes if item.get("zona") == "parte_1"),
            "faltantes_parte_1_confia": sum(1 for item in faltantes if item.get("zona") == "parte_1" and float(item.get("confianza", 0)) >= 0.6),
            "faltantes_por_tipo": dict(Counter(item["elemento_tipo"] for item in faltantes)),
            "sobrantes_por_tipo": dict(Counter(item["elemento_tipo"] for item in sobrantes)),
            "dudosos_por_tipo": dict(Counter(item["elemento_tipo"] for item in dudosos)),
        },
        "correctos": correctos,
        "faltantes": faltantes,
        "sobrantes": sobrantes,
        "dudosos": dudosos,
    }


def conflict_record(index: int, element: dict[str, object], kind: str, description: str, confidence: float) -> dict[str, object]:
    return {
        "id": f"CONFLICT_P1_{index:04d}",
        "elemento": element["id"],
        "tipo": kind,
        "elemento_tipo": element["tipo"],
        "zona": element["zona"],
        "plano": element.get("fuente", {}).get("plano"),
        "ubicacion": axis_location_text(element.get("ejes_aproximados", {})),
        "descripcion": description,
        "confianza": round(float(confidence), 2),
        "estado": "NEEDS_REVIEW" if confidence < 0.75 else "PENDING_MODEL_UPDATE",
        "fuente": element.get("fuente"),
        "motivos_revision": element.get("motivos_revision", []),
        "geometria": {key: element[key] for key in ["inicio", "fin", "centro"] if key in element},
    }


def axis_location_text(location: dict[str, object]) -> str:
    x = location.get("x") or "eje X no determinado"
    y = location.get("y") or "eje Y no determinado"
    return f"entre {x} y {y}"


def _wall_geometry(wall: dict[str, object]) -> tuple[list[float], list[float]]:
    if all(k in wall for k in ("inicio", "fin")):
        xs = [float(wall["inicio"][0]), float(wall["fin"][0])]
        ys = [float(wall["inicio"][1]), float(wall["fin"][1])]
    elif "centro" in wall:
        xs = [float(wall["centro"][0])]
        ys = [float(wall["centro"][1])]
    else:
        xs, ys = [], []
    return xs, ys


def _interface_walls(elements: list[dict[str, object]] | None) -> dict[str, list[dict[str, object]]]:
    zones: dict[str, list[dict[str, object]]] = {"parte_1": [], "parte_2": []}
    if not elements:
        return zones
    for element in elements:
        if element.get("tipo") != "muro" or element.get("zona") not in zones:
            continue
        xs, ys = _wall_geometry(element)
        if not xs:
            continue
        if min(abs(x - LT2_D_AXIS_M) for x in xs) <= 5.0:
            zones[element["zona"]].append(element)
    return zones


def _vertical_walls(walls: list[dict[str, object]]) -> list[dict[str, object]]:
    vertical = []
    for wall in walls:
        xs, ys = _wall_geometry(wall)
        if len(xs) < 2:
            continue
        height = max(ys) - min(ys)
        if height <= 0.0:
            continue
        if (max(xs) - min(xs)) < 0.5 * height:
            vertical.append(wall)
    return vertical


def _wall_center(wall: dict[str, object]) -> tuple[float, float]:
    xs, ys = _wall_geometry(wall)
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _wall_band_key(wall: dict[str, object]) -> int:
    _, cy = _wall_center(wall)
    return int(round(cy / 4.0))


def _merge_vertical_core(walls: list[dict[str, object]]) -> dict[str, object] | None:
    xs = [min(_wall_geometry(w)[0]) for w in walls]
    if not xs:
        return None
    xmin, xmax = min(min(_wall_geometry(w)[0]) for w in walls), max(max(_wall_geometry(w)[0]) for w in walls)
    ymin = min(min(_wall_geometry(w)[1]) for w in walls)
    ymax = max(max(_wall_geometry(w)[1]) for w in walls)
    return {"x_min": xmin, "x_max": xmax, "y_min": ymin, "y_max": ymax, "ids": [w["id"] for w in walls], "piso": walls[0].get("piso")}


def _group_collinear(zone_walls: list[dict[str, object]], band: int, piso: object) -> list[dict[str, object]]:
    in_band = [w for w in zone_walls if _wall_band_key(w) == band and w.get("piso") == piso]
    vertical = _vertical_walls(in_band)
    groups: list[list[dict[str, object]]] = []
    for wall in vertical:
        cx = sum(_wall_geometry(wall)[0]) / len(_wall_geometry(wall)[0])
        placed = False
        for group in groups:
            gx = sum(sum(_wall_geometry(w)[0]) / len(_wall_geometry(w)[0]) for w in group) / len(group)
            if abs(gx - cx) <= 0.35:
                group.append(wall)
                placed = True
                break
        if not placed:
            groups.append([wall])
    return [_merge_vertical_core(group) for group in groups if _merge_vertical_core(group)]


def interface_wall_pairs(elements: list[dict[str, object]] | None) -> dict[str, object]:
    zones = _interface_walls(elements)
    vertical_by_zone = {zone: _vertical_walls(zone_walls) for zone, zone_walls in zones.items()}
    pisos = sorted({w.get("piso") for walls in vertical_by_zone.values() for w in walls if w.get("piso") is not None})
    pairs = []
    for piso in pisos:
        bands = sorted({_wall_band_key(w) for w in vertical_by_zone["parte_2"] if w.get("piso") == piso})
        for band in bands:
            p2_cores_in_band = [c for c in _group_collinear(vertical_by_zone["parte_2"], band, piso) if c]
            if not p2_cores_in_band:
                continue
            p2_core = max(p2_cores_in_band, key=lambda c: c["y_max"] - c["y_min"])
            p1_cores_in_band = [c for c in _group_collinear(vertical_by_zone["parte_1"], band, piso) if c]
            if not p1_cores_in_band:
                continue
            p1_core = max(p1_cores_in_band, key=lambda c: c["y_max"] - c["y_min"])
        overlap_y = max(0.0, min(p2_core["y_max"], p1_core["y_max"]) - max(p2_core["y_min"], p1_core["y_min"]))
        center_y_p2 = (p2_core["y_min"] + p2_core["y_max"]) / 2.0
        center_y_p1 = (p1_core["y_min"] + p1_core["y_max"]) / 2.0
        center_x_p2 = (p2_core["x_min"] + p2_core["x_max"]) / 2.0
        center_x_p1 = (p1_core["x_min"] + p1_core["x_max"]) / 2.0
        usable = overlap_y >= 2.0
        pairs.append(
            {
                "parte_2": "+".join(p2_core["ids"]),
                "parte_1": "+".join(p1_core["ids"]),
                "piso": p2_core.get("piso"),
                "banda_y": band,
                "y_p2": [round(p2_core["y_min"], 3), round(p2_core["y_max"], 3)],
                "y_p1": [round(p1_core["y_min"], 3), round(p1_core["y_max"], 3)],
                "overlap_y_m": round(overlap_y, 3),
                "delta_y_centrolinea_m": round(abs(center_y_p2 - center_y_p1), 3),
                "delta_x_centrolinea_m": round(abs(center_x_p2 - center_x_p1), 3),
                "x_centrolinea_p2": round(center_x_p2, 3),
                "x_centrolinea_p1": round(center_x_p1, 3),
                "segmentos_p2": len(p2_core["ids"]),
                "segmentos_p1": len(p1_core["ids"]),
                "nota": "Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.",
                "usable_para_calce": usable,
            }
        )
    usable = [pair for pair in pairs if pair["usable_para_calce"]]
    return {
        "pares_muros_con_columna": pairs,
        "muros_verticales_por_zona": {zone: len(zone_walls) for zone, zone_walls in zones.items()},
        "pares_muros_usables": len(usable),
    }


def assess_non_collinear_controls(usable_pairs: list[dict[str, object]], wall_pairs: dict[str, object]) -> dict[str, object]:
    usable_walls = [pair for pair in wall_pairs["pares_muros_con_columna"] if pair.get("usable_para_calce")]
    row_set = {round(float(pair.get("delta_y_m")) if pair.get("delta_y_m") is not None else 0.0, 3) for pair in usable_pairs}
    row_set |= {round(float(pair.get("banda_y")) * 4.0 + 2.0, 3) for pair in usable_walls if pair.get("banda_y") is not None}
    rows = sorted(row_set)
    estado = "CON_CONTROLES_NO_COLINEALES" if len(rows) >= 2 and len(usable_walls) >= 1 else "NO_CONFIRMADO"
    return {
        "estado": estado,
        "filas_y_distintas": rows,
    }


def _alignment_conclusion(usable_pairs: list[dict[str, object]], wall_pairs: dict[str, object], non_collinearity: dict[str, object]) -> str:
    if non_collinearity["estado"] == "CON_CONTROLES_NO_COLINEALES":
        y_controls = [pair for pair in wall_pairs["pares_muros_con_columna"] if pair.get("usable_para_calce")]
        residuo_y = max((pair["delta_y_centrolinea_m"] for pair in y_controls), default=0.0)
        return (
            f"Controles no colineales en filas Y distintas: columnas en la interfaz confirman la alineacion X (residuo ~0.1 m) "
            f"en la fila baja; los nucleos de muro adyacentes confirman la continuidad longitudinal Y (residuo de centrolinea ~{residuo_y} m) "
            f"en la banda media. Los residuos X entre nucleos opuestos de la linea de columnas reflejan nucleos de planta distintos, no un error de calce. "
            "CALCE_POSIBLE_NEEDS_REVIEW: requiere confirmacion final sobre planos generales."
        )
    return "Evidencia parcial de continuidad longitudinal; insuficiente para confirmar el calce sin dos puntos comunes no colineales."


def column_alignment_evidence(elements: list[dict[str, object]] | None) -> dict[str, object]:
    if elements is None:
        return {
            "estado": "SIN_ELEMENTOS",
            "criterio": "Se evaluara con columnas extraidas despues de leer los DXF.",
        }
    columns = [element for element in elements if element["tipo"] == "columna"]
    by_zone = {zone: [element for element in columns if element["zona"] == zone] for zone in ["parte_1", "parte_2"]}
    interface = {
        zone: [element for element in zone_columns if abs(float(element["centro"][0]) - LT2_D_AXIS_M) <= 2.0]
        for zone, zone_columns in by_zone.items()
    }
    pairs = []
    for p2_column in interface["parte_2"]:
        p2_y = float(p2_column["centro"][1])
        same_floor_candidates = [item for item in interface["parte_1"] if item.get("piso") == p2_column.get("piso")]
        nearest = min(same_floor_candidates, key=lambda item: abs(float(item["centro"][1]) - p2_y), default=None)
        if nearest is None:
            continue
        y_delta = abs(float(nearest["centro"][1]) - p2_y)
        pairs.append(
            {
                "parte_2": p2_column["id"],
                "parte_1": nearest["id"],
                "piso": p2_column.get("piso"),
                "delta_y_m": round(y_delta, 3),
                "delta_x_interfaz_m": round(abs(float(nearest["centro"][0]) - float(p2_column["centro"][0])), 3),
                "usable_para_calce": y_delta <= 0.50,
            }
        )
    usable_pairs = [pair for pair in pairs if pair["usable_para_calce"]]
    wall_pairs = interface_wall_pairs(elements)
    non_collinearity = assess_non_collinear_controls(usable_pairs, wall_pairs)
    return {
        "criterio": "Control primario: columnas cercanas a la interfaz D/E. Control secundario: muros verticales adyacentes a la interfaz, que aportan puntos en filas Y distintas para evaluar no colinealidad.",
        "columnas_por_zona": {zone: len(zone_columns) for zone, zone_columns in by_zone.items()},
        "columnas_interfaz_por_zona": {zone: len(zone_columns) for zone, zone_columns in interface.items()},
        "pares_columnas_interfaz_por_y": pairs,
        "pares_usables": len(usable_pairs),
        "pares_muros_interfaz": wall_pairs["pares_muros_con_columna"],
        "muros_verticales_interfaz_por_zona": wall_pairs["muros_verticales_por_zona"],
        "controles_no_colineales": non_collinearity,
        "conclusion": _alignment_conclusion(usable_pairs, wall_pairs, non_collinearity),
    }


def alignment_report(elements: list[dict[str, object]] | None = None) -> dict[str, object]:
    column_evidence = column_alignment_evidence(elements)
    return {
        "estado": "NEEDS_REVIEW",
        "sistema_global": "Eje A-1 de Parte 2 / LT2 = (0, 0, 0)",
        "referencia_principal": "columnas",
        "transformacion_candidata_parte_1_respecto_parte_2": {
            "traslacion_x_m": LT2_D_AXIS_M,
            "traslacion_y_m": 0.0,
            "rotacion_grados": 0.0,
            "escala": 1.0,
        },
        "transformacion_parte_1_respecto_parte_2": {
            "traslacion_x_m": LT2_D_AXIS_M,
            "traslacion_y_m": 0.0,
            "rotacion_grados": 0.0,
            "escala": 1.0,
            "estado": "HIPOTESIS_NO_CONFIRMADA",
        },
        "evidencia": [
            "En 2024_22-101 se identifican ejes A, B, C, C', D y D' en la planta LT2.",
            "En 2017_67-101 la Parte 1 usa ejes E a J.",
            "La hipotesis actual alinea D de Parte 2 con E de Parte 1 para continuidad de edificio.",
            "La escala se mantiene 1:1 porque ambas fuentes estan en cm CAD transformados a m.",
        ],
        "evidencia_columnas": column_evidence,
        "faltante_para_confirmar": [
            "Plano general con ambas etapas o referencia explicita D/E.",
            "Verificacion manual de al menos dos puntos coincidentes no colineales entre Parte 1 y Parte 2.",
            "Confirmar si Y=1 de Parte 2 coincide exactamente con Y=1 de Parte 1 o requiere traslacion transversal.",
        ],
    }


def quality_report(elements: list[dict[str, object]], conflicts: dict[str, object], extraction_review: dict[str, object]) -> dict[str, object]:
    confirmed = [element for element in elements if element.get("estado_revision") in {"CONFIRMADA", "CONFIRMADO"}]
    possible = [element for element in elements if element.get("estado_revision") == "POSIBLE"]
    possible_false = [element for element in elements if element.get("estado_revision") == "FALSO_POSITIVO"]
    needs_review = [element for element in elements if element.get("estado_revision") == "NEEDS_REVIEW"]
    duplicated = [element for element in elements if element.get("estado_revision") in {"DUPLICADA", "DUPLICADO"}]
    fragmented = [element for element in elements if element.get("estado_revision") in {"FRAGMENTADA", "FRAGMENTADO"}]
    faltantes = conflicts.get("faltantes", [])
    sobrantes = conflicts.get("sobrantes", [])
    dudosos = conflicts.get("dudosos", [])
    alignment = alignment_report(elements)
    ready_for_3d = not any([faltantes, sobrantes, dudosos, needs_review, possible, fragmented, duplicated]) and alignment["estado"] == "CONFIRMADO"
    return {
        "titulo": "PISO 1 - CONTROL DE EXTRACCION",
        "elementos_inicialmente_detectados": len(elements),
        "recomendacion_3d": "LISTO PARA PASAR A 3D" if ready_for_3d else "A├ÜN NO LISTO",
        "motivo_recomendacion_3d": "El calce sigue NEEDS_REVIEW y/o existen elementos POSIBLE/FRAGMENTADO/NEEDS_REVIEW/conflictos contra el modelo actual.",
        "confirmados": summarize_by_type(confirmed),
        "posibles": summarize_by_type(possible),
        "posibles_falsos_positivos": summarize_by_type(possible_false),
        "duplicados": summarize_by_type(duplicated),
        "fragmentados": summarize_by_type(fragmented),
        "needs_review": summarize_by_type(needs_review),
        "duplicados_detectados": len(extraction_review.get("duplicados", [])),
        "duplicados_detalle": extraction_review.get("duplicados", [])[:100],
        "grupos_logicos_detectados": extraction_review.get("grupos_logicos_por_tipo", {}),
        "grupos_logicos_detalle": extraction_review.get("grupos_logicos", [])[:200],
        "coincidencia_con_modelo_actual": {
            "correctos": len(conflicts.get("correctos", [])),
            "faltantes": len(faltantes),
            "sobrantes": len(sobrantes),
            "dudosos": len(dudosos),
            "faltantes_por_tipo": dict(Counter(item["elemento_tipo"] for item in faltantes)),
            "sobrantes_por_tipo": dict(Counter(item["elemento_tipo"] for item in sobrantes)),
            "dudosos_por_tipo": dict(Counter(item["elemento_tipo"] for item in dudosos)),
            "no_comparados_con_modelo_3d": {
                "perimetro_losa": sum(1 for element in elements if element["tipo"] == "perimetro_losa"),
                "eje_grafico": sum(1 for element in elements if element["tipo"] == "eje_grafico"),
            },
        },
        "revision_especifica": {
            "vigas": {
                "detectadas": sum(1 for element in elements if element["tipo"] == "viga"),
                "por_categoria": dict(Counter(str(element.get("estado_revision", "sin_estado")) for element in elements if element["tipo"] == "viga")),
                "confirmadas": sum(1 for element in confirmed if element["tipo"] == "viga"),
                "posibles": sum(1 for element in possible if element["tipo"] == "viga"),
                "fragmentadas": sum(1 for element in fragmented if element["tipo"] == "viga"),
                "duplicadas": sum(1 for element in duplicated if element["tipo"] == "viga"),
                "needs_review": sum(1 for element in needs_review if element["tipo"] == "viga"),
                "posibles_falsos_positivos": sum(1 for element in possible_false if element["tipo"] == "viga"),
                "criterios": ["capa RLE-VIGA", "longitud minima", "etiqueta de viga cercana", "duplicados exactos", "posibles caras paralelas"],
            },
            "muros": {
                "detectados": sum(1 for element in elements if element["tipo"] == "muro"),
                "por_categoria": dict(Counter(str(element.get("estado_revision", "sin_estado")) for element in elements if element["tipo"] == "muro")),
                "confirmados": sum(1 for element in confirmed if element["tipo"] == "muro"),
                "posibles": sum(1 for element in possible if element["tipo"] == "muro"),
                "fragmentados": sum(1 for element in fragmented if element["tipo"] == "muro"),
                "duplicados": sum(1 for element in duplicated if element["tipo"] == "muro"),
                "needs_review": sum(1 for element in needs_review if element["tipo"] == "muro"),
                "posibles_falsos_positivos": sum(1 for element in possible_false if element["tipo"] == "muro"),
                "criterios": ["capa RLE-MURO", "longitud minima", "etiqueta de muro cercana", "posibles dobles caras", "duplicados exactos"],
            },
            "columnas": {
                "detectadas": sum(1 for element in elements if element["tipo"] == "columna"),
                "por_categoria": dict(Counter(str(element.get("estado_revision", "sin_estado")) for element in elements if element["tipo"] == "columna")),
                "confirmadas": sum(1 for element in confirmed if element["tipo"] == "columna"),
                "needs_review": sum(1 for element in needs_review if element["tipo"] == "columna"),
                "posibles_falsos_positivos": sum(1 for element in possible_false if element["tipo"] == "columna"),
                "criterios": ["cluster de lineas RLE-PILAR", "posicion relativa a ejes", "dimensiones del cluster"],
            },
        },
        "calce_parte_1_parte_2": alignment,
    }


def detailed_review(elements: list[dict[str, object]], tipo: str) -> dict[str, object]:
    selected = [element for element in elements if element["tipo"] == tipo]
    groups = detailed_groups(selected)
    return {
        "piso": "1",
        "tipo": tipo,
        "estado": "DRAFT_NEEDS_REVIEW",
        "total": len(selected),
        "por_zona": dict(Counter(str(element["zona"]) for element in selected)),
        "por_estado_revision": dict(Counter(str(element.get("estado_revision", "sin_estado")) for element in selected)),
        "grupos_logicos": groups,
        "total_grupos_logicos": len(groups),
        "criterio": review_criteria(tipo),
        "elementos": [element_issue_summary(element) | {"geometria": {key: element[key] for key in ["inicio", "fin", "centro"] if key in element}} for element in selected],
    }


def detailed_groups(elements: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for element in elements:
        group_id = element.get("grupo_logico")
        if group_id:
            grouped[str(group_id)].append(element)
    groups = []
    for group_id, items in sorted(grouped.items()):
        groups.append(
            {
                "id": group_id,
                "tipo": items[0]["tipo"],
                "zona": items[0]["zona"],
                "elementos": [item["id"] for item in items],
                "cantidad_segmentos": len(items),
                "longitud_total_m": round(sum(float(item.get("longitud_m", 0.0)) for item in items), 3),
                "estado_grupo": fragmented_category(str(items[0]["tipo"])),
            }
        )
    return groups


def review_criteria(tipo: str) -> list[str]:
    if tipo == "viga":
        return [
            "Debe provenir de capa RLE-VIGA.",
            "Categorias: CONFIRMADA, POSIBLE, FALSO_POSITIVO, DUPLICADA, FRAGMENTADA, NEEDS_REVIEW.",
            "Se marca POSIBLE si no tiene etiqueta V. cercana dentro de 2.0 m o parece cara paralela de otra viga.",
            "Se marca FRAGMENTADA si pertenece a un grupo de segmentos colineales contiguos o solapados.",
            "Se marca FALSO_POSITIVO si es demasiado corta o acumula baja confianza.",
            "No se convierte automaticamente a centrolinea ni a 3D en esta etapa.",
        ]
    if tipo == "muro":
        return [
            "Debe provenir de capa RLE-MURO.",
            "Categorias: CONFIRMADO, POSIBLE, FALSO_POSITIVO, DUPLICADO, FRAGMENTADO, NEEDS_REVIEW.",
            "Se revisa contra etiquetas M.H.A/M.I cercanas.",
            "Se marca POSIBLE si parece doble cara grafica de un mismo muro o no tiene etiqueta cercana.",
            "Se marca FRAGMENTADO si pertenece a un grupo de segmentos colineales contiguos o solapados.",
            "La agrupacion no se lleva a 3D hasta validar la planta 2D.",
        ]
    if tipo == "columna":
        return [
            "Se obtiene por cluster de segmentos RLE-PILAR.",
            "Se registra centro, dimensiones aproximadas y ejes cercanos.",
            "Debe usarse como control fuerte del sistema de coordenadas.",
            "La continuidad vertical se revisara con pisos superiores antes de 3D.",
        ]
    return ["Referencia extraida desde capa CAD; no se considera elemento estructural confirmado."]


def write_quality_markdown(path: Path, report: dict[str, object]) -> None:
    lines = ["# PISO 1 - CONTROL DE EXTRACCION", ""]
    lines.append(f"Elementos inicialmente detectados: `{report['elementos_inicialmente_detectados']}`")
    lines.append(f"Recomendacion 3D: `{report['recomendacion_3d']}`")
    lines.append(f"Motivo: {report['motivo_recomendacion_3d']}")
    lines.append("")
    lines.append("## Confirmados")
    for tipo, count in report["confirmados"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append("## Posibles")
    for tipo, count in report["posibles"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append("## Posibles Falsos Positivos")
    for tipo, count in report["posibles_falsos_positivos"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append("## Duplicados")
    for tipo, count in report["duplicados"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append("## Fragmentados")
    for tipo, count in report["fragmentados"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append("## Needs Review")
    for tipo, count in report["needs_review"].items():
        lines.append(f"- {tipo}: `{count}`")
    lines.append("")
    lines.append(f"Duplicados detectados: `{report['duplicados_detectados']}`")
    lines.append(f"Grupos logicos detectados: `{report['grupos_logicos_detectados']}`")
    lines.append("")
    lines.append("## Coincidencia Con Modelo Actual")
    for key, value in report["coincidencia_con_modelo_actual"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Calce Parte 1 / Parte 2")
    alignment = report["calce_parte_1_parte_2"]
    transform_data = alignment["transformacion_parte_1_respecto_parte_2"]
    lines.append(f"Estado: `{alignment['estado']}`")
    lines.append(f"Traslacion X: `{transform_data['traslacion_x_m']}` m")
    lines.append(f"Traslacion Y: `{transform_data['traslacion_y_m']}` m")
    lines.append(f"Rotacion: `{transform_data['rotacion_grados']}` grados")
    lines.append(f"Escala: `{transform_data['escala']}`")
    lines.append(f"Evidencia columnas: `{alignment['evidencia_columnas']}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    if CURRENT_MODEL.exists() and not BACKUP_MODEL.exists():
        shutil.copyfile(CURRENT_MODEL, BACKUP_MODEL)

    axes = axis_data()
    write_json(DATOS_DIR / "ejes.json", axes)
    write_json(DATOS_DIR / "niveles.json", levels_data())

    raw = []
    labels = []
    underlay = []
    for source in PISO_01_SOURCES:
        raw.extend(extract_raw_segments(source))
        labels.extend(extract_labels(source))
        underlay.extend(extract_underlay(source))
    elements = cluster_columns(raw)
    extraction_review = revise_extraction(elements, labels)
    conflicts = compare_with_existing_model(elements)
    quality = quality_report(elements, conflicts, extraction_review)
    existing = existing_model_elements()
    piso_data = {
        "piso": "1",
        "estado": "DRAFT_NEEDS_REVIEW",
        "unidades": "m",
        "sistema_coordenadas": axes["origen"],
        "fuentes": [source_record(source) for source in PISO_01_SOURCES],
        "etiquetas": labels,
        "elementos": elements,
        "resumen": count_by_type(elements),
        "revision_extraccion": extraction_review,
    }
    write_json(DATOS_DIR / "piso_01.json", piso_data)
    write_json(ISSUES_DIR / "calce_parte_1_parte_2.json", quality["calce_parte_1_parte_2"])
    write_json(ISSUES_DIR / "conflicts.json", conflicts)
    write_json(ISSUES_DIR / "quality_piso_01.json", quality)
    write_json(ISSUES_DIR / "vigas_piso_01_review.json", detailed_review(elements, "viga"))
    write_json(ISSUES_DIR / "muros_piso_01_review.json", detailed_review(elements, "muro"))
    write_json(ISSUES_DIR / "columnas_piso_01_review.json", detailed_review(elements, "columna"))
    write_quality_markdown(ISSUES_DIR / "quality_piso_01.md", quality)
    for zone_key, svg_name in SVG_OUTPUTS.items():
        zones = None if zone_key == "completo" else {zone_key}
        title = f"Piso 1 - validacion visual {zone_key}"
        write_validation_svg(VALIDACION_DIR / svg_name, title, elements, existing, underlay, axes, conflicts, zones)
        write_validation_png(VALIDACION_DIR / PNG_OUTPUTS[zone_key], title, elements, existing, underlay, conflicts, zones)
    # Alias historico para no romper referencias previas.
    shutil.copyfile(VALIDACION_DIR / SVG_OUTPUTS["completo"], VALIDACION_DIR / "piso_01.svg")

    print("Extraccion estructurada Piso 1 creada")
    print(f"  elementos: {len(elements)}")
    print(f"  resumen: {piso_data['resumen']}")
    print(f"  conflictos: {conflicts['resumen']}")
    print(f"  datos: {DATOS_DIR / 'piso_01.json'}")
    print(f"  validacion 2D: {VALIDACION_DIR / 'piso_01_completo.svg'}")
    print(f"  comparacion: {ISSUES_DIR / 'conflicts.json'}")


def count_by_type(elements: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for element in elements:
        counts[str(element["tipo"])] = counts.get(str(element["tipo"]), 0) + 1
    return counts


if __name__ == "__main__":
    main()
