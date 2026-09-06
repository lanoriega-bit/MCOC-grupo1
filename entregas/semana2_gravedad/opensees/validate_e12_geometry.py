#!/usr/bin/env python3
"""Diagnostico geometrico visual del E12 viewer (E1 + E2).

Chequea:
- bounds XYZ por categoria y edificio,
- NaN/Inf en coordenadas,
- miembros de longitud ~0 (zero-length),
- cotas z fuera del stack de pisos [0, 19.80] o mal centradas
  (muros/columnas_vigas deben respetar la altura de historia),
- solapamiento de plantas entre E1 y E2 (posicion relativa).

Uso: python3 validate_e12_geometry.py
Salida: informe en consola + results/E12_GEOMETRY_DIAGNOSTIC.md
No modifica ningun resultado.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"

FLOOR_TOPS = {-1: 3.96, 1: 7.92, 2: 11.88, 3: 15.84, 4: 19.80}
STORY = 3.96
Z_MAX = 19.80 + 1e-6
EPS = 1e-9


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def finite(v: float) -> bool:
    return isinstance(v, (int, float)) and not (math.isnan(v) or math.isinf(v))


def node_zs(item: dict) -> list[float]:
    zs: list[float] = []
    for key in ("node_i", "node_j", "center", "point"):
        v = item.get(key)
        if isinstance(v, list) and len(v) >= 3 and isinstance(v[2], (int, float)):
            zs.append(float(v[2]))
    for v in item.get("vertices", []) or []:
        if isinstance(v, list) and len(v) >= 3 and isinstance(v[2], (int, float)):
            zs.append(float(v[2]))
    return zs


def length_m(item: dict) -> float | None:
    if "length_m" in item and isinstance(item["length_m"], (int, float)):
        return float(item["length_m"])
    i = item.get("node_i")
    j = item.get("node_j")
    if isinstance(i, list) and isinstance(j, list) and len(i) >= 3 and len(j) >= 3:
        return math.dist(i[:3], j[:3])
    return None


def check_category(name: str, items: list[dict], errors: list[str]) -> None:
    counts: dict[str, int] = {}
    z_bounds: dict[str, list[float]] = {}
    for it in items:
        b = it.get("building_id") or "E1"
        counts[b] = counts.get(b, 0) + 1
        zs = node_zs(it)
        if zs:
            lo, hi = min(zs), max(zs)
            j = z_bounds.setdefault(b, [lo, hi])
            j[0], j[1] = min(j[0], lo), max(j[1], hi)
    for b in sorted(counts):
        print(f"  {name:12s} {b}: {counts[b]}")

    for it in items:
        for key in ("node_i", "node_j", "center", "point"):
            v = it.get(key)
            if isinstance(v, list):
                for c in v:
                    if not finite(c):
                        errors.append(f"{name} {it.get('id') or it.get('beam_id') or it.get('slab_id')}: coordenada no finita en {key}")
        if any(not finite(c) for vert in it.get("vertices", []) or [] if isinstance(vert, list) for c in vert):
            errors.append(f"{name} {it.get('id') or it.get('beam_id') or it.get('slab_id')}: vertice no finito")
        L = length_m(it)
        if L is not None and L <= EPS:
            errors.append(f"{name} {it.get('id') or it.get('beam_id')}: longitud cero ({L})")

        zs = node_zs(it)
        if not zs:
            continue
        if any(z < -0.30 or z > Z_MAX for z in zs):
            errors.append(f"{name} {it.get('id') or it.get('beam_id')}: z fuera del stack [0,19.8]: {sorted(set(zs))}")
        for key in ("node_i", "node_j"):
            v = it.get(key)
            if not isinstance(v, list) or len(v) < 3:
                continue
            z = float(v[2])
            if name == "walls":
                if not any(abs(z - (t - STORY / 2.0)) < 0.02 for t in FLOOR_TOPS.values()):
                    errors.append(f"walls {it.get('id')}: z {z:.3f} no es media-historia ({it.get('floor_id')})")
            elif name in ("columns", "vigas"):
                if not any(abs(z - t) < 0.02 or (name == "columns" and abs(z - (t - STORY)) < 0.02) for t in FLOOR_TOPS.values()):
                    errors.append(f"{name} {it.get('id') or it.get('beam_id')}: z {z:.3f} fuera de piso ({it.get('floor_id')})")
        if name == "columns":
            c = it.get("center")
            if isinstance(c, list) and len(c) >= 3:
                zc = float(c[2])
                if not any(abs(zc - (t - STORY / 2.0)) < 0.02 for t in FLOOR_TOPS.values()):
                    errors.append(f"columns {it.get('id')}: center z {zc:.3f} no es media-historia")
    for b, (lo, hi) in sorted(z_bounds.items()):
        print(f"  {name:12s} {b}: z_min={lo:.3f} z_max={hi:.3f}")


def main() -> int:
    errors: list[str] = []
    e1 = load("edificio1_unity.json")
    e12 = load("edificios12_unity.json")
    # building_tag repetido por elemento
    for it in e1.get("walls", []) + e1.get("columns", []) + e1.get("vigas", []):
        it.setdefault("building_id", "E1")

    checks = [
        ("vigas", e1.get("vigas", []) + [b for b in e12.get("vigas", []) if b.get("building_id") == "E2"]),
        ("columns", e1.get("columns", []) + [c for c in e12.get("columns", []) if c.get("building_id") == "E2"]),
        ("walls", e1.get("walls", []) + [w for w in e12.get("walls", []) if w.get("building_id") == "E2"]),
        ("supports", e1.get("supports", []) + [s for s in e12.get("supports", []) if s.get("building_id") == "E2"]),
        ("losas", e1.get("losas", []) + [s for s in e12.get("losas", []) if s.get("building_id") == "E2"]),
    ]
    for name, items in checks:
        print(f"[{name}]")
        check_category(name, items, errors)

    # Posicion relativa E1/E2: bounds XY
    def xy_bounds(items: list[dict]) -> tuple[float, float, float, float]:
        xs, ys = [], []
        for it in items:
            for key in ("node_i", "node_j", "center", "point"):
                v = it.get(key)
                if isinstance(v, list) and len(v) >= 2 and finite(v[0]) and finite(v[1]):
                    xs.append(v[0]); ys.append(v[1])
            for v in it.get("vertices", []) or []:
                if isinstance(v, list) and len(v) >= 2:
                    xs.append(v[0]); ys.append(v[1])
        return (min(xs), max(xs), min(ys), max(ys)) if xs else (0, 0, 0, 0)

    e1xy = xy_bounds(e1.get("columns", []) + e1.get("walls", []))
    e2xy = xy_bounds([c for c in e12.get("columns", []) if c.get("building_id") == "E2"])
    e2walls_xy = xy_bounds([w for w in e12.get("walls", []) if w.get("building_id") == "E2"])
    print(f"\nE1 XY bounds (columns+walls): x[{e1xy[0]:.2f},{e1xy[1]:.2f}] y[{e1xy[2]:.2f},{e1xy[3]:.2f}]")
    print(f"E2 XY bounds (columns):       x[{e2xy[0]:.2f},{e2xy[1]:.2f}] y[{e2xy[2]:.2f},{e2xy[3]:.2f}]")
    print(f"E2 XY bounds (walls):          x[{e2walls_xy[0]:.2f},{e2walls_xy[1]:.2f}] y[{e2walls_xy[2]:.2f},{e2walls_xy[3]:.2f}]")

    # Verificacion wall fix: E2 walls mid-height
    e2w = [w for w in e12.get("walls", []) if w.get("building_id") == "E2"]
    midz = sorted({round(w["node_i"][2], 3) for w in e2w if isinstance(w.get("node_i"), list) and len(w["node_i"]) >= 3})
    print(f"\nE2 walls z values: {midz}")

    # --- Reglas forenses E12 FLOATING GEOMETRY FIX (2026-09-05) ---
    # 1) Determinismo de la clasificacion ESTRUCTURAL/CONTEXTO.
    print("\n[clasificacion E2 ESTRUCTURAL/CONTEXTO]")
    clasif = (e12.get("clasificacion_geometrica") or {}).get("E2") or {}
    frame = clasif.get("frame_bbox_m")
    pad = float(clasif.get("footprint_pad_m") or 1.20)
    tol = float(clasif.get("support_base_tol_m") or 2.50)

    def span_pts(it: dict) -> list[list[float]]:
        out = []
        for k in ("node_i", "node_j", "center", "point"):
            v = it.get(k)
            if isinstance(v, list) and len(v) >= 2:
                out.append([float(v[0]), float(v[1])])
        return out

    e2_cols = [c for c in e12.get("columns", []) if c.get("building_id") == "E2"]
    anchor_pts = set()
    for c in e2_cols:
        p = c.get("center") or c.get("node_j")
        if isinstance(p, list) and len(p) >= 2:
            anchor_pts.add((round(float(p[0]), 3), round(float(p[1]), 3)))

    def fully_outside(it: dict) -> bool:
        pts = span_pts(it)
        if not pts:
            return False
        return all(p[0] < frame["xmin"] - pad or p[0] > frame["xmax"] + pad or p[1] < frame["ymin"] - pad or p[1] > frame["ymax"] + pad for p in pts)

    def near_any_anchor(it: dict) -> bool:
        for p in span_pts(it):
            if any(math.hypot(p[0] - ax, p[1] - ay) <= 2.10 for ax, ay in anchor_pts):
                return True
        return False

    def is_valid_contexto(it: dict) -> tuple[bool, str]:
        if it.get("tipo") == "support":
            if fully_outside(it):
                return True, "support fuera de footprint"
            return (not near_any_anchor(it)), "support sin base FE/columna cercana"
        return fully_outside(it), "viga/muro fuera de footprint"

    ctx = [c for c in e12.get("elementos_contexto", []) if c.get("building_id") == "E2"]
    kept_v = [b for b in e12.get("vigas", []) if b.get("building_id") == "E2"]
    kept_w = [w for w in e12.get("walls", []) if w.get("building_id") == "E2"]
    supports = [s for s in e12.get("supports", []) if s.get("building_id") == "E2"]
    print(f"  contexto={len(ctx)} (viga={sum(1 for c in ctx if c.get('tipo') == 'viga')} muro={sum(1 for c in ctx if c.get('tipo') == 'muro')} support={sum(1 for c in ctx if c.get('tipo') == 'support')})")
    print(f"  kept: vigas={len(kept_v)} walls={len(kept_w)} supports={len(supports)} columns={len(e2_cols)} frame={frame}")
    if not frame:
        errors.append("clasificacion_geometrica.E2.frame_bbox_m ausente en edificios12_unity.json")
    else:
        mism = 0
        for c in ctx:
            ok, kind = is_valid_contexto(c)
            if not ok:
                mism += 1
                errors.append(f"contexto {c.get('id') or c.get('beam_id') or c.get('support_id')}: NO cumple regla ({kind})")
            if c.get("structural_class") != "CONTEXTO":
                errors.append(f"contexto {c.get('id') or c.get('beam_id') or c.get('support_id')}: structural_class != CONTEXTO")
        for it in kept_v + kept_w:
            if it.get("structural_class") != "ESTRUCTURAL":
                errors.append(f"kept {it.get('id') or it.get('beam_id')}: structural_class != ESTRUCTURAL")
            if fully_outside(it):
                errors.append(f"kept viga/muro {it.get('id') or it.get('beam_id')} esta fuera del footprint y NO es CONTEXTO")
        for it in supports:
            cls = it.get("structural_class")
            if cls != "ESTRUCTURAL":
                errors.append(f"kept support {it.get('support_id') or it.get('id')}: structural_class != ESTRUCTURAL")
        print(f"  verificacion clasificacion: {'OK' if mism == 0 else str(mism) + ' mismatches'}")

    # 2) Duplicados (mismob segmento, endpoints invertidos) dentro de kept y dentro de contexto.
    print("\n[duplicados]")
    seen: dict[str, list[str]] = {}
    for it in kept_v + kept_w + supports + ctx:
        i = it.get("node_i")
        j = it.get("node_j")
        if isinstance(i, list) and isinstance(j, list) and len(i) >= 3 and len(j) >= 3:
            a = (round(float(i[0]), 2), round(float(i[1]), 2), round(float(i[2]), 2))
            b = (round(float(j[0]), 2), round(float(j[1]), 2), round(float(j[2]), 2))
            sig = tuple(sorted((a, b)))
            keyid = str(sig)
            seen.setdefault(keyid, []).append(it)
    dup = {k: [x.get("id") or x.get("beam_id") or x.get("support_id") for x in v] for k, v in seen.items() if len(v) > 1}
    for k, ids in dup.items():
        errors.append(f"duplicado span {k}: {ids}")
    print(f"  spans duplicados: {len(dup)}")

    # 3) Floor plane vs z real (regla |delta_z_to_expected| > 0.10 m).
    print("\n[floor plane E2]")
    fid_to_z = {c.get("floor_id"): c.get("floor") for c in []}  # noop, mantenido para claridad
    fid_expect = {-1: 3.96, 1: 7.92, 2: 11.88, 3: 15.84, 4: 19.80}
    for it in kept_v + [c for c in e12.get("losas", []) if c.get("building_id") == "E2"]:
        fid = it.get("floor_id")
        exp = fid_expect.get(fid, it.get("node_i", [None, None, None])[2] if isinstance(it.get("node_i"), list) and len(it.get("node_i")) >= 3 else None)
        for k in ("node_i", "node_j"):
            v = it.get(k)
            if isinstance(v, list) and len(v) >= 3 and exp is not None and abs(float(v[2]) - exp) > 0.10:
                errors.append(f"{'beam' if it.get('beam_id') else 'slab'} {it.get('beam_id') or it.get('slab_id')}: z={float(v[2]):.3f} != floor plane {fid}={exp} (delta>0.10)")
    for it in kept_w:
        fid = it.get("floor_id")
        exp = fid_expect.get(fid)
        if exp is not None:
            for k in ("node_i", "node_j"):
                v = it.get(k)
                if isinstance(v, list) and len(v) >= 3 and abs(float(v[2]) - (exp - 1.98)) > 0.10:
                    errors.append(f"wall {it.get('id')}: z={float(v[2]):.3f} != mid-story {fid}={(exp - 1.98):.3f} (delta>0.10)")
    for it in e2_cols:
        fid = it.get("floor_id")
        exp = fid_expect.get(fid)
        if exp is not None:
            c0, c1, cc = it.get("node_i"), it.get("node_j"), it.get("center")
            if isinstance(c0, list) and len(c0) >= 3 and abs(float(c0[2]) - (exp - 3.96)) > 0.10:
                errors.append(f"column {it.get('id')}: node_i z={float(c0[2]):.3f} != {fid} story bottom {(exp - 3.96):.3f}")
            if isinstance(c1, list) and len(c1) >= 3 and abs(float(c1[2]) - exp) > 0.10:
                errors.append(f"column {it.get('id')}: node_j z={float(c1[2]):.3f} != {fid} floor top {exp}")
    for it in supports:
        for k in ("node_i", "node_j"):
            v = it.get(k)
            if isinstance(v, list) and len(v) >= 3 and abs(float(v[2]) - 0.0) > 0.10:
                errors.append(f"support {it.get('support_id') or it.get('id')}: z={float(v[2]):.3f} != base plane 0.0")

    # Zero-length y NaN global
    n_finite = sum(1 for it in e12.get("losas", []) for v in it.get("vertices", []) or [] for c in v if not finite(c))
    if n_finite:
        errors.append(f"{n_finite} coordenadas no finitas en losas E12")

    print()
    if errors:
        print(f"ERRORES GEOMETRICOS ({len(errors)}):")
        for e in errors[:40]:
            print("  -", e)
        if len(errors) > 40:
            print(f"  ... y {len(errors) - 40} mas")
    else:
        print("GEOMETRIA VISUAL: SIN ERRORES")

    out = RESULTS / "E12_GEOMETRY_DIAGNOSTIC.md"
    lines = ["# Diagnostico geometrico visual E12 (E1 + E2)", ""]
    lines.append(f"- E1 XY bounds (columns+walls): x[{e1xy[0]:.2f},{e1xy[1]:.2f}] y[{e1xy[2]:.2f},{e1xy[3]:.2f}]")
    lines.append(f"- E2 XY bounds (columns): x[{e2xy[0]:.2f},{e2xy[1]:.2f}] y[{e2xy[2]:.2f},{e2xy[3]:.2f}]")
    lines.append(f"- E2 XY bounds (walls): x[{e2walls_xy[0]:.2f},{e2walls_xy[1]:.2f}] y[{e2walls_xy[2]:.2f},{e2walls_xy[3]:.2f}]")
    lines.append(f"- E2 walls z (node_i): {midz}")
    lines.append("")
    if errors:
        lines.append(f"**ERRORES: {len(errors)}**")
        lines += [f"- {e}" for e in errors]
    else:
        lines.append("**GEOMETRIA VISUAL: SIN ERRORES**")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nInforme escrito: {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())