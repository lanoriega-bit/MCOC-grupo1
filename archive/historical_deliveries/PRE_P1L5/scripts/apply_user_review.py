"""Apply reviewed scope/beam decisions to building SOURCES, then rebuild canonical geometry.

Refuses an unrelated input version. Historical results and Luis reference never touched.
"""
import copy,hashlib,json,math,subprocess,sys
from audit_user_structural_review import ROOT,OUT,MODEL,read,write,pair

def main():
    plan=read(OUT/'review_proposal.json');baseline=read(MODEL)
    scope_phase='--approved-exclusions-116' in sys.argv
    previous=read(OUT/'current_review_changes.json') if scope_phase else {'rows':[]}
    expected_hash=previous['geometry_version'] if scope_phase else plan['baseline_geometry_sha256']
    assert hashlib.sha256(MODEL.read_bytes()).hexdigest()==expected_hash,'Not the reviewed baseline; stop instead of overwriting later changes'
    before={s['id']:s for s in baseline['solids']};bytag={s['solidTag']:s for s in baseline['solids']}
    # Narrow independent milestone while broad scope approval is pending.
    assert '--merges-only' in sys.argv or scope_phase,'Choose explicit approved phase.'
    archive=read(ROOT/'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json') if scope_phase else {'merged_id_aliases':{}}
    exclusions={r['element_id']:r for r in plan['exclusions']} if scope_phase else {}
    if scope_phase:
        assert len(exclusions)==116 and set(exclusions)<=set(before)
        plan['merges']=[]
    retired={i for r in plan['merges'] for i in r['merged_from']}
    changes=previous['rows'];aliases=archive['merged_id_aliases']
    for r in exclusions.values():
        r.update(removed_from_current_geometry=True,removed_from_FE=True,historical_commit=plan['baseline_commit'],results_policy='Historical immutable; no current applied loads or results')
        changes.append({'id':r['element_id'],'type':'REMOVED','reason':r['reason'],'source':r['source'],'historical_ids':[r['element_id']]})
    for path in [ROOT/'entregas/P1L2/unity_export/model_1_audited_corrected.json',ROOT/'entregas/P1L2/unity_export/model_2_viewer.json']:
        source=read(path);mapping={};kept=[];removed_tags={}
        for s in source['solids']:
            prior=bytag[s['solidTag']];gid=prior['id'];s['preserved_viewer_id']=gid;mapping[gid]=s
            if gid in exclusions or gid in retired:removed_tags[s['solidTag']]=gid
            else:kept.append(s)
        for merge in plan['merges']:
            if merge['canonical'] not in mapping:continue
            gid=merge['canonical'];target=mapping[gid];originals=[before[g] for g in [gid]+merge['merged_from']]
            a,b=originals;p=pair(a,b)
            assert a['floor']==b['floor'] and a['building']==b['building']
            assert p['section_A']==p['section_B']==[.6,.8] and p['angle_deg']<1e-6 and p['perpendicular_m']<1e-6 and p['z_difference_m']<1e-6
            assert abs(p['gap_m']-merge['gap_m'])<1e-6
            pts=[q for g in [gid]+merge['merged_from'] for q in [mapping[g]['start'],mapping[g]['end']]]
            first,last=max(((x,y) for x in pts for y in pts),key=lambda xy:math.dist(*xy))
            first,last=sorted([first,last]);target.update(start=first,end=last,length_m=math.dist(first,last),canonical_element_id=gid,merged_from=merge['merged_from'])
            target['sourceTags']=sorted({tag for s in originals for tag in s['sourceTags']})
            target['geometry_confirmation']={'status':'ARTIFICIAL_BEAM_FRAGMENTATION_CONFIRMED','face_ids':target['sourceTags'],'audit_file':'entregas/PRE_P1L5/user_structural_review/beam_primary_evidence.json','width_m':.6}
            target['post_p1l4_correction']={'correction_type':'MERGED','reason':'Continuous paired CAD faces across artificial extraction gap; '+merge['id_reason'],'primary_source':'2024_22-102.dxf','external_repo_clue':'NONE_USER_MANUAL_REVIEW','confidence':'CONFIRMED_FROM_PLAN','results_compatibility':'HISTORICAL_RESULTS_NOT_RECALCULATED'}
            for other in merge['merged_from']:aliases[other]=gid
            changes.append({'id':gid,'type':'MERGED','reason':target['post_p1l4_correction']['reason'],'source':'2024_22-102.dxf / beam_primary_evidence.json','historical_ids':[gid]+merge['merged_from'],'gap_m':merge['gap_m'],'before':originals})
        # Explicit label associations must point at surviving physical solids.
        replacements={before[old]['solidTag']:before[new]['solidTag'] for old,new in aliases.items() if old in before}
        def relink(value):
            if isinstance(value,list):return [relink(x) for x in value]
            if isinstance(value,dict):return {k:relink(v) for k,v in value.items()}
            if isinstance(value,str):return replacements.get(value,value)
            return value
        source['solids']=kept;source['labels']=relink(source.get('labels',[]))
        source['current_scope_revision']={'baseline':plan['baseline_commit'],'exclusions_manifest':'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json','stable_ids':'preserved_viewer_id on all survivors','results':'NONE_CURRENT'}
        write(path,source)
    for script in ['build_combined_model.py','enrich_combined_model.py']:
        subprocess.run([sys.executable,str(ROOT/'entregas/P1L2/edificio/scripts'/script)],cwd=ROOT,check=True)
    current=read(MODEL);now={s['id']:s for s in current['solids']};expected=set(before)-set(exclusions)-retired
    assert set(now)==expected,'Stable ID / scope mismatch'
    changed={r['canonical'] for r in plan['merges']}
    for gid,s in now.items():
        assert s['solidTag']==before[gid]['solidTag']
        if gid not in changed:
            for key in ['start','end','center','width_m','height_m','depth_m','points']:
                assert s.get(key)==before[gid].get(key),(gid,key,s.get(key),before[gid].get(key))
    write(ROOT/'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json',{'baseline_commit':plan['baseline_commit'],'exclusions':list(exclusions.values()),'merged_id_aliases':aliases,'merge_history':[r for r in changes if r['type']=='MERGED']})
    write(OUT/'current_review_changes.json',{'geometry_version':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'baseline_commit':plan['baseline_commit'],'rows':changes,'columns_moved':0,'alignment_status':plan['columns_alignment'],'current_results':'NONE'})
    print('Stable IDs PASS;',len(before),'->',len(now),'; exclusions',len(exclusions),'; retired merged IDs',len(retired))
if __name__=='__main__':main()
