"""Exact user-approved S1 exclusion, zero-area mesh repair, fail-closed loads.

No physical perimeter is inferred from tributary zones. Remaining boundaries
are retained as review candidates, with explicit independent geometry storage.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

from shapely import constrained_delaunay_triangles, set_precision
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/'entregas/P1L5/modelo_central'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
sys.path.insert(0,str(HERE))
from audit_slabs import mesh_polygon

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    master=read(CENTRAL/'model_master.json');loads=read(CENTRAL/'loads.json')
    checkpoint='CURRENT_SLAB_S1_SOUTH_EXCLUSION_AND_MESH_REPAIR'
    if any(r.get('revision')==checkpoint for r in master.get('geometry_revision_history',[])):
        print('ALREADY_APPLIED');return
    # Invalidate first. Never leave modified loads displayed as CURRENT.
    contract=read(STREAM/'current_dataset_contract.json')
    contract.update(status='STALE_REANALYSIS_REQUIRED',analysis_available=False,loads_approved=False,
                    result_state='STALE_REANALYSIS_REQUIRED')
    write(STREAM/'current_dataset_contract.json',contract)
    entries=loads['audited_load_catalog']['entries']
    removed=[r for r in entries if r['load_id'].startswith(('L700-E1-S1-H04-','L700-E1-S1-H05-'))]
    assert len(removed)==4
    south=unary_union([shape(r['geometry']) for r in removed])
    assert 227<south.area<228 and south.bounds[3]<0
    loads['audited_load_catalog']['entries']=[r for r in entries if r not in removed]
    # Preserve history separately: excluded entries no longer feed CURRENT.
    for r in removed:r['current_application']={'status':'REMOVED_USER_APPROVED_PHYSICAL_SECTOR','applied':False}
    rows=[]
    for slab in master['elements']:
        if slab['type']!='slab':continue
        geom=slab['geometry'];old=copy.deepcopy(geom);poly,pieces=mesh_polygon(geom)
        if slab['element_id']=='E1-S1-L-001':poly=poly.difference(south.buffer(0.000002))
        # Canonical CAD geometry is six decimal metres. Snap numerical seams,
        # not architectural gaps (1 micrometre, no larger closure tolerance).
        poly=set_precision(poly,0.000001)
        parts=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
        vertices=[];indices=[];rings=[]
        for part in parts:
            assert part.is_valid and part.area>0
            for ring in [part.exterior,*part.interiors]:rings.append([list(p) for p in list(ring.coords)[:-1]])
            for tri in constrained_delaunay_triangles(part).geoms:
                if tri.area<=1e-10:continue
                base=len(vertices);vertices.extend([list(p) for p in list(tri.exterior.coords)[:3]])
                indices.extend([base,base+1,base+2])
        mesh=unary_union([Polygon([vertices[j] for j in indices[i:i+3]]) for i in range(0,len(indices),3)])
        assert mesh.symmetric_difference(poly).area<1e-6
        geom.update(surface_vertices_xy=vertices,surface_triangles=indices,boundary_rings_xy=rings,
                    area_m2=round(poly.area,6),hole_count=sum(len(p.interiors) for p in parts),
                    physical_polygon=mapping(poly),physical_boundary_status='REVIEW_REQUIRED_PRIMARY_BOUNDARY',
                    physical_boundary_source='EXISTING_CURRENT_GEOMETRY_WITH_USER_APPROVED_S1_EXCLUSION')
        x0,y0,x1,y1=poly.bounds;geom['center_m']=[round((x0+x1)/2,6),round((y0+y1)/2,6),old['center_m'][2]]
        if slab['element_id']=='E1-S1-L-001':
            geom['source_panel_ids']=[x for x in geom.get('source_panel_ids',[]) if x not in ('L700-E1-S1-H04','L700-E1-S1-H05')]
        slab.setdefault('geometry_review',[]).append({'type':'SLAB_MESH_REPAIRED','review_checkpoint':checkpoint,
            'reason':'Removed zero-area numerical triangles; only S1 south physical sector removed by explicit user approval.',
            'old_geometry':old,'new_area_m2':geom['area_m2'],'tolerance_m':0.000001,
            'loads_reanalysis_required':True})
        rows.append({'element_id':slab['element_id'],'old_area_m2':old['area_m2'],'area_m2':geom['area_m2'],
                     'holes':geom['hole_count'],'components':len(parts),'triangles':len(indices)//3})
    master['sources']['current_contract'].update(status='STALE_REANALYSIS_REQUIRED',analysis_version='NONE_REANALYSIS_REQUIRED')
    master.setdefault('geometry_revision_history',[]).append({'revision':checkpoint,'slabs_updated':10,
        'physical_exclusion':'ED1 S1 south: explicit user approval 2026-10-01','load_entries_removed':4,
        'fe_topology_changed':False,'physical_boundary_review_required':True})
    write(CENTRAL/'model_master.json',master);write(CENTRAL/'loads.json',loads)
    write(HERE/'APPROVED_CLEANUP.json',{'checkpoint':checkpoint,'removed_area_m2':south.area,
        'excluded_load_entries':removed,'slabs':rows,'physics_changed':True,
        'sources':'user explicit S1 south approval + current mesh (not new load-zone union)'})
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
