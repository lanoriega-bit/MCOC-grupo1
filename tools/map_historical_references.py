"""Inventory references and exact duplicates without executing any module (including AR).

Classification is deliberately conservative: unknown operational references remain
ACTIVE_REQUIRED. Serialized IDs/formats/provenance are not filesystem dependencies.
"""
from collections import Counter, defaultdict
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/repository_architecture_audit'
PATTERN = re.compile(r'entregas[/\\]+P1L[2-7]|pre_|post_|current_cleanup|week7|C:[/\\]Users[/\\]|OneDrive[/\\]', re.I)
SUFFIXES = {'.py', '.cs', '.json', '.ps1', '.bat', '.md', '.meta', '.yaml', '.yml', '.unity', '.asset', '.asmdef', '.txt'}

def classify(path, line):
    if path == 'ar/data/geometry_overlay.json' and any(key in line for key in ('"dataset":', '"central_model":')):
        return 'HISTORICAL_ONLY', 'Frozen source metadata; static consumer review recorded in AR_PATH_PROOF.md. Not opened as a path.'
    if path == 'ar/data/build_dataset.py' and '"geometry": "entregas/' in line:
        return 'HISTORICAL_ONLY', 'Output provenance only; actual inputs use CENTRAL=model and configured StreamingAssets.'
    if path.startswith(('archive/', 'reports/', 'entregas/')) or path == 'REPOSITORY_INVENTORY.json':
        return 'HISTORICAL_ONLY', 'Historical evidence or non-productive delivery; not permission to delete.'
    if path.endswith('.md') or line.lstrip().startswith(('#', '//', '///', '*')):
        return 'DOCUMENTATION_ONLY', 'Documentation/comment; update operational instructions separately.'
    if path == 'config/project_config.json' and '"luis_reference"' in line:
        return 'ACTIVE_REQUIRED', 'Original Luis reference is explicitly protected by AGENTS.md.'
    if 'historical_property_paths' in line or (path == 'config/project_config.json' and 'entregas/P1L5' in line):
        return 'ACTIVE_REQUIRED', 'Git show reads paths at the original analysis commit, not live filesystem paths.'
    if 'check_output' in line and 'git' in line and 'show' in line:
        return 'HISTORICAL_ONLY', 'Regression reads the original Git object, not the live historical folder.'
    if path == 'tools/plan_archive.py' and 'EXCEPTIONS' in line:
        return 'HISTORICAL_ONLY', 'Audit exclusion policy, not a filesystem consumer.'
    if path.endswith('.json') and path.startswith(('model/', 'results/', 'viewer/unity/Assets/StreamingAssets/', 'analysis/fiber/sections/')):
        return 'HISTORICAL_ONLY', 'Frozen data provenance/serialized identifiers; consumers use configured files, not these historical labels.'
    if any(key in line.lower() for key in ('"source', '"format"', '"analysis_version"', '"geometry_source"', '"capacity_source"', '"results_manifest"', '"manifest_source"')):
        return 'HISTORICAL_ONLY', 'Serialized provenance/format/version retained to preserve result bytes and compatibility.'
    if path.startswith(('ar/', 'tests/ar/')) or '/P1L6AR/' in path or '/Assets/AR/' in path:
        return 'ACTIVE_REQUIRED', 'AR is frozen; inspect only, no functional changes or tests.'
    if 'assertFalse' in line and 'viewer_unity' in line:
        return 'HISTORICAL_ONLY', 'Negative regression assertion, not an operational read.'
    if any(term in line for term in ('StreamingAssets', 'p1l5_', 'p1l6_', 'week7_', 'P1L5', 'P1L6')) and path.startswith('viewer/'):
        return 'ACTIVE_REQUIRED', 'Unity serialized API/asset identifier; cannot rename blindly without compatibility QA.'
    if 'entregas/' in line or 'entregas\\' in line:
        return 'ACTIVE_BUT_RELOCATABLE', 'Literal historical path in productive code; verify purpose before relocation.'
    return 'ACTIVE_REQUIRED', 'Ambiguous operational symbol/path; conservative manual review required.'

def main():
    tracked = subprocess.check_output(['git', '-c', 'core.quotepath=false', 'ls-files'], cwd=ROOT, text=True).splitlines()
    references = []
    hashes = defaultdict(list)
    for name in tracked:
        if name in {'reports/repository_architecture_audit/reference_map.json', 'reports/repository_architecture_audit/REFERENCE_MAP.md', 'reports/repository_architecture_audit/exact_duplicates.json'}:
            continue  # Never recursively inventory the previous inventory itself.
        path = ROOT / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if path.suffix in {'.json', '.csv', '.py', '.cs', '.md', '.ps1'}:
            hashes[hashlib.sha256(data).hexdigest()].append(name)
        if path.suffix not in SUFFIXES or name.startswith('archive/'):
            continue
        content = data.decode('utf-8-sig', errors='replace')
        doc_lines = set()
        if path.suffix == '.py':
            try:
                for node in ast.walk(ast.parse(content)):
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        doc_lines.update(range(node.lineno, node.end_lineno + 1))
            except SyntaxError:
                pass  # Unknown text stays conservative, never silently marked dead.
        for number, line in enumerate(content.splitlines(), 1):
            matches = list(dict.fromkeys(PATTERN.findall(line)))
            if not matches:
                continue
            classification, reason = classify(name, line)
            if number in doc_lines:
                classification, reason = 'DOCUMENTATION_ONLY', 'Python documentation literal, not executable filesystem access.'
            references.append({'consumer': name, 'line': number, 'tokens': matches,
                               'classification': classification, 'reason': reason, 'excerpt': line[:280]})
    duplicates = [{'sha256': digest, 'paths': paths, 'decision': 'REVIEW_CONSUMERS_AND_HISTORICAL_REASON'}
                  for digest, paths in hashes.items() if len(paths) > 1]
    summary = {'tracked_files': len(tracked), 'references': len(references),
               'classifications': dict(Counter(row['classification'] for row in references)),
               'exact_duplicate_groups': len(duplicates),
               'scope': 'Static file inventory only; no AR test, generation or result comparison.'}
    grouped = {}
    for row in references:
        key = (row['consumer'], row['classification'], row['excerpt'])
        if key not in grouped:
            grouped[key] = {k: v for k, v in row.items() if k != 'line'}
            grouped[key]['lines'] = []
        grouped[key]['lines'].append(row['line'])
    summary['distinct_reference_groups'] = len(grouped)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'reference_map.json').write_text(json.dumps({'summary': summary, 'references': list(grouped.values())}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'exact_duplicates.json').write_text(json.dumps(duplicates, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Referencias históricas — revisión conservadora', '',
             'Mapa completo: `reference_map.json`. Duplicados exactos: `exact_duplicates.json`.', '',
             'Ninguna clasificación automática autoriza un traslado o borrado.',
             'No hubo ejecución AR. Los hashes de duplicados son identidad de archivos, no comparación física de resultados AR.', '',
             '| Clase | Referencias |', '|---|---:|']
    lines += [f'| {name} | {count} |' for name, count in summary['classifications'].items()]
    lines += ['', '## Dependencias operativas relocalizables', '', '| Consumidor | Línea | Extracto |', '|---|---:|---|']
    for row in references:
        if row['classification'] == 'ACTIVE_BUT_RELOCATABLE':
            lines.append(f"| `{row['consumer']}` | {row['line']} | {row['excerpt'].replace('|', '/')} |")
    (OUT / 'REFERENCE_MAP.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
