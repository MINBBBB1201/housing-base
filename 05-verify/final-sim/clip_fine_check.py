"""Fine (0.1 mm column grid, 0.2 mm surface samples) interference check around each hook of a body STL (design frame).
The 0.5 mm grid of final_sim.py can miss thin hooks (1 mm arms). Usage: python clip_fine_check.py <body.stl> [out.json]"""
import sys, json, re, numpy as np
sys.path.insert(0, '.')
from fs_common import *
from final_sim import PARTS, ZREF
src = open(CAD / 'params.scad', encoding='utf-8').read()
m = re.search(r'clips_list\s*=\s*\[(.*?)\];', src, re.S)
CL = [(int(a), float(b), float(c), d) for a, b, c, d in re.findall(r'\[(\d),\s*([\d.]+),\s*([\d.]+),\s*"(\w)"\]', m.group(1))]
body = load_stl(CAD / sys.argv[1])
parts = {p: sample_surface(dell_to_cad(load_stl(DELL / f'{p}.stl'), ZREF), 0.2) for p in PARTS if 'Display_Assembly' not in p}
oem = dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover-1_002.stl'), ZREF)
rows = []
for w, s, cw, g in CL:
    x, y = {0: (s, 1.5), 1: (s, D - 1.5), 2: (1.5, s), 3: (W - 1.5, s)}[w]
    win = (x - 6, y - 6, x + 6, y + 6)
    cs = ColumnSolid(body, *win, 0.1); co = ColumnSolid(oem, *win, 0.1)
    row = {'wall': 'rear front left right'.split()[w], 'pos': s, 'grade': g, 'hits': {}}
    for p, S in parts.items():
        mk = (S[:, 0] > win[0] + 0.5) & (S[:, 0] < win[2] - 0.5) & (S[:, 1] > win[1] + 0.5) & (S[:, 1] < win[3] - 0.5)
        if not mk.any(): continue
        ins, dep = cs.inside(S[mk]); ino, depo = co.inside(S[mk])
        if ins.any():
            row['hits'][p.replace('Ins_15_3525_', '').replace('Inspiron_3525_', '')] = {
                'n': int(ins.sum()), 'max_depth': round(float(dep[ins].max()), 2),
                'oem_n': int(ino.sum()), 'oem_max_depth': round(float(depo[ino].max()), 2) if ino.any() else 0.0}
    rows.append(row)
    print(f"{row['wall']:5s} {s:6.1f} {g}  " + '; '.join(f"{k}: {v['n']}/{v['max_depth']} (OEM {v['oem_n']}/{v['oem_max_depth']})" for k, v in row['hits'].items()))
if len(sys.argv) > 2: json.dump(rows, open(sys.argv[2], 'w'), indent=1)
