"""List archival candidates and active literal references without moving anything.

Static references are clues, not proof of runtime reachability. AR is excluded
from functional inspection. Do not treat this report as permission for bulk moves.
"""
from collections import Counter
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/repository_architecture_audit'
EXCEPTIONS = {'entregas/P1L2/unity_export/model_viewer.json', 'entregas/P1L2/STATUS.md'}

def main():
    tracked = subprocess.check_output(['git', '-c', 'core.quotepath=false', 'ls-files'], cwd=ROOT, text=True).splitlines()
    candidates = [p for p in tracked if p.startswith('entregas/') and p not in EXCEPTIONS]
    active = [p for p in tracked if p.startswith(('analysis/', 'tools/', 'tests/', 'config/', 'docs/'))
              or p in ('main.py', 'README.md', 'PROJECT_INDEX.md', 'Abrir_Unity.ps1')]
    texts = {}
    for path in active:
        if path.startswith('tests/ar/') or Path(path).suffix not in {'.py', '.ps1', '.md', '.json'}:
            continue
        texts[path] = (ROOT / path).read_text(encoding='utf-8-sig', errors='replace')
    rows = []
    for path in candidates:
        references = [p for p, text in texts.items() if path in text]
        rows.append({'path': path, 'proposed_destination': 'archive/' + path,
                     'active_literal_references': references,
                     'decision': 'REVIEW_REFERENCES' if references else 'REVIEW_DYNAMIC_DEPENDENCIES'})
    report = {'status': 'PLAN_ONLY_NOT_AUTHORIZED_FOR_BULK_MOVE', 'count': len(rows),
              'exceptions': sorted(EXCEPTIONS), 'files': rows,
              'limitations': ['No scripts or AR tests executed.',
                              'No claim that every candidate is obsolete.',
                              'Dynamic imports/relative references need module-by-module review.']}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'archive_candidates.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = Counter('/'.join(p.split('/')[:2]) for p in candidates)
    lines = ['# Plan de archivo pendiente', '', 'No se movió ningún candidato de esta lista.', '',
             'El movimiento masivo fue rechazado por revisión de seguridad porque no demuestra',
             'que todos sean históricos. Revisar por módulo, trasladar auxiliares activos y',
             'actualizar referencias antes de ejecutar movimientos pequeños.', '',
             '| Grupo | Archivos candidatos |', '|---|---:|']
    lines += [f'| `{name}` | {count} |' for name, count in sorted(groups.items())]
    lines += ['', 'Listado exacto y referencias: `archive_candidates.json`.', '',
              'Excepciones inamovibles: referencia original de Luis y STATUS de P1L2.',
              'AR: organización solamente; no auditoría funcional ni ejecución.',
              'El baseline desktop pasó desde una copia Git limpia, pero eso no certifica',
              'que scripts geométricos antiguos no sean necesarios para futuras modificaciones.']
    (OUT / 'ARCHIVE_PLAN.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'candidates': len(rows), 'groups': dict(groups)}, indent=2))

if __name__ == '__main__':
    main()
