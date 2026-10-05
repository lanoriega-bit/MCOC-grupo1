"""Genera curvas P-M de capacidad para todas las familias de seccion del modelo CURRENT.

Reutiliza el motor Fiber Section de P1L4 (wall_pm_interaction.py) sin modificar
resultados historicos. Familias: 5 secciones de columna + 4 de muro del modelo
central CURRENT. Acero longitudinal ASUMIDO_LAB documentado por familia.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "opensees"))

import openseespy.opensees as ops  # noqa: E402,F401
from wall_pm_interaction import run_axial_capacity, run_pm_interaction  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CENTRAL = HERE.parents[1] / "modelo_central"

FC_PA = 35_000_000.0
FY_PA = 420_000_000.0
ES_PA = 200_000_000_000.0
COVER_COL_M = 0.04
COVER_WALL_M = 0.02
EPS_C0 = -0.002
EPS_U = -0.0035
FP_CU_RATIO = 0.20
FRACTIONS = [0.0, 0.03, 0.06, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
STEPS = 260
PHI_FACTOR = 7.0
FIB_WALL_Y = 80
FIB_WALL_Z = 8
FIB_COL_Y = 28
FIB_COL_Z = 28

CSV_FIELDS = ["point_id", "P_kN", "compression_magnitude_kN", "M_kNm", "curvature_at_M_1_per_m", "converged_steps", "requested_steps", "valid", "status"]


def value_wrapped(v):
    return {"value": v}


def base_config(section_id):
    return {
        "section_id": section_id,
        "geometry": {
            "length_m": None,
            "thickness_m": None,
            "cover_m": value_wrapped(COVER_WALL_M),
            "pm_axis": value_wrapped("Mz"),
        },
        "reinforcement": {
            "vertical_bars": {
                "diameter_m": value_wrapped(0.016),
                "spacing_m": value_wrapped(0.20),
                "curtains": value_wrapped(2),
            }
        },
        "materials": {
            "concrete": {
                "fc_pa": value_wrapped(FC_PA),
                "epsc0": value_wrapped(EPS_C0),
                "fpcu_ratio": value_wrapped(FP_CU_RATIO),
                "epsu": value_wrapped(EPS_U),
            },
            "steel_vertical": {
                "fy_pa": value_wrapped(FY_PA),
                "Es_pa": value_wrapped(ES_PA),
                "hardening_ratio": value_wrapped(0.0),
            },
        },
        "fiber_discretization": {"num_fibers_y": value_wrapped(FIB_WALL_Y), "num_fibers_z": value_wrapped(FIB_WALL_Z)},
        "analysis": {
            "moment_curvature": {"num_steps": value_wrapped(STEPS), "target_factor_phi_y": value_wrapped(PHI_FACTOR)},
            "axial_capacity": {"num_steps": value_wrapped(STEPS), "target_strain_factor_epsu": value_wrapped(1.0)},
            "pm_interaction": {"compression_fractions": value_wrapped(FRACTIONS)},
        },
    }


def build_families(master, sections):
    families = {}
    for e in master["elements"]:
        if e["type"] not in ("column", "wall") or not e.get("active", True):
            continue
        key = (e["section_id"], e["type"])
        families.setdefault(key, []).append(e["element_id"])
    out = {}
    for (section_id, kind), members in families.items():
        sec = next(s for s in sections["sections"] if s["section_id"] == section_id)
        dims = sec["dimensions"]
        cfg = base_config(section_id)
        if kind == "wall":
            cfg["geometry"]["length_m"] = value_wrapped(float(dims["length_m"]))
            cfg["geometry"]["thickness_m"] = value_wrapped(float(dims["thickness_m"]))
            cfg["geometry"]["cover_m"] = value_wrapped(COVER_WALL_M)
            cfg["reinforcement"]["vertical_bars"]["diameter_m"] = value_wrapped(0.016)
            cfg["reinforcement"]["vertical_bars"]["spacing_m"] = value_wrapped(0.20)
            note = "Muro: barras verticales 2 capas D16@0.20 + horizontales D12@0.20 (ASUMIDO_LAB, coherente con P1L4)."
        else:
            b = float(dims["width_m"])
            h = float(dims["depth_m"])
            cfg["geometry"]["length_m"] = value_wrapped(max(b, h))
            cfg["geometry"]["thickness_m"] = value_wrapped(min(b, h))
            cfg["geometry"]["cover_m"] = value_wrapped(COVER_COL_M)
            cfg["geometry"]["pm_axis"] = value_wrapped("My")
            cfg["fiber_discretization"] = {"num_fibers_y": value_wrapped(FIB_COL_Y), "num_fibers_z": value_wrapped(FIB_COL_Z)}
            if max(b, h) >= 0.7:
                cfg["reinforcement"]["vertical_bars"]["diameter_m"] = value_wrapped(0.025)
                cfg["reinforcement"]["vertical_bars"]["spacing_m"] = value_wrapped(0.15)
                note = "Columna 0.70: 10D25 (2 capas, s=0.15m, rho=1.0%), r=4cm (ASUMIDO_LAB, similar a 12D25 de P1L3)."
            elif max(b, h) >= 0.35:
                cfg["reinforcement"]["vertical_bars"]["diameter_m"] = value_wrapped(0.020)
                cfg["reinforcement"]["vertical_bars"]["spacing_m"] = value_wrapped(0.15)
                note = "Columna 0.35: 6D20 (2 capas, s=0.15m, rho=1.5%), r=4cm (ASUMIDO_LAB)."
            else:
                cfg["reinforcement"]["vertical_bars"]["diameter_m"] = value_wrapped(0.016)
                cfg["reinforcement"]["vertical_bars"]["spacing_m"] = value_wrapped(0.15)
                note = "Columna 0.20: 4D16 (2 capas, s=0.15m, rho=2.0%), r=4cm (ASUMIDO_LAB)."
        out[section_id] = {
            "kind": kind,
            "section_id": section_id,
            "members": sorted(members),
            "config": cfg,
            "note": note,
            "reinf": json.dumps(
                {
                    "diameter_m": cfg["reinforcement"]["vertical_bars"]["diameter_m"]["value"],
                    "spacing_m": cfg["reinforcement"]["vertical_bars"]["spacing_m"]["value"],
                    "curtains": cfg["reinforcement"]["vertical_bars"]["curtains"]["value"],
                }
            ),
        }
    return out


def run_family(family):
    cfg = family["config"]
    ops.wipe()
    axial_rows, axial_meta = run_axial_capacity(cfg)
    if axial_meta["failed_step"] is not None:
        raise RuntimeError(f"Fallo axial {family['section_id']} paso {axial_meta['failed_step']}")
    pm_rows = run_pm_interaction(cfg, axial_meta["p0_kN"])
    if len([r for r in pm_rows if r["valid"]]) < 5:
        raise RuntimeError(f"Curva {family['section_id']} insuficiente (validos < 5)")
    family["axial_p0_kN"] = axial_meta["p0_kN"]
    family["pm_rows"] = pm_rows
    return family


def write_family(family):
    import csv

    path = RESULTS / f"{family['section_id']}.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(family["pm_rows"])
    return path


def main():
    master = json.loads((CENTRAL / "model_master.json").read_text(encoding="utf-8-sig"))
    sections = json.loads((CENTRAL / "sections.json").read_text(encoding="utf-8-sig"))
    families = build_families(master, sections)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    out = {}
    for section_id, family in families.items():
        if only and section_id != only:
            out[section_id] = {"skipped": True, "members": family["members"], "kind": family["kind"], "section_id": section_id}
            continue
        family = run_family(family)
        csv_path = write_family(family)
        out[section_id] = {
            "kind": family["kind"],
            "section_id": section_id,
            "members": family["members"],
            "axial_p0_kN": round(family["axial_p0_kN"], 2),
            "note": family["note"],
            "reinforcement": family["reinf"],
            "csv": csv_path.name,
            "points": [{"point_id": r["point_id"], "P_kN": round(r["P_kN"], 2), "M_kNm": round(r["M_kNm"], 2), "valid": r["valid"]} for r in family["pm_rows"]],
            "valid_point_count": len([r for r in family["pm_rows"] if r["valid"]]),
        }
        print(f"OK {section_id} kind={family['kind']} p0={family['axial_p0_kN']:.1f}kN valid={out[section_id]['valid_point_count']}")
    (RESULTS / "capacidad_por_seccion.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "families": len(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()