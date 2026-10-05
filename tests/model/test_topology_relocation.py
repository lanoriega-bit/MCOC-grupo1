"""Relocation/import checks; never calls the topology writer."""
import ast
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]

class TopologyRelocationTests(unittest.TestCase):
    def test_kernel_functions_unchanged(self):
        old = subprocess.check_output(['git', 'show', '05e885b:entregas/P1L3/scripts/build_post_p1l3_topology_candidate.py'], cwd=ROOT).decode('utf-8-sig')
        new = (ROOT / 'analysis/geometry/topology_kernel.py').read_text(encoding='utf-8-sig')
        functions = lambda text: [ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)]
        self.assertEqual(functions(old), functions(new))

    def test_adapter_routes(self):
        spec = importlib.util.spec_from_file_location('topology_adapter_check', ROOT / 'analysis/geometry/rebuild_topology.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for path in (module.MASTER_PATH, module.SECTIONS_PATH, module.LEGACY_BUILDER, module.PRIOR_AUDIT):
            self.assertTrue(path.is_file(), str(path))
            self.assertNotIn('entregas', path.parts)

if __name__ == '__main__':
    unittest.main()
