"""Checks the approved P1 exclusions and reports reproducible analysis deltas."""
import json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    exclusion=read(HERE/'P1_LATERAL_EXCLUSION.json')
    master=read(ROOT/'entregas/P1L5/modelo_central/model_master.json')
    loads=read(ROOT/'entregas/P1L5/modelo_central/loads.json')
    totals=loads['current_load_application']['totals'];old=exclusion['old_totals']
    removed=unary_union([shape(s['geometry']) for s in exclusion['surfaces']])
    slab=next(e for e in master['elements'] if e['element_id']=='E1-P1-L-001')
    prefixes=('L700-E1-P1-H08','L700-E1-P1-H10','L700-E1-P1-H12')
    checks={'excluded physical surfaces absent':shape(slab['geometry']['physical_polygon']).intersection(removed).area<1e-5,
            'six excluded catalog entries':len(exclusion['excluded_load_entries'])==6,
            'excluded load entries absent':not any(e['load_id'].startswith(prefixes) for e in loads['audited_load_catalog']['entries'])}
    panels=read(ROOT/'entregas/P1L5/analysis/generated/current_tributary_panels.json')['panos']
    checks['excluded tributary panels absent']=not any(p['id'].startswith(prefixes) for p in panels)
    cases={c:read(ROOT/f'entregas/P1L5/analysis/results/current/{c}.json') for c in ['G','Q','EX','EY']}
    delta={k:totals[k]-old[k] for k in ['G_total_N','Q_N']}
    weight=lambda t:t['G_total_N']+.5*t['Q_N']
    physics={}
    for c,r in cases.items():
        previous=exclusion['old_case_qa'][c];qa=r['qa']
        checks[c+' equilibrium']=qa['equilibrium_status']=='PASS'
        physics[c]={'old':previous,'current':qa,'delta_max_translation_m':qa['max_translation_m']-previous['max_translation_m'],
                    'delta_reaction_force_N':[a-b for a,b in zip(qa['reaction_force_N'],previous['reaction_force_N'])]}
    report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'surfaces':exclusion['surfaces'],
            'old_totals':old,'current_totals':totals,'delta_N':delta,
            'G_plus_half_Q_weight_N':{'old':weight(old),'current':weight(totals),'delta':weight(totals)-weight(old)},
            'actual_seismic_floor_weight_N':{'old':exclusion['old_case_qa']['EX']['external_force_N'][0]/.2,
                                            'current':sum(f['seismic_weight_N'] for f in cases['EX']['seismic_floor_loads'])},
            'weight_note':'Global G+0.5Q includes gravity weights not assigned to the seismic floor groups; actual lateral cases use only documented seismic_floor_loads. No formulation change.',
            'analysis_delta':physics,'pending':'Other physical contours/void classifications still REVIEW_REQUIRED; hull outside areas diagnostic, not automatic removals.'}
    (HERE/'P1_LATERAL_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'checks':checks,'delta_N':delta,'seismic_weight':report['actual_seismic_floor_weight_N']},indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
