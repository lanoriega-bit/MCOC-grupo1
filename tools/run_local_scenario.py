"""Desktop scenario worker. Writes ONLY under ignored results/scenarios/.

--fingerprint prints the current read-only base identity. --preview clips/maps
without OpenSees. No canonical export, no base invalidation, no AR access.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis.opensees.local_scenarios import digest, execute, fingerprint, read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args()
    if args.fingerprint:
        print(digest(fingerprint()))
        return
    directory = ROOT / "results/scenarios"
    path = args.request.resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError("Scenario requests must reside under results/scenarios/")
    request = read(path)
    scenario_id = request["scenario_id"]
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", scenario_id):
        raise ValueError("Invalid scenario ID")
    output = directory / (scenario_id + ("_preview.json" if args.preview else "_result.json"))
    try:
        result = execute(request, preview=args.preview)
        code = 0
    except Exception as error:
        result = {"status": "FAIL", "scenario_id": scenario_id, "error": str(error)}
        code = 1
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "file": str(output.relative_to(ROOT))}))
    return code


if __name__ == "__main__":
    sys.exit(main())
