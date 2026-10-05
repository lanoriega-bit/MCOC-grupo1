"""Read-only structural checks plus desktop migration tests. No AR/OpenSees run."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    commands = [
        ['main.py', 'validar'],
        ['tools/verify_migration.py', '--scope', 'desktop'],
        ['tests/test_project_entrypoint.py'],
        ['tests/test_desktop_relocation.py'],
        ['tests/test_pipeline_commands.py'],
        ['tests/model/test_topology_relocation.py'],
    ]
    for args in commands:
        code = subprocess.run([sys.executable, '-B', *args], cwd=ROOT).returncode
        if code:
            return code
    print('DESKTOP VALIDATION PASS. Does not certify Editor Play, AR or clean regeneration.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
