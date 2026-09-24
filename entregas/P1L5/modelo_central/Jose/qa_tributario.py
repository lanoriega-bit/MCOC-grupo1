#!/usr/bin/env python3
"""Report tributary-data readiness without inventing a CURRENT equilibrium check."""

from __future__ import annotations

import json
from datetime import datetime, timezone
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
    if catalog.get("status") != "APPLIED_CURRENT":
        blockers.append(f"load catalog status={catalog.get('status')}")
    if tributary.get("status") != "CURRENT_VALIDATED":
        blockers.append(f"tributary status={tributary.get('status')}")
    blockers.append("CURRENT OpenSees results are absent; reaction equilibrium cannot be evaluated")
    result = {
        "schema": "P1L2_TRIBUTARY_READINESS_v4",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED" if blockers else "PASS",
        "catalog_entries": len(entries),
        "tributary_pans": len(pans),
        "catalog_status": catalog.get("status"),
        "tributary_status": tributary.get("status"),
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
        "- La conservación CURRENT se evaluará solo tras aplicar cargas y ejecutar OpenSees sobre el modelo central.", "",
        "Bloqueos:", *[f"- {item}" for item in blockers],
    ]
    (HERE / "qa_tributario.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "blockers": len(blockers)}))


if __name__ == "__main__":
    main()
