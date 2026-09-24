"""Accept fresh compile/Play evidence only for identical built/source contracts."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5/second_structural_cleanup'
PROJECT=ROOT/'entregas/P1L3/José/viewer_unity'
BUILD=PROJECT/'Builds/CurrentReview'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    buildlog=ROOT/'second-cleanup-build-verified.log';playlog=ROOT/'second-cleanup-player-verified.log';report=BUILD/'QA/UX_QA.txt'
    assert '[CURRENT BUILD] PASS' in buildlog.read_text(encoding='utf-8',errors='replace')
    assert '[UX REVIEW QA] PASS' in playlog.read_text(encoding='utf-8',errors='replace')
    assert report.stat().st_mtime>buildlog.stat().st_mtime
    result=report.read_text();assert result.startswith('PASS:')
    stream=PROJECT/'Assets/StreamingAssets';built=BUILD/'StructuralReview_Data/StreamingAssets'
    names=['model_viewer.json','post_p1l3_fe_diagnostic.json','project_state.json','current_dataset_contract.json','fe_pending_review.json','current_review_changes.json','column_vertical_stacks.json']
    for name in names:assert read(stream/name)==read(built/name),name
    qa=read(OUT/'review_qa.json');qa['checks']['UNITY_COMPILE']='PASS';qa['checks']['UNITY_PLAY']='PASS'
    qa['unity_evidence']={'build_log_sha256':sha(buildlog),'play_log_sha256':sha(playlog),'fresh_report_sha256':sha(report),'payload_sha256':{name:sha(stream/name) for name in names},'report':result,'additional_tests':'38 stack isolation selections; S1 toggle; reset; full vertical framing at 1366x768 and 1920x1080; zero ED1 walls; absence of removed/absorbed IDs; unknown material remains unconfirmed.'}
    (OUT/'review_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name in ['current_1920x1080.png','column_stack_1366x768.png','column_stack_1920x1080.png','state_1920x1080.png']:
        assert (BUILD/'QA'/name).stat().st_mtime>buildlog.stat().st_mtime
        shutil.copy2(BUILD/'QA'/name,OUT/('unity_'+name))
    (OUT/'UNITY_QA.md').write_text('# Unity QA — segundo saneamiento\n\nPASS: Unity 6000.6.0f1 compilado y Main ejecutado en Player.\n\n'+result+'\n\nSe verificó identidad de siete archivos entre StreamingAssets y aplicación compilada, fechas posteriores a la compilación y hashes de logs. Se recorrieron las 38 cadenas, filtros y reset. Pruebas a 1366×768 y 1920×1080. Capturas adjuntas.\n\nLa primera pasada señaló un ID de fixture inexistente; se sustituyó por E1-P4-C-001, manteniendo la prueba de material desconocido. La revisión visual detectó recorte superior en stacks: se corrigió el encuadre y se añadió una comprobación de proyección vertical. La última pasada es PASS. No se ejecutó OpenSees.\n',encoding='utf-8')
    print('SECOND_CLEANUP_UNITY_QA PASS: fresh compile/Play and seven identical payloads')
if __name__=='__main__':main()
