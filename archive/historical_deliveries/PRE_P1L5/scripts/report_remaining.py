"""Human-readable residual decisions; no geometry or FE mutation."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5'
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def main():
    a=load('remaining_sources_audit.json');p=load('constraint_normalization_proposal.json')
    lines=['# EXT-7 / FE-2 — pendientes y evidencia primaria','','Estado: REVIEW_REQUIRED. No se ejecuta OpenSees.','',
        '## Propiedades confirmadas','',
        '361 miembros RC de ED2 reciben G35_10 (fc=35 MPa) y A630-420H (fy=420 MPa),',
        'por 2024_22-100, MTEXT 53994, desde fundaciones a cielo P4. Se conserva E/nu',
        'histórico sin alteración: resistencia nominal no determina toda la rigidez ni la armadura.',
        'Ed1 tiene G35 hasta cielo P3 en 2017_67-100 y G25 en detalles de 2017_67-600:',
        'se registra la evidencia, pero no se propaga globalmente. Radier G20 no se copia a losas.',
        'Se corrigió la búsqueda anterior: las notas sí existen. Render original en qa/material_*.png.',
        '', '## Ocho muros: revisión uno por uno','',
        'Estos son ocho elementos con incidencias, no ocho pares independientes. Los pares',
        'de pisos adyacentes no son duplicados de un mismo sólido. La clasificación es geométrica;',
        'un encuentro L/T estructural necesita detalle de transferencia. No se conecta por cercanía.','',
        '| Elemento | Vecino | Distancia ejes m | Área intersección m² | Lectura | Decisión |','|---|---|---:|---:|---|---|']
    for w in a['wall_overlaps']:
        for c in w['checks']:
            lines.append(f"| {w['element_id']} | {c['other_id']} | {c['axis_distance_m']:.6f} | {c['physical_footprint_overlap_m2']:.6f} | {c['classification']} | {c['action']} |")
    lines += ['', 'Cuatro continuidades paralelas difieren 0.1 mm: M-003/M-005/M-009/M-010 de P2.',
        'Son candidatos claros de tolerancia del adaptador, no cambios de geometría.',
        'No se promueven a soporte aprobado mientras los brazos rígidos y su extensión física sigan pendientes.',
        'Las áreas minúsculas (<0.0001 m²) son contacto numérico de esquina, no unión probada.',
        'No se eliminó ningún muro. Las incidencias ortogonales requieren distinguir L/T/transferencia',
        'con detalle primario; no es riguroso adjudicar una T solo porque se tocan huellas.',
        '', '## 19 alturas: todas conservadas sin valor inventado','',
        'Los tres labels próximos incluyen VAR en los 19 casos. Esto es una pista de búsqueda,',
        'NO confirmación de que las 19 vigas sean variables. La revisión amplía a TEXT/MTEXT/atributos',
        'y definiciones de bloques en 60 DXF. No asignar por vecino más próximo ni copiar A/I equivalentes externos.','',
        '| Viga | Fuente | Tres labels próximos | Decisión |','|---|---|---|---|']
    for r in a['beam_heights']:
        labels='; '.join(x['text'].replace('|','/') for x in r['nearest_primary_section_labels'])
        lines.append(f"| {r['element_id']} | {r.get('source_dxf',r.get('primary_source','ver JSON'))} | {labels} | REVIEW_REQUIRED |")
    lines += ['', '## 43 pendientes FE agrupados','', '| Edificio | Piso | Tipo | Causa | Cantidad |','|---|---|---|---|---:|']
    groups=Counter((r['building'],r['floor'],r['type'],r['cause']) for r in a['pending_fe'])
    for k,n in sorted(groups.items()):lines.append('| '+' | '.join(k)+f' | {n} |')
    lines += ['', '| ID | Clasificación | Fuente | Acción |','|---|---|---|---|']
    for r in a['pending_fe']:lines.append(f"| {r['element_id']} | {r['classification']} (diagnóstico candidato) | {r['primary_source']} | Mantener; no apoyo ficticio |")
    lines += ['', '## FE-2: propuesta cinemática separada','',
        f"{p['original_count']} restricciones → {p['normalized_count']} enlaces estrella dentro de los mismos componentes.",
        f"Ensayo de seis movimientos base: residual máximo {p['six_basis_max_residual']:.3g}; PASS algebraico.",
        'No se cambió el candidato ni se resolvió el sistema. No añade aristas entre componentes.',
        'La equivalencia presupone brazos rígidos completos y pequeñas rotaciones; no prueba su extensión física.',
        'Clusters con varios apoyos requieren tratamiento SP coherente. No copiar directamente a Transformation.',
        'Referencia: [rigidLink](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidLink.html)',
        'y [Transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/constraint/TransformationMethod.html).',
        '', '## Losas S1/P1 y huecos','',
        'Se conserva EXT-4: S1=UNRESOLVED_OUTER_PERIMETER; P1=UNRESOLVED_OUTBOARD_TRANSITION.',
        'Las regiones manuales y huecos de Cáceres no cambian en el snapshot nuevo; Santiago aporta paños,',
        'no una prueba métrica de esos límites. No hubo nueva confirmación primaria para cerrar bordes.',
        'La resta explícita de vacíos y balance bruto/neto se adopta como criterio de QA futuro, no como geometría.',
        'No se extrajeron cotas de fotos ni se clasificaron loops automáticamente como huecos.',
        '', '## Alcance y bloqueos reales','',
        'Esta relectura textual no equivale a identificar visualmente cada leader/corte/armadura de 60 láminas.',
        'No afirmar que se agotó toda la información de los originales. Faltan asociaciones inequívocas',
        'de perfiles variables, alcance material ED1, detalles de encuentros/transferencia y contornos S1/P1.',
        'Ningún miembro eliminado/añadido/movido. 43 residuales, 22 componentes y 856 miembros se mantienen.',
        'Las fuentes insuficientes se dejan explícitas; no se certifica aptitud resistente para P1L5.','']
    (OUT/'REMAINING_STRUCTURAL_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':main()
