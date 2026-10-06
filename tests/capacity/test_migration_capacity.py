"""Regenerate capacity in isolation and compare every numeric leaf with CURRENT."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def numeric_leaves(value, path=""):
    if isinstance(value, dict):
        return {key: number for name, child in value.items()
                for key, number in numeric_leaves(child, path + "/" + name).items()}
    if isinstance(value, list):
        return {key: number for index, child in enumerate(value)
                for key, number in numeric_leaves(child, path + "/" + str(index)).items()}
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return {path: value}
    return {}


class CapacityMigrationTests(unittest.TestCase):
    def test_capacity_regeneration_has_identical_numeric_values(self):
        spec = importlib.util.spec_from_file_location("migration_capacity", ROOT / "analysis/capacity/build_capacity.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = json.loads(module.STREAM_OUT.read_text(encoding="utf-8-sig"))
        with tempfile.TemporaryDirectory(prefix="mcoc-capacity-migration-") as folder:
            module.OUT = Path(folder) / "capacity.json"
            module.STREAM_OUT = Path(folder) / "unity_capacity.json"
            module.main()
            after = json.loads(module.OUT.read_text(encoding="utf-8"))
            self.assertEqual(numeric_leaves(original), numeric_leaves(after))
            self.assertEqual(original["default_coefficients"], after["default_coefficients"])
            self.assertEqual(original["geometry_version"], after["geometry_version"])


if __name__ == "__main__":
    unittest.main()
