#!/usr/bin/env python3
"""Exhaustive, fail-closed audit of the integrated central model."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
OUT = Path(__file__).resolve().parent


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> None:
    master = load(CENTRAL / "model_master.json")
    sections_data = load(CENTRAL / "sections.json")
    materials_data = load(CENTRAL / "materials.json")
    loads = load(CENTRAL / "loads.json")
    sections = {x["section_id"]: x for x in sections_data["sections"]}
    materials = {x["material_id"]: x for x in materials_data["materials"]}
    elements = master["elements"]
    topology = master["fe_topology"]
    fe_nodes = {
        int(tag): [float(row["x"]), float(row["y"]), float(row["z"])]
        for tag, row in topology["nodes"].items()
    }

    checks = {}
    ids = [x["element_id"] for x in elements] + [x["support_id"] for x in master["supports"]]
    checks["unique_element_ids"] = "PASS" if len(ids) == len(set(ids)) else "FAIL"
    node_ids = [x["node_id"] for x in master["nodes"]]
    checks["unique_model_node_ids"] = "PASS" if len(node_ids) == len(set(node_ids)) else "FAIL"
    coords = [tuple(round(float(v), 6) for v in x["coord_m"]) for x in master["nodes"]]
    checks["duplicate_model_node_coordinates"] = "PASS" if len(coords) == len(set(coords)) else "FAIL"

    refs = [ref for element in elements for ref in element.get("analysis_refs", [])]
    tags = [ref["opensees_tag"] for ref in refs]
    analysis_ids = [ref["analysis_id"] for ref in refs]
    checks["unique_fe_tags"] = "PASS" if len(tags) == len(set(tags)) and len(analysis_ids) == len(set(analysis_ids)) else "FAIL"
    zero_length = []
    repeated_segments = defaultdict(list)
    for element in elements:
        for ref in element.get("analysis_refs", []):
            ni, nj = ref["node_i"], ref["node_j"]
            a, b = fe_nodes[ni], fe_nodes[nj]
            length = math.dist(a, b)
            if length < 1.0e-6:
                zero_length.append(ref["analysis_id"])
            repeated_segments[tuple(sorted((ni, nj)))].append(ref["analysis_id"])
    exact_overlap = {str(k): v for k, v in repeated_segments.items() if len(v) > 1}
    checks["zero_length_fe_segments"] = "PASS" if not zero_length else "FAIL"
    checks["exact_duplicate_fe_segments"] = "PASS" if not exact_overlap else "FAIL"

    structural = [x for x in elements if x["type"] in {"beam", "column", "wall"}]
    unknown = [x["element_id"] for x in structural if x["material_id"] == "MAT_UNKNOWN"]
    missing_elastic_materials = sorted({
        x["material_id"] for x in structural
        if materials[x["material_id"]].get("elastic", {}).get("E_pa", {}).get("value") is None
    })
    checks["section_references"] = "PASS" if all(x["section_id"] in sections for x in elements) else "FAIL"
    checks["material_references"] = "PASS" if all(x["material_id"] in materials for x in elements) else "FAIL"
    checks["current_material_assignments_complete"] = "PASS" if not unknown else "BLOCKED"
    checks["current_elastic_properties_complete"] = "PASS" if not missing_elastic_materials else "BLOCKED"

    floating = topology.get("floating_excluded", {})
    floating_ids = sorted({
        eid for component in floating.get("components", [])
        for eid in component.get("geometry_element_ids", [])
    })
    checks["fe_connectivity"] = "PASS" if not floating_ids else "BLOCKED"
    load_catalog = loads.get("audited_load_catalog", {})
    tributaries = loads.get("tributary_areas", {})
    checks["loads_current"] = "PASS" if load_catalog.get("status") == "APPLIED_CURRENT" else "BLOCKED"
    checks["tributaries_current"] = "PASS" if tributaries.get("status") == "CURRENT_VALIDATED" else "BLOCKED"

    hard_failures = [name for name, state in checks.items() if state == "FAIL"]
    blockers = [name for name, state in checks.items() if state == "BLOCKED"]
    result = {
        "schema": "P1L5_INTEGRATED_MODEL_AUDIT_v1",
        "integrity_status": "PASS" if not hard_failures else "FAIL",
        "analysis_readiness": "READY" if not hard_failures and not blockers else "BLOCKED",
        "checks": checks,
        "counts": {
            "central_nodes": len(master["nodes"]),
            "fe_nodes": len(fe_nodes),
            "physical_elements": len(elements),
            "visual_supports": len(master["supports"]),
            "beams": sum(x["type"] == "beam" for x in elements),
            "columns": sum(x["type"] == "column" for x in elements),
            "walls": sum(x["type"] == "wall" for x in elements),
            "slabs": sum(x["type"] == "slab" for x in elements),
            "fe_segments": len(refs),
            "fe_constraints": len(topology.get("constraints", [])),
            "fe_support_nodes": len(topology.get("support_node_tags", [])),
            "disconnected_components": len(floating.get("components", [])),
            "unknown_structural_materials": len(unknown),
            "load_catalog_entries": len(load_catalog.get("entries", [])),
            "tributary_pans": len(tributaries.get("panos", [])),
        },
        "blockers": {
            "checks": blockers,
            "disconnected_elements": floating_ids,
            "unknown_material_element_ids": unknown,
            "missing_elastic_material_ids": missing_elastic_materials,
            "load_status": load_catalog.get("status"),
            "tributary_status": tributaries.get("status"),
        },
        "hard_failures": hard_failures,
        "diagnostics": {"zero_length": zero_length, "exact_duplicate_segments": exact_overlap},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "integration_qa.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# QA del modelo integrado", "",
        f"- Integridad de contratos: **{result['integrity_status']}**",
        f"- Preparación para análisis CURRENT: **{result['analysis_readiness']}**", "",
        "| Control | Estado |", "|---|---|",
        *[f"| {name} | {state} |" for name, state in checks.items()], "",
        "## Conteos", "", "```json", json.dumps(result["counts"], ensure_ascii=False, indent=2), "```", "",
        "## Bloqueos reales", "",
        f"- Componente desconectado: {', '.join(floating_ids) or 'ninguno'}.",
        f"- Elementos estructurales con material desconocido: {len(unknown)}.",
        f"- Materiales sin E actual: {', '.join(missing_elastic_materials) or 'ninguno'}.",
        f"- Cargas: `{load_catalog.get('status')}`; tributarias: `{tributaries.get('status')}`.",
        "- No se agregaron apoyos, enlaces ni propiedades ficticias para cambiar este veredicto.",
    ]
    (OUT / "INTEGRATION_QA.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"integrity": result["integrity_status"], "analysis": result["analysis_readiness"], "blockers": blockers}))
    if hard_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
