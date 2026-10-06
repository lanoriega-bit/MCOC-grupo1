"""Read-only repository/branch dependency audit; writes reports, never source data.

Static edges are clues, not proof of runtime reachability. An unresolved dynamic
path must be reviewed before archiving its target. Run from any working directory.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "repository_architecture_audit"
BASE = "53a048408b97bbd681063e0fe74c27846f693521"
AR_REF = "origin/p1l7/ar-final-search"
UNITY = "entregas/P1L3/José/viewer_unity"
CENTRAL = "entregas/P1L5/modelo_central"
CODE = {".py", ".cs", ".ps1", ".bat", ".sh"}
TEXT = CODE | {".json", ".md", ".asmdef", ".unity", ".asset", ".yaml", ".yml", ".txt"}
CORE = {
    f"{CENTRAL}/{name}.json": "CANONICAL_SOURCE"
    for name in ("model_master", "materials", "sections", "loads", "analysis_settings")
}
CORE["entregas/P1L2/unity_export/model_viewer.json"] = "LUIS_REFERENCE_READ_ONLY"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-c", "core.quotepath=false", *args],
                                   cwd=ROOT).decode("utf-8-sig").strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classification(path: str) -> str:
    if path in CORE:
        return CORE[path]
    if path.startswith(UNITY + "/Assets/StreamingAssets/"):
        return "UNITY_DERIVED_CONTRACT_REVIEW_HISTORICAL_PAYLOADS"
    if path.startswith(UNITY + "/"):
        return "ACTIVE_UNITY_OR_EMBEDDED_TEST"
    if path.startswith("entregas/P1L5/analysis/results/current/"):
        return "ACTIVE_OPENSEES_RESULT"
    if path.startswith("entregas/P1L7/fiber_studies/"):
        return "FIBER_DERIVED_SEPARATE_METHOD"
    if Path(path).suffix in CODE:
        return "CODE_REQUIRES_REACHABILITY_REVIEW"
    if Path(path).suffix == ".json":
        return "DATA_REQUIRES_CONSUMER_REVIEW"
    return "DOCUMENTATION_OR_REFERENCE_OR_ASSET"


def describe_code(path: str, content: str) -> dict:
    result = {"functions": [], "imports": [], "io_calls": [], "parse_error": None}
    if path.endswith(".py"):
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    result["functions"].append({"name": node.name, "line": node.lineno,
                                               "description": ast.get_docstring(node)})
                elif isinstance(node, ast.Import):
                    result["imports"].extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    result["imports"].append(node.module or "")
                elif isinstance(node, ast.Call):
                    target = ast.unparse(node.func)
                    if any(term in target.lower() for term in
                           ("read", "write", "load", "dump", "open", "save", "subprocess")):
                        result["io_calls"].append({"line": node.lineno,
                                                  "expression": ast.unparse(node)[:500]})
        except SyntaxError as error:
            result["parse_error"] = str(error)
    else:
        result["functions"] = [{"name": match.group(1), "line": content[:match.start()].count("\n") + 1}
                               for match in re.finditer(r"(?:public|private|internal|protected)\s+(?:static\s+)?\w+\s+(\w+)\s*\(", content)]
    return result


def numbers(value, prefix="") -> dict:
    """Compare every numeric leaf by JSON path, not aggregate totals alone."""
    if isinstance(value, dict):
        return {key: number for name, child in value.items()
                for key, number in numbers(child, prefix + "/" + str(name)).items()}
    if isinstance(value, list):
        return {key: number for index, child in enumerate(value)
                for key, number in numbers(child, prefix + "/" + str(index)).items()}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {prefix: value}
    return {}


def main() -> None:
    paths = git("ls-files", "-z").split("\0")
    paths = [path for path in paths if path and not path.startswith("reports/repository_architecture_audit/")]
    texts, jsons, rows = {}, {}, []
    exact, semantic = defaultdict(list), defaultdict(list)
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        raw = path.read_bytes()
        row = {"path": relative, "role": classification(relative), "bytes": len(raw),
               "sha256": digest(raw), "consumers": [], "references": []}
        exact[row["sha256"]].append(relative)
        if path.suffix in TEXT:
            text = raw.decode("utf-8-sig", errors="replace")
            texts[relative] = text
            row["absolute_paths"] = sorted(set(re.findall(r"[A-Za-z]:[/\\][^\n\r\"'<>]+", text)))
            row["weekly_reference_lines"] = [i for i, line in enumerate(text.splitlines(), 1)
                                              if re.search(r"entregas[/\\]|pre_P1L|post_P1L|current_cleanup", line)]
            if path.suffix in CODE:
                row.update(describe_code(relative, text))
            if path.suffix == ".json":
                try:
                    value = json.loads(text)
                    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                                           separators=(",", ":")).encode("utf-8")
                    row["json_semantic_sha256"] = digest(canonical)
                    semantic[row["json_semantic_sha256"]].append(relative)
                    jsons[relative] = value
                except ValueError as error:
                    row["json_parse_error"] = str(error)
        rows.append(row)
    by_path = {row["path"]: row for row in rows}
    basenames = defaultdict(list)
    for relative in paths:
        basenames[Path(relative).name].append(relative)
    # Literal full paths are stronger evidence than ambiguous basename references.
    for consumer, text in texts.items():
        normalized = text.replace("\\", "/")
        candidates = set()
        for name, targets in basenames.items():
            if name in text:
                candidates.update(targets)
        for target in sorted(candidates):
            if consumer == target:
                continue
            strength = "FULL_PATH_LITERAL" if target in normalized else "BASENAME_CANDIDATE"
            by_path[consumer]["references"].append({"target": target, "evidence": strength})
            by_path[target]["consumers"].append({"path": consumer, "evidence": strength})
    branches = []
    for line in git("for-each-ref", "--format=%(refname:short)|%(objectname)|%(committerdate:iso-strict)",
                    "refs/heads", "refs/remotes/origin").splitlines():
        name, commit, date = line.split("|", 2)
        if name.endswith("/HEAD"):
            continue
        ahead, behind = map(int, git("rev-list", "--left-right", "--count", f"{BASE}...{name}").split())
        branches.append({"ref": name, "commit": commit, "date": date,
                         "base_only_commits": ahead, "branch_only_commits": behind,
                         "contained_in_base": behind == 0,
                         "unique_commits": git("log", "--format=%H %s", f"{BASE}..{name}").splitlines()})
    ar_path = UNITY + "/Assets/StreamingAssets/p1l6_current_ar_elements.json"
    remote_ar = json.loads(git("show", f"{AR_REF}:{ar_path}"))
    local_ar = jsons[ar_path]
    before, other = numbers(local_ar), numbers(remote_ar)
    changed = [{"path": key, "ours": before[key], "ar_branch": other[key]}
               for key in sorted(before.keys() & other.keys()) if before[key] != other[key]]
    ar_compare = {"path": ar_path, "external_ref": AR_REF,
                  "numeric_leaf_counts": [len(before), len(other)],
                  "different_numeric_leaves": changed,
                  "only_ours": sorted(before.keys() - other.keys()),
                  "only_ar_branch": sorted(other.keys() - before.keys()),
                  "same_json": local_ar == remote_ar,
                  "policy": "DO_NOT_REPLACE_CURRENT_WITH_REMOTE_AR_DATASET"}
    baseline = {row["path"]: {key: row[key] for key in ("sha256", "json_semantic_sha256") if key in row}
                for row in rows if row["path"] in CORE or row["role"] in {
                    "UNITY_DERIVED_CONTRACT_REVIEW_HISTORICAL_PAYLOADS", "ACTIVE_OPENSEES_RESULT",
                    "FIBER_DERIVED_SEPARATE_METHOD"} or row["path"].endswith("current_ar_elements.json")}
    payload = {"format": "MCOC_ARCHITECTURE_READ_ONLY_AUDIT_V1", "base": BASE,
               "branch": git("branch", "--show-current"),
               "limitations": ["Static literal/import analysis does not execute scripts.",
                                "Basename matches are candidates; they do not authorize deletion.",
                                "No files were moved, removed, or structurally regenerated."],
               "summary": {"files": len(rows), "code": sum(Path(p).suffix in CODE for p in paths),
                           "json": len(jsons), "exact_duplicate_groups": sum(len(v) > 1 for v in exact.values()),
                           "semantic_json_duplicate_groups": sum(len(v) > 1 for v in semantic.values()),
                           "protected_baseline_files": len(baseline)},
               "branches": branches, "files": rows,
               "exact_duplicates": [v for v in exact.values() if len(v) > 1],
               "semantic_json_duplicates": [v for v in semantic.values() if len(v) > 1]}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("inventory.json", payload), ("baseline.json", baseline),
                       ("ar_branch_numeric_comparison.json", ar_compare)):
        (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ["# Auditoría read-only de arquitectura", "", f"Base: `{BASE}`.", "",
              "No autoriza borrar archivos. Los consumidores por basename requieren revisión manual.", "",
              "## Resumen", "", *[f"- {key}: {value}" for key, value in payload["summary"].items()], "",
              "## Ramas", "", "| Rama | Commits exclusivos | Incluida en base |", "|---|---:|---|"]
    report.extend(f"| `{row['ref']}` | {row['branch_only_commits']} | {row['contained_in_base']} |" for row in branches)
    report.extend(["", "## AR pendiente de integrar", "",
                   f"Comparación por ruta JSON: {len(changed)} valores numéricos distintos; "
                   f"{len(ar_compare['only_ours'])} hojas solo actuales y {len(ar_compare['only_ar_branch'])} solo remotas.",
                   "No sustituir el dataset vigente. Revisar funciones nuevas separadamente.", "",
                   "## Evidencias", "", "- `inventory.json`: cada archivo, funciones, imports, IO y consumidores.",
                   "- `baseline.json`: hashes de fuentes y derivados protegidos antes de migrar.",
                   "- `ar_branch_numeric_comparison.json`: diferencias AR completas.", "",
                   "Las carpetas semanales todavía siguen activas; esta auditoría no es el cierre de la migración."])
    (OUT / "AUDIT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({**payload["summary"], "ar_numeric_differences": len(changed)}, indent=2))


if __name__ == "__main__":
    main()
