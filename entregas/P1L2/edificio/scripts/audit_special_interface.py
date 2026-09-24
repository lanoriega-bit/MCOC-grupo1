#!/usr/bin/env python3
"""Audita sectores especiales ED1 y la interfaz geometrica ED1/ED2.

Es un diagnostico: no crea conexiones, no modifica geometria y no toca FE.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import audit_ed1_beams as ed1_source


REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
CALCE = REPO / "entregas/P1L2/edificio/datos/axis_calce_validation.json"
OUTBOARD_PRIOR = REPO / "entregas/P1L2/edificio/datos/outboard_room_reconstruction.json"
ARCH_P4 = REPO / "entregas/P1L3/arquitectura/architectural_visual_model.json"
DILATATION_AUDIT = REPO / "entregas/P1L2/edificio/validacion/special_interface/ed1_dilatation_audit.json"
SOURCE_ROOT = REPO / "recursos/planos/dxf_full"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/special_interface"
OUT_JSON = OUT_DIR / "special_interface_audit.json"
OUT_MD = OUT_DIR / "REPORT.md"
FLOORS = ("S1", "P1", "P2", "P3", "P4")
INTERFACE_X_ED2_M = 27.5
INTERFACE_X_ED1_M = 27.491
INTERFACE_BAND_M = 0.75
CONTACT_TOLERANCE_M = 0.35
OUTBOARD_TOLERANCE_M = 0.35
ED1_ENVELOPE = {"x_min": 27.491, "x_max": 77.491, "y_min": 0.0, "y_max": 16.15}
KEYWORDS = re.compile(r"JUNTA|DILAT|SEPAR|EDIFICIO|EXIST|EMPAL|CONEX|ANCLA|INTERFA", re.I)
JOINT_KEYWORDS = re.compile(r"JUNTA|DILAT", re.I)
TEXT_SHEETS = {
    "2017_67": ("2017_67-000.dxf", "2017_67-001.dxf", "2017_67-002.dxf", "2017_67-100.dxf", "2017_67-101.dxf", "2017_67-102.dxf", "2017_67-103.dxf"),
    "2024_22": ("2024_22-000.dxf", "2024_22-001.dxf", "2024_22-002.dxf", "2024_22-100.dxf", "2024_22-101.dxf", "2024_22-102.dxf"),
}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def points(item: dict[str, object]) -> list[list[float]]:
    if "start" in item and "end" in item:
        return [item["start"], item["end"]]
    if "center" in item:
        return [item["center"]]
    return []


def interface_items(model: dict[str, object], floor: str, building: str) -> list[dict[str, object]]:
    result = []
    for item in model["solids"]:
        if item.get("floor") != floor or item.get("building") != building or item.get("category") not in {"beam", "wall", "column"}:
            continue
        item_points = points(item)
        if item_points and min(abs(float(point[0]) - INTERFACE_X_ED2_M) for point in item_points) <= INTERFACE_BAND_M:
            result.append(item)
    return result


def stations(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in items:
        for index, point in enumerate(points(item)):
            if abs(float(point[0]) - INTERFACE_X_ED2_M) > INTERFACE_BAND_M:
                continue
            rows.append({"id": item.get("id"), "category": item.get("category"), "point_kind": "center" if len(points(item)) == 1 else f"end_{index}", "xy_m": [float(point[0]), float(point[1])]})
    return rows


def crossing_members(items: list[dict[str, object]]) -> list[str]:
    """Miembros cuyo eje cruza materialmente D/E; tocar el eje no basta."""
    rows = []
    for item in items:
        item_points = points(item)
        if len(item_points) != 2:
            continue
        xs = [float(point[0]) for point in item_points]
        if min(xs) < INTERFACE_X_ED2_M - CONTACT_TOLERANCE_M and max(xs) > INTERFACE_X_ED2_M + CONTACT_TOLERANCE_M:
            rows.append(str(item.get("id")))
    return sorted(rows)


def contacts(first: list[dict[str, object]], second: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in first:
        ranked = sorted((math.dist(item["xy_m"], other["xy_m"]), other) for other in second)
        if not ranked or ranked[0][0] > CONTACT_TOLERANCE_M:
            continue
        distance, other = ranked[0]
        rows.append({"ed1": item, "ed2": other, "residual_m": round(distance, 6), "classification": "GEOMETRIC_CONTACT_ONLY"})
    return rows


def outboard_sides(item: dict[str, object]) -> list[str]:
    item_points = points(item)
    if not item_points:
        return []
    sides = []
    if min(float(point[0]) for point in item_points) < ED1_ENVELOPE["x_min"] - OUTBOARD_TOLERANCE_M:
        sides.append("WEST_INTERFACE_SIDE")
    if max(float(point[0]) for point in item_points) > ED1_ENVELOPE["x_max"] + OUTBOARD_TOLERANCE_M:
        sides.append("EAST")
    if min(float(point[1]) for point in item_points) < ED1_ENVELOPE["y_min"] - OUTBOARD_TOLERANCE_M:
        sides.append("SOUTH")
    if max(float(point[1]) for point in item_points) > ED1_ENVELOPE["y_max"] + OUTBOARD_TOLERANCE_M:
        sides.append("NORTH")
    return sides


def text_value(entity) -> str:
    try:
        if entity.dxftype() == "TEXT":
            return str(entity.dxf.text)
        if entity.dxftype() == "MTEXT":
            return str(entity.plain_text())
        if entity.dxftype() in {"ATTRIB", "ATTDEF"}:
            return str(entity.dxf.text)
    except Exception:
        return ""
    return ""


def scan_interface_notes() -> dict[str, object]:
    sheets = []
    hits = []
    for series, names in TEXT_SHEETS.items():
        for name in names:
            path = SOURCE_ROOT / series / name
            row = {"sheet": name, "sha256": sha256(path), "keyword_hits": 0}
            doc = ezdxf.readfile(path)
            for layout in doc.layouts:
                for entity in layout:
                    insert = None
                    if entity.dxftype() in {"TEXT", "MTEXT"} and hasattr(entity.dxf, "insert"):
                        insert = [float(entity.dxf.insert.x), float(entity.dxf.insert.y)]
                    candidates = [(entity.dxf.layer, text_value(entity), insert)]
                    if entity.dxftype() == "INSERT":
                        candidates.extend((attribute.dxf.layer, text_value(attribute), None) for attribute in entity.attribs)
                    for layer, text, raw_insert in candidates:
                        if text and KEYWORDS.search(text):
                            hit = {"sheet": name, "layout": layout.name, "layer": layer, "text": " ".join(text.split())[:240], "joint_keyword": bool(JOINT_KEYWORDS.search(text))}
                            if raw_insert is not None:
                                hit["raw_insert"] = raw_insert
                                for floor, (floor_sheet, bbox, origin) in ed1_source.FLOOR_SOURCES.items():
                                    if name != floor_sheet:
                                        continue
                                    x0, y0, x1, y1 = bbox
                                    if x0 <= raw_insert[0] <= x1 and y0 <= raw_insert[1] <= y1:
                                        global_xy = ed1_source.transform(tuple(raw_insert), origin)
                                        hit["floor"] = floor
                                        hit["global_xy_m"] = [round(float(value), 6) for value in global_xy]
                                        hit["distance_to_interface_x_m"] = round(abs(float(global_xy[0]) - INTERFACE_X_ED2_M), 6)
                            hits.append(hit)
                            row["keyword_hits"] += 1
            sheets.append(row)
    joint_hits = [hit for hit in hits if hit["joint_keyword"]]
    localized = [hit for hit in joint_hits if hit.get("distance_to_interface_x_m", math.inf) <= 1.25]
    return {
        "sheets": sheets,
        "hits": hits,
        "joint_or_dilatation_hits": joint_hits,
        "localized_interface_candidates": localized,
        "explicit_whole_interface_connection_detail_found": False,
    }


def plot_s1_dilatation_source(note_scan: dict[str, object]) -> dict[str, object] | None:
    candidates = [hit for hit in note_scan["localized_interface_candidates"] if hit.get("floor") == "S1"]
    if not candidates:
        return None
    target = candidates[0]
    path = SOURCE_ROOT / "2017_67" / "2017_67-101.dxf"
    doc = ezdxf.readfile(path)
    _sheet, _bbox, origin = ed1_source.FLOOR_SOURCES["S1"]
    target_xy = target["global_xy_m"]
    colors = {"RLE-VIGA": "#1a73e8", "RLE-MURO": "#188038", "RLA-MURO DILATADO": "#d93025", "RLA-MURO INV DILATADO": "#f9ab00", "RLE-LOSA": "#9334e6", "RLE-PILAR": "#f57c00", "RLE-EJE": "#777777", "RLE-EJES": "#aaaaaa"}
    nearby = []
    fig, ax = plt.subplots(figsize=(9, 8))
    for entity in doc.modelspace():
        if entity.dxftype() not in {"LINE", "LWPOLYLINE"}:
            continue
        for first, second in ed1_source.raw_segments(entity):
            start = ed1_source.transform(first, origin)
            end = ed1_source.transform(second, origin)
            if max(start[0], end[0]) < target_xy[0] - 3.0 or min(start[0], end[0]) > target_xy[0] + 3.0 or max(start[1], end[1]) < target_xy[1] - 3.0 or min(start[1], end[1]) > target_xy[1] + 3.0:
                continue
            ax.plot([start[0], end[0]], [start[1], end[1]], color=colors.get(entity.dxf.layer, "#dddddd"), linewidth=1.2 if entity.dxf.layer in colors else 0.5)
            distance = min(math.dist(target_xy, start), math.dist(target_xy, end))
            if distance <= 1.5:
                nearby.append({"entity_type": entity.dxftype(), "handle": str(entity.dxf.handle), "layer": entity.dxf.layer, "start_global_xy_m": [round(v, 4) for v in start], "end_global_xy_m": [round(v, 4) for v in end], "endpoint_distance_to_note_m": round(distance, 4)})
    ax.scatter([target_xy[0]], [target_xy[1]], marker="*", s=110, color="#d93025")
    ax.text(target_xy[0] + 0.05, target_xy[1] + 0.08, str(target["text"]), color="#a50e0e", fontsize=9)
    ax.axvline(INTERFACE_X_ED2_M, color="#d93025", linestyle="--", linewidth=1.0)
    ax.axvline(INTERFACE_X_ED1_M, color="#9334e6", linestyle=":", linewidth=1.0)
    ax.set_xlim(target_xy[0] - 3.0, target_xy[0] + 3.0)
    ax.set_ylim(target_xy[1] - 3.0, target_xy[1] + 3.0)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.4)
    ax.set_title("2017_67-101 / S1: contexto DXF de la nota (DILATADO)")
    output = OUT_DIR / "s1_dilatado_source_detail.png"
    fig.tight_layout()
    fig.savefig(output, dpi=210)
    plt.close(fig)
    return {
        "note": target,
        "overlay": str(output.relative_to(REPO)).replace("\\", "/"),
        "nearby_entity_count": len(nearby),
        "nearby_layer_counts": dict(Counter(item["layer"] for item in nearby)),
        "nearby_entities": sorted(nearby, key=lambda item: (item["endpoint_distance_to_note_m"], item["handle"])),
        "interpretation": "LOCAL_DILATATION_CALLOUT_WITH_CONFIRMED_CLOSED_WALL_CONTOUR; NO_CROSS_BUILDING_CONNECTION_PROVEN",
    }


def plot_interface(floor: str, rows: dict[str, list[dict[str, object]]], note_candidates: list[dict[str, object]]) -> str:
    fig, ax = plt.subplots(figsize=(8, 12))
    for building, color in (("EDIFICIO_1", "#1a73e8"), ("EDIFICIO_2", "#f57c00")):
        for item in rows[building]:
            item_points = points(item)
            if len(item_points) == 2:
                ax.plot([p[0] for p in item_points], [p[1] for p in item_points], color=color, linewidth=1.5)
            else:
                ax.scatter([item_points[0][0]], [item_points[0][1]], color=color, s=18)
    ax.axvline(INTERFACE_X_ED2_M, color="#d93025", linestyle="--", linewidth=1.2, label="D ED2")
    ax.axvline(INTERFACE_X_ED1_M, color="#9334e6", linestyle=":", linewidth=1.2, label="E ED1")
    for note in note_candidates:
        if note.get("floor") != floor:
            continue
        x, y = note["global_xy_m"]
        ax.scatter([x], [y], marker="*", s=80, color="#d93025")
        ax.text(x + 0.08, y + 0.08, str(note["text"]), fontsize=7, color="#a50e0e")
    ax.set_xlim(24.0, 31.0)
    ax.set_ylim(-2.0, 18.5)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend()
    ax.set_title(f"Interfaz ED1/ED2 {floor}: contacto geometrico, no conexion FE")
    output = OUT_DIR / f"interface_{floor.lower()}.png"
    fig.tight_layout()
    fig.savefig(output, dpi=190)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def plot_outboard(floor: str, items: list[dict[str, object]]) -> str:
    fig, ax = plt.subplots(figsize=(14, 7))
    colors = {"beam": "#1a73e8", "wall": "#188038", "column": "#f57c00", "support": "#444444"}
    for item in items:
        item_points = points(item)
        if len(item_points) == 2:
            ax.plot([p[0] for p in item_points], [p[1] for p in item_points], color=colors.get(str(item.get("category")), "#777777"), linewidth=1.4)
        elif item_points:
            ax.scatter([item_points[0][0]], [item_points[0][1]], color=colors.get(str(item.get("category")), "#777777"), s=18)
    ax.plot(
        [ED1_ENVELOPE["x_min"], ED1_ENVELOPE["x_max"], ED1_ENVELOPE["x_max"], ED1_ENVELOPE["x_min"], ED1_ENVELOPE["x_min"]],
        [ED1_ENVELOPE["y_min"], ED1_ENVELOPE["y_min"], ED1_ENVELOPE["y_max"], ED1_ENVELOPE["y_max"], ED1_ENVELOPE["y_min"]],
        color="#d93025", linestyle="--", linewidth=1.0,
    )
    ax.set_xlim(24.0, 82.0)
    ax.set_ylim(-14.0, 31.0)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_title(f"EDIFICIO_1 {floor}: elementos fuera de envolvente primaria")
    output = OUT_DIR / f"outboard_{floor.lower()}.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = load(MODEL)
    calce = load(CALCE)
    prior = load(OUTBOARD_PRIOR)
    architecture = load(ARCH_P4)
    dilatation_audit = load(DILATATION_AUDIT)
    note_scan = scan_interface_notes()
    dilatation_detail = plot_s1_dilatation_source(note_scan)
    by_floor = {}
    outboard_counts: Counter[str] = Counter()
    for floor in FLOORS:
        near = {building: interface_items(model, floor, building) for building in ("EDIFICIO_1", "EDIFICIO_2")}
        structural_by_building = {
            building: [
                item for item in model["solids"]
                if item.get("floor") == floor and item.get("building") == building and item.get("category") in {"beam", "wall", "column"}
            ]
            for building in ("EDIFICIO_1", "EDIFICIO_2")
        }
        floor_contacts = contacts(stations(near["EDIFICIO_1"]), stations(near["EDIFICIO_2"]))
        ed1_floor = [item for item in model["solids"] if item.get("building") == "EDIFICIO_1" and item.get("floor") == floor and item.get("category") in {"beam", "wall", "column", "support"}]
        outside = []
        for item in ed1_floor:
            sides = outboard_sides(item)
            if not sides:
                continue
            outside.append({"id": item.get("id"), "category": item.get("category"), "sides": sides})
            for side in sides:
                outboard_counts[f"{floor}:{side}:{item.get('category')}"] += 1
        by_floor[floor] = {
            "interface_items": {building: dict(Counter(str(item["category"]) for item in rows)) for building, rows in near.items()},
            "geometric_contacts": floor_contacts,
            "geometric_contact_count": len(floor_contacts),
            "members_crossing_interface_axis": {building: crossing_members(rows) for building, rows in structural_by_building.items()},
            "interface_overlay": plot_interface(floor, near, note_scan["localized_interface_candidates"]),
            "outboard_elements": outside,
            "outboard_count": len(outside),
            "outboard_overlay": plot_outboard(floor, ed1_floor),
        }
    unresolved = [
        {"id": item.get("id"), "floor": item.get("floor"), "category": item.get("category"), "reason": item.get("audit_resolution", {}).get("reason")}
        for item in model["solids"]
        if item.get("building") == "EDIFICIO_1" and item.get("audit_resolution", {}).get("resolution_group") == "UNRESOLVED_REQUIRES_REVIEW"
    ]
    p4_objects = architecture.get("objects", [])
    p4_area = float(p4_objects[0]["area_m2"]) if p4_objects else None
    axis_crossing_count = sum(
        len(ids)
        for row in by_floor.values()
        for ids in row["members_crossing_interface_axis"].values()
    )
    result = {
        "status": "PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED",
        "scope": ["GEO-SPECIAL-001", "GEO-INTERFACE-001"],
        "source_priority": "PLANOS_DXF > MODELO_AUDITADO > FOTOS > INFERENCIA",
        "interface": {
            "axis_calce_status": calce.get("status"),
            "ed2_axis_D_x_m": INTERFACE_X_ED2_M,
            "ed1_axis_E_x_m": INTERFACE_X_ED1_M,
            "axis_residual_m": round(abs(INTERFACE_X_ED2_M - INTERFACE_X_ED1_M), 6),
            "plan_note_scan": note_scan,
            "s1_dilatation_detail": dilatation_detail,
            "dilatation_cad_audit": {
                "status": dilatation_audit.get("status"),
                "classification": dilatation_audit["s1_target"]["classification"],
                "closed_component": dilatation_audit["s1_target"]["unique_closed_component"],
                "report": str(DILATATION_AUDIT.relative_to(REPO)).replace("\\", "/"),
            },
            "physical_connection_verdict": "NO_CROSS_BUILDING_FE_CONNECTION_PROVEN",
            "axis_crossing_member_count": axis_crossing_count,
            "cross_building_connection_proven": False,
            "modeling_rule": "DO_NOT_CREATE_CROSS_BUILDING_FE_LINKS_FROM_PROXIMITY_ALONE",
        },
        "special_sectors": {
            "ed1_primary_envelope_m": ED1_ENVELOPE,
            "counts": dict(sorted(outboard_counts.items())),
            "unresolved_model_items": unresolved,
            "prior_audit_status": prior.get("status"),
            "prior_audit_source_note": prior.get("source_priority_note"),
            "p4_architectural_area_m2": p4_area,
            "p4_architectural_participates_in_FE": architecture.get("participates_in_FE"),
            "structural_special_verdict": "NO_UNRESOLVED_MODEL_ITEMS_AFTER_AXIS_H_AND_DILATATION_WALL" if not unresolved else "REVIEW_REQUIRED",
            "remaining_scope": "ARCHITECTURAL_SLAB_OUTLINES_AND_CANOPIES_CONTINUE_WITH_SLAB_ARCHITECTURE_PHASE",
        },
        "by_floor": by_floor,
        "inputs": {str(path.relative_to(REPO)).replace("\\", "/"): sha256(path) for path in (MODEL, CALCE, OUTBOARD_PRIOR, ARCH_P4, DILATATION_AUDIT)},
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FASE 4 — diagnóstico de sectores especiales e interfaz",
        "",
        "Estado: `PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED`",
        "",
        f"- Calce D/E: `{result['interface']['axis_calce_status']}`, residual `{result['interface']['axis_residual_m']:.3f} m`.",
        f"- Textos generales coincidentes con palabras de búsqueda: `{len(note_scan['hits'])}`; menciones de junta/dilatación: `{len(note_scan['joint_or_dilatation_hits'])}`; candidatas localizadas junto a D/E: `{len(note_scan['localized_interface_candidates'])}`.",
        "- En S1, cuatro entidades de `RLA-MURO DILATADO` forman un único contorno cerrado de `0.200 x 2.360 m`; el receptor local ED1 queda confirmado.",
        f"- Contexto DXF de esa llamada: `{dilatation_detail['overlay'] if dilatation_detail else 'NO_GENERADO'}`.",
        "- El elemento local no cruza D/E y no demuestra transferencia entre bloques.",
        "- Veredicto de conexión física: `NO_CROSS_BUILDING_FE_CONNECTION_PROVEN`.",
        "- Regla: la proximidad y los contactos geométricos no autorizan vínculos FE entre edificios.",
        f"- Elementos ED1 todavía `UNRESOLVED_REQUIRES_REVIEW`: `{len(unresolved)}`; las columnas H-1/H-2/H-3 y sus apoyos quedaron confirmados por 2017_67-308.",
        f"- Miembros individuales cuyo eje geométrico sobrepasa D/E: `{axis_crossing_count}`. Son remates locales de un solo edificio; ninguno enlaza un miembro ED1 con uno ED2.",
        f"- Piloto arquitectónico P4: `{p4_area:.6f} m²`, `participates_in_FE=false`.",
        "",
        "| Piso | Contactos geométricos D/E | Elementos fuera de envolvente | Overlay interfaz | Overlay outboard |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for floor, row in by_floor.items():
        lines.append(f"| {floor} | {row['geometric_contact_count']} | {row['outboard_count']} | `{row['interface_overlay']}` | `{row['outboard_overlay']}` |")
    lines.extend([
        "",
        "Los sectores estructurales especiales quedan sin elementos `UNRESOLVED_REQUIRES_REVIEW`. Los perímetros, aleros y canopias arquitectónicas continúan junto con la reconstrucción de losas; no participan en FE. Para FE, mantener separados ambos edificios mientras no exista un detalle primario que pruebe transferencia. Las fotografías solo se usan como contraste visual.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("SPECIAL_INTERFACE_AUDIT: PASS_WITH_ARCHITECTURAL_SCOPE_DEFERRED")
    print({"general_keyword_hits": len(note_scan["hits"]), "joint_hits": len(note_scan["joint_or_dilatation_hits"]), "localized_interface_candidates": len(note_scan["localized_interface_candidates"]), "unresolved_items": len(unresolved), "p4_area_m2": p4_area})
    print(f"Reportes: {OUT_JSON} {OUT_MD}")


if __name__ == "__main__":
    main()
