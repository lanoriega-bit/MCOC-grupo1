"""PRE5 global regression and readiness gate; no OpenSees run."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
BASE='bbc5188'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
    checks=[]
    scripts=[
        'entregas/P1L2/edificio/scripts/validate_axes_and_calce.py',
        'entregas/P1L2/edificio/scripts/validate_combined_geometry.py',
        'entregas/P1L2/edificio/scripts/validate_luis_reference_diff.py',
        'entregas/P1L2/edificio/scripts/validate_core_axis_continuity.py',
        'entregas/P1L2/edificio/scripts/validate_ed1_walls.py',
        'entregas/POST_P1L4/scripts/validate_ed2_walls.py',
        'entregas/P1L2/edificio/scripts/validate_ed1_beams.py',
        'entregas/POST_P1L4/scripts/validate_ed2_beams.py',
        'entregas/POST_P1L4/scripts/validate_ext5_remaining.py',
        'entregas/P1L3/scripts/validate_unity_integration.py',
        'entregas/PRE_P1L5/scripts/audit_historical_equilibrium.py',
        'entregas/PRE_P1L5/scripts/validate_current_readiness.py']
    for path in scripts:
        p=subprocess.run([sys.executable,str(ROOT/path)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        checks.append({'script':path,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'output':p.stdout+p.stderr})
        print(path,p.returncode,flush=True)
    tags={'entregap1l2':'d2e40be4292b2a55b2e0db8be6be51cd31535bd6','P1L3_DELIVERED':'c847c131512d00cc85bb95aa5719278d70da0c2b','P1L4_FINAL':'56e24ac0568b24eba3cf119f2e3cc66fc0af3a35'}
    for tag,commit in tags.items():
        actual=git('rev-parse',tag+'^{commit}').decode().strip()
        checks.append({'check':'immutable '+tag,'status':'PASS' if actual==commit else 'FAIL','commit':actual})
    protected=['entregas/P1L2/unity_export/model_viewer.json','entregas/P1L3/results',
               'entregas/P1L3/capacidad_ha','entregas/P1L3/José/results',
               'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/p1l4_jose',
               'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/analysis_cases.json',
               'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/analysis_results.json',
               'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/capacity_ha.json']
    changed=git('diff','--name-only',BASE,'--',*protected).decode().splitlines()
    checks.append({'check':'historical_results_and_luis_unchanged','status':'PASS' if not changed else 'FAIL','changed':changed})
    path='entregas/P1L2/unity_export/model_combined_viewer.json';m=read(path);old=json.loads(git('show',BASE+':'+path))
    ignore={'material','material_source','material_confidence','concrete_fc_pa','reinforcement_grade','reinforcement_fy_pa','material_scope_note','property_correction'}
    def stable(s):return {k:v for k,v in s.items() if k not in ignore}
    same=[stable(s) for s in m['solids']]==[stable(s) for s in old['solids']]
    props=[s for s in m['solids'] if s.get('property_correction')]
    ed1=[s for s in props if s['building']=='EDIFICIO_1'];ed2=[s for s in props if s['building']=='EDIFICIO_2']
    correct=len(ed1)==391 and len(ed2)==361 and all(s['concrete_fc_pa']==35e6 and s['material_confidence']=='CONFIRMED_FROM_PLAN' for s in props)
    correct=correct and all(s['floor'] in ('S1','P1','P2','P3') and s['source_dxf'] in ('2017_67-101.dxf','2017_67-102.dxf') for s in ed1)
    checks.append({'check':'geometry_sections_unchanged_scoped_materials','status':'PASS' if same and correct else 'FAIL','property_updated':len(props)})
    state=read('entregas/PRE_P1L5/project_state.json')
    bundle=read(STREAM/'model_viewer.json');same_state=(OUT/'project_state.json').read_bytes()==(STREAM/'project_state.json').read_bytes()
    fresh=state['geometry_sha256']==hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    checks.append({'check':'canonical_unity_metadata_identity','status':'PASS' if m==bundle and fresh and same_state else 'FAIL'})
    proposal=read(OUT/'constraint_normalization_proposal.json')
    checks.append({'check':'constraint_proposal_only','status':'PASS' if proposal['kinematic_test']=='PASS' and proposal['status']=='ALGEBRAIC_PROPOSAL_NOT_APPLIED' else 'FAIL'})
    qa=ROOT/'entregas/P1L3/José/viewer_unity/Builds/CurrentReview/QA/UX_QA.txt'
    ui=qa.exists() and qa.read_text().startswith('PASS') and qa.stat().st_mtime>max(p.stat().st_mtime for p in (ROOT/'entregas/P1L3/José/viewer_unity/Assets/Scripts').glob('*.cs'))
    checks.append({'check':'unity_latest_source_runtime','status':'PASS' if ui else 'FAIL','evidence':qa.relative_to(ROOT).as_posix()})
    docs=['CROSS_GROUP_FEATURE_MATRIX.md','EXTERNAL_INTELLIGENCE_SANTIAGO.md','EXTERNAL_INTELLIGENCE_CACERES.md','DELIVERY_RETROSPECTIVE_AUDIT.md','PRE_P1L5_STATUS.md','REMAINING_STRUCTURAL_AUDIT.md']
    checks.append({'check':'documentation','status':'PASS' if all((OUT/p).is_file() for p in docs) else 'FAIL'})
    fail=any(r['status']=='FAIL' for r in checks)
    gates={'AXES':'PASS','FLOORS':'PASS','COLUMNS':'PASS_WITH_NOTE','WALLS':'PASS_WITH_NOTE','BEAMS':'REVIEW_REQUIRED','SLABS':'REVIEW_REQUIRED','PROPERTIES':'REVIEW_REQUIRED','CONNECTIVITY':'REVIEW_REQUIRED','CROSSWALK':'PASS','LOADS':'REVIEW_REQUIRED','UNITY':'PASS' if ui else 'FAIL','DOCUMENTATION':'PASS' if checks[-1]['status']=='PASS' else 'FAIL'}
    for c in checks:
        if c['status']!='FAIL':continue
        name=c.get('script',c.get('check',''))
        for needle,key in [('axes','AXES'),('combined_geometry','FLOORS'),('walls','WALLS'),('beams','BEAMS'),('scoped_materials','PROPERTIES'),('ext5','CONNECTIVITY'),('unity','UNITY')]:
            if needle in name:gates[key]='FAIL'
    out={'regression_status':'FAIL' if fail else 'PASS','baseline_status':'BLOCKED','opensees_run':False,'checks':checks,'technical_gates':gates,
         'note':'Passing regressions do not certify pending physical properties, load coverage or FE formulation.'}
    (OUT/'global_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# PRE5-1 — validación global','','Regresiones: '+out['regression_status']+'. Baseline: BLOCKED. No se ejecutó OpenSees.','', '| Bloque | Estado técnico |','|---|---|']
    lines += [f'| {k} | {v} |' for k,v in gates.items()]
    lines += ['', 'Los estados técnicos incluyen pendientes físicos; no confundir PASS del test con completitud.', '', '| Prueba | Resultado |','|---|---|']
    lines += [f"| {c.get('script',c.get('check'))} | {c['status']} |" for c in checks]
    (OUT/'GLOBAL_VALIDATION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    roles={'geometry':path,'materials':'entregas/PRE_P1L5/primary_material_catalog.json',
           'fe_candidate_not_approved':'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json',
           'loads_audited_not_applied':'entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json',
           'unity_scene':'entregas/P1L3/José/viewer_unity/Assets/Main.unity',
           'project_state':'entregas/PRE_P1L5/project_state.json'}
    baseline={'status':'BLOCKED','branch':'codex/post-p1l4-structural-audit','current_results':'NONE',
              'fe_canonical_approved':None,'loads_current_approved':None,'historical_tags':tags,
              'files':{k:{'path':v,'sha256':hashlib.sha256((ROOT/v).read_bytes()).hexdigest()} for k,v in roles.items()},
              'regression_status':out['regression_status'],'technical_gates':gates,
              'blockers_document':'PRE_P1L5_STATUS.md','remaining_fe':state['pending'],
              'beam_heights_pending':state['beam_heights_pending'],'opensees_run':False}
    (OUT/'PRE_P1L5_BASELINE.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out['regression_status']);return int(fail)
if __name__=='__main__':raise SystemExit(main())
