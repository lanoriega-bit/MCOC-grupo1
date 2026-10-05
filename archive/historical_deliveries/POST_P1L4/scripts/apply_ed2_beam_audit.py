#!/usr/bin/env python3
"""Aplica la propuesta primaria EXT-3 de vigas EDIFICIO_2."""
from __future__ import annotations
import copy,json,math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT/"entregas/P1L2/unity_export/model_2_viewer.json"
PROPOSAL=ROOT/"entregas/POST_P1L4/ed2_beams/ed2_beam_centerline_proposal.json"
OUT=ROOT/"entregas/POST_P1L4/ed2_beams/ed2_beam_resolution.json"
FLOORS=("S1","P1","P2","P3","P4")

def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def descriptor(x):
    a,b=x["start"][:2],x["end"][:2]; vx,vy=b[0]-a[0],b[1]-a[1]; L=math.hypot(vx,vy); u=[vx/L,vy/L]
    if u[0]<-1e-9 or (abs(u[0])<=1e-9 and u[1]<0):u=[-u[0],-u[1]]
    return a,b,u,L
def score(old,new):
    a,b,u,L=descriptor(old); c,d,v,N=descriptor(new); align=abs(u[0]*v[0]+u[1]*v[1])
    if align<.985:return None
    normal=[-v[1],v[0]]
    def project(p):q=[p[0]-c[0],p[1]-c[1]];return q[0]*v[0]+q[1]*v[1],q[0]*normal[0]+q[1]*normal[1]
    p1,n1=project(a);p2,n2=project(b);lo,hi=sorted((p1,p2));over=max(0,min(N,hi)-max(0,lo));perp=(abs(n1)+abs(n2))/2
    if over<min(.30,.45*N) or perp>.65:return None
    return (-over/N,perp,abs(L-N))
def fallback_score(old,new):
    """Preserva un ID cercano cuando el eje nuevo no solapa una cara antigua.

    Esto ocurre en vigas que el plano dibuja con una sola línea central o cuando
    el eje auditado queda entre dos caras. La geometría nunca se toma del
    candidato: solo se reutiliza su identificador histórico.
    """
    a,b,u,L=descriptor(old);c,d,v,N=descriptor(new)
    align=abs(u[0]*v[0]+u[1]*v[1])
    if align<.985:return None
    om=[(a[0]+b[0])/2,(a[1]+b[1])/2];nm=[(c[0]+d[0])/2,(c[1]+d[1])/2]
    return (math.hypot(om[0]-nm[0],om[1]-nm[1]),abs(L-N),-align)
def sections(props):
    result={}
    for p in props:
        height=p.get("height_m"); tags=[]
        if height is None:
            samples=[s for s in p.get("evidence_samples",[]) if s.get("label_match")]
            hs={float(s["nearest_label_height_m"]) for s in samples}
            if len(hs)==1:height=hs.pop();tags=sorted({s["nearest_label"] for s in samples})
        result[p["proposal_id"]]={"height_m":height,"tags":tags,"source":"CAD_CONTOUR_WIDTH+TEXT_LABEL" if height is not None else "CAD_CONTOUR_WIDTH_ONLY"}
    for p in props:
        row=result[p["proposal_id"]]
        if row["height_m"] is not None:continue
        refs=p.get("repeat_evidence",[])+p.get("component_label_evidence",[]); hs={result[r]["height_m"] for r in refs if r in result and result[r]["height_m"] is not None}
        if len(hs)==1:row["height_m"]=hs.pop();row["source"]="CAD_CONTOUR_WIDTH+INFERRED_CONFIRMED_FAMILY"
    return result
def main():
    proposal=load(PROPOSAL)
    if proposal.get("status")!="PROPOSAL_READY":raise RuntimeError("ED2 beam proposal is not ready")
    model=load(MODEL); old=[x for x in model["solids"] if x.get("category")=="beam"]; others=[x for x in model["solids"] if x.get("category")!="beam"]
    props=[copy.deepcopy(x) for f in FLOORS for x in proposal["floors"][f]["proposals"]]; sec=sections(props)
    if len(old)==len(props) and {x.get("sourceTag") for x in old}=={p["proposal_id"] for p in props}:
        print(json.dumps({"status":"ALREADY_APPLIED","beam_centerlines":len(old)},indent=2))
        return
    by_floor={f:[x for x in old if x.get("floor")==f] for f in FLOORS}; used=set(); new=[]; crosswalk=[]
    for p in props:
        proxy={"start":p["start"],"end":p["end"]}; ranked=[]
        for x in by_floor[p["floor"]]:
            if x["solidTag"] in used:continue
            s=score(x,proxy)
            if s is not None:ranked.append((s,str(x["solidTag"]),x))
        match_method="GEOMETRIC_OVERLAP"
        if not ranked:
            fallback=[]
            for x in by_floor[p["floor"]]:
                if x["solidTag"] in used:continue
                s=fallback_score(x,proxy)
                if s is not None:fallback.append((s,str(x["solidTag"]),x))
            if not fallback:raise RuntimeError(f"No historical beam ID for {p['proposal_id']}")
            template=min(fallback,key=lambda x:(x[0],x[1]))[2]
            match_method="NEAREST_PARALLEL_ID_ONLY"
        else:template=min(ranked,key=lambda x:(x[0],x[1]))[2]
        used.add(template["solidTag"])
        section=sec[p["proposal_id"]]; h=section["height_m"] if section["height_m"] is not None else .60
        top=sum(float(x["start"][2])+float(x["height_m"])/2 for x in by_floor[p["floor"]])/len(by_floor[p["floor"]]);z=top-h/2
        beam=copy.deepcopy(template);beam.update({"start":[p["start"][0],p["start"][1],z],"end":[p["end"][0],p["end"][1],z],"width_m":p["width_m"],"height_m":h,"length_m":p["length_m"],"section_width_m":p["width_m"],"section_height_m":section["height_m"],"section_source":section["source"],"section_confidence":"CONFIRMED_FROM_PLAN" if section["height_m"] is not None else "WIDTH_CONFIRMED_HEIGHT_UNKNOWN","sourceTag":p["proposal_id"],"sourceTags":p["face_ids"],"source_layer":"RLE-VIGA_CONTOUR_CENTERLINE","confidence":"confirmed_from_RLE_VIGA_geometry","geometry_confirmation":{"status":p["classification"],"proposal_file":str(PROPOSAL.relative_to(ROOT)).replace("\\","/"),"face_ids":p["face_ids"],"width_m":p["width_m"]},"post_p1l4_correction":{"correction_type":"MERGED","reason":"Caras y cierres RLE-VIGA consolidados en una centrolinea física.","primary_source":"2024_22-101.dxf" if p["floor"]!="P4" else "2024_22-102.dxf","external_repo_clue":"SECONDARY_COMPARISON_ONLY","confidence":"HIGH_PRIMARY_SOURCE","results_compatibility":"P1L4_HISTORICAL_RESULTS_NOT_RECALCULATED"}})
        new.append(beam);crosswalk.append({"proposal_id":p["proposal_id"],"new_solidTag":beam["solidTag"],"old_preserved_id":beam.get("id"),"historical_id_match_method":match_method,"source_face_ids":p["face_ids"],"section_width_m":p["width_m"],"section_height_m":section["height_m"]})
    model["solids"]=others+new;model["beam_consolidation"]={"status":"APPLIED_POST_P1L4","proposal_file":str(PROPOSAL.relative_to(ROOT)).replace("\\","/"),"old_beam_prisms":len(old),"new_beam_centerlines":len(new),"removed_contour_faces_or_details":len(old)-len(new),"results_policy":"P1L4 historical results unchanged"}
    model.setdefault("notes",[]).append("POST-P1L4 EXT-3: EDIFICIO_2 beam contours consolidated; OpenSees results remain historical.")
    write(MODEL,model);result={"status":"PASS","old_beam_prisms":len(old),"new_beam_centerlines":len(new),"removed_contour_faces_or_details":len(old)-len(new),"new_beams_by_floor":dict(Counter(x["floor"] for x in new)),"known_section_heights":sum(x["section_height_m"] is not None for x in new),"unknown_section_heights":sum(x["section_height_m"] is None for x in new),"crosswalk":crosswalk,"opensees_results_recalculated":False};write(OUT,result);print(json.dumps({k:v for k,v in result.items() if k!="crosswalk"},indent=2))
if __name__=="__main__":main()
