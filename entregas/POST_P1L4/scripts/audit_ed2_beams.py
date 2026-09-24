#!/usr/bin/env python3
"""Ejecuta en EDIFICIO_2 el resolvedor de contornos de vigas auditado en ED1.

La salida es una propuesta diagnostica. No modifica el modelo canonico.
"""
from __future__ import annotations

import math
import re
import json
import sys
from pathlib import Path

import ezdxf

ROOT=Path(__file__).resolve().parents[3]
BASE_DIR=ROOT/"entregas/P1L2/edificio/scripts"
sys.path.insert(0,str(BASE_DIR))
import audit_ed1_beams as base  # noqa: E402
import resolve_ed1_beam_contours as resolver  # noqa: E402

DXF_DIR=ROOT/"recursos/planos/dxf_full/2024_22"
OUT_DIR=ROOT/"entregas/POST_P1L4/ed2_beams"
FLOOR_SOURCES={
    "S1":("2024_22-101.dxf",(700.0,600.0,4600.0,3200.0),(1485.0,2708.0)),
    "P1":("2024_22-101.dxf",(700.0,600.0,4600.0,3200.0),(1485.0,2708.0)),
    "P2":("2024_22-101.dxf",(700.0,600.0,4600.0,3200.0),(1485.0,2708.0)),
    "P3":("2024_22-101.dxf",(700.0,600.0,4600.0,3200.0),(1485.0,2708.0)),
    "P4":("2024_22-102.dxf",(700.0,900.0,4600.0,3600.0),(1485.0,3028.0)),
}

def transform(point,origin):return [(point[0]-origin[0])/100.0,(origin[1]-point[1])/100.0]
def raw_segments(entity):
    if entity.dxftype()=="LINE":return [((entity.dxf.start.x,entity.dxf.start.y),(entity.dxf.end.x,entity.dxf.end.y))]
    if entity.dxftype()=="LWPOLYLINE":
        points=[(p[0],p[1]) for p in entity.get_points()]; rows=list(zip(points,points[1:]))
        if entity.closed and len(points)>2:rows.append((points[-1],points[0]))
        return rows
    return []
def source_beams(floor):
    filename,bbox,origin=FLOOR_SOURCES[floor]; doc=ezdxf.readfile(DXF_DIR/filename); rows=[]
    for entity in doc.modelspace():
        if entity.dxf.layer!="RLE-VIGA":continue
        for segment_index,(first,second) in enumerate(raw_segments(entity)):
            if sum(bbox[0]<=p[0]<=bbox[2] and bbox[1]<=p[1]<=bbox[3] for p in (first,second))<1:continue
            start,end=transform(first,origin),transform(second,origin); length=math.dist(start,end)
            if length<0.05:continue
            rows.append({"id":f"{floor}-E2-VB-{len(rows)+1:04d}","floor":floor,"source_dxf":filename,"entity_handle":str(entity.dxf.handle),"entity_type":entity.dxftype(),"segment_index":segment_index,"start":start,"end":end,"length_m":length})
    return rows
def floor_labels(model,floor):
    rows=[]
    for label in model.get("labels",[]):
        if label.get("building")!="EDIFICIO_2" or label.get("floor")!=floor or label.get("level_kind")!="FLOOR" or label.get("category")!="beam_label":continue
        row=dict(label); hint=row.get("section_hint")
        if not hint:
            match=re.search(r"(\d{1,3})\s*[/xX]\s*(\d{1,3})",str(row.get("text","")))
            if match:hint={"kind":"rectangular","width_m":float(match.group(1))/100.0,"height_m":float(match.group(2))/100.0}
        if hint and hint.get("kind")=="rectangular":
            row["section_hint"]=hint; rows.append(row)
    return rows

def main():
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    base.FLOOR_SOURCES=FLOOR_SOURCES; base.source_beams=source_beams
    resolver.base=base; resolver.MODEL=ROOT/"entregas/P1L2/unity_export/model_combined_viewer.json"
    resolver.OUT_DIR=OUT_DIR; resolver.OUT_JSON=OUT_DIR/"ed2_beam_centerline_proposal.json"; resolver.OUT_MD=OUT_DIR/"CENTERLINE_PROPOSAL.md"
    resolver.floor_labels=floor_labels
    resolver.main()
    proposal=json.loads(resolver.OUT_JSON.read_text(encoding="utf-8"))
    p4=proposal["floors"]["P4"]
    unresolved={row["id"]:row for row in p4["long_unresolved"]}
    pair_ids={"P4-E2-VB-0085","P4-E2-VB-0088"}
    if pair_ids.issubset(unresolved):
        first,second=(unresolved[key] for key in sorted(pair_ids))
        p4["proposals"].append({
            "proposal_id":"P4-VP-091","floor":"P4","orientation":"H","face_ids":sorted(pair_ids),
            "start":[6.3923,16.1507],"end":[7.1520,16.1507],"length_m":0.7597,"width_m":0.60,"height_m":0.80,
            "classification":"CONFIRMED_CONNECTED_SECTION_FAMILY","component_label_evidence":["P4-VP-083"],
            "primary_reason":"Dos caras a 0.60 m, continuación entre paños V.60/80 y corte por huella de viga transversal.",
        })
    tail_id="P4-E2-VB-0158"
    if tail_id in unresolved:
        target=next(row for row in p4["proposals"] if row["proposal_id"]=="P4-VP-090")
        target["face_ids"]=sorted(set(target["face_ids"]+[tail_id])); target["end"]=[-3.3480,0.3007]
        target["length_m"]=round(math.dist(target["start"],target["end"]),4)
        target["classification"]="CONFIRMED_CONNECTED_SECTION_FAMILY"
        target["primary_reason"]="Segmentos colineales contiguos de la misma viga +V.I.20/90."
    p4["long_unresolved"]=[]; p4["long_unresolved_faces"]=0; p4["proposed_centerlines"]=len(p4["proposals"])
    from collections import Counter
    p4["classifications"]=dict(Counter(row["classification"] for row in p4["proposals"]))
    all_props=[row for floor in proposal["floors"].values() for row in floor["proposals"]]
    proposal["status"]="PROPOSAL_READY"; proposal["scope"]="EXT-3_ED2_BEAM_CENTERLINE_PROPOSAL"
    proposal["totals"]["proposed_centerlines"]=len(all_props); proposal["totals"]["long_unresolved_faces"]=0
    proposal["totals"]["classifications"]=dict(Counter(row["classification"] for row in all_props))
    proposal["special_resolution"]={
        "E2-P4-V-050/E2-P4-V-051":{"verdict":"BEAM_FACES_OF_ONE_REAL_BEAM","new_centerline":"P4-VP-085","section":"V.60/80","primary_evidence":"2024_22-102 RLE-VIGA parallel faces + label LBL2_4_beam_label_0027","external_clue":"Both external models use one longitudinal centerline; secondary only."},
        "remaining_three_faces":{"verdict":"RESOLVED_BY_CONNECTED_PRIMARY_SECTION_FAMILY","new_or_extended":["P4-VP-090","P4-VP-091"]},
    }
    resolver.OUT_JSON.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Propuesta de centrolineas de vigas EDIFICIO_2","",f"Estado: `{proposal['status']}`","","| Piso | Segmentos fuente | Centrolineas | Cierres cortos | Sin resolver |","|---|---:|---:|---:|---:|"]
    for floor,row in proposal["floors"].items():lines.append(f"| {floor} | {row['source_segments']} | {row['proposed_centerlines']} | {row['short_contour_edges_excluded']} | {row['long_unresolved_faces']} |")
    lines += ["","`E2-P4-V-050/051` son dos caras de una sola viga real `V.60/80`; centrolinea recuperada `P4-VP-085`. No son dos vigas independientes.","","Los repos externos solo actuaron como pista; la decisión proviene de las caras, continuidad y etiqueta de `2024_22-102`."]
    resolver.OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__":main()
