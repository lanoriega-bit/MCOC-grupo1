#!/usr/bin/env python3
"""Audita labels y layers CAD con evidencia de propiedades estructurales."""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from model_contract import EXPECTED_FLOORS

REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

MODEL = UNITY / "model_combined_viewer.json"
OUT_JSON = DATA / "cad_property_audit.json"
OUT_MD = VALID / "cad_property_audit.md"

ASSOCIATION_MAX_M = 2.0

BEAM_RE = re.compile(r"\bV\.?\s*(F\.?)?\s*(\d{1,3})\s*/\s*(\d{1,3})\b", re.IGNORECASE)
MHA_RE = re.compile(r"M\.?\s*H\.?\s*A\.?")
THICKNESS_RE = re.compile(r"\bE\s*=?\s*(\d{1,3})\b", re.IGNORECASE)
COLUMN_RE = re.compile(r"\b(\d{2,3})\s*[Xx]\s*(\d{2,3})\b")
MATERIAL_RE = re.compile(r"HORMIGON|HORMIGON ARMADO|H\.?\s*A\.?|M\.?\s*H\.?\s*A\.?|ACERO|A\s*63|A63", re.IGNORECASE)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def norm_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).replace("\u00d7", "x").strip()).upper()


def round3(value: float) -> float:
    return round(float(value), 3)


def section_property(kind: str, a_cm: int, b_cm: int) -> dict[str, object]:
    return {
        "kind": kind,
        "a_cm": a_cm,
        "b_cm": b_cm,
        "a_m": round(a_cm / 100.0, 3),
        "b_m": round(b_cm / 100.0, 3),
        "source": "TEXT_LABEL",
    }


def parse_property_label(label: dict[str, object]) -> dict[str, object] | None:
    text = norm_text(label.get("text", ""))
    category = str(label.get("category", ""))
    if not text:
        return None

    beam = BEAM_RE.search(text)
    if beam:
        is_foundation = bool(beam.group(1)) or "V.F" in text or "VF" in text
        kind = "foundation_beam_section" if is_foundation else "beam_section"
        a_cm = int(beam.group(2))
        b_cm = int(beam.group(3))
        return {
            "property_type": kind,
            "target_categories": ["support"] if is_foundation else ["beam"],
            "text": label.get("text"),
            "normalized_text": text,
            "property": section_property(kind, a_cm, b_cm),
        }

    if text.startswith("V.F") or text.startswith("VF"):
        return {
            "property_type": "foundation_beam_label_incomplete",
            "target_categories": ["support"],
            "text": label.get("text"),
            "normalized_text": text,
            "property": {"kind": "incomplete_section", "source": "TEXT_LABEL"},
        }

    wall_thickness = THICKNESS_RE.search(text)
    if MHA_RE.search(text) and wall_thickness:
        thickness_cm = int(wall_thickness.group(1))
        return {
            "property_type": "wall_thickness",
            "target_categories": ["wall"],
            "text": label.get("text"),
            "normalized_text": text,
            "property": {
                "kind": "wall_thickness",
                "thickness_cm": thickness_cm,
                "thickness_m": round(thickness_cm / 100.0, 3),
                "source": "TEXT_LABEL",
            },
        }

    column = COLUMN_RE.search(text)
    if column and ("column" in category or "PILAR" in text or "COL" in text or len(text) <= 12):
        a_cm = int(column.group(1))
        b_cm = int(column.group(2))
        return {
            "property_type": "column_section",
            "target_categories": ["column"],
            "text": label.get("text"),
            "normalized_text": text,
            "property": section_property("column_section", a_cm, b_cm),
        }

    material = MATERIAL_RE.search(text)
    if material:
        return {
            "property_type": "material_text_hint",
            "target_categories": [],
            "text": label.get("text"),
            "normalized_text": text,
            "property": {"kind": "material_text_hint", "match": material.group(0), "source": "TEXT_LABEL"},
        }
    return None


def point_xy(obj: dict[str, object]) -> tuple[float, float]:
    p = obj.get("point") or obj.get("center")
    return float(p[0]), float(p[1])


def distance_point_to_segment(px: float, py: float, a: list[float], b: list[float]) -> float:
    ax, ay = float(a[0]), float(a[1])
    bx, by = float(b[0]), float(b[1])
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    c2 = vx * vx + vy * vy
    if c2 <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / c2))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy)


def distance_to_solid(label: dict[str, object], solid: dict[str, object]) -> float:
    px, py = point_xy(label)
    if "start" in solid and "end" in solid:
        return distance_point_to_segment(px, py, solid["start"], solid["end"])
    cx, cy = point_xy(solid)
    return math.hypot(px - cx, py - cy)


def nearest_solid(label: dict[str, object], categories: list[str], solids: list[dict[str, object]]) -> dict[str, object] | None:
    if not categories:
        return None
    building = label.get("building")
    floor = label.get("floor")
    candidates = [
        solid for solid in solids
        if solid.get("building") == building and solid.get("floor") == floor and solid.get("category") in categories
    ]
    if not candidates:
        return None
    best = min(candidates, key=lambda solid: distance_to_solid(label, solid))
    dist = distance_to_solid(label, best)
    return {
        "solidTag": best.get("solidTag"),
        "category": best.get("category"),
        "distance_m": round3(dist),
        "status": "ASSOCIATED_NEAREST" if dist <= ASSOCIATION_MAX_M else "NEAREST_OVER_LIMIT",
        "target_source_dxf": best.get("source_dxf"),
        "target_confidence": best.get("confidence"),
    }


def audit_layers(model: dict[str, object]) -> dict[str, object]:
    solid_layer_category = Counter()
    label_layer_category = Counter()
    source_dxf_layer = Counter()
    layer_roles: dict[str, set[str]] = defaultdict(set)
    for solid in model.get("solids", []):
        layer = str(solid.get("source_layer", "NO_SOURCE_LAYER"))
        cat = str(solid.get("category", "NO_CATEGORY"))
        solid_layer_category[f"{layer}:{cat}"] += 1
        source_dxf_layer[f"{solid.get('source_dxf')}:{layer}"] += 1
        layer_roles[layer].add(cat)
    for label in model.get("labels", []):
        layer = str(label.get("source_layer", "NO_SOURCE_LAYER"))
        cat = str(label.get("category", "NO_CATEGORY"))
        label_layer_category[f"{layer}:{cat}"] += 1
        layer_roles[layer].add(cat)
    return {
        "solid_layer_category_counts": dict(sorted(solid_layer_category.items())),
        "label_layer_category_counts": dict(sorted(label_layer_category.items())),
        "source_dxf_layer_counts": dict(sorted(source_dxf_layer.items())),
        "layer_roles": {layer: sorted(roles) for layer, roles in sorted(layer_roles.items())},
    }


def property_key(item: dict[str, object]) -> str:
    prop = item["property"]
    if item["property_type"] in {"beam_section", "foundation_beam_section", "column_section"}:
        return f"{item['property_type']}:{prop['a_cm']}/{prop['b_cm']}"
    if item["property_type"] == "wall_thickness":
        return f"wall_thickness:e={prop['thickness_cm']}"
    return f"{item['property_type']}:{item['normalized_text']}"


def summarize_properties(properties: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, dict[str, object]] = {}
    for item in properties:
        key = property_key(item)
        if key not in groups:
            groups[key] = {
                "key": key,
                "property_type": item["property_type"],
                "property": item["property"],
                "count": 0,
                "texts": Counter(),
                "buildings": Counter(),
                "floors": Counter(),
                "source_dxfs": Counter(),
            }
        group = groups[key]
        group["count"] += 1
        group["texts"][str(item["text"])] += 1
        group["buildings"][str(item["building"])] += 1
        group["floors"][str(item["floor"])] += 1
        group["source_dxfs"][str(item["source_dxf"])] += 1
    out = []
    for group in groups.values():
        row = dict(group)
        row["texts"] = dict(row["texts"].most_common(10))
        row["buildings"] = dict(row["buildings"].most_common())
        row["floors"] = dict(sorted(row["floors"].items(), key=lambda item: EXPECTED_FLOORS.index(item[0]) if item[0] in EXPECTED_FLOORS else 99))
        row["source_dxfs"] = dict(row["source_dxfs"].most_common(10))
        out.append(row)
    return sorted(out, key=lambda row: (str(row["property_type"]), str(row["key"])))


def build_property_rows(model: dict[str, object]) -> list[dict[str, object]]:
    solids = list(model.get("solids", []))
    rows = []
    for label in model.get("labels", []):
        parsed = parse_property_label(label)
        if not parsed:
            continue
        association = nearest_solid(label, parsed["target_categories"], solids)
        row = {
            "labelTag": label.get("labelTag"),
            "building": label.get("building"),
            "floor": label.get("floor"),
            "source_floor": label.get("source_floor"),
            "level_kind": label.get("level_kind"),
            "source_dxf": label.get("source_dxf"),
            "source_layer": label.get("source_layer"),
            "category": label.get("category"),
            "point_m": [round3(value) for value in label.get("point", [])[:3]],
            **parsed,
            "association": association,
        }
        rows.append(row)
    return rows


def status(properties: list[dict[str, object]]) -> str:
    unassociated = [row for row in properties if row["target_categories"] and (not row["association"] or row["association"]["status"] != "ASSOCIATED_NEAREST")]
    incomplete = [row for row in properties if row["property_type"].endswith("incomplete")]
    if unassociated or incomplete:
        return "PASS_WITH_REVIEW_NOTES"
    return "PASS"


def fmt_property(prop: dict[str, object]) -> str:
    kind = prop.get("kind")
    if kind in {"beam_section", "foundation_beam_section", "column_section"}:
        return f"{prop['a_cm']}/{prop['b_cm']} cm"
    if kind == "wall_thickness":
        return f"e={prop['thickness_cm']} cm"
    if kind == "material_text_hint":
        return str(prop.get("match"))
    return str(kind)


def write_markdown(report: dict[str, object]) -> None:
    properties = report["property_labels"]
    summary = report["property_summary"]
    layers = report["layer_audit"]
    by_type = Counter(row["property_type"] for row in properties)
    assoc_status = Counter((row["association"] or {"status": "NO_TARGET"})["status"] for row in properties)
    lines = [
        "# Auditoria CAD de propiedades",
        "",
        f"- Estado: **{report['status']}**",
        f"- Labels revisados: {report['label_count']}",
        f"- Labels con propiedad/indicio estructural: {len(properties)}",
        f"- Distancia maxima asociacion tentativa: {ASSOCIATION_MAX_M} m",
        "- La auditoria no modifica el modelo 3D ni asigna propiedades globales de material.",
        "",
        "## Labels por tipo",
        "",
        "| Tipo | Conteo |",
        "|---|---:|",
    ]
    for key, value in sorted(by_type.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend([
        "",
        "## Asociacion tentativa",
        "",
        "| Estado | Conteo |",
        "|---|---:|",
    ])
    for key, value in sorted(assoc_status.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend([
        "",
        "## Evidencia textual agrupada",
        "",
        "| Tipo | Propiedad | Conteo | Edificios | Pisos | Textos ejemplo |",
        "|---|---|---:|---|---|---|",
    ])
    for row in summary:
        texts = "; ".join(list(row["texts"].keys())[:4])
        buildings = ", ".join(row["buildings"].keys())
        floors = ", ".join(row["floors"].keys())
        lines.append(f"| {row['property_type']} | {fmt_property(row['property'])} | {row['count']} | {buildings} | {floors} | {texts} |")

    lines.extend([
        "",
        "## Layers estructurales usados",
        "",
        "| Layer | Roles detectados |",
        "|---|---|",
    ])
    for layer, roles in layers["layer_roles"].items():
        lines.append(f"| {layer} | {', '.join(roles)} |")

    review = [row for row in properties if row["target_categories"] and (not row["association"] or row["association"]["status"] != "ASSOCIATED_NEAREST")]
    if review:
        lines.extend([
            "",
            "## Labels a revisar",
            "",
            "| Label | Tipo | Texto | Edificio | Piso | Asociacion | Distancia [m] |",
            "|---|---|---|---|---|---|---:|",
        ])
        for row in review[:30]:
            assoc = row["association"] or {"solidTag": "NO_CANDIDATE", "distance_m": ""}
            lines.append(
                f"| {row['labelTag']} | {row['property_type']} | {row['text']} | {row['building']} | {row['floor']} | "
                f"{assoc.get('solidTag')} | {assoc.get('distance_m', '')} |"
            )

    lines.extend([
        "",
        "## Criterio",
        "",
        "- Las secciones y espesores reportados provienen de texto CAD, no de inferencia resistente.",
        "- `M.H.A.` se conserva como indicio textual de muro de hormigon armado cuando aparece en el label; no se transforma en material global del modelo.",
        "- Las asociaciones son nearest-neighbor sobre el mismo edificio y piso; deben revisarse visualmente antes de usar en calculo resistente.",
    ])
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    model = load(MODEL)
    properties = build_property_rows(model)
    report = {
        "status": status(properties),
        "check": "CAD_PROPERTY_LABEL_AND_LAYER_AUDIT",
        "method": "Parsea labels CAD de secciones/espesores/material hints y resume layers fuente usados por elementos del viewer combinado.",
        "association_max_m": ASSOCIATION_MAX_M,
        "label_count": len(model.get("labels", [])),
        "solid_count": len(model.get("solids", [])),
        "property_labels": properties,
        "property_summary": summarize_properties(properties),
        "layer_audit": audit_layers(model),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report)
    print("CAD_PROPERTY_AUDIT:", report["status"])
    print("Labels:", report["label_count"], "Propiedades/indicios:", len(properties))
    print("Reportes:", OUT_JSON, OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
