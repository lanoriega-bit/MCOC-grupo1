"""Prepare a fail-closed current dataset envelope. No results manufactured."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5/current_readiness'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    geometry='entregas/P1L2/unity_export/model_combined_viewer.json'
    fe_path='entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
    loads_path='entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json'
    fe=load(fe_path);model=load(geometry)
    versions={'format':'MCOC_CURRENT_DATASET_V1','geometry_version':digest(geometry),'fe_version':digest(fe_path),
        'loads_version':digest(loads_path),'analysis_version':'NONE_NOT_RUN',
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'timestamp':datetime.now(timezone.utc).isoformat(),'status':'BLOCKED_NOT_RUN',
        'geometry_stream_sha256':digest(STREAM/'model_viewer.json'),
        'units':{'length':'m','force':'N','moment':'N.m','stress':'Pa','mass':'kg','rotation':'rad'},
        'cases':['G','Q','EX','EY','R'],'basis_cases':['G','Q','EX','EY'],
        'analysis_available':False,'fe_approved':False,'loads_approved':False,'linear_verified':False,
        'payload_file':'','payload_sha256':'','source_geometry':geometry,'source_fe':fe_path,'source_loads':loads_path,
        'basis_policy':'Identical K, supports, local axes, node/member ordering and applied patterns; signed SI components before envelopes',
        'capacity_policy':'Immutable section/material/rebar signature per curve; change demand only for compatible linear combinations'}
    neighbors={s['id']:set() for s in model['solids']}
    for c in fe['junction_connections']:
        a,b=c['geometry_a'],c['geometry_b']
        if a in neighbors:neighbors[a].add(b)
        if b in neighbors:neighbors[b].add(a)
    pending={g for c in fe['floating_excluded']['components'] for g in c['geometry_element_ids']}
    contexts=[]
    for s in model['solids']:
        gid=s['id'];role=''
        if gid=='E1-P2-V-075':role='Viga de descanso de la escalera B, confirmada por plano. Su participación y camino de apoyo FE siguen pendientes.'
        if gid=='E1-P4-M-007':role='Muro del núcleo de ascensores con continuidad geométrica auditada. Idealización FE por validar.'
        contexts.append({'element_id':gid,'connection_status':'Camino de apoyo sin resolver.' if gid in pending else 'Incidencias geométricas identificadas; conectividad FE todavía no aprobada.',
            'candidate_neighbors':sorted(neighbors[gid]),'load_status':'Catálogo 700 disponible, no aplicado al FE actual. Las cargas y áreas receptoras deben aprobarse; ausencia de dato no significa carga cero.',
            'special_role':role})
    OUT.mkdir(parents=True,exist_ok=True)
    for directory in (OUT,STREAM):
        (directory/'current_dataset_contract.json').write_text(json.dumps(versions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (directory/'current_inspector_context.json').write_text(json.dumps({'geometry_version':versions['geometry_version'],'elements':contexts},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CURRENT_CONTRACT: BLOCKED_NOT_RUN; no result payload; '+str(len(contexts))+' inspector records')
if __name__=='__main__':main()
