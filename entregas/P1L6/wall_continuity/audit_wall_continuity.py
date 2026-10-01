"""Audit CURRENT wall footprints against primary axes and read-only repo snapshots."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

import ezdxf
from PIL import Image, ImageDraw
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
FLOORS = ("S1", "P1", "P2", "P3", "P4")
EXTERNAL = Path(r"C:\Users\matis\.codex\visualizations\2026\09\09\01a0872a-aec2-72f2-b78e-e04f148142ed\external_repos")
CORES = {
    "CORE_C_ED1_01": {"S1": [20, 26, 34], "P1": [12, 4, 25], "P2": [10, 7, 9], "P3": [10, 7, 9], "P4": [9, 7, 10]},
    "CORE_C_ED1_02": {"S1": [5, 29, 49], "P1": [2, 10, 26], "P2": [3, 8, 5], "P3": [3, 8, 5], "P4": [3, 8, 12]},
    "CORE_C_ED2_01": {"S1": [7, 8, 10], "P1": [7, 8, 10], "P2": [7, 8, 10], "P3": [7, 8, 10], "P4": [7, 8, 9]},
}

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def helpers():
    p = ROOT / "entregas/POST_P1L4/scripts/build_wall_cross_repo_comparison.py"
    spec = importlib.util.spec_from_file_location("wall_helpers", p)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    return h

def core_ids(group, floor):
    prefix = "E1" if "ED1" in group else "E2"
    return [f"{prefix}-{floor}-M-{n:03d}" for n in CORES[group][floor]]

def draw(path, rows, title, external=None):
    im = Image.new("RGB", (1500, 900), "white")
    d = ImageDraw.Draw(im)
    d.text((25, 15), title, fill="black")
    # Common core-zone bounds so before/after are visually comparable.
    xmin, xmax, ymin, ymax = 23.0, 36.0, -1.0, 18.0
    scale = min(1250 / (xmax-xmin), 780 / (ymax-ymin))
    def xy(p): return (100+(p[0]-xmin)*scale, 840-(p[1]-ymin)*scale)
    for color, data in [("#97b6d7", external or []), ("#137c45", rows)]:
        for r in data:
            if not 24 <= (r["start"][0]+r["end"][0])/2 <= 35: continue
            d.line([xy(r["start"]), xy(r["end"])], fill=color, width=max(3, int(r.get("thickness_m", .2)*scale)))
            if color == "#137c45":
                p = xy([(r["start"][i]+r["end"][i])/2 for i in (0, 1)])
                d.text((p[0]+5,p[1]+5), r["id"], fill="black")
    d.text((900, 90), "CURRENT: verde\nExternos normalizados: azul\nX/Y globales en metros", fill="black")
    im.save(path)

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    master = read(CENTRAL / "model_master.json")
    sections = {s["section_id"]:s for s in read(CENTRAL / "sections.json")["sections"]}
    prior = read(ROOT / "entregas/P1L6/current_cleanup/removed_wall_candidates.json")
    excluded = {r["element_id"]:r["before"] for r in read(ROOT / "entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json")["exclusions"]}
    evidence = read(ROOT / "entregas/PRE_P1L5/user_structural_review/column_axis_primary_evidence.json")
    axis_rows, shifts, docs = [], {}, {}
    for row in evidence["rows"]:
        p = ROOT / "recursos/planos/dxf_full/2017_67" / row["sheet"]
        if row["sheet"] not in docs: docs[row["sheet"]] = ezdxf.readfile(p)
        e = docs[row["sheet"]].entitydb[row["handle"]]
        y = (float(e.dxf.start.y)+float(e.dxf.end.y))/2
        residual = (row["current_origin_cm"][1]-y)/100-row["canonical_y_m"]
        axis_rows.append({**row, "source_hash_rechecked": hashlib.sha256(p.read_bytes()).hexdigest()==row["source_sha256"], "rechecked_residual_m": residual})
        if row["axis"] == "1": shifts[row["floor"]] = -residual
    assert all(r["source_hash_rechecked"] and abs(r["rechecked_residual_m"]-r["residual_m"])<1e-8 for r in axis_rows)
    candidates = {r["candidate_id"]:r for r in prior["candidates"]}
    current = []
    for r in master["elements"]:
        if r["type"] != "wall" or not r["active"]: continue
        current.append({"id":r["element_id"], "building":r["building"], "floor":r["floor"], "start":r["geometry"]["start_m"][:2], "end":r["geometry"]["end_m"][:2], "thickness_m":sections[r["section_id"]]["dimensions"]["thickness_m"], "primary_source":r.get("provenance",{}).get("source_dxf")})
    h = helpers()
    transforms = read(ROOT / "entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json")["normalization"]["transforms"]
    s = h.santiago(EXTERNAL/"Santiago_Trabajo_MCOC/P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json", transforms["SANTIAGO"])
    c = h.caceres(EXTERNAL/"Caceres_Proyecto_1_MCOC/Edificio/results/modelo_3d_manual.json", transforms["CACERES"])
    for r in current:
        r["vertical"] = h.continuity(r,current)
        r["external"] = {}
        for name, data in (("santiago",s),("caceres",c)):
            matches = h.best_matches(r,data)
            r["external"][name] = h.short(matches[0][4], matches[0][5]) if matches else None
    group_rows = []
    for group in CORES:
        for floor in FLOORS:
            ids = core_ids(group,floor)
            rows = []
            for eid in ids:
                active = next((r for r in current if r["id"]==eid),None)
                candidate = candidates.get(eid)
                source = excluded.get(eid)
                if active: geometry = {k:active[k] for k in ("start","end","thickness_m")}
                else:
                    assert candidate and source, eid
                    geometry = {"start":source["start"][:2], "end":source["end"][:2], "thickness_m":candidate["geometry"]["thickness_m"]}
                corrected = {k:list(v) if isinstance(v,list) else v for k,v in geometry.items()}
                if "ED1" in group:
                    for key in ("start","end"):
                        corrected[key] = [round(corrected[key][0],3), round(corrected[key][1]+shifts[floor],3)]
                rows.append({"id":eid,"active_before":bool(active),"geometry_before":geometry,"geometry_axis_registered":corrected,"primary_pair":candidate.get("primary_pair_audit") if candidate else None, "external_clues":{k:candidate.get(k) for k in ("santiago","caceres")} if candidate else active["external"], "source_sheet":source.get("source_dxf") if source else active["primary_source"]})
            group_rows.append({"group":group,"building":"EDIFICIO_1" if "ED1" in group else "EDIFICIO_2","floor":floor,"walls":rows,"present_before":sum(r["active_before"] for r in rows),"status_before":"CONTINUOUS" if all(r["active_before"] for r in rows) else "REVIEW_REQUIRED"})
    # Group every active wall line, using strict 20 mm endpoints and 1 mm thickness.
    lines = []
    for r in current:
        line = next((g for g in lines if g["building"]==r["building"] and abs(g["thickness_m"]-r["thickness_m"])<=.001 and min(max(math.dist(g["start"],r["start"]),math.dist(g["end"],r["end"])),max(math.dist(g["start"],r["end"]),math.dist(g["end"],r["start"])))<=.02),None)
        if line is None:
            line = {"line_id":f"WALL_LINE_{len(lines)+1:03d}", "building":r["building"],"start":r["start"],"end":r["end"],"thickness_m":r["thickness_m"],"floors":{}}
            lines.append(line)
        line["floors"].setdefault(r["floor"],[]).append(r["id"])
    for line in lines: line["state"] = "CONTINUOUS" if set(line["floors"])==set(FLOORS) else "REVIEW_REQUIRED"
    columns=[]
    for number in (4,7):
        stack=[r for r in master["elements"] if r["type"]=="column" and r["building"]=="EDIFICIO_2" and r["element_id"].endswith(f"C-{number:03d}")]
        assert len(stack)==5 and max(math.dist(a["geometry"]["center_m"][:2],b["geometry"]["center_m"][:2]) for a in stack for b in stack)<1e-6
        columns.append({"p4_id":f"E2-P4-C-{number:03d}","stack":[{"id":r["element_id"],"floor":r["floor"],"center_m":r["geometry"]["center_m"],"section_id":r["section_id"],"dimensions":sections[r["section_id"]]["dimensions"]} for r in sorted(stack,key=lambda r:FLOORS.index(r["floor"]))],"recommendation":"COPY_IMMEDIATELY_LOWER_SECTION_PRESERVE_XY_HEIGHT_MATERIAL_ID"})
    data={"base_commit":"ba889a7a27726217798f5d1cae6729fe6df74b96","phase":"AUDIT_BEFORE_CORRECTION","active_walls":current,"wall_lines":lines,"core_groups":group_rows,"columns":columns,"primary_axis_controls":axis_rows,"ed1_wall_registration_shift_y_m":shifts,"missing_on_P4": [r["candidate_id"] for r in prior["candidates"] if r["building"]=="EDIFICIO_2" and r["floor"]=="P4"],"wrong_side_wall":"REVIEW_REQUIRED_USER_LOCATION_NOT_YET_IDENTIFIED"}
    data["wrong_side_wall"] = "CAD_POSITION_RETAINED_NO_PRIMARY_MISMATCH"
    data["wrong_side_user_resolution"] = "Follow CAD only for this case; keep X=27.727 m, no unsupported reflection."
    (HERE/"WALL_CONTINUITY_BEFORE.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=["# Auditoría vertical de muros CURRENT — antes de corregir","",f"54 muros activos; {len(lines)} líneas geométricas distintas. Coincidencia vertical estricta: endpoints ≤0,02 m y espesor ≤0,001 m. Las ausencias no se consideran terminaciones válidas sin respaldo primario.","","## Controles de ejes originales","","Los 15 ejes se releyeron por handle y se verificaron contra el hash DXF. ED1 S1/P2/P3/P4 muestran un error sistemático de origen de 0,1813 m; P1 está correctamente referido al eje 1. El registro de los muros debe corregirse desde ese control primario, no por copiar posiciones externas. Esta auditoría no autoriza desplazar las vigas/columnas de todo ED1.","","| Línea | Edificio | S1 | P1 | P2 | P3 | P4 | Estado |","|---|---|---|---|---|---|---|---|"]
    for g in lines: md.append(f"| {g['line_id']} | {g['building']} | "+" | ".join(', '.join(g['floors'].get(f,[])) or '—' for f in FLOORS)+f" | {g['state']} |")
    md += ["","## Núcleos identificados","","| Grupo | Piso | IDs (ala / fondo / ala) | Activos antes | Fuente |","|---|---|---|---:|---|"]
    for g in group_rows: md.append(f"| {g['group']} | {g['floor']} | "+", ".join(w['id'] for w in g['walls'])+f" | {g['present_before']}/3 | "+", ".join(sorted({w['source_sheet'] for w in g['walls']}))+" |")
    md += ["","Se identifican **tres** grupos en C: dos en ED1 y uno en ED2. ED1_01 conserva solo el fondo S1; ED1_02 conserva sus tres lados únicamente en S1; ED2 conserva la C S1–P3 y falta en P4. Sus paños son elementos independientes, no una sección C monolítica.","","El tramo E2-S1/P1/P2/P3-M-009 no tiene equivalente P4 en la auditoría de caras de 2024_22-102: no se prolonga automáticamente. El muro largo X=27,727 m coincide con CAD y externos; no hay prueba para reflejarlo al lado opuesto. La ubicación del muro señalado por el usuario sigue pendiente de identificación.","","## Columnas P4","","Ambas líneas tienen XY idéntico en los cinco pisos y sección 70×70 cm de S1 a P3. P4 conserva 20×20 cm por una antigua asignación de etiqueta. La corrección solicitada reutiliza la sección existente de P3, mantiene el material/ID/altura y registra el antes/después."]
    md = [line.replace("La ubicación del muro señalado por el usuario sigue pendiente de identificación.", "El usuario resolvió seguir el CAD únicamente para este caso: se conserva X=27,727 m, sin reflejar ni inventar un traslado.") for line in md]
    (HERE/"WALL_CONTINUITY_BEFORE.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    for floor in FLOORS:
        draw(HERE/f"before_cores_{floor}.png",[r for r in current if r["floor"]==floor],f"BEFORE CURRENT / {floor}",[r for r in s+c if r["floor"]==floor])
    print(json.dumps({"active_walls":len(current),"wall_lines":len(lines),"cores":Counter(g['group'] for g in group_rows),"axis_shifts":shifts},indent=2))

if __name__=="__main__": main()
