"""Promote only a validated, exact-scope candidate and invalidate results first."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/"entregas/P1L5/modelo_central"
STREAM=ROOT/"entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    folder=HERE/"candidate"
    qa=read(folder/"candidate_qa.json")
    analysis=read(folder/"results/current/manifest.json")
    manifest=read(folder/"restoration_manifest.json")
    live=read(CENTRAL/"model_master.json");candidate=read(folder/"model_master.json")
    assert qa["status"]=="PASS" and not qa["floating_components"] and not qa["fe_components_without_support"]
    assert analysis["status"]=="PASS" and manifest["restored_count"]==30
    old={e["element_id"]:e for e in live["elements"]};new={e["element_id"]:e for e in candidate["elements"]}
    assert not set(old)-set(new)
    expected={r["element_id"] for r in manifest["restored"]}
    assert set(new)-set(old)==expected
    changed={r["element_id"] for r in manifest["changes"]}
    for eid,e in old.items():
        assert e["type"]=="wall" or all(new[eid][k]==e[k] for k in ("geometry","section_id","material_id","nodes")),eid
        if eid not in changed: assert new[eid]["geometry"]==e["geometry"],eid
    reference=ROOT/"entregas/P1L2/unity_export/model_viewer.json"
    original_sha=hashlib.sha256(reference.read_bytes()).hexdigest()
    write(HERE/"BASELINE_ANALYSIS.json",read(ROOT/"entregas/P1L5/analysis/results/current/manifest.json"))
    contract=read(STREAM/"current_dataset_contract.json")
    contract.update(status="STALE_REANALYSIS_REQUIRED",analysis_available=False,fe_approved=False,loads_approved=False)
    write(STREAM/"current_dataset_contract.json",contract)
    candidate["sources"]["current_contract"].update(status="STALE_REANALYSIS_REQUIRED",analysis_version="NONE_REANALYSIS_REQUIRED")
    for e in candidate["elements"]:
        if e["type"] in ("beam","column","wall"):e["analysis_status"]="STALE_REANALYSIS_REQUIRED"
    write(CENTRAL/"model_master.json",candidate);write(CENTRAL/"sections.json",read(folder/"sections.json"))
    for name in ("validate_central_model.py","build_central_derivatives.py","sync_current_model_to_viewers.py"):
        subprocess.run([sys.executable,str(CENTRAL/name)],check=True,cwd=ROOT)
    assert hashlib.sha256(reference.read_bytes()).hexdigest()==original_sha
    write(HERE/"PROMOTED_CORES.json",{**manifest,"status":"PROMOTED_RESULTS_STALE","isolated_FE_QA":qa,"isolated_analysis":analysis,"LUIS_REFERENCE_FILES_MODIFIED":0})
    print("PROMOTED: 30 restored walls, 4 registered existing walls; results STALE")
if __name__=="__main__":main()
