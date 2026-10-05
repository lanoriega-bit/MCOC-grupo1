"""Generate bounded proposals and primary-source checks BEFORE any mutation."""
import json,sys,math,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from audit_user_structural_review import ROOT,OUT,read,write,center,line,angle,pair
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
sys.path.insert(0,str(ROOT/'entregas/POST_P1L4/scripts'))
import audit_ed1_walls as w1
import audit_ed2_walls as w2

def main():
    m=read(ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json');ss=m['solids'];ids={s['id']:s for s in ss}
    removals={};chains=[]
    def add(g,reason,source):
        s=ids[g];removals[g]={'element_id':g,'reason':reason,'source':source,'decision_date':'2026-09-23','removed_from_current_geometry':False,'removed_from_FE':False,'before':s}
    explicit=['E1-P1-C-'+f'{i:03}' for i in [7,9,16,17,18,19,20]]+['E1-P1-V-'+f'{i:03}' for i in [73,71,84,82,93,89,91,68,72,98]]+['E1-P2-V-'+f'{i:03}' for i in [53,69,82,75,55]]+['E1-P1-M-027']
    for g in explicit:add(g,'USER_SCOPE_EXCLUSION_EXTERIOR_NOT_CAD_ABSENCE','Manual review + canonical primary CAD provenance. C007/C009: explicit clarification retains P2; transfer remains unverified.')
    for g in ['E1-P1-M-028','E1-P1-M-029']:
        add(g,'USER_SCOPE_EXCLUSION_INTERIOR_WALL_ACKNOWLEDGED','2026-09-23 clarification: remove also the two interior axis-I panels, after location discrepancy was reported. Not classified as exterior.')
    # Explicit vertical correspondence, NOT graph traversal. East/west ED2
    # distinction follows user clarification and the physical plan locations.
    groups=[['E1-S1-M-026','E1-P1-M-004','E1-P2-M-007','E1-P3-M-007','E1-P4-M-007'],
            ['E1-S1-M-029','E1-P1-M-010','E1-P2-M-008','E1-P3-M-008','E1-P4-M-008'],
            ['E1-P1-M-003','E1-P2-M-002','E1-P3-M-002','E1-P4-M-002']]
    for upper,lower in [(7,7),(8,8),(9,10),(10,11)]:
        groups.append([f'E2-{f}-M-{lower:03}' for f in ['S1','P1','P2','P3']]+[f'E2-P4-M-{upper:03}'])
    groups.append([f'E2-{f}-M-009' for f in ['S1','P1','P2','P3']])
    faces={}
    for b in ['EDIFICIO_1','EDIFICIO_2']:
        for f in ['S1','P1','P2','P3','P4']:
            rows=w1.source_faces(f) if b=='EDIFICIO_1' else w2.read_source(f)[0]
            faces[b,f]={r['id']:r for r in rows}
    for group in groups:
        chain=[]
        for g in group:
            s=ids[g];references=s['geometry_confirmation']['face_ids'];primary=[faces[s['building'],s['floor']][r] for r in references]
            add(g,'USER_SCOPE_EXCLUSION_WALL_CHAIN_NOT_CAD_ABSENCE','User seeds + 2026-09-23 clarification (ED2 east removed; west M002/M003 and neighbors retained)')
            removals[g]['primary_faces']=primary
            chain.append({'id':g,'start':s['start'],'end':s['end'],'thickness_m':s['width_m'],'faces':references})
        chains.append(chain)
    # S1 exterior sector named by M001 and M060: explicit spatial enclosure,
    # not all outboard items and not a numerical ID range.
    s1=[]
    for s in ss:
        if s['building']!='EDIFICIO_1' or s['floor']!='S1' or s['category'] not in ['wall','beam','support']:continue
        pts=[s['start'],s['end']] if 'start' in s else [s['center']]
        if not all(27.0<=p[0]<=49.1 and -10.8<=p[1]<=-.4 for p in pts):continue
        add(s['id'],'USER_SCOPE_EXCLUSION_S1_SOUTH_SECTOR','2017_67-101: sector bounded by M001/M060, south of axis 1; exact proposal overlay')
        s1.append(s)
    write(OUT/'confirmed_removal_chains.json',{'status':'PROPOSAL_BEFORE_REMOVAL','chains':chains,'ED2_retained':[s['id'] for s in ss if s['building']=='EDIFICIO_2' and s['category']=='wall' and s['id'] not in removals]})
    md=['# Propuesta exacta de cadenas a excluir','','Cambio de alcance solicitado, NO afirmación de que los muros no existen. No se certifica suficiencia resistente del edificio sin ellos. Sin OpenSees.','']
    for chain in chains:md.append('- '+' → '.join(r['id'] for r in chain))
    md+=['','ED1 cadena M002: no se encontró continuación S1 inequívoca; no se incorpora un vecino por proximidad. ED2 se conserva íntegro el grupo oeste M001–M006 de cada piso. El grupo este tiene un paño inferior adicional M009 (S1–P3) sin homólogo P4, registrado por separado.']
    (OUT/'REMOVAL_CHAIN_PROPOSAL.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    md=['# Sector exterior S1: propuesta previa','','Solo el sector sur entre M001 y M060; no equivale a todos los elementos fuera de ejes. Conserva muros perimetrales que cruzan hacia el interior.','', '| Elemento | Tipo | Inicio / fin (m) | Evidencia |','|---|---|---|---|']
    for s in s1:md.append(f"| {s['id']} | {s['category']} | {s.get('start',s.get('center'))} / {s.get('end')} | {s.get('source_dxf')} / {s.get('sourceTags',s.get('sourceTag'))} |")
    (OUT/'S1_EXTERIOR_REMOVAL_PROPOSAL.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    for b,f,title in [('EDIFICIO_1','S1','S1_EXTERIOR'),('EDIFICIO_2','P4','ED2_WALL_SCOPE'),('EDIFICIO_1','P1','ED1_P1_SCOPE')]:
        fig,ax=plt.subplots(figsize=(13,8))
        for r in faces[b,f].values():
            a,c=r['start'],r['end'];ax.plot([a[0],c[0]],[a[1],c[1]],color='.65',lw=.5)
        for s in ss:
            if s['building']!=b or s['floor']!=f or s['category'] not in ['wall','beam','column']:continue
            if b=='EDIFICIO_2' and s['category']!='wall':continue
            color='red' if s['id'] in removals else 'navy';a=s.get('start',s.get('center'));c=s.get('end',a)
            ax.plot([a[0],c[0]],[a[1],c[1]],color=color,lw=1.7 if s['category']=='wall' else .5)
            if s['category']=='wall' or s['id'] in removals:ax.text(*center(s)[:2],s['id'].split('-')[-2]+'-'+s['id'].split('-')[-1],fontsize=6,color=color)
        ax.set_aspect('equal');ax.set_title(title+' | rojo: propuesta de exclusión; azul: conservar; gris: caras CAD');ax.set_xlabel('X global m');ax.set_ylabel('Y global m');fig.tight_layout();fig.savefig(OUT/(title+'.png'),dpi=150);plt.close(fig)
    proposal={'baseline_commit':'b11d12d','baseline_geometry_sha256':hashlib.sha256((ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json').read_bytes()).hexdigest(),'status':'PROPOSED_NOT_APPLIED','exclusions':list(removals.values()),'held':[],'columns_alignment':'HELD_OFFSETS_OVER_5CM_REQUIRE_TRANSFORM_REVIEW','merges':[{'canonical':'E2-P4-V-042','merged_from':['E2-P4-V-046'],'gap_m':.1745,'id_reason':'Main labeled span retained versus residual short extraction.'},{'canonical':'E2-P4-V-049','merged_from':['E2-P4-V-048'],'gap_m':.091,'id_reason':'Same primary faces; preserves dominant 6.4344 m span and historical solidTag0417 versus 1.475 m short fragment0418.'}]}
    write(OUT/'review_proposal.json',proposal)
    print('Proposed exclusions:',len(removals),'S1:',len(s1),'wall chains:',len(chains),'merges:',2)
if __name__=='__main__':main()
