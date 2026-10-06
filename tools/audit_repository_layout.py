"""Static repository closeout: no imports of project modules or execution of engines."""
import ast
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/repository_architecture_audit/STATIC_ORGANIZATION_QA.json'


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT, text=True).splitlines()


def main():
    tracked = git('ls-files')
    config = json.loads((ROOT / 'config/project_config.json').read_text(encoding='utf-8'))
    missing = [p for p in [*config['paths'].values(), *config['validators']] if not (ROOT / p).exists()]
    syntax_errors = []
    parsed = 0
    for name in tracked:
        if name.endswith('.py') and (name.startswith(('analysis/', 'tools/', 'tests/')) or name == 'main.py') and not name.startswith('tests/ar/'):
            try:
                ast.parse((ROOT / name).read_text(encoding='utf-8-sig'), filename=name)
                parsed += 1
            except SyntaxError as error:
                syntax_errors.append(f'{name}: {error}')
    # Git names only: no AR data is loaded or compared. Freeze everything in Unity.
    frozen_changes = git('diff', '--name-only', 'ce7233d', '--', 'viewer/unity', 'ar', 'model', 'results', 'config/analysis_settings.json')
    protected = json.loads((OUT.parent / 'migration_equivalence_desktop.json').read_text(encoding='utf-8'))
    references = json.loads((OUT.parent / 'reference_map.json').read_text(encoding='utf-8'))['summary']
    duplicates = json.loads((OUT.parent / 'exact_duplicates.json').read_text(encoding='utf-8'))
    unresolved_duplicates = [row for row in duplicates if row['decision'] == 'REVIEW_CONSUMERS_AND_HISTORICAL_REASON']
    branch = git('branch', '--show-current')[0]
    checks = {
        'configured_paths_exist': not missing,
        'productive_python_syntax': not syntax_errors,
        'frozen_sources_unchanged_since_scope_correction': not frozen_changes,
        'protected_desktop_bytes_identical': protected['status'] == 'PASS',
        'no_relocatable_active_legacy_paths': references['classifications'].get('ACTIVE_BUT_RELOCATABLE', 0) == 0,
        'exact_duplicates_have_recorded_retention_reason': not unresolved_duplicates,
        'working_branch_not_main': branch == 'codex/final-repository-architecture',
    }
    report = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'scope': 'STATIC_ORGANIZATION_ONLY',
              'branch': branch, 'checks': checks, 'missing_paths': missing, 'syntax_errors': syntax_errors,
              'python_files_parsed_not_executed': parsed, 'frozen_changed_paths': frozen_changes,
              'protected_files': protected['files_checked'], 'tracked_files': len(tracked),
              'untracked_local_files_preserved': git('ls-files', '--others', '--exclude-standard'),
              'unity_execution': 'NOT_RUN_OUT_OF_SCOPE', 'ar_execution': 'NOT_RUN_OUT_OF_SCOPE',
              'solver_execution': 'NOT_RUN', 'limitations': ['Static checks do not certify runtime behavior.',
              'Historical APIs/provenance and standalone academic benchmarks are documented exceptions.']}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'untracked_local_files_preserved'}, indent=2))
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
