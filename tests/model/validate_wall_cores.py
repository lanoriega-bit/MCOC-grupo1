"""Read-only CURRENT core continuity regression; no CAD/AR/external checkout required.

Groups and tolerances are the audited primary-source wall-continuity contract.
Historical before/after studies remain preserved separately, not rerun as CURRENT.
"""
import json
from pathlib import Path
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[2]
FLOORS = ('S1', 'P1', 'P2', 'P3', 'P4')
CORES = {
    'ED1_01': {'S1': [20,26,34], 'P1': [12,4,25], 'P2': [10,7,9], 'P3': [10,7,9], 'P4': [9,7,10]},
    'ED1_02': {'S1': [5,29,49], 'P1': [2,10,26], 'P2': [3,8,5], 'P3': [3,8,5], 'P4': [3,8,12]},
    'ED2_01': {'S1': [7,8,10], 'P1': [7,8,10], 'P2': [7,8,10], 'P3': [7,8,10], 'P4': [7,8,9]},
}

def main():
    master = json.loads((ROOT / 'model/model_master.json').read_text(encoding='utf-8-sig'))
    sections = {s['section_id']: s for s in json.loads((ROOT / 'model/sections.json').read_text(encoding='utf-8-sig'))['sections']}
    elements = {e['element_id']: e for e in master['elements']}
    errors = []
    for group, floors in CORES.items():
        prefix = 'E1' if group.startswith('ED1') else 'E2'
        footprints = []
        for floor in FLOORS:
            rows = [elements[f'{prefix}-{floor}-M-{number:03d}'] for number in floors[floor]]
            if not all(row['active'] for row in rows):
                errors.append(f'{group}/{floor}: inactive core member')
            footprints.append([(LineString([r['geometry']['start_m'][:2], r['geometry']['end_m'][:2]]),
                                sections[r['section_id']]['dimensions']['thickness_m']) for r in rows])
        for floor, footprint in zip(FLOORS, footprints):
            for (line, thickness), (base, base_thickness) in zip(footprint, footprints[0]):
                if line.hausdorff_distance(base) > 0.002 or abs(thickness-base_thickness) > 0.001:
                    errors.append(f'{group}/{floor}: primary core continuity mismatch')
    print(json.dumps({'status': 'PASS' if not errors else 'FAIL', 'groups': len(CORES),
                      'floors': len(FLOORS), 'members_checked': 45, 'errors': errors,
                      'endpoint_tolerance_m': 0.002, 'thickness_tolerance_m': 0.001}, indent=2))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
