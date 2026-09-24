#!/usr/bin/env python3
"""Run the documented P1L5 CURRENT linear-elastic OpenSees basis cases."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import openseespy.opensees as ops


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
OUT = Path(__file__).resolve().parent / "results" / "current"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class UnionFind:
    def __init__(self, tags):
        self.parent = {int(tag): int(tag) for tag in tags}

    def find(self, tag):
        tag = int(tag)
        if self.parent[tag] != tag:
            self.parent[tag] = self.find(self.parent[tag])
        return self.parent[tag]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def section_properties(section: dict) -> tuple[float, float, float, float]:
    dims = section["dimensions"]
    if section["type"] == "beam_rectangular":
        b, h = dims["width_m"], dims["height_m"]
    elif section["type"] == "column_rectangular":
        b, h = dims["width_m"], dims["depth_m"]
    elif section["type"] == "wall_equivalent_rectangular":
        b, h = dims["thickness_m"], dims["length_m"]
    else:
        raise ValueError(f"Unsupported FE section {section['section_id']}")
    area = b * h
    iy = b * h**3 / 12.0
    iz = h * b**3 / 12.0
    a, c = max(b, h), min(b, h)
    torsion_j = a * c**3 * (1.0 / 3.0 - 0.21 * c / a * (1.0 - c**4 / (12.0 * a**4)))
    return area, max(iy, 1e-10), max(iz, 1e-10), max(torsion_j, 1e-10)


def prepare_contract(master: dict, sections: dict, materials: dict, loads: dict) -> dict:
    nodes = master["fe_topology"]["nodes"]
    active = []
    for row in master["elements"]:
        if row["type"] not in {"beam", "column", "wall"} or not row.get("active"):
            continue
        for ref in row.get("analysis_refs", []):
            active.append((row, ref))
    used_nodes = {int(ref[key]) for _, ref in active for key in ("node_i", "node_j")}

    uf = UnionFind(nodes)
    constraints = []
    for constraint in master["fe_topology"]["constraints"]:
        a, b = int(constraint["master_node"]), int(constraint["slave_node"])
        if a in used_nodes and b in used_nodes:
            uf.union(a, b)
            constraints.append(constraint)
    clusters = defaultdict(list)
    for tag in used_nodes:
        clusters[uf.find(tag)].append(tag)
    support_tags = set(master["fe_topology"]["support_node_tags"]) & used_nodes
    cluster_contract = []
    tag_to_retained = {}
    for members in clusters.values():
        supports = sorted(set(members) & support_tags)
        retained = supports[0] if supports else min(members)
        for tag in members:
            tag_to_retained[tag] = retained
        xyz = [[nodes[str(tag)][axis] for axis in "xyz"] for tag in members]
        cluster_contract.append({
            "retained": retained,
            "members": sorted(members),
            "contains_support": bool(supports),
            "extent_m": [round(max(p[i] for p in xyz) - min(p[i] for p in xyz), 6) for i in range(3)],
        })
    retained_supports = sorted({tag_to_retained[tag] for tag in support_tags})

    nodal = {
        case: {int(row["node_tag"]): float(row["Fz_N"]) for row in loads["current_load_application"]["nodal_loads"][case]}
        for case in ("G", "Q")
    }
    # Put loads on retained DOFs so the constraint handler cannot hide them.
    for case in ("G", "Q"):
        aggregated = defaultdict(float)
        for tag, value in nodal[case].items():
            if tag in used_nodes:
                aggregated[tag_to_retained[tag]] += value
        nodal[case] = dict(aggregated)
    # Pseudo-static seismic actions are applied once per building/floor at the
    # closest retained structural node to the floor geometry centroid.  The
    # force magnitude comes from the audited floor weights, not from a visual
    # or evenly distributed approximation.
    group_nodes = defaultdict(set)
    node_groups = defaultdict(list)
    for row, ref in active:
        group = (row["building"], row["floor"])
        for key in ("node_i", "node_j"):
            tag = int(ref[key])
            retained = tag_to_retained[tag]
            group_nodes[group].add(retained)
            node_groups[tag].append(group)
    floor_loads = {(row["building"], row["floor"]): row for row in loads["current_load_application"]["by_floor"]}
    seismic_floor_loads = []
    lateral = defaultdict(float)
    for group, candidates in sorted(group_nodes.items()):
        source = floor_loads.get(group)
        if not source or not candidates:
            continue
        unique_xyz = [nodes[str(tag)] for tag in sorted(candidates)]
        centroid = [sum(point[axis] for point in unique_xyz) / len(unique_xyz) for axis in "xyz"]
        application_tag = min(
            candidates,
            key=lambda tag: sum((nodes[str(tag)][axis] - centroid[i]) ** 2 for i, axis in enumerate("xyz")),
        )
        weight = float(source["G_total_N"]) + 0.5 * float(source["Q_N"])
        force = 0.20 * weight
        lateral[application_tag] += force
        point = nodes[str(application_tag)]
        seismic_floor_loads.append({
            "building": group[0],
            "lt_block": source.get("lt_block"),
            "floor": group[1],
            "G_N": float(source["G_total_N"]),
            "Q_N": float(source["Q_N"]),
            "seismic_weight_N": weight,
            "lateral_force_N": force,
            "target_centroid_m": centroid,
            "application_node": application_tag,
            "application_position_m": [point[axis] for axis in "xyz"],
            "centroid_offset_m": math.hypot(point["x"] - centroid[0], point["y"] - centroid[1]),
            "application_basis": "CLOSEST_RETAINED_NODE_TO_FLOOR_GEOMETRY_CENTROID",
        })

    return {
        "nodes": nodes,
        "active": active,
        "used_nodes": used_nodes,
        "clusters": cluster_contract,
        "tag_to_retained": tag_to_retained,
        "retained_supports": retained_supports,
        "nodal": nodal,
        "lateral": dict(lateral),
        "seismic_floor_loads": seismic_floor_loads,
        "node_groups": node_groups,
        "sections": sections,
        "materials": materials,
    }


def build_model(contract: dict, case: str) -> tuple[dict[int, dict], dict[int, list[float]]]:
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    nodes = contract["nodes"]
    for tag in sorted(contract["used_nodes"]):
        node = nodes[str(tag)]
        ops.node(tag, node["x"], node["y"], node["z"])

    for cluster in contract["clusters"]:
        retained = cluster["retained"]
        for tag in cluster["members"]:
            if tag != retained:
                ops.equalDOF(retained, tag, 1, 2, 3, 4, 5, 6)
    for tag in contract["retained_supports"]:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)

    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    element_meta = {}
    skipped_rigid = []
    for row, ref in contract["active"]:
        ni, nj = int(ref["node_i"]), int(ref["node_j"])
        # A segment whose endpoint DOFs are already tied is redundant in the
        # rigid-joint idealisation; keeping it creates a numerically singular
        # zero-deformation loop.
        if contract["tag_to_retained"][ni] == contract["tag_to_retained"][nj]:
            skipped_rigid.append(ref["analysis_id"])
            continue
        pi, pj = nodes[str(ni)], nodes[str(nj)]
        dx, dy, dz = pj["x"] - pi["x"], pj["y"] - pi["y"], pj["z"] - pi["z"]
        transf = 2 if abs(dz) > math.hypot(dx, dy) else 1
        section = contract["sections"][row["section_id"]]
        material = contract["materials"][row["material_id"]]
        area, iy, iz, j = section_properties(section)
        elastic = material["elastic"]
        e_mod = float(elastic["E_pa"]["value"])
        nu = float(elastic["nu"]["value"])
        g_mod = e_mod / (2.0 * (1.0 + nu))
        tag = int(ref["opensees_tag"])
        ops.element("elasticBeamColumn", tag, ni, nj, area, e_mod, g_mod, j, iy, iz, transf)
        element_meta[tag] = {
            "analysis_id": ref["analysis_id"],
            "element_id": row["element_id"],
            "node_i": ni,
            "node_j": nj,
            "type": row["type"],
            "section_id": row["section_id"],
            "material_id": row["material_id"],
        }

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    external = defaultdict(lambda: [0.0, 0.0, 0.0])
    if case in {"G", "Q"}:
        for tag, fz in contract["nodal"][case].items():
            ops.load(tag, 0.0, 0.0, fz, 0.0, 0.0, 0.0)
            external[tag][2] += fz
    else:
        dof = 0 if case == "EX" else 1
        for tag, force in contract["lateral"].items():
            vector = [0.0, 0.0, 0.0]
            vector[dof] = force
            ops.load(tag, *vector, 0.0, 0.0, 0.0)
            external[tag][dof] += force

    return element_meta, external, skipped_rigid


def run_case(contract: dict, case: str) -> dict:
    element_meta, external, skipped_rigid = build_model(contract, case)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    try:
        ops.system("UmfPack")
    except Exception:
        ops.system("BandGeneral")
    ops.test("NormDispIncr", 1e-10, 20)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    code = ops.analyze(1)
    if code != 0:
        raise RuntimeError(f"OpenSees failed for {case}, code={code}")
    ops.reactions()

    node_results = []
    max_translation = 0.0
    finite = True
    for tag in sorted(contract["used_nodes"]):
        disp = list(ops.nodeDisp(tag))
        finite = finite and all(math.isfinite(value) for value in disp)
        max_translation = max(max_translation, math.sqrt(sum(value * value for value in disp[:3])))
        node = contract["nodes"][str(tag)]
        node_results.append({
            "node_tag": tag,
            "position_m": [node["x"], node["y"], node["z"]],
            "displacement": disp,
        })

    element_results = []
    for tag, meta in sorted(element_meta.items()):
        force = list(ops.eleResponse(tag, "localForce"))
        finite = finite and len(force) >= 12 and all(math.isfinite(value) for value in force)
        if len(force) < 12:
            force = (force + [0.0] * 12)[:12]
        element_results.append(meta | {
            "local_end_forces": {
                "i": {"N": force[0], "Vy": force[1], "Vz": force[2], "T": force[3], "My": force[4], "Mz": force[5]},
                "j": {"N": force[6], "Vy": force[7], "Vz": force[8], "T": force[9], "My": force[10], "Mz": force[11]},
            },
            "representation": "OPENSEES_LOCAL_END_FORCES",
        })

    reaction_sum = [0.0, 0.0, 0.0]
    support_reactions = []
    for tag in contract["retained_supports"]:
        reaction = list(ops.nodeReaction(tag))
        for i in range(3):
            reaction_sum[i] += reaction[i]
        support_reactions.append({"node_tag": tag, "reaction": reaction})
    external_sum = [sum(v[i] for v in external.values()) for i in range(3)]
    residual = [external_sum[i] + reaction_sum[i] for i in range(3)]
    reference = max(1.0, max(abs(x) for x in external_sum + reaction_sum))
    relative_residual = max(abs(x) for x in residual) / reference
    status = "PASS" if finite and relative_residual < 1e-6 and max_translation < 1.0 else "FAIL"
    return {
        "format": "MCOC_P1L5_CURRENT_OPENSEES_CASE_V2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "case_id": case,
        "status": status,
        "result_state": "CURRENT_WITH_DOCUMENTED_FALLBACKS",
        "units": {"length": "m", "force": "N", "moment": "N.m"},
        "model": {
            "active_physical_segments_requested": len(contract["active"]),
            "analysed_segments": len(element_results),
            "redundant_segments_skipped_in_rigid_clusters": skipped_rigid,
            "nodes": len(contract["used_nodes"]),
            "retained_supports": len(contract["retained_supports"]),
            "constraint_clusters": len(contract["clusters"]),
            "assumptions": [
                "Linear elastic 3D academic model.",
                "G35 E=28 GPa and nu=0.2 are authorised P1L5 approximations.",
                "Rigid-arm graph is normalised to one retained node per local cluster.",
                "Seismic force is 0.20*(G+0.5Q) per building/floor at the closest retained node to its geometry centroid.",
                "No unresolved point or line load is silently replaced by zero; those loads remain excluded and explicit in loads.json.",
            ],
        },
        "seismic_floor_loads": contract["seismic_floor_loads"] if case in {"EX", "EY"} else [],
        "qa": {
            "finite": finite,
            "max_translation_m": max_translation,
            "external_force_N": external_sum,
            "reaction_force_N": reaction_sum,
            "equilibrium_residual_N": residual,
            "equilibrium_relative_residual": relative_residual,
            "equilibrium_status": "PASS" if relative_residual < 1e-6 else "FAIL",
        },
        "nodes": node_results,
        "elements": element_results,
        "support_reactions": support_reactions,
    }


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    sections_data = read(CENTRAL / "sections.json")
    materials_data = read(CENTRAL / "materials.json")
    loads = read(CENTRAL / "loads.json")
    sections = {row["section_id"]: row for row in sections_data["sections"]}
    materials = {row["material_id"]: row for row in materials_data["materials"]}
    contract = prepare_contract(master, sections, materials, loads)
    cases = {}
    for case in ("G", "Q", "EX", "EY"):
        result = run_case(contract, case)
        write(OUT / f"{case}.json", result)
        cases[case] = {
            "status": result["status"],
            "max_translation_m": result["qa"]["max_translation_m"],
            "equilibrium_relative_residual": result["qa"]["equilibrium_relative_residual"],
        }
    overall = "PASS" if all(row["status"] == "PASS" for row in cases.values()) else "FAIL"
    manifest = {
        "format": "MCOC_P1L5_CURRENT_RESULTS_MANIFEST_V2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": overall,
        "analysis_version": "P1L5_CURRENT_ZONED_V2",
        "cases": cases,
        "linear_superposition_compatible": overall == "PASS",
        "stop_elements": [],
        "result_state": "CURRENT_WITH_DOCUMENTED_FALLBACKS",
        "load_contract": {
            "status": loads["current_load_application"]["status"],
            "G_total_N": loads["current_load_application"]["totals"]["G_total_N"],
            "Q_total_N": loads["current_load_application"]["totals"]["Q_N"],
            "unresolved_load_ids": loads["current_load_application"]["unresolved_load_ids"],
        },
    }
    write(OUT / "manifest.json", manifest)
    if overall == "PASS":
        master["sources"]["current_contract"].update({
            "status": "CURRENT_VERIFIED",
            "analysis_version": manifest["analysis_version"],
            "results_manifest": "entregas/P1L5/analysis/results/current/manifest.json",
        })
        for row in loads.get("base_cases", []):
            if row.get("case_id") in {"G", "Q", "EX", "EY"}: row["status"] = "CURRENT_READY"
            elif row.get("case_id") == "R": row["status"] = "CURRENT_LINEAR_SUPERPOSITION_READY"
        write(CENTRAL / "model_master.json", master)
        write(CENTRAL / "loads.json", loads)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if overall != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
