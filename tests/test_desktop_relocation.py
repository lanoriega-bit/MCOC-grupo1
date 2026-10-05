"""Desktop-only relocation checks. Does not execute AR or structural analysis."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DesktopRelocationTests(unittest.TestCase):
    def test_project_and_main_exist(self):
        config = json.loads((ROOT / 'config/project_config.json').read_text())
        self.assertEqual(config['paths']['unity'], 'viewer/unity')
        project = ROOT / config['paths']['unity']
        for name in ('Assets/Main.unity', 'Packages/manifest.json',
                     'ProjectSettings/ProjectVersion.txt',
                     'Assets/StreamingAssets/current_dataset_contract.json'):
            self.assertTrue((project / name).is_file(), name)
        self.assertFalse((ROOT / 'entregas/P1L3/José/viewer_unity/Assets').exists())

    def test_desktop_reanalysis_has_no_ar_steps(self):
        text = (ROOT / 'tools/reanalyse_current.ps1').read_text()
        self.assertNotIn("'ar/", text)
        self.assertNotIn('export_current_ar', text)
        self.assertNotIn('validate_ar', text)
        self.assertIn('analysis/postprocessing/export_unity.py', text)

    def test_desktop_protected_files_are_identical(self):
        report = json.loads((ROOT / 'reports/repository_architecture_audit/migration_equivalence_desktop.json').read_text())
        self.assertEqual(report['scope'], 'desktop')
        self.assertEqual(report['status'], 'PASS')
        for row in report['files']:
            self.assertEqual(hashlib.sha256((ROOT / row['current']).read_bytes()).hexdigest(),
                             row['expected_sha256'], row['current'])


if __name__ == '__main__':
    unittest.main()
