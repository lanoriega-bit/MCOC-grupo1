#!/usr/bin/env python3
"""Genera un inventario reproducible del repositorio sin mover ni borrar archivos."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "REPOSITORY_INVENTORY.json"

CANONICAL = {
    "entregas/P1L2/unity_export/model_combined_viewer.json": "GEOMETRY_CURRENT",
    "entregas/P1L2/unity_export/model_1_audited_corrected.json": "GEOMETRY_ED1_CURRENT",
    "entregas/P1L2/unity_export/model_2_viewer.json": "GEOMETRY_ED2_CURRENT",
    "entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json": "FE_CURRENT_CANDIDATE_NOT_RUN",
    "entregas/P1L3/results/a3a4/analysis_model.json": "FE_P1L3_DELIVERED_HISTORY",
    "entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json": "LOAD_CATALOG_CURRENT_NOT_APPLIED",
    "entregas/P1L3/José/viewer_unity/Assets/Main.unity": "UNITY_SCENE_CURRENT",
    "entregas/P1L3/scripts/build_unity_bundle.py": "UNITY_BUNDLE_PIPELINE_CURRENT",
    "entregas/P1L3/scripts/run_p1l3_integrated.py": "OPENSEES_P1L3_DELIVERED_RUNNER",
    "Abrir_Unity.bat": "ENTRYPOINT_CURRENT",
    "Validar_Modelo.bat": "ENTRYPOINT_CURRENT",
    "PROJECT_INDEX.md": "PROJECT_INDEX_CURRENT",
}

SUPERSEDED = {
    "entregas/P1L2/unity_export/model_1_audited.json",
    "entregas/P1L2/unity_export/model_viewer_candidate.json",
    "entregas/P1L2/unity_export/model_viewer_pre_reextraction_backup.json",
    "entregas/P1L2/edificio/modelo/model_viewer_backup_576f014.json",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def classify(path: str) -> str:
    if path in CANONICAL:
        return CANONICAL[path]
    if path == "entregas/P1L2/unity_export/model_viewer.json":
        return "LUIS_REFERENCE_READ_ONLY"
    if path in SUPERSEDED:
        return "SUPERSEDED_RETAINED"
    if path.startswith("entregas/P1L3/José/viewer_unity/"):
        return "UNITY_CURRENT"
    if path.startswith("entregas/P1L2/viewer/") or path == "entregas/P1L2/Abrir_Viewer_P1L2.bat":
        return "LEGACY_DEBUG_VIEWER"
    if path.startswith("entregas/semana2/viewer/") or path == "tools/build_viewer.py":
        return "DELIVERED_LEGACY_VIEWER"
    if path.startswith("entregas/P1L3/results/post_p1l3_candidate/"):
        return "EXPERIMENTAL_CANDIDATE_NOT_RUN"
    if path.startswith("entregas/P1L3/results/") or path.startswith("entregas/P1L3/capacidad_ha/results/"):
        return "P1L3_DELIVERED_HISTORY"
    if "/validacion/" in path or path.startswith("reports/"):
        return "AUDIT_EVIDENCE_OR_REFERENCE"
    if "/scripts/" in path or "/opensees/" in path:
        return "PIPELINE_OR_ANALYSIS_CODE"
    if path.startswith(("entregas/p1l0/", "entregas/p1l1_", "entregas/semana2/", "entregas/semana3/")):
        return "DELIVERED_HISTORY"
    if path.endswith(".md") or path.startswith("docs/"):
        return "DOCUMENTATION"
    return "SUPPORTING_PROJECT_FILE"


def main() -> None:
    tracked = [line for line in git("-c", "core.quotepath=false", "ls-files").splitlines() if line]
    for special in ("tools/inventory_repository.py", "PROJECT_INDEX.md"):
        if special not in tracked and (ROOT / special).is_file():
            tracked.append(special)
    rows = []
    hashes = defaultdict(list)
    for relative in tracked:
        path = ROOT / relative
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        hashes[digest].append(relative)
        rows.append(
            {
                "path": relative,
                "classification": classify(relative),
                "size_bytes": len(data),
                "sha256": digest,
            }
        )

    branches = []
    branch_classes = {
        "origin/codex/pre-p1l4-consolidation": "CURRENT",
        "origin/main": "SHARED_MAIN_REVIEW_BEFORE_INTEGRATION",
        "origin/codex/arquitectura-p4": "DELIVERED_HISTORY_FULLY_CONTAINED",
        "origin/jose-viewer": "SUPERSEDED",
        "origin/luis-semana3-capacidad-ha": "SUPERSEDED_PORTED",
        "origin/luis-gravedad-tributarias": "PARTIALLY_PORTED_REFERENCE",
        "origin/e2-work": "SUPERSEDED_GEOMETRY_REFERENCE",
        "origin/luis": "HISTORICAL_SETUP",
    }
    refs = git("for-each-ref", "--format=%(refname:short)|%(objectname:short)|%(committerdate:short)|%(subject)", "refs/remotes/origin")
    for line in refs.splitlines():
        name, commit, date, subject = line.split("|", 3)
        branches.append(
            {
                "name": name,
                "commit": commit,
                "date": date,
                "subject": subject,
                "classification": branch_classes.get(name, "REVIEW_REQUIRED"),
            }
        )

    exact_duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    output = {
        "format": "MCOC_REPOSITORY_INVENTORY_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "branch": git("branch", "--show-current"),
        "commit": git("rev-parse", "HEAD"),
        "policy": "INVENTORY_ONLY_NO_FILES_MOVED_OR_DELETED",
        "self_exclusion": "REPOSITORY_INVENTORY.json is excluded because a file cannot contain its own stable hash",
        "summary": {
            "tracked_files": len(rows),
            "classification_counts": dict(sorted(Counter(row["classification"] for row in rows).items())),
            "exact_duplicate_groups": len(exact_duplicates),
        },
        "branches": branches,
        "exact_duplicate_groups": exact_duplicates,
        "files": rows,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
