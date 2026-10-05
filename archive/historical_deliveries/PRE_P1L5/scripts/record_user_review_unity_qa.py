"""Archive successful Unity run only when the built/current payloads match."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5/user_structural_review'
PROJECT=ROOT/'entregas/P1L3/José/viewer_unity';BUILD=PROJECT/'Builds/CurrentReview'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    result=(BUILD/'QA/UX_QA.txt').read_text();assert result.startswith('PASS:'),result
    log=ROOT/'user-review-build-final.log';assert '[CURRENT BUILD] PASS' in log.read_text(encoding='utf-8',errors='replace')
    assert (BUILD/'QA/UX_QA.txt').stat().st_mtime>log.stat().st_mtime,'Stale Play QA'
    stream=PROJECT/'Assets/StreamingAssets';built=BUILD/'StructuralReview_Data/StreamingAssets'
    names=['model_viewer.json','post_p1l3_fe_diagnostic.json','project_state.json','fe_pending_review.json']
    for name in names:assert load(stream/name)==load(built/name),name
    geometry=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json';fe=ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
    assert load(fe)['inputs']['geometry_sha256']==hashlib.sha256(geometry.read_bytes()).hexdigest()
    qa=load(OUT/'review_qa.json');qa['checks']['Unity']='PASS';qa['unity_evidence']={'build_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'play_log_sha256':hashlib.sha256((ROOT/'user-review-player-final.log').read_bytes()).hexdigest(),'geometry_sha256':hashlib.sha256(geometry.read_bytes()).hexdigest(),'fe_sha256':hashlib.sha256(fe.read_bytes()).hexdigest(),'verified_payloads':names,'report':result}
    (OUT/'review_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name in ['current_1366x768.png','current_1920x1080.png','state_1920x1080.png']:
        shutil.copy2(BUILD/'QA'/name,OUT/('unity_'+name))
    (OUT/'UNITY_REVIEW_QA.md').write_text('# Unity — revisión de alcance y fusiones\n\nPASS: compilación Unity 6000.6.0f1 y ejecución de Main en Player.\n\n'+result+'\n\nPruebas adicionales: cada exclusión ausente de model.solids; cada fusión tiene exactamente un ID canónico y ningún ID absorbido activo; registro de cambios y pendientes ligados a hash de geometría; número de pendientes leído desde metadata, no 43 fijo. Se comprueba igualdad de los cuatro payloads principales entre fuente y aplicación compilada.\n\nLa primera prueba detectó un fixture que seleccionaba el muro excluido E1-P4-M-007. Fue reemplazado por E1-P4-M-003 y la segunda pasada resultó PASS; no se debilitó el test de ejes/material desconocido.\n\nCapturas: `unity_current_1366x768.png`, `unity_current_1920x1080.png`, `unity_state_1920x1080.png`. No constituye validación resistente ni corrida OpenSees.\n',encoding='utf-8')
    print('Unity compilation/Play/payload QA PASS')
if __name__=='__main__':main()
