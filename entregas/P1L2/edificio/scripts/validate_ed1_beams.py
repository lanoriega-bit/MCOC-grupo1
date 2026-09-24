#!/usr/bin/env python3
"""Validacion final de vigas EDIFICIO_1 consolidadas en el modelo combinado."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / "entregas/P1L2/unity_export/model_combined_viewer.json"
PROPOSAL = REPO / "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json"
REFERENCE = REPO / "entregas/P1L2/edificio/datos/luis_reference_diff_validation.json"
OUT_JSON = REPO / "entregas/P1L2/edificio/datos/ed1_beam_validation.json"
OUT_MD = REPO / "entregas/P1L2/edificio/validacion/ed1_beams/VALIDATION.md"
EXPECTED_BY_FLOOR = {"S1": 53, "P1": 69, "P2": 64, "P3": 60, "P4": 54}
LOCAL_TO_FLOOR = {"1S": "S1", "1": "P1", "2": "P2", "3": "P3", "4": "P4"}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def centerline_key(item: dict[str, object]) -> tuple[object, ...]:
    start = tuple(round(float(value), 4) for value in item["start"][:2])
    end = tuple(round(float(value), 4) for value in item["end"][:2])
    return (item["floor"],) + tuple(sorted((start, end))) + (round(float(item["width_m"]), 3),)


def main() -> None:
    model = load(MODEL)
    proposal = load(PROPOSAL)
    reference = load(REFERENCE)
    beams = [
        item for item in model["solids"]
        if item.get("building") == "EDIFICIO_1" and item.get("category") == "beam"
    ]
    counts = Counter(LOCAL_TO_FLOOR.get(str(item["floor"]), str(item["floor"])) for item in beams)
    proposal_ids = {
        str(item["proposal_id"])
        for floor in proposal["floors"].values()
        for item in floor["proposals"]
    }
    model_proposal_ids = [str(item.get("sourceTag")) for item in beams]
    ids = [str(item["id"]) for item in beams]
    tags = [str(item["solidTag"]) for item in beams]
    keys = [centerline_key(item) for item in beams]
    geometry_failures = [
        str(item["id"]) for item in beams
        if not str(item.get("geometry_confirmation", {}).get("status", "")).startswith("CONFIRMED_")
        or abs(float(item["width_m"]) - float(item["section_width_m"])) > 1e-9
        or abs(float(item["width_m"]) - float(item["geometry_confirmation"]["width_m"])) > 1e-9
    ]
    unknown_height_failures = [
        str(item["id"]) for item in beams
        if item.get("section_height_m") is None
        and (
            item.get("section_confidence") != "WIDTH_CONFIRMED_HEIGHT_UNKNOWN"
            or item.get("visual_height_source") != "LEGACY_VISUAL_DEFAULT_0.60_NOT_SECTION"
            or abs(float(item["height_m"]) - 0.60) > 1e-9
        )
    ]
    known_height_failures = [
        str(item["id"]) for item in beams
        if item.get("section_height_m") is not None
        and (
            abs(float(item["height_m"]) - float(item["section_height_m"])) > 1e-9
            or item.get("visual_height_source") != "CONFIRMED_SECTION_HEIGHT"
        )
    ]
    known_heights = sum(item.get("section_height_m") is not None for item in beams)
    unknown_heights = len(beams) - known_heights
    checks = {
        "proposal_ready": proposal.get("status") == "PROPOSAL_READY",
        "counts_match_expected": dict(counts) == EXPECTED_BY_FLOOR,
        "proposal_crosswalk_complete": set(model_proposal_ids) == proposal_ids and len(model_proposal_ids) == len(set(model_proposal_ids)),
        "unique_viewer_ids": len(ids) == len(set(ids)),
        "unique_solid_tags": len(tags) == len(set(tags)),
        "unique_centerlines": len(keys) == len(set(keys)),
        "all_widths_geometry_traceable": not geometry_failures,
        "known_heights_consistent": known_heights == 281 and not known_height_failures,
        "unknown_heights_explicit": unknown_heights == 19 and not unknown_height_failures,
        "historical_id_crosswalk_declared": all(item.get("historical_id_match_quality") in {"GEOMETRIC_OVERLAP", "NEAREST_RETIRED_ID_SAME_ORIENTATION"} for item in beams),
        "luis_reference_files_modified_zero": reference.get("luis_reference_files_modified") == 0,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "status": status,
        "checks": checks,
        "beam_counts_by_floor": dict(counts),
        "beam_centerlines_total": len(beams),
        "confirmed_or_evidence_inferred_section_heights": known_heights,
        "unknown_section_heights": unknown_heights,
        "historical_id_match_quality": dict(Counter(str(item["historical_id_match_quality"]) for item in beams)),
        "failures": {
            "geometry": geometry_failures,
            "known_height": known_height_failures,
            "unknown_height": unknown_height_failures,
        },
        "validated_model": str(MODEL.relative_to(REPO)).replace("\\", "/"),
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Validacion final de vigas EDIFICIO_1",
        "",
        f"Estado: `{status}`",
        "",
        "| Verificacion | Resultado |",
        "| --- | --- |",
        *[f"| {name} | `{'PASS' if passed else 'FAIL'}` |" for name, passed in checks.items()],
        "",
        f"Centrolineas: `{len(beams)}`; alturas confirmadas o inferidas con evidencia: `{known_heights}`; alturas `UNKNOWN`: `{unknown_heights}`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ED1_BEAM_VALIDATION: {status}")
    print(f"Reporte: {OUT_JSON} {OUT_MD}")
    if status != "PASS":
        print(json.dumps(result["failures"], ensure_ascii=False, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
