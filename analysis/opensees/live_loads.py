"""Uniform project Q on frozen CURRENT tributaries; never rebuild areas here.

The CAD SC catalog remains an immutable reference. Permanent actions are kept;
only the live case is replaced. Structural/tributary changes require a separate
geometry audit, not an implicit regeneration caused by a qQ edit.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENTRAL = ROOT / "model"
CONFIG = ROOT / "config" / "analysis_settings.json"
OUT = ROOT / "results/loads"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def settings():
    config = read(CONFIG)
    q = float(config["live_load"]["intensity_kN_m2"])
    if not math.isfinite(q) or q < 0:
        raise ValueError("qQ must be finite and non-negative, in kN/m2")
    return config


def geometry_signature(master):
    rows = [{k: row.get(k) for k in (
        "element_id", "type", "active", "geometry", "section_id", "material_id", "analysis_refs"
    )} for row in master["elements"]]
    return digest({"elements": rows, "fe_topology": master["fe_topology"]})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def tributary_signature(panels):
    return digest([{k: panel.get(k) for k in ("id", "building", "floor", "geometry", "area_m2")}
                   | {"receivers": [{k: row.get(k) for k in (
                       "element_id", "tributary_area_m2", "equivalent_width_m", "fraction"
                   )} for row in panel["receivers"]]} for panel in panels])


def refresh(loads, master, config):
    """Pure update: caller owns writes. G nodal loads and all area data stay intact."""
    q = float(config["live_load"]["intensity_kN_m2"])
    if not math.isfinite(q) or q < 0:
        raise ValueError("Invalid qQ")
    result = copy.deepcopy(loads)
    app = result["current_load_application"]
    panels = result["tributary_areas"]["panos"]
    if geometry_signature(master) != config["frozen_geometry_sha256"]:
        raise ValueError("Geometry/sections changed: re-audit tributaries before refreshing Q")
    if tributary_signature(panels) != config["frozen_tributaries_sha256"]:
        raise ValueError("Frozen CURRENT tributary areas changed")
    elements = {r["element_id"]: r for r in master["elements"]}
    physical_g = {r["element_id"]: r for r in app["physical_beam_loads"]["G"]}
    nodal = defaultdict(float)
    by_element = defaultdict(float)
    by_floor = defaultdict(float)
    total_area = 0.0
    for panel in panels:
        area = float(panel["area_m2"])
        force = q * 1000.0 * area
        total_area += area
        weights = [float(r["tributary_area_m2"]) for r in panel["receivers"]]
        assigned_area = sum(weights)
        if area <= 0 or assigned_area <= 0 or abs(assigned_area - area) > 1e-4:
            raise ValueError(f"Invalid frozen area distribution: {panel['id']}")
        panel["qQ_kN_m2"] = q
        panel["case_force_N"]["Q"] = force
        panel["live_load_source"] = "PROJECT_ASSUMPTION_UNIFORM_CURRENT"
        by_floor[(panel["building"], panel["floor"])] += force
        for receiver, weight in zip(panel["receivers"], weights):
            rid = receiver["element_id"]
            if rid not in physical_g or not elements[rid].get("active"):
                raise ValueError(f"Missing active tributary receiver: {rid}")
            # Existing rounded areas are normalized ONLY for force conservation.
            # The geometry, A, width and fraction fields are never changed.
            share = force * weight / assigned_area
            receiver["Q_force_N"] = share
            by_element[rid] += share
            for end in ("node_i", "node_j"):
                nodal[int(physical_g[rid][end])] -= share / 2.0
    app["physical_beam_loads"]["Q"] = [
        {"element_id": rid, "node_i": physical_g[rid]["node_i"],
         "node_j": physical_g[rid]["node_j"], "P_N": force, "end_load_N": force / 2,
         "representation": "FROZEN_CURRENT_AREA_TO_EXISTING_FE_END_NODES"}
        for rid, force in sorted(by_element.items())]
    app["nodal_loads"]["Q"] = [{"node_tag": tag, "Fz_N": force} for tag, force in sorted(nodal.items())]
    for row in app["element_loads"]:
        rid = row["element_id"]
        data = row["Q"]
        force = by_element.get(rid, 0.0)
        data["surface_force_N"] = force
        data["average_surface_intensity_kN_m2"] = q if data["tributary_area_m2"] > 0 else 0.0
        data["base_intensity_kN_m2"] = q
        geom = elements[rid]["geometry"]
        length = math.dist(geom["start_m"][:2], geom["end_m"][:2]) if elements[rid]["type"] == "beam" else 0
        data["equivalent_line_load_N_m"] = force / length if length else None
        data["source"] = "PROJECT_ASSUMPTION"
    # Recompute aggregate AFTER every permanent component has been included.
    for row in app["by_floor"]:
        row["Q_N"] = by_floor[(row["building"], row["floor"])]
        row["G_total_N"] = sum(float(row[k]) for k in ("G_self_weight_N", "G_superimposed_N", "G_slab_N"))
        row["area_with_Q_m2"] = row["area_total_m2"] if q > 0 else 0.0
        row["area_without_Q_m2"] = 0.0 if q > 0 else row["area_total_m2"]
    for building, row in app["by_building"].items():
        row["Q_N"] = sum(r["Q_N"] for r in app["by_floor"] if r["building"] == building)
        row["Q_difference_percent"] = 100 * (row["Q_N"] - row["etabs_CV_N"]) / row["etabs_CV_N"]
    app["line_load_applications"] = [r for r in app["line_load_applications"] if r["case"] != "Q"]
    app["totals"]["Q_N"] = q * 1000 * total_area
    transferred = -sum(nodal.values())
    if not math.isclose(transferred, app["totals"]["Q_N"], abs_tol=1e-6, rel_tol=1e-12):
        raise ValueError("Q conservation failed")
    app["conservation"]["Q"] = {"generated_N": app["totals"]["Q_N"], "transferred_N": transferred,
                                "residual_N": transferred-app["totals"]["Q_N"], "status": "PASS"}
    for entry in result["audited_load_catalog"]["entries"]:
        if entry["load_type"].startswith("SC_"):
            entry["current_application"] = {"status": "REFERENCE_ONLY_REPLACED_BY_PROJECT_Q", "applied": False,
                "reason": "Approved uniform project Q replaces all historical SC, including special line/point SC."}
    app["unresolved_load_ids"] = [r["load_id"] for r in result["audited_load_catalog"]["entries"]
                                 if r["current_application"]["status"] == "UNRESOLVED"]
    counts = dict(Counter(r["current_application"]["status"] for r in result["audited_load_catalog"]["entries"]))
    app["catalog_status_counts"] = counts
    result["audited_load_catalog"]["current_status_counts"] = counts
    app["live_load"] = copy.deepcopy(config["live_load"])
    app["seismic_policy"] = copy.deepcopy(config["seismic"])
    app["q_intensity_scale"] = 1.0
    app["generated_utc"] = datetime.now(timezone.utc).isoformat()
    app["basis"] = "FROZEN_CURRENT_TRIBUTARIES_UNIFORM_PROJECT_Q"
    result["generated_utc"] = app["generated_utc"]
    result["sources_week7_config"] = "entregas/P1L5/modelo_central/analysis_settings.json"
    result["tributary_areas"]["coverage_by_floor"] = copy.deepcopy(app["by_floor"])
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def main():
    master = read(CENTRAL / "model_master.json")
    loads = refresh(read(CENTRAL / "loads.json"), master, settings())
    write(CENTRAL / "loads.json", loads)
    app = loads["current_load_application"]
    write(OUT / "current_tributary_loads.json", app)
    write(OUT / "current_tributary_panels.json", loads["tributary_areas"])
    write(OUT / "current_loads_by_element.json", {"format": "MCOC_P1L5_CURRENT_ELEMENT_LOADS_V1",
          "generated_utc": app["generated_utc"], "data_state": "CURRENT_RECOMPUTED", "elements": app["element_loads"]})
    print(json.dumps({"status": "PASS", "qQ_kN_m2": app["live_load"]["intensity_kN_m2"], "totals": app["totals"]}))


if __name__ == "__main__":
    main()
