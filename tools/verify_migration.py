"""Verify the saved migration baseline without modifying any protected artifact."""
from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports/repository_architecture_audit"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=('all', 'desktop'), default='all')
    args = parser.parse_args()
    baseline = json.loads((AUDIT / "baseline.json").read_text(encoding="utf-8"))
    mapping = json.loads((AUDIT / "path_mapping.json").read_text(encoding="utf-8"))
    rows = []
    for old, recorded in baseline.items():
        relative = mapping.get(old, old)
        if args.scope == 'desktop' and (
            relative.startswith('ar/') or '/AR/' in relative or '/P1L6AR/' in relative
            or '/AR' in relative.split('/StreamingAssets/')[ -1]
            or 'ar_' in Path(relative).name.lower()
            or Path(relative).name.startswith('AR')
        ):
            continue
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError(f"Mapping escapes repository: {relative}")
        current = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
        rows.append({"original": old, "current": relative,
                     "expected_sha256": recorded["sha256"], "actual_sha256": current,
                     "exact_bytes_equal": current == recorded["sha256"]})
    failures = [row["current"] for row in rows if not row["exact_bytes_equal"]]
    report = {"status": "PASS" if not failures else "FAIL", "scope": args.scope, "files_checked": len(rows),
              "identical_files": len(rows) - len(failures), "failures": failures,
              "policy": "Exact byte identity is stronger than numeric equality. No metadata differences accepted silently.",
              "files": rows}
    filename = 'migration_equivalence_desktop.json' if args.scope == 'desktop' else 'migration_equivalence.json'
    (AUDIT / filename).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
