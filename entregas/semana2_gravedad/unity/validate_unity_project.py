"""Static validation for the Semana 2 E1 Unity viewer project."""

from __future__ import annotations

import json
import sys
from pathlib import Path


UNITY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UNITY_ROOT.parents[2]
E1_JSON = REPO_ROOT / "entregas" / "semana2_gravedad" / "results" / "edificio1_unity.json"
L101_STATUS = "GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY"

REQUIRED_FILES = [
    "Assets/Scenes/E1GravityViewer.unity",
    "Assets/Scripts/E1GravityModels.cs",
    "Assets/Scripts/E1GravityJsonLoader.cs",
    "Assets/Scripts/E1ViewerBootstrap.cs",
    "Assets/Scripts/E1ViewerController.cs",
    "Packages/manifest.json",
    "ProjectSettings/ProjectVersion.txt",
    "ProjectSettings/EditorBuildSettings.asset",
    "README.md",
]

REQUIRED_CONTROLLER_TOKENS = [
    "showNodes",
    "showBeams",
    "showColumns",
    "showWalls",
    "showSupports",
    "showDiaphragms",
    "showIds",
    "showLocalAxes",
    "showTributaryAreas",
    "SearchById",
    "BeamText",
    "NodeText",
    "AddLocalAxes",
    "BuildColumnBox",
    "BuildWallPanel",
    "BuildSupportLinear",
    "BuildDiaphragmPlane",
    "HandleCamera",
]

VISUAL_KEYS = ("columns", "walls", "supports", "diaphragms")


def fail(message: str) -> None:
    print(f"unity_project FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def check_balanced_braces(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    depth = 0
    in_string = False
    escape = False
    for char in text:
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                fail(f"llaves desbalanceadas en {path.name}")
    if depth != 0:
        fail(f"llaves desbalanceadas en {path.name}")


def strip_visual(data: dict) -> dict:
    clean = json.loads(json.dumps(data))
    for key in VISUAL_KEYS:
        clean.pop(key, None)
    return clean


def head_json() -> dict | None:
    import subprocess

    rel = "entregas/semana2_gravedad/results/edificio1_unity.json"
    completed = subprocess.run(
        ["git", "show", "HEAD:" + rel],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return None
    return json.loads(completed.stdout)


def ensure_unique_ids(items: list[dict], key: str) -> None:
    seen = set()
    for item in items:
        value = item.get(key) or item.get("id")
        if not value:
            fail(f"{key} vacio en capa visual")
        if value in seen:
            fail(f"ID duplicado en capa visual: {value}")
        seen.add(value)


def main() -> None:
    for rel in REQUIRED_FILES:
        path = UNITY_ROOT / rel
        if not path.exists():
            fail(f"falta {rel}")

    manifest = json.loads((UNITY_ROOT / "Packages/manifest.json").read_text(encoding="utf-8"))
    deps = manifest.get("dependencies", {})
    if "com.unity.nuget.newtonsoft-json" not in deps:
        fail("manifest no incluye Newtonsoft Json")

    loader = (UNITY_ROOT / "Assets/Scripts/E1GravityJsonLoader.cs").read_text(encoding="utf-8")
    if not all(token in loader for token in ('".."', '"results"')):
        fail("loader no referencia results/edificio1_unity.json externo")
    if "edificio1_unity.json" not in loader:
        fail("loader no referencia edificio1_unity.json")

    controller = (UNITY_ROOT / "Assets/Scripts/E1ViewerController.cs").read_text(encoding="utf-8")
    for token in REQUIRED_CONTROLLER_TOKENS:
        if token not in controller:
            fail(f"controller no contiene {token}")

    for path in (UNITY_ROOT / "Assets/Scripts").glob("*.cs"):
        check_balanced_braces(path)

    data = json.loads(E1_JSON.read_text(encoding="utf-8"))
    baseline = head_json()
    if baseline is not None and strip_visual(data) != strip_visual(baseline):
        fail("campos existentes de gravedad/modelo cambiaron respecto a HEAD")
    if data.get("formato") != "MCOC-grupo1-gravity-v1":
        fail("JSON E1 tiene formato inesperado")
    if set(data.get("pisos_presentes", [])) != {-1, 1, 2, 3, 4}:
        fail("pisos_presentes no conserva 5 niveles E1")
    l101 = next((slab for slab in data.get("losas", []) if slab.get("slab_id") == "E1_F01_L101"), None)
    if not l101 or l101.get("status") != L101_STATUS or l101.get("gravity_verified") is not False:
        fail("L101 no conserva estado de blocker excluido")

    expected_counts = {"columns": 149, "walls": 134, "supports": 94, "diaphragms": 5}
    for key, expected in expected_counts.items():
        items = data.get(key)
        if not isinstance(items, list) or len(items) != expected:
            fail(f"{key} esperado={expected}, actual={0 if not isinstance(items, list) else len(items)}")
    ensure_unique_ids(data["columns"], "column_id")
    ensure_unique_ids(data["walls"], "wall_id")
    ensure_unique_ids(data["supports"], "support_id")
    ensure_unique_ids(data["diaphragms"], "diaphragm_id")

    for key in ("columns", "walls", "supports", "diaphragms"):
        for item in data[key]:
            if "origin/main:entregas/P1L2/unity_export/model_viewer.json" not in item.get("visual_source", ""):
                fail(f"{key} sin fuente visual trazable")

    print(
        "unity_project OK: "
        f"{len(data.get('losas', []))} losas, "
        f"{len(data.get('vigas', []))} vigas, "
        f"{len(data.get('columns', []))} columnas, "
        f"{len(data.get('walls', []))} muros, "
        f"{len(data.get('supports', []))} apoyos, "
        f"{len(data.get('diaphragms', []))} diafragmas, "
        f"{len(data.get('geometric_blockers', []))} blockers"
    )


if __name__ == "__main__":
    main()
