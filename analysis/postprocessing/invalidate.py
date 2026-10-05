"""Fail closed before regeneration and after any pipeline failure."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT_CONFIG = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8-sig"))
STREAM = ROOT / PROJECT_CONFIG["paths"]["unity"] / "Assets" / "StreamingAssets"


def main():
    path = STREAM / "current_dataset_contract.json"
    contract = json.loads(path.read_text(encoding="utf-8-sig"))
    contract["status"] = "STALE_REANALYSIS_REQUIRED"
    contract["analysis_available"] = False
    contract["week7_failure_policy"] = "Only a fully successful regeneration may expose CURRENT results."
    path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("CURRENT invalidated; regeneration/QA required")


if __name__ == "__main__":
    main()
