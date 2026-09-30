#!/usr/bin/env python3
"""elementTag -> geometry -> OpenSees result, through the canonical transform.

Reusable query service for the P1L6 AR bridge:

    elementTag
      -> identity (element_id, solidTag, opensees tags, building, floor)
      -> geometry (start/end/center in model, unity and anchor-local AR)
      -> nodes + positions
      -> section, material
      -> result (R envelope forces P/V/T/My/Mz and node displacements)

Output mirrors the example contract:

    E1-P1-C-010 -> nodos -> posicion -> seccion -> P -> M -> desplazamiento

Run:
    python element_query.py E1-P1-C-010
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from ar_math import (fake_anchor, identity, model_to_unity, unity_to_ar, unity_to_model)

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "entregas" / "P1L6" / "preparation" / "current_ar_elements.json"
OVERLAY = ROOT / "entregas" / "P1L6" / "transform" / "current_ar_geometry_overlay.json"
CAPACITY = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "p1l6_current_capacity.json"

_raw = None
_overlay = None
_cap_by_id = None


def _load():
    global _raw, _overlay, _cap_by_id
    if _raw is None:
        _raw = json.loads(DATASET.read_text(encoding="utf-8-sig"))
    if _overlay is None and OVERLAY.exists():
        _overlay = json.loads(OVERLAY.read_text(encoding="utf-8-sig"))["elements"]
    if _cap_by_id is None and CAPACITY.exists():
        cap = json.loads(CAPACITY.read_text(encoding="utf-8-sig"))
        _cap_by_id = {row["element_id"]: row for row in cap.get("elements", [])} if isinstance(cap, dict) else {}
    return _raw, _overlay, _cap_by_id


def find(tag: str) -> dict:
    raw, _, _ = _load()
    for rec in raw["elements"]:
        if rec["element_id"] == tag or rec.get("elementTag") == tag:
            return rec
    raise KeyError(f"elementTag no existe en el dataset AR: {tag}")


def geometry(tag: str, anchor=None):
    """Start/end/center in model, unity and anchor-local coordinates."""
    rec = find(tag)
    raw, overlay, _ = _load()
    t, r, s = anchor if anchor is not None else fake_anchor()

    start_m = end_m = center_m = None
    ov = overlay.get(tag)
    if ov:
        start_m, end_m = ov["start_m"], ov["end_m"]
        center_m = ov.get("center_m", rec.get("model_coordinates_m", {}).get("center"))
    if start_m is None:
        start_m = rec.get("model_coordinates_m", {}).get("start")
    if end_m is None:
        end_m = rec.get("model_coordinates_m", {}).get("end")
    if center_m is None:
        center_m = rec.get("model_coordinates_m", {}).get("center")

    def to_unity(p):
        return model_to_unity(p) if p else None

    def to_ar(p):
        return unity_to_ar(to_unity(p), t, r, s) if p else None

    orient = ov["orientation_model"] if ov else (rec.get("orientation_model") or [0.0, 0.0, 1.0])
    orient_u = ov["orientation_unity"] if ov else (rec.get("orientation_unity") or [0.0, 1.0, 0.0])

    return {
        "tag": tag,
        "model": {"start_m": start_m, "end_m": end_m, "center_m": center_m},
        "unity": {"start_m": to_unity(start_m), "end_m": to_unity(end_m), "center_m": to_unity(center_m)},
        "ar": {
            "start_m": to_ar(start_m), "end_m": to_ar(end_m), "center_m": to_ar(center_m),
            "anchor_pose": {"t_m": list(t), "scale": s},
        },
        "orientation_model": orient,
        "orientation_unity": orient_u,
        "length_m": ov.get("length_m", rec.get("length_m")) if ov else rec.get("length_m"),
        "source": ov.get("source", "dataset") if ov else "dataset",
    }


def result(tag: str):
    """R envelope for the element: axial P, shear V, torsion T, moments My/Mz,
    and node displacements. Derived from the CURRENT basis combination on the
    phone side (never recalculated from scratch)."""
    rec = find(tag)
    r = rec.get("current_result_R", {})
    segments = r.get("segments", [])
    coeff = r.get("coefficients", {})

    N = Vy = Vz = T = My = Mz = 0.0
    seg_out = []
    for seg in segments:
        e1, e2 = seg["localForce_end1_N_Nm"], seg["localForce_end2_N_Nm"]
        for f in (e1, e2):
            N = max(N, abs(f[0]))
            Vy = max(Vy, abs(f[1]))
            Vz = max(Vz, abs(f[2]))
            T = max(T, abs(f[3]))
            My = max(My, abs(f[4]))
            Mz = max(Mz, abs(f[5]))
        seg_out.append({
            "analysis_id": seg["analysis_id"], "opensees_tag": seg["opensees_tag"],
            "node_i": seg["node_i"], "node_j": seg["node_j"],
        })

    disp_rows = []
    max_disp = 0.0
    for row in r.get("node_displacements", []):
        mag = row.get("magnitude_m", 0.0)
        max_disp = max(max_disp, mag)
        disp_rows.append({
            "node_tag": row["node_tag"],
            "model_coord_m": row.get("model_coord_m"),
            "unity_coord_m": row.get("unity_coord_m"),
            "displacement_model_m": row.get("displacement_model_m"),
            "magnitude_m": round(mag, 9),
        })

    return {
        "case": "R",
        "coefficients": coeff,
        "segments": seg_out,
        "envelope": {
            "P_kN": round(N / 1e3, 4), "V_kN": round(max(Vy, Vz) / 1e3, 4),
            "My_kNm": round(My / 1e3, 4), "Mz_kNm": round(Mz / 1e3, 4),
            "T_kNm": round(T / 1e3, 4),
        },
        "displacements": disp_rows,
        "max_displacement_mm": round(max_disp * 1e3, 4),
    }


def capacity(tag: str):
    _raw, _overlay, _cap_by_id = _load()
    c = (_cap_by_id or {}).get(tag)
    if not c:
        rec = find(tag)
        return {"available": False, "note": rec.get("data_state", "NO_CAPACITY")}
    dc = c.get("demand_capacity", {})
    pm = c.get("capacity") or {}
    beam = c.get("beam_capacity") or {}
    return {
        "available": True,
        "status": pm.get("status") or beam.get("status"),
        "dc_ratio": dc.get("DC_ratio"),
        "inside_envelope": dc.get("inside_envelope"),
        "pm_axis": pm.get("pm_axis"),
    }


def query(tag: str, anchor=None, verbose: bool = True) -> dict:
    rec = find(tag)
    geo = geometry(tag, anchor)
    res = result(tag)
    identity_block = {
        "elementTag": rec["elementTag"],
        "element_id": rec["element_id"],
        "future_ar_elementTag": rec.get("future_ar_elementTag"),
        "solidTag": rec.get("solidTag"),
        "opensees_tags": rec.get("opensees_tags"),
        "type": rec.get("type"), "building": rec.get("building"), "floor": rec.get("floor"),
        "physical_nodes": rec.get("physical_nodes"), "fe_node_tags": rec.get("fe_node_tags"),
        "data_state": rec.get("data_state"),
    }
    out = {
        "identity": identity_block,
        "geometry": geo,
        "nodes": [
            {"node_tag": d["node_tag"], "model_coord_m": d["model_coord_m"],
             "unity_coord_m": d["unity_coord_m"]}
            for d in res["displacements"]
        ],
        "section": rec.get("section", {}).get("section_id") if rec.get("section") else None,
        "material": rec.get("material", {}).get("material_id") if rec.get("material") else None,
        "length_m": geo["length_m"],
        "result_R": res,
        "capacity": capacity(tag),
        "anchor_pose": {"t_m": list(geo["ar"]["anchor_pose"]["t_m"]),
                        "rotation_z_rad": 0.0, "scale": geo["ar"]["anchor_pose"]["scale"]},
    }
    if verbose:
        print(_human(out))
    return out


def _human(o: dict) -> str:
    id_ = o["identity"]
    g = o["geometry"]
    e = o["result_R"]["envelope"]
    lines = [
        f"elementTag           : {o['identity']['elementTag']}",
        f"element_id           : {id_['element_id']}   solidTag={id_['solidTag']}",
        f"opensees_tags        : {id_['opensees_tags']}   type={id_['type']} {id_['building']}/{id_['floor']}",
        f"physical_nodes       : {id_['physical_nodes']}   fe_node_tags={id_['fe_node_tags']}",
        f"longitud             : {o['length_m']} m   estado={id_['data_state']}",
        f"seccion              : {o['section']}   material={o['material']}",
    ]
    for space, key in (("model", "start_m"), ("unity", "start_m"), ("ar", "start_m")):
        lines.append(f"  {space:6s} start = {[round(x,4) for x in g[space][key]] if g[space][key] else None}")
    for space, key in (("model", "center_m"), ("unity", "center_m"), ("ar", "center_m")):
        lines.append(f"  {space:6s} center= {[round(x,4) for x in g[space][key]] if g[space][key] else None}")
    lines.append(f"orientacion_model    : {[round(x,4) for x in g['orientation_model']]}")
    lines.append("resultado R (envolvente):")
    lines.append(f"  P = {e['P_kN']:>10.2f} kN   V = {e['V_kN']:>8.2f} kN   T = {e['T_kNm']:>8.2f} kN.m")
    lines.append(f"  My= {e['My_kNm']:>10.2f} kN.m   Mz = {e['Mz_kNm']:>8.2f} kN.m")
    lines.append(f"  desplazamiento max = {o['result_R']['max_displacement_mm']:.4f} mm")
    cap = o.get("capacity") or {}
    lines.append(f"capacidad            : disponible={cap.get('available')} status={cap.get('status')} "
                 f"DC={cap.get('dc_ratio')} dentro={cap.get('inside_envelope')}")
    return "\n".join(lines)


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "E1-P1-C-010"
    query(tag)
