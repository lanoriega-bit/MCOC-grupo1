"""Record a prefix relocation without changing protected baseline hashes."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old")
    parser.add_argument("new")
    args = parser.parse_args()
    target = ROOT / "reports/repository_architecture_audit/path_mapping.json"
    mapping = json.loads(target.read_text(encoding="utf-8"))
    baseline = json.loads((target.parent / "baseline.json").read_text(encoding="utf-8"))
    for original in baseline:
        relative = mapping.get(original, original)
        if relative == args.old or relative.startswith(args.old + "/"):
            mapping[original] = args.new + relative[len(args.old):]
    target.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recorded relocation:", args.old, "->", args.new)

if __name__ == "__main__":
    main()
