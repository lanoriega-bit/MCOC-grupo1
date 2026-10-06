"""Read-only external contrast. Existing audited transforms; no external push/write."""
import importlib.util
import json
import subprocess
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ext4',ROOT/'entregas/POST_P1L4/scripts/audit_ext4_slabs_properties_connectivity.py')
ext4=importlib.util.module_from_spec(spec);spec.loader.exec_module(ext4)
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True,encoding='utf-8')
def main():
    transforms=json.loads((ROOT/'entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json').read_text(encoding='utf-8-sig'))['normalization']['transforms']
    external={};sources=[]
    for name,path,function in (
        ('SANTIAGO','P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json',ext4.external_santiago),
        ('CACERES','Edificio/results/modelo_3d_manual.json',ext4.external_caceres)):
        repo=ROOT/'recursos/planos/external_slab_refs'/name.lower()
        data=json.loads(git(repo,'show','HEAD:'+path))
        ext4.load=lambda _path: data
        external[name]=function(Path(path),transforms[name])
        sources.append({'repo':name,'commit':git(repo,'rev-parse','HEAD').strip(),'path':path,'raw_slab_count':len(data['slabs']),'normalization':'existing independently audited rigid transforms; comparison only'})
    master=json.loads((ROOT/'entregas/P1L5/modelo_central/model_master.json').read_text(encoding='utf-8-sig'))
    rows=[]
    for slab in master['elements']:
        if not slab.get('active') or slab['type']!='slab':continue
        g=shape(slab['geometry']['physical_polygon']);key=(slab['building'],slab['floor'])
        row={'building':key[0],'floor':key[1],'ours_area_m2':g.area}
        for name,groups in external.items():
            other=groups.get(key)
            row[name]=ext4.comp(g,other)
            if other is not None:
                row[name]['holes']=sum(len(p.interiors) for p in (list(other.geoms) if other.geom_type=='MultiPolygon' else [other]))
                row[name]['bounds']=list(other.bounds)
        row['decision']='SECONDARY_CLUE_ONLY_NOT_PHYSICAL_BOUNDARY_CONFIRMATION'
        rows.append(row)
    result={'status':'READ_ONLY_COMPLETE_NO_EXTERNAL_GEOMETRY_ADOPTED','sources':sources,'floors':rows,
        'reason':'Santiago uses rectangular beam-enclosed load panels, not independently measured physical perimeters. Caceres uses manual slab polygons; hole/perimeter agreement is insufficient to promote unresolved CAD edges. Existing transformations are comparison references, not an alignment of our model.'}
    (HERE/'EXTERNAL_SLAB_CONTRAST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
