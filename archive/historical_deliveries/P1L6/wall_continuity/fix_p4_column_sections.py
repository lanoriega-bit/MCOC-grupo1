"""Explicit user-requested P4 section continuity; preserve identity and material."""
import copy
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/"entregas/P1L5/modelo_central"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    master=read(CENTRAL/"model_master.json");sections=read(CENTRAL/"sections.json")
    elements={e["element_id"]:e for e in master["elements"]};changes=[]
    for number in (4,7):
        eid=f"E2-P4-C-{number:03d}";below=f"E2-P3-C-{number:03d}"
        e=elements[eid];b=elements[below];before=copy.deepcopy(e)
        assert e["geometry"]["center_m"][:2]==b["geometry"]["center_m"][:2]
        assert b["section_id"]=="SEC_COLUMN_RECT_0.700x0.700"
        e["section_id"]=b["section_id"]
        e["analysis_status"]="STALE_REANALYSIS_REQUIRED"
        e["provenance"]["section_continuity_override"]={"reason":"EXPLICIT_USER_REQUEST_VERTICAL_STACK","primary_geometry_control":"same XY across all five floors","copied_from":below,"previous_section_id":before["section_id"],"status":"CONFIRMED_VERTICAL_CONTINUITY_USER_REVIEW","note":"Overrides earlier label assignment; does not assert a newly decoded CAD section label."}
        assert all(e[k]==before[k] for k in ("geometry","material_id","nodes","element_id","solidTag"))
        changes.append({"element_id":eid,"copied_from":below,"before_section":before["section_id"],"after_section":e["section_id"],"preserved":["XY","height","orientation","material","element_id"],"geometry":e["geometry"]})
    counts=Counter(e["section_id"] for e in master["elements"] if e["active"])
    for s in sections["sections"]:s["used_by_count"]=counts[s["section_id"]]
    master.setdefault("geometry_revision_history",[]).append({"revision":"E2_P4_COLUMN_SECTION_CONTINUITY","status":"STALE_REANALYSIS_REQUIRED","changes":changes})
    write(CENTRAL/"model_master.json",master);write(CENTRAL/"sections.json",sections)
    write(HERE/"COLUMN_SECTION_CORRECTIONS.json",{"status":"CORRECTED_RESULTS_STALE","changes":changes})
    print(json.dumps(changes,indent=2))
if __name__=="__main__":main()
