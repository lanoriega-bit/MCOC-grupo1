from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
AUDIT = REPO / "entregas/P1L2/edificio/validacion/ed1_walls/ed1_wall_face_audit.json"
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
DIFF_VALIDATION = REPO / "entregas/P1L2/edificio/datos/luis_reference_diff_validation.json"
OUT_JSON = REPO / "entregas/P1L2/edificio/datos/ed1_wall_validation.json"
OUT_MD = REPO / "entregas/P1L2/edificio/validacion/ed1_walls/VALIDATION.md"
EXPECTED_BY_FLOOR = {"S1": 21, "P1": 25, "P2": 7, "P3": 7, "P4": 7}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def xy_key(item: dict[str, object]) -> tuple[object, ...]:
    start = tuple(round(float(value), 4) for value in item["start"][:2])
    end = tuple(round(float(value), 4) for value in item["end"][:2])
    return (item["floor"],) + tuple(sorted((start, end))) + (round(float(item["width_m"]), 3),)


def main() -> None:
    audit = load(AUDIT)
    model = load(MODEL)
    reference = load(DIFF_VALIDATION)
    walls = [
        item for item in model["solids"]
        if item.get("building") == "EDIFICIO_1" and item.get("category") == "wall"
    ]
    wall_supports = [
        item for item in model["solids"]
        if item.get("building") == "EDIFICIO_1"
        and item.get("category") == "support"
        and item.get("kind") == "linear_prism"
        and str(item.get("sourceTag", "")).startswith("SOL_1S_wall_")
    ]
    counts = dict(Counter(str(item["floor"]) for item in walls))
    audit_counts = {
        floor: len(audit["floors"][floor]["pairs"])
        for floor in EXPECTED_BY_FLOOR
    }
    thickness_failures = [
        item["id"] for item in walls
        if item.get("geometry_confirmation", {}).get("status") != "CONFIRMED_CONTOUR_PAIR"
        or abs(float(item["width_m"]) - float(item["wall_thickness_m"])) > 1e-9
        or abs(float(item["width_m"]) - float(item["geometry_confirmation"]["thickness_m"])) > 1e-9
        or not str(item.get("thickness_source", "")).startswith("CAD_CONTOUR_PAIR")
    ]
    wall_ids = [str(item["id"]) for item in walls]
    wall_keys = [xy_key(item) for item in walls]
    checks = {
        "audit_pass": audit.get("status") == "PASS",
        "counts_match_expected": counts == EXPECTED_BY_FLOOR,
        "counts_match_audit": counts == audit_counts,
        "all_thicknesses_traceable": not thickness_failures,
        "unique_wall_ids": len(wall_ids) == len(set(wall_ids)),
        "unique_centerlines": len(wall_keys) == len(set(wall_keys)),
        "s1_wall_support_count": len(wall_supports) == EXPECTED_BY_FLOOR["S1"],
        "luis_reference_files_modified_zero": reference.get("luis_reference_files_modified") == 0,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "status": status,
        "checks": checks,
        "wall_counts_by_floor": counts,
        "wall_segments_total": len(walls),
        "s1_wall_supports": len(wall_supports),
        "thicknesses_m": dict(sorted(Counter(str(item["wall_thickness_m"]) for item in walls).items())),
        "geometry_and_label_confirmed": sum(item.get("thickness_source") == "CAD_CONTOUR_PAIR+TEXT_LABEL" for item in walls),
        "geometry_only_confirmed": sum(item.get("thickness_source") == "CAD_CONTOUR_PAIR" for item in walls),
        "thickness_failures": thickness_failures,
        "source_audit": str(AUDIT.relative_to(REPO)).replace("\\", "/"),
        "validated_model": str(MODEL.relative_to(REPO)).replace("\\", "/"),
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Validacion final de muros EDIFICIO_1",
        "",
        f"Estado: `{status}`",
        "",
        "| Verificacion | Resultado |",
        "| --- | --- |",
        *[f"| {name} | `{'PASS' if passed else 'FAIL'}` |" for name, passed in checks.items()],
        "",
        f"Segmentos analiticos: `{len(walls)}`. Apoyos lineales S1: `{len(wall_supports)}`.",
        f"Espesores confirmados por geometria y etiqueta: `{result['geometry_and_label_confirmed']}`; solo por geometria: `{result['geometry_only_confirmed']}`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ED1_WALL_VALIDATION: {status}")
    print(f"Reporte: {OUT_JSON} {OUT_MD}")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
