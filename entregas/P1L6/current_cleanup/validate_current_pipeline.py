#!/usr/bin/env python3
"""End-to-end CURRENT identity, physics and Unity JSON checks (no Unity launch)."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from fe_support_graph import unsupported_components


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
ANALYSIS = ROOT / "entregas/P1L5/analysis"
STREAM = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
HERE = Path(__file__).resolve().parent


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    master_path, loads_path = CENTRAL / "model_master.json", CENTRAL / "loads.json"
    master, loads = read(master_path), read(loads_path)
    manifest_path = ANALYSIS / "results/current/manifest.json"
    manifest = read(manifest_path)
    contract = read(STREAM / "current_dataset_contract.json")
    payload_path = STREAM / contract["payload_file"]
    payload = read(payload_path)
    capacity_path = STREAM / "p1l6_current_capacity.json"
    capacity = read(capacity_path)
    viewer_path = STREAM / "model_viewer.json"
    viewer = read(viewer_path)
    active = [r for r in master["elements"] if r.get("active") and r["type"] in {"beam", "column", "wall"}]
    active_ids = {r["element_id"] for r in active}
    cap_ids = [r["element_id"] for r in capacity["elements"]]
    physical_ids = [r["element_id"] for r in master["elements"]]
    viewer_ids = [r["id"] for r in viewer["solids"]]
    basis = {name: read(ANALYSIS / f"results/current/{name}.json") for name in ("G", "Q", "EX", "EY")}
    result_ids = {name: {r["element_id"] for r in case["elements"]} for name, case in basis.items()}
    unsupported = unsupported_components(master)
    checks = {
        "analysis_settings_identity": manifest.get("analysis_settings_sha256") == sha(CENTRAL / "analysis_settings.json") == contract.get("analysis_settings_sha256") == sha(STREAM / "week7_analysis_settings.json"),
        "unique_physical_and_viewer_ids": len(physical_ids) == len(set(physical_ids)) and len(viewer_ids) == len(set(viewer_ids)),
        "unity_geometry_covers_central": set(viewer_ids) == set(physical_ids) | {r["support_id"] for r in master["supports"]},
        "linear_geometry_metadata": all(
            r["geometry"].get("length_m", 0) > 0 and len(r["geometry"].get("direction_unit", [])) == 3
            for r in master["elements"] if r["type"] in {"beam", "wall"}
        ),
        "column_height_metadata": all(r["geometry"].get("height_m", 0) > 0 for r in master["elements"] if r["type"] == "column"),
        "fe_support_reachability": not unsupported and master["fe_topology"]["floating_excluded"]["n_componentes"] == 0,
        "load_conservation": all(loads["current_load_application"]["conservation"][name]["status"] == "PASS" for name in ("G", "Q")),
        "opensees_four_cases": manifest["status"] == "PASS" and all(
            basis[name]["status"] == "PASS" and basis[name]["qa"]["finite"] and
            basis[name]["qa"]["equilibrium_relative_residual"] < 1e-6 for name in basis
        ),
        "result_crosswalk_complete": all(ids == active_ids for ids in result_ids.values()),
        "capacity_crosswalk_complete": set(cap_ids) == active_ids and len(cap_ids) == len(active_ids),
        "capacity_source_identity": capacity["geometry_version"] == sha(master_path) and
            capacity["analysis_manifest_sha256"] == sha(manifest_path) and
            capacity["analysis_version"] == manifest["analysis_version"],
        "unity_contract_verified": contract["status"] == "CURRENT_VERIFIED" and contract["analysis_available"] and
            contract["fe_approved"] and contract["loads_approved"] and contract["linear_verified"],
        "unity_contract_hashes": contract["geometry_version"] == sha(master_path) and
            contract["fe_version"] == hashlib.sha256(json.dumps(master["fe_topology"], sort_keys=True).encode()).hexdigest() and
            contract["geometry_stream_sha256"] == sha(viewer_path) and
            contract["loads_version"] == sha(loads_path) and
            contract["payload_sha256"] == sha(payload_path) and
            contract["current_element_loads_sha256"] == sha(STREAM / contract["current_element_loads_file"]),
        "unity_capacity_artifact_matches_generated": sha(capacity_path) == sha(ANALYSIS / "generated/current_capacity.json"),
        "unity_basis_and_capacity_coefficients": payload["basis_cases"] == ["G", "Q", "EX", "EY"] and
            payload["default_coefficients"] == capacity["default_coefficients"],
    }
    sample_id = "E1-P2-V-041"
    sample = next(r for r in capacity["elements"] if r["element_id"] == sample_id)
    g_rows = [r for r in basis["G"]["elements"] if r["element_id"] == sample_id]
    q_rows = {r["analysis_id"]: r for r in basis["Q"]["elements"] if r["element_id"] == sample_id}
    manual_my = max(abs(g["local_end_forces"][end]["My"] + 0.5 *
                        q_rows[g["analysis_id"]]["local_end_forces"][end]["My"]) / 1000
                    for g in g_rows for end in ("i", "j"))
    checks["manual_R_My_sample"] = math.isclose(manual_my, sample["demand"]["My_kNm"], rel_tol=1e-12)
    issues = [name for name, okay in checks.items() if not okay]
    report = {
        "status": "PASS_WITH_EXPLICIT_NOTES" if not issues else "FAIL",
        "checks": checks, "failures": issues,
        "counts": {"beams": sum(r["type"] == "beam" for r in active),
                   "columns": sum(r["type"] == "column" for r in active),
                   "walls": sum(r["type"] == "wall" for r in active),
                   "slabs": sum(r["type"] == "slab" for r in master["elements"]),
                   "active_structural": len(active),
                   "fe_segments": sum(len(r["analysis_refs"]) for r in active),
                   "unity_solids": len(viewer_ids),
                   "capacity_records": len(cap_ids),
                   "unresolved_loads": len(loads["current_load_application"]["unresolved_load_ids"])},
        "manual_sample": {"element_id": sample_id, "R_My_kNm": manual_my},
        "unsupported_fe_components": unsupported,
        "limitations": [
            "Remaining wall candidates are review-only; see the latest wall-continuity audit, not previous checkpoint counts.",
            f"{sum(r['building'] == 'EDIFICIO_1' and r['floor'] == 'P4' for r in active)} active ED1/P4 structural members retain an explicitly inferred material fallback.",
            "10 non-FE slabs have MAT_UNKNOWN; slab thickness 0.15 m is an academic load fallback.",
            f"{len(loads['current_load_application']['unresolved_load_ids'])} permanent point-load catalog entries lack an unequivocal receiver and remain excluded; historical SC is reference-only under the project-Q policy.",
            f"LT1 Q differs by {loads['current_load_application']['by_building']['EDIFICIO_1']['Q_difference_percent']:+.3f}% from ETABS; benchmark, not a calibration target.",
            "Unity compile/Play requires a separate editor test; this script verifies the JSON contract only.",
        ],
    }
    (HERE / "CURRENT_PIPELINE_QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# CURRENT pipeline QA", "", f"Estado: **{report['status']}**. Verifica identidad geométrica, FE, cargas, OpenSees, capacidad y contrato JSON de Unity; no sustituye la prueba Play.", "", "| Control | Estado |", "| --- | --- |"]
    lines += [f"| {key} | {'PASS' if okay else 'FAIL'} |" for key, okay in checks.items()]
    lines += ["", "## Conteos", "", *[f"- {key}: {value}" for key, value in report["counts"].items()],
              "", f"Control manual `{sample_id}`: R My = {manual_my:.6f} kN·m.", "", "## Notas explícitas", "",
              *[f"- {item}" for item in report["limitations"]], ""]
    (HERE / "CURRENT_PIPELINE_QA.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": report["status"], "failed_checks": issues, "counts": report["counts"]}, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
