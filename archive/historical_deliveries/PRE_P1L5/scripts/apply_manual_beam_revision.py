"""Apply the explicitly requested PRE-P1L5 beam corrections once.

No loads, results, OpenSees run, section, material, or global axes are changed.
"""
import copy
import hashlib
import json
import math
import subprocess
import sys
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5/manual_beam_revision'
MODEL=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
ED1=ROOT/'entregas/P1L2/unity_export/model_1_audited_corrected.json'
ED2=ROOT/'entregas/P1L2/unity_export/model_2_viewer.json'
ARCHIVE=ROOT/'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json'
CHANGES=ROOT/'entregas/PRE_P1L5/second_structural_cleanup/current_review_changes.json'
DIFF=ROOT/'entregas/P1L2/edificio/datos/luis_reference_diff.json'
BASE='b5d07f3c5c482b8fa13afb37d8b2869ca46aec82'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ed1_local(s):
    row=copy.deepcopy(s)
    for key in ('start','end','center'):
        if key in row:row[key][0]-=27.491
    return row

GROUPS=[
 ['E1-P4-V-004','E1-P4-V-005'],
 *[[f'E2-P4-V-{a:03}',f'E2-P4-V-{b:03}'] for a,b in [(82,83),(72,73),(79,75),(61,62),(51,50),(58,54),(56,52),(53,57),(40,41),(31,25),(26,32),(27,33)]],
 ['E1-P3-V-005','E1-P3-V-004'],
 ['E1-P2-V-005','E1-P2-V-004'],['E1-P2-V-111','E1-P2-V-108'],
 ['E1-P2-V-013','E1-P2-V-019'],['E1-P2-V-048','E1-P2-V-051'],['E1-P2-V-076','E1-P2-V-080'],
 ['E1-P2-V-097','E1-P2-V-100'],['E1-P2-V-029','E1-P2-V-032'],['E1-P2-V-060','E1-P2-V-067'],
 ['E1-P2-V-087','E1-P2-V-091'],
 ['E1-P1-V-096','E1-P1-V-094'],['E1-P1-V-001','E1-P1-V-002'],
 ['E1-P1-V-086','E1-P1-V-087'],['E1-P1-V-078','E1-P1-V-088'],
 ['E1-S1-V-018','E1-S1-V-021','E1-S1-V-020'],
 ['E1-S1-V-025','E1-S1-V-030','E1-S1-V-026','E1-S1-V-011'],
]
EXTENSIONS={
 'E2-P4-V-011':[-3.548,4.2657,19.4], 'E2-P4-V-012':[-3.548,11.8857,19.4],
 'E1-P1-V-066':[57.491,8.9,7.52], 'E1-P1-V-067':[57.491,16.15,7.52],
}
NEW_IDS={'S1':'E2-S1-V-045','P1':'E2-P1-V-045','P2':'E2-P2-V-045','P3':'E2-P3-V-045','P4':'E2-P4-V-092'}
LEVEL={'S1':3.56,'P1':7.52,'P2':11.48,'P3':15.44,'P4':19.4}

def choose(ids,byid):
    def rank(g):
        s=byid[g];label=s.get('geometry_confirmation',{}).get('status')=='CONFIRMED_LABEL_WIDTH'
        return (label,math.dist(s['start'],s['end']),g)
    return max(ids,key=rank)

def validate_group(ids,byid):
    ss=[byid[g] for g in ids];a=ss[0];length=math.dist(a['start'],a['end']);u=[(a['end'][k]-a['start'][k])/length for k in (0,1)]
    cross=lambda q:(q[0]-a['start'][0])*u[1]-(q[1]-a['start'][1])*u[0]
    assert all(s['category']=='beam' and s['building']==a['building'] and s['floor']==a['floor'] for s in ss)
    assert max(abs(cross(q)) for s in ss for q in (s['start'],s['end']))<.002
    assert all(abs(s['start'][2]-a['start'][2])<.002 and s['width_m']==a['width_m'] and s['height_m']==a['height_m'] and s.get('material')==a.get('material') for s in ss)

def mutate_source(path,byid,plans,retired,extensions,new_beams):
    source=read(path); mapping={s.get('preserved_viewer_id'):s for s in source['solids']}
    dx=27.491 if path==ED1 else 0.0
    for p in plans:
        if p['canonical'] not in mapping:continue
        local=[mapping[g] for g in p['ids']];target=mapping[p['canonical']]
        pts=[q for s in local for q in (s['start'],s['end'])]
        a,b=max(combinations(pts,2),key=lambda x:math.dist(*x));a,b=sorted((a,b))
        target.update(start=a,end=b,length_m=math.dist(a,b),canonical_element_id=p['canonical'])
        target['merged_from']=sorted(set(target.get('merged_from',[])+[g for g in p['ids'] if g!=p['canonical']]+[h for s in local for h in s.get('merged_from',[])]))
        target['sourceTags']=sorted({t for s in local for t in s.get('sourceTags',[])})
        target['geometry_confirmation']['face_ids']=target['sourceTags']
        target['post_p1l4_correction']={'correction_type':'BEAM_MERGED','reason':'USER_CONFIRMED_CONTINUOUS_PHYSICAL_BEAM; collinear, same section/material/Z; intermediate geometric cuts are artificial.','primary_source':target['source_dxf'],'confidence':'USER_CONFIRMED_WITH_CANONICAL_GEOMETRY','checkpoint':'PRE5_MANUAL_BEAM_REVISION','results_compatibility':'HISTORICAL_NOT_RECALCULATED'}
    for gid,target_global in extensions.items():
        if gid not in mapping:continue
        s=mapping[gid];target=[target_global[0]-dx,target_global[1],target_global[2]]
        old=[s['start'][:],s['end'][:]];which=min((0,1),key=lambda i:math.dist(old[i],target))
        if which==0:s['start']=target
        else:s['end']=target
        s['length_m']=math.dist(s['start'],s['end'])
        s['post_p1l4_correction']={'correction_type':'BEAM_ENDPOINT_RECONNECTED','reason':'Disconnected trimmed endpoint extended along its unchanged axis to the existing structural joint; no support created.','primary_source':s['source_dxf'],'confidence':'USER_CONFIRMED_WITH_EXISTING_NODE','checkpoint':'PRE5_MANUAL_BEAM_REVISION','results_compatibility':'HISTORICAL_NOT_RECALCULATED'}
    source['solids']=[s for s in source['solids'] if s.get('preserved_viewer_id') not in retired and s.get('preserved_viewer_id')!='E1-S1-V-005']
    if path==ED2:source['solids'].extend(copy.deepcopy(new_beams))
    replacements={g:p['canonical'] for p in plans for g in p['ids'] if g!=p['canonical']}
    def relink(v):
        if isinstance(v,list):return [relink(x) for x in v]
        if isinstance(v,dict):return {k:relink(x) for k,x in v.items()}
        return replacements.get(v,v) if isinstance(v,str) else v
    source['labels']=relink(source.get('labels',[]))
    write(path,source)

def replace_diff_entries(diff,byid,plans):
    diff['changes']=[r for r in diff['changes'] if r.get('review_checkpoint')!='PRE5_MANUAL_BEAM_REVISION']
    current={s.get('preserved_viewer_id'):s for s in read(ED1)['solids']}
    def append(g,new):
        old=ed1_local(byid[g])
        diff['changes'].append({'id':g,'solidTag':old['solidTag'],'category':'beam','old_geometry':old,'new_geometry':new,'reason':'USER_MANUAL_BEAM_REVISION','classification':'GEOMETRY_CORRECTION','evidence':'manual_beam_revision/applied_revision.json','review_checkpoint':'PRE5_MANUAL_BEAM_REVISION'})
    for p in plans:
        if not p['canonical'].startswith('E1-'):continue
        append(p['canonical'],current[p['canonical']])
        for g in p['absorbed']:append(g,'REMOVED')
    for gid in ('E1-P1-V-066','E1-P1-V-067'):append(gid,current[gid])
    append('E1-S1-V-005','REMOVED')
    return diff

def main():
    before=read(MODEL);byid={s['id']:s for s in before['solids']};archive=read(ARCHIVE);changes=read(CHANGES);diff=read(DIFF)
    assert archive['current_revision']=='SECOND_STRUCTURAL_CLEANUP' and not any(r.get('checkpoint')=='PRE5_MANUAL_BEAM_REVISION' for r in changes['rows']),'Migration already applied'
    assert all(g in byid for ids in GROUPS for g in ids)
    plans=[];retired=set()
    for ids in GROUPS:
        validate_group(ids,byid);canonical=choose(ids,byid);absorbed=[g for g in ids if g!=canonical]
        assert not retired.intersection(ids);retired.update(absorbed)
        pts=[q for g in ids for q in (byid[g]['start'],byid[g]['end'])];a,b=max(combinations(pts,2),key=lambda x:math.dist(*x))
        plans.append({'canonical':canonical,'ids':ids,'absorbed':absorbed,'endpoints':sorted((a,b)),'gap_total_m':math.dist(a,b)-sum(math.dist(byid[g]['start'],byid[g]['end']) for g in ids)})
    new=[];ref=byid['E2-P3-V-006']
    for floor,gid in NEW_IDS.items():
        assert gid not in byid
        s={k:copy.deepcopy(v) for k,v in ref.items() if k not in ('id','human_id','elementTag','legacy_solidTag','coordinates','axis_location','location_description','axis_x','axis_y','model_z_m','source_elevation_m','source_sheet','material_source','material_confidence','concrete_fc_pa','reinforcement_grade','reinforcement_fy_pa','material_scope_note','property_correction')}
        z=LEVEL[floor];s.update(solidTag=f'SOL2_PRE5_{floor}_beam_001',floor=floor,start=[-3.348,8.9007,z],end=[-0.298,8.9007,z],length_m=3.05,sourceTag=f'PRE5-{floor}-MISSING-BEAM-001',sourceTags=[],source_dxf='2024_22-102.dxf' if floor=='P4' else '2024_22-101.dxf',source_floor={'S1':'1S','P1':'1','P2':'2','P3':'3','P4':'4'}[floor],preserved_viewer_id=gid)
        s['geometry_confirmation']={'status':'CONFIRMED_USER_VERTICAL_REPETITION','reference_element':'E2-P3-V-006','vertical_pattern':'S1-P4','width_m':.3}
        s['post_p1l4_correction']={'correction_type':'BEAM_ADDED','reason':'User-identified missing member repeated at equivalent C-001 / V-002+V-003 joint on S1-P4.','reference_element':'E2-P3-V-006','confidence':'USER_CONFIRMED_VERTICAL_STRUCTURAL_PATTERN','checkpoint':'PRE5_MANUAL_BEAM_REVISION','results_compatibility':'NONE_CURRENT'}
        new.append(s)
    mutate_source(ED1,byid,plans,retired,EXTENSIONS,new)
    mutate_source(ED2,byid,plans,retired,EXTENSIONS,new)
    for p in plans:
        row={'id':p['canonical'],'type':'BEAM_MERGED','reason':'USER_CONFIRMED_CONTINUOUS_PHYSICAL_BEAM','source':'manual beam revision + canonical geometry/sourceTags','historical_ids':p['ids'],'merged_from':p['absorbed'],'gap_total_m':p['gap_total_m'],'checkpoint':'PRE5_MANUAL_BEAM_REVISION'}
        changes['rows'].append(row);archive['merge_history'].append(row)
        for g in p['absorbed']:archive['merged_id_aliases'][g]=p['canonical']
    for gid,target in EXTENSIONS.items():changes['rows'].append({'id':gid,'type':'BEAM_ENDPOINT_RECONNECTED','reason':'Extended along beam axis to existing structural joint; no support created.','source':byid[gid]['source_dxf'],'historical_ids':[gid],'old_endpoints':[byid[gid]['start'],byid[gid]['end']],'target':target,'checkpoint':'PRE5_MANUAL_BEAM_REVISION'})
    for s in new:changes['rows'].append({'id':s['preserved_viewer_id'],'type':'BEAM_ADDED','reason':s['post_p1l4_correction']['reason'],'source':s['source_dxf']+' / reference E2-P3-V-006','historical_ids':[],'checkpoint':'PRE5_MANUAL_BEAM_REVISION'})
    removed=byid['E1-S1-V-005'];archive['exclusions'].append({'element_id':'E1-S1-V-005','before':removed,'reason':'USER_CONFIRMED_INVALID_ISOLATED_GEOMETRY','source':'Manual beam revision; prior FE pending after ED1 wall removal','historical_commit':BASE,'removed_from_current_geometry':True,'removed_from_FE':True,'results_policy':'Historical immutable; no current loads/results'})
    changes['rows'].append({'id':'E1-S1-V-005','type':'BEAM_REMOVED','reason':'USER_CONFIRMED_INVALID_ISOLATED_GEOMETRY; removal eliminates prior pending member, no valid load path depended on it.','source':removed['source_dxf'],'historical_ids':['E1-S1-V-005'],'checkpoint':'PRE5_MANUAL_BEAM_REVISION'})
    archive['current_revision']='MANUAL_BEAM_REVISION'
    diff=replace_diff_entries(diff,byid,plans)
    write(ARCHIVE,archive);write(DIFF,diff);write(CHANGES,changes)
    for script in ('build_combined_model.py','enrich_combined_model.py'):
        subprocess.run([sys.executable,str(ROOT/'entregas/P1L2/edificio/scripts'/script)],cwd=ROOT,check=True)
    now={s['id']:s for s in read(MODEL)['solids']}
    assert set(now)==(set(byid)-retired-{'E1-S1-V-005'})|set(NEW_IDS.values())
    for p in plans:
        assert now[p['canonical']]['merged_from'] and all(g in now[p['canonical']]['merged_from'] for g in p['absorbed'])
    for gid,target in EXTENSIONS.items():assert min(math.dist(now[gid][x],target) for x in ('start','end'))<1e-8
    # No section/material change to every surviving prior member.
    for g,s in now.items():
        if g not in byid:continue
        for k in ('width_m','height_m','section_width_m','section_height_m','material'):assert s.get(k)==byid[g].get(k),(g,k)
    changes['geometry_version']=sha(MODEL);write(CHANGES,changes)
    write(OUT/'applied_revision.json',{'baseline_commit':BASE,'geometry_sha256':sha(MODEL),'merge_groups':plans,'endpoint_reconnections':EXTENSIONS,'added_beams':[s['preserved_viewer_id'] for s in new],'removed_beams':['E1-S1-V-005'],'opensees_run':False,'loads_recalculated':False})
    print('APPLIED',len(plans),'merge groups',len(retired),'absorbed,',len(new),'added, 4 endpoints reconnected, 1 removed')

def repair_diff():
    before=json.loads(subprocess.check_output(['git','show',BASE+':entregas/P1L2/unity_export/model_combined_viewer.json'],cwd=ROOT,text=True,encoding='utf-8'))
    byid={s['id']:s for s in before['solids']};applied=read(OUT/'applied_revision.json')
    write(DIFF,replace_diff_entries(read(DIFF),byid,applied['merge_groups']))
    print('REPAIRED sequential Luis diff; original reference untouched')

def resolve_overlap():
    model=read(MODEL);byid={s['id']:s for s in model['solids']};assert 'E2-P4-V-055' in byid and 'E2-P4-V-052' in byid
    source=read(ED2);mapping={s.get('preserved_viewer_id'):s for s in source['solids']};target=mapping['E2-P4-V-052'];other=mapping['E2-P4-V-055']
    target['sourceTags']=sorted(set(target.get('sourceTags',[])+other.get('sourceTags',[])))
    target['geometry_confirmation']['face_ids']=target['sourceTags']
    target['merged_from']=sorted(set(target.get('merged_from',[])+['E2-P4-V-055']))
    target['post_p1l4_correction']['reason']='USER_CONFIRMED_CONTINUOUS_PHYSICAL_BEAM; V-055 lay inside the 052+056 union and is absorbed to prevent duplicate geometry/stiffness.'
    source['solids']=[s for s in source['solids'] if s.get('preserved_viewer_id')!='E2-P4-V-055'];write(ED2,source)
    archive=read(ARCHIVE);archive['merged_id_aliases']['E2-P4-V-055']='E2-P4-V-052'
    row={'id':'E2-P4-V-052','type':'BEAM_MERGED','reason':target['post_p1l4_correction']['reason'],'source':'2024_22-102.dxf / overlap regression','historical_ids':['E2-P4-V-052','E2-P4-V-055','E2-P4-V-056'],'merged_from':['E2-P4-V-055','E2-P4-V-056'],'checkpoint':'PRE5_MANUAL_BEAM_REVISION'}
    archive['merge_history']=[r for r in archive['merge_history'] if not (r.get('checkpoint')=='PRE5_MANUAL_BEAM_REVISION' and r.get('id')=='E2-P4-V-052')]+[row];write(ARCHIVE,archive)
    changes=read(CHANGES);changes['rows']=[r for r in changes['rows'] if not (r.get('checkpoint')=='PRE5_MANUAL_BEAM_REVISION' and r.get('id')=='E2-P4-V-052')]+[row];write(CHANGES,changes)
    applied=read(OUT/'applied_revision.json')
    for p in applied['merge_groups']:
        if p['canonical']=='E2-P4-V-052':
            p['ids']=sorted(set(p['ids']+['E2-P4-V-055']));p['absorbed']=sorted(set(p['absorbed']+['E2-P4-V-055']));p['gap_total_m']=.1248
    for script in ('build_combined_model.py','enrich_combined_model.py'):subprocess.run([sys.executable,str(ROOT/'entregas/P1L2/edificio/scripts'/script)],cwd=ROOT,check=True)
    applied['geometry_sha256']=sha(MODEL);write(OUT/'applied_revision.json',applied);changes['geometry_version']=sha(MODEL);write(CHANGES,changes)
    print('RESOLVED overlap: E2-P4-V-055 -> E2-P4-V-052')

if __name__=='__main__':
    if '--repair-diff' in sys.argv:repair_diff()
    elif '--resolve-overlap' in sys.argv:resolve_overlap()
    else:main()
