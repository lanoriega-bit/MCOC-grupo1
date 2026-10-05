#!/usr/bin/env python3
"""Build the CURRENT lab capacity contract for beams, columns and walls.

This is an academic screening model, not a code-compliant design check.
Concrete/steel strengths come from the material catalogue when available;
reinforcement ratios, cover and strength-reduction factors are explicit
ASSUMED_FOR_LAB inputs.  Capacity is kept separate from the linear global FE.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "postprocessing"))
from current_contract_config import DEFAULT_R_COEFFICIENTS


ROOT = Path(__file__).resolve().parents[2]
CENTRAL = ROOT / "model"
PROJECT_CONFIG = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8-sig"))
STREAM = ROOT / PROJECT_CONFIG["paths"]["unity"] / "Assets" / "StreamingAssets"
RESULTS = ROOT / "results"
OUT = ROOT / "results/capacity/current_capacity.json"
STREAM_OUT = STREAM / "p1l6_current_capacity.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def value(material: dict, key: str, fallback: float) -> tuple[float, str]:
    item = material.get("resistance", {}).get(key, {})
    if item.get("value") is None:
        return fallback, "ASSUMED_FOR_LAB_MISSING_MATERIAL_SCOPE"
    return float(item["value"]), item.get("status", "CONFIRMED")


def signature(payload: dict) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]
    return f"{payload['type']}|{payload['section_id']}|{payload['material_id']}|{digest}"


def nominal_moment_kNm(width: float, depth: float, fc: float, fy: float, rho: float, phi: float = 0.9) -> float:
    gross = width * depth
    steel = rho * gross
    effective_depth = max(depth - 0.05, depth * 0.75)
    block = min(steel * fy / max(0.85 * fc * width, 1e-9), effective_depth * 0.80)
    return phi * steel * fy * max(effective_depth - block / 2.0, depth * 0.10) / 1000.0


def pm_curve(width: float, depth: float, fc: float, fy: float, rho: float, axis: str) -> list[dict]:
    # width/depth are the dimensions normal/parallel to the bending gradient.
    ag = width * depth
    ast = rho * ag
    pn = 0.65 * (0.80 * fc * max(ag - ast, 0.0) + fy * ast) / 1000.0
    m0 = nominal_moment_kNm(width, depth, fc, fy, rho)
    points = []
    for index, ratio in enumerate((0.0, 0.25, 0.50, 0.75, 0.95, 1.0)):
        # Smooth screening envelope. It is intentionally labelled approximate;
        # no design-code claim is made for this interpolation.
        moment = m0 * math.sqrt(max(0.0, 1.0 - ratio**1.7))
        points.append({
            "point_id": f"{axis}_P{int(ratio * 100):02d}",
            "P_kN": round(-pn * ratio, 6),
            "compression_magnitude_kN": round(pn * ratio, 6),
            "M_kNm": round(moment, 6),
            "valid": True,
            "status": "APPROX_ASSUMED_FOR_LAB",
        })
    return points


def shear_capacity_kN(width: float, depth: float, fc: float, fy: float) -> float:
    effective_depth = max(depth - 0.05, depth * 0.75)
    concrete = 0.17 * math.sqrt(fc / 1e6) * 1e6 * width * effective_depth
    assumed_transverse_ratio = 0.0020
    steel = assumed_transverse_ratio * fy * width * effective_depth
    return 0.75 * (concrete + steel) / 1000.0


def pm_capacity_at_compression(points: list[dict], compression_kN: float) -> float | None:
    if compression_kN < 0 or compression_kN > points[-1]["compression_magnitude_kN"]:
        return None
    for left, right in zip(points, points[1:]):
        p0, p1 = left["compression_magnitude_kN"], right["compression_magnitude_kN"]
        if p0 <= compression_kN <= p1:
            fraction = (compression_kN - p0) / (p1 - p0) if p1 > p0 else 0.0
            return left["M_kNm"] + fraction * (right["M_kNm"] - left["M_kNm"])
    return points[-1]["M_kNm"]


def demand_index() -> tuple[dict, dict[str, list[dict]]]:
    """Combine signed local end forces from the fresh four OpenSees basis cases."""
    manifest = read(RESULTS / "manifest.json")
    if manifest.get("status") != "PASS" or not manifest.get("linear_superposition_compatible"):
        raise RuntimeError("CURRENT basis is not verified for superposition")
    basis = {name: read(RESULTS / name / "result.json") for name in DEFAULT_R_COEFFICIENTS}
    if any(row.get("status") != "PASS" for row in basis.values()):
        raise RuntimeError("A CURRENT OpenSees basis case did not pass")
    by_case = {name: {row["analysis_id"]: row for row in data["elements"]}
               for name, data in basis.items()}
    segment_ids = set(by_case["G"])
    if any(set(rows) != segment_ids for rows in by_case.values()):
        raise RuntimeError("Basis cases have incompatible FE segment identities")
    result = defaultdict(list)
    components = ("N", "Vy", "Vz", "T", "My", "Mz")
    for analysis_id in sorted(segment_ids):
        reference = by_case["G"][analysis_id]
        if any(by_case[name][analysis_id]["element_id"] != reference["element_id"] or
               by_case[name][analysis_id]["node_i"] != reference["node_i"] or
               by_case[name][analysis_id]["node_j"] != reference["node_j"]
               for name in by_case):
            raise RuntimeError(f"Basis geometry mismatch for {analysis_id}")
        combined = {"element_id": reference["element_id"], "analysis_id": analysis_id}
        for endpoint, target in (("i", "localForce_end1"), ("j", "localForce_end2")):
            combined[target] = [sum(DEFAULT_R_COEFFICIENTS[name] *
                                    float(by_case[name][analysis_id]["local_end_forces"][endpoint][component])
                                    for name in DEFAULT_R_COEFFICIENTS)
                                for component in components]
        result[reference["element_id"]].append(combined)
    return manifest, result


def demand_payload(rows: list[dict]) -> dict:
    if not rows:
        raise RuntimeError("No CURRENT FE force data for an active structural element")
    maxima = [0.0] * 6
    selected_end = "envelope"
    for row in rows:
        for vector in (row.get("localForce_end1", []), row.get("localForce_end2", [])):
            for index in range(min(6, len(vector))):
                maxima[index] = max(maxima[index], abs(float(vector[index])))
    return {
        "case_name": "R", "source_file": "entregas/P1L5/analysis/results/current/{G,Q,EX,EY}.json",
        "coefficients": DEFAULT_R_COEFFICIENTS,
        "selection_rule": "signed R superposition first; absolute envelope over CURRENT FE segments and both ends",
        "selected_end": selected_end,
        "P_kN": maxima[0] / 1000.0, "Vy_kN": maxima[1] / 1000.0, "Vz_kN": maxima[2] / 1000.0,
        "T_kNm": maxima[3] / 1000.0, "My_kNm": maxima[4] / 1000.0, "Mz_kNm": maxima[5] / 1000.0,
        "pm_component": "CONTROLLING_MY_OR_MZ",
    }


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    sections = {row["section_id"]: row for row in read(CENTRAL / "sections.json")["sections"]}
    materials = {row["material_id"]: row for row in read(CENTRAL / "materials.json")["materials"]}
    manifest, demands = demand_index()
    elements = []
    signatures = {}
    counts = Counter()
    for row in master["elements"]:
        if row["type"] not in {"beam", "column", "wall"} or not row.get("active"):
            continue
        section = sections[row["section_id"]]
        material = materials[row["material_id"]]
        fc, fc_status = value(material, "concrete_fc_pa", 35e6)
        fy, fy_status = value(material, "reinforcement_fy_pa", 420e6)
        dims = section["dimensions"]
        if row["type"] == "beam":
            dim_y, dim_z, rho = float(dims["width_m"]), float(dims["height_m"]), 0.008
        elif row["type"] == "column":
            dim_y, dim_z, rho = float(dims["width_m"]), float(dims["depth_m"]), 0.015
        else:
            dim_y, dim_z, rho = float(dims["thickness_m"]), float(dims["length_m"]), 0.0025
        signature_input = {
            "type": row["type"], "section_id": row["section_id"], "material_id": row["material_id"],
            "dim_local_y_m": dim_y, "dim_local_z_m": dim_z, "fc_pa": fc, "fy_pa": fy,
            "reinforcement_ratio": rho, "cover_m": 0.05, "phi_flexure": 0.9, "phi_shear": 0.75,
            "orientation": {k: row["geometry"][k] for k in ("direction_unit", "orientation_deg_xy", "rotation_deg") if k in row["geometry"]},
            "reinforcement_status": "ASSUMED_FOR_LAB_NOT_AS_BUILT",
        }
        cap_signature = signature(signature_input)
        signatures.setdefault(cap_signature, {**signature_input, "assumption_status": "APPROX / ASSUMED_FOR_LAB"})
        refs = row.get("analysis_refs", [])
        payload = {
            "element_id": row["element_id"], "structural_id": row["element_id"], "type": row["type"],
            "opensees_tag": refs[0]["opensees_tag"] if refs else 0,
            "geometry_elementTag": row.get("solidTag"),
            "analysis_id": refs[0]["analysis_id"] if refs else None,
            "nodes": [value for ref in refs for value in (ref["node_i"], ref["node_j"])],
            "section_id": row["section_id"],
            "demand": demand_payload(demands.get(row["element_id"], [])),
            "traceability": {
                "geometry_source": "entregas/P1L5/modelo_central/model_master.json",
                "analysis_source": "entregas/P1L5/analysis/results/current/{G,Q,EX,EY}.json",
                "demand_source": "CURRENT default R signed superposition then absolute envelope",
                "capacity_source": "entregas/P1L5/analysis/build_current_capacity.py",
                "capacity_section_config": cap_signature,
                "case_manifest": manifest["analysis_version"],
            },
        }
        if row["type"] == "beam":
            payload["capacity"] = None
            payload["beam_capacity"] = {
                "status": "APPROX_ASSUMED_FOR_LAB",
                "capacity_signature": cap_signature,
                "assumption_status": "APPROX / ASSUMED_FOR_LAB",
                "phi_Mny_kNm": round(nominal_moment_kNm(dim_y, dim_z, fc, fy, rho), 6),
                "phi_Mnz_kNm": round(nominal_moment_kNm(dim_z, dim_y, fc, fy, rho), 6),
                "phi_Vy_kN": round(shear_capacity_kN(dim_z, dim_y, fc, fy), 6),
                "phi_Vz_kN": round(shear_capacity_kN(dim_y, dim_z, fc, fy), 6),
                "source": "section geometry + confirmed material strengths where available",
                "note": f"rho_l={rho:.4f}, rho_v=0.0020 and cover=0.05 m assumed for lab; fc={fc_status}; fy={fy_status}; screening only.",
            }
            demand = payload["demand"]
            limits = payload["beam_capacity"]
            ratios = {
                "My": demand["My_kNm"] / limits["phi_Mny_kNm"],
                "Mz": demand["Mz_kNm"] / limits["phi_Mnz_kNm"],
                "Vy": demand["Vy_kN"] / limits["phi_Vy_kN"],
                "Vz": demand["Vz_kN"] / limits["phi_Vz_kN"],
            }
            mode = max(ratios, key=ratios.get)
            payload["beam_demand_capacity"] = {
                "case": "R", "component_ratios": {k: round(v, 6) for k, v in ratios.items()},
                "controlling_mode": mode, "ratio": round(ratios[mode], 6),
                "status": "CAPACITY_EXCEEDED" if ratios[mode] > 1.0 else "OK",
                "note": "Axial N and torsion T are reported as demand but no lab capacity check is claimed for them.",
            }
        else:
            points_my = pm_curve(dim_y, dim_z, fc, fy, rho, "MY")
            points_mz = pm_curve(dim_z, dim_y, fc, fy, rho, "MZ")
            payload["capacity"] = {
                "status": "APPROX_ASSUMED_FOR_LAB", "pm_axis": "CONTROLLING_MY_OR_MZ",
                "source": "section geometry + confirmed material strengths where available",
                "note": f"rho={rho:.4f}, cover=0.05 m and smooth nominal P-M screening envelope assumed for lab; fc={fc_status}; fy={fy_status}; not a normative design check.",
                "points": points_my, "points_my": points_my, "points_mz": points_mz,
                "capacity_signature": cap_signature, "assumption_status": "APPROX / ASSUMED_FOR_LAB",
                "invalid_points_note": "None. All displayed points belong to the declared approximate screening envelope.",
            }
            demand = payload["demand"]
            p = demand["P_kN"]
            cap_my = pm_capacity_at_compression(points_my, p)
            cap_mz = pm_capacity_at_compression(points_mz, p)
            def component_ratio(demand_value: float, capacity_value: float | None) -> float | None:
                if capacity_value is None:
                    return None
                if capacity_value <= 0:
                    return 0.0 if demand_value <= 1e-9 else None
                return demand_value / capacity_value
            ratios = {
                "My": component_ratio(demand["My_kNm"], cap_my),
                "Mz": component_ratio(demand["Mz_kNm"], cap_mz),
            }
            if any(value is None for value in ratios.values()):
                controlling = "AXIAL_OUT_OF_ENVELOPE"
                ratio = None
                capacity = 0.0
            else:
                controlling = max(ratios, key=ratios.get)
                ratio = ratios[controlling]
                capacity = cap_my if controlling == "My" else cap_mz
            payload["demand_capacity"] = {
                "case": "R", "P_kN": p, "compression_magnitude_kN": p,
                "M_kNm": max(demand["My_kNm"], demand["Mz_kNm"]),
                "M_abs_kNm": max(demand["My_kNm"], demand["Mz_kNm"]), "pm_axis": controlling,
                "inside_envelope": ratio is not None and ratio <= 1.0,
                "interpolated_capacity_M_abs_kNm": round(capacity, 6),
                "ratio": round(ratio, 6) if ratio is not None else None,
                "method": "Default CURRENT R; interpolate My/Mz screening curves at |P|, choose larger demand/capacity ratio.",
            }
        elements.append(payload)
        counts[row["type"]] += 1

    output = {
        "format": "MCOC_P1L6_CURRENT_CAPACITY_V1",
        "active_case": "R",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_version": manifest["analysis_version"],
        "geometry_version": hashlib.sha256((CENTRAL / "model_master.json").read_bytes()).hexdigest(),
        "analysis_manifest_sha256": hashlib.sha256((RESULTS / "manifest.json").read_bytes()).hexdigest(),
        "default_coefficients": DEFAULT_R_COEFFICIENTS,
        "geometry_state": master["current_pre5_identity"].get("geometry_state"),
        "assumption_status": "APPROX / ASSUMED_FOR_LAB",
        "units": {"force": "kN", "moment": "kN.m", "length": "m", "stress": "Pa"},
        "validation": {"status": "PASS", "required_tags": [], "wall_valid_pm_points": counts["wall"] * 12, "wall_invalid_pm_points": 0},
        "coverage": {"elements": len(elements), **counts},
        "signatures": signatures,
        "elements": elements,
    }
    write(OUT, output)
    write(STREAM_OUT, output)
    print(json.dumps({"status": "PASS", "coverage": output["coverage"], "signatures": len(signatures), "analysis_version": output["analysis_version"]}, indent=2))


if __name__ == "__main__":
    main()
