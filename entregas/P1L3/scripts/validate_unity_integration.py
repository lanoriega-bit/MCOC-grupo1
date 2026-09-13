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


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    geometry = load(GEOMETRY)
    unity_geometry = load(UNITY_DATA / "model_viewer.json")
    candidate = load(CANDIDATE)
    diagnostic = load(DIAGNOSTIC)
    manifest = load(MANIFEST)

    assert geometry == unity_geometry, "Unity no contiene la geometria canonica vigente"
    assert len(geometry["solids"]) == 1212
    assert set(geometry["expectedFloors"]) == {"S1", "P1", "P2", "P3", "P4"}
    assert candidate["status"] == "CANDIDATE_NOT_APPROVED_NOT_RUN"
    assert candidate["run_policy"]["opensees_run"] is False
    assert len(diagnostic["members"]) == len(candidate["elements"]) == 1167

    focus = [row for row in diagnostic["elements"] if row["diagnostic_focus"]]
    assert len(focus) == 72
    assert Counter(row["validation"] for row in focus) == {
        "CONNECTED_EXPECTED": 31,
        "FREE_END_EXPECTED": 1,
        "DISCONNECTED_ERROR": 31,
        "UNRESOLVED": 9,
    }
    one_to_many = [row for row in diagnostic["elements"] if len(row["crosswalk"]) > 1]
    assert len(one_to_many) == 33
    assert max(len(row["crosswalk"]) for row in diagnostic["elements"]) == 3

    state = manifest["data_state"]
    assert state["geometry"] == "POST_P1L3_CURRENT"
    assert state["fe_diagnosis"] == "POST_P1L3_CANDIDATE_NOT_RUN"
    assert state["analysis_results"] == "P1L3_DELIVERED_HISTORICAL"
    assert state["loads"] == "P1L3_DELIVERED_HISTORICAL"
    assert state["capacity"] == "P1L3_DELIVERED_HISTORICAL"
    for item in manifest["files"]:
        path = UNITY_DATA / item["name"]
        assert path.is_file(), f"Falta {item['name']}"
        assert sha256(path) == item["sha256"], f"Hash incorrecto: {item['name']}"

    print("UNITY_INTEGRATION_VALIDATION = PASS")
    print("Geometria actual: 1212 solidos")
    print("Malla FE candidata: 1167 miembros; NO EJECUTADA")
    print("Diagnostico: 72 elementos; 33 crosswalks 1:N")
    print("Resultados/cargas/capacidad: snapshot historico P1L3")


if __name__ == "__main__":
    main()
