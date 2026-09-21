#!/usr/bin/env python3
"""Consolida EXT-4 sin aplicar losas candidatas ni ejecutar OpenSees."""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union

FLOORS=("S1","P1","P2","P3","P4");BUILDINGS=("EDIFICIO_1","EDIFICIO_2")
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def orient(p,t):
    x,y=p;q={"IDENTITY":(x,y),"ROT90":(-y,x),"ROT180":(-x,-y),"ROT270":(y,-x),"REFLECT_X":(-x,y),"REFLECT_Y":(x,-y),"SWAP_XY":(y,x),"SWAP_NEG_XY":(-y,-x)}[t["orientation"]]
    return (q[0]+t["dx_m"],q[1]+t["dy_m"])
def external_santiago(path,transforms):
    d=load(path);fm={"CIELO_1S":"S1","CIELO_1":"P1","CIELO_2":"P2","CIELO_3":"P3","CIELO_4":"P4"};groups=defaultdict(list)
    for s in d["slabs"]:
        floor=fm.get(s.get("nivel"));cx=(float(s["x0"])+float(s["x1"]))/2;building="EDIFICIO_2" if cx<-20 else "EDIFICIO_1"
        if not floor:continue
        raw=[(s["x0"],s["y0"]),(s["x1"],s["y0"]),(s["x1"],s["y1"]),(s["x0"],s["y1"])]
        groups[(building,floor)].append(Polygon([orient(p,transforms[building]) for p in raw]))
    return {k:unary_union(v) for k,v in groups.items()}
def external_caceres(path,transforms):
    d=load(path);zmap={3.96:"S1",7.92:"P1",11.88:"P2",15.84:"P3",19.80:"P4"};groups=defaultdict(list)
    for s in d["slabs"]:
        pts=[(float(p["x_m"]),float(p["y_m"])) for p in s["coordinates"]];cx=sum(p[0] for p in pts)/len(pts);building="EDIFICIO_2" if cx<-20 else "EDIFICIO_1";z=min(zmap,key=lambda v:abs(v-float(s["z_m"])));floor=zmap[z]
        groups[(building,floor)].append(Polygon([orient(p,transforms[building]) for p in pts]))
    return {k:unary_union(v) for k,v in groups.items()}
def candidate_polygons(root):
    a=load(root/"entregas/P1L2/edificio/validacion/slabs/ed1_outline_proposal/ed1_slab_outline_proposal.json");b=load(root/"entregas/P1L2/edificio/validacion/slabs/ed2_outline_proposal/ed2_slab_outline_proposal.json");out={}
    for building,data in (("EDIFICIO_1",a),("EDIFICIO_2",b)):
        for floor,row in data["floors"].items():
            out[(building,floor)]={"polygon":Polygon(row["outline_xy"]) if row.get("outline_xy") else None,"area_m2":row.get("area_m2"),"status":row.get("status",data.get("status","CANDIDATE")),"source_sheet":row.get("source_sheet"),"confidence_counts":row.get("confidence_counts",{})}
    return out
def comp(candidate,external):
    if not candidate or not external or external.is_empty:return None
    inter=candidate.intersection(external).area;union=candidate.union(external).area
    return {"external_area_m2":round(external.area,3),"intersection_m2":round(inter,3),"iou":round(inter/union,4) if union else 0.0,"candidate_coverage_by_external_percent":round(100*inter/candidate.area,2) if candidate.area else 0.0}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--santiago",type=Path,required=True);ap.add_argument("--caceres",type=Path,required=True);args=ap.parse_args();root=Path(__file__).resolve().parents[3];out=root/"entregas/POST_P1L4"
    master=load(out/"STRUCTURAL_CROSS_REPO_COMPARISON.json");transforms=master["normalization"]["transforms"]
    ours=candidate_polygons(root);s=external_santiago(args.santiago/"P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json",transforms["SANTIAGO"]);c=external_caceres(args.caceres/"Edificio/results/modelo_3d_manual.json",transforms["CACERES"])
    floors=[]
    for building in BUILDINGS:
        for floor in FLOORS:
            row=ours.get((building,floor));poly=row["polygon"] if row else None
            floors.append({"building":building,"floor":floor,"our_status":row["status"] if row else "UNRESOLVED_NO_OUTLINE","our_candidate_area_m2":round(poly.area,3) if poly else row.get("area_m2") if row else None,"source_sheet":row.get("source_sheet") if row else None,"edge_confidence":row.get("confidence_counts") if row else {},"santiago":comp(poly,s.get((building,floor))),"caceres":comp(poly,c.get((building,floor))),"holes_policy":"NOT_CLASSIFIED_AS_HOLES","action":"KEEP_VISUAL_PILOT_ONLY" if row and row["status"]=="FROZEN_APPROVED_PILOT" else "DO_NOT_APPLY"})
    model=load(root/"entregas/P1L2/unity_export/model_combined_viewer.json");solids=model["solids"]
    props={"beam":{},"column":{},"wall":{},"slab":{}}
    for cat in props:
        rows=[x for x in solids if x.get("category")==cat]
        props[cat]={"total":len(rows),"material_unknown":sum(str(x.get("material","UNKNOWN")).upper() in ("UNKNOWN","") for x in rows),"section_confirmed":sum(str(x.get("section_confidence","")).startswith("CONFIRMED") for x in rows),"section_unknown":sum(x.get("section_height_m") is None and cat in ("beam","column") for x in rows),"visual_only":sum(x.get("participates_in_FE") is False or x.get("confidence")=="low" for x in rows)}
    cad=load(root/"entregas/P1L2/edificio/datos/cad_property_audit.json");conn=load(root/"entregas/P1L2/edificio/validacion/fe_connectivity_post_geometry/connectivity_comparison.json");candidate=load(root/"entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json")
    payload={"status":"PASS_WITH_REVIEW_REQUIRED","scope":"EXT-4_SLABS_PROPERTIES_CONNECTIVITY","slabs":{"policy":"PROPOSALS_NOT_APPLIED","floors":floors,"reason":"ED1 S1/P1 lack a defensible outer perimeter; internal RLE-LOSA features are not proven holes; external agreement is secondary only."},"properties":{"model_summary":props,"cad_labels_reviewed":cad.get("summary",{}),"policy":"Do not promote nearest-neighbor associations without direct visual/plan confirmation."},"connectivity":{"historic_adapter":conn["current_in_memory"],"candidate":candidate["qa"],"status":candidate["status"],"opensees_run":False},"results_policy":"P1L4_HISTORICAL_RESULTS_UNCHANGED"}
    (out/"EXT_4_SLABS_PROPERTIES_CONNECTIVITY.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":payload["status"],"slab_floors":len(floors),"properties":props,"connectivity":{"baseline_floating":conn["current_in_memory"]["floating_elements"],"candidate_floating":candidate["qa"]["candidate_floating_geometry_elements"],"candidate_components":candidate["qa"]["candidate_floating_components"]}},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
