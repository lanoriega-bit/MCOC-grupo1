#!/usr/bin/env python3
"""Genera matriz columnas-ejes-pisos para el modelo combinado."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from model_contract import EXPECTED_FLOORS

REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

MODEL = UNITY / "model_combined_viewer.json"
OUT_JSON = DATA / "column_axis_matrix.json"
OUT_CSV = DATA / "column_axis_matrix.csv"
OUT_MD = VALID / "column_axis_matrix.md"

AXIS_TOLERANCE_M = 0.35
STATION_ROUND_M = 0.05


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rounded_grid(value: float) -> float:
    return round(round(value / STATION_ROUND_M) * STATION_ROUND_M, 3)


def axis_position(axis_system: dict[str, object], name: str) -> float:
    data = axis_system["X"][name]
    if "x_m" in data:
        return float(data["x_m"])
    if name == "D/E":
        return float(data["edificio_1_E_transformed_x_m"])
    raise KeyError(name)


def building_axis_maps(model: dict[str, object]) -> dict[str, dict[str, dict[str, float]]]:
    axis = model["globalAxisSystem"]
    y_common = {name: float(data["y_m"]) for name, data in axis["Y"].items()}
    ed1_x = {"D/E": float(axis["X"]["D/E"]["edificio_1_E_transformed_x_m"])}
    ed1_x.update({name: float(data["x_m"]) for name, data in axis["X"].items() if data.get("source") == "EDIFICIO_1_TRANSFORMED"})
    return {
        "EDIFICIO_2": {
            "X": {
                "A": axis_position(axis, "A"),
                "B": axis_position(axis, "B"),
                "C": axis_position(axis, "C"),
                "D/E": float(axis["X"]["D/E"]["edificio_2_D_x_m"]),
            },
            "Y": {name: y_common[name] for name in ["1", "2", "3"]},
        },
        "EDIFICIO_1": {
            "X": ed1_x,
            "Y": y_common,
        },
    }


def classify_column(x_assign: dict[str, object], y_assign: dict[str, object], x: float, y: float, floors_at_station: int) -> dict[str, object]:
    x_on = x_assign["status"] == "ON_AXIS"
    y_on = y_assign["status"] == "ON_AXIS"
    if x_on and y_on:
        return {"classification": "ON_CANONICAL_AXIS", "classification_confidence": "CONFIRMED", "classification_reason": "Centro dentro de tolerancia de ejes canonicos X/Y."}
    if x_on and not y_on and y > float(y_assign["axis_coord_m"]):
        return {
            "classification": "OFF_AXIS_LEGITIMATE",
            "classification_confidence": "GEOMETRY_CONFIRMED" if floors_at_station >= 3 else "NEEDS_REVIEW_GEOMETRY_ONLY",
            "classification_reason": "Columna alineada a eje X real y repetida en posicion Y exterior al eje 3; no hay etiqueta de eje Y para promoverla.",
        }
    if not x_on and y_on and floors_at_station >= 5:
        return {
            "classification": "SPECIAL_POSITION_CONFIRMED",
            "classification_confidence": "GEOMETRY_CONFIRMED",
            "classification_reason": "Columna repetida en los cinco pisos sobre eje Y primario, pero sin etiqueta de eje X respaldada.",
        }
    if not x_on and y_on:
        return {
            "classification": "SPECIAL_POSITION_CONFIRMED",
            "classification_confidence": "NEEDS_REVIEW_GEOMETRY_ONLY",
            "classification_reason": "Posicion especial sobre eje Y real; falta respaldo nominal para eje X secundario.",
        }
    if not x_on and not y_on:
        return {
            "classification": "OFF_AXIS_LEGITIMATE",
            "classification_confidence": "GEOMETRY_CONFIRMED" if floors_at_station >= 3 else "NEEDS_REVIEW_GEOMETRY_ONLY",
            "classification_reason": "Posicion fuera de la grilla canonica actual, repetida por geometria; no se inventa eje sin etiqueta/cota nominal.",
        }
    return {"classification": "NEEDS_REVIEW", "classification_confidence": "LOW", "classification_reason": "No clasificado por reglas automaticas."}


def nearest_axis(value: float, axes: dict[str, float]) -> dict[str, object]:
    name, pos = min(axes.items(), key=lambda item: abs(value - item[1]))
    offset = value - pos
    status = "ON_AXIS" if abs(offset) <= AXIS_TOLERANCE_M else "OFF_AXIS_REFERENCE"
    return {
        "axis": name,
        "axis_coord_m": round(pos, 3),
        "offset_m": round(offset, 3),
        "abs_offset_m": round(abs(offset), 3),
        "status": status,
    }


def matrix_axis_label(assign: dict[str, object], coord: float, orientation: str) -> str:
    if assign["status"] == "ON_AXIS":
        return str(assign["axis"])
    return f"{orientation}={rounded_grid(coord):.2f} near {assign['axis']} {float(assign['offset_m']):+.2f}m"


def floor_cell(columns: list[dict[str, object]]) -> str:
    if not columns:
        return ""
    if len(columns) == 1:
        return "1"
    return str(len(columns))


def station_sort_key(station: dict[str, object]) -> tuple[object, ...]:
    building_order = {"EDIFICIO_2": 0, "EDIFICIO_1": 1}
    return (building_order.get(station["building"], 99), float(station["x_m"]), float(station["y_m"]))


def build_rows(model: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    axes = building_axis_maps(model)
    details: list[dict[str, object]] = []
    stations: dict[tuple[str, str, str], dict[str, object]] = {}

    for solid in model.get("solids", []):
        if solid.get("category") != "column":
            continue
        building = str(solid.get("building"))
        floor = str(solid.get("floor"))
        if building not in axes or floor not in EXPECTED_FLOORS:
            continue
        cx, cy, cz = [float(value) for value in solid["center"]]
        x_assign = nearest_axis(cx, axes[building]["X"])
        y_assign = nearest_axis(cy, axes[building]["Y"])
        x_label = matrix_axis_label(x_assign, cx, "X")
        y_label = matrix_axis_label(y_assign, cy, "Y")
        key = (building, x_label, y_label)

        detail = {
            "solidTag": solid.get("solidTag"),
            "building": building,
            "floor": floor,
            "x_m": round(cx, 3),
            "y_m": round(cy, 3),
            "z_m": round(cz, 3),
            "width_m": round(float(solid.get("width_m", 0.0)), 3),
            "depth_m": round(float(solid.get("depth_m", 0.0)), 3),
            "height_m": round(float(solid.get("height_m", 0.0)), 3),
            "x_axis_matrix": x_label,
            "y_axis_matrix": y_label,
            "nearest_x_axis": x_assign,
            "nearest_y_axis": y_assign,
            "axis_status": "ON_AXIS" if x_assign["status"] == "ON_AXIS" and y_assign["status"] == "ON_AXIS" else "OFF_AXIS_REFERENCE",
            "source_dxf": solid.get("source_dxf"),
            "source_floor": solid.get("source_floor"),
            "confidence": solid.get("confidence"),
        }
        details.append(detail)

        if key not in stations:
            stations[key] = {
                "building": building,
                "x_axis_matrix": x_label,
                "y_axis_matrix": y_label,
                "x_m": rounded_grid(cx),
                "y_m": rounded_grid(cy),
                "nearest_x_axis": x_assign["axis"],
                "nearest_y_axis": y_assign["axis"],
                "max_abs_x_offset_m": 0.0,
                "max_abs_y_offset_m": 0.0,
                "axis_status": "ON_AXIS",
                "floors": {name: [] for name in EXPECTED_FLOORS},
                "dimensions_by_floor": {name: [] for name in EXPECTED_FLOORS},
            }
        station = stations[key]
        station["floors"][floor].append(str(solid.get("solidTag")))
        station["dimensions_by_floor"][floor].append(f"{detail['width_m']:.2f}x{detail['depth_m']:.2f}")
        station["max_abs_x_offset_m"] = max(float(station["max_abs_x_offset_m"]), float(x_assign["abs_offset_m"]))
        station["max_abs_y_offset_m"] = max(float(station["max_abs_y_offset_m"]), float(y_assign["abs_offset_m"]))
        if detail["axis_status"] != "ON_AXIS":
            station["axis_status"] = "OFF_AXIS_REFERENCE"

    matrix = []
    for station in stations.values():
        floor_counts = {floor: len(station["floors"][floor]) for floor in EXPECTED_FLOORS}
        dimensions = {floor: sorted(set(station["dimensions_by_floor"][floor])) for floor in EXPECTED_FLOORS if station["dimensions_by_floor"][floor]}
        row = {
            "building": station["building"],
            "x_axis_matrix": station["x_axis_matrix"],
            "y_axis_matrix": station["y_axis_matrix"],
            "x_m": station["x_m"],
            "y_m": station["y_m"],
            "nearest_x_axis": station["nearest_x_axis"],
            "nearest_y_axis": station["nearest_y_axis"],
            "max_abs_x_offset_m": round(float(station["max_abs_x_offset_m"]), 3),
            "max_abs_y_offset_m": round(float(station["max_abs_y_offset_m"]), 3),
            "axis_status": station["axis_status"],
            "classification": "ON_CANONICAL_AXIS",
            "classification_confidence": "CONFIRMED",
            "classification_reason": "Centro dentro de tolerancia de ejes canonicos X/Y.",
            "floor_counts": floor_counts,
            "total_columns": sum(floor_counts.values()),
            "dimensions_by_floor": dimensions,
            "solid_tags_by_floor": station["floors"],
        }
        if row["axis_status"] != "ON_AXIS":
            x_assign = {"status": "ON_AXIS" if row["max_abs_x_offset_m"] <= AXIS_TOLERANCE_M else "OFF_AXIS_REFERENCE", "axis_coord_m": row["x_m"] - row["max_abs_x_offset_m"], "axis": row["nearest_x_axis"]}
            y_assign = {"status": "ON_AXIS" if row["max_abs_y_offset_m"] <= AXIS_TOLERANCE_M else "OFF_AXIS_REFERENCE", "axis_coord_m": row["y_m"] - row["max_abs_y_offset_m"], "axis": row["nearest_y_axis"]}
            row.update(classify_column(x_assign, y_assign, float(row["x_m"]), float(row["y_m"]), sum(1 for count in floor_counts.values() if count)))
        matrix.append(row)

    by_station = {(row["building"], row["x_axis_matrix"], row["y_axis_matrix"]): row for row in matrix}
    for detail in details:
        row = by_station[(detail["building"], detail["x_axis_matrix"], detail["y_axis_matrix"])]
        detail["classification"] = row["classification"]
        detail["classification_confidence"] = row["classification_confidence"]
        detail["classification_reason"] = row["classification_reason"]

    matrix.sort(key=station_sort_key)
    details.sort(key=lambda item: (item["building"], item["floor"], item["x_m"], item["y_m"], str(item["solidTag"])))
    return matrix, details


def summary(matrix: list[dict[str, object]], details: list[dict[str, object]]) -> dict[str, object]:
    by_floor = Counter(item["floor"] for item in details)
    by_building = Counter(item["building"] for item in details)
    by_building_floor = Counter(f"{item['building']}:{item['floor']}" for item in details)
    off_axis = [item for item in details if item["axis_status"] != "ON_AXIS"]
    by_class = Counter(item["classification"] for item in details)
    return {
        "status": "PASS_WITH_OFF_AXIS_NOTES" if off_axis else "PASS",
        "column_count": len(details),
        "station_count": len(matrix),
        "axis_tolerance_m": AXIS_TOLERANCE_M,
        "station_round_m": STATION_ROUND_M,
        "columns_by_floor": dict(sorted(by_floor.items(), key=lambda item: EXPECTED_FLOORS.index(item[0]))),
        "columns_by_building": dict(sorted(by_building.items())),
        "columns_by_building_floor": dict(sorted(by_building_floor.items())),
        "off_axis_reference_count": len(off_axis),
        "off_axis_classification_counts": dict(sorted(by_class.items())),
        "off_axis_reference_sample": off_axis[:20],
    }


def write_csv(matrix: list[dict[str, object]]) -> None:
    fields = [
        "building", "x_axis_matrix", "y_axis_matrix", "x_m", "y_m", "nearest_x_axis", "nearest_y_axis",
        "max_abs_x_offset_m", "max_abs_y_offset_m", "axis_status", "total_columns", *EXPECTED_FLOORS, "dimensions_by_floor",
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in matrix:
            out = {key: row.get(key) for key in fields if key not in EXPECTED_FLOORS}
            for floor in EXPECTED_FLOORS:
                out[floor] = row["floor_counts"][floor]
            out["dimensions_by_floor"] = json.dumps(row["dimensions_by_floor"], ensure_ascii=False, sort_keys=True)
            writer.writerow(out)


def write_markdown(report: dict[str, object]) -> None:
    s = report["summary"]
    matrix = report["matrix"]
    lines = [
        "# Matriz columnas-ejes-pisos",
        "",
        f"- Estado: **{s['status']}**",
        f"- Columnas: {s['column_count']}",
        f"- Estaciones de columna: {s['station_count']}",
        f"- Tolerancia eje-columna: {s['axis_tolerance_m']} m",
        f"- Redondeo de estacion: {s['station_round_m']} m",
        f"- Columnas fuera de ejes canonicos: {s['off_axis_reference_count']}",
        f"- CSV: `{OUT_CSV.relative_to(REPO)}`",
        "",
        "## Columnas por piso",
        "",
        "| Piso | Columnas |",
        "|---|---:|",
    ]
    for floor in EXPECTED_FLOORS:
        lines.append(f"| {floor} | {s['columns_by_floor'].get(floor, 0)} |")
    lines.extend([
        "",
        "## Columnas por edificio",
        "",
        "| Edificio | Columnas |",
        "|---|---:|",
    ])
    for building, count in s["columns_by_building"].items():
        lines.append(f"| {building} | {count} |")

    lines.extend([
        "",
        "## Matriz",
        "",
        "Celdas S1/P1/P2/P3/P4 indican cantidad de columnas en esa estacion. `OFF_AXIS_REFERENCE` significa que la columna se conserva, pero queda fuera de la tolerancia respecto de los ejes canonicos actualmente registrados.",
        "",
        "| Edificio | X eje/ref | Y eje/ref | x [m] | y [m] | S1 | P1 | P2 | P3 | P4 | Estado | Clasificacion |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in matrix:
        cells = [floor_cell(row["solid_tags_by_floor"][floor]) for floor in EXPECTED_FLOORS]
        lines.append(
            f"| {row['building']} | {row['x_axis_matrix']} | {row['y_axis_matrix']} | {row['x_m']:.2f} | {row['y_m']:.2f} | "
            f"{cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {cells[4]} | {row['axis_status']} | {row['classification']} |"
        )

    lines.extend(["", "## Clasificacion off-axis", "", "| Clasificacion | Columnas |", "|---|---:|"])
    for key, value in s["off_axis_classification_counts"].items():
        if key == "ON_CANONICAL_AXIS":
            continue
        lines.append(f"| {key} | {value} |")

    if s["off_axis_reference_count"]:
        lines.extend([
            "",
            "## Notas fuera de eje",
            "",
            "Las columnas fuera de eje no se eliminan ni se corrigen. Se reportan porque el set canonico de ejes todavia no contiene todos los posibles ejes secundarios de los planos.",
            "",
            "| Tag | Edificio | Piso | x [m] | y [m] | X cercano | dx [m] | Y cercano | dy [m] | Clasificacion |",
            "|---|---|---|---:|---:|---|---:|---|---:|---|",
        ])
        for item in s["off_axis_reference_sample"]:
            lines.append(
                f"| {item['solidTag']} | {item['building']} | {item['floor']} | {item['x_m']:.3f} | {item['y_m']:.3f} | "
                f"{item['nearest_x_axis']['axis']} | {item['nearest_x_axis']['offset_m']:.3f} | "
                f"{item['nearest_y_axis']['axis']} | {item['nearest_y_axis']['offset_m']:.3f} | {item['classification']} |"
            )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    model = load(MODEL)
    matrix, details = build_rows(model)
    report = {
        "check": "COLUMN_AXIS_FLOOR_MATRIX",
        "method": "Asigna cada columna al eje X/Y mas cercano por edificio; agrupa estaciones por referencia eje/offset y piso canonico.",
        "summary": summary(matrix, details),
        "matrix": matrix,
        "column_details": details,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(matrix)
    write_markdown(report)
    print("COLUMN_AXIS_MATRIX:", report["summary"]["status"])
    print("Columnas:", report["summary"]["column_count"], "Estaciones:", report["summary"]["station_count"])
    print("Fuera de ejes canonicos:", report["summary"]["off_axis_reference_count"])
    print("Reportes:", OUT_JSON, OUT_CSV, OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
