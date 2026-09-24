"""Second scoped cleanup. No solver, historical results or reference edits.

Audit is read-only to canonical inputs; --apply-walls is a baseline-guarded
migration. --finalize derives current diagnostics after topology regeneration.
"""
import copy
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path
from shapely.geometry import LineString, Point, box

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'entregas/PRE_P1L5/second_structural_cleanup'
MODEL = ROOT / 'entregas/P1L2/unity_export/model_combined_viewer.json'
SOURCE = ROOT / 'entregas/P1L2/unity_export/model_1_audited_corrected.json'
FE = ROOT / 'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
ARCHIVE = ROOT / 'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json'
STREAM = ROOT / 'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
BASE = 'd323e248434162bfc8cd5a888ad6578cd3600ac9'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def old(p):
    return json.loads(subprocess.check_output(['git','show',BASE+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT))
def center(s): return s.get('center') or [(a+b)/2 for a,b in zip(s['start'],s['end'])]
def footprint(s):
    if 'start' in s:
        return LineString([s['start'][:2],s['end'][:2]]).buffer(s['width_m']/2,cap_style=2)
    x,y=center(s)[:2]; w=s['width_m']/2; d=s.get('depth_m',s['width_m'])/2
    return box(x-w,y-d,x+w,y+d)
def ids_pending(fe): return {g for c in fe['floating_excluded']['components'] for g in c['geometry_element_ids']}

def audit_walls():
    model=old(MODEL); fe=old(FE); solids=model['solids']; bytag={s['solidTag']:s for s in solids}
    walls=[s for s in solids if s['building']=='EDIFICIO_1' and s['category']=='wall']
    wallids={s['id'] for s in walls}
    # Archived walls may still have a generated support. They remain primary
    # provenance, not reintroduced physical/FE members.
    wall_history=walls+[r['before'] for r in old(ARCHIVE)['exclusions'] if r['before']['building']=='EDIFICIO_1' and r['before']['category']=='wall']
    retained=[s for s in solids if s['category'] in ('column','beam','wall') and s['id'] not in wallids]
    visual=[]
    for s in solids:
        if s['building']!='EDIFICIO_1' or s['category']!='support': continue
        # Precise provenance or identical wall axis/extents is required, not proximity.
        refs=[bytag[t]['id'] for t in s.get('sourceTags',[]) if t in bytag]
        exact_walls=[]
        if 'start' in s:
            axis=LineString([s['start'][:2],s['end'][:2]])
            exact_walls=[w['id'] for w in wall_history if w['floor']=='S1' and axis.hausdorff_distance(LineString([w['start'][:2],w['end'][:2]]))<.001]
        contact=[]
        for t in retained:
            if t['building']!=s['building'] or abs(t['coordinates']['z_bottom_m'])>.01: continue
            if footprint(s).buffer(.001).intersects(footprint(t)): contact.append(t['id'])
        columns=[g for g in set(refs+contact) if g in {t['id'] for t in retained if t['category']=='column'}]
        others=[g for g in contact if g not in columns]
        if (columns or others) and exact_walls: kind='SHARED_SUPPORT'
        elif columns: kind='COLUMN_SUPPORT'
        elif others: kind='SHARED_SUPPORT'
        elif exact_walls: kind='WALL_ONLY_SUPPORT'
        else: kind='UNKNOWN_SUPPORT'
        visual.append({'id':s['id'],'classification':kind,'source_references':refs,'exact_wall_axes':exact_walls,'retained_contacts':contact,'column_contacts':columns,'action':'EXCLUDE' if kind=='WALL_ONLY_SUPPORT' else 'PRESERVE'})
    analytical=[]
    for n in fe['supports']:
        node=fe['nodes'][str(n)]
        if node['building']!='EDIFICIO_1':continue
        incident=[e for e in fe['elements'] if n in (e['node_i'],e['node_j'])]
        kept={e['element_id'] for e in incident if e['element_id'] not in wallids}
        columns={e['element_id'] for e in incident if e['type']=='column'}
        removed={e['element_id'] for e in incident if e['element_id'] in wallids}
        kind='SHARED_SUPPORT' if kept and removed else 'COLUMN_SUPPORT' if columns else 'SHARED_SUPPORT' if kept else 'WALL_ONLY_SUPPORT' if removed else 'UNKNOWN_SUPPORT'
        analytical.append({'baseline_node':n,'coordinate':[node[k] for k in ('x','y','z')],'building':node['building'],'classification':kind,'retained_members':sorted(kept),'excluded_walls':sorted(removed),'action':'EXCLUDE' if kind=='WALL_ONLY_SUPPORT' else 'PRESERVE'})
    result={'baseline_commit':BASE,'walls':sorted(wallids),'visual_supports':visual,'analytical_supports':analytical,'visual_counts':dict(Counter(r['classification'] for r in visual)),'analytical_counts':dict(Counter(r['classification'] for r in analytical)),'note':'Support visuals are not FE constraints. Incidence is rechecked after rebuilding; no virtual supports or stiffness are added.'}
    write(OUT/'wall_scope_audit.json',result)
    print(json.dumps({k:result[k] for k in ['visual_counts','analytical_counts']},indent=2))
    return result

def apply_walls():
    audit=audit_walls(); model=read(MODEL); before=old(MODEL)
    assert model==before,'Wall migration only accepts the reviewed d323e24 input'
    source=read(SOURCE); original=copy.deepcopy(source)
    ids=set(audit['walls'])|{r['id'] for r in audit['visual_supports'] if r['action']=='EXCLUDE'}
    mapping={s['solidTag']:s for s in before['solids']}; archive=read(ARCHIVE)
    diffpath=ROOT/'entregas/P1L2/edificio/datos/luis_reference_diff.json'; diff=read(diffpath)
    rows=[]; kept=[]
    for s in source['solids']:
        prior=mapping[s['solidTag']]; gid=prior['id']
        if gid not in ids: kept.append(s); continue
        kind='WALL_REMOVED' if prior['category']=='wall' else 'WALL_SUPPORT_REMOVED'
        reason='USER_SCOPE_DECISION_ED1_WALLS'
        archive['exclusions'].append({'element_id':gid,'before':prior,'reason':reason,'source':'Explicit second cleanup scope; wall_scope_audit.json','historical_commit':BASE,'removed_from_current_geometry':True,'removed_from_FE':True,'results_policy':'Historical immutable; no current applied loads or results'})
        diff['changes'].append({'id':gid,'solidTag':s['solidTag'],'category':s['category'],'old_geometry':copy.deepcopy(s),'new_geometry':'REMOVED','reason':reason,'classification':'USER_APPROVED_SCOPE_EXCLUSION','evidence':'second_structural_cleanup/wall_scope_audit.json','confidence':'EXPLICIT_USER_SCOPE_NOT_CAD_ABSENCE','review_checkpoint':'PRE5_SECOND_WALL_SCOPE'})
        rows.append({'id':gid,'type':kind,'reason':reason,'source':'wall_scope_audit.json','historical_ids':[gid]})
    assert len(rows)==len(ids)
    source['solids']=kept
    source['current_scope_revision']['second_cleanup']=BASE
    archive['current_revision']='SECOND_STRUCTURAL_CLEANUP'
    write(SOURCE,source); write(ARCHIVE,archive); write(diffpath,diff)
    for script in ('build_combined_model.py','enrich_combined_model.py'):
        subprocess.run([sys.executable,str(ROOT/'entregas/P1L2/edificio/scripts'/script)],cwd=ROOT,check=True)
    now=read(MODEL); assert {s['id'] for s in now['solids']}=={s['id'] for s in before['solids']}-ids
    write(OUT/'current_review_changes.json',{'baseline_commit':BASE,'geometry_version':sha(MODEL),'rows':rows,'current_results':'NONE'})
    print('WALL_SCOPE_APPLIED',len(audit['walls']),'walls;',len(ids)-len(audit['walls']),'support visuals')

def finalize():
    model=read(MODEL); now={s['id']:s for s in model['solids']}; before={s['id']:s for s in old(MODEL)['solids']}
    fe=read(FE); prev=old(FE); audit=read(OUT/'wall_scope_audit.json'); archive=read(ARCHIVE)
    removed={r['element_id'] for r in archive['exclusions']}; aliases=archive['merged_id_aliases']; pending=ids_pending(fe)
    changes=read(OUT/'current_review_changes.json'); changes['geometry_version']=sha(MODEL)
    checks={}
    def check(k,v):checks[k]='PASS' if v else 'FAIL'
    check('ED1_ACTIVE_WALLS_ZERO',not any(s['building']=='EDIFICIO_1' and s['category']=='wall' for s in now.values()))
    check('COLUMN_SUPPORTS_PRESERVED',all(r['id'] in now for r in audit['visual_supports'] if r['classification']=='COLUMN_SUPPORT'))
    check('SHARED_SUPPORTS_PRESERVED',all(r['id'] in now for r in audit['visual_supports'] if r['classification']=='SHARED_SUPPORT'))
    check('UNKNOWN_SUPPORTS_PRESERVED',all(r['id'] in now for r in audit['visual_supports'] if r['classification']=='UNKNOWN_SUPPORT'))
    check('COLUMNS_PRESERVED',all(g in now for g,s in before.items() if s['category']=='column'))
    check('SLABS_PRESERVED',all(g in now and now[g]==s for g,s in before.items() if s['category']=='slab'))
    check('STABLE_IDS',set(now)==set(before)-removed-set(aliases) and all(s['solidTag']==before[g]['solidTag'] for g,s in now.items()))
    check('CROSSWALK',len(fe['crosswalk'])==len(fe['elements']) and all(r['element_id'] in now for r in fe['crosswalk']))
    check('NO_EXCLUDED_FE',not (removed|set(aliases))&{e['element_id'] for e in fe['elements']})
    check('FE_INPUT_HASH',fe['inputs']['geometry_sha256']==sha(MODEL))
    check('NO_ANALYSIS',fe['run_policy']['opensees_run'] is False)
    check('LUIS_REFERENCE',read(ROOT/'entregas/P1L2/unity_export/model_viewer.json')==old(ROOT/'entregas/P1L2/unity_export/model_viewer.json'))
    support_ids=set(fe['supports']); protection=[]
    for r in audit['analytical_supports']:
        if r['action']=='EXCLUDE':continue
        # IDs are regenerated: verify retained base members still have a fixed end.
        members=[e for e in fe['elements'] if e['element_id'] in r['retained_members']]
        ok=bool(members) and all(e['node_i'] in support_ids or e['node_j'] in support_ids for e in members)
        protection.append({**r,'preserved_after_rebuild':ok})
    check('FE_COLUMN_SHARED_SUPPORTS_PRESERVED',all(r['preserved_after_rebuild'] for r in protection))
    summary={'baseline_commit':BASE,'geometry_solids':len(now),'ED1_active_walls':0,'walls_excluded_this_revision':len(audit['walls']),'support_visuals_excluded_this_revision':sum(r['action']=='EXCLUDE' for r in audit['visual_supports']),'FE_wall_only_supports_removed':sum(r['action']=='EXCLUDE' for r in audit['analytical_supports']),'FE_members':len(fe['elements']),'FE_pending':len(pending),'FE_components':len(fe['floating_excluded']['components']),'FE_constraints':len(fe['constraints']),'FE_supports':len(fe['supports']),'pending_ids':sorted(pending),'new_pending_ids':sorted(pending-ids_pending(prev)),'current_results':'NONE','analysis_run':False}
    write(OUT/'review_qa.json',{'summary':summary,'checks':checks,'FE_support_protection':protection})
    bridge=old(STREAM/'fe_pending_review.json'); oldrows={r['id']:r for r in bridge['rows']}; rows=[]
    for i,g in enumerate(sorted(pending),1):
        s=now[g]; row=copy.deepcopy(oldrows.get(g,{'id':g,'building':s['building'],'floor':s['floor'],'priority':'A','axes':s.get('location_description'),'plan':s.get('source_dxf'),'question':'Comprobar trayectoria física de cargas; no introducir apoyos ficticios.','neighbors':[g],'level_z':s.get('model_z_m',0)}))
        row.update(label=f'{i:02}/{len(pending)}',problem='SIN CAMINO FE A APOYO; nuevo diagnóstico tras saneamiento.',neighbors=sorted({g}|{x for c in fe['floating_excluded']['components'] if g in c['geometry_element_ids'] for x in c['geometry_element_ids']}|{x for x in row['neighbors'] if x in now}))
        rows.append(row)
    bridge.update(geometry_version=sha(MODEL),rows=rows); write(STREAM/'fe_pending_review.json',bridge)
    changes['summary']=summary; write(OUT/'current_review_changes.json',changes); write(STREAM/'current_review_changes.json',changes)
    stacks_path=OUT/'COLUMN_VERTICAL_STACKS.json'
    if stacks_path.exists():
        stacks=read(stacks_path); stacks['geometry_version']=sha(MODEL)
        write(STREAM/'column_vertical_stacks.json',stacks)
    receptor=[]
    # Include all prior exclusions and merged aliases, not just this checkpoint.
    allids=set(before)|removed|set(aliases)
    for g in sorted(allids):
        receptor.append({'historical_id':g,'current_id':None if g in removed else aliases.get(g,g),'status':'EXCLUDED_NO_CURRENT_RECEPTOR' if g in removed else 'REBUILD_REQUIRED_NO_CURRENT_LOADS','loads_applied':False})
    write(OUT/'current_tributary_receptor_crosswalk.json',{'geometry_version':sha(MODEL),'status':'ELIGIBILITY_ONLY_NOT_LOAD_ALLOCATION','rows':receptor})
    md=['# ED1 wall scope removal audit','',f'Baseline: `{BASE}`. User scope decision, NOT a finding that the real building has no walls.','',f"{summary['walls_excluded_this_revision']} walls and {summary['support_visuals_excluded_this_revision']} exclusively wall support visuals excluded. {summary['FE_wall_only_supports_removed']} exclusively wall FE support nodes removed by rebuilding. These are distinct counts.",'','All columns, column supports and shared/unknown support visuals preserved. Removing real walls changes the structural idealization: no current analysis or adequacy certification.','', '| Support visual | Class | Wall correspondence | Retained members | Action |','|---|---|---|---|---|']
    for r in audit['visual_supports']:md.append(f"| {r['id']} | {r['classification']} | {', '.join(r['exact_wall_axes'])} | {', '.join(r['retained_contacts'])} | {r['action']} |")
    md+=['','## Excluded wall IDs','',', '.join(audit['walls']),'','## Fresh topology','',json.dumps(summary,ensure_ascii=False,indent=2),'','## QA','']+[f'- {k}: {v}' for k,v in checks.items()]
    (ROOT/'entregas/PRE_P1L5/ED1_WALL_SCOPE_REMOVAL_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'summary':summary,'checks':checks},indent=2))
    assert 'FAIL' not in checks.values()

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if '--apply-walls' in sys.argv: apply_walls()
    elif '--finalize' in sys.argv: finalize()
    else: audit_walls()
