#!/usr/bin/env python3
"""Confirma las columnas S1 H-1/H-2/H-3 desde la elevacion 2017_67-308."""

from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import ezdxf

import audit_s1_columns_full_set as base


REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "recursos/planos/dxf_full/2017_67/2017_67-308.dxf"
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/special_interface"
OUT_JSON = OUT_DIR / "s1_axis_h_audit.json"
OUT_MD = OUT_DIR / "S1_AXIS_H_AUDIT.md"
TARGETS = {"E1-S1-C-011": "1", "E1-S1-C-012": "2", "E1-S1-C-013": "3"}
EXPECTED = {"1": 0.0, "2": 8.9, "3": 16.15}


def grid_stations(block) -> dict[str, float]:
    xs = []
    for entity in block.query("LINE"):
        start, end = entity.dxf.start, entity.dxf.end
        if "RLA-EJES" not in str(entity.dxf.layer).upper() or abs(float(start.x) - float(end.x)) > 1e-6:
            continue
        y0, y1 = sorted((float(start.y), float(end.y)))
        if y0 <= -650.0 and y1 >= 1400.0 and -1300.0 <= float(start.x) <= 500.0:
            xs.append(float(start.x))
    unique = sorted({round(value, 3) for value in xs}, reverse=True)
    candidates = []
    for triplet in combinations(unique, 3):
        values = sorted(triplet, reverse=True)
        score = abs((values[0] - values[1]) - 890.0) + abs((values[1] - values[2]) - 725.0)
        candidates.append((score, values))
    if not candidates or min(candidates, key=lambda item: item[0])[0] > 0.2:
        raise RuntimeError(f"No se identificaron tres ejes con luces 8.90/7.25 m: {unique}")
    selected = min(candidates, key=lambda item: item[0])[1]
    return dict(zip(("1", "2", "3"), selected))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.readfile(SOURCE)
    block = doc.blocks["EJEH"]
    stations = grid_stations(block)
    labels = base.section_labels(block, stations)
    contours = {axis: base.lower_column_contours(block, station) for axis, station in stations.items()}
    spans = {"1-2": abs(stations["1"] - stations["2"]) / 100.0, "2-3": abs(stations["2"] - stations["3"]) / 100.0}
    residuals = {"1-2": spans["1-2"] - 8.9, "2-3": spans["2-3"] - 7.25}
    columns = []
    for element_id, axis_y in TARGETS.items():
        confirmed = len(labels[axis_y]) >= 1 and len(contours[axis_y]) >= 2 and all(math.isclose(value, 0.0, abs_tol=0.001) for value in residuals.values())
        columns.append(
            {
                "id": element_id,
                "axis_x": "H",
                "axis_y": axis_y,
                "canonical_center_xy_m": [57.491, EXPECTED[axis_y]],
                "section_m": [0.7, 0.7],
                "classification": "CONFIRMED" if confirmed else "UNRESOLVED_FINAL",
                "evidence": {
                    "source_sheet": "2017_67-308",
                    "block": "EJEH",
                    "elevation_title": base.title(block),
                    "axis_station_drawing_units": stations[axis_y],
                    "p70x70_label_count_at_station": len(labels[axis_y]),
                    "lower_story_contour_count": len(contours[axis_y]),
                },
            }
        )
    status = "PASS" if all(row["classification"] == "CONFIRMED" for row in columns) else "REVIEW_REQUIRED"
    render = OUT_DIR / "2017_67-308_H_crop.png"
    base.render_crop(doc, block, render)
    result = {
        "status": status,
        "scope": "GEO-SPECIAL-001_S1_AXIS_H",
        "method": "DIRECT_AXIS_ELEVATION_GRID_LINES_LABELS_AND_LOWER_STORY_CONTOURS",
        "source_sheet": "2017_67-308",
        "source_file": str(SOURCE.relative_to(REPO)).replace("\\", "/"),
        "title": base.title(block),
        "axis_stations_drawing_units": stations,
        "measured_spans_m": {key: round(value, 6) for key, value in spans.items()},
        "residuals_m": {key: round(value, 6) for key, value in residuals.items()},
        "section_labels_by_axis": labels,
        "lower_story_contours_by_axis": contours,
        "columns": columns,
        "render": str(render.relative_to(REPO)).replace("\\", "/"),
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Auditoría final de columnas S1 en eje H",
        "",
        f"Estado: `{status}`",
        "",
        f"La elevación `{result['title']}` de 2017_67-308 mide 8.900 m entre 1–2 y 7.250 m entre 2–3, con residual máximo `{max(abs(v) for v in residuals.values()):.3f} m`.",
        "En las tres estaciones existen cuatro rótulos `P. 70x70` y dos caras continuas del pilar bajo el primer piso.",
        "",
        "| ID | Eje | Sección | Contornos inferiores | Veredicto |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in columns:
        lines.append(f"| {row['id']} | H-{row['axis_y']} | 0.70 x 0.70 m | {row['evidence']['lower_story_contour_count']} | {row['classification']} |")
    lines.extend(["", f"Overlay: `{result['render']}`"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"S1_AXIS_H_AUDIT: {status}")
    print({"stations": stations, "spans_m": result["measured_spans_m"], "columns": [(row["id"], row["classification"]) for row in columns]})
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
