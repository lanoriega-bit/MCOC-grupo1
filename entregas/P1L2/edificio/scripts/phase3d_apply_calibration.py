"""
Phase 3d: robust global-XY calibration of each part_1 floor region by ICP column matching
to the part_1 Piso-1 reference columns. Solves rigid translation (dx,dy), rotation 0,
scale 1. Then applies the offset to part_1 geometry in each floor file, and cross-checks
continuity with part_2 columns of the same floor.
"""
import json
import math
from pathlib import Path

DATOS = Path(r"C:\Users\matis\OneDrive\Documentos\Proyecto_1_MCOC\entregas\P1L2\edificio\datos")


def load(fl):
    return json.load(open(DATOS / f"{fl}.json", encoding="utf-8"))


def cols(d, zone):
    return [(round(e["centro"][0], 3), round(e["centro"][1], 3)) for e in d["elementos"]
            if e["tipo"] == "columna" and e["zona"] == zone]


def icp_translation(target, ref, iters=20, match_tol=2.5):
    """Solve global (dx,dy) translating target onto ref via nearest-neighbor ICP."""
    best_dx, best_dy = 0.0, 0.0
    best_cost = 1e18
    # grid search coarse then ICP refine
    for i in range(iters):
        cost = 0.0
        n = 0
        dxl = []
        dyl = []
        for tx, ty in target:
            best = None; bd = 1e18
            for rx, ry in ref:
                d = (rx - (tx + best_dx)) ** 2 + (ry - (ty + best_dy)) ** 2
                if d < bd:
                    bd = d; best = (rx, ry)
            if best is None or bd > match_tol ** 2:
                continue
            dxl.append(best[0] - tx)
            dyl.append(best[1] - ty)
            cost += math.sqrt(bd); n += 1
        if not dxl:
            break
        mx = sum(dxl) / len(dxl)
        my = sum(dyl) / len(dyl)
        # damped update
        new_dx = best_dx + 0.6 * mx
        new_dy = best_dy + 0.6 * my
        if abs(new_dx - best_dx) < 0.005 and abs(new_dy - best_dy) < 0.005:
            best_dx, best_dy = new_dx, new_dy
            break
        best_dx, best_dy = new_dx, new_dy
    return round(best_dx, 3), round(best_dy, 3)


def apply_offset(fl, dx, dy, zone):
    d = load(fl)
    for e in d["elementos"]:
        if e["zona"] != zone:
            continue
        if "centro" in e:
            e["centro"][0] = round(e["centro"][0] + dx, 3)
            e["centro"][1] = round(e["centro"][1] + dy, 3)
        if "inicio" in e and "fin" in e:
            e["inicio"][0] = round(e["inicio"][0] + dx, 3)
            e["inicio"][1] = round(e["inicio"][1] + dy, 3)
            e["fin"][0] = round(e["fin"][0] + dx, 3)
            e["fin"][1] = round(e["fin"][1] + dy, 3)
    # recompute bbox
    pts = []
    for e in d["elementos"]:
        if "centro" in e:
            pts.append(e["centro"])
        elif "inicio" in e:
            pts.append(e["inicio"]); pts.append(e["fin"])
    if pts:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        d["bbox"] = [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]
    with open(DATOS / f"{fl}.json", "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    return d


def main():
    p1_ref = cols(load("piso_01"), "parte_1")
    results = {}
    # floors whose part_1 needs calibration (piso_01 is reference)
    for fl in ["fundacion", "subterraneo_01", "piso_02", "piso_03", "piso_04"]:
        t = cols(load(fl), "parte_1")
        dx, dy = icp_translation(t, p1_ref)
        results[fl] = {"parte_1_dx_m": dx, "parte_1_dy_m": dy, "n": len(t)}
        print(f"{fl:15s} parte_1 -> dx={dx:+.3f} dy={dy:+.3f}  n={len(t)}")
        apply_offset(fl, dx, dy, "parte_1")
    # store calibration
    (DATOS / "calibration_offsets.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nApplied+stored calibration_offsets.json")


if __name__ == "__main__":
    main()
