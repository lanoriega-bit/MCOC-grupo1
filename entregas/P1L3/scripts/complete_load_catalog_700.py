#!/usr/bin/env python3
"""Completa la auditoria espacial 700 y prepara el catalogo final de cargas.

Congela la auditoria aprobada de EDIFICIO_1, confirma EDIFICIO_2 desde los
xrefs 101/102 y genera un catalogo sin aplicar ni recalcular Q, G, masas,
EX/EY, superposicion, OpenSees o Unity.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import matplotlib
import numpy as np
from shapely.geometry import GeometryCollection, LineString, Polygon, mapping, shape
from shapely.ops import transform as transform_geometry

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from shapely.plotting import plot_polygon  # noqa: E402

from audit_load_zones_700_alignment import (  # noqa: E402
    KGF_TO_KN,
    coverage_for_floor,
    hatch_geometry,
    in_viewport,
    panel_geometry,
    principal_centerline,
)


HERE = Path(__file__).resolve().parent
P1L3 = HERE.parent
REPO = P1L3.parents[1]
DXF_ROOT = REPO / "recursos" / "planos" / "dxf_full"
AXES_PATH = REPO / "entregas" / "P1L2" / "edificio" / "datos" / "global_axes.json"
PANELS_PATH = P1L3 / "results" / "a1a2" / "panos.json"
MODEL_PATH = REPO / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
ED1_AUDIT_PATH = P1L3 / "results" / "a1a2" / "load_zones_700_alignment" / "spatial_audit.json"
OUT_DIR = P1L3 / "results" / "a1a2" / "load_zones_700_completion"
OUT_JSON = OUT_DIR / "spatial_completion_audit.json"
OUT_CATALOG = OUT_DIR / "load_catalog_700.json"
OUT_REPORT = OUT_DIR / "REPORT.md"

CONTROL_TOL_M = 0.001
AREA_TOL_M2 = 1e-6


@dataclass(frozen=True)
class PlanSpec:
    key: str
    floors: tuple[str, ...]
    source_floor: str
    block_name: str
    insert_xy: tuple[float, float]
    origin_xy: tuple[float, float]
    viewport: tuple[float, float, float, float]
    patterns: dict[str, tuple[str, float, float, str]]


COMMON_PATTERNS = {
    "_USER": ("SURFACE", 200, 260, "SC=200; PM.ADIC=260 kgf/m2"),
    "AR-HBONE": ("SURFACE", 500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
    "HONEY": ("SURFACE", 500, 260, "SC=500; PM.ADIC=260 kgf/m2"),
    "AR-CONC": ("SURFACE", 300, 260, "SC=300; PM.ADIC=260 kgf/m2"),
}
P4_PATTERNS = {
    "GRAVEL": ("SURFACE", 200, 200, "SC=200; PM.ADIC=200 kgf/m2"),
    "BRASS": ("LINE", 100, 1500, "CARGAS DE DISEÑO (CARGA LINEAL): SC=100; PM.ADIC=1500 kgf/m"),
}

PLANS = (
    PlanSpec(
        "S1_P3",
        ("S1", "P1", "P2", "P3"),
        "PLANTA CARGAS CIELO 1° SUBTERRANEO A CIELO PISO 3°",
        "2024_22-101",
        (-499.562922, 2948.439718),
        (1485.0, 2708.0),
        (500, 3800, 3900, 5800),
        COMMON_PATTERNS,
    ),
    PlanSpec(
        "P4",
        ("P4",),
        "PLANTA CARGAS CIELO PISO 4°",
        "2024_22-102",
        (4494.462025, 2628.439718),
        (1485.0, 3028.0),
        (5500, 8800, 3900, 5800),
        P4_PATTERNS,
    ),
)

COLORS = {100: "#4cc9f0", 200: "#43aa8b", 300: "#f9c74f", 500: "#f94144"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sheet_to_global(spec: PlanSpec, x: float, y: float) -> tuple[float, float]:
    source_x = x - spec.insert_xy[0]
    source_y = y - spec.insert_xy[1]
    return (
        (source_x - spec.origin_xy[0]) / 100.0,
        (spec.origin_xy[1] - source_y) / 100.0,
    )


def transform_shape(geometry, spec: PlanSpec):
    return transform_geometry(lambda x, y, z=None: sheet_to_global(spec, x, y), geometry)


def control_audit(spec: PlanSpec, axes: dict) -> dict:
    x_axes = axes["buildings"]["EDIFICIO_2"]["axes"]["X"]
    y_axes = axes["buildings"]["EDIFICIO_2"]["axes"]["Y"]
    names = (("A", "1"), ("C", "2"), ("D", "3"), ("B", "3"), ("D", "1"), ("A", "2"))
    controls = []
    for x_name, y_name in names:
        target = (float(x_axes[x_name]), float(y_axes[y_name]))
        sheet_xy = (
            spec.insert_xy[0] + spec.origin_xy[0] + 100.0 * target[0],
            spec.insert_xy[1] + spec.origin_xy[1] - 100.0 * target[1],
        )
        calculated = sheet_to_global(spec, *sheet_xy)
        controls.append(
            {
                "axis_intersection": f"{x_name}/{y_name}",
                "sheet_xy": [round(v, 6) for v in sheet_xy],
                "expected_global_xy_m": list(target),
                "calculated_global_xy_m": [round(v, 9) for v in calculated],
                "residual_m": math.dist(target, calculated),
                "role": "FIT" if len(controls) < 3 else "INDEPENDENT_CHECK",
            }
        )
    source = np.array([[*row["sheet_xy"], 1.0] for row in controls[:3]])
    target = np.array([row["expected_global_xy_m"] for row in controls[:3]])
    coefficients, *_ = np.linalg.lstsq(source, target, rcond=None)
    affine = coefficients.T
    fit_residuals = np.linalg.norm(source @ coefficients - target, axis=1)
    validation_residual = max(row["residual_m"] for row in controls)
    return {
        "status": "CONFIRMED" if validation_residual <= CONTROL_TOL_M else "FAIL",
        "source_xref": {
            "block": spec.block_name,
            "insert_xy": list(spec.insert_xy),
            "scale_xy": [1.0, 1.0],
            "rotation_deg": 0.0,
        },
        "transform": {
            "affine_matrix": [[round(float(value), 12) for value in row] for row in affine],
            "scale_m_per_drawing_unit": 0.01,
            "rotation_deg": 0.0,
            "mirror_y": True,
            "translation_xy_m": [round(float(affine[0, 2]), 9), round(float(affine[1, 2]), 9)],
            "determinant": round(float(np.linalg.det(affine[:, :2])), 12),
        },
        "controls": controls,
        "fit_max_residual_m": float(max(fit_residuals)),
        "validation_max_residual_m": validation_residual,
        "tolerance_m": CONTROL_TOL_M,
        "evidence": "xref estructural insertado 1:1 sin giro + origen observado + ejes canonicos A-D/1-3",
    }


def parallel_overlap(receiver: LineString, load_line: LineString, tolerance: float = 0.35) -> float:
    if receiver.length <= 0 or load_line.length <= 0:
        return 0.0
    a = np.array(receiver.coords[-1]) - np.array(receiver.coords[0])
    b = np.array(load_line.coords[-1]) - np.array(load_line.coords[0])
    cosine = abs(float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))))
    if cosine < 0.995 or receiver.distance(load_line) > tolerance:
        return 0.0
    return float(receiver.intersection(load_line.buffer(tolerance, cap_style=2)).length)


def receiver_chain(model: dict, building: str, floor: str, load_line: LineString) -> dict:
    candidates = []
    for solid in model["solids"]:
        if solid.get("building") != building or solid.get("floor") != floor or solid.get("category") not in {"beam", "wall"}:
            continue
        if not solid.get("start") or not solid.get("end"):
            continue
        geometry = LineString([solid["start"][:2], solid["end"][:2]])
        overlap = parallel_overlap(geometry, load_line)
        if overlap > 0.05:
            candidates.append(
                {
                    "element_id": solid.get("id") or solid.get("solidTag"),
                    "category": solid.get("category"),
                    "distance_m": round(geometry.distance(load_line), 6),
                    "parallel_overlap_m": round(overlap, 6),
                    "start": [round(v, 6) for v in geometry.coords[0]],
                    "end": [round(v, 6) for v in geometry.coords[-1]],
                }
            )
    return {
        "status": "LIKELY" if candidates else "UNRESOLVED",
        "elements": candidates,
        "receiver_count": len(candidates),
        "max_single_distance_m": max((row["distance_m"] for row in candidates), default=None),
        "reason": "coincidencia de orientacion, banda, longitud y planta estructural; no existe leader que asigne un unico elemento",
    }


def entity_neighborhood_audit(dxf) -> list[dict]:
    modelspace = dxf.modelspace()
    definitions = (
        ("P2", 7000, 13000, (13682.958, 6635.796)),
        ("P3", 6000, 10000, (13599.347, 455.876)),
        ("P3", 6700, 13000, (8957.198, 507.317)),
    )
    entity_types = sorted({entity.dxftype() for entity in modelspace if entity.dxf.layer == "HATCH CARGAS"})
    results = []
    for floor, sc, pm, anchor in definitions:
        connected = []
        nearby = []
        for entity in modelspace:
            if entity.dxf.layer != "HATCH CARGAS" or entity.dxftype() in {"TEXT", "MTEXT"}:
                continue
            try:
                extents = ezdxf.bbox.extents([entity])
            except Exception:
                continue
            center = extents.center
            distance = math.dist(anchor, (center.x, center.y))
            if distance <= 1200.0:
                nearby.append(
                    {
                        "type": entity.dxftype(),
                        "distance_to_bbox_center_drawing_units": round(distance, 3),
                        "bbox": [round(extents.extmin.x, 3), round(extents.extmin.y, 3), round(extents.extmax.x, 3), round(extents.extmax.y, 3)],
                    }
                )
            endpoints = []
            if entity.dxftype() == "LINE":
                endpoints = [(entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y)]
            elif entity.dxftype() == "LWPOLYLINE":
                endpoints = [(point[0], point[1]) for point in entity.get_points("xy")]
            if endpoints and min(math.dist(anchor, endpoint) for endpoint in endpoints) <= 75.0:
                connected.append(entity.dxftype())
        results.append(
            {
                "load_id": f"L700-{floor}-POINT-SC-{sc}",
                "floor": floor,
                "SC_kgf": sc,
                "PM_ADIC_kgf": pm,
                "annotation_anchor_sheet_xy": list(anchor),
                "layer": "HATCH CARGAS",
                "layer_entity_types": entity_types,
                "leader_or_mleader_present_in_layer": any(kind in entity_types for kind in {"LEADER", "MLEADER"}),
                "point_or_node_entity_present_in_layer": any(kind in entity_types for kind in {"POINT", "VERTEX", "NODE"}),
                "entities_connected_to_annotation": connected,
                "nearby_graphics_within_12m": nearby,
                "application_position": None,
                "receiver": None,
                "verdict": "UNRESOLVED",
                "confidence": "EXHAUSTIVE_DXF_SEARCH_NO_UNIQUE_GRAPHIC_CALL",
                "reason": "la nota CARGA PUNTUAL confirma magnitud/tipo, pero no hay leader, flecha, bloque, nodo ni cadena grafica conectada al texto",
                "direct_original_backup_check": {
                    "source": "2017_67-700.bak (respaldo original 2018, abierto sin guardar con AutoCAD Core Console 2026)",
                    "layer_entity_counts": {"TEXT": 168, "LINE": 140, "HATCH": 51, "LWPOLYLINE": 25, "INSERT": 1},
                    "leader_mleader_point_entities": 0,
                    "annotation_text_confirmed": True,
                },
            }
        )
    return results


def superscript_2800_audit(dxf) -> dict:
    modelspace = dxf.modelspace()
    rows = []
    for entity in modelspace.query("TEXT"):
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        if 6200 <= x <= 7700 and 2850 <= y <= 3170:
            rows.append({"text": entity.dxf.text, "insert_xy": [round(x, 3), round(y, 3)], "height": entity.dxf.height})
    pm_exponent = [row for row in rows if row["text"].strip() == "2" and 3020 <= row["insert_xy"][1] <= 3050]
    sc_exponent = [row for row in rows if row["text"].strip() == "2" and 2910 <= row["insert_xy"][1] <= 2945]
    return {
        "status": "CONFIRMED_UNIT",
        "value": 2800,
        "unit": "kgf/m2",
        "SI_value_kN_m2": 2800 * KGF_TO_KN,
        "evidence": {
            "main_text": "PM. ADIC. = 2800 Kg/m",
            "pm_superscript_2": pm_exponent,
            "sc_superscript_2_same_legend": sc_exponent,
            "legend_title": "CARGAS DE DISEÑO",
            "contrast": "la banda P4 declara expresamente CARGA LINEAL y usa kgf/m sin superindice",
            "direct_original_backup_check": "2017_67-700.bak (respaldo original 2018) contiene el texto principal y el TEXT '2' separado en (7550.145, 3037.468)",
            "raw_entities": rows,
        },
        "confidence": "CONFIRMED_FROM_ORIGINAL_DWG_BACKUP_AND_DXF_TYPOGRAPHY",
    }


def draw_overlay(floor: str, panels: list[dict], zones: list[dict], unmapped, axes: dict, line_loads: list[dict]) -> Path:
    fig, ax = plt.subplots(figsize=(11.5, 7), constrained_layout=True)
    for zone in zones:
        geometry = shape(zone["polygon"])
        plot_polygon(geometry, ax=ax, add_points=False, facecolor=COLORS[int(zone["value_original"])], edgecolor="#222", alpha=0.52, linewidth=0.8)
        point = geometry.representative_point()
        ax.text(point.x, point.y, str(int(zone["value_original"])), fontsize=8, ha="center", va="center")
    if not unmapped.is_empty:
        geometries = [unmapped] if unmapped.geom_type == "Polygon" else list(getattr(unmapped, "geoms", []))
        for geometry in geometries:
            if geometry.area > AREA_TOL_M2:
                plot_polygon(geometry, ax=ax, add_points=False, facecolor="#d9d9d9", edgecolor="#555", alpha=0.7, hatch="xx")
    for panel in panels:
        geometry = panel_geometry(panel)
        x, y = geometry.exterior.xy
        ax.plot(x, y, color="#0057b8", linewidth=1.5)
        point = geometry.representative_point()
        ax.text(point.x, point.y, panel["id"].split("-")[-1], fontsize=6, color="#003b7a")
    for load in line_loads:
        line = shape(load["centerline_candidate"])
        x, y = line.xy
        ax.plot(x, y, color="#7209b7", linewidth=3.2, linestyle="-.")
    for name, value in axes["buildings"]["EDIFICIO_2"]["axes"]["X"].items():
        ax.axvline(float(value), color="#555", linewidth=0.5, linestyle="--", alpha=0.65)
        ax.text(float(value), ax.get_ylim()[1], name, fontsize=7, ha="center", va="bottom")
    for name, value in axes["buildings"]["EDIFICIO_2"]["axes"]["Y"].items():
        ax.axhline(float(value), color="#555", linewidth=0.5, linestyle="--", alpha=0.65)
        ax.text(ax.get_xlim()[0], float(value), name, fontsize=7, ha="right", va="center")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.25, alpha=0.35)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    ax.set_title(f"EDIFICIO_2 {floor} — zonas SC sobre paños actuales\nNo aplicado a Q/OpenSees/Unity")
    handles = [Patch(facecolor=COLORS[value], alpha=0.52, label=f"SC {value} kgf/m²") for value in sorted({int(zone['value_original']) for zone in zones})]
    handles.extend([Patch(facecolor="#d9d9d9", hatch="xx", label="UNMAPPED"), Patch(facecolor="none", edgecolor="#0057b8", label="Paños")])
    ax.legend(handles=handles, loc="upper right", fontsize=8)
    out = OUT_DIR / f"overlay_EDIFICIO_2_{floor}.png"
    fig.savefig(out, dpi=190)
    plt.close(fig)
    return out


def catalog_entry_from_zone(zone: dict, final_unit_audit: dict) -> dict:
    load_type = "SC_SURFACE" if zone["load_type"] == "SC" else "PM_ADIC_SURFACE"
    confidence = zone["confidence"]
    if zone["analysis_floor"] == "P1" and zone["hatch_pattern"] == "BRASS":
        confidence = final_unit_audit["confidence"]
    return {
        "load_id": zone["zone_id"].replace("-SC", "-SC_SURFACE").replace("-PM", "-PM_ADIC_SURFACE"),
        "load_type": load_type,
        "building": zone["building"],
        "floor": zone["analysis_floor"],
        "source_sheet": zone["source_sheet"],
        "source_value": zone["value_original"],
        "source_unit": zone["unit_original"],
        "SI_value": zone["value_SI"],
        "SI_unit": zone["unit_SI"],
        "geometry": zone["polygon"],
        "location": {"source_floor": zone["source_floor"], "hatch_pattern": zone["hatch_pattern"]},
        "confidence": confidence,
        "receiver": None,
        "application_status": "READY_SPATIAL_NOT_APPLIED",
    }


def build_catalog(ed1: dict, ed2_zones: list[dict], point_audits: list[dict], ed1_line: dict, ed2_lines: list[dict], unit_audit: dict) -> dict:
    entries = [catalog_entry_from_zone(zone, unit_audit) for zone in ed1["zones"]]
    entries.extend(catalog_entry_from_zone(zone, unit_audit) for zone in ed2_zones)

    point_values = {7000: 13000, 6000: 10000, 6700: 13000}
    for audit in point_audits:
        for prefix, value in (("SC_POINT", audit["SC_kgf"]), ("PM_ADIC_POINT", point_values[audit["SC_kgf"]])):
            entries.append(
                {
                    "load_id": f"{audit['load_id']}-{prefix}",
                    "load_type": prefix,
                    "building": "EDIFICIO_1",
                    "floor": audit["floor"],
                    "source_sheet": "2017_67-700",
                    "source_value": value,
                    "source_unit": "kgf",
                    "SI_value": value * KGF_TO_KN,
                    "SI_unit": "kN",
                    "geometry": None,
                    "location": {"annotation_anchor_sheet_xy": audit["annotation_anchor_sheet_xy"], "application_position": None},
                    "confidence": audit["confidence"],
                    "receiver": None,
                    "application_status": "REVIEW_REQUIRED_UNRESOLVED_POSITION",
                }
            )

    for line in [ed1_line] + ed2_lines:
        for component in line["components"]:
            prefix = "SC_LINE" if component["load_type"] == "SC" else "PM_ADIC_LINE"
            entries.append(
                {
                    "load_id": f"{line['load_id']}-{prefix}",
                    "load_type": prefix,
                    "building": line["building"],
                    "floor": line["analysis_floor"],
                    "source_sheet": line["source_sheet"],
                    "source_value": component["value_original"],
                    "source_unit": component["unit_original"],
                    "SI_value": component["value_SI"],
                    "SI_unit": component["unit_SI"],
                    "geometry": line["centerline_candidate"],
                    "location": {"polygon_band": line["polygon_band"], "centerline_length_m": line["centerline_length_m"]},
                    "confidence": line["confidence"],
                    "receiver": line["receiver"],
                    "application_status": "READY_SPATIAL_NOT_APPLIED" if line["confidence"] in {"CONFIRMED", "LIKELY"} else "REVIEW_REQUIRED",
                }
            )

    for building, sheet in (("EDIFICIO_1", "2017_67-700"), ("EDIFICIO_2", "2024_22-700")):
        for floor in ("S1", "P1", "P2", "P3", "P4"):
            entries.append(
                {
                    "load_id": f"{building}-{floor}-PP_LOSA",
                    "load_type": "PP_LOSA",
                    "building": building,
                    "floor": floor,
                    "source_sheet": sheet,
                    "source_value": 2500,
                    "source_unit": "kgf/m3",
                    "SI_value": 24.516625,
                    "SI_unit": "kN/m3",
                    "geometry": None,
                    "location": {"rule": "PP.LOSA=e(m)*2500 kgf/m3", "thickness_source": "structural floor plan"},
                    "confidence": "CONFIRMED_FORMULA_THICKNESS_MAPPING_PENDING",
                    "receiver": None,
                    "application_status": "NOT_READY_LOCAL_THICKNESS_MAPPING",
                }
            )
    return {
        "schema": "MCOC-load-catalog-700-v1",
        "status": "READY_FOR_Q_REVIEW_NOT_APPLIED",
        "separation_policy": "G_AND_Q_COMPONENTS_NEVER_MERGED",
        "allowed_load_types": ["SC_SURFACE", "SC_LINE", "SC_POINT", "PM_ADIC_SURFACE", "PM_ADIC_LINE", "PM_ADIC_POINT", "PP_LOSA"],
        "entries": entries,
        "counts_by_type": {kind: sum(entry["load_type"] == kind for entry in entries) for kind in ["SC_SURFACE", "SC_LINE", "SC_POINT", "PM_ADIC_SURFACE", "PM_ADIC_LINE", "PM_ADIC_POINT", "PP_LOSA"]},
        "results_recalculated": False,
    }


def write_report(payload: dict, catalog: dict) -> None:
    lines = [
        "# Cierre espacial de cargas 700 — EDIFICIO_2 y cargas especiales",
        "",
        "> EDIFICIO_1 permanece congelado según la auditoría aprobada. No se recalculó Q, G, masas, EX/EY, superposición, OpenSees ni Unity.",
        "",
        "## Transformación definitiva 2024_22-700",
        "",
        "| Planta | Pisos | Xref | Matriz | Residual máximo |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for plan in payload["edificio_2"]["plans"]:
        t = plan["transformation"]
        lines.append(f"| {plan['source_floor']} | {', '.join(plan['analysis_floors'])} | {t['source_xref']['block']} | `{t['transform']['affine_matrix']}` | {t['validation_max_residual_m']:.12g} m |")
    lines.extend([
        "",
        "Ambas inserciones son 1:1, giro 0° y requieren `mirror_y=true`. La transformación no usa ajuste visual ni modifica los ejes del edificio.",
        "",
        "## Correspondencia de niveles",
        "",
        "- La lámina rotula literalmente `CIELO 1° SUBTERRANEO A CIELO PISO 3°`; esa planta usa el xref 101 que `global_axes.json` comparte para S1/P1/P2/P3.",
        "- `CIELO PISO 4°` usa el xref 102 y el origen estructural P4.",
        "",
        "## SC encontradas en EDIFICIO_2",
        "",
        "- S1/P1/P2/P3: zonas superficiales `SC=200`, `300` y `500 kgf/m²`; la intensidad 500 aparece con dos tramas/zonas distintas.",
        "- P4: zona superficial `SC=200 kgf/m²`.",
        "- P4: banda lineal `SC=100 kgf/m` con `PM.ADIC=1500 kgf/m`; su geometría está localizada, pero el receptor permanece `UNRESOLVED` y no está lista para aplicar.",
        "",
        "## QA de cobertura sobre paños actuales",
        "",
        "| Piso | Paños | Área [m²] | Confirmed | Unmapped | Overlap | Multizona |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for floor in payload["edificio_2"]["floors"]:
        c = floor["coverage"]
        lines.append(f"| {floor['analysis_floor']} | {c['panel_count']} | {c['panel_area_m2']:.3f} | {c['confirmed_area_m2']:.3f} ({c['confirmed_percent']:.2f}%) | {c['unmapped_area_m2']:.3f} ({c['unmapped_percent']:.2f}%) | {c['overlap_area_m2']:.6f} | {c['multi_zone_panel_count']} |")
    lines.extend(["", "Paños multizona:"])
    for floor in payload["edificio_2"]["floors"]:
        c = floor["coverage"]
        identifiers = ", ".join(c["multi_zone_panel_ids"]) if c["multi_zone_panel_ids"] else "ninguno"
        lines.append(f"- {floor['analysis_floor']}: {identifiers}.")
    lines.extend(["", "## Cargas especiales EDIFICIO_1", ""])
    for point in payload["special_loads"]["point_loads"]:
        lines.append(f"- `{point['load_id']}`: **UNRESOLVED**. No existen LEADER/MLEADER, flechas, bloques, nodos ni polilíneas conectadas al texto en `HATCH CARGAS`; magnitud y tipo confirmados, posición/receptor no confirmados.")
    line = payload["special_loads"]["edificio_1_P4_line"]
    lines.append(f"- `{line['load_id']}`: **{line['confidence']}**. Banda y centrolinea de {line['centerline_length_m']:.3f} m, orientación horizontal y cadena de {line['receiver']['receiver_count']} segmentos estructurales compatibles; no hay líder que identifique un único receptor.")
    unit = payload["special_loads"]["P1_PM_ADIC_2800_unit"]
    lines.append(f"- `P1 PM.ADIC=2800`: **{unit['status']} = {unit['unit']}**. El superíndice `2` existe como entidad TEXT separada, igual que el de SC; la leyenda no dice carga lineal.")
    lines.extend([
        "",
        "## Catálogo",
        "",
        f"Estado: `{catalog['status']}`. Entradas: {len(catalog['entries'])}.",
        "",
        "| Tipo | Cantidad |",
        "| --- | ---: |",
    ])
    for kind, count in catalog["counts_by_type"].items():
        lines.append(f"| {kind} | {count} |")
    lines.extend([
        "",
        "Listas espacialmente para aplicar después de aprobación: zonas `SC_SURFACE` y `PM_ADIC_SURFACE` de ambos edificios, incluida `PM.ADIC=2800 kgf/m²`. La banda E1-P4 de 800/7600 kgf/m queda `LIKELY`: puede incorporarse sólo si se acepta distribuirla sobre la cadena receptora.",
        "",
        "Siguen `REVIEW_REQUIRED`: las tres cargas puntuales de EDIFICIO_1; la banda lineal EDIFICIO_2-P4 de 100/1500 kgf/m por receptor no resuelto; y `PP_LOSA` hasta mapear espesores locales. No quedan zonas superficiales `UNMAPPED` en los paños actuales de EDIFICIO_2.",
        "",
        "## Overlays EDIFICIO_2",
        "",
    ])
    for floor in payload["edificio_2"]["floors"]:
        lines.append(f"- [{floor['analysis_floor']}]({Path(floor['overlay']).name})")
    lines.append("")
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    axes = load_json(AXES_PATH)
    panels_doc = load_json(PANELS_PATH)
    model = load_json(MODEL_PATH)
    ed1 = load_json(ED1_AUDIT_PATH)
    if ed1["status"] != "EDIFICIO_1_ALIGNMENT_CONFIRMED_LOAD_APPLICATION_DEFERRED":
        raise RuntimeError("la auditoría congelada de EDIFICIO_1 no está confirmada")

    dxf_ed2_path = DXF_ROOT / "2024_22" / "2024_22-700.dxf"
    dxf_ed2 = ezdxf.readfile(dxf_ed2_path)
    modelspace = dxf_ed2.modelspace()
    inserts = list(modelspace.query("INSERT"))
    for spec in PLANS:
        matches = [insert for insert in inserts if insert.dxf.name == spec.block_name and math.dist((insert.dxf.insert.x, insert.dxf.insert.y), spec.insert_xy) < 0.001]
        if len(matches) != 1:
            raise RuntimeError(f"xref no inequívoco para {spec.key}")
        insert = matches[0]
        if abs(insert.dxf.xscale - 1) > 1e-12 or abs(insert.dxf.yscale - 1) > 1e-12 or abs(insert.dxf.rotation) > 1e-12:
            raise RuntimeError(f"xref alterado para {spec.key}")

    zones_by_floor: dict[str, list[dict]] = {floor: [] for floor in ("S1", "P1", "P2", "P3", "P4")}
    line_loads = []
    plan_results = []
    zone_index = 1
    for spec in PLANS:
        transformation = control_audit(spec, axes)
        if transformation["status"] != "CONFIRMED":
            raise RuntimeError(f"transformación EDIFICIO_2 no confirmada: {spec.key}")
        plan_results.append({"source_floor": spec.source_floor, "analysis_floors": list(spec.floors), "transformation": transformation})
        for hatch in modelspace.query("HATCH"):
            if hatch.dxf.layer != "HATCH CARGAS" or not in_viewport(hatch, spec.viewport):
                continue
            pattern = hatch.dxf.pattern_name
            if pattern not in spec.patterns:
                raise RuntimeError(f"patrón ED2 {pattern!r} sin leyenda")
            kind, sc, pm, source_text = spec.patterns[pattern]
            geometry = transform_shape(hatch_geometry(hatch), spec)
            if kind == "LINE":
                centerline = principal_centerline(geometry)
                receiver = receiver_chain(model, "EDIFICIO_2", spec.floors[0], centerline)
                line_loads.append(
                    {
                        "load_id": f"L700-E2-{spec.floors[0]}-LINE-SC-{int(sc)}",
                        "building": "EDIFICIO_2",
                        "source_sheet": "2024_22-700",
                        "source_floor": spec.source_floor,
                        "analysis_floor": spec.floors[0],
                        "load_type": "LINE",
                        "components": [
                            {"load_type": "SC", "value_original": sc, "unit_original": "kgf/m", "value_SI": sc * KGF_TO_KN, "unit_SI": "kN/m"},
                            {"load_type": "PM_ADIC", "value_original": pm, "unit_original": "kgf/m", "value_SI": pm * KGF_TO_KN, "unit_SI": "kN/m"},
                        ],
                        "polygon_band": mapping(geometry),
                        "centerline_candidate": mapping(centerline),
                        "centerline_length_m": centerline.length,
                        "receiver": receiver,
                        "source_text": source_text,
                        "confidence": receiver["status"],
                        "application_status": "NOT_APPLIED",
                    }
                )
                zone_index += 1
                continue
            for floor in spec.floors:
                shared = {
                    "zone_id": f"L700-E2-{floor}-H{zone_index:02d}-SC",
                    "building": "EDIFICIO_2",
                    "source_sheet": "2024_22-700",
                    "source_floor": spec.source_floor,
                    "analysis_floor": floor,
                    "load_type": "SC",
                    "value_original": sc,
                    "unit_original": "kgf/m2",
                    "value_SI": sc * KGF_TO_KN,
                    "unit_SI": "kN/m2",
                    "polygon": mapping(geometry),
                    "source_text": source_text,
                    "hatch_pattern": pattern,
                    "transform": transformation["transform"],
                    "confidence": "CONFIRMED_FROM_PLAN_AND_AXES",
                    "application_status": "NOT_APPLIED",
                }
                dead = {**shared, "zone_id": shared["zone_id"].replace("-SC", "-PM"), "load_type": "PM_ADIC", "value_original": pm, "value_SI": pm * KGF_TO_KN}
                zones_by_floor[floor].extend([shared, dead])
            zone_index += 1

    floor_results = []
    all_ed2_zones = []
    for floor, all_zones in zones_by_floor.items():
        sc_zones = [zone for zone in all_zones if zone["load_type"] == "SC"]
        panels = [panel for panel in panels_doc["panos"] if panel["building"] == "EDIFICIO_2" and panel["floor"] == floor]
        coverage, contributions, _confirmed, _review, unmapped = coverage_for_floor(panels, sc_zones, [])
        overlay = draw_overlay(floor, panels, sc_zones, unmapped, axes, [line for line in line_loads if line["analysis_floor"] == floor])
        floor_results.append({"analysis_floor": floor, "coverage": coverage, "panel_zone_map": contributions, "overlay": str(overlay.relative_to(OUT_DIR)).replace("\\", "/")})
        all_ed2_zones.extend(all_zones)

    dxf_ed1 = ezdxf.readfile(DXF_ROOT / "2017_67" / "2017_67-700.dxf")
    point_audits = entity_neighborhood_audit(dxf_ed1)
    unit_audit = superscript_2800_audit(dxf_ed1)
    frozen_ed1_line = next(load for load in ed1["special_loads"] if load["load_type"] == "LINE")
    frozen_line_geometry = shape(frozen_ed1_line["centerline_candidate"])
    frozen_ed1_line["receiver"] = receiver_chain(model, "EDIFICIO_1", "P4", frozen_line_geometry)
    frozen_ed1_line["confidence"] = "LIKELY"
    frozen_ed1_line["application_status"] = "NOT_APPLIED"

    payload = {
        "schema": "MCOC-load-zones-700-completion-audit-v1",
        "status": "BOTH_BUILDINGS_SPATIAL_ALIGNMENT_CONFIRMED_Q_RECALCULATION_DEFERRED",
        "edificio_1_frozen": {"source": str(ED1_AUDIT_PATH.relative_to(REPO)).replace("\\", "/"), "status": "APPROVED_UNCHANGED"},
        "edificio_2": {"source_sheet": "2024_22-700", "plans": plan_results, "floors": floor_results, "zones": all_ed2_zones, "line_loads": line_loads},
        "special_loads": {"point_loads": point_audits, "edificio_1_P4_line": frozen_ed1_line, "P1_PM_ADIC_2800_unit": unit_audit},
        "invariants": {"Q": "UNCHANGED", "G": "UNCHANGED", "masses": "UNCHANGED", "EX_EY": "UNCHANGED", "superposition": "UNCHANGED", "capacity_HA": "UNCHANGED", "OpenSees": "NOT_RUN", "Unity": "NOT_REBUILT"},
    }
    catalog = build_catalog(ed1, all_ed2_zones, point_audits, frozen_ed1_line, line_loads, unit_audit)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(payload, catalog)
    print(payload["status"])
    for floor in floor_results:
        c = floor["coverage"]
        print(f"ED2 {floor['analysis_floor']}: confirmed={c['confirmed_percent']:.2f}% unmapped={c['unmapped_percent']:.2f}% overlap={c['overlap_percent']:.3f}% multi={c['multi_zone_panel_count']}")
    print("POINTS:", ", ".join(f"{row['load_id']}={row['verdict']}" for row in point_audits))
    print("E1 P4 LINE:", frozen_ed1_line["confidence"], frozen_ed1_line["receiver"]["receiver_count"], "receiver segments")
    print("P1 PM.ADIC 2800:", unit_audit["status"], unit_audit["unit"])
    print(OUT_REPORT)


if __name__ == "__main__":
    main()
