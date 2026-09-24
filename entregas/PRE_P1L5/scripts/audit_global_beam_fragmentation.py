"""All physical beams; conservative candidate chains, primary faces, no FE inference."""
import math
import sys
from collections import Counter,defaultdict
from itertools import combinations
from shapely.geometry import LineString,Point
from second_structural_cleanup import ROOT,OUT,MODEL,ARCHIVE,BASE,read,write,old,center,footprint
from audit_user_structural_review import pair,angle,direction
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
import audit_ed1_beams as ed1
sys.path.insert(0,str(ROOT/'entregas/POST_P1L4/scripts'))
import audit_ed2_beams as ed2

def main():
    model=read(MODEL); beams=[s for s in model['solids'] if s['category']=='beam']
    # An excluded physical wall can still explain a CAD interruption. Removing it
    # from the chosen FE scope is not evidence of continuous construction.
    supports=[s for s in old(MODEL)['solids'] if s['category'] in ('column','wall')]
    supports += [r['before'] for r in read(ARCHIVE)['exclusions'] if r['before']['category'] in ('column','wall')]
    groups=defaultdict(list); rows=[]
    for b in beams:groups[(b['building'],b['floor'])].append(b)
    for (building,floor),bs in groups.items():
        faces=(ed1 if building=='EDIFICIO_1' else ed2).source_beams(floor)
        for a,b in combinations(bs,2):
            if angle(a,b)>.5:continue
            p=pair(a,b)
            if p['perpendicular_m']>.01 or p['gap_m']>.20 or p['overlap_m']>.005:continue
            pa,pb=min(((x,y) for x in (a['start'],a['end']) for y in (b['start'],b['end'])),key=lambda xy:math.dist(*xy))
            bridge=LineString([pa[:2],pb[:2]]) if math.dist(pa[:2],pb[:2])>1e-9 else Point(pa[:2])
            touching=sorted({s['id'] for s in supports if s['building']==building and s['floor']==floor and footprint(s).buffer(.001).intersects(bridge)})
            p.update(building=building,floor=floor,endpoints_A=[a['start'],a['end']],endpoints_B=[b['start'],b['end']],bridge=[pa,pb],intermediate_physical_supports=touching)
            u=direction(a); origin=a['start']; width=a.get('section_width_m'); evidence=[]
            if width:
                for side in (-1,1):
                    found=[]
                    for f in faces:
                        v=[f['end'][i]-f['start'][i] for i in range(2)]; length=math.hypot(*v)
                        if abs(u[0]*v[1]-u[1]*v[0])/length>1e-5:continue
                        offsets=[(q[0]-origin[0])*u[1]-(q[1]-origin[1])*u[0] for q in (f['start'],f['end'])]
                        if max(abs(o-side*width/2) for o in offsets)>.003:continue
                        interval=sorted(sum((q[k]-origin[k])*u[k] for k in range(2)) for q in (f['start'],f['end']))
                        gap=sorted(sum((q[k]-origin[k])*u[k] for k in range(2)) for q in (pa,pb))
                        # Each primary face must itself span the interruption and
                        # extend 2 cm into both physical fragments.
                        if interval[0]<=gap[0]-.02 and interval[1]>=gap[1]+.02:found.append({'handle':f['entity_handle'],'face_id':f['id'],'start':f['start'],'end':f['end'],'sheet':f['source_dxf']})
                    evidence.append({'side':side,'continuous_faces':found})
            p['primary_face_evidence']=evidence
            same=p['section_A']==p['section_B'] and all(v is not None for v in p['section_A'])
            if not same:p['decision']='REJECT_SECTION_DIFFERENT_OR_UNKNOWN'
            elif p['z_difference_m']>.001:p['decision']='REJECT_LEVEL_DIFFERENCE'
            elif touching:p['decision']='RETAIN_PRIMARY_SUPPORT_REVIEW'
            elif len(evidence)==2 and all(r['continuous_faces'] for r in evidence):p['decision']='PRIMARY_CONTINUITY_CANDIDATE_REVIEW_LABELS_JOINTS'
            else:p['decision']='REVIEW_REQUIRED_NO_UNEQUIVOCAL_CONTINUOUS_FACES'
            rows.append(p)
    adjacency=defaultdict(set)
    for p in rows:
        if p['decision'].startswith('REJECT'):continue
        adjacency[p['beam_A']].add(p['beam_B']);adjacency[p['beam_B']].add(p['beam_A'])
    seen=set(); chains=[]
    for g in adjacency:
        if g in seen:continue
        todo=[g]; comp=set()
        while todo:
            x=todo.pop()
            if x in comp:continue
            comp.add(x);todo.extend(adjacency[x]-comp)
        seen|=comp
        if len(comp)>2:chains.append({'ids':sorted(comp),'status':'CANDIDATE_CHAIN_NOT_MERGE_AUTHORIZATION'})
    micro=[{'id':s['id'],'length_m':math.dist(s['start'],s['end']),'section':[s.get('section_width_m'),s.get('section_height_m')],'source':s.get('geometry_confirmation'),'status':'REVIEW_SHORT_PHYSICAL_MEMBER_NOT_AUTOMATIC_DELETION'} for s in beams if math.dist(s['start'],s['end'])<.30]
    result={'baseline_commit':BASE,'beams_audited':len(beams),'tolerances':{'angle_deg':.5,'transverse_m':.01,'gap_m':.20,'overlap_m':.005,'primary_face_offset_m':.003},'policy':'0.20m detects prior confirmed gaps 0.1745/0.091, does not authorize merging. Archived walls remain physical clues.','counts':dict(Counter(r['decision'] for r in rows)),'candidates':rows,'chains':chains,'microsegments':micro,'new_auto_merges':[]}
    write(OUT/'GLOBAL_BEAM_FRAGMENTATION_AUDIT.json',result)
    md=['# Global beam fragmentation audit','',f'{len(beams)} active beams checked, both buildings, S1–P4; {len(rows)} candidate pairs; {len(chains)} multi-member candidate chains; {len(micro)} members shorter than 0.30 m.','',result['policy'],'','No new automatic merge is authorized by screening alone. Primary faces, sections, Z, support and joint evidence must all pass. Previously confirmed two merges remain unchanged.','', '| A | B | Gap m | Angle deg | dZ m | Sections | Physical support | Decision |','|---|---|---:|---:|---:|---|---|---|']
    for p in rows:md.append(f"| {p['beam_A']} | {p['beam_B']} | {p['gap_m']:.6f} | {p['angle_deg']:.6f} | {p['z_difference_m']:.6f} | {p['section_A']} / {p['section_B']} | {', '.join(p['intermediate_physical_supports'])} | {p['decision']} |")
    md+=['','## Chains','']+[', '.join(r['ids'])+' — '+r['status'] for r in chains]
    md+=['','## Short members','']+[f"- {r['id']}: {r['length_m']:.6f} m; {r['status']}" for r in micro]
    (ROOT/'entregas/PRE_P1L5/GLOBAL_BEAM_FRAGMENTATION_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(result['counts']);print('CHAINS',chains);print('PRIMARY_CANDIDATES',[(r['beam_A'],r['beam_B']) for r in rows if r['decision'].startswith('PRIMARY')])
if __name__=='__main__':main()
