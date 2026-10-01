"""Prepare primary-evidenced cores in isolation; never promote unvalidated FE."""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
OUT = HERE / "candidate"

def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def main():
    master = read(CENTRAL / "model_master.json")
    sections = read(CENTRAL / "sections.json")
    audit = read(HERE / "WALL_CONTINUITY_BEFORE.json")
    exclusions = {r["element_id"]:r["before"] for r in read(ROOT / "entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json")["exclusions"]}
    candidates = {r["candidate_id"]:r for r in read(ROOT / "entregas/P1L6/current_cleanup/removed_wall_candidates.json")["candidates"]}
    elements = {r["element_id"]:r for r in master["elements"]}
    section_map = {r["section_id"]:r for r in sections["sections"]}
    nodes = {tuple(round(v,4) for v in r["coord_m"]):r["node_id"] for r in master["nodes"]}
    assert len(nodes)==len(master["nodes"])
    node_number = max(int(r["node_id"].split("-")[-1]) for r in master["nodes"])+1
    def node(point, owner):
        nonlocal node_number
        key=tuple(round(v,4) for v in point)
        if key not in nodes:
            nodes[key]=f"N-{node_number:05d}"
            node_number+=1
            master["nodes"].append({"node_id":nodes[key],"coord_m":list(key),"sources":[{"reason":"axis_registered_wall_endpoint","owner":owner}]})
        return nodes[key]
    targets=[]
    for group in audit["core_groups"]:
        for row in group["walls"]: targets.append((group["group"],row))
    # Long ED2 wall is evidenced on the top-floor CAD as well, without reflection.
    eid="E2-P4-M-010"
    c=candidates[eid]
    targets.append(("ED2_LONG_WALL_CAD_POSITION",{"id":eid,"geometry_axis_registered":{"start":c["geometry"]["start_xy_m"],"end":c["geometry"]["end_xy_m"],"thickness_m":c["geometry"]["thickness_m"]}}))
    changes=[]
    for group,row in targets:
        eid=row["id"]
        original=elements.get(eid)
        if original:
            element=original
            before=copy.deepcopy(element["geometry"])
            bottom,top=before["z_bottom_m"],before["z_top_m"]
            z=before["start_m"][2]
        else:
            c=candidates[eid]; src=exclusions[eid]
            assert c["primary_pair_audit"]["confirmed_pair"] and c["primary_pair_audit"]["pair_count"]==1,eid
            assert not c["active_duplicate"],eid
            # Externals are clues only. They must not supply lengths or thickness.
            before=None
            bottom,top=src["coordinates"]["z_bottom_m"],src["coordinates"]["z_top_m"]
            z=src["coordinates"]["start"][2]
            building=c["building"];floor=c["floor"]
            material="MAT_G35_10_2017_67_100_1E116" if building=="EDIFICIO_1" and floor!="P4" else "MAT_G35_10_2024_22_100_53994"
            element={"element_id":eid,"solidTag":src["solidTag"],"type":"wall","building":building,"floor":floor,"active":True,"material_id":material,"aliases":[],"merged_from":[],"merge_history":[],"analysis_id":None,"opensees_tag":None,"analysis_refs":[],"provenance":{"source_file":"entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json","source_dxf":src["source_dxf"],"source_layer":src["source_layer"],"sourceTags":src["sourceTags"],"confidence":src["confidence"],"primary_pair_audit":c["primary_pair_audit"],"external_repo_clue":[c[k]["id"] for k in ("santiago","caceres") if c[k]],"prior_exclusion_reason":c["previous_removal_reason"]}}
            if building=="EDIFICIO_1" and floor=="P4":
                element["provenance"]["material_scope"]="INFERRED_MATERIAL_FALLBACK_EXISTING_CURRENT_LAB_G35; NOT_PRIMARY_CONFIRMED_ED1_P4"
            master["elements"].append(element);elements[eid]=element
        g=row["geometry_axis_registered"]
        start=[round(float(v),3) for v in g["start"]]+[z]
        end=[round(float(v),3) for v in g["end"]]+[z]
        length=math.dist(start,end);thickness=g["thickness_m"]
        assert min(length,thickness,top-bottom)>0
        section_id=f"SEC_WALL_{thickness:.3f}x{length:.3f}"
        if section_id not in section_map:
            section={"section_id":section_id,"type":"wall_equivalent_rectangular","units":"m","dimensions":{"thickness_m":thickness,"length_m":round(length,4)},"status":"GEOMETRY_DERIVED_LENGTH","provenance":{"source_dxf":element["provenance"]["source_dxf"]},"used_by_count":0,"provenance_examples":[]}
            sections["sections"].append(section);section_map[section_id]=section
        element["section_id"]=section_id
        element["geometry"]={"kind":"linear_prism","start_m":start,"end_m":end,"center_m":[(a+b)/2 for a,b in zip(start,end)],"z_bottom_m":bottom,"z_top_m":top,"length_m":round(length,4),"direction_unit":[(b-a)/length for a,b in zip(start,end)],"orientation_deg_xy":math.degrees(math.atan2(end[1]-start[1],end[0]-start[0]))}
        element["nodes"]=[node(start,eid),node(end,eid)]
        element["provenance"]["core_group"]=group
        if before is None or before!=element["geometry"]:
            element["analysis_status"]="STALE_REANALYSIS_REQUIRED"
            element["provenance"]["axis_registration_evidence"]="entregas/P1L6/wall_continuity/WALL_CONTINUITY_BEFORE.json"
            changes.append({"element_id":eid,"group":group,"type":"RESTORED" if before is None else "AXIS_REGISTERED","before":before,"after":copy.deepcopy(element["geometry"]),"section_id":section_id,"material_id":element["material_id"]})
    counts=Counter(r["section_id"] for r in master["elements"] if r["active"])
    for s in sections["sections"]: s["used_by_count"]=counts[s["section_id"]]
    master.setdefault("geometry_revision_history",[]).append({"revision":"P1L6_CORE_CONTINUITY_CANDIDATE","status":"STALE_REANALYSIS_REQUIRED","changes":changes})
    write(OUT/"model_master.json",master);write(OUT/"sections.json",sections)
    write(OUT/"restoration_manifest.json",{"status":"CANDIDATE_NOT_PROMOTED","restored_count":sum(r["type"]=="RESTORED" for r in changes),"restored":[r for r in changes if r["type"]=="RESTORED"],"changes":changes,"material_limitation":"ED1/P4 retains explicit existing CURRENT G35 lab fallback, not new primary confirmation."})
    print(json.dumps({"changes":len(changes),"restored":sum(r["type"]=="RESTORED" for r in changes),"walls":sum(r["type"]=="wall" and r["active"] for r in master["elements"])},indent=2))

if __name__=="__main__": main()
