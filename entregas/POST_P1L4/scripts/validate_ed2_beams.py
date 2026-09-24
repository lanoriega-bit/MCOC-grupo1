#!/usr/bin/env python3
"""Validación reproducible del checkpoint EXT-3 de vigas EDIFICIO_2."""
from __future__ import annotations
import json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def main():
    proposal=load(ROOT/"entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json")
    resolution=load(ROOT/"entregas/POST_P1L4/ed2_beams/ed2_beam_resolution.json")
    model=load(ROOT/"entregas/P1L2/unity_export/model_2_viewer.json")
    beams=[x for x in model["solids"] if x.get("category")=="beam"]
    expected={"S1":44,"P1":44,"P2":44,"P3":44,"P4":91};actual=Counter(x["floor"] for x in beams)
    checks={
        "proposal_ready":proposal.get("status")=="PROPOSAL_READY",
        "resolution_pass":resolution.get("status")=="PASS",
        "beam_count_267":len(beams)==267,
        "counts_by_floor":dict(actual)==expected,
        "all_sections_confirmed":all(x.get("section_width_m") and x.get("section_height_m") for x in beams),
        "unique_ids":len({x["solidTag"] for x in beams})==len(beams),
        "all_primary_traceable":all(x.get("source_dxf") in ("2024_22-101.dxf","2024_22-102.dxf") and x.get("sourceTags") for x in beams),
        "no_opensees_recalculation":resolution.get("opensees_results_recalculated") is False,
    }
    special=next((x for x in beams if x.get("sourceTag")=="P4-VP-085"),None)
    checks["v050_v051_one_v60x80"] = bool(special and abs(special["width_m"]-.60)<1e-6 and abs(special["height_m"]-.80)<1e-6 and len(special["sourceTags"])==2)
    status="PASS" if all(checks.values()) else "FAIL"
    report={"status":status,"checks":checks,"counts":{"total":len(beams),"by_floor":dict(actual),"known_sections":sum(bool(x.get("section_height_m")) for x in beams)},"special_E2_P4_V050_V051":{"verdict":"TWO_FACES_OF_ONE_REAL_BEAM_V60x80","result_id":special.get("id") if special else None,"proposal_id":"P4-VP-085"},"opensees_results_recalculated":False}
    out=ROOT/"entregas/POST_P1L4/ed2_beams/VALIDATION.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ED2_BEAM_VALIDATION:",status);print(json.dumps(report,ensure_ascii=False,indent=2))
    if status!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
