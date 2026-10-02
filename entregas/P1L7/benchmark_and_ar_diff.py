"""Read-only benchmark extraction and exact baseline/current AR identity diff."""
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = "3cc21d613377f295880974a62fe98c48c9eea50f"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def old(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode('utf-8-sig'))


def main():
    path = "entregas/P1L6/preparation/current_ar_elements.json"
    before, after = old(path), read(path)
    a = {r['element_id']: r for r in before['elements']}
    b = {r['element_id']: r for r in after['elements']}
    added = [{k: b[i].get(k) for k in ('element_id','elementTag','solidTag','type','building','floor')}
             for i in sorted(b.keys()-a.keys())]
    removed = sorted(a.keys()-b.keys())
    groups = Counter((r['building'],r['floor'],r['type']) for r in added)
    result = {'base_commit':BASE,'before':len(a),'after':len(b),'added':added,'removed':removed,
              'added_by_group':[{'building':k[0],'floor':k[1],'type':k[2],'count':v} for k,v in sorted(groups.items())],
              'reason':'Base AR export predates CURRENT geometry corrections; exact identity diff, not an inference from counts.',
              'non_FE':'Slabs/supports are intentionally visual-only; no fabricated results/capacity.'}
    (OUT/'AR_EXACT_DIFF.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    app = read('entregas/P1L5/modelo_central/loads.json')['current_load_application']
    historical = old('entregas/P1L5/modelo_central/loads.json')['current_load_application']
    sx = read('entregas/P1L5/analysis/results/current/EX.json')['seismic_floor_loads']
    rows=[]
    benchmarks={'EDIFICIO_1':{'CM':47140276.,'CV':11620380.,'EX':6593501.,'EY':4331107.},
                'EDIFICIO_2':{'CM':34723194.,'CV':11096777.,'EX':2953084.,'EY':3680735.}}
    for building, etabs in benchmarks.items():
        actual=app['by_building'][building]
        force=sum(r['lateral_force_N'] for r in sx if r['building']==building)
        for case, key in [('G','CM'),('Q','CV'),('EX','EX'),('EY','EY')]:
            value=actual['G_total_N' if case=='G' else 'Q_N'] if case in ('G','Q') else force
            rows.append({'building':building,'case':case,'CURRENT_N':value,'ETABS_N':etabs[key],
                         'difference_percent':100*(value/etabs[key]-1),
                         'comparison_scope':'building load resultant; global basal equilibrium verified separately'})
    seismic_old=sum(r['G_total_N']+.5*r['Q_N'] for r in historical['by_floor'])
    historical_correct=sum(sum(r[k] for k in ('G_self_weight_N','G_superimposed_N','G_slab_N'))+.5*r['Q_N'] for r in historical['by_floor'])
    summary={'source':'resumen_modelos.pdf, page 1, forces N; LT1=ED1/LT2=ED2', 'comparisons':rows,
             'seismic_weight_before_N':seismic_old,'seismic_weight_old_Q_correct_G_N':historical_correct,
             'missing_G_N':historical_correct-seismic_old,
             'seismic_weight_new_Q_N':sum(r['seismic_weight_N'] for r in sx),
             'note':'New Q is deliberately different; do not interpret the Q-driven decrease as the effect of fixing missing G.',
             'unmatched':['ETABS node 311/2987 and C9/C21/B739/C1/C4/B189 have no verified CURRENT crosswalk; no false displacement/internal-force comparison.',
                          'ETABS modal periods not comparable: this CURRENT pipeline does not perform eigenanalysis.',
                          'Pseudo-static 0.2*(G+0.5Q), centroid-nearest-node and rigid-arm simplifications differ from ETABS.']}
    (OUT/'ETABS_COMPARISON.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# ETABS: contraste sin calibración','',summary['source'],'', '| Edificio | Caso | CURRENT [MN] | ETABS [MN] | Diferencia |','| --- | --- | ---: | ---: | ---: |']
    lines += [f"| {r['building']} | {r['case']} | {r['CURRENT_N']/1e6:.6f} | {r['ETABS_N']/1e6:.6f} | {r['difference_percent']:+.2f}% |" for r in rows]
    lines += ['', 'G/Q: resultantes por edificio; EX/EY: fuerza aplicada por edificio, no reacción basal individual asignada arbitrariamente.',
              'La nueva Q uniforme explica gran parte de la diferencia CV. G conserva espesores de losa/materiales académicos; no se han ajustado contra ETABS.',
              '', *['- '+s for s in summary['unmatched']], '']
    (OUT/'ETABS_COMPARISON.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'AR_before':len(a),'AR_after':len(b),'added':len(added),'removed':len(removed),'missing_G_N':summary['missing_G_N']},indent=2))


if __name__ == '__main__':
    main()
