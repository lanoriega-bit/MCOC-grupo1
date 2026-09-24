#!/usr/bin/env python3
"""Aplica al modelo corregido las centrolineas de vigas EDIFICIO_1 ya validadas."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas/P1L2/unity_export"
DATA = REPO / "entregas/P1L2/edificio/datos"
VALID = REPO / "entregas/P1L2/edificio/validacion/ed1_beams"
MODEL = UNITY / "model_1_audited_corrected.json"
PROPOSAL = VALID / "ed1_beam_centerline_proposal.json"
PROPOSAL_VALIDATION = VALID / "ed1_beam_proposal_validation.json"
DIFF = DATA / "luis_reference_diff.json"
OUT = DATA / "ed1_beam_resolution.json"
OUT_MD = VALID / "APPLICATION.md"
CALCE_A_DX_M = 27.491
FLOORS = ("S1", "P1", "P2", "P3", "P4")
FLOOR_TO_LOCAL = {"S1": "1S", "P1": "1", "P2": "2", "P3": "3", "P4": "4"}
PRE_BEAM_BASELINE_REF = "802c236"
GEOMETRY_KEYS = ("solidTag", "category", "kind", "floor", "center", "start", "end", "width_m", "depth_m", "height_m", "length_m", "area_m2")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_git_json(ref: str, path: Path) -> dict[str, object]:
    relative = str(path.relative_to(REPO)).replace("\\", "/")
    payload = subprocess.check_output(["git", "show", f"{ref}:{relative}"], cwd=REPO)
    return json.loads(payload.decode("utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_hash(model: dict[str, object]) -> str:
    records = [{key: item.get(key) for key in GEOMETRY_KEYS if key in item} for item in model.get("solids", [])]
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def geometry(item: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item.get(key)) for key in GEOMETRY_KEYS if key in item}


def descriptor(item: dict[str, object]) -> tuple[list[float], list[float], list[float], float]:
    start = [float(value) for value in item["start"][:2]]
    end = [float(value) for value in item["end"][:2]]
    vx, vy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(vx, vy)
    if length <= 1e-9:
        raise ValueError("Segmento de longitud cero")
    unit = [vx / length, vy / length]
    if unit[0] < -1e-9 or (abs(unit[0]) <= 1e-9 and unit[1] < 0):
        unit = [-unit[0], -unit[1]]
    midpoint = [(start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0]
    return start, end, unit, length


def match_score(old: dict[str, object], new: dict[str, object]) -> tuple[float, float, float, float] | None:
    old_start, old_end, old_unit, old_length = descriptor(old)
    new_start, new_end, new_unit, new_length = descriptor(new)
    alignment = abs(old_unit[0] * new_unit[0] + old_unit[1] * new_unit[1])
    if alignment < 0.985:
        return None
    axis = new_unit
    normal = [-axis[1], axis[0]]
    new_origin = new_start

    def project(point: list[float]) -> tuple[float, float]:
        delta = [point[0] - new_origin[0], point[1] - new_origin[1]]
        return delta[0] * axis[0] + delta[1] * axis[1], delta[0] * normal[0] + delta[1] * normal[1]

    old_a, old_n1 = project(old_start)
    old_b, old_n2 = project(old_end)
    lo, hi = sorted((old_a, old_b))
    overlap = max(0.0, min(new_length, hi) - max(0.0, lo))
    if overlap < min(0.30, 0.45 * new_length):
        return None
    perpendicular = (abs(old_n1) + abs(old_n2)) / 2.0
    if perpendicular > 0.65:
        return None
    old_mid = [(old_start[0] + old_end[0]) / 2.0, (old_start[1] + old_end[1]) / 2.0]
    new_mid = [(new_start[0] + new_end[0]) / 2.0, (new_start[1] + new_end[1]) / 2.0]
    return (-overlap / new_length, perpendicular, math.dist(old_mid, new_mid), abs(old_length - new_length))


def fallback_id_score(old: dict[str, object], new: dict[str, object]) -> tuple[float, float] | None:
    old_start, old_end, old_unit, old_length = descriptor(old)
    new_start, new_end, new_unit, new_length = descriptor(new)
    alignment = abs(old_unit[0] * new_unit[0] + old_unit[1] * new_unit[1])
    if alignment < 0.985:
        return None
    old_mid = [(old_start[0] + old_end[0]) / 2.0, (old_start[1] + old_end[1]) / 2.0]
    new_mid = [(new_start[0] + new_end[0]) / 2.0, (new_start[1] + new_end[1]) / 2.0]
    return (math.dist(old_mid, new_mid), abs(old_length - new_length))


def direct_section(proposal: dict[str, object]) -> dict[str, object]:
    classification = str(proposal["classification"])
    if proposal.get("height_m") is not None:
        return {
            "height_m": float(proposal["height_m"]),
            "source": "CAD_CONTOUR_WIDTH+TEXT_LABEL",
            "confidence": "CONFIRMED_FROM_GEOMETRY_AND_LABEL",
            "label_tags": [proposal.get("source_label")],
        }
    if classification == "CONFIRMED_LABEL_WIDTH":
        samples = [sample for sample in proposal.get("evidence_samples", []) if sample.get("label_match")]
        heights = {float(sample["nearest_label_height_m"]) for sample in samples}
        if len(heights) == 1:
            return {
                "height_m": heights.pop(),
                "source": "CAD_CONTOUR_WIDTH+TEXT_LABEL",
                "confidence": "CONFIRMED_FROM_GEOMETRY_AND_LABEL",
                "label_tags": sorted({sample["nearest_label"] for sample in samples}),
            }
    return {"height_m": None, "source": "CAD_CONTOUR_WIDTH_ONLY", "confidence": "WIDTH_CONFIRMED_HEIGHT_UNKNOWN", "label_tags": []}


def section_map(proposals: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    by_id = {str(proposal["proposal_id"]): proposal for proposal in proposals}
    result = {proposal_id: direct_section(proposal) for proposal_id, proposal in by_id.items()}
    for proposal_id, proposal in by_id.items():
        if result[proposal_id]["height_m"] is not None:
            continue
        references = proposal.get("repeat_evidence", []) + proposal.get("component_label_evidence", [])
        referenced = [result[str(reference)] for reference in references if str(reference) in result]
        heights = {float(item["height_m"]) for item in referenced if item["height_m"] is not None}
        if len(heights) == 1:
            kind = "REPEATED_PLAN" if proposal.get("repeat_evidence") else "CONNECTED_SECTION_FAMILY"
            result[proposal_id] = {
                "height_m": heights.pop(),
                "source": f"CAD_CONTOUR_WIDTH+INFERRED_{kind}_LABEL",
                "confidence": "INFERRED_SECTION_HEIGHT_FROM_CONFIRMED_FAMILY",
                "label_tags": sorted({tag for item in referenced for tag in item["label_tags"] if tag}),
            }
        elif len(heights) > 1:
            result[proposal_id]["candidate_heights_m"] = sorted(heights)
    return result


def same_applied_geometry(model: dict[str, object], proposals: list[dict[str, object]]) -> bool:
    beams = [item for item in model.get("solids", []) if item.get("category") == "beam"]
    by_proposal = {str(item.get("sourceTag")): item for item in beams}
    if len(beams) != len(proposals) or len(by_proposal) != len(proposals):
        return False
    for proposal in proposals:
        beam = by_proposal.get(str(proposal["proposal_id"]))
        if beam is None:
            return False
        expected_start = [float(proposal["start"][0]) - CALCE_A_DX_M, float(proposal["start"][1])]
        expected_end = [float(proposal["end"][0]) - CALCE_A_DX_M, float(proposal["end"][1])]
        actual = sorted((tuple(round(float(v), 4) for v in beam["start"][:2]), tuple(round(float(v), 4) for v in beam["end"][:2])))
        expected = sorted((tuple(round(v, 4) for v in expected_start), tuple(round(v, 4) for v in expected_end)))
        if actual != expected or abs(float(beam["width_m"]) - float(proposal["width_m"])) > 1e-9:
            return False
    return True


def make_beam(
    proposal: dict[str, object], template: dict[str, object], top_z: float, section: dict[str, object]
) -> dict[str, object]:
    section_height = section["height_m"]
    visual_height = float(section_height) if section_height is not None else 0.60
    z_center = top_z - visual_height / 2.0
    start = [float(proposal["start"][0]) - CALCE_A_DX_M, float(proposal["start"][1]), z_center]
    end = [float(proposal["end"][0]) - CALCE_A_DX_M, float(proposal["end"][1]), z_center]
    beam = {
        "solidTag": template["solidTag"],
        "category": "beam",
        "kind": "linear_prism",
        "floor": FLOOR_TO_LOCAL[str(proposal["floor"])],
        "sourceTag": proposal["proposal_id"],
        "sourceTags": proposal["face_ids"],
        "source_layer": "RLE-VIGA_CONTOUR_CENTERLINE",
        "source_dxf": template.get("source_dxf"),
        "start": start,
        "end": end,
        "width_m": float(proposal["width_m"]),
        "height_m": visual_height,
        "length_m": math.dist(start[:2], end[:2]),
        "section_width_m": float(proposal["width_m"]),
        "section_height_m": section_height,
        "section_source": section["source"],
        "section_confidence": section["confidence"],
        "visual_height_source": "CONFIRMED_SECTION_HEIGHT" if section_height is not None else "LEGACY_VISUAL_DEFAULT_0.60_NOT_SECTION",
        "confidence": "confirmed_from_RLE_VIGA_geometry",
        "preserved_viewer_id": template.get("preserved_viewer_id"),
        "audit_resolution": {
            "classification": proposal["classification"],
            "resolution_group": "CONFIRMED_CORRECTED_GEOMETRY",
            "reason": "La centrolinea y el ancho se obtienen de la auditoria reproducible de RLE-VIGA.",
        },
        "geometry_confirmation": {
            "status": proposal["classification"],
            "proposal_file": str(PROPOSAL.relative_to(REPO)).replace("\\", "/"),
            "face_ids": proposal["face_ids"],
            "width_m": float(proposal["width_m"]),
        },
        "section_evidence_labels": section["label_tags"],
    }
    if section.get("candidate_heights_m"):
        beam["section_height_candidates_m"] = section["candidate_heights_m"]
        beam["section_review"] = "AMBIGUOUS_CONNECTED_LABEL_HEIGHTS"
    return beam


def main() -> None:
    proposal = load(PROPOSAL)
    validation = load(PROPOSAL_VALIDATION)
    if proposal.get("status") != "PROPOSAL_READY" or validation.get("status") != "PASS":
        raise RuntimeError("La propuesta de vigas no esta validada")
    proposal_sha = file_hash(PROPOSAL)
    model = load(MODEL)
    proposals = [copy.deepcopy(item) for floor in FLOORS for item in proposal["floors"][floor]["proposals"]]
    if model.get("beam_consolidation", {}).get("proposal_sha256") == proposal_sha:
        print("ED1_BEAM_CONSOLIDATION: ALREADY_APPLIED")
        return

    if same_applied_geometry(model, proposals):
        prior_result = load(OUT) if OUT.exists() else {}
        if prior_result.get("old_beam_prisms") == 545:
            print("ED1_BEAM_CONSOLIDATION: ALREADY_APPLIED_SEMANTIC_GEOMETRY")
            return
        # Recupera el registro historico si una version anterior no idempotente
        # reescribio el crosswalk al ejecutarse sobre las 300 centrolineas.
        model = load_git_json(PRE_BEAM_BASELINE_REF, MODEL)

    old_beams = [item for item in model.get("solids", []) if item.get("category") == "beam"]
    other_solids = [item for item in model.get("solids", []) if item.get("category") != "beam"]
    sections = section_map(proposals)
    old_by_floor = {floor: [beam for beam in old_beams if beam.get("floor") == FLOOR_TO_LOCAL[floor]] for floor in FLOORS}
    top_by_floor = {
        floor: sum(float(beam["start"][2]) + float(beam["height_m"]) / 2.0 for beam in beams) / len(beams)
        for floor, beams in old_by_floor.items()
    }
    used_old: set[str] = set()
    new_beams = []
    changes = []
    crosswalk = []
    for row in proposals:
        proxy = {"start": row["start"], "end": row["end"]}
        proxy["start"] = [float(proxy["start"][0]) - CALCE_A_DX_M, float(proxy["start"][1])]
        proxy["end"] = [float(proxy["end"][0]) - CALCE_A_DX_M, float(proxy["end"][1])]
        ranked = []
        for old in old_by_floor[str(row["floor"])]:
            if str(old["solidTag"]) in used_old:
                continue
            score = match_score(old, proxy)
            if score is not None:
                ranked.append((score, str(old["solidTag"]), old))
        if ranked:
            template = min(ranked, key=lambda item: (item[0], item[1]))[2]
            id_match_quality = "GEOMETRIC_OVERLAP"
        else:
            fallback = []
            for old in old_by_floor[str(row["floor"])]:
                if str(old["solidTag"]) in used_old:
                    continue
                score = fallback_id_score(old, proxy)
                if score is not None:
                    fallback.append((score, str(old["solidTag"]), old))
            if not fallback:
                raise RuntimeError(f"No hay ID historico compatible para {row['proposal_id']}")
            template = min(fallback, key=lambda item: (item[0], item[1]))[2]
            id_match_quality = "NEAREST_RETIRED_ID_SAME_ORIENTATION"
        used_old.add(str(template["solidTag"]))
        beam = make_beam(row, template, top_by_floor[str(row["floor"])], sections[str(row["proposal_id"])])
        beam["historical_id_match_quality"] = id_match_quality
        new_beams.append(beam)
        changes.append({
            "id": template.get("preserved_viewer_id"),
            "solidTag": template["solidTag"],
            "category": "beam",
            "old_geometry": geometry(template),
            "new_geometry": geometry(beam),
            "reason": "Las caras RLE-VIGA se consolidan en una centrolinea analitica con ancho trazable.",
            "classification": row["classification"],
            "source_dxf": template.get("source_dxf"),
            "evidence": beam["geometry_confirmation"],
            "confidence": "HIGH",
            "scope": "ED1_BEAM_CONTOUR_CONSOLIDATION",
        })
        crosswalk.append({
            "proposal_id": row["proposal_id"],
            "preserved_id": template.get("preserved_viewer_id"),
            "solidTag": template["solidTag"],
            "source_face_ids": row["face_ids"],
            "section_width_m": beam["section_width_m"],
            "section_height_m": beam["section_height_m"],
            "section_confidence": beam["section_confidence"],
            "historical_id_match_quality": id_match_quality,
        })

    for old in old_beams:
        if str(old["solidTag"]) in used_old:
            continue
        changes.append({
            "id": old.get("preserved_viewer_id"),
            "solidTag": old["solidTag"],
            "category": "beam",
            "old_geometry": geometry(old),
            "new_geometry": "REMOVED",
            "reason": "Cara de contorno o detalle retirado al consolidar la viga fisica.",
            "classification": "DUPLICATE_CONTOUR_FACE_OR_DETAIL_REMOVED",
            "source_dxf": old.get("source_dxf"),
            "evidence": {"proposal_file": str(PROPOSAL.relative_to(REPO)).replace("\\", "/")},
            "confidence": "HIGH",
            "scope": "ED1_BEAM_CONTOUR_CONSOLIDATION",
        })

    model["solids"] = other_solids + new_beams
    known_heights = sum(beam["section_height_m"] is not None for beam in new_beams)
    model["beam_consolidation"] = {
        "status": "APPLIED",
        "proposal_sha256": proposal_sha,
        "proposal_file": str(PROPOSAL.relative_to(REPO)).replace("\\", "/"),
        "old_beam_prisms": len(old_beams),
        "new_beam_centerlines": len(new_beams),
        "confirmed_section_heights": known_heights,
        "unknown_section_heights": len(new_beams) - known_heights,
        "policy": "one analytical centerline per physical beam span; geometry-only widths do not invent section heights",
    }
    write(MODEL, model)

    diff = load(DIFF)
    prior = [change for change in diff.get("changes", []) if change.get("scope") != "ED1_BEAM_CONTOUR_CONSOLIDATION"]
    diff["changes"] = prior + changes
    diff["geometry_hash_after"] = geometry_hash(model)
    diff["geometry_changed"] = True
    diff["post_p1l3_beam_consolidation"] = model["beam_consolidation"]
    write(DIFF, diff)

    result = {
        "status": "PASS",
        "proposal_sha256": proposal_sha,
        "old_beam_prisms": len(old_beams),
        "new_beam_centerlines": len(new_beams),
        "removed_contour_faces_or_details": len(old_beams) - len(new_beams),
        "new_beams_by_floor": dict(Counter(str(beam["floor"]) for beam in new_beams)),
        "confirmed_section_heights": known_heights,
        "unknown_section_heights": len(new_beams) - known_heights,
        "crosswalk": crosswalk,
        "luis_reference_files_modified": 0,
    }
    write(OUT, result)
    OUT_MD.write_text("\n".join([
        "# Aplicacion de consolidacion de vigas EDIFICIO_1",
        "",
        "Estado: `PASS`",
        "",
        f"- Prismas historicos: `{len(old_beams)}`.",
        f"- Centrolineas analiticas: `{len(new_beams)}`.",
        f"- Caras o detalles retirados: `{len(old_beams) - len(new_beams)}`.",
        f"- Alturas de seccion confirmadas o inferidas con evidencia: `{known_heights}`.",
        f"- Alturas de seccion `UNKNOWN`: `{len(new_beams) - known_heights}`; conservan 0.60 m solo como profundidad visual declarada.",
        "- `LUIS_REFERENCE_FILES_MODIFIED = 0`.",
    ]) + "\n", encoding="utf-8")
    print("ED1_BEAM_CONSOLIDATION: PASS")
    print({key: value for key, value in result.items() if key != "crosswalk"})


if __name__ == "__main__":
    main()
