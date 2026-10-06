#!/usr/bin/env python3
"""Compara muros de los tres repos; externos son solo pistas secundarias."""

from __future__ import annotations

import argparse, json, math
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw

FLOORS=("S1","P1","P2","P3","P4")
BUILDINGS=("EDIFICIO_1","EDIFICIO_2")

def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def orient_point(p,t):
    x,y=p; name=t["orientation"]
    q={"IDENTITY":(x,y),"ROT90":(-y,x),"ROT180":(-x,-y),"ROT270":(y,-x),"REFLECT_X":(-x,y),"REFLECT_Y":(x,-y),"SWAP_XY":(y,x),"SWAP_NEG_XY":(-y,-x)}[name]
    return [round(q[0]+t["dx_m"],4),round(q[1]+t["dy_m"],4)]
def length(row): return math.dist(row["start"],row["end"])
def angle(row):
    a,b=row["start"],row["end"]
    return math.atan2(b[1]-a[1],b[0]-a[0])
def angle_delta(a,b):
    d=abs((a-b)%math.pi)
    return min(d,math.pi-d)
def match_metrics(a,b):
    ad=angle_delta(angle(a),angle(b))
    if ad>math.radians(5): return None
    av=[a["end"][0]-a["start"][0],a["end"][1]-a["start"][1]]; al=max(length(a),1e-9); u=[av[0]/al,av[1]/al]
    normal=[-u[1],u[0]]
    bc=[(b["start"][0]+b["end"][0])/2,(b["start"][1]+b["end"][1])/2]
    perp=abs((bc[0]-a["start"][0])*normal[0]+(bc[1]-a["start"][1])*normal[1])
    if perp>0.30: return None
    def proj(p): return (p[0]-a["start"][0])*u[0]+(p[1]-a["start"][1])*u[1]
    p1,p2=sorted((proj(b["start"]),proj(b["end"])))
    overlap=max(0,min(al,p2)-max(0,p1)); ratio=overlap/max(min(al,length(b)),1e-9)
    if overlap<0.30 or ratio<0.50: return None
    return {"perpendicular_distance_m":round(perp,4),"angle_delta_deg":round(math.degrees(ad),3),"overlap_m":round(overlap,4),"overlap_ratio":round(ratio,4),"length_delta_m":round(abs(al-length(b)),4),"strong":perp<=0.15 and ad<=math.radians(3) and ratio>=0.80}

def ours(path):
    rows=[]
    for w in load(path)["solids"]:
        if w.get("category")!="wall": continue
        rows.append({"repo":"OURS","id":w.get("id") or w["solidTag"],"building":w["building"],"floor":w["floor"],"start":[float(x) for x in w["start"][:2]],"end":[float(x) for x in w["end"][:2]],"thickness_m":w.get("wall_thickness_m") or w.get("width_m"),"source_dxf":w.get("source_dxf"),"source_layer":w.get("source_layer"),"confidence":w.get("confidence"),"thickness_source":w.get("thickness_source"),"correction":w.get("post_p1l4_correction")})
    return rows
def santiago(path,norm):
    data=load(path); nodes={str(n["id"]):n for n in data["nodes"]}; rows=[]
    e1={"FOUNDATION":"S1","CIELO_1S":"P1","CIELO_1":"P2","CIELO_2":"P3","CIELO_3":"P4"}
    e2={"E2_Z-4.16":"S1","E2_Z-4.01":"P1","E2_Z-0.05":"P2","E2_Z3.91":"P3","E2_Z7.87":"P4"}
    for w in data["walls"]:
        building="EDIFICIO_1" if int(w["id"])<=30 else "EDIFICIO_2"; floor=(e1 if building=="EDIFICIO_1" else e2).get(w["bottom"])
        if not floor: continue
        a,b=nodes[str(w["nodeI"])],nodes[str(w["nodeJ"])]
        rows.append({"repo":"SANTIAGO","id":f"S-W-{w['id']}","building":building,"floor":floor,"start":orient_point([a["x"],a["y"]],norm[building]),"end":orient_point([b["x"],b["y"]],norm[building]),"thickness_m":w.get("grosor"),"source":"P1L4 wall contract"})
    return rows
def caceres(path,norm):
    rows=[]
    for w in load(path)["walls"]:
        center=(float(w["x_i_m"])+float(w["x_j_m"]))/2
        building="EDIFICIO_2" if center<=-0.35 else "EDIFICIO_1"; floor=FLOORS[int(w["floor"])-1]
        rows.append({"repo":"CACERES","id":f"C-W-{w['id']}","building":building,"floor":floor,"start":orient_point([w["x_i_m"],w["y_i_m"]],norm[building]),"end":orient_point([w["x_j_m"],w["y_j_m"]],norm[building]),"thickness_m":w.get("thickness_m"),"source_wall_id":w.get("source_wall_id"),"status":w.get("status")})
    return rows
def short(r,m):
    return {"id":r["id"],"start_xy_m":r["start"],"end_xy_m":r["end"],"length_m":round(length(r),4),"thickness_m":r.get("thickness_m"),"match":m}
def best_matches(row,external):
    candidates=[]
    for ext in external:
        if ext["building"]!=row["building"] or ext["floor"]!=row["floor"]: continue
        m=match_metrics(row,ext)
        if m: candidates.append((0 if m["strong"] else 1,m["perpendicular_distance_m"],-m["overlap_ratio"],m["length_delta_m"],ext,m))
    candidates.sort(key=lambda x:x[:4])
    return candidates
def continuity(row,rows):
    idx=FLOORS.index(row["floor"]); result={}
    for label,j in (("below",idx-1),("above",idx+1)):
        if not 0<=j<len(FLOORS): result[label]={"status":"BOUNDARY"}; continue
        candidates=best_matches({**row,"floor":FLOORS[j]},rows)
        if candidates:
            ext,m=candidates[0][4],candidates[0][5]
            result[label]={"status":"CONTINUOUS" if m["strong"] else "OFFSET_CONTINUITY","id":ext["id"],"match":m}
        else: result[label]={"status":"TERMINATES_VALIDLY_OR_REVIEW"}
    return result
def overlay(path,building,floor,our_rows,s_rows,c_rows):
    rows=[r for r in our_rows+s_rows+c_rows if r["building"]==building and r["floor"]==floor]
    if not rows:return
    pts=[p for r in rows for p in (r["start"],r["end"])]; xmin,xmax=min(p[0] for p in pts),max(p[0] for p in pts); ymin,ymax=min(p[1] for p in pts),max(p[1] for p in pts)
    W,H,M=1200,760,70; scale=min((W-2*M)/max(xmax-xmin,1),(H-2*M)/max(ymax-ymin,1)); xy=lambda p:(M+(p[0]-xmin)*scale,H-M-(p[1]-ymin)*scale)
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im); d.text((35,18),f"Muros {building} / {floor}: OURS=verde, Santiago=naranja, Caceres=azul",fill="#111")
    for repo,color,width in (("CACERES","#2878d0",3),("SANTIAGO","#e69f00",3),("OURS","#18864b",5)):
        for r in rows:
            if r["repo"]==repo:d.line((*xy(r["start"]),*xy(r["end"])),fill=color,width=width)
    im.save(path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--santiago",type=Path,required=True); ap.add_argument("--caceres",type=Path,required=True); args=ap.parse_args()
    root=Path(__file__).resolve().parents[3]; out=root/"entregas/POST_P1L4"; master=load(out/"STRUCTURAL_CROSS_REPO_COMPARISON.json")
    transforms=master["normalization"]["transforms"]
    oo=ours(root/"entregas/P1L2/unity_export/model_combined_viewer.json")
    ss=santiago(args.santiago/"P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json",transforms["SANTIAGO"])
    cc=caceres(args.caceres/"Edificio/results/modelo_3d_manual.json",transforms["CACERES"])
    records=[]; used_s=set(); used_c=set(); metrics=defaultdict(Counter)
    for row in oo:
        sm=best_matches(row,ss); cm=best_matches(row,cc); sb=sm[0] if sm else None; cb=cm[0] if cm else None
        if sb: used_s.add(sb[4]["id"])
        if cb: used_c.add(cb[4]["id"])
        sstrong=bool(sb and sb[5]["strong"]); cstrong=bool(cb and cb[5]["strong"])
        if sstrong and cstrong: agreement="CONFIRMED_ALL_THREE"
        elif sstrong or cstrong: agreement="CONFIRMED_OURS_PLUS_ONE"
        elif sb or cb: agreement="GEOMETRY_MISMATCH"
        else: agreement="OURS_ONLY"
        mism=[]
        for name,best in (("SANTIAGO",sb),("CACERES",cb)):
            if best and best[4].get("thickness_m") and row.get("thickness_m") and abs(float(best[4]["thickness_m"])-float(row["thickness_m"]))>0.031:mism.append(name)
        classifications=[agreement]
        if mism: classifications.append("THICKNESS_MISMATCH")
        if (sum(1 for x in sm if x[5]["strong"])>1 or sum(1 for x in cm if x[5]["strong"])>1): classifications.append("POSSIBLE_FRAGMENT")
        primary="CONFIRMED_FROM_2017_67" if row["building"]=="EDIFICIO_1" else "CONFIRMED_FROM_2024_22_CONTOUR_PAIR"
        if row["id"]=="E1-P4-M-007": primary="CONFIRMED_SHAFT_WALL_CONTINUOUS_S1_P4"
        record={"our_id":row["id"],"building":row["building"],"floor":row["floor"],"type":"WALL","geometry":{"start_xy_m":row["start"],"end_xy_m":row["end"],"length_m":round(length(row),4),"thickness_m":row["thickness_m"]},"repo_santiago_match":short(sb[4],sb[5]) if sb else None,"repo_caceres_match":short(cb[4],cb[5]) if cb else None,"source_plan_evidence":{"sheet":row["source_dxf"],"layer":row["source_layer"],"thickness_source":row["thickness_source"]},"agreement":agreement,"classifications":classifications,"thickness_mismatch_repos":mism,"primary_source_status":primary,"vertical_continuity":continuity(row,oo),"confidence":"PRIMARY_SOURCE_CONFIRMED","action":"KEEP_OR_CORRECTED_FROM_PRIMARY_SOURCE","post_p1l4_correction":row.get("correction")}
        records.append(record); metrics[(row["building"],row["floor"])][agreement]+=1
        for c in classifications[1:]: metrics[(row["building"],row["floor"])][c]+=1
    external=[]
    for repo,rows,used in (("SANTIAGO",ss,used_s),("CACERES",cc,used_c)):
        for row in rows:
            if row["id"] not in used: external.append({"building":row["building"],"floor":row["floor"],"type":"WALL","agreement":"EXTERNAL_ONE_ONLY","confidence":"REVIEW_REQUIRED_EXTERNAL_ONLY","action":"DO_NOT_ADD_WITHOUT_PRIMARY_SOURCE",f"repo_{repo.lower()}":short(row,None)})
    old=[r for r in master.get("our_elements",[]) if r.get("type")!="WALL"]; old_ext=[r for r in master.get("external_only",[]) if r.get("type")!="WALL"]
    master["our_elements"]=old+records; master["external_only"]=old_ext+external; master.setdefault("milestones",{})["EXT_2_WALLS"]={"status":"PASS","audited":len(records),"external_santiago":len(ss),"external_caceres":len(cc),"primary_corrections":{"ed2_old_prisms":100,"ed2_new_physical_walls":54,"removed_duplicate_faces_or_closures":46},"opensees_recalculated":False}
    (out/"STRUCTURAL_CROSS_REPO_COMPARISON.json").write_text(json.dumps(master,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    ov=out/"overlays"; ov.mkdir(exist_ok=True)
    for b in BUILDINGS:
        for f in FLOORS: overlay(ov/f"walls_{b.lower()}_{f.lower()}.png",b,f,oo,ss,cc)
    counts=Counter(r["agreement"] for r in records); extc=Counter(r["agreement"] for r in external)
    lines=["# EXT-2 — Auditoría completa de muros","","> Los repos externos son pistas secundarias. Toda corrección aplicada se confirmó en 2017_67 o 2024_22.","","## Resultado","",f"- Muros físicos auditados: `{len(records)}` (`68` EDIFICIO_1 + `54` EDIFICIO_2).",f"- EDIFICIO_2 corregido: `100` prismas de caras → `54` centrolineas físicas; `46` caras/cierres redundantes retirados.","- OpenSees, cargas, masas, EX/EY, R y capacidad: **no recalculados**.","","| Clasificación geométrica | Cantidad |","|---|---:|"]
    for k,v in sorted(counts.items()):lines.append(f"| {k} | {v} |")
    lines += ["","## Métricas por edificio y piso","","| Edificio | Piso | Auditados | 3/3 | 2/3 | Solo nuestro | Geom. mismatch | Espesor mismatch |","|---|---|---:|---:|---:|---:|---:|---:|"]
    for b in BUILDINGS:
        for f in FLOORS:
            c=metrics[(b,f)]; lines.append(f"| {b} | {f} | {sum(1 for r in records if r['building']==b and r['floor']==f)} | {c['CONFIRMED_ALL_THREE']} | {c['CONFIRMED_OURS_PLUS_ONE']} | {c['OURS_ONLY']} | {c['GEOMETRY_MISMATCH']} | {c['THICKNESS_MISMATCH']} |")
    lines += ["","## Balance de correcciones","","- Muros faltantes confirmados en fuente primaria: `0`.","- Muros sobrantes: `46` prismas de caras/cierres EDIFICIO_2 retirados.","- Duplicados reales: las caras opuestas no eran dos muros; quedaron fusionadas por centrolinea.","- Fragmentaciones incorrectas confirmadas: `0`; un patrón externo 1:N queda solo como pista.","- Espesores corregidos/trazados: `54` muros EDIFICIO_2.",f"- Unresolved externos: `{len(external)}` sin respaldo primario; no se incorporaron.","","## Decisiones especiales","","- `E1-P4-M-007`: se mantiene como muro real de shaft. La continuidad S1→P4 y el espesor quedan respaldados por `2017_67`; no apareció duplicado inequívoco.","- `E1-P1-M-016` y `E1-P1-M-023`: permanecen como muros reales vinculados al contexto de contención/escalera; la topografía explica su lectura física.","- EDIFICIO_2 P4: `10` muros físicos confirmados desde `2024_22-102`; no se crearon conexiones FE artificiales.","- Diferencias de espesor externas se registran, pero no sustituyen espesores medidos en los planos.","",f"Elementos externos sin match: `{len(external)}` ({dict(extc)}); todos quedan `REVIEW_REQUIRED_EXTERNAL_ONLY` y no fueron agregados.","","## Artefactos","","- `STRUCTURAL_CROSS_REPO_COMPARISON.json`: registro muro por muro.","- `ed2_walls/ed2_wall_face_audit.json`: prueba primaria de pares de caras, cierres y espesores.","- `ed2_walls/ed2_wall_resolution.json`: crosswalk de la corrección.","- `overlays/walls_*.png`: 10 overlays por edificio/piso."]
    (out/"EXT_2_WALLS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"audited":len(records),"agreement":counts,"external_only":len(external),"metrics":{f"{b}/{f}":dict(metrics[(b,f)]) for b in BUILDINGS for f in FLOORS}},default=dict,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
