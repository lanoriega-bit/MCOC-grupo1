"""Read-only numerical modification demo: solve 0/default/double/restored Q.

Actual OpenSees solves are performed in memory. No canonical sources/results
are changed by this test. Run from root: python -B entregas/P1L7/test_week7_loads.py
"""
import copy
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/opensees"))
import live_loads as w
import run_cases as solver


def response(result):
    return ([x for n in result["nodes"] for x in n["displacement"]]
            + [x for r in result["support_reactions"] for x in r["reaction"]]
            + [x for r in result["elements"] for end in ("i", "j")
               for x in r["local_end_forces"][end].values()])


def main():
    master = w.read(w.CENTRAL / "model_master.json")
    original = w.read(w.CENTRAL / "loads.json")
    sections = {r["section_id"]: r for r in w.read(w.CENTRAL / "sections.json")["sections"]}
    materials = {r["material_id"]: r for r in w.read(w.CENTRAL / "materials.json")["materials"]}
    config = w.settings()
    baseline = config["live_load"]["default_intensity_kN_m2"]
    for invalid in (-0.1, float('nan'), float('inf')):
        trial = copy.deepcopy(config)
        trial["live_load"]["intensity_kN_m2"] = invalid
        try:
            w.refresh(original, master, trial)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid qQ accepted: {invalid}")
    solved = []
    for q in (0.0, baseline, 2 * baseline, baseline):
        trial = copy.deepcopy(config)
        trial["live_load"]["intensity_kN_m2"] = q
        loads = w.refresh(original, master, trial)
        assert loads["current_load_application"]["nodal_loads"]["G"] == original["current_load_application"]["nodal_loads"]["G"]
        assert w.tributary_signature(loads["tributary_areas"]["panos"]) == config["frozen_tributaries_sha256"]
        app = loads["current_load_application"]
        area = sum(p["area_m2"] for p in loads["tributary_areas"]["panos"])
        assert math.isclose(app["totals"]["Q_N"], q * 1000 * area, abs_tol=1e-6)
        assert math.isclose(sum(r["G_total_N"] for r in app["by_floor"]), app["totals"]["G_total_N"], abs_tol=0.1)
        contract = solver.prepare_contract(master, sections, materials, loads)
        result = solver.run_case(contract, "Q")
        assert result["status"] == "PASS", result["qa"]
        solved.append(result)
        print(json.dumps({"qQ_kN_m2": q, "Q_N": app["totals"]["Q_N"], "max_translation_m": result["qa"]["max_translation_m"]}))
    # Compare all nodal DOFs, not only a single maximum.
    zero, base, double, restored = map(response, solved)
    assert max(map(abs, zero)) < 1e-10
    assert all(math.isclose(b, 2*a, rel_tol=1e-8, abs_tol=1e-6) for a,b in zip(base,double))
    assert all(math.isclose(a,b, rel_tol=1e-8, abs_tol=1e-6) for a,b in zip(base,restored))
    print("PASS: qQ 0/default/double/restored, unchanged G/areas, real OpenSees Q, lambdaQ equivalence")
    loads = w.refresh(original, master, config)
    contract = solver.prepare_contract(master, sections, materials, loads)
    basis = {name: solver.run_case(contract, name) for name in ("G", "Q", "EX", "EY")}
    basis_vectors = {name: response(data) for name,data in basis.items()}
    for factors in ({"G":0.,"Q":0.,"EX":0.,"EY":0.},
                    {"G":1.,"Q":1.,"EX":1.,"EY":1.},
                    {"G":0.83,"Q":1.17,"EX":-0.21,"EY":0.13}):
        combined = defaultdict(lambda: [0.,0.,0.])
        for name in ("G", "Q"):
            for tag, force in contract["nodal"][name].items():
                combined[tag][2] += factors[name]*force
        for tag, force in contract["lateral"].items():
            combined[tag][0] += factors["EX"]*force
            combined[tag][1] += factors["EY"]*force
        contract["combined_nodal_loads"] = dict(combined)
        explicit = response(solver.run_case(contract, "R"))
        expected = [sum(factors[k]*values[i] for k,values in basis_vectors.items()) for i in range(len(explicit))]
        scale = max(1.,max(map(abs,expected)))
        error = max(abs(a-b) for a,b in zip(explicit,expected))
        assert error <= scale * 1e-8, (factors, error)
        print(json.dumps({"explicit_R_coefficients": factors, "max_absolute_mixed_SI_error": error, "relative_global_error": error/scale}))


if __name__ == "__main__":
    main()
