#!/usr/bin/env python3
"""Validate the P1L5 central model against current PRE5 identity."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

MODEL_MASTER = HERE / "model_master.json"
SECTIONS = HERE / "sections.json"
MATERIALS = HERE / "materials.json"
LOADS = HERE / "loads.json"
GEOMETRY = ROOT / "entregas/P1L2/unity_export/model_combined_viewer.json"
FE_CANDIDATE = ROOT / "entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json"
READINESS = ROOT / "entregas/PRE_P1L5/current_readiness/structural_readiness.json"

DOCUMENTED_PRE5 = {
    "solid_count": 695,
    "beam_count": 466,
    "fe_candidate_members": 647,
    "pending_element_id": "E2-P4-V-009",
}


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    master = load(MODEL_MASTER)
    sections = load(SECTIONS)
    materials = load(MATERIALS)
    loads = load(LOADS)
    geometry = load(GEOMETRY)
    fe = load(FE_CANDIDATE)
    readiness = load(READINESS)

    nodes = master.get("nodes", [])
    elements = master.get("elements", [])
    supports = master.get("supports", [])
    aliases = master.get("aliases", [])

    node_ids = [row.get("node_id") for row in nodes]
    element_ids = [row.get("element_id") for row in elements]
    support_ids = [row.get("support_id") for row in supports]
    section_ids = {row.get("section_id") for row in sections.get("sections", [])}
    material_ids = {row.get("material_id") for row in materials.get("materials", [])}

    if len(node_ids) != len(set(node_ids)):
        fail(errors, "Duplicate node_id in model_master.nodes")
    if len(element_ids) != len(set(element_ids)):
        fail(errors, "Duplicate element_id in model_master.elements")
    if len(support_ids) != len(set(support_ids)):
        fail(errors, "Duplicate support_id in model_master.supports")

    node_set = set(node_ids)
    for row in elements:
        if not isinstance(row.get("active"), bool):
            fail(errors, f"active must be bool for {row.get('element_id')}")
        for node_id in row.get("nodes", []):
            if node_id not in node_set:
                fail(errors, f"Missing node {node_id} referenced by {row.get('element_id')}")
        if row.get("section_id") not in section_ids:
            fail(errors, f"Missing section_id {row.get('section_id')} for {row.get('element_id')}")
        if row.get("material_id") not in material_ids:
            fail(errors, f"Missing material_id {row.get('material_id')} for {row.get('element_id')}")
    for row in supports:
        if not isinstance(row.get("active"), bool):
            fail(errors, f"active must be bool for support {row.get('support_id')}")
        for node_id in row.get("nodes", []):
            if node_id not in node_set:
                fail(errors, f"Missing node {node_id} referenced by support {row.get('support_id')}")
        if row.get("section_id") not in section_ids:
            fail(errors, f"Missing support section_id {row.get('section_id')} for {row.get('support_id')}")
        if row.get("material_id") not in material_ids:
            fail(errors, f"Missing support material_id {row.get('material_id')} for {row.get('support_id')}")

    active_element_set = set(element_ids) | set(support_ids)
    for row in aliases:
        alias = row.get("alias")
        canonical = row.get("canonical_element_id")
        if canonical not in active_element_set:
            fail(errors, f"Alias {alias} maps to missing canonical {canonical}")
        if alias in active_element_set and alias != canonical:
            fail(errors, f"Alias {alias} collides with active central element")

    merged_from_count = sum(len(row.get("merged_from", [])) for row in elements + supports)
    if merged_from_count < len(aliases):
        warnings.append("Not every alias appears in merged_from; check non-geometric aliases if needed.")

    opensees_tags = []
    analysis_ids = []
    for row in elements:
        for ref in row.get("analysis_refs", []):
            if ref.get("opensees_tag") is not None:
                opensees_tags.append(ref.get("opensees_tag"))
            if ref.get("analysis_id") is not None:
                analysis_ids.append(ref.get("analysis_id"))
    if len(opensees_tags) != len(set(opensees_tags)):
        fail(errors, "Duplicate opensees_tag in analysis_refs")
    if len(analysis_ids) != len(set(analysis_ids)):
        fail(errors, "Duplicate analysis_id in analysis_refs")

    source_counts = Counter(row.get("category") for row in geometry.get("solids", []))
    central_counts = Counter(row.get("type") for row in elements)
    if len(geometry.get("solids", [])) != DOCUMENTED_PRE5["solid_count"]:
        fail(errors, f"Current source solid count differs from documented PRE5: {len(geometry.get('solids', []))} != {DOCUMENTED_PRE5['solid_count']}")
    if source_counts.get("beam", 0) != DOCUMENTED_PRE5["beam_count"]:
        fail(errors, f"Current source beam count differs from documented PRE5: {source_counts.get('beam', 0)} != {DOCUMENTED_PRE5['beam_count']}")
    if len(fe.get("elements", [])) != DOCUMENTED_PRE5["fe_candidate_members"]:
        fail(errors, f"Current FE candidate member count differs from documented PRE5: {len(fe.get('elements', []))} != {DOCUMENTED_PRE5['fe_candidate_members']}")

    if len(elements) + len(supports) != len(geometry.get("solids", [])):
        fail(errors, "Central active elements + supports do not reproduce source solid count")
    for category in ("beam", "column", "wall", "slab"):
        if central_counts.get(category, 0) != source_counts.get(category, 0):
            fail(errors, f"Central {category} count differs from source: {central_counts.get(category, 0)} != {source_counts.get(category, 0)}")
    if len(supports) != source_counts.get("support", 0):
        fail(errors, f"Central support count differs from source: {len(supports)} != {source_counts.get('support', 0)}")

    pending_rows = [row for row in readiness.get("pending_elements", []) if row.get("element_id") == DOCUMENTED_PRE5["pending_element_id"]]
    central_pending = master.get("current_pre5_identity", {}).get("pending_case", {})
    if not pending_rows:
        fail(errors, "Readiness source does not contain pending E2-P4-V-009")
    if central_pending.get("element_id") != DOCUMENTED_PRE5["pending_element_id"]:
        fail(errors, "model_master pending_case does not preserve E2-P4-V-009")

    if loads.get("audited_load_catalog", {}).get("status") != "AUDITED_NOT_APPLIED":
        fail(errors, "loads.json audited catalog must be AUDITED_NOT_APPLIED")
    if loads.get("tributary_areas", {}).get("status") != "HISTORICAL":
        fail(errors, "loads.json tributary areas must be HISTORICAL")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "nodes": len(nodes),
            "elements": len(elements),
            "supports": len(supports),
            "beams": central_counts.get("beam", 0),
            "columns": central_counts.get("column", 0),
            "walls": central_counts.get("wall", 0),
            "slabs": central_counts.get("slab", 0),
            "sections": len(section_ids),
            "materials": len(material_ids),
            "analysis_refs": len(analysis_ids),
            "aliases": len(aliases),
        },
        "source_identity": {
            "solid_count": len(geometry.get("solids", [])),
            "category_counts": dict(source_counts),
            "fe_candidate_members": len(fe.get("elements", [])),
            "pending": DOCUMENTED_PRE5["pending_element_id"],
        },
    }
    return result


def main() -> None:
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
