"""Directed PRE5 investigation: physical constraint extent and explicit blockers.
No model/results mutation. A connected graph alone never approves support.
"""
import json
from collections import Counter
from pathlib import Path
from shapely.geometry import LineString,box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5/current_readiness'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def main():
    model=read('entregas/P1L2/unity_export/model_combined_viewer.json');solids={s['solidTag']:s for s in model['solids']}
    fe=read('entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json')
    proposal=read('entregas/PRE_P1L5/constraint_normalization_proposal.json')
    clusters=[]
    for group in proposal['clusters']:
        nodes=set(group['nodes']);arms=[c for c in fe['constraints'] if c['master_node'] in nodes]
        owners=sorted({c['geometry_elementTag'] for c in arms});walls=[solids[t] for t in owners if solids[t]['category']=='wall']
        footprints=unary_union([LineString([w['start'][:2],w['end'][:2]]).buffer(w['width_m']/2,cap_style=2) for w in walls])
        joint_parts=[footprints]
        for t in owners:
            s=solids[t]
            if s['category']=='column':
                x,y=s['center'][:2];joint_parts.append(box(x-s['width_m']/2,y-s['depth_m']/2,x+s['width_m']/2,y+s['depth_m']/2))
        beam_shapes=[LineString([solids[t]['start'][:2],solids[t]['end'][:2]]).buffer(solids[t]['width_m']/2,cap_style=2) for t in owners if solids[t]['category']=='beam']
        for i,shape in enumerate(beam_shapes):
            for other in beam_shapes[i+1:]:joint_parts.append(shape.intersection(other))
        joint_footprints=unary_union(joint_parts)
        locked=[]
        for e in fe['elements']:
            if e['node_i'] not in nodes or e['node_j'] not in nodes:continue
            a=fe['nodes'][str(e['node_i'])];b=fe['nodes'][str(e['node_j'])]
            line=LineString([(a['x'],a['y']),(b['x'],b['y'])]);length=line.length
            outside=line.difference(footprints.buffer(.001)).length if not footprints.is_empty else length
            outside_joint=line.difference(joint_footprints.buffer(.001)).length if not joint_footprints.is_empty else length
            locked.append({'element_id':e['element_id'],'analysis_id':e['analysis_id'],'type':e['type'],
                'length_m':length,'outside_owner_wall_footprints_m':outside,
                'outside_physical_joint_footprints_m':outside_joint,
                'classification':'ELASTIC_MEMBER_SHORT_CIRCUITED_OUTSIDE_JOINT' if outside_joint>.10 else 'EMBEDDED_MEMBER_RIGID_IDEALIZATION_REVIEW'})
        severe=any(e['outside_physical_joint_footprints_m']>.10 for e in locked)
        clusters.append({**group,'arm_types':dict(Counter(c['type'] for c in arms)),
            'owner_ids':[solids[t]['id'] for t in owners],'rigidized_elements':locked,
            'classification':'ERROR_PROPAGATION_CANDIDATE' if severe else 'WALL_JOINT_IDEALIZATION_REVIEW',
            'not_a_diaphragm':'All six DOF tied; no approved diaphragm input or shell model',
            'decision':'NOT_APPROVED_FOR_CURRENT_ANALYSIS'})
    prior=read('entregas/PRE_P1L5/remaining_sources_audit.json')
    rows=[{**r,'analysis_blocking':True,'final_classification':r['classification'],
        'reason':'Support path/formulation unapproved; no deletion, fixation or live-load omission justified'} for r in prior['pending_fe']]
    loads=read('entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json')
    entry_counts=Counter((x['load_type'],x.get('confidence','MISSING')) for x in loads['entries'])
    heights=[]
    for r in prior['beam_heights']:
        members=[e['analysis_id'] for e in fe['elements'] if e['element_id']==r['element_id']]
        heights.append({'element_id':r['element_id'],'fe_members':members,'blocks_analysis':bool(members),
            'reason':'Required A/I/J cannot be derived from visual proxy or nearby VAR label',
            'labels':r['nearest_primary_section_labels']})
    out={'status':'BLOCKED','opensees_run':False,'clusters':clusters,'pending_elements':rows,'height_readiness':heights,
        'loads':{'status':loads['status'],'entries':len(loads['entries']),
                 'by_type_confidence':[{'type':k[0],'confidence':k[1],'count':v} for k,v in sorted(entry_counts.items())],
                 'current_applied_load_vector_exists':False},
        'summary':{'clusters':len(clusters),'clusters_with_elastic_short_circuit_outside_joint':sum(c['classification']=='ERROR_PROPAGATION_CANDIDATE' for c in clusters),
                   'rigidized_elastic_members':sum(len(c['rigidized_elements']) for c in clusters),'residuals':len(rows),
                   'unknown_heights_in_candidate':sum(h['blocks_analysis'] for h in heights)}}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'structural_readiness.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out['summary'],indent=2))
if __name__=='__main__':main()
