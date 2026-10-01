#!/usr/bin/env python3
"""Read-only graph check of the exact OpenSees contract after rigid DOF ties."""

from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
ANALYSIS = ROOT / "entregas/P1L5/analysis/run_current_opensees.py"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    spec = importlib.util.spec_from_file_location("current_opensees_diagnostic", ANALYSIS)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    master = read(CENTRAL / "model_master.json")
    sections = {r["section_id"]: r for r in read(CENTRAL / "sections.json")["sections"]}
    materials = {r["material_id"]: r for r in read(CENTRAL / "materials.json")["materials"]}
    loads = read(CENTRAL / "loads.json")
    contract = module.prepare_contract(master, sections, materials, loads)
    parent = {r["retained"]: r["retained"] for r in contract["clusters"]}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    members = defaultdict(list)
    skipped = []
    for row, ref in contract["active"]:
        a, b = (contract["tag_to_retained"][int(ref[k])] for k in ("node_i", "node_j"))
        if a == b:
            skipped.append(row["element_id"])
            continue
        parent[find(a)] = find(b)
        members[a].append(row["element_id"])
        members[b].append(row["element_id"])
    components = defaultdict(list)
    for tag in parent:
        components[find(tag)].append(tag)
    supports = set(contract["retained_supports"])
    unsupported = []
    for tags in components.values():
        if not supports.intersection(tags):
            ids = sorted({eid for tag in tags for eid in members.get(tag, [])})
            unsupported.append({"retained_nodes": tags, "element_ids": ids})
    isolated = [tag for tag in parent if tag not in members and tag not in supports]
    print(json.dumps({"contract_active_segments": len(contract["active"]),
                      "skipped_same_cluster_segments": skipped,
                      "connected_components": len(components),
                      "components_without_support": unsupported,
                      "isolated_free_retained_nodes": isolated,
                      "retained_supports": len(supports)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
