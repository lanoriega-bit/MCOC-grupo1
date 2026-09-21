#!/usr/bin/env python3
"""QA de la consolidacion EXT-2 de muros EDIFICIO_2."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT/"entregas/P1L2/unity_export/model_combined_viewer.json"
AUDIT=ROOT/"entregas/POST_P1L4/ed2_walls/ed2_wall_face_audit.json"
OUT=ROOT/"entregas/POST_P1L4/ed2_walls/VALIDATION.md"
EXPECTED={"S1":11,"P1":11,"P2":11,"P3":11,"P4":10}

def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def main():
    model,audit=load(MODEL),load(AUDIT)
    walls=[x for x in model["solids"] if x.get("building")=="EDIFICIO_2" and x.get("category")=="wall"]
    counts=dict(Counter(x["floor"] for x in walls))
    keys=[(x["floor"],tuple(round(float(v),4) for v in x["start"][:2]),tuple(round(float(v),4) for v in x["end"][:2])) for x in walls]
    checks={
        "primary_audit_pass":audit.get("status")=="PASS",
        "counts_match_primary_audit":counts==EXPECTED,
        "unique_centerlines":len(keys)==len(set(keys)),
        "all_thicknesses_primary":all(x.get("thickness_confidence") in {"CONFIRMED_FROM_PLAN","CONFIRMED_FROM_GEOMETRY","CONFIRMED_FROM_GEOMETRY_AND_LABEL"} for x in walls),
        "all_corrections_traceable":all(x.get("post_p1l4_correction",{}).get("primary_source") in {"2024_22-101.dxf","2024_22-102.dxf"} for x in walls),
        "no_opensees_results_recalculated":all(x.get("post_p1l4_correction",{}).get("results_compatibility")=="P1L4_HISTORICAL_RESULTS_NOT_RECALCULATED" for x in walls),
    }
    status="PASS" if all(checks.values()) else "FAIL"
    lines=["# Validación EXT-2 — muros EDIFICIO_2","",f"Estado: `{status}`","","| Control | Resultado |","|---|---|"]+[f"| {k} | `{'PASS' if v else 'FAIL'}` |" for k,v in checks.items()]+["",f"Muros físicos: `{len(walls)}`. Por piso: `{counts}`.","","Unity consume esta geometría, pero los resultados OpenSees P1L4 permanecen históricos."]
    OUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"ED2_WALL_VALIDATION: {status}")
    if status!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
