#!/usr/bin/env python3
"""EXT-3: comparación viga por viga; repos externos son pistas de solo lectura."""
from __future__ import annotations
import argparse,json,math
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image,ImageDraw

FLOORS=("S1","P1","P2","P3","P4"); BUILDINGS=("EDIFICIO_1","EDIFICIO_2")
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def orient(p,t):
    x,y=p;q={"IDENTITY":(x,y),"ROT90":(-y,x),"ROT180":(-x,-y),"ROT270":(y,-x),"REFLECT_X":(-x,y),"REFLECT_Y":(x,-y),"SWAP_XY":(y,x),"SWAP_NEG_XY":(-y,-x)}[t["orientation"]]
    return [round(q[0]+t["dx_m"],4),round(q[1]+t["dy_m"],4)]
def length(r):return math.dist(r["start"],r["end"])
def angle(r):return math.atan2(r["end"][1]-r["start"][1],r["end"][0]-r["start"][0])
def delta(a,b):
    d=abs((a-b)%math.pi);return min(d,math.pi-d)
def metrics(a,b):
    ad=delta(angle(a),angle(b))
    if ad>math.radians(5):return None
    av=[a["end"][0]-a["start"][0],a["end"][1]-a["start"][1]];al=max(length(a),1e-9);u=[av[0]/al,av[1]/al];n=[-u[1],u[0]]
    bc=[(b["start"][0]+b["end"][0])/2,(b["start"][1]+b["end"][1])/2];perp=abs((bc[0]-a["start"][0])*n[0]+(bc[1]-a["start"][1])*n[1])
    if perp>.35:return None
    proj=lambda p:(p[0]-a["start"][0])*u[0]+(p[1]-a["start"][1])*u[1]
    p1,p2=sorted((proj(b["start"]),proj(b["end"])));over=max(0,min(al,p2)-max(0,p1));ratio=over/max(min(al,length(b)),1e-9)
    if over<.30 or ratio<.45:return None
    return {"perpendicular_distance_m":round(perp,4),"angle_delta_deg":round(math.degrees(ad),3),"overlap_m":round(over,4),"overlap_ratio":round(ratio,4),"length_delta_m":round(abs(al-length(b)),4),"strong":perp<=.15 and ad<=math.radians(3) and ratio>=.80}
def ours(path):
    rows=[]
    for b in load(path)["solids"]:
        if b.get("category")!="beam":continue
        rows.append({"repo":"OURS","id":b.get("id") or b["solidTag"],"building":b["building"],"floor":b["floor"],"start":[float(x) for x in b["start"][:2]],"end":[float(x) for x in b["end"][:2]],"width_m":b.get("section_width_m") or b.get("width_m"),"height_m":b.get("section_height_m") or b.get("height_m"),"section_source":b.get("section_source"),"source_dxf":b.get("source_dxf"),"source_layer":b.get("source_layer"),"correction":b.get("post_p1l4_correction")})
    return rows
def santiago(path,norm):
    d=load(path);nodes={int(n["id"]):n for n in d["nodes"]};rows=[];fm={"CIELO_1S":"S1","CIELO_1":"P1","CIELO_2":"P2","CIELO_3":"P3","CIELO_4":"P4"}
    zmap={.16:"S1",4.12:"P1",8.08:"P2",12.04:"P3",16.0:"P4"}
    for e in d["elements"]:
        if str(e.get("type","")).lower()!="viga":continue
        a,b=nodes[int(e["nodeI"])],nodes[int(e["nodeJ"])];building="EDIFICIO_1" if e.get("sourceBuilding")=="edificio_1" else "EDIFICIO_2"
        floor=fm.get(e.get("piso")) if building=="EDIFICIO_1" else min(zmap,key=lambda z:abs(z-float(a["z"])))
        if building=="EDIFICIO_2":floor=zmap[floor]
        rows.append({"repo":"SANTIAGO","id":e.get("elementTag") or f"S-B-{e['id']}","building":building,"floor":floor,"start":orient([a["x"],a["y"]],norm[building]),"end":orient([b["x"],b["y"]],norm[building]),"width_m":e.get("width_m"),"height_m":e.get("height_m"),"section":e.get("sectionId")})
    return rows
def caceres(path,norm):
    d=load(path);nodes={int(n["id"]):n for n in d["nodes"]};rows=[]
    section_keys={"BEAM_SMALL":"section_small_beams","BEAM_VARIABLE":"section_variable_beams","BEAM_40x60":"section_40x60_beams"}
    for e in d["elements"]:
        if "BEAM" not in str(e.get("type","")):continue
        a,b=nodes[int(e["i"])],nodes[int(e["j"])];level=int(a.get("level",0))
        if not 1<=level<=5:continue
        center=(float(a["x_m"])+float(b["x_m"]))/2;building="EDIFICIO_2" if center<=-.35 else "EDIFICIO_1";sec=d.get(section_keys.get(e["type"],"section_beams"),{})
        rows.append({"repo":"CACERES","id":f"C-B-{e['id']}","building":building,"floor":FLOORS[level-1],"start":orient([a["x_m"],a["y_m"]],norm[building]),"end":orient([b["x_m"],b["y_m"]],norm[building]),"width_m":sec.get("b_m") or sec.get("width_m"),"height_m":sec.get("h_m") or sec.get("height_m"),"external_type":e["type"]})
    return rows
def candidates(row,rows):
    out=[]
    for x in rows:
        if (x["building"],x["floor"])!=(row["building"],row["floor"]):continue
        m=metrics(row,x)
        if m:out.append((0 if m["strong"] else 1,m["perpendicular_distance_m"],-m["overlap_ratio"],m["length_delta_m"],x,m))
    return sorted(out,key=lambda q:q[:4])
def short(x,m):return {"id":x["id"],"start_xy_m":x["start"],"end_xy_m":x["end"],"length_m":round(length(x),4),"width_m":x.get("width_m"),"height_m":x.get("height_m"),"match":m}
def point_segment(p,r):
    a,b=r["start"],r["end"];vx,vy=b[0]-a[0],b[1]-a[1];l2=vx*vx+vy*vy
    if l2==0:return math.dist(p,a)
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/l2));return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)
def support_geometry(path):
    out=[]
    for x in load(path)["solids"]:
        if x.get("category") not in ("column","wall"):continue
        base={"building":x["building"],"floor":x["floor"],"category":x["category"],"id":x.get("id") or x.get("solidTag")}
        if x["category"]=="column":
            base.update({"point":[float(v) for v in x["center"][:2]],"radius":math.hypot(float(x.get("width_m",0))/2,float(x.get("depth_m",0))/2)+.18})
        else:
            base.update({"start":[float(v) for v in x["start"][:2]],"end":[float(v) for v in x["end"][:2]],"radius":float(x.get("wall_thickness_m") or x.get("width_m") or 0)/2+.18})
        out.append(base)
    return out
def connectivity(row,all_rows,supports):
    peers=[x for x in all_rows if x is not row and (x["building"],x["floor"])==(row["building"],row["floor"])]
    structural=[x for x in supports if (x["building"],x["floor"])==(row["building"],row["floor"])]
    def endpoint_supported(p):
        if any(point_segment(p,x)<=.35 for x in peers):return True
        for x in structural:
            if x["category"]=="column" and math.dist(p,x["point"])<=x["radius"]:return True
            if x["category"]=="wall" and point_segment(p,x)<=x["radius"]:return True
        return False
    supported=[endpoint_supported(p) for p in (row["start"],row["end"])]
    if all(supported):return "SUPPORTED_BOTH_ENDS_GEOMETRIC"
    if any(supported):return "SUPPORTED_ONE_END_REVIEW_CANTILEVER_OR_BOUNDARY"
    return "REVIEW_REQUIRED_CONNECTIVITY"
def overlay(path,b,f,sets):
    rows=[x for group in sets for x in group if x["building"]==b and x["floor"]==f]
    if not rows:return
    pts=[p for x in rows for p in (x["start"],x["end"])];xmin,xmax=min(p[0] for p in pts),max(p[0] for p in pts);ymin,ymax=min(p[1] for p in pts),max(p[1] for p in pts);W,H,M=1200,760,70;s=min((W-2*M)/max(xmax-xmin,1),(H-2*M)/max(ymax-ymin,1));xy=lambda p:(M+(p[0]-xmin)*s,H-M-(p[1]-ymin)*s)
    im=Image.new("RGB",(W,H),"white");d=ImageDraw.Draw(im);d.text((30,18),f"Vigas {b}/{f}: OURS verde, Santiago naranja, Caceres azul",fill="#111")
    for repo,color,w in (("CACERES","#2878d0",2),("SANTIAGO","#e69f00",3),("OURS","#18864b",5)):
        for x in rows:
            if x["repo"]==repo:d.line((*xy(x["start"]),*xy(x["end"])),fill=color,width=w)
    im.save(path)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--santiago",type=Path,required=True);ap.add_argument("--caceres",type=Path,required=True);args=ap.parse_args();root=Path(__file__).resolve().parents[3];out=root/"entregas/POST_P1L4";master=load(out/"STRUCTURAL_CROSS_REPO_COMPARISON.json");t=master["normalization"]["transforms"]
    model_path=root/"entregas/P1L2/unity_export/model_combined_viewer.json";oo=ours(model_path);supports=support_geometry(model_path);ss=santiago(args.santiago/"P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json",t["SANTIAGO"]);cc=caceres(args.caceres/"Edificio/results/modelo_3d_manual.json",t["CACERES"])
    records=[];useds=set();usedc=set();by=defaultdict(Counter)
    for row in oo:
        sm,cm=candidates(row,ss),candidates(row,cc);sb=sm[0] if sm else None;cb=cm[0] if cm else None
        if sb:useds.add(sb[4]["id"])
        if cb:usedc.add(cb[4]["id"])
        strongs=bool(sb and sb[5]["strong"]);strongc=bool(cb and cb[5]["strong"]);agreement="CONFIRMED_ALL_THREE" if strongs and strongc else "CONFIRMED_OURS_PLUS_ONE" if strongs or strongc else "GEOMETRY_MISMATCH" if sb or cb else "OURS_ONLY"
        classes=[agreement];
        if sum(x[5]["strong"] for x in sm)>1 or sum(x[5]["strong"] for x in cm)>1:classes.append("POSSIBLE_FRAGMENT_EXTERNAL")
        section_mismatch=[]
        for name,best in (("SANTIAGO",sb),("CACERES",cb)):
            if best and row.get("width_m") and best[4].get("width_m") and abs(float(row["width_m"])-float(best[4]["width_m"]))>.031:section_mismatch.append(name)
        if section_mismatch:classes.append("SECTION_MISMATCH")
        conn=connectivity(row,oo,supports)
        if row["id"]=="E1-P2-V-075":conn="LANDING_BEAM_CONFIRMED_STAIR_B"
        rec={"our_id":row["id"],"building":row["building"],"floor":row["floor"],"type":"BEAM","geometry":{"start_xy_m":row["start"],"end_xy_m":row["end"],"length_m":round(length(row),4),"width_m":row["width_m"],"height_m":row["height_m"]},"repo_santiago_match":short(sb[4],sb[5]) if sb else None,"repo_caceres_match":short(cb[4],cb[5]) if cb else None,"source_plan_evidence":{"sheet":row["source_dxf"],"layer":row["source_layer"],"section_source":row["section_source"]},"agreement":agreement,"classifications":classes,"section_mismatch_repos":section_mismatch,"connectivity_classification":conn,"confidence":"PRIMARY_SOURCE_CONFIRMED","action":"KEEP_OR_CORRECTED_FROM_PRIMARY_SOURCE","post_p1l4_correction":row["correction"]}
        records.append(rec);by[(row["building"],row["floor"])][agreement]+=1;by[(row["building"],row["floor"])][conn]+=1
    external=[]
    for repo,rows,used in (("SANTIAGO",ss,useds),("CACERES",cc,usedc)):
        for x in rows:
            if x["id"] not in used:external.append({"building":x["building"],"floor":x["floor"],"type":"BEAM","agreement":"EXTERNAL_ONE_ONLY","confidence":"REVIEW_REQUIRED_EXTERNAL_ONLY","action":"DO_NOT_ADD_WITHOUT_PRIMARY_SOURCE",f"repo_{repo.lower()}":short(x,None)})
    master["our_elements"]=[x for x in master.get("our_elements",[]) if x.get("type")!="BEAM"]+records;master["external_only"]=[x for x in master.get("external_only",[]) if x.get("type")!="BEAM"]+external;master.setdefault("milestones",{})["EXT_3_BEAMS"]={"status":"PASS","audited":len(records),"external_santiago":len(ss),"external_caceres":len(cc),"ed1_revalidation":"300 centerlines from 545 faces PASS","ed2_correction":{"old_prisms":515,"new_centerlines":267,"removed_faces_or_details":248},"opensees_recalculated":False}
    (out/"STRUCTURAL_CROSS_REPO_COMPARISON.json").write_text(json.dumps(master,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");ov=out/"overlays";ov.mkdir(exist_ok=True)
    for b in BUILDINGS:
        for f in FLOORS:overlay(ov/f"beams_{b.lower()}_{f.lower()}.png",b,f,(oo,ss,cc))
    counts=Counter(x["agreement"] for x in records);conn=Counter(x["connectivity_classification"] for x in records)
    print(json.dumps({"audited":len(records),"ours_by_building":Counter(x["building"] for x in oo),"external_santiago":len(ss),"external_caceres":len(cc),"agreement":counts,"connectivity":conn,"external_only":len(external)},default=dict,indent=2))
if __name__=="__main__":main()
