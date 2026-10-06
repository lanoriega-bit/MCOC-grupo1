"""Fail if this visual revision changed any physical input/result or CURRENT JSON."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
BASE="d3ee850"
PROTECTED=["entregas/P1L5/modelo_central", "entregas/P1L5/analysis",
           "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets",
           "entregas/P1L2/unity_export", "entregas/P1L4"]


def main():
    checks={}
    for path in PROTECTED:
        changed=subprocess.check_output(["git","diff","--name-only",BASE,"--",path],cwd=ROOT)
        checks["unchanged: "+path]=not changed
    checks["P1L4_FINAL unchanged"]=subprocess.check_output(["git","rev-parse","P1L4_FINAL^{}"],cwd=ROOT,text=True).strip()=="56e24ac0568b24eba3cf119f2e3cc66fc0af3a35"
    report={"status":"PASS" if all(checks.values()) else "FAIL","baseline":BASE,"checks":checks}
    (Path(__file__).parent/"VISUAL_SCOPE_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
