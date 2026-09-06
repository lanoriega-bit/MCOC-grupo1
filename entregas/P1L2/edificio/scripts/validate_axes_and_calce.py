#!/usr/bin/env python3
"""Valida ejes verticales y confirma CALCE_A por hipotesis D/E."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf

from model_contract import EXPECTED_FLOORS

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
ISSUES = REPO / "entregas" / "P1L2" / "edificio" / "issues"
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DXF = REPO / "recursos" / "planos" / "dxf_generated"

GLOBAL_AXES = DATA / "global_axes.json"
CALCE_FILE = ISSUES / "calce_parte_1_parte_2.json"
OUT_JSON = DATA / "axis_calce_validation.json"
OUT_MD = REPO / "entregas" / "P1L2" / "edificio" / "validacion" / "axis_calce_validation.md"

CALCE_A_DX_M = 27.491000000000003
CALCE_A_DY_M = 0.0
AXIS_MATCH_TOL_M = 0.02
Y_TOL_M = 0.001


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def axis_coord(axes: dict[str, object], building: str, orientation: str, name: str) -> float:
    return float(axes["buildings"][building]["axes"][orientation][name])


def dimension_evidence(series: str, files: list[str], targets_m: list[float], tol_m: float = 0.02) -> list[float]:
    found: set[float] = set()
    for fname in files:
        doc = ezdxf.readfile(DXF / series / fname)
        for entity in doc.modelspace():
            if entity.dxftype() != "DIMENSION" or "COTA" not in entity.dxf.layer.upper():
                continue
            try:
                value_m = float(entity.get_measurement()) / 100.0
            except Exception:
                continue
            for target in targets_m:
                if abs(value_m - target) <= tol_m:
                    found.add(round(target, 3))
    return sorted(found)


def point_from_solid(solid: dict[str, object]) -> tuple[float, float] | None:
    if "center" in solid:
        return float(solid["center"][0]), float(solid["center"][1])
    if "start" in solid and "end" in solid:
        return ((float(solid["start"][0]) + float(solid["end"][0])) / 2.0,
                (float(solid["start"][1]) + float(solid["end"][1])) / 2.0)
    return None


def transform_point(point: tuple[float, float], dx: float, dy: float) -> tuple[float, float]:
    return point[0] + dx, point[1] + dy


def count_columns_near_axis(viewer: dict[str, object], axis_x_global: float, dx: float = 0.0, dy: float = 0.0, tol: float = 0.20) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for solid in viewer.get("solids", []):
        if solid.get("category") != "column":
            continue
        point = point_from_solid(solid)
        if point is None:
            continue
        x, _y = transform_point(point, dx, dy)
        if abs(x - axis_x_global) <= tol:
            counts[str(solid.get("floor"))] += 1
    return {floor: counts.get(floor, 0) for floor in EXPECTED_FLOORS}


def count_linear_near_axis(viewer: dict[str, object], axis_x_global: float, dx: float = 0.0, dy: float = 0.0, tol: float = 0.60) -> dict[str, object]:
    counts: dict[str, Counter[str]] = {floor: Counter() for floor in EXPECTED_FLOORS}
    for solid in viewer.get("solids", []):
        if solid.get("category") not in {"beam", "wall"}:
            continue
        point = point_from_solid(solid)
        if point is None:
            continue
        x, _y = transform_point(point, dx, dy)
        if abs(x - axis_x_global) <= tol:
            counts[str(solid.get("floor"))][str(solid.get("category"))] += 1
    return {floor: dict(counts[floor]) for floor in EXPECTED_FLOORS}


def count_segments_near_axis(viewer: dict[str, object], axis_x_global: float, categories: set[str], dx: float = 0.0, dy: float = 0.0, tol: float = 0.60) -> dict[str, object]:
    counts: dict[str, Counter[str]] = {floor: Counter() for floor in EXPECTED_FLOORS}
    for segment in viewer.get("segments", []):
        if segment.get("category") not in categories or "points" not in segment:
            continue
        points = segment["points"]
        if len(points) < 2:
            continue
        x = (float(points[0][0]) + float(points[1][0])) / 2.0 + dx
        if abs(x - axis_x_global) <= tol:
            counts[str(segment.get("floor"))][str(segment.get("category"))] += 1
    return {floor: dict(counts[floor]) for floor in EXPECTED_FLOORS}


def write_markdown(report: dict[str, object]) -> None:
    lines = [
        "# Validacion de ejes y CALCE_A",
        "",
        f"- Estado: **{report['status']}**",
        f"- Transformacion: dx={report['transform']['dx_m']} m, dy={report['transform']['dy_m']} m, rotation={report['transform']['rotation_deg']} deg, scale={report['transform']['scale']}",
        f"- Residuo D/E: **{report['residuals']['D_E_m']:.3f} m**",
        f"- Residuales Y comunes: `{report['residuals']['Y_common_m']}`",
        "",
        "## Evidencia",
        "",
        f"- Etiquetas/lineas: {report['evidence']['axis_labels_and_lines']}",
        f"- Cotas EDIFICIO_1: {report['evidence']['dimensions']['EDIFICIO_1']}",
        f"- Cotas EDIFICIO_2: {report['evidence']['dimensions']['EDIFICIO_2']}",
        f"- Columnas cerca D (ED2): {report['evidence']['columns_near_interface']['EDIFICIO_2_D']}",
        f"- Columnas cerca E transformado (ED1): {report['evidence']['columns_near_interface']['EDIFICIO_1_E_transformed']}",
        f"- Vigas/muros cerca interfaz: {report['evidence']['linear_near_interface']}",
        f"- Perimetros/axis segments cerca interfaz: {report['evidence']['segments_near_interface']}",
        f"- Fuentes/plano general: {report['evidence']['plan_sources']}",
        "",
        "## Decision",
        "",
        report["decision"],
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_calce_issue(report: dict[str, object]) -> None:
    data = load(CALCE_FILE) if CALCE_FILE.exists() else {}
    data["estado"] = report["status"]
    data["referencia_principal"] = "ejes"
    data["transformacion_parte_1_respecto_parte_2"] = {
        "traslacion_x_m": CALCE_A_DX_M,
        "traslacion_y_m": CALCE_A_DY_M,
        "rotacion_grados": 0.0,
        "escala": 1.0,
        "estado": report["status"],
    }
    data["evidencia_axis_calce"] = report
    if report["status"] == "AXIS_CONFIRMED":
        data["faltante_para_confirmar"] = []
    CALCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CALCE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    axes = load(GLOBAL_AXES)
    if axes.get("validation", {}).get("status") != "PASS":
        raise RuntimeError("AXIS_VERTICAL_ALIGNMENT debe pasar antes de validar CALCE_A")

    ed2_d = axis_coord(axes, "EDIFICIO_2", "X", "D")
    ed1_e = axis_coord(axes, "EDIFICIO_1", "X", "E") + CALCE_A_DX_M
    residual_de = abs(ed2_d - ed1_e)
    y_residuals = {}
    for name in ("1", "2", "3"):
        ed2_y = axis_coord(axes, "EDIFICIO_2", "Y", name)
        ed1_y = axis_coord(axes, "EDIFICIO_1", "Y", name) + CALCE_A_DY_M
        y_residuals[name] = round(abs(ed2_y - ed1_y), 6)

    ed1_span = axis_coord(axes, "EDIFICIO_1", "Y", "3") - axis_coord(axes, "EDIFICIO_1", "Y", "1")
    ed2_span = axis_coord(axes, "EDIFICIO_2", "Y", "3") - axis_coord(axes, "EDIFICIO_2", "Y", "1")
    scale_residual = abs((ed2_span / ed1_span) - 1.0) if ed1_span else math.inf

    ed1_viewer = load(UNITY / "model_viewer_candidate.json")
    ed2_viewer = load(UNITY / "model_2_viewer.json")
    columns = {
        "EDIFICIO_2_D": count_columns_near_axis(ed2_viewer, ed2_d),
        "EDIFICIO_1_E_transformed": count_columns_near_axis(ed1_viewer, ed2_d, dx=CALCE_A_DX_M, dy=CALCE_A_DY_M),
    }
    linear = {
        "EDIFICIO_2_D": count_linear_near_axis(ed2_viewer, ed2_d),
        "EDIFICIO_1_E_transformed": count_linear_near_axis(ed1_viewer, ed2_d, dx=CALCE_A_DX_M, dy=CALCE_A_DY_M),
    }
    segments_near = {
        "EDIFICIO_2_D": count_segments_near_axis(ed2_viewer, ed2_d, {"slab_edge", "axis"}),
        "EDIFICIO_1_E_transformed": count_segments_near_axis(ed1_viewer, ed2_d, {"slab_edge", "axis"}, dx=CALCE_A_DX_M, dy=CALCE_A_DY_M),
    }
    dims = {
        "EDIFICIO_1": dimension_evidence("2017_67", ["2017_67-101.dxf", "2017_67-102.dxf", "2017_67-103.dxf"], [3.9, 8.9, 16.15, 50.0]),
        "EDIFICIO_2": dimension_evidence("2024_22", ["2024_22-100.dxf", "2024_22-101.dxf", "2024_22-102.dxf"], [7.5, 8.9, 10.0, 16.15, 27.5]),
    }

    status = "AXIS_CONFIRMED"
    if residual_de > AXIS_MATCH_TOL_M or any(value > Y_TOL_M for value in y_residuals.values()) or scale_residual > 0.001:
        status = "NEEDS_REVIEW"

    report = {
        "status": status,
        "check": "CALCE_A_D_E_AXIS_HYPOTHESIS",
        "transform": {"dx_m": CALCE_A_DX_M, "dy_m": CALCE_A_DY_M, "rotation_deg": 0.0, "scale": 1.0},
        "residuals": {"D_E_m": round(residual_de, 6), "Y_common_m": y_residuals, "scale_residual": round(scale_residual, 9)},
        "tolerances": {"D_E_m": AXIS_MATCH_TOL_M, "Y_common_m": Y_TOL_M},
        "evidence": {
            "axis_labels_and_lines": "ED2 D=27.500 m; ED1 E+dx=27.491 m; ejes Y 1/2/3 coinciden en 0/8.90/16.15; rotacion=0; escala=1.",
            "plan_sources": "cad_sources.md identifica 2017_67 como planos estructurales actuales y 2024_22 como especialidades/calculo LT2 del mismo Edificio de Ingenieria; la secuencia de ejes A-D/E-J respalda continuidad de alas.",
            "dimensions": dims,
            "columns_near_interface": columns,
            "linear_near_interface": linear,
            "segments_near_interface": segments_near,
        },
        "decision": "Se conserva dx=27.491 m; no se normaliza a 27.500 m. El residuo de 9 mm queda documentado como tolerancia CAD/extraccion hasta evidencia de cota que exija correccion exacta.",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report)
    update_calce_issue(report)
    print("CALCE_A:", status)
    print("D/E residual m:", f"{residual_de:.3f}")
    print("Y residuals:", y_residuals)
    print("Reportes:", OUT_JSON, OUT_MD)
    return 0 if status == "AXIS_CONFIRMED" else 2


if __name__ == "__main__":
    sys.exit(main())
