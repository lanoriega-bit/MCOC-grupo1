#!/usr/bin/env python3
"""Construye candidato topologico PRE-P1L4 sin ejecutar OpenSees ni cargas."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point


REPO = Path(__file__).resolve().parents[3]
P1L3 = REPO / "entregas/P1L3"
sys.path.insert(0, str(P1L3))
from p1l3.modelado import _section_props  # noqa: E402
from p1l3.rutas import COMBINED_VIEWER_JSON, LEVELS_Z_M  # noqa: E402

OUT_DIR = P1L3 / "results/post_p1l3_candidate"
OUT_JSON = OUT_DIR / "analysis_model_post_p1l3_candidate.json"
OUT_REPORT = OUT_DIR / "TOPOLOGY_REPORT.md"
AUDIT = REPO / "entregas/P1L2/edificio/validacion/fe_connectivity_post_geometry/connectivity_comparison.json"
TOL = 0.06


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    model = load(COMBINED_VIEWER_JSON)
    prior = load(AUDIT)
    solids = [s for s in model["solids"] if s.get("category") in {"column", "wall", "beam"}]
    vertical = [s for s in solids if s["category"] in {"column", "wall"}]
    walls = [s for s in vertical if s["category"] == "wall"]
    columns = [s for s in vertical if s["category"] == "column"]
    beams = [s for s in solids if s["category"] == "beam"]

    nodes, node_index = {}, {}
    def node(x, y, z, building, reason):
        key = (building, round(x, 3), round(y, 3), round(z, 3))
        for existing_key, existing_tag in node_index.items():
            if existing_key[0] == building and abs(existing_key[3] - key[3]) <= .001 and math.hypot(existing_key[1] - key[1], existing_key[2] - key[2]) <= .05:
                if reason not in nodes[existing_tag]["reasons"]:
                    nodes[existing_tag]["reasons"].append(reason)
                return existing_tag
        if key not in node_index:
            tag = len(nodes) + 1
            node_index[key] = tag
            nodes[tag] = {"tag": tag, "x": key[1], "y": key[2], "z": key[3], "building": building, "reasons": []}
        tag = node_index[key]
        if reason not in nodes[tag]["reasons"]:
            nodes[tag]["reasons"].append(reason)
        return tag

    wall_lines = {s["solidTag"]: LineString([s["start"][:2], s["end"][:2]]) for s in walls}
    wall_junctions = defaultdict(list)
    connections = []
    def add_wall_junction(wall, xy, z, kind, other):
        key = (wall["solidTag"], round(z, 3), round(xy[0], 3), round(xy[1], 3))
        if key not in {(r["wallTag"], r["z"], r["x"], r["y"]) for r in wall_junctions[wall["solidTag"]]}:
            wall_junctions[wall["solidTag"]].append({"wallTag": wall["solidTag"], "x": key[2], "y": key[3], "z": key[1], "kind": kind, "other": other})
            connections.append({"type": kind, "geometry_a": wall.get("id"), "geometry_b": other, "point": [key[2], key[3], key[1]], "evidence": "same building/level + physical centerline intersection or overlap"})

    # Muro-muro: intersecciones en cada extremo vertical del piso.
    for i, a in enumerate(walls):
        la = wall_lines[a["solidTag"]]
        za = (a["coordinates"]["z_bottom_m"], a["coordinates"]["z_top_m"])
        for b in walls[i + 1:]:
            if a["building"] != b["building"] or a["floor"] != b["floor"]:
                continue
            lb = wall_lines[b["solidTag"]]
            inter = la.intersection(lb)
            if inter.is_empty:
                continue
            pts = [inter] if inter.geom_type == "Point" else [inter.interpolate(0.5, normalized=True)] if inter.geom_type == "LineString" else []
            for p in pts:
                for z in za:
                    add_wall_junction(a, (p.x, p.y), z, "WALL_WALL_INTERSECTION", b["id"])
                    add_wall_junction(b, (p.x, p.y), z, "WALL_WALL_INTERSECTION", a["id"])

    # Solape de muros entre pisos contiguos, sin copiar conexiones entre edificios.
    for a in walls:
        la = wall_lines[a["solidTag"]]
        ztop = float(a["coordinates"]["z_top_m"])
        for b in walls:
            if a is b or a["building"] != b["building"] or abs(ztop - float(b["coordinates"]["z_bottom_m"])) > 0.01:
                continue
            lb = wall_lines[b["solidTag"]]
            inter = la.intersection(lb)
            if inter.is_empty:
                continue
            p = inter if inter.geom_type == "Point" else inter.interpolate(0.5, normalized=True) if inter.geom_type == "LineString" else None
            if p is not None:
                add_wall_junction(a, (p.x, p.y), ztop, "WALL_VERTICAL_OVERLAP", b["id"])
                add_wall_junction(b, (p.x, p.y), ztop, "WALL_VERTICAL_OVERLAP", a["id"])

    # Incidencias de columnas sobre muros por interseccion de huellas fisicas.
    for c in columns:
        cp = Point(c["coordinates"]["center"][:2])
        cz = (float(c["coordinates"]["z_bottom_m"]), float(c["coordinates"]["z_top_m"]))
        radius = 0.5 * max(float(c.get("section_width_m") or c.get("width_m", .7)), float(c.get("section_depth_m") or c.get("depth_m", .7)))
        for w in walls:
            if c["building"] != w["building"] or c["floor"] != w["floor"]:
                continue
            if wall_lines[w["solidTag"]].distance(cp) <= radius + 0.5 * float(w.get("width_m", .22)) + TOL:
                q = wall_lines[w["solidTag"]].interpolate(wall_lines[w["solidTag"]].project(cp))
                for z in cz:
                    add_wall_junction(w, (q.x, q.y), z, "COLUMN_WALL_FOOTPRINT_INTERSECTION", c["id"])

    beam_splits = defaultdict(list)
    column_beam_links = []
    beam_beam_links = []
    # Viga-muro: exige cruce de ejes o que el extremo caiga dentro de la huella del muro.
    for b in beams:
        bl = LineString([b["start"][:2], b["end"][:2]])
        z = LEVELS_Z_M[b["floor"]]
        beam_splits[b["solidTag"]].extend([(0.0, tuple(b["start"][:2]), "BEAM_END"), (bl.length, tuple(b["end"][:2]), "BEAM_END")])
        for w in walls:
            if b["building"] != w["building"] or b["floor"] != w["floor"]:
                continue
            wl = wall_lines[w["solidTag"]]
            inter = bl.intersection(wl)
            points = [inter] if inter.geom_type == "Point" else []
            if not points:
                for endpoint in (Point(bl.coords[0]), Point(bl.coords[-1])):
                    if wl.distance(endpoint) <= 0.5 * float(w.get("width_m", .22)) + 0.5 * float(b.get("width_m", .3)) + TOL:
                        points.append(wl.interpolate(wl.project(endpoint)))
            for p in points:
                d = bl.project(p)
                q = bl.interpolate(d)
                beam_splits[b["solidTag"]].append((d, (q.x, q.y), "BEAM_WALL_INTERSECTION"))
                add_wall_junction(w, (q.x, q.y), z, "BEAM_WALL_INTERSECTION", b["id"])

    # Columna-viga: interseccion de huellas en el nivel, incluso a mitad de vano.
    for b in beams:
        bl = LineString([b["start"][:2], b["end"][:2]])
        z = LEVELS_Z_M[b["floor"]]
        for c in columns:
            if b["building"] != c["building"] or not (abs(float(c["coordinates"]["z_bottom_m"]) - z) <= .01 or abs(float(c["coordinates"]["z_top_m"]) - z) <= .01):
                continue
            cp = Point(c["coordinates"]["center"][:2])
            radius = 0.5 * max(float(c.get("section_width_m") or c.get("width_m", .7)), float(c.get("section_depth_m") or c.get("depth_m", .7)))
            if bl.distance(cp) <= radius + 0.5 * float(b.get("width_m", .3)) + TOL:
                d = bl.project(cp); q = bl.interpolate(d)
                beam_splits[b["solidTag"]].append((d, (q.x, q.y), "COLUMN_BEAM_FOOTPRINT_INTERSECTION"))
                connections.append({"type": "COLUMN_BEAM_FOOTPRINT_INTERSECTION", "geometry_a": b["id"], "geometry_b": c["id"], "point": [round(q.x,3), round(q.y,3), z], "evidence": "same building/level + physical footprint intersection"})
                column_beam_links.append((b, c, (q.x, q.y), z))

    # Cruces reales entre ejes de viga del mismo piso/edificio.
    for i, a in enumerate(beams):
        la = LineString([a["start"][:2], a["end"][:2]])
        for b in beams[i + 1:]:
            if a["building"] != b["building"] or a["floor"] != b["floor"]:
                continue
            lb = LineString([b["start"][:2], b["end"][:2]])
            inter = la.intersection(lb)
            if inter.geom_type != "Point":
                ua=(la.coords[-1][0]-la.coords[0][0],la.coords[-1][1]-la.coords[0][1]); ub=(lb.coords[-1][0]-lb.coords[0][0],lb.coords[-1][1]-lb.coords[0][1])
                cross=abs(ua[0]*ub[1]-ua[1]*ub[0])/max(la.length*lb.length,1e-9)
                limit=.5*float(a.get("width_m",.3))+.5*float(b.get("width_m",.3))+TOL
                pairs=[]
                if cross>.10:
                    for source,receiver,ls,lr in ((a,b,la,lb),(b,a,lb,la)):
                        for endpoint in (Point(ls.coords[0]),Point(ls.coords[-1])):
                            if lr.distance(endpoint)<=limit:
                                q=lr.interpolate(lr.project(endpoint)); pairs.append((source,receiver,endpoint,q,lr.project(q)))
                else:
                    for ea in (Point(la.coords[0]),Point(la.coords[-1])):
                        for eb in (Point(lb.coords[0]),Point(lb.coords[-1])):
                            if ea.distance(eb)<=limit: pairs.append((a,b,ea,eb,lb.project(eb)))
                for source,receiver,p,q,d in pairs:
                    beam_splits[receiver["solidTag"]].append((d,(q.x,q.y),"BEAM_BEAM_FOOTPRINT_INTERSECTION"))
                    beam_beam_links.append((source,receiver,(p.x,p.y),(q.x,q.y),LEVELS_Z_M[a["floor"]]))
                    connections.append({"type":"BEAM_BEAM_FOOTPRINT_INTERSECTION","geometry_a":source["id"],"geometry_b":receiver["id"],"point":[round(q.x,3),round(q.y,3),LEVELS_Z_M[a["floor"]]],"evidence":"same building/level + physical beam footprint intersection"})
                continue
            beam_splits[a["solidTag"]].append((la.project(inter), (inter.x, inter.y), "BEAM_BEAM_INTERSECTION"))
            beam_splits[b["solidTag"]].append((lb.project(inter), (inter.x, inter.y), "BEAM_BEAM_INTERSECTION"))
            connections.append({"type":"BEAM_BEAM_INTERSECTION","geometry_a":a["id"],"geometry_b":b["id"],"point":[round(inter.x,3),round(inter.y,3),LEVELS_Z_M[a["floor"]]],"evidence":"same building/level + centerline intersection"})

    elements, crosswalk, constraints = [], [], []
    def add_element(s, ni, nj, segment_index=0):
        tag = len(elements) + 10001
        aid = f"POST-A-{tag-10000:05d}"
        row = {"analysis_id": aid, "opensees_element_tag": tag, "element_id": s["id"], "geometry_elementTag": s["solidTag"], "geometry_segment_index": segment_index, "type": s["category"], "building": s["building"], "floor": s["floor"], "node_i": ni, "node_j": nj, "opensees_node_i": ni, "opensees_node_j": nj}
        elements.append(row); crosswalk.append(dict(row))

    centroid_nodes = {}
    for s in vertical:
        x, y = s["coordinates"]["center"][:2]; zb=s["coordinates"]["z_bottom_m"]; zt=s["coordinates"]["z_top_m"]
        ni=node(x,y,zb,s["building"],"VERTICAL_CENTROID"); nj=node(x,y,zt,s["building"],"VERTICAL_CENTROID")
        centroid_nodes[(s["solidTag"],round(zb,3))]=ni; centroid_nodes[(s["solidTag"],round(zt,3))]=nj
        add_element(s,ni,nj)
    for w in walls:
        for j in wall_junctions[w["solidTag"]]:
            nj=node(j["x"],j["y"],j["z"],w["building"],j["kind"])
            nc=centroid_nodes[(w["solidTag"],round(j["z"],3))]
            if nc != nj:
                constraints.append({"type":"RIGID_WALL_ARM","master_node":nc,"slave_node":nj,"geometry_elementTag":w["solidTag"],"reason":j["kind"],"other_geometry_id":j["other"]})
    for b in beams:
        bl=LineString([b["start"][:2],b["end"][:2]]); z=LEVELS_Z_M[b["floor"]]
        unique={round(d,3):(d,xy,reason) for d,xy,reason in beam_splits[b["solidTag"]]}
        pts=[unique[k] for k in sorted(unique)]
        for idx,(a,c) in enumerate(zip(pts,pts[1:])):
            if c[0]-a[0] < .02: continue
            ni=node(*a[1],z,b["building"],a[2]); nj=node(*c[1],z,b["building"],c[2]); add_element(b,ni,nj,idx)
    for b, c, xy, z in column_beam_links:
        beam_node = node(*xy, z, b["building"], "COLUMN_BEAM_FOOTPRINT_INTERSECTION")
        cx, cy = c["coordinates"]["center"][:2]
        column_node = node(cx, cy, z, c["building"], "VERTICAL_CENTROID")
        if beam_node != column_node:
            constraints.append({"type":"RIGID_COLUMN_FOOTPRINT_ARM","master_node":column_node,"slave_node":beam_node,"geometry_elementTag":c["solidTag"],"reason":"COLUMN_BEAM_FOOTPRINT_INTERSECTION","other_geometry_id":b["id"]})
    for source, receiver, source_xy, receiver_xy, z in beam_beam_links:
        a=node(*source_xy,z,source["building"],"BEAM_BEAM_FOOTPRINT_INTERSECTION")
        b=node(*receiver_xy,z,receiver["building"],"BEAM_BEAM_FOOTPRINT_INTERSECTION")
        if a!=b:
            constraints.append({"type":"RIGID_BEAM_JOINT_ARM","master_node":b,"slave_node":a,"geometry_elementTag":source["solidTag"],"reason":"BEAM_BEAM_FOOTPRINT_INTERSECTION","other_geometry_id":receiver["id"]})

    # Una sola restriccion por par de nodos; conserva todos los motivos/IDs.
    constraint_by_pair={}
    for c in constraints:
        pair=tuple(sorted((c["master_node"],c["slave_node"])))
        if pair not in constraint_by_pair:
            constraint_by_pair[pair]={**c,"reasons":[c["reason"]],"other_geometry_ids":[c["other_geometry_id"]]}
        else:
            row=constraint_by_pair[pair]
            if c["reason"] not in row["reasons"]: row["reasons"].append(c["reason"])
            if c["other_geometry_id"] not in row["other_geometry_ids"]: row["other_geometry_ids"].append(c["other_geometry_id"])
    constraints=list(constraint_by_pair.values())

    parent={t:t for t in nodes}
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[rb]=ra
    for e in elements: union(e["node_i"],e["node_j"])
    for c in constraints: union(c["master_node"],c["slave_node"])
    supports={centroid_nodes[(s["solidTag"],0.0)] for s in vertical if abs(float(s["coordinates"]["z_bottom_m"]))<.01}
    supported_roots={find(t) for t in supports}
    floating=[e for e in elements if find(e["node_i"]) not in supported_roots]
    roots={find(e["node_i"]) for e in floating}

    old_focus={r["element_id"] for r in prior["current_floating_classification"]["elements"]}
    floating_geometry={e["element_id"] for e in floating}
    resolved=sorted(old_focus-floating_geometry); remaining=sorted(old_focus&floating_geometry)
    degree=Counter()
    for e in elements: degree.update((e["node_i"],e["node_j"]))
    for c in constraints: degree.update((c["master_node"],c["slave_node"]))
    focus_rows={r["element_id"]:r for r in prior["current_floating_classification"]["elements"]}
    classifications=[]
    for gid in sorted(old_focus):
        row=focus_rows[gid]; solid=next(s for s in solids if s["id"]==gid); connected=gid not in floating_geometry
        if row["type"]=="beam":
            z=LEVELS_Z_M[solid["floor"]]; ends=[node(*solid[p][:2],z,solid["building"],"VALIDATION") for p in ("start","end")]
            free=sum(degree[t]<=1 for t in ends)
            structural="REAL_CANTILEVER" if connected and free==1 else "FE_ADAPTER_ERROR" if connected else "UNRESOLVED"
            validation="FREE_END_EXPECTED" if structural=="REAL_CANTILEVER" else "CONNECTED_EXPECTED" if connected else "UNRESOLVED"
        elif row["type"]=="wall":
            structural="FE_ADAPTER_ERROR" if connected else "UNRESOLVED"
            validation="CONNECTED_EXPECTED" if connected else "DISCONNECTED_ERROR"
        else:
            cp=Point(solid["coordinates"]["center"][:2]); zb=float(solid["coordinates"]["z_bottom_m"]); zt=float(solid["coordinates"]["z_top_m"])
            lower=any(c["id"]!=gid and c["building"]==solid["building"] and abs(float(c["coordinates"]["z_top_m"])-zb)<.01 and Point(c["coordinates"]["center"][:2]).distance(cp)<=.05 for c in columns)
            upper=any(c["id"]!=gid and c["building"]==solid["building"] and abs(float(c["coordinates"]["z_bottom_m"])-zt)<.01 and Point(c["coordinates"]["center"][:2]).distance(cp)<=.05 for c in columns)
            structural="CONTINUOUS" if lower or upper else "TRANSFERRED" if connected else "UNRESOLVED"
            validation="CONNECTED_EXPECTED" if connected else "UNRESOLVED"
        classifications.append({"element_id":gid,"type":row["type"],"building":row["building"],"floor":row["floor"],"structural_classification":structural,"validation":validation,"connected_in_candidate":connected})
    component_rows=[]
    for root in sorted(roots):
        members=[e for e in floating if find(e["node_i"])==root]
        component_rows.append({"component_id":f"POST-FLOAT-{len(component_rows)+1:03d}","fe_segment_count":len(members),"analysis_ids":sorted(e["analysis_id"] for e in members),"geometry_element_ids":sorted({e["element_id"] for e in members})})
    split_groups=Counter(r["geometry_elementTag"] for r in crosswalk)
    required={"element_id","geometry_elementTag","analysis_id","opensees_element_tag","opensees_node_i","opensees_node_j"}
    assert all(required <= set(row) for row in crosswalk)
    baseline_elements=int(prior["current_in_memory"]["floating_elements"]);baseline_components=int(prior["current_in_memory"]["floating_components"])
    candidate={"format":"POST_P1L4_ANALYSIS_TOPOLOGY_CANDIDATE_v2","units":{"length":"m","force":"N","stress":"Pa"},"status":"CANDIDATE_NOT_APPROVED_NOT_RUN","inputs":{"geometry_sha256":sha(COMBINED_VIEWER_JSON),"connectivity_audit_sha256":sha(AUDIT)},"nodes":nodes,"elements":elements,"constraints":constraints,"supports":sorted(supports),"crosswalk":crosswalk,"junction_connections":connections,"connectivity_validation":classifications,"floating_excluded":{"n_componentes":len(component_rows),"n_fe_segments":len(floating),"n_geometry_elements":len(floating_geometry),"components":component_rows},"qa":{"baseline_floating_elements":baseline_elements,"baseline_components":baseline_components,"candidate_floating_fe_segments":len(floating),"candidate_floating_geometry_elements":len(floating_geometry),"candidate_floating_components":len(roots),"focus_resolved_geometry_ids":resolved,"focus_remaining_geometry_ids":remaining,"classification_counts":dict(sorted(Counter(r["structural_classification"] for r in classifications).items())),"validation_counts":dict(sorted(Counter(r["validation"] for r in classifications).items())),"beam_wall_connections":sum(c["type"]=="BEAM_WALL_INTERSECTION" for c in connections),"wall_wall_connections":sum(c["type"]=="WALL_WALL_INTERSECTION" for c in connections),"wall_vertical_overlaps":sum(c["type"]=="WALL_VERTICAL_OVERLAP" for c in connections),"column_beam_connections":sum(c["type"]=="COLUMN_BEAM_FOOTPRINT_INTERSECTION" for c in connections),"node_count":len(nodes),"fe_element_count":len(elements),"constraint_count":len(constraints),"geometry_elements_split_into_multiple_fe":sum(v>1 for v in split_groups.values()),"max_fe_segments_per_geometry":max(split_groups.values()),"crosswalk_required_fields":"PASS"},"run_policy":{"opensees_run":False,"loads_changed":False,"results_changed":False,"unity_changed":False}}
    OUT_DIR.mkdir(parents=True,exist_ok=True); OUT_JSON.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    q=candidate["qa"]
    def ids(kind, field="type"):
        return ", ".join(r["element_id"] for r in classifications if r[field]==kind) or "—"
    report=["# EXT-4 — candidato topológico POST-P1L4","","Estado: `CANDIDATE_NOT_APPROVED_NOT_RUN`. No reemplaza A3-A4 ni ejecuta OpenSees.","","## Estrategia","","Los muros conservan un miembro vertical equivalente en su centro para no multiplicar rigidez. Los encuentros comprobados generan nodos sobre el eje y restricciones rígidas internas al muro. Las vigas se segmentan solo en incidencias de huellas o cruces del mismo edificio y nivel.","","## Métricas","",f"- Flotantes: {q['baseline_floating_elements']} geometrías/{q['baseline_components']} componentes → {q['candidate_floating_geometry_elements']}/{q['candidate_floating_components']}.",f"- Nodos candidatos: {q['node_count']}.",f"- Elementos FE candidatos: {q['fe_element_count']}.",f"- Restricciones internas: {q['constraint_count']}.",f"- Geometrías con relación 1:N: {q['geometry_elements_split_into_multiple_fe']}; máximo {q['max_fe_segments_per_geometry']} segmentos.",f"- Viga–muro: {q['beam_wall_connections']}; muro–muro: {q['wall_wall_connections']}; solapes verticales: {q['wall_vertical_overlaps']}; columna–viga: {q['column_beam_connections']}.","",f"## Clasificación de los {q['baseline_floating_elements']} elementos foco","",*[f"- `{k}`: {v}." for k,v in q["classification_counts"].items()],"",f"- `REAL_CANTILEVER`: {ids('REAL_CANTILEVER','structural_classification')}.",f"- `TRANSFERRED`: {ids('TRANSFERRED','structural_classification')}.",f"- `FE_ADAPTER_ERROR`: {ids('FE_ADAPTER_ERROR','structural_classification')}.",f"- `UNRESOLVED`: {ids('UNRESOLVED','structural_classification')}.","","## Validación","",*[f"- `{k}`: {v}." for k,v in q["validation_counts"].items()],"",f"Crosswalk: `{q['crosswalk_required_fields']}` con `element_id`, `geometry_elementTag`, `analysis_id`, `opensees_element_tag` y nodos OpenSees. No se ejecutó OpenSees ni se modificaron cargas, resultados o geometría."]
    OUT_REPORT.write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(q,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
