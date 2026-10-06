"""Pure rigid-transformation math for the P1L6 AR bridge.

Canonical maps (documented in entregas/P1L6/AR_TRANSFORM_CONTRACT.md):

    model -> unity :  [x, y, z] -> [x, z, -y]      (root Rx = -90deg in Unity viewer)
    unity -> model :  [X, Y, Z] -> [X, -Z, Y]      (inverse, same rotation)
    unity -> ar    :  p_ar = R_anchor * (s * p_unity) + t_anchor
    ar    -> unity :  p_unity = R_anchor^T * (p_ar - t_anchor) / s

Units are SI throughout: m, N, N.m, Pa, rad.
All routines are dependency-free (math only) so tests run without Unity or numpy.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

EPS = 1e-9


# ---------------------------------------------------------------------------
# Linear algebra helpers (3x3 matrices as tuples of tuples).
# ---------------------------------------------------------------------------

def mat_vec(m: Sequence[Sequence[float]], v: Sequence[float]) -> list[float]:
    return [m[r][0] * v[0] + m[r][1] * v[1] + m[r][2] * v[2] for r in range(3)]


def mat_mult(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    return [
        [sum(a[r][k] * b[k][c] for k in range(3)) for c in range(3)]
        for r in range(3)
    ]


def transpose(m: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[m[r][c] for r in range(3)] for c in range(3)]


def identity() -> list[list[float]]:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def rotation_z(rad: float) -> list[list[float]]:
    c, s = math.cos(rad), math.sin(rad)
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def rotation_x(rad: float) -> list[list[float]]:
    c, s = math.cos(rad), math.sin(rad)
    return [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]]


# ---------------------------------------------------------------------------
# Canonical model <-> Unity map (a proper rotation, det = +1).
# ---------------------------------------------------------------------------

MODEL_TO_UNITY = [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]]
UNITY_TO_MODEL = transpose(MODEL_TO_UNITY)


def model_to_unity(p: Sequence[float]) -> list[float]:
    return mat_vec(MODEL_TO_UNITY, [float(p[0]), float(p[1]), float(p[2])])


def unity_to_model(p: Sequence[float]) -> list[float]:
    return mat_vec(UNITY_TO_MODEL, [float(p[0]), float(p[1]), float(p[2])])


# ---------------------------------------------------------------------------
# Anchor (AR) placement.
# ---------------------------------------------------------------------------

def unity_to_ar(
    p_unity: Sequence[float],
    t_anchor: Sequence[float],
    r_anchor: Sequence[Sequence[float]],
    scale: float = 1.0,
) -> list[float]:
    """p_ar = R_anchor * (scale * p_unity) + t_anchor."""
    return [r_anchor[r][0] * (scale * p_unity[0])
            + r_anchor[r][1] * (scale * p_unity[1])
            + r_anchor[r][2] * (scale * p_unity[2])
            + t_anchor[r] for r in range(3)]


def ar_to_unity(
    p_ar: Sequence[float],
    t_anchor: Sequence[float],
    r_anchor: Sequence[Sequence[float]],
    scale: float = 1.0,
) -> list[float]:
    """Inverse of unity_to_ar (anchor assumed rigid, scale > 0 optional)."""
    r_inv = transpose(r_anchor)
    shifted = [p_ar[i] - t_anchor[i] for i in range(3)]
    s = scale if scale else 1.0
    return [mat_vec(r_inv, shifted)[i] / s for i in range(3)]


def model_to_ar(
    p_model: Sequence[float],
    t_anchor: Sequence[float] = (0.0, 0.0, 0.0),
    r_anchor: Sequence[Sequence[float]] | None = None,
    scale: float = 1.0,
) -> list[float]:
    """Full chain model -> Unity -> anchor-local AR coordinates."""
    r_anchor = r_anchor if r_anchor is not None else identity()
    return unity_to_ar(model_to_unity(p_model), t_anchor, r_anchor, scale)


def ar_to_model(
    p_ar: Sequence[float],
    t_anchor: Sequence[float] = (0.0, 0.0, 0.0),
    r_anchor: Sequence[Sequence[float]] | None = None,
    scale: float = 1.0,
) -> list[float]:
    r_anchor = r_anchor if r_anchor is not None else identity()
    return unity_to_model(ar_to_unity(p_ar, t_anchor, r_anchor, scale))


# ---------------------------------------------------------------------------
# Rigid invariants (distances / orientations / handedness).
# ---------------------------------------------------------------------------

def distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.dist([float(x) for x in a], [float(x) for x in b])


def length(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def normalize(v: Sequence[float]) -> list[float]:
    n = length(v)
    if n == 0.0:
        return [0.0, 0.0, 0.0]
    return [float(x) / n for x in v]


def is_rigid_rotation(m: Sequence[Sequence[float]], rel_tol: float = 1e-9) -> bool:
    """True if m is an orthonormal proper rotation (R^T R = I, det = +1)."""
    eye = identity()
    mt = mat_mult(m, transpose(m))
    det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
           - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
           + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return all(abs(mt[r][c] - eye[r][c]) < rel_tol for r in range(3) for c in range(3)) and abs(det - 1.0) < rel_tol


def distance_error_max(
    pairs_a: Sequence[tuple[Sequence[float], Sequence[float]]],
    pairs_b: Sequence[tuple[Sequence[float], Sequence[float]]],
) -> float:
    """Max relative distance error between the same point-pairs mapped by A and B."""
    assert len(pairs_a) == len(pairs_b)
    worst = 0.0
    for (a1, a2), (b1, b2) in zip(pairs_a, pairs_b):
        d_a = distance(a1, a2)
        d_b = distance(b1, b2)
        base = max(d_a, d_b, 1e-12)
        worst = max(worst, abs(d_a - d_b) / base)
    return worst


def orientation_error_max(
    directions_a: Sequence[Sequence[float]],
    directions_b: Sequence[Sequence[float]],
) -> float:
    """Max angular error (rad) between direction vectors mapped by two systems."""
    worst = 0.0
    for da, db in zip(directions_a, directions_b):
        na, nb = normalize(da), normalize(db)
        dot = min(1.0, max(-1.0, sum(na[i] * nb[i] for i in range(3))))
        worst = max(worst, math.acos(dot))
    return worst


def vec_sub(a: Sequence[float], b: Sequence[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def angle_between(a: Sequence[float], b: Sequence[float]) -> float:
    na, nb = normalize(a), normalize(b)
    dot = min(1.0, max(-1.0, sum(na[i] * nb[i] for i in range(3))))
    return math.acos(dot)


def pseudo_scalar(u: Sequence[float], v: Sequence[float], w: Sequence[float]) -> float:
    """Triple product (u x v) . w : +1/-1 preserves chirality of a rigid rotation."""
    return (u[1] * v[2] - u[2] * v[1]) * w[0] \
        + (u[2] * v[0] - u[0] * v[2]) * w[1] \
        + (u[0] * v[1] - u[1] * v[0]) * w[2]


def model_to_unity_direction(d_model: Sequence[float]) -> list[float]:
    """Direction vectors transform with the same rotation (no translation part)."""
    return mat_vec(MODEL_TO_UNITY, [float(x) for x in d_model])


# ---------------------------------------------------------------------------
# Round-trip and invariant self-checks (used by tests).
# ---------------------------------------------------------------------------

def check_round_trip(points: Iterable[Sequence[float]], atol: float = 1e-6) -> float:
    """Max |model -> unity -> model error| over points."""
    worst = 0.0
    for p in points:
        q = ar_to_model(model_to_unity(p), t_anchor=(0.0, 0.0, 0.0), r_anchor=identity(), scale=1.0)
        worst = max(worst, distance(p, q))
    return worst


def check_anchor_rigidity(
    points: Iterable[Sequence[float]],
    t_anchor: Sequence[float],
    r_anchor: Sequence[Sequence[float]],
    scale: float = 1.0,
    atol: float = 1e-6,
) -> tuple[float, float]:
    """Return (max distance-preservation error, max relative-angle error) for a
    group of points mapped by unity_to_ar with the given anchor.

    A rigid rotation may re-orient each vector, so the orientation invariant is
    the RELATIVE angle between pairs of directions (proper rotations preserve
    angles between vectors, not the absolute direction of any single one).
    """
    pts = [tuple(float(x) for x in p) for p in points]
    mapped = [tuple(unity_to_ar(p, t_anchor, r_anchor, scale)) for p in pts]
    pairs = [(pts[i], pts[j]) for i in range(len(pts)) for j in range(i + 1, len(pts))]
    pairs_m = [(mapped[i], mapped[j]) for i in range(len(mapped)) for j in range(i + 1, len(mapped))]
    dist_err = distance_error_max(pairs, pairs_m)
    orient_err = 0.0
    if len(pts) >= 3:
        v1 = vec_sub(pts[1], pts[0])
        v2 = vec_sub(pts[2], pts[0])
        w1 = vec_sub(mapped[1], mapped[0])
        w2 = vec_sub(mapped[2], mapped[0])
        angle_a = angle_between(v1, v2)
        angle_b = angle_between(w1, w2)
        orient_err = abs(angle_a - angle_b)
    return dist_err, orient_err


def fake_anchor() -> tuple[list[float], list[list[float]], float]:
    """Pose without a phone: anchor at origin, no rotation, unit scale."""
    return [0.0, 0.0, 0.0], identity(), 1.0


if __name__ == "__main__":
    t0, r0, s0 = fake_anchor()
    print("round-trip err:", check_round_trip([(1, 2, 3), (-5, 0.2, 9), (47.491, 0.182, 5.94)]))
    print("rigid(model->unity):", is_rigid_rotation(MODEL_TO_UNITY))
    print("model->unity [1,2,3] =", model_to_unity([1, 2, 3]))