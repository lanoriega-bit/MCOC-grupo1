"""EXT-7 / FE-2: primary-source survey and explicit decisions, no FE solve.

External files are read-only clues. CAD block coordinates remain block-local
unless the entity belongs to modelspace; they are not application points.
"""
import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
import ezdxf
from shapely.geometry import LineString

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def xyz(n):return [n[k] for k in ('x','y','z')]
def delta(a,b):return [b[i]-a[i] for i in range(3)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def rigid(u,d):return [u[i]+cross(u[3:],d)[i] for i in range(3)]+u[3:]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--santiago',type=Path,required=True);ap.add_argument('--caceres',type=Path,required=True);a=ap.parse_args()
    model=load(ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json');byid={s['id']:s for s in model['solids']}
    old=load(ROOT/'entregas/POST_P1L4/EXT_5_REMAINING_AUDIT.json')
    comp=load(ROOT/'entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json');matches={r['our_id']:r for r in comp['our_elements']}
    walls=[]
    for row in old['elements']:
        if 'OVERLAP' not in row['cause']:continue
        s=byid[row['element_id']];ls=LineString([s['start'][:2],s['end'][:2]])
        checks=[]
        for hit in row['adjacent_wall_checks']:
            if hit['exact_axis_intersection'] or hit['physical_footprint_overlap_m2']<=0:continue
            t=byid[hit['other_id']];lt=LineString([t['start'][:2],t['end'][:2]])
            u=delta(s['start'],s['end']);v=delta(t['start'],t['end'])
            cosine=abs(sum(u[i]*v[i] for i in range(2)))/(ls.length*lt.length)
            angle=math.degrees(math.acos(min(1,cosine)))
            if hit['physical_footprint_overlap_m2']<1e-4:kind='NUMERICAL_CORNER_TOUCH_NOT_A_JOINT'
            elif angle<1 and hit['axis_distance_m']<=.0002:kind='PARALLEL_VERTICAL_CONTINUITY_AXIS_ROUNDING'
            elif angle<1:kind='PARALLEL_OFFSET_VERTICAL_OVERLAP'
            else:kind='ORTHOGONAL_END_FACE_OVERLAP_L_OR_T_REVIEW'
            checks.append({**hit,'angle_deg':round(angle,6),'classification':kind,'same_floor':s['floor']==t['floor'],
                'is_duplicate':False,'duplicate_reason':'Adjacent vertical intervals, not coincident solids',
                'source_a':s.get('geometry_confirmation'),'source_b':t.get('geometry_confirmation'),
                'source_sheets':[s['source_dxf'],t['source_dxf']],
                'action':'FE_ADAPTER_ERROR_CANDIDATE_NOT_APPLIED' if kind.endswith('ROUNDING') else 'NO_CONNECTION_WITHOUT_JUNCTION_DETAIL'})
        walls.append({'element_id':s['id'],'checks':checks,'decision':'KEEP_PHYSICAL_GEOMETRY; REVIEW_FE_JUNCTION'})
    sources=[];notes=[];labels=[]
    pattern=re.compile(r'hormig[oó]n|A\s*6[3]?0\s*[-/]?\s*4[2]?0|\b[HG]\s*-\s*\d{2}\b|f[\s\'´’]*c\s*[=:]|D\.M\.[HV]?|\bV\.?\s*\d+\s*/',re.I)
    for path in sorted((ROOT/'recursos/planos/dxf_full').rglob('*.dxf')):
        doc=ezdxf.readfile(path);seen=set();count=0;hits=[]
        # Reading all block definitions catches annotations not exposed as top-level TEXT.
        for block in doc.blocks:
            for ent in block:
                entities=[ent]+(list(ent.attribs) if ent.dxftype()=='INSERT' else [])
                for e in entities:
                    if e.dxftype() not in ('TEXT','MTEXT','ATTRIB','ATTDEF') or e.dxf.handle in seen:continue
                    seen.add(e.dxf.handle);count+=1
                    text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
                    if not pattern.search(text):continue
                    hit={'sheet':path.stem,'handle':e.dxf.handle,'layer':e.dxf.layer,'block':block.name,'text':text,
                         'position':list(e.dxf.insert),'coordinate_space':'MODEL' if block.name.upper()=='*MODEL_SPACE' else 'BLOCK_LOCAL_NOT_TRANSFORMED'}
                    hits.append(hit)
        sources.append({'sheet':path.stem,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_block_text_entities':count,'hits':len(hits)})
        notes.extend(hits);print('PRIMARY',path.name,count,len(hits),flush=True)
    external_sections={}
    for name,path in [('SANTIAGO',a.santiago/'P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json'),('CACERES',a.caceres/'Edificio/results/modelo_3d_manual.json')]:
        data=load(path);external_sections[name]={'source':str(path.relative_to(a.santiago if name=='SANTIAGO' else a.caceres)),
            'sections':data.get('sections',data.get('properties',{})),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    heights=[]
    for row in old['unknown_beam_heights']:
        s=byid[row['element_id']];near=row['nearest_primary_section_labels'];m=matches.get(s['id'],{})
        hints=[x for x in near if 'VAR' in x['text'].upper()]
        heights.append({**row,'classification':'VARIABLE_PROFILE_CLUE' if hints else 'NO_UNAMBIGUOUS_SECTION_ASSOCIATION',
            'external_matches':{k:m.get(k) for k in ('repo_santiago_match','repo_caceres_match')},
            'same_plan_section_texts':[x for x in notes if x['sheet']+'.dxf'==s['source_dxf'] and 'V' in x['text'].upper()],
            'decision':'REVIEW_REQUIRED_NO_CONSTANT_HEIGHT_INVENTED'})
    pending=[]
    for row in old['elements']:
        w=next((r for r in walls if r['element_id']==row['element_id']),None)
        classification='FE_ADAPTER_ERROR' if w and any(c['classification'].endswith('ROUNDING') for c in w['checks']) else 'UNRESOLVED_REAL'
        pending.append({'element_id':row['element_id'],'type':row['type'],'building':row['building'],'floor':row['floor'],
            'classification':classification,'qualification':'CANDIDATE diagnosis, support path NOT APPROVED','cause':row['cause'],
            'primary_source':row['primary_source'],'decision':'NO_REMOVAL_NO_ARTIFICIAL_SUPPORT'})
    candidate=load(ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json')
    nodes={int(k):v for k,v in candidate['nodes'].items()};parent={k:k for k in nodes}
    def find(n):
        while parent[n]!=n:parent[n]=parent[parent[n]];n=parent[n]
        return n
    for c in candidate['constraints']:parent[find(c['slave_node'])]=find(c['master_node'])
    groups=defaultdict(set)
    for c in candidate['constraints']:
        for n in (c['master_node'],c['slave_node']):groups[find(n)].add(n)
    normalized=[];cluster_rows=[];max_error=0
    for members in groups.values():
        fixed=sorted(members&set(candidate['supports']));root=fixed[0] if fixed else min(members)
        for n in sorted(members-{root}):normalized.append({'type':'RIGID_LINK_BEAM_PROPOSAL','master_node':root,'slave_node':n})
        mins=[min(xyz(nodes[n])[i] for n in members) for i in range(3)];maxs=[max(xyz(nodes[n])[i] for n in members) for i in range(3)]
        cluster_rows.append({'root':root,'nodes':sorted(members),'fixed_nodes':fixed,'extent_m':delta(mins,maxs),
            'physical_scope':'REVIEW_REQUIRED_RIGID_CLUSTER_EXTENT','same_building':len({nodes[n]['building'] for n in members})==1})
        # Independent six-basis kinematic test of every original arm, not just graph equivalence.
        for c in candidate['constraints']:
            if c['master_node'] not in members:continue
            for k in range(6):
                basis=[float(i==k) for i in range(6)]
                um=rigid(basis,delta(xyz(nodes[root]),xyz(nodes[c['master_node']])))
                via=rigid(um,delta(xyz(nodes[c['master_node']]),xyz(nodes[c['slave_node']])))
                direct=rigid(basis,delta(xyz(nodes[root]),xyz(nodes[c['slave_node']])))
                max_error=max(max_error,max(abs(via[i]-direct[i]) for i in range(6)))
    proposal={'status':'ALGEBRAIC_PROPOSAL_NOT_APPLIED','assumption':'Every existing arm is a small-rotation rigidLink beam; no other MP constraints',
        'original_count':len(candidate['constraints']),'normalized_count':len(normalized),'six_basis_max_residual':max_error,
        'kinematic_test':'PASS' if max_error<1e-10 else 'FAIL','clusters':cluster_rows,'constraints':normalized,
        'blockers':['Physical rigid cluster extent must be validated','Multiple supports in a rigid cluster require consistent SP treatment','Does not resolve missing physical paths'],
        'source':'https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidLink.html'}
    out={'status':'REVIEW_REQUIRED','geometry_changed':False,'opensees_run':False,'wall_overlaps':walls,'beam_heights':heights,
        'pending_fe':pending,'source_survey':sources,'primary_text_hits':notes,'external_sections':external_sections,
        'slabs':{'status':'REVIEW_REQUIRED','decision':'External load polygons and voids are candidates, not architectural perimeter proof'},
        'summary':{'wall_cases':len(walls),'height_cases':len(heights),'pending_fe':len(pending),'source_sheets':len(sources),
            'variable_profile_clues':sum(r['classification']=='VARIABLE_PROFILE_CLUE' for r in heights)}}
    for name,data in [('remaining_sources_audit.json',out),('constraint_normalization_proposal.json',proposal)]:
        (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'summary':out['summary'],'normalized_constraints':len(normalized),'kinematic_error':max_error},indent=2))

if __name__=='__main__':main()
