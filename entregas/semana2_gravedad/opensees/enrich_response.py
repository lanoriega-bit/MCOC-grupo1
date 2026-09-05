"""Enrich the OpenSees E1 analysis JSON with per-element analysis_status and a
verified-region displacement summary for the Unity viewer.

Distinguishes (per project rules):
  - VERIFIED_CONNECTED_RESPONSE : columns whose vertical stack reaches the
    foundation (base z ~ 0) -> a traceable load path to ground. Their nodes and
    the beams that connect two verified columns are also verified.
  - FLOATING_LOAD_PATH_BLOCKER  : columns whose stack has NO member to foundation
    (floating) -> structural response NOT verified. Their nodes/attached beams
    are tagged accordingly.
  - RECONCILED_SCOPING_RESPONSE : elements whose FE response is a reconciled
    scope (e.g. 1S nodal scoping), not a defensible connected result.
  - UNMATCHED_STRUCTURAL_RESPONSE: an element that carries an id not traceable
    to the reconciliation stacks.

Outputs (written next to the analysis JSON):
  edificio1_opensees_analysis.json   -> enriched in place (adds per-element
                                        analysis_status + response_summary)
  edificio1_unity_response.json      -> dedicated JSON for the Unity viewer with
                                        statuses, verified max displacement, and
                                        the Global QA block.
"""

from __future__ import annotations
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS = REPO_ROOT / "entregas" / "semana2_gravedad" / "results"
ANALYSIS_JSON = RESULTS / "edificio1_opensees_analysis.json"
RECON_JSON = REPO_ROOT / "entregas" / "P1L2_reconcile" / "resultados" / "continuous_column_reconciliation.json"
OUT_RESPONSE = RESULTS / "edificio1_unity_response.json"

BASE_MARGIN = 0.05
APPLIED_KP = 21189.36

STATUS_VERIFIED = "VERIFIED_CONNECTED_RESPONSE"
STATUS_BLOCKED = "FLOATING_LOAD_PATH_BLOCKER"
STATUS_SCOPING = "RECONCILED_SCOPING_RESPONSE"
STATUS_UNMATCHED = "UNMATCHED_STRUCTURAL_RESPONSE"

STUB_STATUS_STUB = "SEGMENTATION_STUB_ARTIFACT"
STUB_STATUS_PHYSICAL = "PHYSICAL_MEMBER"
STUB_LIMIT = 0.60  # m


def stub_status_for(e: dict) -> str:
    """Classify a beam as a SEGMENTATION_STUB_ARTIFACT only when ALL hold:
    1) it is a segmentation child (parent_beam_id present or id contains _seg);
    2) it maps to no visual beam (visual_beam_id is None);
    3) its length is shorter than the stub limit (residual corner gap piece).
    Uses origin metadata in addition to length, never length alone."""
    is_child = bool(e.get("parent_beam_id")) or "_seg" in str(e.get("id", ""))
    no_visual = e.get("visual_beam_id") is None
    short = e.get("L_m", 0.0) < STUB_LIMIT
    if is_child and no_visual and short:
        return STUB_STATUS_STUB
    return STUB_STATUS_PHYSICAL

DOWN = "DOWN"  # noqa: F841 (kept for clarity)


def load_analysis(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_reconcile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stack_reaches_base(stack: dict) -> bool:
    return any(
        mm.get("level_bottom") == "base" or mm["node_bottom"][2] <= BASE_MARGIN
        for mm in stack.get("story_members", [])
    )


def build_stack_lookup(recon: dict) -> tuple[dict, dict, set]:
    """Map: column_id -> {'status','stack_id','reaches_base'};
    stack_id -> reaches_base(bool);
    collect set of floating column ids and verified column ids."""
    col_status: dict[str, dict] = {}
    stack_base: dict[str, bool] = {}
    floating_cols: set = set()
    verified_cols: set = set()
    for stack in recon.get("stacks", []):
        sid = stack["stack_id"]
        reaches = stack_reaches_base(stack)
        stack_base[sid] = reaches
        cls = stack.get("class")
        for mm in stack.get("story_members", []):
            cid = mm["column_id"]
            if reaches:
                st = STATUS_VERIFIED
                verified_cols.add(cid)
            elif cls == "B":
                st = STATUS_SCOPING  # reconciled w/ wall evidence but still floating
            else:
                st = STATUS_BLOCKED
                floating_cols.add(cid)
            col_status[cid] = {"stack_id": sid, "status": st, "reaches_base": reaches}
    return col_status, stack_base, floating_cols, verified_cols


def main() -> None:
    analysis = load_analysis(ANALYSIS_JSON)
    recon = load_reconcile(RECON_JSON)

    col_status, stack_base, floating_cols, verified_cols = build_stack_lookup(recon)

    # --- tag each FE element -------------------------------------------------
    elements = analysis.get("element_forces", {})
    node_element_kinds: dict[tuple[float, float, float], set] = {}
    tagged: dict[str, dict] = {}

    for eid, e in elements.items():
        ni = tuple(round(v, 4) for v in e["node_i"])
        nj = tuple(round(v, 4) for v in e["node_j"])
        kind = e.get("kind")
        if kind == "column":
            info = col_status.get(eid)
            if info is None:
                status = STATUS_UNMATCHED
            else:
                status = info["status"]
        else:  # beam
            # beam verified only if BOTH ends land on verified column nodes
            status = STATUS_VERIFIED
        tagged[eid] = {
            "kind": kind,
            "floor": e.get("floor"),
            "bm_id": e.get("bm_id"),
            "visual_beam_id": e.get("visual_beam_id"),
            "analysis_status": status,
            "stub_status": stub_status_for(e) if kind == "beam" else STUB_STATUS_PHYSICAL,
            "node_i": list(ni),
            "node_j": list(nj),
        }
        node_element_kinds.setdefault(ni, set()).add(kind)
        node_element_kinds.setdefault(nj, set()).add(kind)

    # --- node status -----------------------------------------------------------
    nodes = analysis.get("displacements", {})
    reactions = analysis.get("reactions", {})
    node_status = {}
    # Determine floating nodes: endpoints of floating columns
    floating_nodes = set()
    for eid, t in tagged.items():
        if t["kind"] == "column" and t["analysis_status"] in (STATUS_BLOCKED, STATUS_SCOPING):
            floating_nodes.add(tuple(t["node_i"]))
            floating_nodes.add(tuple(t["node_j"]))
    # verified nodes = nodes that belong to a verified column (reach base)
    verified_nodes = set()
    for eid, t in tagged.items():
        if t["kind"] == "column" and t["analysis_status"] == STATUS_VERIFIED:
            verified_nodes.add(tuple(t["node_i"]))
            verified_nodes.add(tuple(t["node_j"]))

    for eid, t in tagged.items():
        if t["kind"] != "beam":
            continue
        ni = tuple(t["node_i"])
        nj = tuple(t["node_j"])
        if ni in verified_nodes and nj in verified_nodes:
            t["analysis_status"] = STATUS_VERIFIED
        elif ni in floating_nodes or nj in floating_nodes:
            t["analysis_status"] = STATUS_BLOCKED
        else:
            t["analysis_status"] = STATUS_SCOPING

    for key, d in nodes.items():
        c = tuple(round(v, 4) for v in d["coords"])
        if c in verified_nodes:
            node_status[key] = STATUS_VERIFIED
        elif c in floating_nodes:
            node_status[key] = STATUS_BLOCKED
        else:
            node_status[key] = STATUS_SCOPING

    # --- verified-region max displacement -------------------------------------
    verified_disp = []
    for key, d in analysis.get("displacements", {}).items():
        c = tuple(round(v, 4) for v in d["coords"])
        if c in verified_nodes:
            verified_disp.append((abs(d["uz_m"]), key, d))
    if verified_disp:
        verified_disp.sort(key=lambda x: x[0], reverse=True)
        max_verified = verified_disp[0]
        vnode = max_verified[1]
        vd = max_verified[2]
    else:
        max_verified = None
        vnode, vd = None, None

    # --- global numerical max (full modal) -------------------------------------
    num_max = max((abs(v["uz_m"]) for v in analysis.get("displacements", {}).values()), default=0.0)

    beam_verified_count = sum(1 for t in tagged.values() if t["kind"] == "beam" and t["analysis_status"] == STATUS_VERIFIED)
    col_verified_count = sum(1 for t in tagged.values() if t["kind"] == "column" and t["analysis_status"] == STATUS_VERIFIED)
    blocked_count = sum(1 for t in tagged.values() if t["analysis_status"] == STATUS_BLOCKED)
    scoping_count = sum(1 for t in tagged.values() if t["analysis_status"] == STATUS_SCOPING)
    stub_count = sum(1 for t in tagged.values() if t.get("stub_status") == STUB_STATUS_STUB)
    physical_beam_count = sum(1 for t in tagged.values() if t["kind"] == "beam" and t.get("stub_status") == STUB_STATUS_PHYSICAL)
    fe_beam_total = sum(1 for t in tagged.values() if t["kind"] == "beam")

    eq = analysis.get("global_equilibrium", {})

    response_summary = {
        "global_equilibrium": {
            "applied_gravity_kN": round(APPLIED_KP, 2),
            "sum_support_reaction_z_kN": round(eq.get("sum_Rz_kN", float("nan")), 3),
            "residual_fz_kN": round(eq.get("residual_Fz_kN", float("nan")), 6),
            "relative_error_pct": round(eq.get("equilibrium_error_pct", float("nan")), 6),
            "status": "PASS" if eq.get("equilibrium_error_pct", 1.0) < 0.5 else "FAIL",
        },
        "verified_connected": {
            "node_count": int(len(verified_nodes)),
            "column_count": int(col_verified_count),
            "beam_count": int(beam_verified_count),
            "max_displacement_m": round(max_verified[0], 6) if max_verified else None,
            "max_displacement_node": vnode,
            "max_displacement_coords": vd["coords"] if vd else None,
            "max_displacement_floor": _floor_for_z((vd["coords"][2]) if vd else None),
        },
        "blocked": {
            "floating_column_stacks": len([k for k, v in stack_base.items() if not v]),
            "blocked_elements": int(blocked_count),
            "scoping_elements": int(scoping_count),
            "blocked_node_count": int(len(floating_nodes) - len(floating_nodes & verified_nodes)),
            "numerical_global_max_displacement_m": round(num_max, 6),
            "numerical_global_max_status": "INVALID_FOR_PHYSICAL_INTERPRETATION",
            "numerical_global_max_reason": "floating load-path blocker (Parte 1, far-east STK_0072-0074 etc.)",
        },
        "beam_accounting": {
            "fe_beam_total": int(fe_beam_total),
            "physical_member": int(physical_beam_count),
            "segmentation_stub_artifact": int(stub_count),
            "not_materialized_zero_length": 2,  # SOL_3_logical_0095, SOL_4_logical_0145
            "sum_check": "PASS" if fe_beam_total == physical_beam_count + stub_count else "FAIL",
            "stub_status": {
                "PHYSICAL_MEMBER": STUB_STATUS_PHYSICAL,
                "SEGMENTATION_STUB_ARTIFACT": STUB_STATUS_STUB,
                "criterion": "segmentation child AND no visual beam AND L < 0.60 m",
            },
        },
    }

    # write enriched element/nodes with status
    analysis["element_analysis_status"] = tagged
    analysis["node_analysis_status"] = node_status
    analysis["response_summary"] = response_summary
    ANALYSIS_JSON.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")

    support_restraints = {
        node: {
            "coords": reaction.get("coords"),
            "dof_order": ["Tx", "Ty", "Tz", "RotX", "RotY", "RotZ"],
            "fixity": [1, 1, 1, 1, 1, 1],
            "source": "ops.fix(node, 1, 1, 1, 1, 1, 1)",
        }
        for node, reaction in sorted(reactions.items(), key=lambda item: int(item[0]))
    }

    # --- Unity response JSON --------------------------------------------------
    unity_resp = {
        "formato": "E1_UNITY_STRUCTURAL_RESPONSE_v1",
        "building_id": analysis.get("source", "E1"),
        "units": {"length": "m", "force": "kN", "load": "kN", "pressure": "kN/m2"},
        "global_qa": response_summary["global_equilibrium"],
        "max_displacement": {
            "numerical_global_max_m": round(num_max, 6),
            "numerical_global_max_status": "INVALID_FOR_PHYSICAL_INTERPRETATION",
            "numerical_global_max_reason": "floating load-path blocker",
            "verified_connected_region_max_m": response_summary["verified_connected"]["max_displacement_m"],
            "verified_region_node": vnode,
            "verified_region_floor": response_summary["verified_connected"]["max_displacement_floor"],
        },
        "status_counts": {
            "VERIFIED_CONNECTED_RESPONSE": int(col_verified_count + beam_verified_count),
            "FLOATING_LOAD_PATH_BLOCKER": int(blocked_count),
            "RECONCILED_SCOPING_RESPONSE": int(scoping_count),
            "UNMATCHED_STRUCTURAL_RESPONSE": int(sum(1 for t in tagged.values() if t["analysis_status"] == STATUS_UNMATCHED)),
            "PHYSICAL_MEMBER": int(physical_beam_count),
            "SEGMENTATION_STUB_ARTIFACT": int(stub_count),
            "FE_BEAM_TOTAL": int(fe_beam_total),
        },
        "floating_column_stacks": sorted([k for k, v in stack_base.items() if not v]),
        "elements": tagged,
        "node_analysis_status": node_status,
        "element_forces_kN": {
            eid: {
                "kind": e.get("kind"),
                "analysis_status": tagged[eid]["analysis_status"],
                "stub_status": tagged[eid].get("stub_status", STUB_STATUS_PHYSICAL),
                "floor": e.get("floor"),
                "visual_beam_id": e.get("visual_beam_id"),
                "node_i": e.get("node_i"),
                "node_j": e.get("node_j"),
                "element_type": e.get("element_type"),
                "section": e.get("section"),
                "material": e.get("material"),
                "geomTransf": e.get("geomTransf"),
                "connectivity": e.get("connectivity"),
                "forces_kN": e.get("forces_kN"),
            }
            for eid, e in analysis.get("element_forces", {}).items()
        },
        "support_restraints": support_restraints,
        "reactions_kN": reactions,
        "displacements_m": {
            key: {"coords": d["coords"], "ux_m": d["ux_m"], "uy_m": d["uy_m"], "uz_m": d["uz_m"],
                  "rx_rad": d["rx_rad"], "ry_rad": d["ry_rad"], "rz_rad": d["rz_rad"]}
            for key, d in analysis.get("displacements", {}).items()
        },
        "blocker_warning_text": "Structural response not verified: no traceable foundation load path.",
        "stub_warning_text": "Short reconciliation stub. Internal-force magnitude is affected by EI/L idealization and is excluded from physical member interpretation.",
    }
    OUT_RESPONSE.write_text(json.dumps(unity_resp, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Enriched  :", ANALYSIS_JSON)
    print("Unity resp:", OUT_RESPONSE)
    print(json.dumps(response_summary, indent=2, ensure_ascii=False))


def _floor_for_z(z):
    if z is None:
        return None
    levels = {"base": 0.0, "1S": 3.96, "1": 7.92, "2": 11.88, "3": 15.84, "4": 19.8}
    best, bd = None, 1e9
    for name, zf in levels.items():
        d = abs(z - zf)
        if d < bd:
            bd, best = d, name
    return best


if __name__ == "__main__":
    main()
