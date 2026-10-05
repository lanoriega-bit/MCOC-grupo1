"""Verify the saved migration baseline without modifying any protected artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports/repository_architecture_audit"


def main() -> int:
    baseline = json.loads((AUDIT / "baseline.json").read_text(encoding="utf-8"))
    mapping = json.loads((AUDIT / "path_mapping.json").read_text(encoding="utf-8"))
    rows = []
    for old, recorded in baseline.items():
        relative = mapping.get(old, old)
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError(f"Mapping escapes repository: {relative}")
        current = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
        rows.append({"original": old, "current": relative,
                     "expected_sha256": recorded["sha256"], "actual_sha256": current,
                     "exact_bytes_equal": current == recorded["sha256"]})
    failures = [row["current"] for row in rows if not row["exact_bytes_equal"]]
    report = {"status": "PASS" if not failures else "FAIL", "files_checked": len(rows),
              "identical_files": len(rows) - len(failures), "failures": failures,
              "policy": "Exact byte identity is stronger than numeric equality. No metadata differences accepted silently.",
              "files": rows}
    (AUDIT / "migration_equivalence.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
