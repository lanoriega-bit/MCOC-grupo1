#!/usr/bin/env python3
"""Audita el calce espacial de las zonas de carga de las laminas 700.

Este script NO calcula ni aplica Q. Reconstruye la transformacion desde cada
planta insertada en la lamina 700 hasta el sistema combinado confirmado,
intersecta geometricamente zonas SC con los panos existentes y deja toda
contribucion mecanica en estado DEFERRED_UNTIL_USER_APPROVAL.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import ezdxf.path
import matplotlib
import numpy as np
from ezdxf import bbox
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon, mapping, shape
from shapely.ops import transform as transform_geometry
from shapely.ops import unary_union

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from shapely.plotting import plot_polygon  # noqa: E402


HERE = Path(__file__).resolve().parent
P1L3 = HERE.parent
REPO = P1L3.parents[1]
DXF_ROOT = REPO / "recursos" / "planos" / "dxf_full"
AXES_PATH = REPO / "entregas" / "P1L2" / "edificio" / "datos" / "global_axes.json"
CALCE_PATH = REPO / "entregas" / "P1L2" / "edificio" / "datos" / "axis_calce_validation.json"
PANELS_PATH = P1L3 / "results" / "a1a2" / "panos.json"
MODEL_PATH = REPO / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
OUT_DIR = P1L3 / "results" / "a1a2" / "load_zones_700_alignment"
OUT_JSON = OUT_DIR / "spatial_audit.json"
OUT_MD = OUT_DIR / "REPORT.md"

KGF_TO_KN = 9.80665 / 1000.0
AREA_TOL_M2 = 1e-6
CONTROL_TOL_M = 0.001


@dataclass(frozen=True)
class FloorSpec:
    floor: str
    block_name: str
    insert_xy: tuple[float, float]
    source_origin_xy: tuple[float, float]
    viewport: tuple[float, float, float, float]
    source_floor_title: str
    source_sheet: str
    patterns: dict[str, tuple[float, float, str]]


SURFACE_PATTERNS = {
    "S1": {
        "_USER": (500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
        "AR-HBONE": (300, 260, "SC=300; PM.ADIC=260 kgf/m2"),
        "ANGLE": (250, 260, "SC=250; PM.ADIC=260 kgf/m2"),
        "HONEY": (500, 300, "SC=500; PM.ADIC=300 kgf/m2"),
        "AR-CONC": (500, 300, "SC=500; PM.ADIC=300 kgf/m2"),
    },
    "P1": {
        "GRAVEL": (200, 200, "SC=200; PM.ADIC=200 kgf/m2"),
        "ANGLE": (250, 260, "SC=250; PM.ADIC=260 kgf/m2"),
        "_USER": (500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
        "AR-HBONE": (300, 260, "SC=300; PM.ADIC=260 kgf/m2"),
        "ANSI34": (400, 260, "SC=400; PM.ADIC=260 kgf/m2"),
        "BRASS": (500, 2800, "SC=500; PM.ADIC=2800; unidad superficial por confirmar"),
    },
    "P2": {
        "GRAVEL": (200, 200, "SC=200; PM.ADIC=200 kgf/m2"),
        "ANGLE": (250, 260, "SC=250; PM.ADIC=260 kgf/m2"),
        "_USER": (500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
        "AR-HBONE": (300, 260, "SC=300; PM.ADIC=260 kgf/m2"),
        "ANSI34": (400, 260, "SC=400; PM.ADIC=260 kgf/m2"),
    },
    "P3": {
        "GRAVEL": (200, 200, "SC=200; PM.ADIC=200 kgf/m2"),
        "ANGLE": (250, 260, "SC=250; PM.ADIC=260 kgf/m2"),
        "_USER": (500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
        "AR-HBONE": (300, 260, "SC=300; PM.ADIC=260 kgf/m2"),
    },
    "P4": {
        "_USER": (100, 350, "SC=100; PM.ADIC=350 kgf/m2"),
        "GRAVEL": (200, 200, "SC=200; PM.ADIC=200 kgf/m2"),
        "BRASS": (800, 7600, "CARGAS DE DISEÑO (CARGA LINEAL): SC=800; PM.ADIC=7600 kgf/m"),
    },
}


FLOORS = (
    FloorSpec("S1", "2017_67-101", (-2255.295399857105, 670.840836560862), (1061.32, 7183.28), (-1300, 1000, 6100, 9000), "PLANTA CIELO 1° SUBTERRANEO", "2017_67-700", SURFACE_PATTERNS["S1"]),
    FloorSpec("P1", "2017_67-101", (2209.813741090573, 4607.85282741067), (1061.32, 3558.02), (3200, 7900, 5200, 9300), "PLANTA CIELO PISO 1°", "2017_67-700", SURFACE_PATTERNS["P1"]),
    FloorSpec("P2", "2017_67-102", (8412.405680405014, 978.9262132984513), (893.24, 7903.06), (9200, 13900, 6800, 9100), "PLANTA CIELO PISO 2°", "2017_67-700", SURFACE_PATTERNS["P2"]),
    FloorSpec("P3", "2017_67-102", (8543.584636270043, -1576.397983484503), (534.98, 4278.48), (9000, 14200, 600, 2800), "PLANTA CIELO PISO 3°", "2017_67-700", SURFACE_PATTERNS["P3"]),
    FloorSpec("P4", "2017_67-103", (-2380.173863817861, -4389.168763025671), (490.34, 6297.31), (-2000, 3300, -200, 2100), "PLANTA CIELO PISO 4°", "2017_67-700", SURFACE_PATTERNS["P4"]),
)

COLORS = {
    100: "#4cc9f0",
    200: "#43aa8b",
    250: "#577590",
    300: "#f9c74f",
    400: "#f8961e",
    500: "#f94144",
    800: "#9d4edd",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hatch_geometry(hatch) -> Polygon | MultiPolygon | GeometryCollection:
    external: list[Polygon] = []
    holes: list[Polygon] = []
    for boundary, path in zip(hatch.paths, ezdxf.path.from_hatch(hatch)):
        vertices = [(vertex.x, vertex.y) for vertex in path.flattening(0.25)]
        if len(vertices) < 3:
            continue
        polygon = Polygon(vertices)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            continue
        if boundary.path_type_flags & 1:
            external.append(polygon)
        else:
            holes.append(polygon)
    geometry = unary_union(external)
    if holes and not geometry.is_empty:
        geometry = geometry.difference(unary_union(holes))
    return geometry


def in_viewport(entity, bounds: tuple[float, float, float, float]) -> bool:
    extents = bbox.extents([entity])
    center = extents.center
    xmin, xmax, ymin, ymax = bounds
    return xmin <= center.x <= xmax and ymin <= center.y <= ymax


def sheet_to_global(spec: FloorSpec, dx_m: float, dy_m: float, x: float, y: float) -> tuple[float, float]:
    """Transforma coordenada de lamina 700 al sistema combinado.

    Los planos fuente trabajan en centimetros y su Y CAD crece en sentido
    opuesto al Y canonico. La insercion xref es 1:1, sin rotacion.
    """
    source_x = x - spec.insert_xy[0]
    source_y = y - spec.insert_xy[1]
    return (
        dx_m + (source_x - spec.source_origin_xy[0]) / 100.0,
        dy_m + (spec.source_origin_xy[1] - source_y) / 100.0,
    )


def transform_shape(geometry, spec: FloorSpec, dx_m: float, dy_m: float):
    return transform_geometry(lambda x, y, z=None: sheet_to_global(spec, dx_m, dy_m, x, y), geometry)


def control_audit(spec: FloorSpec, axes: dict, dx_m: float, dy_m: float) -> dict:
    x_axes = axes["buildings"]["EDIFICIO_1"]["axes"]["X"]
    y_axes = axes["buildings"]["EDIFICIO_1"]["axes"]["Y"]
    names = (("E", "1"), ("H", "2"), ("J", "3"), ("F", "3"), ("I", "1"), ("G", "2a"))
    controls = []
    for x_name, y_name in names:
        x_local = float(x_axes[x_name])
        y_local = float(y_axes[y_name])
        sheet_x = spec.insert_xy[0] + spec.source_origin_xy[0] + 100.0 * x_local
        sheet_y = spec.insert_xy[1] + spec.source_origin_xy[1] - 100.0 * y_local
        expected = (dx_m + x_local, dy_m + y_local)
        calculated = sheet_to_global(spec, dx_m, dy_m, sheet_x, sheet_y)
        residual = math.dist(expected, calculated)
        controls.append({
            "axis_intersection": f"{x_name}/{y_name}",
            "sheet_xy": [round(sheet_x, 6), round(sheet_y, 6)],
            "expected_global_xy_m": [round(v, 6) for v in expected],
            "calculated_global_xy_m": [round(v, 6) for v in calculated],
            "residual_m": residual,
            "role": "FIT" if len(controls) < 3 else "INDEPENDENT_CHECK",
        })

    source = np.array([[*row["sheet_xy"], 1.0] for row in controls[:3]], dtype=float)
    target = np.array([row["expected_global_xy_m"] for row in controls[:3]], dtype=float)
    coefficients, *_ = np.linalg.lstsq(source, target, rcond=None)
    affine = coefficients.T
    predicted = source @ coefficients
    fit_residual = np.linalg.norm(predicted - target, axis=1)
    max_residual = max(row["residual_m"] for row in controls)
    return {
        "status": "CONFIRMED" if max_residual <= CONTROL_TOL_M else "FAIL",
        "source_sheet": spec.source_sheet,
        "source_xref": {
            "block": spec.block_name,
            "insert_xy": list(spec.insert_xy),
            "scale_xy": [1.0, 1.0],
            "rotation_deg": 0.0,
        },
        "transform": {
            "affine_matrix": [[round(float(v), 12) for v in row] for row in affine],
            "scale_m_per_drawing_unit": 0.01,
            "rotation_deg": 0.0,
            "mirror_y": True,
            "translation_xy_m": [round(float(affine[0, 2]), 9), round(float(affine[1, 2]), 9)],
            "determinant": round(float(np.linalg.det(affine[:, :2])), 12),
        },
        "controls": controls,
        "fit_max_residual_m": float(max(fit_residual)),
        "validation_max_residual_m": max_residual,
        "tolerance_m": CONTROL_TOL_M,
        "evidence": "xref 101/102/103 insertado 1:1 sin giro + origen de ejes de global_axes.json + CALCE_A confirmado",
    }


def panel_geometry(panel: dict) -> Polygon:
    return Polygon(panel["vertices"])


def nearest_receiver(model: dict, floor: str, geometry, allowed_categories: set[str] | None = None) -> dict:
    allowed = allowed_categories or {"beam", "wall", "column"}
    candidates = []
    for solid in model["solids"]:
        if solid.get("building") != "EDIFICIO_1" or solid.get("floor") != floor:
            continue
        if solid.get("category") not in allowed:
            continue
        if solid.get("start") and solid.get("end"):
            receiver_geometry = LineString([solid["start"][:2], solid["end"][:2]])
        elif solid.get("center"):
            receiver_geometry = Point(solid["center"][:2])
        elif solid.get("coordinates", {}).get("center"):
            receiver_geometry = Point(solid["coordinates"]["center"][:2])
        else:
            continue
        candidates.append((geometry.distance(receiver_geometry), solid))
    if not candidates:
        return {"status": "UNRESOLVED", "reason": "sin receptores geometricos"}
    distance, solid = min(candidates, key=lambda row: row[0])
    if distance > 0.50:
        return {
            "status": "UNRESOLVED",
            "element_id": None,
            "distance_m": round(float(distance), 6),
            "nearest_candidate_id": solid.get("id") or solid.get("solidTag"),
            "nearest_candidate_category": solid.get("category"),
            "confidence": "REVIEW_REQUIRED",
            "reason": "la anotacion esta demasiado lejos de un receptor para inferir aplicacion",
        }
    return {
        "status": "CANDIDATE_ONLY",
        "element_id": solid.get("id") or solid.get("solidTag"),
        "category": solid.get("category"),
        "distance_m": round(float(distance), 6),
        "confidence": "REVIEW_REQUIRED",
        "reason": "proximidad geometrica; la anotacion no contiene lider o punto de aplicacion inequívoco",
    }


def text_value(entity) -> str:
    return (entity.dxf.text if entity.dxftype() == "TEXT" else entity.text).replace("\\P", " ").strip()


def special_point_loads(modelspace, specs: dict[str, FloorSpec], dx_m: float, dy_m: float, model: dict) -> list[dict]:
    wanted = {7000: ("P2", 13000), 6000: ("P3", 10000), 6700: ("P3", 13000)}
    out = []
    for entity in modelspace.query("TEXT MTEXT"):
        text = text_value(entity)
        match = re.search(r"SC\s*=\s*(7000|6000|6700)\s*Kg", text, re.IGNORECASE)
        if not match:
            continue
        sc = int(match.group(1))
        floor, pm = wanted[sc]
        spec = specs[floor]
        point_sheet = (float(entity.dxf.insert.x), float(entity.dxf.insert.y))
        point_global = sheet_to_global(spec, dx_m, dy_m, *point_sheet)
        receiver = nearest_receiver(model, floor, Point(point_global))
        out.append({
            "load_id": f"L700-{floor}-POINT-SC-{sc}",
            "zone_id": None,
            "building": "EDIFICIO_1",
            "source_sheet": "2017_67-700",
            "source_floor": spec.source_floor_title,
            "analysis_floor": floor,
            "load_type": "POINT",
            "components": [
                {"load_type": "SC", "value_original": sc, "unit_original": "kgf", "value_SI": sc * KGF_TO_KN, "unit_SI": "kN"},
                {"load_type": "PM_ADIC", "value_original": pm, "unit_original": "kgf", "value_SI": pm * KGF_TO_KN, "unit_SI": "kN"},
            ],
            "annotation_insert_sheet_xy": list(point_sheet),
            "annotation_insert_global_xy_m": [round(v, 6) for v in point_global],
            "application_position": None,
            "position_status": "REVIEW_REQUIRED_NO_EXPLICIT_LEADER",
            "receiver": receiver,
            "source_text": f"SC={sc} kgf; PM.ADIC={pm} kgf",
            "confidence": "REVIEW_REQUIRED",
            "application_status": "NOT_APPLIED",
        })
    return sorted(out, key=lambda row: (row["analysis_floor"], row["components"][0]["value_original"]))


def principal_centerline(geometry) -> LineString:
    rectangle = geometry.minimum_rotated_rectangle
    coords = list(rectangle.exterior.coords)[:-1]
    edges = [(coords[i], coords[(i + 1) % 4]) for i in range(4)]
    lengths = [math.dist(*edge) for edge in edges]
    short_indices = sorted(range(4), key=lambda i: lengths[i])[:2]
    short_edges = [edges[i] for i in short_indices]
    mids = [((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0) for a, b in short_edges]
    return LineString(mids)


def coverage_for_floor(panels: list[dict], sc_zones: list[dict], review_zones: list[dict]) -> tuple[dict, list[dict], object, object, object]:
    panel_union = unary_union([panel_geometry(panel) for panel in panels])
    confirmed_geometries = [shape(zone["polygon"]) for zone in sc_zones]
    review_geometries = [shape(zone["polygon"]) for zone in review_zones]
    confirmed_union = unary_union(confirmed_geometries) if confirmed_geometries else GeometryCollection()
    review_union = unary_union(review_geometries) if review_geometries else GeometryCollection()
    all_union = unary_union([confirmed_union, review_union])
    confirmed_in_panels = panel_union.intersection(confirmed_union)
    review_in_panels = panel_union.intersection(review_union).difference(confirmed_union)
    unmapped = panel_union.difference(all_union)

    pairwise_overlap = GeometryCollection()
    all_geometries = confirmed_geometries + review_geometries
    overlaps = []
    for i, first in enumerate(all_geometries):
        for second in all_geometries[i + 1:]:
            intersection = first.intersection(second)
            if intersection.area > AREA_TOL_M2:
                overlaps.append(intersection)
    if overlaps:
        pairwise_overlap = unary_union(overlaps).intersection(panel_union)

    contributions = []
    for panel in panels:
        geometry = panel_geometry(panel)
        rows = []
        for zone in sc_zones + review_zones:
            area = geometry.intersection(shape(zone["polygon"])).area
            if area <= AREA_TOL_M2:
                continue
            rows.append({
                "zone_id": zone["zone_id"],
                "intersection_area_m2": round(area, 6),
                "q_SC_kN_m2": zone["value_SI"],
                "Q_contribution_kN": None,
                "calculation_status": "DEFERRED_UNTIL_USER_APPROVAL",
                "confidence": zone["confidence"],
            })
        contributions.append({
            "pano_id": panel["id"],
            "area_m2": panel["area_m2"],
            "zone_contributions": rows,
            "crosses_multiple_zones": len(rows) > 1,
            "mapped_area_m2": round(sum(row["intersection_area_m2"] for row in rows), 6),
            "unmapped_area_m2": round(geometry.difference(all_union).area, 6),
            "Q_total_kN": None,
            "Q_status": "DEFERRED_UNTIL_USER_APPROVAL",
        })

    total_area = panel_union.area
    summary = {
        "panel_count": len(panels),
        "panel_area_m2": round(total_area, 6),
        "confirmed_area_m2": round(confirmed_in_panels.area, 6),
        "confirmed_percent": round(100.0 * confirmed_in_panels.area / total_area, 4) if total_area else 0.0,
        "review_required_area_m2": round(review_in_panels.area, 6),
        "review_required_percent": round(100.0 * review_in_panels.area / total_area, 4) if total_area else 0.0,
        "unmapped_area_m2": round(unmapped.area, 6),
        "unmapped_percent": round(100.0 * unmapped.area / total_area, 4) if total_area else 0.0,
        "overlap_area_m2": round(pairwise_overlap.area, 6),
        "overlap_percent": round(100.0 * pairwise_overlap.area / total_area, 4) if total_area else 0.0,
        "multi_zone_panel_count": sum(row["crosses_multiple_zones"] for row in contributions),
        "multi_zone_panel_ids": [row["pano_id"] for row in contributions if row["crosses_multiple_zones"]],
    }
    return summary, contributions, confirmed_union, review_union, unmapped


def draw_overlay(floor: str, panels: list[dict], zones: list[dict], review_zones: list[dict], axes: dict, unmapped, points: list[dict], line_loads: list[dict]) -> Path:
    fig, ax = plt.subplots(figsize=(15, 7.5), constrained_layout=True)
    for zone in zones:
        geometry = shape(zone["polygon"])
        plot_polygon(geometry, ax=ax, add_points=False, facecolor=COLORS[int(zone["value_original"])], edgecolor="#222", alpha=0.50, linewidth=0.8)
        anchor = geometry.representative_point()
        ax.text(anchor.x, anchor.y, f"{zone['value_original']:.0f}", fontsize=7, ha="center", va="center", color="#111")
    for zone in review_zones:
        geometry = shape(zone["polygon"])
        plot_polygon(geometry, ax=ax, add_points=False, facecolor="#ff00aa", edgecolor="#65003f", alpha=0.50, linewidth=1.2, hatch="///")
        anchor = geometry.representative_point()
        ax.text(anchor.x, anchor.y, "500?", fontsize=7, ha="center", va="center")
    if not unmapped.is_empty:
        if unmapped.geom_type == "Polygon":
            plot_polygon(unmapped, ax=ax, add_points=False, facecolor="#d9d9d9", edgecolor="#555", alpha=0.65, hatch="xx")
        elif unmapped.geom_type == "MultiPolygon":
            for polygon in unmapped.geoms:
                plot_polygon(polygon, ax=ax, add_points=False, facecolor="#d9d9d9", edgecolor="#555", alpha=0.65, hatch="xx")
    for panel in panels:
        geometry = panel_geometry(panel)
        x, y = geometry.exterior.xy
        ax.plot(x, y, color="#0057b8", linewidth=1.35)
        anchor = geometry.representative_point()
        ax.text(anchor.x, anchor.y, panel["id"].split("-")[-1], fontsize=5.5, color="#003b7a")

    building_axes = axes["buildings"]["EDIFICIO_1"]["axes"]
    for name, value in building_axes["X"].items():
        x = float(value) + 27.491
        ax.axvline(x, color="#555", linewidth=0.45, linestyle="--", alpha=0.6)
        ax.text(x, ax.get_ylim()[1] if ax.get_ylim()[1] else 0, name, fontsize=6, ha="center", va="bottom")
    for name, value in building_axes["Y"].items():
        y = float(value)
        ax.axhline(y, color="#555", linewidth=0.45, linestyle="--", alpha=0.6)
        ax.text(ax.get_xlim()[0], y, name, fontsize=6, ha="right", va="center")

    for point_load in points:
        x, y = point_load["annotation_insert_global_xy_m"]
        value = point_load["components"][0]["value_original"]
        ax.scatter([x], [y], marker="x", s=55, color="#7209b7", zorder=7)
        ax.annotate(f"SC {value} kgf\nanotacion", (x, y), xytext=(5, 5), textcoords="offset points", fontsize=7, color="#7209b7")
    for line_load in line_loads:
        centerline = shape(line_load["centerline_candidate"])
        x, y = centerline.xy
        ax.plot(x, y, color="#7209b7", linewidth=3.0, linestyle="-.", label="linea candidata")

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.25, alpha=0.35)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    ax.set_title(f"EDIFICIO_1 {floor} — zonas SC confirmadas sobre paños actuales\nNo aplicado a Q/OpenSees/Unity")
    handles = [Patch(facecolor=COLORS[value], alpha=0.5, label=f"SC {value} kgf/m²") for value in sorted({int(z["value_original"]) for z in zones})]
    handles.extend([
        Patch(facecolor="#ff00aa", hatch="///", alpha=0.5, label="REVIEW_REQUIRED"),
        Patch(facecolor="#d9d9d9", hatch="xx", alpha=0.65, label="UNMAPPED"),
        Patch(facecolor="none", edgecolor="#0057b8", label="Paños actuales"),
    ])
    ax.legend(handles=handles, loc="upper left", fontsize=7, ncol=2)
    out = OUT_DIR / f"overlay_EDIFICIO_1_{floor}.png"
    fig.savefig(out, dpi=190)
    plt.close(fig)
    return out


def write_report(payload: dict) -> None:
    lines = [
        "# Auditoría espacial de zonas de carga — lámina 2017_67-700",
        "",
        "> Estado: transformación confirmada; cargas no aplicadas. El caso uniforme vigente se conserva como `LEGACY_UNIFORM_Q_VALIDATION`.",
        "",
        "## Alcance y decisión",
        "",
        "La lámina contiene **seis** intensidades superficiales SC distintas: 100, 200, 250, 300, 400 y 500 kgf/m². El calce usa los xrefs estructurales 101/102/103 insertados 1:1 en la lámina 700 y el sistema canónico de `global_axes.json`; no recalibra el edificio.",
        "",
        "La convención del CAD exige `scale=0.01`, `rotation=0°` y `mirror_y=true`. Luego se aplica el calce global confirmado de EDIFICIO_1: `dx=27.491 m`, `dy=0`.",
        "",
        "## Transformaciones y correspondencia de niveles",
        "",
        "| Planta fuente | Nivel analítico | Xref | Residual máximo [m] | Estado |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for floor in payload["floors"]:
        t = floor["transformation"]
        lines.append(f"| {floor['source_floor']} | {floor['analysis_floor']} | {t['source_xref']['block']} | {t['validation_max_residual_m']:.9f} | {t['status']} |")
    lines.extend([
        "",
        "La correspondencia no se asumió por nombre: cada planta cielo contiene un xref cuya planta y origen coinciden con la observación del mismo nivel en `global_axes.json` (101: S1/P1; 102: P2/P3; 103: P4). Las vigas y ejes pertenecen, por tanto, al nivel analítico homónimo.",
        "",
        "## Puntos de control",
        "",
    ])
    for floor in payload["floors"]:
        lines.extend([f"### {floor['analysis_floor']}", "", "| Intersección | Rol | XY lámina | XY global [m] | Residual [m] |", "| --- | --- | --- | --- | ---: |"])
        for control in floor["transformation"]["controls"]:
            lines.append(f"| {control['axis_intersection']} | {control['role']} | {control['sheet_xy']} | {control['calculated_global_xy_m']} | {control['residual_m']:.9f} |")
        lines.append("")
    lines.extend([
        "## Cobertura de los paños actuales",
        "",
        "Estas áreas sólo diagnostican el mapeo espacial. No se multiplicaron por SC ni se reemplazó el Q vigente.",
        "",
        "| Piso | Paños | Área [m²] | Confirmed | Unmapped | Overlap | Review required | Multizona |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for floor in payload["floors"]:
        c = floor["coverage"]
        lines.append(f"| {floor['analysis_floor']} | {c['panel_count']} | {c['panel_area_m2']:.3f} | {c['confirmed_area_m2']:.3f} ({c['confirmed_percent']:.2f}%) | {c['unmapped_area_m2']:.3f} ({c['unmapped_percent']:.2f}%) | {c['overlap_area_m2']:.6f} ({c['overlap_percent']:.3f}%) | {c['review_required_area_m2']:.3f} ({c['review_required_percent']:.2f}%) | {c['multi_zone_panel_count']} |")
    lines.extend(["", "## Zonas SC", "", "| ID | Piso | SC original | SI | Trama | Confianza |", "| --- | --- | ---: | ---: | --- | --- |"])
    for zone in payload["zones"]:
        if zone["load_type"] != "SC":
            continue
        lines.append(f"| {zone['zone_id']} | {zone['analysis_floor']} | {zone['value_original']:.0f} {zone['unit_original']} | {zone['value_SI']:.6f} {zone['unit_SI']} | {zone['hatch_pattern']} | {zone['confidence']} |")
    lines.extend(["", "## Cargas puntuales y lineales", "", "| ID | Piso | Tipo | Referencia XY global [m] | Receptor | Estado |", "| --- | --- | --- | --- | --- | --- |"])
    for load in payload["special_loads"]:
        xy = load.get("annotation_insert_global_xy_m") or load.get("centerline_centroid_global_xy_m")
        receiver = load.get("receiver", {})
        lines.append(f"| {load['load_id']} | {load['analysis_floor']} | {load['load_type']} | {xy} | {receiver.get('element_id', 'UNRESOLVED')} | {load.get('position_status', load.get('geometry_status'))} |")
    lines.extend([
        "",
        "Las tres cargas puntuales aparecen como anotaciones junto al borde superior de sus plantas, pero no poseen un líder o símbolo inequívoco en la capa de cargas. Se registra la coordenada de inserción del texto sólo como referencia documental; no es una posición de aplicación y no se asigna receptor. La carga lineal P4 sí conserva su banda HATCH y una línea central geométrica candidata, también sin aplicación mecánica.",
        "",
        "## Zonas pendientes",
        "",
        "- `P1 / BRASS / SC=500 / PM.ADIC=2800`: geometría alineada, unidad de `2800` aún `REVIEW_REQUIRED`.",
        "- Cargas puntuales P2/P3: posición de aplicación y receptor `REVIEW_REQUIRED`.",
        "- Carga lineal P4: eje central y receptor quedan como candidatos geométricos hasta comprobar el detalle/DWG.",
        "- EDIFICIO_2 no fue promovido a confirmado en esta etapa; debe auditarse separadamente con `2024_22-700`.",
        "",
        "## Overlays",
        "",
    ])
    for floor in payload["floors"]:
        lines.append(f"- [{floor['analysis_floor']}]({Path(floor['overlay']).name})")
    lines.extend(["", "## Invariantes", "", "- Q actual: intacto.", "- G: intacta.", "- `analysis_model.json`: intacto.", "- Masas, EX/EY y superposición: intactas.", "- OpenSees y Unity: no regenerados.", "- `model_viewer.json` original de Luis: intacto.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    axes = load_json(AXES_PATH)
    calce = load_json(CALCE_PATH)
    panels_doc = load_json(PANELS_PATH)
    model = load_json(MODEL_PATH)
    if axes.get("validation", {}).get("status") != "PASS":
        raise RuntimeError("global_axes.json no tiene AXIS_VERTICAL_ALIGNMENT PASS")
    if calce.get("status") != "AXIS_CONFIRMED":
        raise RuntimeError("CALCE_A no está confirmado")
    dx_m = float(calce["transform"]["dx_m"])
    dy_m = float(calce["transform"]["dy_m"])

    dxf_path = DXF_ROOT / "2017_67" / "2017_67-700.dxf"
    document = ezdxf.readfile(dxf_path)
    modelspace = document.modelspace()
    specs = {spec.floor: spec for spec in FLOORS}

    inserts = [entity for entity in modelspace.query("INSERT") if entity.dxf.name.startswith("2017_67-")]
    for spec in FLOORS:
        matches = [insert for insert in inserts if insert.dxf.name == spec.block_name and math.dist((insert.dxf.insert.x, insert.dxf.insert.y), spec.insert_xy) < 1e-6]
        if len(matches) != 1:
            raise RuntimeError(f"xref no inequívoco para {spec.floor}: {len(matches)}")
        insert = matches[0]
        if abs(insert.dxf.xscale - 1.0) > 1e-12 or abs(insert.dxf.yscale - 1.0) > 1e-12 or abs(insert.dxf.rotation) > 1e-12:
            raise RuntimeError(f"xref {spec.floor} no es 1:1 sin giro")

    all_zones = []
    floor_results = []
    zone_index = 1
    line_loads = []
    point_loads = special_point_loads(modelspace, specs, dx_m, dy_m, model)
    for spec in FLOORS:
        transformation = control_audit(spec, axes, dx_m, dy_m)
        if transformation["status"] != "CONFIRMED":
            raise RuntimeError(f"transformación no confirmada para {spec.floor}")
        floor_zones = []
        review_zones = []
        for hatch in modelspace.query("HATCH"):
            if hatch.dxf.layer != "HATCH CARGAS" or not in_viewport(hatch, spec.viewport):
                continue
            pattern = hatch.dxf.pattern_name
            if pattern not in spec.patterns:
                raise RuntimeError(f"patrón {pattern!r} sin leyenda en {spec.floor}")
            geometry_source = hatch_geometry(hatch)
            geometry_global = transform_shape(geometry_source, spec, dx_m, dy_m)
            sc, pm, source_text = spec.patterns[pattern]
            if spec.floor == "P4" and pattern == "BRASS":
                centerline = principal_centerline(geometry_global)
                receiver = nearest_receiver(model, spec.floor, centerline, {"beam", "wall"})
                centroid = centerline.centroid
                line_loads.append({
                    "load_id": "L700-P4-LINE-SC-800",
                    "zone_id": f"L700-E1-{spec.floor}-H{zone_index:02d}",
                    "building": "EDIFICIO_1",
                    "source_sheet": spec.source_sheet,
                    "source_floor": spec.source_floor_title,
                    "analysis_floor": spec.floor,
                    "load_type": "LINE",
                    "components": [
                        {"load_type": "SC", "value_original": sc, "unit_original": "kgf/m", "value_SI": sc * KGF_TO_KN, "unit_SI": "kN/m"},
                        {"load_type": "PM_ADIC", "value_original": pm, "unit_original": "kgf/m", "value_SI": pm * KGF_TO_KN, "unit_SI": "kN/m"},
                    ],
                    "polygon_band": mapping(geometry_global),
                    "centerline_candidate": mapping(centerline),
                    "centerline_centroid_global_xy_m": [round(centroid.x, 6), round(centroid.y, 6)],
                    "centerline_length_m": round(centerline.length, 6),
                    "geometry_status": "CENTERLINE_CANDIDATE_FROM_HATCH_BAND",
                    "receiver": receiver,
                    "source_text": source_text,
                    "confidence": "REVIEW_REQUIRED",
                    "application_status": "NOT_APPLIED",
                })
                zone_index += 1
                continue

            review = spec.floor == "P1" and pattern == "BRASS"
            shared = {
                "zone_id": f"L700-E1-{spec.floor}-H{zone_index:02d}-SC",
                "building": "EDIFICIO_1",
                "source_sheet": spec.source_sheet,
                "source_floor": spec.source_floor_title,
                "analysis_floor": spec.floor,
                "load_type": "SC",
                "value_original": sc,
                "unit_original": "kgf/m2",
                "value_SI": sc * KGF_TO_KN,
                "unit_SI": "kN/m2",
                "polygon": mapping(geometry_global),
                "source_text": source_text,
                "hatch_pattern": pattern,
                "transform": transformation["transform"],
                "confidence": "REVIEW_REQUIRED_UNIT" if review else "CONFIRMED_FROM_PLAN_AND_AXES",
                "application_status": "NOT_APPLIED",
            }
            dead = {
                **shared,
                "zone_id": f"L700-E1-{spec.floor}-H{zone_index:02d}-PM",
                "load_type": "PM_ADIC",
                "value_original": pm,
                "value_SI": pm * KGF_TO_KN,
            }
            all_zones.extend([shared, dead])
            (review_zones if review else floor_zones).append(shared)
            zone_index += 1

        panels = [panel for panel in panels_doc["panos"] if panel["building"] == "EDIFICIO_1" and panel["floor"] == spec.floor]
        coverage, contributions, _confirmed_union, _review_union, unmapped = coverage_for_floor(panels, floor_zones, review_zones)
        relevant_points = [load for load in point_loads if load["analysis_floor"] == spec.floor]
        relevant_lines = [load for load in line_loads if load["analysis_floor"] == spec.floor]
        overlay = draw_overlay(spec.floor, panels, floor_zones, review_zones, axes, unmapped, relevant_points, relevant_lines)
        floor_results.append({
            "source_floor": spec.source_floor_title,
            "analysis_floor": spec.floor,
            "level_correspondence_status": "CONFIRMED_BY_XREF_AND_AXES",
            "level_evidence": f"xref {spec.block_name} contiene el origen estructural observado para {spec.floor} en global_axes.json",
            "transformation": transformation,
            "coverage": coverage,
            "panel_zone_map": contributions,
            "overlay": str(overlay.relative_to(OUT_DIR)).replace("\\", "/"),
        })

    payload = {
        "schema": "MCOC-load-zones-700-spatial-audit-v1",
        "status": "EDIFICIO_1_ALIGNMENT_CONFIRMED_LOAD_APPLICATION_DEFERRED",
        "generated_from": [
            str(dxf_path.relative_to(REPO)).replace("\\", "/"),
            str(AXES_PATH.relative_to(REPO)).replace("\\", "/"),
            str(CALCE_PATH.relative_to(REPO)).replace("\\", "/"),
            str(PANELS_PATH.relative_to(REPO)).replace("\\", "/"),
        ],
        "units": {"length": "m", "area": "m2", "surface_load": "kN/m2", "line_load": "kN/m", "point_load": "kN"},
        "load_policy": {
            "current_case": "LEGACY_UNIFORM_Q_VALIDATION",
            "current_results_modified": False,
            "zone_Q_calculation": "DEFERRED_UNTIL_USER_APPROVAL",
            "unmapped_policy": "UNMAPPED_NO_DEFAULT_FILL",
            "G_and_Q_separated": True,
        },
        "distinct_surface_SC_kgf_m2": [100, 200, 250, 300, 400, 500],
        "floors": floor_results,
        "zones": all_zones,
        "special_loads": point_loads + line_loads,
        "review_required": [
            "P1 BRASS: unidad de PM.ADIC=2800 y naturaleza superficial pendientes de DWG visual",
            "P2/P3 cargas puntuales: texto confirmado; punto de aplicación y receptor no inequívocos",
            "P4 carga lineal: banda confirmada; centrolinea/receptor candidatos",
            "EDIFICIO_2: auditoría equivalente pendiente y separada",
        ],
        "invariants": {
            "Q": "UNCHANGED",
            "G": "UNCHANGED",
            "analysis_model_json": "UNCHANGED",
            "masses": "UNCHANGED",
            "EX_EY": "UNCHANGED",
            "superposition": "UNCHANGED",
            "OpenSees": "NOT_RUN",
            "Unity": "NOT_REBUILT",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(payload)
    print(f"SPATIAL_AUDIT: {payload['status']}")
    for floor in floor_results:
        coverage = floor["coverage"]
        print(f"{floor['analysis_floor']}: confirmed={coverage['confirmed_percent']:.2f}% unmapped={coverage['unmapped_percent']:.2f}% review={coverage['review_required_percent']:.2f}% overlap={coverage['overlap_percent']:.3f}% multi={coverage['multi_zone_panel_count']}")
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
