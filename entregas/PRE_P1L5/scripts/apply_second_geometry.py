"""Apply individually evidenced physical merges and primary column registration."""
import copy
import math
import subprocess
import sys
from second_structural_cleanup import ROOT,OUT,MODEL,SOURCE,ARCHIVE,BASE,read,write,sha

def main():
    before=read(MODEL); byid={s['id']:s for s in before['solids']}; bytag={s['solidTag']:s for s in before['solids']}
    changes=read(OUT/'current_review_changes.json')
    assert sha(MODEL)==changes['geometry_version'] and not any(r['type'] in ('COLUMN_ALIGNED','BEAM_MERGED') for r in changes['rows']),'Migration already applied or unrelated input'
    columns=read(OUT/'COLUMN_VERTICAL_STACKS.json'); pairs=read(OUT/'confirmed_beam_pairs.json'); archive=read(ARCHIVE)
    aligned={r['id']:r for st in columns['stacks'] for r in st['rows'] if r['decision']=='ALIGN_PRIMARY_CONFIRMED'}
    plans=[]; retired=set(); touched=set()
    for p in pairs['pairs']:
        ids=[p['beam_A'],p['beam_B']]; assert not set(ids)&touched,'Overlapping pair must first be consolidated as a chain'
        touched.update(ids)
        def rank(g):
            s=byid[g]; status=s.get('geometry_confirmation',{}).get('status','')
            return (status=='CONFIRMED_LABEL_WIDTH',math.dist(s['start'],s['end']),g)
        canonical=max(ids,key=rank); merged=next(g for g in ids if g!=canonical); retired.add(merged)
        plans.append({'canonical':canonical,'merged_from':[merged],'evidence':p,'id_reason':'Prefer direct label-confirmed contour; then longer surviving historical span; deterministic stable-ID tie break.'})
    diffpath=ROOT/'entregas/P1L2/edificio/datos/luis_reference_diff.json';diff=read(diffpath)
    support_audit=read(OUT/'wall_scope_audit.json'); generated_supports={r['id'] for r in support_audit['visual_supports'] if r['classification']=='COLUMN_SUPPORT'}
    for path in (SOURCE,ROOT/'entregas/P1L2/unity_export/model_2_viewer.json'):
        source=read(path); original={s['solidTag']:copy.deepcopy(s) for s in source['solids']}; mapping={bytag[s['solidTag']]['id']:s for s in source['solids']};changed_local={}
        dx=27.491 if path==SOURCE else 0
        for gid,r in aligned.items():
            if gid not in mapping:continue
            s=mapping[gid];s['center'][:2]=[r['target_xy'][0]-dx,r['target_xy'][1]]
            s['post_p1l4_correction']={'correction_type':'COLUMN_ALIGNED','reason':'Primary contour centre, not mean of CAD vertices; same structural stack registered to P2 primary frame.','primary_source':r['source_sheet'],'primary_handles':r.get('primary_handles',[]),'source_floor':r.get('primary_source_floor'),'confidence':'CONFIRMED_PRIMARY_FACES_AND_AXES','external_repo_clue':'Santiago/Caceres snapshot per COLUMN_VERTICAL_STACKS.json; candidate fit, not truth','delta_xy_m':r['delta_xy'],'section_changed':False,'dimension_note':r.get('dimension_note'),'results_compatibility':'NONE_CURRENT'}
            changed_local[gid]=s
            changes['rows'].append({'id':gid,'type':'COLUMN_ALIGNED','reason':s['post_p1l4_correction']['reason']+f" Move {r['displacement_m']:.6f} m; dimensions unchanged.",'source':r['source_sheet']+' / COLUMN_VERTICAL_STACKS.json','historical_ids':[gid],'before':byid[gid],'delta_xy_m':r['delta_xy']})
        for gid in generated_supports:
            if gid not in mapping:continue
            s=mapping[gid];refs=[bytag[t]['id'] for t in s.get('sourceTags',[]) if t in bytag]
            if len(refs)==1 and refs[0] in aligned and s.get('source_layer')=='generated_connected_support':
                r=aligned[refs[0]];s['center'][:2]=[r['target_xy'][0]-dx,r['target_xy'][1]]
                s['post_p1l4_correction']={'correction_type':'COLUMN_SUPPORT_FOLLOWED','column':refs[0],'reason':'Generated support visual follows conserved column; not a relocated surveyed footing. Dimensions and support existence unchanged.'};changed_local[gid]=s
        for p in plans:
            gid=p['canonical']
            if gid not in mapping:continue
            ids=[gid]+p['merged_from'];target=mapping[gid]
            pts=[q for g in ids for q in (mapping[g]['start'],mapping[g]['end'])];a,b=max(((a,b) for a in pts for b in pts),key=lambda q:math.dist(*q));a,b=sorted((a,b))
            target.update(start=a,end=b,length_m=math.dist(a,b),canonical_element_id=gid,merged_from=sorted(set(target.get('merged_from',[])+p['merged_from'])))
            target['sourceTags']=sorted({t for g in ids for t in byid[g].get('sourceTags',[])})
            target['geometry_confirmation']['face_ids']=target['sourceTags']
            target['post_p1l4_correction']={'correction_type':'BEAM_MERGED','reason':'ARTIFICIAL_BEAM_FRAGMENTATION: same confirmed section/Z; paired continuous primary faces; no identified intermediate support/joint.','primary_source':byid[gid]['source_dxf'],'confidence':'CONFIRMED_FROM_PLAN','audit':'second_structural_cleanup/GLOBAL_BEAM_FRAGMENTATION_AUDIT.json','id_reason':p['id_reason'],'results_compatibility':'HISTORICAL_NOT_RECALCULATED'}
            changed_local[gid]=target
            for other in p['merged_from']:archive['merged_id_aliases'][other]=gid;changed_local[other]=None
            entry={'id':gid,'type':'BEAM_MERGED','reason':target['post_p1l4_correction']['reason'],'source':byid[gid]['source_dxf']+' / GLOBAL_BEAM_FRAGMENTATION_AUDIT.json','historical_ids':ids,'gap_m':p['evidence']['gap_m'],'before':[byid[g] for g in ids],'id_reason':p['id_reason']}
            changes['rows'].append(entry);archive['merge_history'].append(entry)
        source['solids']=[s for s in source['solids'] if bytag[s['solidTag']]['id'] not in retired]
        replacements={byid[o]['solidTag']:byid[n]['solidTag'] for o,n in archive['merged_id_aliases'].items() if o in byid and n in byid}
        def relink(v):
            if isinstance(v,list):return [relink(x) for x in v]
            if isinstance(v,dict):return {k:relink(x) for k,x in v.items()}
            return replacements.get(v,v) if isinstance(v,str) else v
        source['labels']=relink(source.get('labels',[]))
        if path==SOURCE:
            for gid,s in changed_local.items():
                oldsolid=original[byid[gid]['solidTag']]
                diff['changes'].append({'id':gid,'solidTag':oldsolid['solidTag'],'category':oldsolid['category'],'old_geometry':oldsolid,'new_geometry':s if s is not None else 'REMOVED','reason':'PRIMARY_CONFIRMED_SECOND_CLEANUP','classification':'GEOMETRY_CORRECTION','evidence':'second_structural_cleanup','review_checkpoint':'PRE5_SECOND_GEOMETRY'})
        write(path,source)
    write(ARCHIVE,archive);write(diffpath,diff)
    for script in ('build_combined_model.py','enrich_combined_model.py'):
        subprocess.run([sys.executable,str(ROOT/'entregas/P1L2/edificio/scripts'/script)],cwd=ROOT,check=True)
    now={s['id']:s for s in read(MODEL)['solids']}
    assert set(now)==set(byid)-retired
    for gid,s in now.items():
        for key in ('width_m','height_m','depth_m','section_width_m','section_height_m','section_depth_m','material'):
            assert s.get(key)==byid[gid].get(key),(gid,key,s.get(key),byid[gid].get(key))
    columns.update(applied=True,geometry_version=sha(MODEL));write(OUT/'COLUMN_VERTICAL_STACKS.json',columns)
    pairs.update(applied=True,merge_plans=plans,geometry_version=sha(MODEL));write(OUT/'confirmed_beam_pairs.json',pairs)
    changes['geometry_version']=sha(MODEL);write(OUT/'current_review_changes.json',changes)
    print('APPLIED',len(plans),'physical beam pairs;',len(aligned),'column XY corrections; no section/material change')
if __name__=='__main__':main()
