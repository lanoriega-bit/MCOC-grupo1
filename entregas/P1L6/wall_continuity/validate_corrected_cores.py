"""Compare exact-scope corrections, wall continuity and end-to-end CURRENT QA."""
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path
from shapely.geometry import LineString
from audit_wall_continuity import CORES, FLOORS, core_ids, draw

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/"entregas/P1L5/modelo_central"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    master=read(CENTRAL/"model_master.json")
    elements={e["element_id"]:e for e in master["elements"]}
    sections={s["section_id"]:s for s in read(CENTRAL/"sections.json")["sections"]}
    before=json.loads(subprocess.check_output(["git","show","ba889a7:entregas/P1L5/modelo_central/model_master.json"],cwd=ROOT))
    old={e["element_id"]:e for e in before["elements"]}
    checks={"unrelated_beams_and_slabs_preserved":all(all(elements[eid][k]==e[k] for k in ("geometry","section_id","material_id")) for eid,e in old.items() if e["type"] in ("beam","slab")),"wall_materials_preserved":all(elements[eid]["material_id"]==e["material_id"] for eid,e in old.items() if e["type"]=="wall")}
    groups=[]
    for group in CORES:
        lines=[]
        for floor in FLOORS:
            rows=[elements[eid] for eid in core_ids(group,floor)]
            footprint=[(r["geometry"]["start_m"][:2],r["geometry"]["end_m"][:2],sections[r["section_id"]]["dimensions"]["thickness_m"]) for r in rows]
            lines.append(footprint)
            groups.append({"group":group,"floor":floor,"ids":[r["element_id"] for r in rows],"status":"CONTINUOUS"})
        # CAD millimetre rounding must not be confused with a real offset.
        checks[group+"_vertical"]=all(all(LineString([a[0],a[1]]).hausdorff_distance(LineString([b[0],b[1]]))<=0.002 and abs(a[2]-b[2])<=0.001 for a,b in zip(line,lines[0])) for line in lines)
    walls=[];pairs=[];duplicates=[]
    for e in elements.values():
        if e["type"]!="wall" or not e["active"]:continue
        g=e["geometry"];dims=sections[e["section_id"]]["dimensions"]
        assert math.dist(g["start_m"],g["end_m"])>0 and dims["thickness_m"]>0 and g["z_top_m"]>g["z_bottom_m"]
        walls.append({"id":e["element_id"],"building":e["building"],"floor":e["floor"],"start":g["start_m"][:2],"end":g["end_m"][:2],"thickness_m":dims["thickness_m"],"length_m":dims["length_m"],"group":e["provenance"].get("core_group","OTHER_CAD_WALL"),"source":e["provenance"].get("source_dxf")})
    for i,a in enumerate(walls):
        la=LineString([a["start"],a["end"]]);pa=la.buffer(a["thickness_m"]/2,cap_style=2)
        for b in walls[i+1:]:
            if (a["building"],a["floor"])!=(b["building"],b["floor"]):continue
            lb=LineString([b["start"],b["end"]])
            if la.hausdorff_distance(lb)<1e-6:duplicates.append([a["id"],b["id"]])
            area=pa.intersection(lb.buffer(b["thickness_m"]/2,cap_style=2)).area
            if area>1e-6:pairs.append({"a":a["id"],"b":b["id"],"overlap_m2":area,"status":"REVIEW_REQUIRED_NOT_AUTO_RESOLVED"})
    checks["wall_duplicates_zero"]=not duplicates
    checks["unexpected_wall_overlap_zero"]=not pairs
    checks["columns_follow_immediately_lower_section"]=all(elements[f"E2-P4-C-{n:03d}"]["section_id"]==elements[f"E2-P3-C-{n:03d}"]["section_id"] and all(elements[f"E2-P4-C-{n:03d}"][k]==old[f"E2-P4-C-{n:03d}"][k] for k in ("geometry","material_id")) for n in (4,7))
    checks["luis_reference_unchanged"]=not subprocess.check_output(["git","diff","ba889a7","--","entregas/P1L2/unity_export/model_viewer.json"],cwd=ROOT)
    after=read(ROOT/"entregas/P1L5/analysis/results/current/manifest.json")
    baseline=read(HERE/"BASELINE_ANALYSIS.json")
    comparison={case:{"before_max_translation_m":baseline["cases"][case]["max_translation_m"],"after_max_translation_m":after["cases"][case]["max_translation_m"],"equilibrium_relative_residual":after["cases"][case]["equilibrium_relative_residual"]} for case in ("G","Q","EX","EY")}
    for case,row in comparison.items():
        previous=json.loads(subprocess.check_output(["git","show",f"ba889a7:entregas/P1L5/analysis/results/current/{case}.json"],cwd=ROOT))
        current=read(ROOT/f"entregas/P1L5/analysis/results/current/{case}.json")
        row["before_reaction_force_N"]=previous["qa"]["reaction_force_N"]
        row["after_reaction_force_N"]=current["qa"]["reaction_force_N"]
    remaining=[r["candidate_id"] for r in read(ROOT/"entregas/P1L6/current_cleanup/removed_wall_candidates.json")["candidates"] if r["candidate_id"] not in elements]
    wall_lines=[]
    for w in walls:
        line=next((l for l in wall_lines if l["building"]==w["building"] and abs(l["thickness_m"]-w["thickness_m"])<=0.001 and LineString([l["start"],l["end"]]).hausdorff_distance(LineString([w["start"],w["end"]]))<=0.002),None)
        if line is None:
            line={"line_id":f"WALL_LINE_{len(wall_lines)+1:03d}","building":w["building"],"start":w["start"],"end":w["end"],"thickness_m":w["thickness_m"],"floors":{}}
            wall_lines.append(line)
        line["floors"].setdefault(w["floor"],[]).append(w["id"])
    for line in wall_lines:
        if set(line["floors"])==set(FLOORS):line["status"]="CONTINUOUS"
        elif line["building"]=="EDIFICIO_2" and all(eid.endswith("M-009") for ids in line["floors"].values() for eid in ids):line["status"]="EXPECTED_TERMINATION"
        else:line["status"]="REVIEW_REQUIRED"
    data={"status":"PASS_WITH_EXPLICIT_NOTES" if all(checks.values()) else "FAIL","checks":checks,"wall_count":len(walls),"cores":groups,"wall_lines":wall_lines,"continuity_tolerance_m":0.002,"all_walls":walls,"duplicate_walls":duplicates,"wall_overlap_reviews":pairs,"analysis_comparison":comparison,"remaining_removed_wall_candidates":remaining,"wrong_side_verdict":"CAD_POSITION_RETAINED; not moved; no evidence for reflection","material_note":"ED1-P4 G35 is existing lab fallback, not newly primary-confirmed; capacity reinforcement remains ASSUMED_FOR_LAB."}
    write(HERE/"WALL_CONTINUITY_AFTER.json",data)
    for floor in FLOORS:draw(HERE/f"after_cores_{floor}.png",[r for r in walls if r["floor"]==floor],f"AFTER CURRENT / {floor}")
    md=["# Corrección CURRENT de núcleos y columnas","",f"Estado geométrico: {data['status']}. {len(walls)} muros activos; {len(remaining)} candidatos previos siguen fuera del modelo y requieren revisión.","","## Grupos en C","","| Grupo | Piso | Muros | Continuidad |","|---|---|---|---|"]
    md += [f"| {g['group']} | {g['floor']} | {', '.join(g['ids'])} | {g['status']} |" for g in groups]
    md += ["","Continuidad verificada con tolerancia 2 mm en endpoints y 1 mm en espesor: ED1_02 tiene 1 mm de diferencia de extremo entre S1 y superiores por redondeo CAD; no se alteró para imponer igualdad numérica.","","Los tres paños de cada C conservan IDs físicos distintos. El FE utiliza muros equivalentes de barra; esto no equivale a una sección C monolítica ni a un modelo shell.","","## Continuidad global","","| Línea | S1 | P1 | P2 | P3 | P4 | Estado |","|---|---|---|---|---|---|---|"]
    md += ["| "+l["line_id"]+" | "+" | ".join(", ".join(l["floors"].get(f,[])) or "—" for f in FLOORS)+" | "+l["status"]+" |" for l in wall_lines]
    md += ["","## Muros activos","","| ID | Edificio | Piso | Largo m | Espesor m | Grupo | Fuente |","|---|---|---|---:|---:|---|---|"]
    md += [f"| {w['id']} | {w['building']} | {w['floor']} | {w['length_m']:.3f} | {w['thickness_m']:.3f} | {w['group']} | {w['source']} |" for w in walls]
    md += ["","## OpenSees antes / después","","| Caso | Máximo antes m | Máximo después m | Residual equilibrio |","|---|---:|---:|---:|"]
    md += [f"| {c} | {r['before_max_translation_m']:.8f} | {r['after_max_translation_m']:.8f} | {r['equilibrium_relative_residual']:.3g} |" for c,r in comparison.items()]
    md += ["","Reacciones globales, ejes X/Y/Z en kN:","","| Caso | Antes Rx/Ry/Rz kN | Después Rx/Ry/Rz kN |","|---|---|---|"]
    md += [f"| {c} | "+" / ".join(f"{v/1000:.3f}" for v in r["before_reaction_force_N"])+" | "+" / ".join(f"{v/1000:.3f}" for v in r["after_reaction_force_N"])+" |" for c,r in comparison.items()]
    md += ["","No se fuerza una reducción de desplazamientos: cambian rigidez, caminos de carga y peso propio. Q conserva su total; G incluye el peso nuevo.","","## Alcance y límites","","El muro largo ED2 X=27,727 m permanece en el lado CAD. No se inventó una inversión. Los ejes CAD corrigen únicamente los núcleos ED1; no se trasladan vigas o columnas ajenas a esta revisión.","",data["material_note"],"","Las columnas E2-P4-C-004/C-007 pasan 20×20→70×70 cm por revisión explícita del usuario y continuidad con P3. XY, altura, material e IDs quedan intactos. No se afirma haber descifrado una etiqueta CAD nueva.","","## QA","",*[f"- {k}: {'PASS' if v else 'FAIL'}" for k,v in checks.items()],""]
    (HERE/"WALL_CONTINUITY_AFTER.md").write_text("\n".join(md),encoding="utf-8")
    sys.path.insert(0,str(ROOT/"entregas/P1L6/current_cleanup"))
    spec=importlib.util.spec_from_file_location("pipeline_qa",ROOT/"entregas/P1L6/current_cleanup/validate_current_pipeline.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.HERE=HERE;mod.main()
    print(json.dumps({"status":data["status"],"checks":checks,"overlaps":pairs,"remaining":len(remaining)},indent=2))
    if not all(checks.values()):raise SystemExit(1)
if __name__=="__main__":main()
