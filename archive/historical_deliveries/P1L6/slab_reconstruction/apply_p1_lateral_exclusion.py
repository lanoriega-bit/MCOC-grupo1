"""Explicit user exclusion: ED1/P1 north H08 and south H10/H12 only.

Do not clip the structural hull or other outboard floors. Historical data stays
in this report and geometry_review. CURRENT is invalidated before input writes.
"""
import copy
import json
from pathlib import Path
from shapely import constrained_delaunay_triangles, set_precision
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/'entregas/P1L5/modelo_central'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    revision='ED1_P1_TWO_UNSUPPORTED_LATERAL_SLABS_EXCLUDED'
    master=read(CENTRAL/'model_master.json');loads=read(CENTRAL/'loads.json')
    if any(r.get('revision')==revision for r in master.get('geometry_revision_history',[])):
        print('ALREADY_APPLIED');return
    prefixes=('L700-E1-P1-H08-','L700-E1-P1-H10-','L700-E1-P1-H12-')
    entries=loads['audited_load_catalog']['entries']
    removed=[e for e in entries if e['load_id'].startswith(prefixes)]
    assert len(removed)==6
    north=unary_union([shape(e['geometry']) for e in removed if '-H08-' in e['load_id']])
    south=unary_union([shape(e['geometry']) for e in removed if '-H08-' not in e['load_id']])
    assert 100<north.area<102 and 70<south.area<71
    assert north.bounds[0]>61 and north.bounds[1]>16.5
    assert south.bounds[0]>61 and south.bounds[3]<-1.14
    slab=next(e for e in master['elements'] if e['element_id']=='E1-P1-L-001')
    old=copy.deepcopy(slab['geometry']);original=shape(old['physical_polygon'])
    poly=set_precision(original.difference(unary_union([north,south]).buffer(0.000002)),0.000001)
    assert poly.is_valid and original.area-poly.area>171 and original.area-poly.area<172
    components=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
    vertices=[];indices=[];rings=[]
    for part in components:
        for ring in [part.exterior,*part.interiors]:rings.append([list(p) for p in list(ring.coords)[:-1]])
        for triangle in constrained_delaunay_triangles(part).geoms:
            if triangle.area<=1e-10:continue
            offset=len(vertices);vertices.extend([list(p) for p in list(triangle.exterior.coords)[:3]])
            indices.extend([offset,offset+1,offset+2])
    hole_count=sum(len(p.interiors) for p in components)
    assert hole_count==old['hole_count']
    contract=read(STREAM/'current_dataset_contract.json')
    contract.update(status='STALE_REANALYSIS_REQUIRED',analysis_available=False,loads_approved=False,result_state='STALE_REANALYSIS_REQUIRED')
    write(STREAM/'current_dataset_contract.json',contract)
    report={'revision':revision,'baseline_commit':'d81514d','building':'EDIFICIO_1','floor':'P1',
      'surfaces':[{'side':'NORTH','source_panels':['L700-E1-P1-H08'],'area_m2':north.area,'geometry':mapping(north)},
                  {'side':'SOUTH','source_panels':['L700-E1-P1-H10','L700-E1-P1-H12'],'area_m2':south.area,'geometry':mapping(south)}],
      'old_geometry':old,'new_area_m2':poly.area,'old_totals':loads['current_load_application']['totals'],
      'excluded_load_entries':copy.deepcopy(removed),
      'old_case_qa':{case:read(ROOT/f'entregas/P1L5/analysis/results/current/{case}.json').get('qa',{}) for case in ['G','Q','EX','EY']},
      'primary_authority':'Explicit user correction 2026-10-01; exact two lateral areas reviewed in TOP',
      'preserved_outboard':'H13 x37–45 north extension and other floors untouched; no structural hull clipping'}
    g=slab['geometry'];g.update(physical_polygon=mapping(poly),area_m2=round(poly.area,6),surface_vertices_xy=vertices,
      surface_triangles=indices,boundary_rings_xy=rings,hole_count=hole_count,
      physical_boundary_source='EXISTING_CURRENT_MESH_WITH_USER_APPROVED_S1_AND_P1_EXCLUSIONS')
    x0,y0,x1,y1=poly.bounds;g['center_m']=[round((x0+x1)/2,6),round((y0+y1)/2,6),old['center_m'][2]]
    g['source_panel_ids']=[p for p in g.get('source_panel_ids',[]) if p not in ('L700-E1-P1-H08','L700-E1-P1-H10','L700-E1-P1-H12')]
    slab.setdefault('geometry_review',[]).append({'type':'SLAB_LATERAL_EXCLUSION','review_checkpoint':revision,
      'old_geometry':old,'new_area_m2':g['area_m2'],'reason':'Two unsupported lateral surfaces explicitly excluded by user; associated active load zones removed.'})
    loads['audited_load_catalog']['entries']=[e for e in entries if e not in removed]
    master['sources']['current_contract'].update(status='STALE_REANALYSIS_REQUIRED',analysis_version='NONE_REANALYSIS_REQUIRED')
    master.setdefault('geometry_revision_history',[]).append({'revision':revision,'element_id':slab['element_id'],'load_entries_removed':6,'fe_topology_changed':False})
    write(HERE/'P1_LATERAL_EXCLUSION.json',report);write(CENTRAL/'model_master.json',master);write(CENTRAL/'loads.json',loads)
    print(json.dumps({'removed_north_m2':north.area,'removed_south_m2':south.area,'new_P1_area_m2':poly.area,'holes':hole_count},indent=2))
if __name__=='__main__':main()
