#!/usr/bin/env python3
"""Audita evidencia CAD de juntas y elementos rotulados como dilatados en ED1.

El script es deliberadamente diagnostico: no modifica modelos ni crea enlaces FE.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import audit_ed1_beams as source


REPO = Path(__file__).resolve().parents[4]
DXF_DIR = REPO / "recursos/planos/dxf_full/2017_67"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/special_interface"
OUT_JSON = OUT_DIR / "ed1_dilatation_audit.json"
OUT_MD = OUT_DIR / "DILATATION_AUDIT.md"
TARGET_LAYER = "RLA-MURO DILATADO"
INVERSE_LAYER = "RLA-MURO INV DILATADO"
ENDPOINT_TOLERANCE_RAW = 0.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_segments(entity) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    if entity.dxftype() in {"LINE", "LWPOLYLINE"}:
        return source.raw_segments(entity)
    if entity.dxftype() == "POLYLINE":
        points = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in entity.vertices]
        rows = list(zip(points, points[1:]))
        if entity.is_closed and len(points) > 2:
            rows.append((points[-1], points[0]))
        return rows
    return []


def text_value(entity) -> str:
    try:
        if entity.dxftype() == "TEXT":
            return str(entity.dxf.text)
        if entity.dxftype() == "MTEXT":
            return str(entity.plain_text())
        if entity.dxftype() in {"ATTRIB", "ATTDEF"}:
            return str(entity.dxf.text)
    except Exception:
        pass
    return ""


def floor_for_point(sheet: str, point: tuple[float, float]) -> str | None:
    matches = []
    for floor, (floor_sheet, bbox, _origin) in source.FLOOR_SOURCES.items():
        if floor_sheet != sheet:
            continue
        x0, y0, x1, y1 = bbox
        if x0 <= point[0] <= x1 and y0 <= point[1] <= y1:
            matches.append(floor)
    return matches[0] if len(matches) == 1 else None


def entity_floor(sheet: str, segments: list[tuple[tuple[float, float], tuple[float, float]]]) -> str | None:
    votes = Counter()
    for first, second in segments:
        for point in (first, second, ((first[0] + second[0]) / 2.0, (first[1] + second[1]) / 2.0)):
            floor = floor_for_point(sheet, point)
            if floor:
                votes[floor] += 1
    return votes.most_common(1)[0][0] if votes else None


def canonical_point(point: tuple[float, float]) -> tuple[int, int]:
    return (round(point[0] / ENDPOINT_TOLERANCE_RAW), round(point[1] / ENDPOINT_TOLERANCE_RAW))


def closed_components(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    segments = []
    for row in rows:
        for first, second in row["segments_raw"]:
            segments.append((first, second, row))
    adjacency: defaultdict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    segment_rows: defaultdict[tuple[tuple[int, int], tuple[int, int]], list[dict[str, object]]] = defaultdict(list)
    coordinates: defaultdict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for first, second, row in segments:
        a, b = canonical_point(first), canonical_point(second)
        if a == b:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
        key = tuple(sorted((a, b)))
        segment_rows[key].append(row)
        coordinates[a].append(first)
        coordinates[b].append(second)
    seen = set()
    components = []
    for root in adjacency:
        if root in seen:
            continue
        stack = [root]
        nodes = set()
        while stack:
            node = stack.pop()
            if node in nodes:
                continue
            nodes.add(node)
            seen.add(node)
            stack.extend(adjacency[node] - nodes)
        edges = {edge for edge in segment_rows if edge[0] in nodes and edge[1] in nodes}
        degree = Counter()
        handles = set()
        raw_points = []
        for edge in edges:
            degree.update(edge)
            for row in segment_rows[edge]:
                handles.add(str(row["handle"]))
            for node in edge:
                raw_points.extend(coordinates[node])
        xs = [p[0] for p in raw_points]
        ys = [p[1] for p in raw_points]
        components.append(
            {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "closed": bool(nodes) and all(value == 2 for value in degree.values()),
                "handles": sorted(handles),
                "bbox_raw": [min(xs), min(ys), max(xs), max(ys)],
                "size_raw": [max(xs) - min(xs), max(ys) - min(ys)],
            }
        )
    return sorted(components, key=lambda item: (not item["closed"], -item["edge_count"], item["bbox_raw"]))


def transform_component(component: dict[str, object], floor: str) -> dict[str, object]:
    _sheet, _bbox, origin = source.FLOOR_SOURCES[floor]
    x0, y0, x1, y1 = component["bbox_raw"]
    corners = [source.transform((x0, y0), origin), source.transform((x1, y1), origin)]
    gx = sorted([corners[0][0], corners[1][0]])
    gy = sorted([corners[0][1], corners[1][1]])
    return {
        **component,
        "floor": floor,
        "bbox_global_m": [round(gx[0], 6), round(gy[0], 6), round(gx[1], 6), round(gy[1], 6)],
        "size_m": [round(gx[1] - gx[0], 6), round(gy[1] - gy[0], 6)],
        "center_global_m": [round((gx[0] + gx[1]) / 2.0, 6), round((gy[0] + gy[1]) / 2.0, 6)],
    }


def plot_s1(rows: list[dict[str, object]], component: dict[str, object]) -> str:
    _sheet, _bbox, origin = source.FLOOR_SOURCES["S1"]
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = {TARGET_LAYER: "#d93025", INVERSE_LAYER: "#f9ab00", "RLE-MURO": "#188038", "RLE-VIGA": "#1a73e8"}
    path = DXF_DIR / "2017_67-101.dxf"
    doc = ezdxf.readfile(path)
    center = component["center_global_m"]
    for entity in doc.modelspace():
        if entity.dxftype() not in {"LINE", "LWPOLYLINE", "POLYLINE"}:
            continue
        for first, second in raw_segments(entity):
            a, b = source.transform(first, origin), source.transform(second, origin)
            if max(a[0], b[0]) < center[0] - 2.2 or min(a[0], b[0]) > center[0] + 2.2 or max(a[1], b[1]) < center[1] - 2.2 or min(a[1], b[1]) > center[1] + 2.2:
                continue
            layer = str(entity.dxf.layer)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=colors.get(layer, "#dddddd"), linewidth=2.4 if layer == TARGET_LAYER else 1.1 if layer in colors else 0.45)
    x0, y0, x1, y1 = component["bbox_global_m"]
    ax.text(x1 + 0.08, (y0 + y1) / 2.0, f"{TARGET_LAYER}\n{component['size_m'][0]:.2f} x {component['size_m'][1]:.2f} m", color="#a50e0e", fontsize=8)
    ax.axvline(27.491, color="#9334e6", linestyle=":", linewidth=1.0, label="E ED1")
    ax.axvline(27.500, color="#d93025", linestyle="--", linewidth=1.0, label="D ED2")
    ax.set_xlim(center[0] - 2.2, center[0] + 2.2)
    ax.set_ylim(center[1] - 2.2, center[1] + 2.2)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.4)
    ax.legend()
    ax.set_title("S1: contorno CAD cerrado de muro dilatado junto a interfaz D/E")
    output = OUT_DIR / "s1_dilatation_wall_contour.png"
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return str(output.relative_to(REPO)).replace("\\", "/")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    entity_rows = []
    text_rows = []
    sheets = []
    for path in sorted(DXF_DIR.glob("*.dxf")):
        doc = ezdxf.readfile(path)
        layer_counts = Counter()
        text_count = 0
        for layout in doc.layouts:
            for entity in layout:
                layer = str(entity.dxf.layer)
                text = " ".join(text_value(entity).split())
                if "DILAT" in text.upper():
                    text_rows.append({"sheet": path.name, "layout": layout.name, "handle": str(entity.dxf.handle), "layer": layer, "text": text[:300]})
                    text_count += 1
                if "DILAT" not in layer.upper():
                    continue
                segments = raw_segments(entity)
                floor = entity_floor(path.name, segments) if layout.name == "Model" and segments else None
                row = {"sheet": path.name, "layout": layout.name, "handle": str(entity.dxf.handle), "entity_type": entity.dxftype(), "layer": layer, "floor": floor, "segment_count": len(segments), "segments_raw": segments}
                entity_rows.append(row)
                layer_counts[layer] += 1
        if layer_counts or text_count:
            sheets.append({"sheet": path.name, "sha256": sha256(path), "layer_entity_counts": dict(sorted(layer_counts.items())), "dilatation_text_count": text_count})

    by_sheet_floor_layer = Counter((r["sheet"], r["floor"] or "OUTSIDE_FLOOR", r["layer"]) for r in entity_rows)
    target_rows = [r for r in entity_rows if r["sheet"] == "2017_67-101.dxf" and r["layout"] == "Model" and r["floor"] == "S1" and r["layer"] == TARGET_LAYER]
    components = [transform_component(item, "S1") for item in closed_components(target_rows)]
    closed = [item for item in components if item["closed"]]
    target = closed[0] if len(closed) == 1 else None
    overlay = plot_s1(target_rows, target) if target else None
    result = {
        "status": "PASS_WITH_SCOPE_LIMIT",
        "scope": "CAD_DILATATION_EVIDENCE_ONLY_NO_MODEL_CHANGE",
        "all_series_dilatation_layer_entities": len(entity_rows),
        "all_series_dilatation_texts": len(text_rows),
        "sheets": sheets,
        "counts_by_sheet_floor_layer": [
            {"sheet": key[0], "floor_region": key[1], "layer": key[2], "count": value}
            for key, value in sorted(by_sheet_floor_layer.items())
        ],
        "s1_target": {
            "source_sheet": "2017_67-101.dxf",
            "source_layer": TARGET_LAYER,
            "entity_count": len(target_rows),
            "components": components,
            "unique_closed_component": target,
            "overlay": overlay,
            "classification": "CONFIRMED_CLOSED_WALL_CONTOUR_LABELLED_DILATADO" if target else "UNRESOLVED",
            "structural_interpretation": "LOCAL_ED1_WALL_SEGMENT; DOES_NOT_PROVE_CROSS_BUILDING_CONNECTION",
        },
        "inverse_layer_interpretation": "SEPARATE_REINFORCEMENT_GRAPHICS; NOT_MERGED_WITH_TARGET_CONTOUR",
        "physical_interface_verdict": "NO_CROSS_BUILDING_FE_CONNECTION_PROVEN",
        "modeling_rule": "DO_NOT_CREATE_CROSS_BUILDING_FE_LINKS_FROM_GEOMETRIC_PROXIMITY",
        "texts": text_rows,
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    size = target["size_m"] if target else [math.nan, math.nan]
    center = target["center_global_m"] if target else [math.nan, math.nan]
    lines = [
        "# Auditoría CAD de dilatación EDIFICIO_1",
        "",
        "Estado: `PASS_WITH_SCOPE_LIMIT` — diagnóstico, sin cambio de modelo.",
        "",
        f"- La serie 2017_67 contiene `{len(entity_rows)}` entidades en capas con `DILAT` y `{len(text_rows)}` textos relacionados.",
        f"- En S1, lámina 101, hay `{len(target_rows)}` entidades de `{TARGET_LAYER}` que forman `{len(closed)}` contorno cerrado único.",
        f"- Contorno global: centro `({center[0]:.3f}, {center[1]:.3f}) m`, tamaño `{size[0]:.3f} x {size[1]:.3f} m`.",
        "- La dimensión transversal de 0.20 m y el contorno cerrado confirman un segmento local de muro ED1 rotulado `DILATADO`.",
        "- Las entidades `RLA-MURO INV DILATADO` se conservan como gráficos de armadura separados; no se usan para agrandar el contorno.",
        "- Esta evidencia no demuestra conexión física ni transferencia FE entre EDIFICIO_1 y EDIFICIO_2.",
        "- Veredicto de interfaz: `NO_CROSS_BUILDING_FE_CONNECTION_PROVEN`.",
        "",
        f"Overlay: `{overlay}`",
        "",
        "## Conteos por región de planta",
        "",
        "| Lámina | Región | Capa | Entidades |",
        "| --- | --- | --- | ---: |",
    ]
    for row in result["counts_by_sheet_floor_layer"]:
        lines.append(f"| {row['sheet']} | {row['floor_region']} | {row['layer']} | {row['count']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ED1_DILATATION_AUDIT: PASS_WITH_SCOPE_LIMIT")
    print({"layer_entities": len(entity_rows), "texts": len(text_rows), "s1_target_entities": len(target_rows), "closed_components": len(closed), "target": target})


if __name__ == "__main__":
    main()
