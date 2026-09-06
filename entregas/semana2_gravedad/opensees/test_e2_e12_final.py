"""Reproducible E2/E12 final-output checks."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "entregas" / "semana2_gravedad" / "results"
UNITY = ROOT / "entregas" / "semana2_gravedad" / "unity"


def load(name: str):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def assert_json_clean(data) -> None:
    text = json.dumps(data, allow_nan=False)
    assert "NaN" not in text
    assert "Infinity" not in text


def test_required_outputs_exist_and_are_clean() -> None:
    names = [
        "edificio2_gravity.json",
        "edificio2_unity.json",
        "edificio2_opensees_analysis.json",
        "edificio2_unity_response.json",
        "e2_structural_mapping_coverage.json",
        "edificios12_unity.json",
        "edificios12_unity_response.json",
        "edificios12_opensees_analysis.json",
        "e12_interface_reconciliation.json",
    ]
    for name in names:
        path = RESULTS / name
        assert path.exists(), name
        assert_json_clean(load(name))


def test_e2_slabs_are_not_bbox_verified() -> None:
    data = load("edificio2_unity.json")
    assert data["losas"]
    for slab in data["losas"]:
        assert slab["status"] == "VERIFIED_CLOSED_SLAB"
        assert slab.get("geometry_status") == "VERIFIED_CLOSED_SLAB"
        assert not slab.get("es_relleno_bbox", False)
        assert len(slab["vertices"]) >= 4
        assert slab["closure_residual_m"] == 0.0


def test_e2_gravity_conservation_by_floor() -> None:
    data = load("edificio2_unity.json")
    for row in data["verificacion"]["qa_por_piso"].values():
        assert row["status"] == "PASS"
        assert abs(row["residual_area_m2"]) <= 1e-9
        assert abs(row["residual_load_kN"]) <= 1e-6
    assert data["verificacion"]["global_status"] == "PASS"


def test_e2_opensees_equilibrium_and_supports() -> None:
    data = load("edificio2_opensees_analysis.json")
    eq = data["global_equilibrium"]
    assert eq["status"] == "PASS"
    assert abs(eq["applied_gravity_kN"] - eq["sum_Rz_kN"]) <= 1e-6
    response = load("edificio2_unity_response.json")
    assert len(response["support_restraints"]) == len(response["reactions_kN"])
    for restraint in response["support_restraints"].values():
        assert restraint["dof_order"] == ["Tx", "Ty", "Tz", "RotX", "RotY", "RotZ"]
        assert restraint["fixity"] == [1, 1, 1, 1, 1, 1]


def test_force_ordering_and_statuses() -> None:
    response = load("edificio2_unity_response.json")
    required = {"N1", "Vy1", "Vz1", "T1", "My1", "Mz1", "N2", "Vy2", "Vz2", "T2", "My2", "Mz2"}
    for item in response["element_forces_kN"].values():
        assert required <= set(item["forces_kN"])
        assert item["analysis_status"] == "VERIFIED_CONNECTED_RESPONSE"
        assert item["stub_status"] != "SEGMENTATION_STUB_ARTIFACT"


def test_integrated_outputs_and_interface() -> None:
    assert (UNITY / "Assets" / "Scenes" / "E1GravityViewer.unity").exists()
    assert (UNITY / "Assets" / "Scenes" / "E12IntegratedViewer.unity").exists()
    e12 = load("edificios12_opensees_analysis.json")
    assert e12["integrated_fe_model"] is False
    assert e12["interface_status"] == "UNRESOLVED_INTERFACE"
    assert e12["E12_GLOBAL_QA"]["status"] == "PASS"


def test_losas_schema_e1_e2_compatible() -> None:
    """Regression for Newtonsoft parse failure at losas[104].source_plan.

    source_plan must be a JSON string in BOTH buildings (E1 keeps it as a
    scalar string; E2 must not serialize the sorted set as a JSON array).
    """
    e12 = load("edificios12_unity.json")
    losas = e12["losas"]
    assert len(losas) >= 105
    e1_losas = [s for s in losas if str(s.get("composite_id", "")).startswith("E1::")]
    e2_losas = [s for s in losas if str(s.get("composite_id", "")).startswith("E2::")]
    assert len(e1_losas) == 104
    assert len(e2_losas) == 60
    assert losas[104]["building_id"] == "E2", losas[104].get("composite_id")
    for slab in losas:
        assert isinstance(slab.get("source_plan"), str), (
            slab.get("composite_id"), type(slab.get("source_plan")).__name__
        )
        assert slab["source_plan"], slab.get("composite_id")


def _tname(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "num"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def test_no_scalar_container_type_mismatch() -> None:
    """E1 vs E2 shared-field type check over the combined JSON.

    C# (Newtonsoft) fields declared as scalars/list in E1 must accept E2
    values of the same JSON kind. 'None' versus value is tolerated (nullable
    / optional DTO fields); a scalar-vs-list/dict mismatch is a hard failure
    because it aborts deserialization at runtime.
    """
    e12 = load("edificios12_unity.json")
    for category in ("losas", "vigas", "columns", "walls", "supports", "diaphragms"):
        items = e12.get(category, [])
        e1 = [x for x in items if str(x.get("composite_id", "")).startswith("E1::")]
        e2 = [x for x in items if str(x.get("composite_id", "")).startswith("E2::")]
        if not e1 or not e2:
            continue
        common = set(k for x in e1 for k in x) & set(k for x in e2 for k in x)
        for key in sorted(common):
            t1 = {_tname(x.get(key)) for x in e1}
            t2 = {_tname(x.get(key)) for x in e2}
            t1_no_none = t1 - {"None"}
            t2_no_none = t2 - {"None"}
            if not t1_no_none or not t2_no_none:
                continue
            scalar = {"str", "num", "bool"}
            shape = lambda ts: "scalar" if (ts <= scalar) else ("list" if ts == {"list"} else ("dict" if ts == {"dict"} else "mixed"))
            s1 = shape(t1_no_none)
            s2 = shape(t2_no_none)
            if s1 != s2:
                raise AssertionError(
                    f"{category}.{key}: JSON shape mismatch E1={sorted(t1_no_none)} E2={sorted(t2_no_none)}"
                )


def test_duplicate_composite_ids_across_categories() -> None:
    e12 = load("edificios12_unity.json")
    seen: dict[str, str] = {}
    for category in ("losas", "vigas", "columns", "walls", "supports", "diaphragms", "nodes"):
        for item in e12.get(category, []):
            cid = item.get("composite_id")
            assert cid, (category, item.get("slab_id"), item.get("beam_id"))
            assert seen.get(cid, category) == category, f"duplicate composite_id {cid}"
            seen[cid] = category


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
    print("e2_e12_final_tests OK")
