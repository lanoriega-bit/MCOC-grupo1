"""Read-only all-member regression inspired by Caceres' postprocessing tests.

Independent implementation; never executes OpenSees or alters result numbers.
End actions are NOT internal cut forces. Assumes nodal loading only, audited
in p1l3/opensees_mdl.py; no beam distributed loads in these saved five cases.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def main():
    meta=read(STREAM/'p1l4_structural_metadata.json')
    members={x['analysis_id']:x for x in meta['elements']}
    rows=[];axes=[];sources=[]
    for aid,m in members.items():
        a=m['local_axes'];x,y,z=[a[k] for k in ('x','y','z')]
        length=math.dist(m['node_i_coord_m'],m['node_j_coord_m'])
        dx=[(b-a)/length for a,b in zip(m['node_i_coord_m'],m['node_j_coord_m'])]
        err=max(abs(dot(v,v)-1) for v in (x,y,z))
        err=max(err,abs(dot(x,y)),abs(dot(y,z)),abs(dot(z,x)),abs(dot(cross(x,y),z)-1),max(abs(a-b) for a,b in zip(x,dx)))
        axes.append({'analysis_id':aid,'max_error':err,'status':'PASS' if err<1e-7 else 'FAIL'})
    for case in ('G','Q','EX','EY','R'):
        p=STREAM/f'p1l4_jose/fuerzas_internas/{case}.json';data=read(p)
        sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        for f in data['elements']:
            m=members[f['analysis_id']];length=math.dist(m['node_i_coord_m'],m['node_j_coord_m'])
            i={k:f[k+'_end1'] for k in ('N','Vy','Vz','T','My','Mz')}
            j={k:f[k+'_end2'] for k in i}
            residual={k:i[k]+j[k] for k in ('N','Vy','Vz','T')}
            residual['My']=i['My']+j['My']+i['Vz']*length
            residual['Mz']=i['Mz']+j['Mz']-i['Vy']*length
            scaleF=max(1,*[abs(v) for k in ('N','Vy','Vz') for v in (i[k],j[k])])
            scaleM=max(1,scaleF*length,*[abs(v) for k in ('T','My','Mz') for v in (i[k],j[k])])
            normalized=max(abs(v)/(scaleF if k in ('N','Vy','Vz') else scaleM) for k,v in residual.items())
            finite=all(math.isfinite(v) for v in [*i.values(),*j.values()])
            rows.append({'case':case,'analysis_id':f['analysis_id'],'element_id':f['element_id'],'length_m':length,
                'residual_SI':residual,'max_relative_residual':normalized,'status':'PASS' if finite and normalized<1e-6 else 'FAIL'})
    bad=[r for r in rows if r['status']!='PASS'];axesbad=[r for r in axes if r['status']!='PASS']
    out={'status':'PASS' if not bad and not axesbad else 'FAIL','scope':'HISTORICAL_ONLY_NOT_CURRENT_FE_VALIDATION',
        'external_repo_clue':'jpCaceres123/Proyecto-1-MCOC b4a7bd8 Edificio/verification/tests/test_postproceso.py',
        'member_cases':len(rows),'axis_count':len(axes),'force_failures':len(bad),'axis_failures':len(axesbad),
        'max_relative_residual':max(r['max_relative_residual'] for r in rows),'tolerance_relative':1e-6,
        'units':'N, N.m, m; nodal end actions','sources':sources,'axis_checks':axes,'checks':rows}
    (ROOT/'entregas/PRE_P1L5/historical_equilibrium_qa.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ('sources','axis_checks','checks')},indent=2))
    return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
