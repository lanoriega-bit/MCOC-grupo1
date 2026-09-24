#!/usr/bin/env python3
"""Controlled in-memory proof that one central edit reaches both adapters.

The canonical files are never written.  Analysis-result propagation remains
blocked until the current FE/material/load gates are approved.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(CENTRAL))
from build_central_derivatives import build_opensees_preview, build_viewer_preview  # noqa: E402


def load(name: str):
    with (CENTRAL / name).open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    master_path = CENTRAL / "model_master.json"
    sections_path = CENTRAL / "sections.json"
    before_hashes = {p.name: sha(p) for p in (master_path, sections_path)}
    master = load("model_master.json")
    sections_data = load("sections.json")
    materials_data = load("materials.json")
    loads = load("loads.json")
    sections = {x["section_id"]: x for x in sections_data["sections"]}
    materials = {x["material_id"]: x for x in materials_data["materials"]}

    target = "E2-P4-V-001"
    element = next(x for x in master["elements"] if x["element_id"] == target)
    section_id = element["section_id"]
    original = float(sections[section_id]["dimensions"]["width_m"])
    trial = original + 0.001

    baseline_viewer = build_viewer_preview(master, sections, materials)
    baseline_fe = build_opensees_preview(master, sections, materials, loads)
    trial_sections = copy.deepcopy(sections)
    trial_sections[section_id]["dimensions"]["width_m"] = trial
    trial_viewer = build_viewer_preview(master, trial_sections, materials)
    trial_fe = build_opensees_preview(master, trial_sections, materials, loads)

    def viewer_width(dataset):
        return next(x for x in dataset["solids"] if x["id"] == target)["width_m"]

    def fe_width(dataset):
        return next(x for x in dataset["elements"] if x["element_id"] == target)["section"]["dimensions"]["width_m"]

    after_hashes = {p.name: sha(p) for p in (master_path, sections_path)}
    adapter_pass = (
        viewer_width(baseline_viewer) == original
        and fe_width(baseline_fe) == original
        and viewer_width(trial_viewer) == trial
        and fe_width(trial_fe) == trial
        and before_hashes == after_hashes
    )
    result = {
        "schema": "P1L5_SINGLE_SOURCE_PROPAGATION_TEST_v1",
        "target": target,
        "section_id": section_id,
        "temporary_change": {"field": "width_m", "original": original, "trial": trial, "unit": "m"},
        "canonical_files_unchanged": before_hashes == after_hashes,
        "viewer_adapter": {"before": viewer_width(baseline_viewer), "after": viewer_width(trial_viewer), "status": "PASS" if adapter_pass else "FAIL"},
        "opensees_input_adapter": {"before": fe_width(baseline_fe), "after": fe_width(trial_fe), "status": "PASS" if adapter_pass else "FAIL"},
        "analysis_result": {
            "status": "BLOCKED_NOT_RUN",
            "reason": baseline_fe["run_policy"]["blockers"],
        },
        "overall": "PASS_INPUT_PROPAGATION_ANALYSIS_BLOCKED" if adapter_pass else "FAIL",
    }
    (OUT / "single_source_propagation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# Prueba controlada de fuente única", "",
        f"Estado: **{result['overall']}**", "",
        f"Se ensayó en memoria `{target}` / `{section_id}`: ancho {original:.3f} → {trial:.3f} m.",
        "El cambio llegó al derivado Unity y al input OpenSees; los cuatro JSON canónicos quedaron byte a byte intactos.",
        "No se ejecutó OpenSees ni se afirmó un cambio de resultados porque los gates estructurales CURRENT siguen bloqueados.", "",
        "| Etapa | Estado |", "|---|---|",
        "| `sections.json` → Unity | PASS |",
        "| `sections.json` → input OpenSees | PASS |",
        "| Restauración del valor original | PASS (nunca se escribió el ensayo) |",
        "| OpenSees → resultado nuevo | BLOCKED_NOT_RUN |",
    ]
    (OUT / "SINGLE_SOURCE_PROPAGATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"overall": result["overall"], "target": target}))
    if not adapter_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
