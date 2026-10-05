"""Single entry to existing in-memory solver/load/superposition checks.

Implementation stays in tests/loads/test_live_loads.py: no duplicate calculations,
no saved results written, no AR calls.
"""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    raise SystemExit(subprocess.run([sys.executable, '-B', str(root / 'tests/loads/test_live_loads.py')], cwd=root).returncode)
