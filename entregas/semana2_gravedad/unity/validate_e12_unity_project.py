"""Static validation for the integrated E1/E2 Unity delivery."""

from __future__ import annotations

import json
import sys
from pathlib import Path


UNITY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UNITY_ROOT.parents[2]
RESULTS = REPO_ROOT / "entregas" / "semana2_gravedad" / "results"


def fail(message: str) -> None:
    print(f"e12_unity_project FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.exists():
        fail(f"falta {name}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        json.dumps(data, allow_nan=False)
        return data
    except Exception as exc:
        fail(f"JSON invalido {name}: {exc}")


def main() -> None:
    if not (UNITY_ROOT / "Assets" / "Scenes" / "E1GravityViewer.unity").exists():
        fail("falta escena E1")
    if not (UNITY_ROOT / "Assets" / "Scenes" / "E12IntegratedViewer.unity").exists():
        fail("falta escena E12IntegratedViewer")

    loader = (UNITY_ROOT / "Assets" / "Scripts" / "E1GravityJsonLoader.cs").read_text(encoding="utf-8")
    for token in ("edificio1_unity.json", "edificios12_unity.json", "edificios12_unity_response.json", "SceneManager"):
        if token not in loader:
            fail(f"loader no contiene {token}")

    e12_unity = load("edificios12_unity.json")
    e12_response = load("edificios12_unity_response.json")
    e12_analysis = load("edificios12_opensees_analysis.json")
    interface = load("e12_interface_reconciliation.json")

    if e12_unity.get("formato") != "MCOC-grupo1-integrated-gravity-v1":
        fail("formato integrado inesperado")
    if set(e12_unity.get("buildings", [])) != {"E1", "E2"}:
        fail("buildings integrado no contiene E1/E2")
    if not e12_unity.get("losas") or not e12_unity.get("vigas"):
        fail("modelo integrado sin losas/vigas")
    if e12_response.get("deformation_scale") != 20.0:
        fail("deformation scale integrado no es 20x")
    if e12_analysis.get("E12_GLOBAL_QA", {}).get("status") != "PASS":
        fail("QA global E12 no pasa")
    if interface.get("interface_status") != "UNRESOLVED_INTERFACE":
        fail("interface status inesperado")

    for key in ("losas", "vigas", "columns", "walls", "supports", "diaphragms"):
        seen = set()
        for item in e12_unity.get(key, []):
            cid = item.get("composite_id")
            if not cid:
                fail(f"{key} sin composite_id")
            if cid in seen:
                fail(f"composite_id duplicado {cid}")
            seen.add(cid)

    print(
        "e12_unity_project OK: "
        f"{len(e12_unity.get('losas', []))} losas, "
        f"{len(e12_unity.get('vigas', []))} vigas, "
        f"{len(e12_unity.get('columns', []))} columnas, "
        f"{len(e12_unity.get('walls', []))} muros, "
        f"{len(e12_unity.get('supports', []))} apoyos"
    )


if __name__ == "__main__":
    main()
