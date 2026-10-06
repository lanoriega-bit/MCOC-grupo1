#!/usr/bin/env python3
"""Run loads and OpenSees only inside an isolated wall candidate directory."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
ANALYSIS = ROOT / "entregas/P1L5/analysis"


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
    folder = args.candidate_dir.resolve()
    qa = json.loads((folder / "candidate_qa.json").read_text(encoding="utf-8"))
    if qa["status"] != "PASS" or qa["floating_components"] or qa["fe_components_without_support"]:
        raise SystemExit("Candidate topology/support graph has not passed")
    for name in ("materials.json", "loads.json"):
        (folder / name).write_bytes((CENTRAL / name).read_bytes())
    loads = module(ANALYSIS / "build_current_loads.py", "isolated_current_loads")
    loads.CENTRAL = folder
    loads.MASTER_PATH = folder / "model_master.json"
    loads.LOADS_PATH = folder / "loads.json"
    loads.SECTIONS_PATH = folder / "sections.json"
    loads.MATERIALS_PATH = folder / "materials.json"
    loads.OUT = folder / "generated"
    loads.main()
    analysis = module(ANALYSIS / "run_current_opensees.py", "isolated_current_opensees")
    analysis.CENTRAL = folder
    analysis.OUT = folder / "results/current"
    analysis.main()
    manifest = json.loads((analysis.OUT / "manifest.json").read_text(encoding="utf-8"))
    print(json.dumps({"status": manifest["status"], "cases": manifest["cases"],
                      "candidate_dir": str(folder)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
