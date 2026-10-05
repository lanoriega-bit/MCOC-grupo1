"""Tests de la entrada pública: sin tocar geometría, cargas ni Unity."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("project_entrypoint", ROOT / "main.py")
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)


class EntryPointTests(unittest.TestCase):
    def test_config_paths_exist(self):
        self.assertEqual(entry.load_config()["schema_version"], 1)

    def test_no_path_escape(self):
        with self.assertRaises(ValueError):
            entry.project_path("../outside.json")

    def test_default_is_read_only_status(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main([]), 0)

    def test_paths(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(entry.main(["rutas"]), 0)
        self.assertIn("model_master.json", output.getvalue())

    def test_stale_geometry_fails_closed(self):
        with patch.object(entry, "sha256", return_value="changed"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main(["estado"]), 1)

    def test_stops_after_failed_validator(self):
        with patch.object(entry, "properties_match_export", return_value=True), patch.object(entry.subprocess, "run") as runner, contextlib.redirect_stdout(io.StringIO()):
            runner.return_value.returncode = 7
            self.assertEqual(entry.validate(entry.load_config()), 7)
            self.assertEqual(runner.call_count, 1)

    def test_validator_source_mutation_is_detected(self):
        with patch.object(entry, "properties_match_export", return_value=True), patch.object(entry.subprocess, "run") as runner, patch.object(entry, "sha256") as digest, contextlib.redirect_stdout(io.StringIO()):
            runner.return_value.returncode = 0
            digest.side_effect = ["before"] * 5 + ["after"] * 5
            self.assertEqual(entry.validate(entry.load_config()), 1)

    def test_no_reanalysis_command(self):
        self.assertEqual(set(entry.COMMANDS), {"estado", "rutas", "validar", "unity"})

    def test_property_change_is_detected(self):
        with patch.object(entry.subprocess, "check_output", return_value=b'{}'):
            self.assertFalse(entry.properties_match_export(entry.load_config()))

    def test_document_links_exist(self):
        import re
        for relative in ("README.md", "PROJECT_INDEX.md", "docs/GUIA_USO_Y_CAMBIOS.md",
                         "model/README.md"):
            path = ROOT / relative
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((path.parent / target.split("#")[0]).exists(), f"{relative}: {target}")


if __name__ == "__main__":
    unittest.main()
