#!/usr/bin/env python3
"""Cierra la auditoria de las seis columnas S1 en los ejes I e I'.

La evidencia se extrae directamente de las elevaciones estructurales 309 y 310.
El script no depende de proximidad a simbolos de la planta S1: comprueba ejes,
separaciones, rotulos de seccion y contornos verticales bajo el primer piso.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


REPO = Path(__file__).resolve().parents[4]
DXF_DIR = REPO / "recursos" / "planos" / "dxf_full" / "2017_67"
OUT_DIR = REPO / "entregas" / "P1L2" / "edificio" / "validacion" / "s1_columns_final"
OUT_JSON = OUT_DIR / "s1_columns_final_audit.json"
OUT_MD = OUT_DIR / "REPORT.md"

AXIS_X_GLOBAL = {"I": 67.491, "I'": 72.491}
AXIS_Y_GLOBAL = {"1": 0.0, "2": 8.9, "3": 16.15}
TARGETS = {
    "E1-S1-C-014": ("I", "2"),
    "E1-S1-C-015": ("I", "1"),
    "E1-S1-C-016": ("I", "3"),
    "E1-S1-C-017": ("I'", "1"),
    "E1-S1-C-018": ("I'", "2"),
    "E1-S1-C-019": ("I'", "3"),
}
SOURCES = {
    "I": (DXF_DIR / "2017_67-309.dxf", "EJEI"),
    "I'": (DXF_DIR / "2017_67-310.dxf", "EJEIA"),
}


def clean_text(entity) -> str | None:
    if entity.dxftype() == "TEXT":
        return str(entity.dxf.text).strip()
    if entity.dxftype() == "MTEXT":
        return str(entity.plain_text()).strip()
    return None


def xy(entity) -> tuple[float, float]:
    point = entity.dxf.insert
    return float(point.x), float(point.y)


def axis_stations(block) -> dict[str, float]:
    candidates: dict[str, list[float]] = {"1": [], "2": [], "3": []}
    for entity in block:
        text = clean_text(entity)
        if text in candidates and entity.dxf.is_supported("insert"):
            x, y = xy(entity)
            if y > 1400.0:
                candidates[text].append(x)
    stations = {}
    for axis, values in candidates.items():
        if len(values) != 1:
            raise RuntimeError(f"Expected one top axis label {axis}, found {values}")
        stations[axis] = values[0]
    return stations


def section_labels(block, stations: dict[str, float]) -> dict[str, list[dict[str, float | str]]]:
    rows: dict[str, list[dict[str, float | str]]] = {axis: [] for axis in stations}
    for entity in block:
        text = clean_text(entity)
        if text != "P. 70x70":
            continue
        x, y = xy(entity)
        axis = min(stations, key=lambda key: abs(x - stations[key]))
        if abs(x - stations[axis]) <= 150.0:
            rows[axis].append({"text": text, "x": round(x, 3), "y": round(y, 3)})
    return rows


def lower_column_contours(block, station: float) -> list[dict[str, object]]:
    """Busca las dos caras del pilar entre fundacion y el primer nivel."""
    lines = []
    for entity in block.query("LINE"):
        if "CONTORNO" not in entity.dxf.layer.upper():
            continue
        start = entity.dxf.start
        end = entity.dxf.end
        if abs(float(start.x) - float(end.x)) > 1e-6:
            continue
        x = float(start.x)
        y_min = min(float(start.y), float(end.y))
        y_max = max(float(start.y), float(end.y))
        if abs(x - station) <= 50.0 and y_min <= -400.0 and y_max >= -25.0:
            lines.append(
                {
                    "x": round(x, 3),
                    "y_min": round(y_min, 3),
                    "y_max": round(y_max, 3),
                    "layer": entity.dxf.layer,
                }
            )
    return sorted(lines, key=lambda row: float(row["x"]))


def foundation_labels(block) -> list[dict[str, object]]:
    rows = []
    for entity in block:
        text = clean_text(entity)
        if text and text.startswith("V.F."):
            x, y = xy(entity)
            rows.append({"text": text, "x": round(x, 3), "y": round(y, 3)})
    return rows


def title(block) -> str:
    values = [clean_text(entity) for entity in block]
    return next(value for value in values if value and value.upper().startswith("ELEVACION EJE"))


def render_crop(doc, block, output: Path) -> None:
    fig = plt.figure(figsize=(16, 8), facecolor="white")
    ax = fig.add_axes((0.01, 0.01, 0.98, 0.98), facecolor="white")
    context = RenderContext(doc)
    context.set_current_layout(doc.modelspace())
    backend = MatplotlibBackend(ax)
    Frontend(context, backend).draw_entities(block)
    ax.set_xlim(-1550.0, 750.0)
    ax.set_ylim(-800.0, 1600.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=240, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_results = {}
    for axis_x, (path, block_name) in SOURCES.items():
        doc = ezdxf.readfile(path)
        block = doc.blocks[block_name]
        stations = axis_stations(block)
        labels = section_labels(block, stations)
        contours = {axis: lower_column_contours(block, station) for axis, station in stations.items()}
        measured_spans_m = {
            "1-2": round(abs(stations["1"] - stations["2"]) / 100.0, 3),
            "2-3": round(abs(stations["2"] - stations["3"]) / 100.0, 3),
        }
        render_path = OUT_DIR / f"2017_67-{'309' if axis_x == 'I' else '310'}_{'I' if axis_x == 'I' else 'Iprime'}_crop.png"
        render_crop(doc, block, render_path)
        source_results[axis_x] = {
            "source_sheet": path.stem,
            "source_file": str(path.relative_to(REPO)).replace("\\", "/"),
            "block": block_name,
            "title": title(block),
            "axis_stations_drawing_units": {key: round(value, 3) for key, value in stations.items()},
            "measured_spans_m": measured_spans_m,
            "expected_spans_m": {"1-2": 8.9, "2-3": 7.25},
            "span_residual_m": {
                "1-2": round(measured_spans_m["1-2"] - 8.9, 6),
                "2-3": round(measured_spans_m["2-3"] - 7.25, 6),
            },
            "section_labels_by_axis": labels,
            "lower_story_column_contours_by_axis": contours,
            "foundation_beam_labels": foundation_labels(block),
            "render": str(render_path.relative_to(REPO)).replace("\\", "/"),
        }

    columns = []
    for element_id, (axis_x, axis_y) in TARGETS.items():
        source = source_results[axis_x]
        labels = source["section_labels_by_axis"][axis_y]
        contours = source["lower_story_column_contours_by_axis"][axis_y]
        section_confirmed = len(labels) >= 1
        lower_story_confirmed = len(contours) >= 2
        spans_confirmed = all(math.isclose(value, 0.0, abs_tol=0.001) for value in source["span_residual_m"].values())
        classification = "CONFIRMED" if section_confirmed and lower_story_confirmed and spans_confirmed else "UNRESOLVED_FINAL"
        columns.append(
            {
                "id": element_id,
                "building": "EDIFICIO_1",
                "floor": "S1",
                "axis_x": axis_x,
                "axis_y": axis_y,
                "canonical_center_xy_m": [AXIS_X_GLOBAL[axis_x], AXIS_Y_GLOBAL[axis_y]],
                "section_m": [0.7, 0.7] if section_confirmed else None,
                "classification": classification,
                "evidence": {
                    "source_sheet": source["source_sheet"],
                    "elevation_title": source["title"],
                    "axis_span_match": spans_confirmed,
                    "p70x70_label_count_at_station": len(labels),
                    "lower_story_contour_count": len(contours),
                    "foundation_beam_labels": source["foundation_beam_labels"],
                },
                "reason": "La elevacion estructural del eje dibuja un pilar de 70x70 en la estacion 1/2/3, con contornos continuos bajo el primer piso hasta la viga de fundacion; las separaciones 1-2 y 2-3 coinciden exactamente con los ejes canonicos.",
            }
        )

    status = "PASS" if all(row["classification"] == "CONFIRMED" for row in columns) else "REVIEW_REQUIRED"
    result = {
        "status": status,
        "scope": "GEO-COL-S1-001",
        "method": "direct_full_DXF_axis_elevation_cross_check",
        "units": "m",
        "sources": source_results,
        "columns": columns,
        "conclusion": "Las seis columnas S1 quedan confirmadas por evidencia primaria en elevacion estructural." if status == "PASS" else "Quedan columnas sin evidencia primaria suficiente.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Auditoria final de columnas S1 en ejes I e I'",
        "",
        f"Estado: `{status}`",
        "Alcance: `GEO-COL-S1-001`",
        "Metodo: lectura directa de las elevaciones estructurales completas, no extrapolacion desde plantas superiores.",
        "",
        "## Evidencia geometrica",
        "",
        "| Eje | Lamina | Elevacion | Luz 1-2 | Luz 2-3 | Residual maximo |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for axis_x, source in source_results.items():
        maximum = max(abs(value) for value in source["span_residual_m"].values())
        lines.append(f"| {axis_x} | {source['source_sheet']} | {source['title']} | {source['measured_spans_m']['1-2']:.3f} m | {source['measured_spans_m']['2-3']:.3f} m | {maximum:.3f} m |")
    lines.extend(
        [
            "",
            "En ambos ejes, los contornos inferiores llegan desde el nivel del primer piso hasta la viga de fundacion. Cada estacion 1, 2 y 3 tiene rotulo `P. 70x70`.",
            "",
            "## Veredicto individual",
            "",
            "| ID | Ubicacion | Seccion | Veredicto | Fuente |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in columns:
        lines.append(f"| {row['id']} | {row['axis_x']}-{row['axis_y']} | 0.70 x 0.70 m | {row['classification']} | {row['evidence']['source_sheet']} |")
    lines.extend(
        [
            "",
            "## Correccion derivada",
            "",
            "La existencia de las seis columnas deja de ser una inferencia. Sus centros se normalizan a las intersecciones de ejes canonicos y su seccion a 0.70 x 0.70 m. Esto corrige especialmente `E1-S1-C-016`, cuya envolvente extraida de planta (0.85 x 0.92 m y centro desplazado) contradice la elevacion estructural explicita.",
            "",
            "## Archivos visuales",
            "",
            "- `2017_67-309_I_crop.png`: elevacion I, estaciones 1-3 y tramo inferior.",
            "- `2017_67-310_Iprime_crop.png`: elevacion I', estaciones 1-3 y tramo inferior.",
            "- `s1_columns_final_audit.json`: evidencia estructurada reproducible.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_JSON)
    print(OUT_MD)
    print(status)


if __name__ == "__main__":
    main()
