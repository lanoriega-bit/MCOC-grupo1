#!/usr/bin/env python3
"""Rebuild and validate the isolated wall candidate without changing CURRENT."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from fe_support_graph import unsupported_components


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(loaded)
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", required=True, type=Path)
    args = parser.parse_args()
    directory = args.candidate_dir.resolve()
    if not (directory / "restoration_manifest.json").is_file():
        raise SystemExit("Candidate manifest missing")

    fe = module(CENTRAL / "rebuild_central_fe_topology.py", "isolated_fe_builder")
    fe.MASTER_PATH = directory / "model_master.json"
    fe.SECTIONS_PATH = directory / "sections.json"
    fe.ADAPTER_PATH = directory / "generated/current_geometry_for_fe.json"
    fe.CANDIDATE_PATH = directory / "generated/rebuilt_fe_topology.json"
    fe.CANDIDATE_REPORT = directory / "generated/rebuilt_fe_topology.md"
    fe.main()

    validation = module(CENTRAL / "validate_central_model.py", "isolated_model_validator")
    validation.MODEL_MASTER = directory / "model_master.json"
    validation.SECTIONS = directory / "sections.json"
    validation.MATERIALS = CENTRAL / "materials.json"
    validation.LOADS = CENTRAL / "loads.json"
    result = validation.validate()
    master = json.loads((directory / "model_master.json").read_text(encoding="utf-8"))
    topology = master["fe_topology"]
    unsupported = unsupported_components(master)
    floating_ids = sorted({identifier
                           for component in topology["floating_excluded"]["components"]
                           for identifier in component["geometry_element_ids"]})
    report = {
        "status": result["status"], "errors": result["errors"], "warnings": result["warnings"],
        "counts": result["counts"],
        "floating_components": topology["floating_excluded"]["n_componentes"],
        "floating_geometry_elements": topology["floating_excluded"]["n_geometry_elements"],
        "floating_ids": floating_ids,
        "fe_components_without_support": unsupported,
        "connectivity_validation": topology.get("connectivity_validation"),
        "opensees_executed": False,
    }
    (directory / "candidate_qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if result["status"] != "PASS" or report["floating_components"] != 0 or unsupported:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
