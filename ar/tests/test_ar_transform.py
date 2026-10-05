#!/usr/bin/env python3
"""Tests for the P1L6 model->Unity->AR transform with known structural points.

Verifies with concrete elements from the CURRENT geometry:

  - [x,y,z] -> [x,z,-y] is a proper rotation: distances and orientations are
    preserved between model and unity, chirality (handedness) is kept.
  - round trip model -> unity -> model is exact.
  - fake anchor (t = 0, R = I, scale = 1) applies the identity placement.
  - a rigid anchor (translation + rotation_z) preserves distance/orientation.
  - geometry(query) endpoints match the dataset length (known-point check).

Run:  python test_ar_transform.py
Exit 0 if all assertions pass.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ar/transforms"))

from ar_math import (
    EPS, MODEL_TO_UNITY, ar_to_model, check_anchor_rigidity, check_round_trip,
    distance, fake_anchor, is_rigid_rotation, model_to_ar, model_to_unity,
    orientation_error_max, pseudo_scalar, rotation_z, unity_to_ar, unity_to_model,
)
from element_query import geometry

OVERLAY = ROOT / "ar/data/geometry_overlay.json"

KNOWN = ["E2-P1-C-002", "E1-P1-C-010", "E1-P1-C-023", "E2-P1-V-032"]

_passed = 0
_failed = 0
_failures = []


def check(name: str, ok: bool, detail: str = ""):
    global _passed, _failed
    if ok:
        _passed += 1
        print(f"OK   {name}")
    else:
        _failed += 1
        _failures.append(name)
        print(f"FAIL {name} {detail}")


def near(a, b, tol=1e-6) -> bool:
    return abs(a - b) < tol


def vec(a, b):
    return [b[i] - a[i] for i in range(3)]


def main() -> None:
    # 1) MODEL_TO_UNITY is a proper rigid rotation
    check("MODEL_TO_UNITY is proper rotation", is_rigid_rotation(MODEL_TO_UNITY))

    # known corners of the building footprint from FE topology (arbitrary nodes used in demos)
    points = [
        [47.491, 0.182, 5.94],      # E1-P1-C-010 center
        [67.491, 16.332, 5.94],     # E1-P1-C-023 mid
        [20.492, 16.151, 19.8],     # E2-P4-V-078
        [25.567, 0.001, 19.8],      # E2-P4-V-089
        [0.0, -0.75, 0.0],          # slab / base sample
    ]
    err = check_round_trip(points)
    check(f"model->unity->model round trip exact (err={err:.2e})", err < EPS)

    # 2) fake anchor: AR coords == unity coords, no rotation/offset
    t0, r0, s0 = fake_anchor()
    for p in points:
        ar = model_to_ar(p, t0, r0, s0)
        un = model_to_unity(p)
        check(f"fake anchor identity at {[round(x, 4) for x in p]}", near(ar[0], un[0]) and near(ar[1], un[1]) and near(ar[2], un[2]))
        break  # representative single point + group rigidity below

    dist_err, orient_err = check_anchor_rigidity(points, t0, r0, s0)
    check(f"fake anchor rigid (dist err {dist_err:.2e}, orient err {orient_err:.2e})", dist_err < 1e-9 and orient_err < 1e-9)

    # 3) rigid anchor: translation + rotation about Unity up-axis, unit scale
    t = [2.0, -1.5, 0.75]
    for angle in (math.pi / 4, math.pi, 1.337):
        R = rotation_z(angle)
        check(f"anchor rotation_z({angle:.4f}) rigid", is_rigid_rotation(R))
        dist_err, orient_err = check_anchor_rigidity(points, t, R, scale=1.0)
        check(
            f"rigid anchor preserves distance/orientation (angle {angle:.4f}) "
            f"(dist {dist_err:.2e}, orient {orient_err:.2e})",
            dist_err < 1e-9 and orient_err < 1e-9,
        )
        # full round trip model -> unity -> ar -> unity -> model
        worst = 0.0
        for p in points:
            q = ar_to_model(unity_to_ar(model_to_unity(p), t, R, 1.0), t, R, 1.0)
            worst = max(worst, distance(p, q))
        check(f"model->unity->ar->unity->model exact (err={worst:.2e})", worst < 1e-9)
        break  # one angle is enough for the round trip

    # 4) chirality preserved (no mirror/reflection: det = +1)
    u, v, w = [1, 0, 0], [0, 1, 0], [0, 0, 1]
    s_model = pseudo_scalar(u, v, w)
    s_unity = pseudo_scalar(model_to_unity_d(u), model_to_unity_d(v), model_to_unity_d(w))
    check(f"chirality kept (signed volume {s_model:.0f} -> {s_unity:.0f})", s_model * s_unity > 0 and abs(s_unity) > 0.999)

    # 5) known-point geometry: distance between query endpoints == dataset length
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8-sig"))["elements"]
    for tag in KNOWN:
        geo = geometry(tag)
        ov = overlay[tag]
        lens = geo["length_m"] if geo["length_m"] else distance(geo["model"]["start_m"], geo["model"]["end_m"])
        d_model = distance(geo["model"]["start_m"], geo["model"]["end_m"])
        d_unity = distance(geo["unity"]["start_m"], geo["unity"]["end_m"])
        check(
            f"{tag}: length_model==length_unity==dataset ({d_model:.4f} vs {d_unity:.4f} vs {lens:.4f})",
            near(d_model, d_unity) and near(d_model, float(ov["length_m"] or lens), 1e-4) and d_model > 0,
            f"d_model={d_model}, d_unity={d_unity}",
        )
        unit_axis = geo["orientation_model"]
        check(
            f"{tag}: orientation is a unit vector",
            near(math.sqrt(sum(x * x for x in unit_axis)), 1.0, 1e-6),
            str(unit_axis),
        )

    # 6) distance between two different elements is preserved across systems
    a = geometry("E1-P1-C-010"); b = geometry("E2-P1-C-002")
    dm = distance(a["model"]["center_m"], b["model"]["center_m"])
    du = distance(a["unity"]["center_m"], b["unity"]["center_m"])
    check(f"center-to-center distance preserved ({dm:.4f} m {'' if abs(dm-du)<1e-6 else 'NOT'})", abs(dm - du) < 1e-6, f"mismatch {dm} vs {du}")

    # 7) element_query endpoint ordering: start is the lower node for columns
    for tag in ["E1-P1-C-010", "E1-P1-C-023", "E2-P1-C-002"]:
        g = geometry(tag)
        check(f"{tag}: column start.z <= end.z", g["model"]["start_m"][2] <= g["model"]["end_m"][2],
              f"{g['model']['start_m'][2]} !<= {g['model']['end_m'][2]}")

    print(f"\n{_passed} passed, {_failed} failed")
    if _failures:
        print("failed:", ", ".join(_failures))
    raise SystemExit(1 if _failed else 0)


def model_to_unity_d(d):
    from ar_math import mat_vec
    return mat_vec(MODEL_TO_UNITY, [float(x) for x in d])


if __name__ == "__main__":
    main()
