"""AR regeneration equality in a temporary destination, without replacing CURRENT."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ARDatasetMigrationTests(unittest.TestCase):
    def test_regeneration_identical_except_timestamp(self):
        spec = importlib.util.spec_from_file_location("ar_dataset_migration", ROOT / "ar/data/build_dataset.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = json.loads(module.STREAM_OUT.read_text(encoding="utf-8-sig"))
        with tempfile.TemporaryDirectory(prefix="mcoc-ar-migration-") as directory:
            module.STREAM_OUT = Path(directory) / "dataset.json"
            module.main()
            after = json.loads(module.STREAM_OUT.read_text(encoding="utf-8"))
            original.pop("generated_utc", None)
            after.pop("generated_utc", None)
            self.assertEqual(original, after)


if __name__ == "__main__":
    unittest.main()
