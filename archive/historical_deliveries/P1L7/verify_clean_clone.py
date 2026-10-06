"""Verify README regeneration in an isolated clone, without changing the live viewer.

Create a clone and its .venv-p1l5 first. This script records commands actually run,
exit codes, semantic input signatures and numerical agreement. It does not assert
Unity or standalone execution merely because the JSON tests pass.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clone-root", required=True, type=Path)
    args = parser.parse_args()
    clone = args.clone_root.resolve()
    if clone == ROOT or not (clone / ".git").is_dir():
        raise ValueError("Expected a separate Git clone, not the live project")
    python = clone / ".venv-p1l5/Scripts/python.exe"
    if not python.is_file():
        raise ValueError("Install pinned requirements in the clone first")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip()
    commands = [
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "entregas/P1L7/reanalyse_current.ps1"],
        [str(python), "-B", "entregas/P1L7/test_week7_loads.py"],
        [str(python), "-B", "entregas/P1L6/transform/test_ar_transform.py"],
        [str(python), "-B", "tools/test_project_entrypoint.py"],
        [str(python), "-B", "entregas/P1L6/slab_reconstruction/validate_slab_cleanup.py"],
    ]
    runs = []
    for index, command in enumerate(commands):
        run = subprocess.run(command, cwd=clone, capture_output=True, text=True, encoding="utf-8", errors="replace")
        log = OUT / f"clean_clone_{index}.log"
        log.write_text(run.stdout + run.stderr, encoding="utf-8")
        runs.append({"command": ["python" if arg == str(python) else arg for arg in command],
                     "exit_code": run.returncode, "log": log.name})
        print(f"{index + 1}/{len(commands)} exit={run.returncode}")
        if run.returncode:
            break
    central = Path("entregas/P1L5/modelo_central")
    result = Path("entregas/P1L5/analysis/results/current/manifest.json")
    original, restored = read(ROOT / result), read(clone / result)
    checks = {
        "all_commands_completed": len(runs) == len(commands) and all(r["exit_code"] == 0 for r in runs),
        "same_logical_settings": read(ROOT / central / "analysis_settings.json") == read(clone / central / "analysis_settings.json"),
        "same_case_response_and_equilibrium": original["cases"] == restored["cases"],
        "same_load_contract": original["load_contract"] == restored["load_contract"],
        "same_canonical_runtime": original["runtime"] == restored["runtime"],
        "clone_analysis_pass": restored["status"] == "PASS",
    }
    report = {"status": "PASS" if all(checks.values()) else "FAIL", "generated_utc": datetime.now(timezone.utc).isoformat(),
              "tested_commit": commit, "clone_method": "LOCAL_CLONE_OF_COMMIT_PUSHED_TO_GITHUB",
              "commands": runs, "checks": checks, "cases": restored["cases"],
              "scope": "CLEAN_CHECKOUT_AND_NEW_PYTHON_ENVIRONMENT; NOT_A_UNITY_OR_STANDALONE_TEST",
              "note": "Byte hashes may differ with Git line-ending conversion. Configuration contents and numerical outputs are compared semantically."}
    (OUT / "CLEAN_CLONE_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
