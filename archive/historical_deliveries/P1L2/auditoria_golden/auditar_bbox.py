import json, collections, math

base = r'C:\Users\matis\OneDrive\Documentos\Proyecto_1_MCOC\entregas\P1L2\unity_export'


def bbox_points(solids):
    out = {}
    for s in solids:
        fl = s.get('floor')
        cat = s.get('category')
        if fl not in out:
            out[fl] = {}
        if cat not in out[fl]:
            out[fl][cat] = {'x0': 1e9, 'y0': 1e9, 'x1': -1e9, 'y1': -1e9, 'n': 0}
        b = out[fl][cat]
        pts = []
        if 'center' in s and len(s.get('center', [])) >= 2:
            cx, cy = s['center'][0], s['center'][1]
            dx = s.get('width_m', 0) / 2.0
            dy = s.get('depth_m', 0) / 2.0
            pts = [(cx - dx, cy - dy), (cx + dx, cy + dy)]
        if 'start' in s and len(s.get('start', [])) >= 2:
            a = s['start']
            c = s['end']
            pts.append((a[0], a[1]))
            pts.append((c[0], c[1]))
        for (x, y) in pts:
            b['x0'] = min(b['x0'], x)
            b['x1'] = max(b['x1'], x)
            b['y0'] = min(b['y0'], y)
            b['y1'] = max(b['y1'], y)
        b['n'] += 1
    return out


for name in ['model_viewer.json', 'model_viewer_candidate.json']:
    d = json.load(open(base + '\\' + name, encoding='utf-8'))
    print('#####', name, '#####')
    bx = bbox_points(d['solids'])
    for fl in sorted(bx.keys()):
        for cat in sorted(bx[fl].keys()):
            b = bx[fl][cat]
            n = b['n']
            print('  %-5s %-8s n=%5d X[%8.2f,%8.2f] Y[%8.2f,%8.2f]' % (
                str(fl), str(cat), n, b['x0'], b['x1'], b['y0'], b['y1']))