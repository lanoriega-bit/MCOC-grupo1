"""
Phase 3b: Y (and X) calibration per part_1 region.
The DXF sheets do NOT share a common global Y origin; the established mechanism
(sistema_global) uses per-sheet column-pattern alignment. Here we recompute offsets
for the RE-EXTRACTED per-floor regions, anchoring each part_1 floor to the part_1
Piso-1 reference columns (un-shifted) via nearest-column matching. Part_2 of a floor
provides an independent Y ruler to cross-check.

Outputs: region calibration offsets recorded in region_specs.json (offset_final_m for
part_1; part_2 uses its own per-sheet offsets from the old system).
"""
import json
from pathlib import Path
from itertools import product

DATOS = Path(r"C:\Users\matis\OneDrive\Documentos\Proyecto_1_MCOC\entregas\P1L2\edificio\datos")


def load(fl):
    return json.load(open(DATOS / f"{fl}.json", encoding="utf-8"))


def cols(d, zone=None):
    out = []
    for e in d["elementos"]:
        if e["tipo"] == "columna" and (zone is None or e["zona"] == zone):
            out.append((round(e["centro"][0], 3), round(e["centro"][1], 3)))
    return out


def best_offset(target, reference):
    """Search dy minimizing mean |dx| to nearest reference column (Y-matched)."""
    best_dy = 0.0
    best_cost = 1e18
    for k in range(-600, 600):
        dy = k * 0.1
        cost = 0.0
        n = 0
        for tx, ty in target:
            cands = [r for r in reference if abs(r[1] - (ty + dy)) < 1.0]
            if not cands:
                continue
            cost += min(abs(rx - tx) for rx, ry in cands)
            n += 1
        if n == 0:
            continue
        cost = cost / n
        if cost < best_cost:
            best_cost = cost
            best_dy = dy
    return best_dy, best_cost


def main():
    p1_ref = cols(load("piso_01"), "parte_1")   # reference (un-shifted)
    floors = ["fundacion", "subterraneo_01", "piso_02", "piso_03", "piso_04"]
    result = {}
    for fl in floors:
        d = load(fl)
        tcols = cols(d, "parte_1")
        if not tcols:
            result[fl] = {"parte_1_y_offset": 0.0, "n": 0}
            continue
        dy, cost = best_offset(tcols, p1_ref)
        result[fl] = {"parte_1_y_offset_m": round(dy, 3), "n": len(tcols), "mean_x_residual_m": round(cost, 3)}
        print(f"{fl:15s} n={len(tcols):3d}  Y offset parte_1 = {dy:+8.3f}  mean|dx|={cost:.3f}")

    with open(DATOS / "calibration_offsets.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\nSaved calibration_offsets.json")


if __name__ == "__main__":
    main()
