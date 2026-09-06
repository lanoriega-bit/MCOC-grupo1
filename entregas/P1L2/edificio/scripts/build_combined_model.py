#!/usr/bin/env python3
"""Construye el viewer conjunto EDIFICIO_1 + EDIFICIO_2.

Precondiciones obligatorias:
    - global_axes.json debe tener AXIS_VERTICAL_ALIGNMENT PASS.
    - axis_calce_validation.json debe tener CALCE_A AXIS_CONFIRMED.
    - ambos viewers fuente deben cumplir EXPECTED_FLOORS=5.
    - EDIFICIO_1 usa la reconstruccion auditada/corregida, no el Luis provisional.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from model_contract import EXPECTED_FLOORS, assert_expected_floors, canonicalize_viewer_model

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
UNITY = REPO / "entregas" / "P1L2" / "unity_export"

ED1 = UNITY / "model_1_audited_corrected.json"
ED2 = UNITY / "model_2_viewer.json"
AXES = DATA / "global_axes.json"
CALCE = DATA / "axis_calce_validation.json"
LUIS_DIFF = DATA / "luis_reference_diff.json"
OUT = UNITY / "model_combined_viewer.json"
OUT_VALIDATION = DATA / "combined_model_validation.json"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def transformed_axis_system(axes: dict[str, object], dx: float, dy: float) -> dict[str, object]:
    ed1_building = axes["buildings"]["EDIFICIO_1"]
    ed2_building = axes["buildings"]["EDIFICIO_2"]
    ed1 = ed1_building["axes"]
    ed2 = ed2_building["axes"]
    ed1_meta = ed1_building.get("axis_metadata", {})
    ed2_meta = ed2_building.get("axis_metadata", {})
    x_axes: dict[str, object] = {}
    for name, value in ed2["X"].items():
        meta = ed2_meta.get("X", {}).get(name, {"axis_type": "PRIMARY_AXIS"})
        x_axes[name] = {"x_m": float(value), "source": "EDIFICIO_2", **meta}
    x_axes["D/E"] = {
        "edificio_2_D_x_m": float(ed2["X"]["D"]),
        "edificio_1_E_transformed_x_m": float(ed1["X"]["E"]) + dx,
        "residual_m": round(abs(float(ed2["X"]["D"]) - (float(ed1["X"]["E"]) + dx)), 6),
        "source": "CALCE_A_AXIS_CONFIRMED",
        "axis_type": "INTERFACE_AXIS",
        "evidence": "EDIFICIO_2 eje D y EDIFICIO_1 eje E transformado; residual CAD documentado.",
    }
    for name, value in ed1["X"].items():
        if name == "E":
            continue
        meta = ed1_meta.get("X", {}).get(name, {})
        x_axes[name] = {"x_m": float(value) + dx, "source": "EDIFICIO_1_TRANSFORMED", **meta}

    y_axes: dict[str, object] = {}
    for name, value in ed2["Y"].items():
        meta = ed2_meta.get("Y", {}).get(name, {"axis_type": "PRIMARY_AXIS"})
        y_axes[name] = {"y_m": float(value), "source": "COMMON_AXIS", **meta}
    for name, value in ed1["Y"].items():
        transformed = float(value) + dy
        meta = ed1_meta.get("Y", {}).get(name, {})
        if name in y_axes:
            y_axes[name]["edificio_1_transformed_y_m"] = transformed
            y_axes[name]["residual_m"] = round(abs(float(y_axes[name]["y_m"]) - transformed), 6)
            y_axes[name].update({key: value for key, value in meta.items() if key not in y_axes[name]})
        else:
            y_axes[name] = {"y_m": transformed, "source": "EDIFICIO_1_TRANSFORMED", **meta}

    return {"X": x_axes, "Y": y_axes}


def count_by_floor(solids: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = {floor: Counter() for floor in EXPECTED_FLOORS}
    for solid in solids:
        counts[str(solid.get("floor"))][str(solid.get("category"))] += 1
    return {floor: dict(counts[floor]) for floor in EXPECTED_FLOORS}


def main() -> int:
    axes = load(AXES)
    calce = load(CALCE)
    if not ED1.exists():
        raise RuntimeError(f"EDIFICIO_1 corregido no existe: {ED1}. Ejecutar resolve_luis_inferred_columns.py antes de combinar.")
    if not LUIS_DIFF.exists():
        raise RuntimeError(f"Falta LUIS_REFERENCE_DIFF: {LUIS_DIFF}. No se debe volver a usar Luis como golden silencioso.")
    luis_diff = load(LUIS_DIFF)
    if luis_diff.get("luis_reference_files_modified") != 0:
        raise RuntimeError("LUIS_REFERENCE_FILES_MODIFIED debe permanecer en 0")
    if axes.get("validation", {}).get("status") != "PASS":
        raise RuntimeError("AXIS_VERTICAL_ALIGNMENT debe pasar antes de construir el modelo conjunto")
    if calce.get("status") != "AXIS_CONFIRMED":
        raise RuntimeError("CALCE_A no esta AXIS_CONFIRMED; no se genera modelo conjunto")

    dx = float(calce["transform"]["dx_m"])
    dy = float(calce["transform"]["dy_m"])

    ed1 = canonicalize_viewer_model(load(ED1), building="EDIFICIO_1", dx=dx, dy=dy)
    ed2 = canonicalize_viewer_model(load(ED2), building="EDIFICIO_2")
    ed1_report = assert_expected_floors(ed1, str(ED1))
    ed2_report = assert_expected_floors(ed2, str(ED2))

    combined = {
        "model": "P1L2 - EDIFICIO_1 + EDIFICIO_2 axis-combined viewer",
        "units": "m",
        "availableToggles": ed1.get("availableToggles", ed2.get("availableToggles", [])),
        "colors": ed1.get("colors", ed2.get("colors", {})),
        "expectedFloors": list(EXPECTED_FLOORS),
        "expectedFloorCount": len(EXPECTED_FLOORS),
        "axisReference": "Sistema global por ejes. EDIFICIO_2 queda en local A-D; EDIFICIO_1 se traslada por CALCE_A dx=27.491 m.",
        "sourceModels": {
            "EDIFICIO_1": str(ED1.relative_to(REPO)).replace("\\", "/"),
            "EDIFICIO_2": str(ED2.relative_to(REPO)).replace("\\", "/"),
        },
        "referencePolicy": {
            "primary_truth": "PLANOS_ORIGINALES_DXF_DWG_PDF",
            "luis_reference": "LUIS_REFERENCE_PROVISIONAL",
            "audited_model": "EDIFICIO_1_AUDITED_CORRECTED",
            "golden_in_combined_required": False,
            "replacement_check": str(LUIS_DIFF.relative_to(REPO)).replace("\\", "/"),
        },
        "globalAxisSystem": transformed_axis_system(axes, dx=dx, dy=dy),
        "transformations": {
            "EDIFICIO_2": {"dx_m": 0.0, "dy_m": 0.0, "rotation_deg": 0.0, "scale": 1.0},
            "EDIFICIO_1": {"dx_m": dx, "dy_m": dy, "rotation_deg": 0.0, "scale": 1.0, "status": "AXIS_CONFIRMED"},
        },
        "solids": ed2["solids"] + ed1["solids"],
        "segments": ed2["segments"] + ed1["segments"],
        "labels": ed2["labels"] + ed1["labels"],
        "diaphragms": ed2["diaphragms"] + ed1["diaphragms"],
        "notes": [
            "Pisos canonicos: S1/P1/P2/P3/P4. Fundacion/radier no crea piso extra.",
            "CALCE_A confirmado por ejes D/E con residual 0.009 m; no se fuerza D y E a igualdad exacta.",
            "La geometria de EDIFICIO_2 en S1/P1/P2/P3 proviene de lamina 101 superpuesta; no genera pisos adicionales.",
            "EDIFICIO_1 proviene de model_1_audited_corrected.json; GOLDEN_IN_COMBINED ya no es criterio obligatorio de igualdad con Luis.",
        ],
    }
    combined_report = assert_expected_floors(combined, str(OUT))

    validation = {
        "status": "PASS",
        "floor_contract": combined_report,
        "source_floor_contracts": {"EDIFICIO_1": ed1_report, "EDIFICIO_2": ed2_report},
        "axis_validation": axes["validation"],
        "calce_validation": calce,
        "luis_reference_diff": luis_diff,
        "source_models": combined["sourceModels"],
        "reference_policy": combined["referencePolicy"],
        "solid_counts_by_floor": count_by_floor(combined["solids"]),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_VALIDATION.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Modelo conjunto escrito:", OUT)
    print("Validacion:", OUT_VALIDATION)
    print("Floors:", combined_report["actual_floors"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
