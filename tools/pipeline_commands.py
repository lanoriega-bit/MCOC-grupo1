"""Functional command plans; explicit execution, fail-closed and desktop-only.

These commands coordinate existing implementations. They do not define another
structural model. Plans are read-only unless --execute is explicitly supplied.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PLANS = {
    'build_model': ['tests/model/validate_model.py', 'analysis/opensees/build_fe.py'],
    'run_analysis': ['analysis/postprocessing/invalidate.py',
                     'analysis/opensees/apply_request.py', 'analysis/opensees/live_loads.py',
                     'tests/model/validate_model.py', 'analysis/opensees/run_cases.py'],
    'generate_unity_data': ['analysis/postprocessing/export_unity.py',
                            'analysis/postprocessing/export_member_identity.py',
                            'analysis/postprocessing/export_materials.py',
                            'tests/model/validate_pipeline.py'],
    'rebuild_all': ['analysis/postprocessing/invalidate.py',
                    'analysis/opensees/apply_request.py', 'analysis/opensees/live_loads.py',
                    'tests/model/validate_model.py', 'analysis/opensees/run_cases.py',
                    'analysis/capacity/build_capacity.py',
                    'analysis/postprocessing/export_unity.py',
                    'analysis/postprocessing/export_member_identity.py',
                    'analysis/postprocessing/export_materials.py',
                    'tests/model/validate_pipeline.py'],
}


def run(name, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true',
                        help='Allow writes/reanalysis in THIS checkout; omitted means plan only.')
    args = parser.parse_args(argv)
    scripts = PLANS[name]
    for script in scripts:
        if not (ROOT / script).is_file():
            raise FileNotFoundError(script)
    print(f'{name}: ' + ('EXECUTE' if args.execute else 'PLAN ONLY; no files changed'))
    for script in scripts:
        print(script, flush=True)
    if not args.execute:
        return 0
    for script in scripts:
        code = subprocess.run([sys.executable, '-B', str(ROOT / script)], cwd=ROOT).returncode
        if code:
            # Never let a partially rebuilt pipeline advertise CURRENT.
            if name != 'build_model':
                subprocess.run([sys.executable, '-B', str(ROOT / 'analysis/postprocessing/invalidate.py')], cwd=ROOT)
            return code
    if name == 'run_analysis':
        # Solver output alone is not a compatible Viewer/capacity bundle.
        subprocess.run([sys.executable, '-B', str(ROOT / 'analysis/postprocessing/invalidate.py')], cwd=ROOT, check=True)
        print('Solver completed. Viewer remains STALE until complete export/capacity QA.')
    return 0
