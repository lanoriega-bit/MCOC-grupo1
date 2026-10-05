"""Source migration invariants; never recalculates or modifies sources."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports/repository_architecture_audit"


class SourceMigrationTests(unittest.TestCase):
    def test_sources_have_one_live_location(self):
        mapping = json.loads((AUDIT / "path_mapping.json").read_text(encoding="utf-8"))
        for old, new in mapping.items():
            self.assertFalse((ROOT / old).exists(), old)
            self.assertTrue((ROOT / new).is_file(), new)

    def test_protected_bytes_match_baseline(self):
        baseline = json.loads((AUDIT / "baseline.json").read_text(encoding="utf-8"))
        mapping = json.loads((AUDIT / "path_mapping.json").read_text(encoding="utf-8"))
        for old, value in baseline.items():
            path = ROOT / mapping.get(old, old)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), value["sha256"], str(path))

    def test_public_configuration_points_to_sources(self):
        config = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8"))
        for name in ("geometry", "sections", "materials", "loads"):
            self.assertTrue(config["paths"][name].startswith("model/"), name)
        self.assertEqual(config["paths"]["analysis_settings"], "config/analysis_settings.json")

    def test_slabs_not_duplicated(self):
        master = json.loads((ROOT / "model/model_master.json").read_text(encoding="utf-8"))
        self.assertTrue(any(e["type"] == "slab" for e in master["elements"]))
        self.assertFalse((ROOT / "model/slabs.json").exists())


if __name__ == "__main__":
    unittest.main()
