#!/usr/bin/env python3
"""Report tributary-data readiness without inventing a CURRENT equilibrium check."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CENTRAL = HERE.parent


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> None:
    loads = load(CENTRAL / "loads.json")
    catalog = loads.get("audited_load_catalog", {})
    tributary = loads.get("tributary_areas", {})
    entries = catalog.get("entries", [])
    pans = tributary.get("panos", [])
    blockers = []
    if catalog.get("status") not in {"APPLIED_CURRENT", "CURRENT_PARTIAL_WITH_DOCUMENTED_UNRESOLVED"}:
        blockers.append(f"load catalog status={catalog.get('status')}")
    if tributary.get("status") not in {"CURRENT_VALIDATED", "CURRENT_WITH_DOCUMENTED_FALLBACKS"}:
        blockers.append(f"tributary status={tributary.get('status')}")
    current = loads.get("current_load_application", {})
    conservation = current.get("conservation", {})
    for case in ("G", "Q"):
        if conservation.get(case, {}).get("status") != "PASS":
            blockers.append(f"conservation {case} is not PASS")
    results_path = HERE.parents[1] / "analysis" / "results" / "current" / "manifest.json"
    results = load(results_path) if results_path.exists() else {}
    if results.get("status") != "PASS":
        blockers.append("CURRENT OpenSees manifest is not PASS")
    result = {
        "schema": "P1L2_TRIBUTARY_READINESS_v4",
        "status": "BLOCKED" if blockers else "PASS",
        "catalog_entries": len(entries),
        "tributary_pans": len(pans),
        "catalog_status": catalog.get("status"),
        "tributary_status": tributary.get("status"),
        "conservation": conservation,
        "opensees_status": results.get("status"),
        "blockers": blockers,
        "correction": "G and Q are independent load cases and are not expected to have equal column axial sums.",
        "historical_results_policy": "May be audited retrospectively, never used as CURRENT fallback.",
    }
    (HERE / "qa_tributario.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# Preparación tributaria actual", "",
        f"**Estado: {result['status']}**", "",
        f"- Catálogo auditado: {len(entries)} entradas (`{catalog.get('status')}`).",
        f"- Paños tributarios conservados: {len(pans)} (`{tributary.get('status')}`).",
        "- No se compara G con Q como si debieran ser iguales: son casos físicos distintos.",
        f"- Conservación G: `{conservation.get('G',{}).get('status')}`; Q: `{conservation.get('Q',{}).get('status')}`.",
        f"- OpenSees CURRENT: `{results.get('status')}`.", "",
        "Bloqueos:", *[f"- {item}" for item in blockers],
    ]
    (HERE / "qa_tributario.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "blockers": len(blockers)}))


if __name__ == "__main__":
    main()
