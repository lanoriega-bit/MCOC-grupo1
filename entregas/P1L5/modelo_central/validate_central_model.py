#!/usr/bin/env python3
"""Validate the self-contained P1L5 central model.

Historical/PRE5 files are provenance, never a silent runtime fallback.
"""

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

    nodes = master.get("nodes", [])
    elements = master.get("elements", [])
    supports = master.get("supports", [])
    aliases = master.get("aliases", [])
    topology = master.get("fe_topology", {})
    identity = master.get("current_pre5_identity", {})

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

    central_counts = Counter(row.get("type") for row in elements)
    expected_counts = identity.get("category_counts", {})
    if len(elements) + len(supports) != identity.get("solid_count"):
        fail(errors, "Central active elements + visual supports do not match current_pre5_identity.solid_count")
    for category in ("beam", "column", "wall", "slab"):
        if central_counts.get(category, 0) != expected_counts.get(category, 0):
            fail(errors, f"Central {category} count differs from current identity")
    if len(supports) != expected_counts.get("support", 0):
        fail(errors, "Central visual support count differs from current identity")

    fe_nodes = topology.get("nodes", {})
    fe_supports = topology.get("support_node_tags", [])
    expected_total = identity.get("fe_total_segments", identity.get("fe_candidate_members"))
    if len(analysis_ids) != expected_total:
        fail(errors, "Embedded FE segment count differs from current identity")
    if len(fe_nodes) != identity.get("fe_candidate_nodes"):
        fail(errors, "Embedded FE node count differs from current identity")
    if len(fe_supports) != identity.get("fe_candidate_supports"):
        fail(errors, "Embedded FE support count differs from current identity")
    for tag in fe_supports:
        if str(tag) not in fe_nodes:
            fail(errors, f"FE support node {tag} is absent from embedded FE nodes")
    for row in elements:
        for ref in row.get("analysis_refs", []):
            if str(ref.get("node_i")) not in fe_nodes or str(ref.get("node_j")) not in fe_nodes:
                fail(errors, f"Embedded FE node missing for {ref.get('analysis_id')}")

    central_pending = identity.get("pending_case")
    floating_ids = {
        element_id
        for component in topology.get("floating_excluded", {}).get("components", [])
        for element_id in component.get("geometry_element_ids", [])
    }
    if central_pending:
        pending_id = central_pending.get("element_id")
        if pending_id not in floating_ids:
            fail(errors, "Documented pending case is absent from the embedded disconnected components")
        pending_row = next((row for row in elements if row.get("element_id") == pending_id), None)
        if not pending_row or pending_row.get("active"):
            fail(errors, "Documented pending case must be retained as an inactive element")
    elif floating_ids:
        fail(errors, "Embedded FE topology has disconnected elements but current identity has no pending case")

    active_analysis_refs = sum(
        len(row.get("analysis_refs", []))
        for row in elements
        if row.get("type") in {"beam", "column", "wall"} and row.get("active")
    )
    if active_analysis_refs != identity.get("fe_active_segments"):
        fail(errors, "Active FE segment count differs from current identity")

    if loads.get("audited_load_catalog", {}).get("status") not in {
        "AUDITED_NOT_APPLIED",
        "CURRENT_PARTIAL_WITH_DOCUMENTED_UNRESOLVED",
        "CURRENT_RECONSTRUCTED_WITH_EXPLICIT_UNRESOLVED",
        "APPLIED_CURRENT",
    }:
        fail(errors, "loads.json has an unsupported audited load catalog status")
    if loads.get("tributary_areas", {}).get("status") not in {
        "HISTORICAL",
        "CURRENT_VALIDATED",
        "CURRENT_WITH_DOCUMENTED_FALLBACKS",
        "CURRENT_RECOMPUTED",
    }:
        fail(errors, "loads.json has an unsupported tributary-area status")

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
            "active_analysis_refs": active_analysis_refs,
            "aliases": len(aliases),
        },
        "current_identity": {
            "solid_count": len(elements) + len(supports),
            "category_counts": dict(central_counts | Counter({"support": len(supports)})),
            "fe_total_members": len(analysis_ids),
            "fe_active_members": active_analysis_refs,
            "fe_nodes": len(fe_nodes),
            "fe_supports": len(fe_supports),
            "pending": central_pending.get("element_id") if central_pending else None,
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
