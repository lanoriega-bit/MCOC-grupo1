#!/usr/bin/env python3
"""Valida el bundle Unity vigente sin ejecutar OpenSees ni recalcular cargas."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UNITY_DATA = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
GEOMETRY = ROOT / "entregas/P1L2/unity_export/model_combined_viewer.json"
CANDIDATE = ROOT / "entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json"
DIAGNOSTIC = UNITY_DATA / "post_p1l3_fe_diagnostic.json"
MANIFEST = UNITY_DATA / "integration_manifest.json"
PROJECT_STATE = UNITY_DATA / "project_state.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_sha256(path: Path) -> set[str]:
    """Accept the tracked JSON hash across Git's Windows EOL checkout policy."""
    data = path.read_bytes()
    hashes = {hashlib.sha256(data).hexdigest()}
    if path.suffix.lower() == ".json":
        hashes.add(hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest())
    return hashes


def main() -> None:
    geometry = load(GEOMETRY)
    unity_geometry = load(UNITY_DATA / "model_viewer.json")
    candidate = load(CANDIDATE)
    diagnostic = load(DIAGNOSTIC)
    manifest = load(MANIFEST)
    project_state = load(PROJECT_STATE)

    assert geometry == unity_geometry, "Unity no contiene la geometria canonica vigente"
    assert len(geometry["solids"]) == project_state["geometry_count"]
    assert set(geometry["expectedFloors"]) == {"S1", "P1", "P2", "P3", "P4"}
    assert candidate["status"] == "CANDIDATE_NOT_APPROVED_NOT_RUN"
    assert candidate["run_policy"]["opensees_run"] is False
    assert len(diagnostic["members"]) == len(candidate["elements"]) == project_state["fe_members"]

    focus = [row for row in diagnostic["elements"] if row["diagnostic_focus"]]
    summary = diagnostic["summary"]
    assert len(focus) == summary["focus_elements"]
    floating_ids = {gid for c in candidate['floating_excluded']['components'] for gid in c['geometry_element_ids']}
    assert floating_ids <= {r['element_id'] for r in focus}, 'Current floating geometry omitted from diagnostic focus'
    validation_counts = Counter(row["validation"] for row in focus)
    for name, count in summary["validation_counts"].items():
        assert validation_counts[name] == count
    assert validation_counts["UNRESOLVED"] == summary["candidate_floating_geometry_elements"]
    one_to_many = [row for row in diagnostic["elements"] if len(row["crosswalk"]) > 1]
    assert len(one_to_many) == summary["geometry_elements_split_into_multiple_fe"]
    assert max(len(row["crosswalk"]) for row in diagnostic["elements"]) == summary["max_fe_segments_per_geometry"]

    state = manifest["data_state"]
    assert state["geometry"] == "POST_P1L4_CURRENT"
    assert state['current_results'] == 'NONE'
    assert state['historical_results_default_visible'] is False
    assert "RESULTADOS_P1L4_HISTORICOS_NO_RECALCULADOS" in state["compatibility_warning"]
    assert state["fe_diagnosis"] == "POST_P1L3_CANDIDATE_NOT_RUN"
    assert state["analysis_results"] == "P1L3_DELIVERED_HISTORICAL"
    assert state["loads"] == "P1L3_DELIVERED_HISTORICAL"
    assert state["capacity"] == "P1L3_DELIVERED_HISTORICAL"
    for item in manifest["files"]:
        path = UNITY_DATA / item["name"]
        assert path.is_file(), f"Falta {item['name']}"
        assert item["sha256"] in accepted_sha256(path), f"Hash incorrecto: {item['name']}"

    print("UNITY_INTEGRATION_VALIDATION = PASS")
    print(f"Geometria actual: {len(geometry['solids'])} solidos (POST_P1L4_CURRENT)")
    print(f"Malla FE candidata: {len(candidate['elements'])} miembros; NO EJECUTADA")
    print(f"Diagnostico: {len(focus)} elementos; {len(one_to_many)} crosswalks 1:N; todos los flotantes cubiertos")
    print("Resultados/cargas/capacidad: snapshot historico P1L3")


if __name__ == "__main__":
    main()
