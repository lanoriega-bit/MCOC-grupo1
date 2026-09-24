#!/usr/bin/env python3
"""Validacion independiente de la propuesta de centrolineas de vigas EDIFICIO_1."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import audit_ed1_beams as source


REPO = Path(__file__).resolve().parents[4]
PROPOSAL = REPO / "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_centerline_proposal.json"
OUT_JSON = REPO / "entregas/P1L2/edificio/validacion/ed1_beams/ed1_beam_proposal_validation.json"
OUT_MD = REPO / "entregas/P1L2/edificio/validacion/ed1_beams/BEAM_PROPOSAL_VALIDATION.md"
STANDARD_WIDTHS_M = (0.15, 0.20, 0.30, 0.40, 0.60)
MIN_FACE_LENGTH_M = 0.75
EXPECTED_SOURCE_SEGMENTS = 553
EXPECTED_CENTERLINES = 300
EXPECTED_SHORT_EDGES = 46
EXPECTED_INTERIOR_DETAILS = 4


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def centerline_key(proposal: dict[str, object]) -> tuple[object, ...]:
    start = tuple(round(float(value), 4) for value in proposal["start"][:2])
    end = tuple(round(float(value), 4) for value in proposal["end"][:2])
    return (proposal["floor"],) + tuple(sorted((start, end))) + (round(float(proposal["width_m"]), 3),)


def main() -> None:
    data = load(PROPOSAL)
    proposals = [proposal for row in data["floors"].values() for proposal in row["proposals"]]
    excluded_details = [item for row in data["floors"].values() for item in row["interior_detail_excluded"]]
    source_rows = {floor: source.source_beams(floor) for floor in source.FLOOR_SOURCES}
    all_source = [item for rows in source_rows.values() for item in rows]
    source_ids = {str(item["id"]) for item in all_source}
    short_ids = {str(item["id"]) for item in all_source if float(item["length_m"]) < MIN_FACE_LENGTH_M}
    long_ids = source_ids - short_ids
    retained_face_ids = {str(face) for proposal in proposals for face in proposal["face_ids"]}
    excluded_face_ids = {str(face) for item in excluded_details for face in item["face_ids"]}
    referenced_face_ids = retained_face_ids | excluded_face_ids

    proposal_ids = [str(proposal["proposal_id"]) for proposal in proposals]
    keys = [centerline_key(proposal) for proposal in proposals]
    invalid_lengths = [str(p["proposal_id"]) for p in proposals if float(p["length_m"]) < MIN_FACE_LENGTH_M]
    invalid_widths = [
        str(p["proposal_id"])
        for p in proposals
        if min(abs(float(p["width_m"]) - width) for width in STANDARD_WIDTHS_M) > 0.021
    ]
    retained_conflicts = [str(p["proposal_id"]) for p in proposals if p.get("label_conflict") is True]
    review_items = [str(p["proposal_id"]) for p in proposals if p["classification"] == "REVIEW_GEOMETRY_ONLY"]
    foreign_faces = sorted(referenced_face_ids - source_ids)
    uncovered_long_faces = sorted(long_ids - referenced_face_ids)
    short_used_as_beams = sorted(short_ids & retained_face_ids)
    counts = Counter(str(p["classification"]) for p in proposals)

    checks = {
        "proposal_ready": data.get("status") == "PROPOSAL_READY",
        "source_segment_count": len(all_source) == EXPECTED_SOURCE_SEGMENTS == data["totals"]["source_segments"],
        "centerline_count": len(proposals) == EXPECTED_CENTERLINES == data["totals"]["proposed_centerlines"],
        "short_edges_accounted": len(short_ids) == EXPECTED_SHORT_EDGES == data["totals"]["short_contour_edges_excluded"],
        "interior_details_accounted": len(excluded_details) == EXPECTED_INTERIOR_DETAILS == data["totals"]["interior_detail_excluded"],
        "zero_long_unresolved": data["totals"]["long_unresolved_faces"] == 0 and not uncovered_long_faces,
        "zero_diagonal_unresolved": data["totals"]["diagonal_unresolved_faces"] == 0,
        "zero_review_items": not review_items,
        "unique_proposal_ids": len(proposal_ids) == len(set(proposal_ids)),
        "unique_centerlines": len(keys) == len(set(keys)),
        "valid_lengths": not invalid_lengths,
        "standard_traceable_widths": not invalid_widths,
        "no_retained_label_conflicts": not retained_conflicts,
        "all_face_references_exist": not foreign_faces,
        "short_edges_not_retained": not short_used_as_beams,
        "classification_totals_match": dict(counts) == data["totals"]["classifications"],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "status": status,
        "checks": checks,
        "counts": {
            "source_segments": len(all_source),
            "centerlines": len(proposals),
            "short_contour_edges": len(short_ids),
            "interior_details_excluded": len(excluded_details),
            "long_source_faces": len(long_ids),
            "long_source_faces_referenced": len(long_ids & referenced_face_ids),
        },
        "classifications": dict(counts),
        "failures": {
            "review_items": review_items,
            "invalid_lengths": invalid_lengths,
            "invalid_widths": invalid_widths,
            "retained_label_conflicts": retained_conflicts,
            "foreign_faces": foreign_faces,
            "uncovered_long_faces": uncovered_long_faces,
            "short_used_as_beams": short_used_as_beams,
        },
        "source_proposal": str(PROPOSAL.relative_to(REPO)).replace("\\", "/"),
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Validacion de propuesta de vigas EDIFICIO_1",
        "",
        f"Estado: `{status}`",
        "",
        "| Verificacion | Resultado |",
        "| --- | --- |",
        *[f"| {name} | `{'PASS' if passed else 'FAIL'}` |" for name, passed in checks.items()],
        "",
        f"Trazos fuente: `{len(all_source)}`; centrolineas propuestas: `{len(proposals)}`; cierres cortos excluidos: `{len(short_ids)}`; detalles interiores excluidos: `{len(excluded_details)}`.",
        "",
        "La validacion confirma existencia, centrolinea y ancho. Una altura no rotulada permanece sin confirmar y no debe inferirse de este control.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ED1_BEAM_PROPOSAL_VALIDATION: {status}")
    print(f"Reporte: {OUT_JSON} {OUT_MD}")
    if status != "PASS":
        print(json.dumps(result["failures"], ensure_ascii=False, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
