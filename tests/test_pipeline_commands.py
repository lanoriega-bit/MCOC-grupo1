"""Command safety tests; solver/export/AR never run in these tests."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pipeline_commands', ROOT / 'tools/pipeline_commands.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PipelineCommandTests(unittest.TestCase):
    def test_default_plans_do_not_execute(self):
        with patch.object(module.subprocess, 'run') as runner, contextlib.redirect_stdout(io.StringIO()):
            for name in module.PLANS:
                self.assertEqual(module.run(name, []), 0)
        runner.assert_not_called()

    def test_no_ar_in_desktop_pipeline(self):
        for scripts in module.PLANS.values():
            self.assertTrue(all(not s.startswith('ar/') and '/AR' not in s for s in scripts))

    def test_failed_step_stops_and_invalidates(self):
        with patch.object(module.subprocess, 'run') as runner, contextlib.redirect_stdout(io.StringIO()):
            runner.return_value.returncode = 5
            self.assertEqual(module.run('rebuild_all', ['--execute']), 5)
            self.assertEqual(runner.call_count, 2)
            self.assertIn('invalidate.py', runner.call_args.args[0][-1])

    def test_paths_exist(self):
        for scripts in module.PLANS.values():
            for script in scripts:
                self.assertTrue((ROOT / script).is_file(), script)

if __name__ == '__main__':
    unittest.main()
