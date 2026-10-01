"""Numerical regression: exact source exclusions, unchanged FE, void-preserving meshes."""
import json
import subprocess
from pathlib import Path
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def baseline(path):return json.loads(subprocess.check_output(['git','show','21aa110:'+path],cwd=ROOT,text=True,encoding='utf-8-sig'))
def main():
    path='entregas/P1L5/modelo_central/model_master.json';old=baseline(path);master=read(ROOT/path)
    loads=read(ROOT/'entregas/P1L5/modelo_central/loads.json');report=read(HERE/'after/SLAB_SOURCE_AUDIT.json')
    panels=read(ROOT/'entregas/P1L5/analysis/generated/current_tributary_panels.json')['panos']
    visual=read(ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/p1l5_current_tributary_areas.json')['areas']
    old_elements={e['element_id']:e for e in old['elements']};slabs=[e for e in master['elements'] if e.get('active') and e['type']=='slab']
    checks={
      'FE topology unchanged':master['fe_topology']==old['fe_topology'],
      'structural members unchanged':all(e==old_elements[e['element_id']] for e in master['elements'] if e['type']!='slab'),
      'ten floors covered':len(slabs)==10 and len({(e['building'],e['floor']) for e in slabs})==10,
      'no active boxes':all(e['geometry']['kind']=='slab_polygon' for e in slabs),
      'no orphan receptors':not report['orphan_receivers'] and not report['unity_tributary_orphans'],
      'no duplicate panel IDs':not report['duplicate_panel_ids'],
      'no load overlap':all(abs(e['load_overlap_m2'])<1e-4 for e in report['floors']),
      'no degenerate slab triangles':all(e['valid'] and e['degenerate_triangles']==0 and abs(e['mesh_sum_area_m2']-e['area_m2'])<1e-4 for e in report['floors']),
      'G Q conservation':all(loads['current_load_application']['conservation'][c]['status']=='PASS' for c in ['G','Q']),
      'approved zones inactive':all(not e['load_id'].startswith(('L700-E1-S1-H04-','L700-E1-S1-H05-')) for e in loads['audited_load_catalog']['entries']),
    }
    strips=[p for p in panels if 'LINE-SC-100-STRIP' in p['id']]
    checks['single equivalent line strip']=len(strips)==1
    checks['line strip correct live intensity']=len(strips)==1 and abs(strips[0]['case_force_N']['Q']-strips[0]['area_m2']*100*9.80665)<0.02
    checks['surface mesh equals physical polygon']=True;checks['hole-aware visual load mesh']=True
    for slab in slabs:
        g=slab['geometry'];v=g['surface_vertices_xy'];t=g['surface_triangles']
        mesh=unary_union([Polygon([v[j] for j in t[i:i+3]]) for i in range(0,len(t),3)])
        checks['surface mesh equals physical polygon'] &= mesh.symmetric_difference(shape(g['physical_polygon'])).area<1e-6
        old_geo=old_elements[slab['element_id']]['geometry']
        if slab['floor']!='S1' or slab['building']!='EDIFICIO_1':
            checks['preserve voids '+slab['element_id']]=g['hole_count']==old_geo['hole_count']
    for row in visual:
        verts=row['surface_vertices_xy_flat'];indices=row['surface_triangles']
        mesh=unary_union([Polygon([(verts[2*j],verts[2*j+1]) for j in indices[i:i+3]]) for i in range(0,len(indices),3)])
        checks['hole-aware visual load mesh'] &= abs(mesh.area-row['area_m2'])<1e-4
    immutable='entregas/P1L2/unity_export/model_viewer.json'
    checks['Luis original unchanged']=subprocess.check_output(['git','rev-parse','21aa110:'+immutable],cwd=ROOT).strip()==subprocess.check_output(['git','hash-object','--path='+immutable,immutable],cwd=ROOT).strip()
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'physical_boundary_certification':'REVIEW_REQUIRED_NOT_A_NUMERICAL_QA_PASS','slabs':len(slabs),'panels':len(panels),'visual_components':len(visual)}
    (HERE/'SLAB_CLEANUP_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
