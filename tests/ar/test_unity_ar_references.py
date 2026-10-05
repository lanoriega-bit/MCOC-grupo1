"""Static AR scene references and protection of the desktop scene/shader."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8"))
UNITY = ROOT / CONFIG["paths"]["unity"]
BASE = "53a048408b97bbd681063e0fe74c27846f693521"


class ARReferenceTests(unittest.TestCase):
    def test_final_scene_has_core_script_references(self):
        scene = (UNITY / "Assets/Scenes/Luis_AR_Test.unity").read_text(encoding="utf-8")
        for name in ("ARDatasetRepository", "StructuralARElementRenderer", "ARStructuralElementController",
                     "LuisAnchorProviderAdapter", "TrackedModelToARTransformBehaviour"):
            meta = (UNITY / f"Assets/Scripts/P1L6AR/{name}.cs.meta").read_text(encoding="utf-8")
            guid = re.search(r"^guid: (\w+)", meta, re.MULTILINE).group(1)
            self.assertIn(guid, scene, name)

    def test_overlay_and_desktop_shader_are_distinct(self):
        identifiers = []
        for name in ("ARForceOverlay", "TechnicalSurface"):
            meta = (UNITY / f"Assets/Resources/{name}.shader.meta").read_text(encoding="utf-8")
            identifiers.append(re.search(r"^guid: (\w+)", meta, re.MULTILINE).group(1))
        self.assertEqual(len(set(identifiers)), 2)

    def test_desktop_scene_and_appearance_not_replaced(self):
        prefix = "entregas/P1L3/José/viewer_unity/"
        for relative in ("Assets/Main.unity", "Assets/Scripts/ViewerVisualTerrain.cs",
                         "Assets/Scripts/ViewerVisualTheme.cs", "Assets/Resources/TechnicalSurface.shader"):
            before = subprocess.check_output(["git", "show", f"{BASE}:{prefix}{relative}"], cwd=ROOT).decode("utf-8-sig")
            after = (UNITY / relative).read_text(encoding="utf-8-sig")
            self.assertEqual(before.replace("\r\n", "\n"), after.replace("\r\n", "\n"), relative)


if __name__ == "__main__":
    unittest.main()
