#!/usr/bin/env python3
"""Aplica la consolidacion primaria de muros EDIFICIO_2 al modelo fuente."""

from __future__ import annotations

import copy
import json
import math
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
MODEL = REPO / "entregas/P1L2/unity_export/model_2_viewer.json"
AUDIT = REPO / "entregas/POST_P1L4/ed2_walls/ed2_wall_face_audit.json"
OUT = REPO / "entregas/POST_P1L4/ed2_walls/ed2_wall_resolution.json"
FLOORS = ("S1", "P1", "P2", "P3", "P4")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def line_data(start, end):
    if abs(start[0]-end[0]) <= abs(start[1]-end[1]):
        return "V", (start[0]+end[0])/2, *sorted((start[1],end[1]))
    return "H", (start[1]+end[1])/2, *sorted((start[0],end[0]))


def score(old, pair):
    o1,f1,a1,b1 = line_data(old["start"],old["end"])
    o2,f2,a2,b2 = line_data(pair["centerline_start_xy_m"],pair["centerline_end_xy_m"])
    if o1 != o2:
        return None
    overlap = max(0.0,min(b1,b2)-max(a1,a2))
    if overlap < 0.30:
        return None
    return (-overlap/max(b2-a2,1e-9),abs(f1-f2),abs((b1-a1)-(b2-a2)))


def main():
    audit = load(AUDIT)
    if audit.get("status") != "PASS":
        raise RuntimeError("ED2 wall primary audit must be PASS before application")
    model = load(MODEL)
    old_walls = [x for x in model["solids"] if x.get("category")=="wall"]
    old_supports = [x for x in model["solids"] if x.get("category")=="support" and x.get("kind")=="linear_prism"]
    others = [x for x in model["solids"] if x not in old_walls and x not in old_supports]
    by_floor = {floor:[w for w in old_walls if w.get("floor")==floor] for floor in FLOORS}
    used, new_walls, crosswalk, changes = set(), [], [], []
    for floor in FLOORS:
        samples = by_floor[floor]
        z = sum(float(x["start"][2]) for x in samples)/len(samples)
        height = sum(float(x["height_m"]) for x in samples)/len(samples)
        for pair in audit["floors"][floor]["pairs"]:
            candidates=[]
            for old in samples:
                if old["solidTag"] in used:
                    continue
                match=score(old,pair)
                if match is not None:
                    candidates.append((match,str(old["solidTag"]),old))
            if not candidates:
                raise RuntimeError(f"No historical wall ID for {pair['pair_id']}")
            template=min(candidates,key=lambda x:(x[0],x[1]))[2]
            used.add(template["solidTag"])
            start=[*pair["centerline_start_xy_m"],z]
            end=[*pair["centerline_end_xy_m"],z]
            wall=copy.deepcopy(template)
            wall.update({
                "start":start,"end":end,"width_m":float(pair["thickness_m"]),"wall_thickness_m":float(pair["thickness_m"]),
                "height_m":height,"length_m":math.dist(start[:2],end[:2]),"sourceTag":pair["pair_id"],
                "sourceTags":pair["face_ids"],"source_layer":"RLE-MURO_CONTOUR_PAIR","source_dxf":pair["source_sheet"],
                "confidence":"confirmed_from_RLE_MURO_contour_pair","thickness_source":pair["thickness_source"],
                "thickness_confidence":"CONFIRMED_FROM_PLAN","geometry_confirmation":{
                    "status":"CONFIRMED_CONTOUR_PAIR","audit_file":str(AUDIT.relative_to(REPO)).replace("\\","/"),
                    "face_ids":pair["face_ids"],"measured_face_separation_m":pair["measured_face_separation_m"],"thickness_m":pair["thickness_m"]},
                "post_p1l4_correction":{
                    "correction_type":"MERGED","reason":"Dos caras RLE-MURO y sus cierres representaban un solo muro físico.",
                    "primary_source":pair["source_sheet"],"external_repo_clue":"Santiago modela 9 muros por nivel; pista secundaria, no criterio de decisión.",
                    "confidence":"HIGH_PRIMARY_SOURCE","results_compatibility":"P1L4_HISTORICAL_RESULTS_NOT_RECALCULATED"},
            })
            new_walls.append(wall)
            crosswalk.append({"new_solidTag":wall["solidTag"],"new_id":wall.get("id"),"source_face_ids":pair["face_ids"],"centerline_start_xy_m":pair["centerline_start_xy_m"],"centerline_end_xy_m":pair["centerline_end_xy_m"],"thickness_m":pair["thickness_m"]})
            changes.append({"solidTag":wall["solidTag"],"change":"MERGED_RESIZED","source_faces":pair["face_ids"],"primary_source":pair["source_sheet"]})
    # Rebuild S1 line supports one-to-one from confirmed physical walls.
    used_supports,new_supports=set(),[]
    for wall in [w for w in new_walls if w["floor"]=="S1"]:
        candidates=[]
        for old in old_supports:
            if old["solidTag"] in used_supports:
                continue
            match=score(old,{"centerline_start_xy_m":wall["start"],"centerline_end_xy_m":wall["end"]})
            if match is not None:
                candidates.append((match,str(old["solidTag"]),old))
        if not candidates:
            raise RuntimeError(f"No historical support for {wall['solidTag']}")
        template=min(candidates,key=lambda x:(x[0],x[1]))[2]
        used_supports.add(template["solidTag"])
        support=copy.deepcopy(template)
        support.update({"start":[wall["start"][0],wall["start"][1],-0.15],"end":[wall["end"][0],wall["end"][1],-0.15],"width_m":max(wall["width_m"]*1.8,0.45),"height_m":0.30,"length_m":wall["length_m"],"sourceTag":wall["solidTag"],"source_layer":"generated_from_confirmed_wall_centerline","confidence":"derived_from_confirmed_wall_centerline"})
        new_supports.append(support)
    model["solids"] = others + new_walls + new_supports
    model["wall_consolidation"]={"status":"APPLIED_POST_P1L4","audit_file":str(AUDIT.relative_to(REPO)).replace("\\","/"),"old_wall_prisms":len(old_walls),"new_wall_segments":len(new_walls),"old_wall_supports":len(old_supports),"new_wall_supports":len(new_supports),"results_policy":"P1L4 historical results unchanged"}
    model.setdefault("notes",[]).append("POST-P1L4: EDIFICIO_2 walls consolidated from paired 2024_22 RLE-MURO contour faces. P1L4 results remain historical and were not recalculated.")
    write(MODEL,model)
    result={"status":"PASS","old_wall_prisms":len(old_walls),"new_wall_segments":len(new_walls),"removed_duplicate_faces_or_closures":len(old_walls)-len(new_walls),"old_wall_supports":len(old_supports),"new_wall_supports":len(new_supports),"new_walls_by_floor":dict(Counter(w["floor"] for w in new_walls)),"changes":changes,"crosswalk":crosswalk,"opensees_results_recalculated":False}
    write(OUT,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('changes','crosswalk')},indent=2))


if __name__ == "__main__":
    main()
