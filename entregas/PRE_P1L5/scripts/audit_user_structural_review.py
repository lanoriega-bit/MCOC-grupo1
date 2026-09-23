"""Read-only proposals from Matías's manual review; never changes canonical models."""
import json,math,sys,hashlib
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from shapely.geometry import LineString,Point
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5/user_structural_review'
MODEL=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
FLOORS=['S1','P1','P2','P3','P4']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def center(s):return s.get('center') or [(a+b)/2 for a,b in zip(s['start'],s['end'])]
def line(s):return LineString([s['start'][:2],s['end'][:2]])
def direction(s):
    a,b=s['start'],s['end'];l=math.dist(a[:2],b[:2]);return [(b[i]-a[i])/l for i in range(2)]
def angle(a,b):return math.degrees(math.acos(min(1,abs(sum(x*y for x,y in zip(direction(a),direction(b)))))))
def pair(a,b):
    u=direction(a);origin=a['start'];v=direction(b)
    aa=sorted(sum((p[k]-origin[k])*u[k] for k in range(2)) for p in [a['start'],a['end']])
    bb=sorted(sum((p[k]-origin[k])*u[k] for k in range(2)) for p in [b['start'],b['end']])
    overlap=max(0,min(aa[1],bb[1])-max(aa[0],bb[0]));gap=max(0,max(aa[0],bb[0])-min(aa[1],bb[1]))
    perp=max(abs((p[0]-origin[0])*u[1]-(p[1]-origin[1])*u[0]) for p in [b['start'],b['end']])
    return {'beam_A':a['id'],'beam_B':b['id'],'gap_m':gap,'overlap_m':overlap,'angle_deg':angle(a,b),'perpendicular_m':perp,'z_difference_m':abs(center(a)[2]-center(b)[2]),'section_A':[a.get('section_width_m'),a.get('section_height_m')],'section_B':[b.get('section_width_m'),b.get('section_height_m')],'axis_location':a.get('location_description'),'source_faces_A':a.get('sourceTags'),'source_faces_B':b.get('sourceTags')}
def main():
    OUT.mkdir(exist_ok=True);m=read(MODEL);ss=m['solids'];byid={s['id']:s for s in ss};walls=[s for s in ss if s['category']=='wall'];cols=[s for s in ss if s['category']=='column'];beams=[s for s in ss if s['category']=='beam']
    groups=defaultdict(list)
    for s in beams:groups[(s['building'],s['floor'])].append(s)
    matches=[];explicit=[{'E2-P4-V-042','E2-P4-V-046'},{'E2-P4-V-048','E2-P4-V-049'}]
    for group,items in groups.items():
        for a,b in combinations(items,2):
            if angle(a,b)>.5:continue
            p=pair(a,b)
            if p['perpendicular_m']>.01 or p['gap_m']>.20 or p['overlap_m']>.005:continue
            pa,pb=min(((x,y) for x in [a['start'],a['end']] for y in [b['start'],b['end']]),key=lambda xy:math.dist(xy[0],xy[1]));bridge=LineString([pa[:2],pb[:2]]) if math.dist(pa[:2],pb[:2])>1e-8 else Point(pa[:2])
            supports=[]
            for t in cols+walls:
                if t['building']!=group[0] or t['floor']!=group[1]:continue
                foot=Point(center(t)[:2]).buffer(max(t.get('depth_m',0),t['width_m'])/2) if t['category']=='column' else line(t).buffer(t['width_m']/2,cap_style=2)
                if foot.intersects(bridge):supports.append(t['id'])
            p.update({'building':group[0],'floor':group[1],'intermediate_support_footprints':supports,'explicit_user_pair':{a['id'],b['id']} in explicit,'same_known_section':p['section_A']==p['section_B'] and all(x is not None for x in p['section_A']),'same_source_faces':set(a.get('sourceTags',[]))==set(b.get('sourceTags',[])),'recommendation':'REVIEW_CAD_NO_AUTOMATIC_MERGE','gap_class':'NUMERICAL_CANDIDATE' if p['gap_m']<=.001 else 'DRAWING_OR_PHYSICAL_GAP_REQUIRES_PRIMARY_REVIEW'})
            if supports:p['recommendation']='RETAIN_PENDING_INTERMEDIATE_SUPPORT_REVIEW'
            if not p['same_known_section']:p['recommendation']='RETAIN_SECTION_MISMATCH_OR_UNKNOWN'
            matches.append(p)
    write(OUT/'beam_fragmentation_candidates.json',matches)
    seeds=['E1-P4-M-007','E1-P4-M-008','E1-P4-M-002','E2-P4-M-008','E2-P4-M-010'];chains=[]
    for seed in seeds:
        base=byid[seed];rows=[]
        for floor in reversed(FLOORS):
            options=[]
            for t in walls:
                if t['building']!=base['building'] or t['floor']!=floor or angle(base,t)>.5:continue
                p=pair(base,t);ratio=p['overlap_m']/min(line(base).length,line(t).length)
                if p['perpendicular_m']>.3 or ratio<.6:continue
                options.append({'id':t['id'],'center':center(t),'length_m':line(t).length,'width_m':t['width_m'],'offset_axis_m':p['perpendicular_m'],'overlap_ratio':ratio,'length_ratio':line(t).length/line(base).length,'source':t.get('geometry_confirmation'),'location':t.get('location_description')})
            rows.append({'floor':floor,'candidates':sorted(options,key=lambda x:(x['offset_axis_m'],-x['overlap_ratio'])),'status':'REVIEW_PRIMARY_AND_SCOPE_NO_GRAPH_FLOOD_FILL'})
        chains.append({'seed':seed,'seed_length_m':line(base).length,'floors':rows})
    write(OUT/'removal_chain_proposal.json',chains)
    stacks=[]
    for s in cols:
        if s['building']!='EDIFICIO_1' or s['floor'] not in ['S1','P1']:continue
        options=[]
        for t in cols:
            if t['building']!=s['building'] or t['floor'] not in ['P2','P3','P4']:continue
            distance=math.dist(center(s)[:2],center(t)[:2])
            if distance<=.2:options.append({'id':t['id'],'floor':t['floor'],'xy':center(t)[:2],'distance_m':distance,'section':[t['width_m'],t.get('depth_m')],'source':t.get('source_dxf'),'sourceTags':t.get('sourceTags')})
        stacks.append({'id':s['id'],'floor':s['floor'],'xy_original':center(s)[:2],'section':[s['width_m'],s.get('depth_m')],'axis':s.get('axis_location'),'upper_candidates':options,'decision':'REVIEW_REQUIRED_NO_MOVE'})
    write(OUT/'column_vertical_stacks.json',stacks)
    exterior=[]
    for s in ss:
        if s['building']!='EDIFICIO_1' or s['floor']!='S1' or s['category'] not in ['wall','beam','support']:continue
        pts=[s['start'],s['end']] if s.get('start') else [s['center']]
        # Primary grid is only a screening envelope, never a removal rule.
        outside=all(p[0]<27.491 or p[0]>77.491 or p[1]<0 or p[1]>16.15 for p in pts)
        if outside:exterior.append({'id':s['id'],'type':s['category'],'coordinates':s.get('coordinates'),'axis':s.get('axis_location'),'source':s.get('source_dxf'),'status':'OUTSIDE_GRID_SCREEN_ONLY_NOT_REMOVAL_AUTHORIZATION'})
    write(OUT/'s1_exterior_screen.json',exterior)
    print(json.dumps({'geometry_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'beam_candidates':len(matches),'explicit_pairs':[p for p in matches if p['explicit_user_pair']],'wall_chains':chains,'columns_007_009':[p for p in stacks if p['id'] in ['E1-P1-C-007','E1-P1-C-009']],'column_stacks':len(stacks),'S1_exterior_screen':[r['id'] for r in exterior]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
