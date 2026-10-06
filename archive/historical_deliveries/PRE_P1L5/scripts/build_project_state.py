"""Build delivery history and current state from immutable Git snapshots and QA.

Never executes analysis or writes into a delivered snapshot.
"""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'entregas/PRE_P1L5'
STREAM = ROOT / 'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
GEOMETRY = 'entregas/P1L2/unity_export/model_combined_viewer.json'
FE = 'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8-sig')

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def counts(model):
    data = Counter(s.get('category', 'unknown') for s in model.get('solids', []))
    return f"{len(model.get('solids', []))} sólidos: " + ', '.join(f'{key}={value}' for key, value in sorted(data.items()))

def main():
    current = read(GEOMETRY)
    candidate = read(FE)
    definitions = [
        ('P1L2', 'entregap1l2', 'entregas/P1L2/unity_export/model_viewer.json', 'entregas/P1L2/README.md',
         'Modelo 3D desde CAD; ejes, pisos, columnas, vigas, muros y gravedad preliminar.',
         'HISTÓRICO ENTREGADO: esqueleto y viewer preliminares, no modelo físico definitivo.',
         'P1L2_CORRECTED_CURRENT: usar geometría POST-P1L4; losas y propiedades todavía parciales.',
         'Centrolineas consolidadas; muros ED2 100→54 entre checkpoints posteriores; vigas ED2 515→267. No comparar prismas CAD con miembros FE como si fueran iguales.',
         'Equilibrio histórico no certifica geometría. QA actual: ejes, pisos, continuidad y geometría; pendientes explícitos.'),
        ('P1L3', 'P1L3_DELIVERED', GEOMETRY, 'entregas/P1L3/INFORME.md',
         'G: permanentes; Q: viva; EX/EY: sismo X/Y; R: combinación. OpenSees y capacidad HA separada.',
         'VALID_AS_DELIVERED_ASSUMPTION: validaciones numéricas bajo geometría y cargas de esa entrega.',
         'STILL_VALID_METHOD / SUPERSEDED_INPUT / NEEDS_RECALCULATION: inputs actuales no compatibles.',
         'Q uniforme conserva el papel de ensayo del motor. Catálogo 700, PP.LOSA, cargas especiales y masas deben validarse antes de recalcular.',
         'Conservación Q, equilibrio EX/EY y superposición de desplazamiento/reacción/fuerzas documentados en A7. P-M es capacidad de sección, no certificado del edificio.'),
        ('P1L4', 'P1L4_FINAL', GEOMETRY, 'entregas/P1L4/FINAL_STATUS.md',
         'Unity como postprocesador: identidad/nodos/sección/material, ejes, N/V/T/M, deformada, gráficos 2D/3D, cargas/apoyos/tributarias, P-M y demanda.',
         'HISTÓRICO ENTREGADO: postprocesador funcional; fuerzas de la corrida P1L3 y capacidad con supuestos declarados.',
         'UI_ONLY_UPDATE + DATASET_SUPERSEDED: conservar métodos; reintegrar una corrida compatible cuando exista.',
         'Interfaz semántica, ejes geométricos distinguidos del FE, crosswalk candidato y separación estricta actual/histórico.',
         'Compilación/Play y contratos entregados. END_FORCES_INTERPOLATION no se presenta como diagrama interno exacto.'),
    ]
    deliveries = []
    for key, tag, model_path, doc, objective, original, corrected, changes, qa in definitions:
        commit = git('rev-parse', tag + '^{commit}').strip()
        model = json.loads(git('show', f'{tag}:{model_path}'))
        deliveries.append(dict(id=key, title=key, tag=tag, commit=commit, objective=objective,
            original_status=original, current_status=corrected, changes=changes, qa=qa,
            statistics=counts(model), model_path=model_path, source_path=doc,
            url=f'https://github.com/lanoriega-bit/MCOC-grupo1/blob/{commit}/{doc}',
            unknown_metrics='Pendientes/correcciones históricas: no homologables; no inferir cero.'))
    residual = {gid for comp in candidate['floating_excluded']['components'] for gid in comp['geometry_element_ids']}
    heights = sum(s['category']=='beam' and s.get('section_height_m') is None for s in current['solids'])
    material_count=sum(s.get('material_confidence')=='CONFIRMED_FROM_PLAN' for s in current['solids'])
    force_qa_path=OUT/'historical_equilibrium_qa.json'
    force_qa=json.loads(force_qa_path.read_text(encoding='utf-8')) if force_qa_path.exists() else None
    if force_qa:
        for delivery in deliveries[1:]:
            delivery['qa']+=f" Equilibrio local histórico: {force_qa['status']}, {force_qa['member_cases']} barra/casos y {force_qa['axis_count']} ejes. No valida CURRENT."
    state = dict(format='MCOC_PRE5_PROJECT_STATE_V1', geometry='POST_P1L4_CURRENT',
        properties=f'{material_count} materiales confirmados por plano; REVIEW_REQUIRED: {heights} alturas, ED1 P4 y losas',
        fe='CANDIDATE NOT RUN', results='NONE CURRENT', unity='PASS: checkpoint UX / ver QA vigente',
        pending=len(residual), floating_components=len(candidate['floating_excluded']['components']),
        geometry_count=len(current['solids']), fe_members=len(candidate['elements']),
        beam_heights_pending=heights, geometry_sha256=hashlib.sha256((ROOT/GEOMETRY).read_bytes()).hexdigest(),
        fe_sha256=hashlib.sha256((ROOT/FE).read_bytes()).hexdigest(),
        geometry_path=GEOMETRY, fe_path=FE, baseline_status='BLOCKED',
        blockers=[f'{len(residual)} trayectorias FE pendientes; no añadir apoyos ficticios',
                  'Restricciones múltiples/cadenas sin formulación validada',
                  'Alturas/materiales/losas y cobertura completa de cargas por confirmar'],
        deliveries=deliveries)
    state['deliveries'].append(dict(id='POST-P1L4', title='POST-P1L4 / PRE-P1L5', tag='', commit='',
        objective='Auditoría comparativa Santiago/Cáceres; fuentes primarias antes de cambios.',
        original_status='EXT-0…EXT-5: geometría auditada, candidato sin ejecutar.',
        current_status=f"MODELO ACTUAL: {len(residual)} pendientes FE / {state['floating_components']} componentes.",
        changes=f'Correcciones de caras duplicadas; {material_count} materiales confirmados por nota primaria; trazabilidad. No se implementa P1L5.',
        qa='Geometría/contratos/Unity validados; análisis resistente aún no aprobado.',
        statistics=counts(current), model_path=GEOMETRY, source_path='entregas/PRE_P1L5/PRE_P1L5_STATUS.md',
        url='https://github.com/lanoriega-bit/MCOC-grupo1/tree/codex/post-p1l4-structural-audit/entregas/PRE_P1L5',
        unknown_metrics='No existe aún una nueva corrida compatible.'))
    OUT.mkdir(parents=True, exist_ok=True)
    for path in (OUT/'project_state.json', STREAM/'project_state.json'):
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({d['id']:d['statistics'] for d in deliveries}, ensure_ascii=False, indent=2))

if __name__=='__main__':
    main()
