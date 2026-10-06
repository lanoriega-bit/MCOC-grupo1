"""Directed primary review: titles, exceptions and axis-linked cut candidates.
Text matches identify sheets to inspect, NEVER a section assignment.
"""
import hashlib,json,re
from pathlib import Path
import ezdxf
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5/current_readiness'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def main():
    model=read('entregas/P1L2/unity_export/model_combined_viewer.json');byid={s['id']:s for s in model['solids']}
    pending=read('entregas/PRE_P1L5/remaining_sources_audit.json')['beam_heights'];survey=[]
    for path in sorted((ROOT/'recursos/planos/dxf_full').rglob('2017_67-*.dxf')):
        if path.stem.split('-')[1] not in ['100','101','102','103','600','300','301','302','303','304','305','306','307','308','309','310']:continue
        doc=ezdxf.readfile(path);hits=[]
        for block in doc.blocks:
            for e in block:
                if e.dxftype()=='INSERT':
                    for a in e.attribs:
                        if a.dxf.text.strip() and (a.dxf.tag.startswith('TITULO') or a.dxf.tag in ('NUMERO','ESP')):
                            hits.append({'text':a.dxf.text,'tag':a.dxf.tag,'handle':a.dxf.handle,'layer':a.dxf.layer,'block':block.name,'insert_handle':e.dxf.handle,'xy':list(a.dxf.insert)[:2]})
                if e.dxftype() not in ('TEXT','MTEXT'):continue
                text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
                if re.search(r'\bEJE|ESCAL|RAMPA|CUBIERTA|CIELO|HORMIG|G35|G25|V\.?\s*(?:F\.?\s*)?\d+\s*/',text,re.I):
                    hits.append({'text':text,'handle':e.dxf.handle,'layer':e.dxf.layer,'block':block.name,'xy':list(e.dxf.insert)[:2]})
        survey.append({'sheet':path.stem,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'hits':hits})
    rows=[]
    for r in pending:
        s=byid[r['element_id']];ax=s.get('axis_x');ay=s.get('axis_y')
        candidates=[]
        for sheet in survey:
            if not sheet['sheet'].split('-')[1].startswith('3'):continue
            titles=[h for h in sheet['hits'] if re.search(r'\bEJE',h['text'],re.I) and any(str(a) in h['text'] for a in (ax,ay) if a)]
            if titles:candidates.append({'sheet':sheet['sheet'],'axis_title_clues':titles})
        rows.append({'element_id':s['id'],'floor':s['floor'],'axes':[ax,ay],'source':s['source_dxf'],
            'section_width_m':s.get('section_width_m'),'nearest_labels':r['nearest_primary_section_labels'],
            'cut_sheet_candidates':candidates,'decision':'NO_SECTION_PROMOTED_WITHOUT_LABEL_TO_MEMBER_ASSOCIATION'})
    out={'status':'DIRECTED_REVIEW_NOT_ASSIGNMENT','sheets':survey,'beam_height_cases':rows,
         'ed1_material_decision':'Review grade scope against sheet600 title and floor contract; never global G35'}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'directed_sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('DIRECTED_SOURCE_REVIEW:',len(survey),'sheets;',len(rows),'height cases; no section assigned')
if __name__=='__main__':main()
