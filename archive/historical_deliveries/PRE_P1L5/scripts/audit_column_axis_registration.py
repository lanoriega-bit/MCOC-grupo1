"""Primary RLE-EJES controls: distinguish floor registration from column offsets."""
import hashlib,sys,json
from audit_user_structural_review import ROOT,OUT,write
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
import audit_ed1_walls as cad
HANDLES={'S1':['1C32A','1C328','1C327'],'P1':['1D060','1D05F','1D05E'],'P2':['1ECFC','1ECFB','1ECFA'],'P3':['1F4A3','1F4A2','1F4A1'],'P4':['1E58F','1E58E','1E58D']}
def main():
    rows=[]
    for floor,handles in HANDLES.items():
        sheet,_,origin=cad.FLOOR_SOURCES[floor];path=cad.DXF_DIR/sheet;doc=cad.ezdxf.readfile(path)
        for axis,canonical,handle in zip(['1','2','3'],[0,8.9,16.15],handles):
            e=doc.entitydb[handle];assert e.dxftype()=='LINE' and e.dxf.layer=='RLE-EJES' and abs(e.dxf.start.y-e.dxf.end.y)<.01
            observed=(origin[1]-e.dxf.start.y)/100
            rows.append({'floor':floor,'sheet':sheet,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'handle':handle,'layer':e.dxf.layer,'axis':axis,'original_cad_start_cm':list(e.dxf.start),'original_cad_end_cm':list(e.dxf.end),'current_origin_cm':origin,'canonical_y_m':canonical,'transformed_axis_y_m':observed,'residual_m':observed-canonical})
    write(OUT/'column_axis_primary_evidence.json',{'status':'FLOOR_REGISTRATION_CONTRADICTION_REVIEW_REQUIRED','applied':False,'rows':rows,'decision':'Do not translate only S1/P1 columns to upper model XY. Reconcile complete floor extraction transforms, primary grids and load-zone registration in a separately reviewed change. Approved 700 calibration untouched.'})
    md=['# Control primario de ejes antes de alinear columnas','','RLE-EJES del DXF, no coordenadas deducidas de fotografías ni de textos. Escala cm→m, Y invertida conforme al extractor vigente.','', '| Piso | Eje | Lámina / handle | Y transformada m | Y canónica m | Residual m |','|---|---|---|---:|---:|---:|']
    for r in rows:md.append(f"| {r['floor']} | {r['axis']} | {r['sheet']} / {r['handle']} | {r['transformed_axis_y_m']:.6f} | {r['canonical_y_m']:.3f} | {r['residual_m']:.6f} |")
    md+=['','P1 queda prácticamente en 0/8.9/16.15; S1 y P2–P4 presentan ~+0.181 m en la transformación de caras/ejes. Algunas columnas S1 fueron normalizadas mediante otro origen. La discrepancia supera 5 cm y afecta al registro de plantas, no a una única columna.','', 'No se aplica corrección: se requiere reconciliar transformaciones completas y comprobar vigas, muros y losas antes de seleccionar XY objetivo. Se mantiene intacto el calce aprobado de cargas 700.']
    (OUT/'COLUMN_AXIS_PRIMARY_CONTROLS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print('Primary axis controls:',len(rows),'NO_GEOMETRY_CHANGE')
if __name__=='__main__':main()
