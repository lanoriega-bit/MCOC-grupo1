#!/usr/bin/env python3
"""Diagnostica por que la panelizacion tributaria no cubre todo el edificio.

No modifica geometria ni cargas. Compara el criterio vigente con una barrida
de tolerancias y clasifica las celdas excluidas por borde sin soporte.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from p1l3.panos import (  # noqa: E402
    FLOORS,
    beam_lines,
    build_panos,
    edge_cover,
    grid_from_beams,
    load_model,
)
from p1l3.rutas import COMBINED_VIEWER_JSON, RESULTS_DIR  # noqa: E402

OUT_DIR = RESULTS_DIR / "a1a2"
OUT_JSON = OUT_DIR / "tributary_coverage_audit.json"
OUT_MD = OUT_DIR / "tributary_coverage_audit.md"
HISTORICAL = ROOT / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "tributary_areas.json"


def group_lines(model: dict) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for line in beam_lines(model):
        grouped[(line["building"], line["floor"])].append(line)
    return grouped


def wall_lines(model: dict) -> list[dict]:
    lines = []
    for solid in model["solids"]:
        if solid.get("category") != "wall":
            continue
        x1, y1, z1 = solid["start"]
        x2, y2, z2 = solid["end"]
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        orient = "H" if dy < 1e-3 else "V" if dx < 1e-3 else None
        if orient is None:
            continue
        lines.append(
            {
                "id": solid.get("id"),
                "building": solid.get("building"),
                "floor": solid.get("floor"),
                "orient": orient,
                "x1": x1,
                "y1": y1,
                "z1": z1,
                "x2": x2,
                "y2": y2,
                "z2": z2,
                "c": y1 if orient == "H" else x1,
                "lo": min(x1, x2) if orient == "H" else min(y1, y2),
                "hi": max(x1, x2) if orient == "H" else max(y1, y2),
                "receiver_type": "wall",
            }
        )
    return lines


def cell_diagnostics(
    support_lines: list[dict],
    clust_tol: float,
    beam_tol: float,
    min_cover: float,
    grid_lines: list[dict] | None = None,
) -> dict:
    grid_lines = support_lines if grid_lines is None else grid_lines
    gx = grid_from_beams(grid_lines, "V", clust_tol)
    gy = grid_from_beams(grid_lines, "H", clust_tol)
    excluded = []
    accepted_area = 0.0
    grid_area = 0.0
    unsupported_edges: Counter[str] = Counter()

    for i in range(max(0, len(gx) - 1)):
        for j in range(max(0, len(gy) - 1)):
            xlo, xhi = gx[i], gx[i + 1]
            ylo, yhi = gy[j], gy[j + 1]
            width, height = xhi - xlo, yhi - ylo
            if width < 0.8 or height < 0.8:
                continue
            area = width * height
            grid_area += area
            edges = {
                "bottom": ("H", ylo, xlo, xhi),
                "top": ("H", yhi, xlo, xhi),
                "left": ("V", xlo, ylo, yhi),
                "right": ("V", xhi, ylo, yhi),
            }
            covers = {
                name: edge_cover(support_lines, orient, coord, a, b, tol=beam_tol) / (b - a)
                for name, (orient, coord, a, b) in edges.items()
            }
            missing = sorted(name for name, fraction in covers.items() if fraction < min_cover - 1e-9)
            if missing:
                unsupported_edges.update(missing)
                excluded.append(
                    {
                        "bbox_m": [round(xlo, 3), round(ylo, 3), round(xhi, 3), round(yhi, 3)],
                        "area_m2": round(area, 3),
                        "missing_edges": missing,
                        "coverage": {name: round(value, 4) for name, value in covers.items()},
                    }
                )
            else:
                accepted_area += area

    excluded.sort(key=lambda row: row["area_m2"], reverse=True)
    return {
        "grid_x_count": len(gx),
        "grid_y_count": len(gy),
        "grid_cell_area_m2": round(grid_area, 3),
        "accepted_area_m2": round(accepted_area, 3),
        "excluded_area_m2": round(grid_area - accepted_area, 3),
        "accepted_fraction_of_grid": round(accepted_area / grid_area, 4) if grid_area else 0.0,
        "unsupported_edges": dict(sorted(unsupported_edges.items())),
        "largest_excluded_cells": excluded[:10],
    }


def audit_historical_visual_layers(model: dict, historical: dict) -> list[dict]:
    """Audita los poligonos de visualizacion de las dos etapas historicas.

    ``areas`` distribuye la losa a vigas y ``point_areas`` presenta la etapa
    posterior hacia receptores verticales. Ambas describen la misma carga, no
    dos superficies sumables. El campo ``area_m2`` puede acumular componentes
    que el unico ``polygon`` de cada entrada no conserva, por lo que tambien se
    mide explicitamente esa diferencia.
    """
    rows = []
    for dataset, transfer_stage in (
        ("areas", "losa_a_vigas"),
        ("point_areas", "vigas_a_receptores_verticales"),
    ):
        for building in ("EDIFICIO_1", "EDIFICIO_2"):
            for floor in FLOORS:
                entries = [
                    item
                    for item in historical.get(dataset, [])
                    if item["building"] == building and item["floor"] == floor
                ]
                polygons = []
                missing_polygon_area = 0.0
                invalid_count = 0
                polygon_area_mismatch_count = 0
                polygon_area_abs_error = 0.0
                for item in entries:
                    declared_item_area = float(item["area_m2"])
                    coords = [(point["x"], point["y"]) for point in item.get("polygon", [])]
                    if len(coords) < 3:
                        missing_polygon_area += declared_item_area
                        if declared_item_area > 0.01:
                            polygon_area_mismatch_count += 1
                            polygon_area_abs_error += declared_item_area
                        continue
                    polygon = Polygon(coords)
                    if not polygon.is_valid:
                        invalid_count += 1
                        polygon = polygon.buffer(0)
                    polygon_area = polygon.area if not polygon.is_empty else 0.0
                    item_error = abs(declared_item_area - polygon_area)
                    if item_error > 0.01:
                        polygon_area_mismatch_count += 1
                    polygon_area_abs_error += item_error
                    if polygon_area > 0:
                        polygons.append(polygon)

                merged = unary_union(polygons) if polygons else Polygon()
                raw_polygon_area = sum(polygon.area for polygon in polygons)
                declared_area = sum(float(item["area_m2"]) for item in entries)

                cad_lines = []
                for segment in model["segments"]:
                    if (
                        segment.get("building") == building
                        and segment.get("floor") == floor
                        and segment.get("category") == "slab_edge"
                        and len(segment.get("points", [])) >= 2
                    ):
                        cad_lines.append(LineString([(p[0], p[1]) for p in segment["points"]]))
                cad_length = sum(line.length for line in cad_lines)
                boundary = merged.boundary

                def nearby_length(tolerance: float) -> float:
                    if boundary.is_empty:
                        return 0.0
                    zone = boundary.buffer(tolerance)
                    return sum(line.intersection(zone).length for line in cad_lines)

                rows.append(
                    {
                        "dataset": dataset,
                        "transfer_stage": transfer_stage,
                        "building": building,
                        "floor": floor,
                        "entries": len(entries),
                        "declared_area_m2": round(declared_area, 4),
                        "polygon_union_area_m2": round(merged.area, 4),
                        "raw_polygon_area_m2": round(raw_polygon_area, 4),
                        "overlap_area_m2": round(max(0.0, raw_polygon_area - merged.area), 6),
                        "nonzero_area_without_polygon_m2": round(missing_polygon_area, 4),
                        "invalid_polygon_count": invalid_count,
                        "polygon_area_mismatch_count": polygon_area_mismatch_count,
                        "polygon_area_abs_error_m2": round(polygon_area_abs_error, 4),
                        "union_vs_declared_rel_error": round(
                            abs(merged.area - declared_area) / declared_area if declared_area else 0.0,
                            6,
                        ),
                        "cad_slab_edge_length_m": round(cad_length, 3),
                        "cad_edge_near_union_boundary_frac_0_15m": round(
                            nearby_length(0.15) / cad_length if cad_length else 0.0, 4
                        ),
                        "cad_edge_near_union_boundary_frac_0_60m": round(
                            nearby_length(0.60) / cad_length if cad_length else 0.0, 4
                        ),
                    }
                )
    return rows


def main() -> None:
    model = load_model(COMBINED_VIEWER_JSON)
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    historical_visual_layers = audit_historical_visual_layers(model, historical)
    grouped = group_lines(model)
    walls_grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for line in wall_lines(model):
        walls_grouped[(line["building"], line["floor"])].append(line)
    rows = []
    for building in ("EDIFICIO_1", "EDIFICIO_2"):
        for floor in FLOORS:
            lines = grouped.get((building, floor), [])
            walls = walls_grouped.get((building, floor), [])
            beam_only = cell_diagnostics(lines, 0.7, 0.35, 0.5)
            beam_and_wall = cell_diagnostics(lines + walls, 0.7, 0.35, 0.5, grid_lines=lines)
            row = {
                "building": building,
                "floor": floor,
                "beam_lines": len(lines),
                "horizontal": sum(line["orient"] == "H" for line in lines),
                "vertical": sum(line["orient"] == "V" for line in lines),
                "wall_horizontal": sum(line["orient"] == "H" for line in walls),
                "wall_vertical": sum(line["orient"] == "V" for line in walls),
                "accepted_with_beams_and_walls_m2": beam_and_wall["accepted_area_m2"],
                "area_recovered_by_walls_m2": round(
                    beam_and_wall["accepted_area_m2"] - beam_only["accepted_area_m2"], 3
                ),
                "fraction_with_beams_and_walls": beam_and_wall["accepted_fraction_of_grid"],
                "historical_area_m2": float(historical["buildings"][building][floor]["area_m2"]),
            }
            row.update(beam_only)
            row["current_fraction_of_historical"] = round(
                row["accepted_area_m2"] / row["historical_area_m2"], 4
            )
            rows.append(row)

    sensitivity = []
    for beam_tol in (0.35, 0.50, 0.70):
        for min_cover in (0.30, 0.50, 0.70, 0.90):
            panels, stats = build_panos(
                model,
                clust_tol=0.7,
                beam_tol=beam_tol,
                min_cover=min_cover,
            )
            sensitivity.append(
                {
                    "beam_tol_m": beam_tol,
                    "min_cover": min_cover,
                    "panels": len(panels),
                    "area_m2": round(sum(panel.area_m2 for panel in panels), 3),
                    "excluded_unsupported": stats["excluded_unsupported"],
                }
            )

    result = {
        "status": "REVIEW_REQUIRED",
        "source_model": str(COMBINED_VIEWER_JSON),
        "historical_comparison_source": str(HISTORICAL),
        "historical_comparison_status": (
            "REFERENCE_ONLY: el archivo no conserva el algoritmo que genero sus poligonos; "
            "su area no se adopta como verdad sin reconstruccion desde RLE-LOSA."
        ),
        "historical_visual_layers_audit": historical_visual_layers,
        "current_parameters": {"clust_tol_m": 0.7, "beam_tol_m": 0.35, "min_cover": 0.5},
        "rows": rows,
        "sensitivity": sensitivity,
        "interpretation_rule": (
            "Una mejora grande al variar tolerancias indica problema numerico; "
            "una mejora pequena indica geometria receptora incompleta o tipologia no rectangular."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Auditoria de cobertura tributaria",
        "",
        "Estado: **REVIEW_REQUIRED**. Este informe no modifica cargas ni geometria.",
        "",
        "## Diagnostico por edificio y piso",
        "",
        "| Edificio | Piso | Vigas H/V | Muros H/V | Area grilla [m2] | Solo vigas [m2] | + muros [m2] | Historica [m2] | Actual/historica |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['building']} | {row['floor']} | {row['horizontal']}/{row['vertical']} | "
            f"{row['wall_horizontal']}/{row['wall_vertical']} | {row['grid_cell_area_m2']:.3f} | "
            f"{row['accepted_area_m2']:.3f} | {row['accepted_with_beams_and_walls_m2']:.3f} | "
            f"{row['historical_area_m2']:.3f} | {row['current_fraction_of_historical']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Sensibilidad de tolerancias",
            "",
            "| Tolerancia viga [m] | Cobertura minima | Panos | Area [m2] | Excluidas |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in sensitivity:
        lines.append(
            f"| {item['beam_tol_m']:.2f} | {item['min_cover']:.2f} | {item['panels']} | "
            f"{item['area_m2']:.3f} | {item['excluded_unsupported']} |"
        )
    lines.extend(
        [
            "",
            "Los detalles de las mayores celdas excluidas y el borde responsable quedan en "
            "`tributary_coverage_audit.json`.",
            "",
            "## Capas historicas de transferencia contra CAD",
            "",
            "`areas` es la etapa losa->vigas y `point_areas` la etapa hacia muros/columnas. "
            "Representan la misma carga y nunca se suman.",
            "",
            "| Dataset | Edificio | Piso | Area declarada | Union poligonos | Entradas con diferencia | Sin poligono [m2] | Borde CAD cerca 0,60 m |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in historical_visual_layers:
        lines.append(
            f"| {item['dataset']} | {item['building']} | {item['floor']} | "
            f"{item['declared_area_m2']:.3f} | {item['polygon_union_area_m2']:.3f} | "
            f"{item['polygon_area_mismatch_count']} | "
            f"{item['nonzero_area_without_polygon_m2']:.3f} | "
            f"{item['cad_edge_near_union_boundary_frac_0_60m']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Los `polygon` historicos son geometria de visualizacion incompleta: en muchas "
            "entradas su area no coincide con `area_m2`, que acumula la transferencia. El "
            "repositorio no conserva el algoritmo que genero esa discretizacion. Por eso el "
            "area historica solo se usa como contraste y la huella debe reconstruirse desde "
            "los planos y `RLE-LOSA` antes de adoptarla como fuente final.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"TRIBUTARY_COVERAGE_AUDIT: {result['status']}")
    print(f"Reportes: {OUT_JSON} {OUT_MD}")


if __name__ == "__main__":
    main()
