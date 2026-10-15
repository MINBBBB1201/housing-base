"""Vertical surface stack at each base-cover screw (scene frame, mm). For each screw, cast vertical rays
at the axis and on a ring (r = 1.6 / 2.6 / 3.6 mm) and list the Z of every surface of base body, palmrest, screw."""
import struct, json, numpy as np
def load(p):
    b = open(p, 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v'].astype(float)
P = {k: load(f'parts/{v}.stl') for k, v in {'base': 'Inspiron_3525_Basecover-1_002', 'palm': 'Ins_15_3525_Palmrest_GP',
     'rem': 'Inspiron_3525_Basecover_Remove_Screws', 'loo': 'Inspiron_3525_Basecover_Loosen_Screws'}.items()}
def ray(t, x, y):
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(den) > 1e-12; den = np.where(ok, den, 1)
    w0 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / den
    w1 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / den
    w2 = 1 - w0 - w1; m = ok & (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    z = (w0 * a[:, 2] + w1 * b[:, 2] + w2 * c[:, 2])[m]
    return sorted(set(np.round(z, 2)))
# screw axes from screw meshes: cluster screw vertices by XY
sc = np.concatenate([P['rem'], P['loo']]).reshape(-1, 3)
cent = []
for v in sc:
    for c in cent:
        if np.hypot(*(v[:2] - c['s'][:2] / c['n'])) < 4: c['s'] += v; c['n'] += 1; c['zmin'] = min(c['zmin'], v[2]); c['zmax'] = max(c['zmax'], v[2]); break
    else: cent.append({'s': v.copy(), 'n': 1, 'zmin': v[2], 'zmax': v[2]})
out = []
for c in sorted(cent, key=lambda c: (round(c['s'][1] / c['n'] / 50), c['s'][0] / c['n'])):
    x, y = c['s'][:2] / c['n']
    row = {'x': round(x, 2), 'y': round(y, 2), 'screw_z': [round(c['zmin'], 2), round(c['zmax'], 2)]}
    for r in (0.0, 1.6, 2.6, 3.6):
        # 4 directions, keep union
        zs = {k: sorted(set(sum((ray(P[k], x + r * dx, y + r * dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), []))) for k in ('base', 'palm')}
        row[f'r{r}'] = zs
    out.append(row)
    print(f"\n== screw @ X{x:.2f} Y{y:.2f}  screw Z {c['zmin']:.2f}..{c['zmax']:.2f}")
    for r in (0.0, 1.6, 2.6, 3.6):
        print(f"  r={r:<3} base {row[f'r{r}']['base']}\n        palm {row[f'r{r}']['palm']}")
json.dump(out, open('screw-stack.json', 'w'), indent=1)
