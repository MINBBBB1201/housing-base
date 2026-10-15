"""Dimensional conformance: our CAD body vs the Dell 3525 3D-guide OEM base cover and palmrest.
Checks (all in the CAD frame, OEM mapped with dell_to_cad):
  1. handedness of the CAD frame vs the physical laptop
  2. scale: Dell assembly bbox vs Dell published dimensions, OEM cover vs user ruler
  3. plan outline (silhouette) per edge, corners, hinge notches
  4. screw holes: our hole centre/size vs OEM screw axis, OEM cover hole, palmrest boss
  5. rim-top height vs OEM (from rim-profile-<tag>.json)
Usage: python dim_check.py <body.stl> [--print-frame]   (--print-frame: STL already mirrored x -> W - x)"""
import sys, json, re, numpy as np
sys.path.insert(0, '.')
from fs_common import *
ZREF = 10.06
body_name = sys.argv[1]; PRINT = '--print-frame' in sys.argv
TAG = (re.search(r'_(v\d+\w*?)_body', body_name) or re.search(r'(.*)', 'cad')).group(1) + ('-print' if PRINT else '')
ours = load_stl(CAD / body_name)
if PRINT:                                    # bring the print-frame STL back to the design frame for comparison
    ours = ours.copy(); ours[..., 0] = W - ours[..., 0]; ours = ours[:, ::-1]
oem = dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover-1_002.stl'), ZREF)
palm = dell_to_cad(load_stl(DELL / 'Ins_15_3525_Palmrest_GP.stl'), ZREF)
out = {'body': body_name, 'print_frame': PRINT}

# ---- 1. handedness -------------------------------------------------------------------------------------------
def det3(M): return float(np.linalg.det(np.array(M, float)))
# Dell parts frame = glTF (right-handed) through toCAD [x,-z,y] (det +1) -> right-handed.
# dell_to_cad keeps X,Y and negates Z -> det -1: the design frame is a mirror of physical space.
out['handedness'] = {'gltf_to_parts_det': det3([[1, 0, 0], [0, 0, -1], [0, 1, 0]]),
                     'dell_to_cad_det': det3([[1, 0, 0], [0, 1, 0], [0, 0, -1]]),
                     'print_frame_det(design->print, x->W-x)': det3([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])}

# ---- 2. scale ------------------------------------------------------------------------------------------------
disp = load_stl(DELL / 'Ins_15_3525_Display_Assembly_GP.stl'); pr = load_stl(DELL / 'Ins_15_3525_Palmrest_GP.stl')
bb = lambda T: (T.reshape(-1, 3).max(0) - T.reshape(-1, 3).min(0)).round(2).tolist()
out['scale'] = {'display_assembly_bbox_mm': bb(disp), 'dell_spec_WxD_mm': [358.50, 235.56],
                'palmrest_bbox_mm': bb(pr), 'oem_cover_bbox_mm': bb(oem), 'user_ruler_cover_mm': [355, 227],
                'ours_bbox_mm': bb(ours)}

# ---- 3. outline ----------------------------------------------------------------------------------------------
H = 0.25
so = ColumnSolid(oem, h=H); su = ColumnSolid(ours, h=H)
occ_o = (so.count > 0).reshape(so.nx, so.ny); occ_u = (su.count > 0).reshape(su.nx, su.ny)
xs = so.x0 + np.arange(so.nx) * H; ys = so.y0 + np.arange(so.ny) * H
def edge(occ, axis, side):
    """Outermost occupied coordinate per line (nan if empty). axis 0: per Y row -> X extents."""
    o = occ if axis == 0 else occ.T
    coord = xs if axis == 0 else ys
    anyv = o.any(0)
    if side == 'min': idx = np.argmax(o, 0)
    else: idx = o.shape[0] - 1 - np.argmax(o[::-1], 0)
    return np.where(anyv, coord[idx], np.nan)
res = {}
for name, axis, side, lo, hi in (('left edge (X min)', 0, 'min', 12, 214), ('right edge (X max)', 0, 'max', 12, 214),
                                 ('rear edge (Y min)', 1, 'min', 70, 285), ('front edge (Y max)', 1, 'max', 12, 343)):
    eo, eu = edge(occ_o, axis, side), edge(occ_u, axis, side)
    line = ys if axis == 0 else xs
    m = (line >= lo) & (line <= hi) & np.isfinite(eo) & np.isfinite(eu)
    d = (eu - eo)[m] * (1 if side == 'max' else -1)          # + = ours sticks out beyond OEM
    res[name] = {'span': [lo, hi], 'oem_median': round(float(np.median(eo[m])), 2), 'ours_median': round(float(np.median(eu[m])), 2),
                 'dev_median': round(float(np.median(d)), 2), 'dev_min': round(float(d.min()), 2), 'dev_max': round(float(d.max()), 2)}
# silhouette XOR (area) split into "ours only" and "OEM only"
cell = H * H
res['area_ours_only_mm2'] = round(float((occ_u & ~occ_o).sum() * cell), 1)
res['area_oem_only_mm2'] = round(float((occ_o & ~occ_u).sum() * cell), 1)
res['area_oem_mm2'] = round(float(occ_o.sum() * cell), 1)
# corners: diagonal inset from the bbox corner to the first occupied cell (R corner -> (1-1/sqrt2) R sqrt2)
def corner_inset(occ, cx, cy, sx, sy):
    for t in np.arange(0, 20, H / 2):
        x, y = cx + sx * t / np.sqrt(2), cy + sy * t / np.sqrt(2)
        i = int(round((x - so.x0) / H)); j = int(round((y - so.y0) / H))
        if occ[i, j]: return round(float(t), 2)
    return None
res['corner_diag_inset'] = {k: {'oem': corner_inset(occ_o, *c), 'ours': corner_inset(occ_u, *c)} for k, c in
                            {'rear-left': (0, 0, 1, 1), 'rear-right': (W, 0, -1, 1), 'front-left': (0, D, 1, -1), 'front-right': (W, D, -1, -1)}.items()}
# hinge notches: along the rear edge, X extents where the silhouette starts later than Y=3
def notches(occ):
    eo = edge(occ, 1, 'min'); m = np.isfinite(eo) & (eo > 3)
    runs, cur = [], None
    for x, f, e in zip(xs, m, eo):
        if f and cur is None: cur = [x, x, e]
        elif f: cur[1] = x; cur[2] = max(cur[2], e)
        elif cur is not None: runs.append(cur); cur = None
    return [[round(a, 2), round(b, 2), round(e, 2)] for a, b, e in runs if b - a > 5]
res['hinge_notches_[x0,x1,depthY]'] = {'oem': notches(occ_o), 'ours': notches(occ_u)}
out['outline'] = res

# ---- 4. screws -----------------------------------------------------------------------------------------------
SCREWS = [('rear-L', 20.41, 11.83), ('rear-C', 177.66, 11.83), ('rear-R', 334.91, 11.83), ('mid-L', 9.01, 119.63),
          ('mid-R', 346.31, 119.63), ('front-L', 9.01, 217.14), ('front-C', 177.66, 217.98), ('front-R', 346.31, 217.14)]
scr = dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover_Remove_Screws.stl'), ZREF)
scr = np.concatenate([scr, dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover_Loosen_Screws.stl'), ZREF)])
def through_hole(T, x, y, r=4.0, h=0.05):
    """Empty (no crossing at all) columns around (x,y): centroid, X/Y extent of the component nearest (x,y)."""
    cs = ColumnSolid(T, x - r, y - r, x + r, y + r, h)
    emp = (cs.count == 0).reshape(cs.nx, cs.ny)
    from scipy.ndimage import label
    lab, n = label(emp)
    I, J = np.meshgrid(np.arange(cs.nx), np.arange(cs.ny), indexing='ij')
    X, Y = cs.x0 + I * h, cs.y0 + J * h
    best = None
    for k in range(1, n + 1):
        mk = lab == k
        if mk[0, :].any() or mk[-1, :].any() or mk[:, 0].any() or mk[:, -1].any(): continue    # touches window edge
        cx, cy = X[mk].mean(), Y[mk].mean(); dd = np.hypot(cx - x, cy - y)
        if best is None or dd < best[0]:
            best = (dd, cx, cy, X[mk].max() - X[mk].min() + h, Y[mk].max() - Y[mk].min() + h, mk.sum() * h * h)
    if best is None: return None
    return {'cx': round(best[1], 2), 'cy': round(best[2], 2), 'size_x': round(best[3], 2), 'size_y': round(best[4], 2),
            'eq_d': round(float(2 * np.sqrt(best[5] / np.pi)), 2)}
def screw_axis(x, y, r=2.2):
    V = scr.reshape(-1, 3); m = np.hypot(V[:, 0] - x, V[:, 1] - y) < r
    P = V[m]; return round(float((P[:, 0].min() + P[:, 0].max()) / 2), 2), round(float((P[:, 1].min() + P[:, 1].max()) / 2), 2)
def palm_boss(x, y, r=4.0, h=0.05):
    """Palmrest boss: columns whose lowest palmrest crossing is the boss face (Dell Z 4.45 -> CAD zp + 5.61)."""
    cs = ColumnSolid(palm, x - r, y - r, x + r, y + r, h)
    I, J = np.meshgrid(np.arange(cs.nx), np.arange(cs.ny), indexing='ij'); X, Y = cs.x0 + I * h, cs.y0 + J * h
    low = np.full(cs.nx * cs.ny, np.nan); has = cs.count > 0; low[has] = cs.z[cs.start[has]]
    low = low.reshape(cs.nx, cs.ny) - zp(Y)
    mk = np.abs(low - (ZREF - 4.45)) < 0.08
    if mk.sum() < 20: return None
    from scipy.ndimage import label
    lab, n = label(mk); k = lab[int(round((x - cs.x0) / h)), int(round((y - cs.y0) / h))]
    if k == 0:
        sizes = [(lab == i).sum() for i in range(1, n + 1)]; k = 1 + int(np.argmax(sizes))
    m = lab == k
    return {'cx': round(float(X[m].mean()), 2), 'cy': round(float(Y[m].mean()), 2), 'eq_d': round(float(2 * np.sqrt(m.sum() * h * h / np.pi)), 2)}
rows = []
for name, x, y in SCREWS:
    ax_ = screw_axis(x, y); ho = through_hole(oem, x, y); hu = through_hole(ours, x, y); pb = palm_boss(x, y)
    row = {'screw': name, 'oem_screw_axis': ax_, 'oem_cover_hole': ho, 'our_hole': hu, 'palmrest_boss': pb}
    if hu:
        row['our_vs_axis_mm'] = round(float(np.hypot(hu['cx'] - ax_[0], hu['cy'] - ax_[1])), 2)
        if pb: row['our_vs_boss_mm'] = round(float(np.hypot(hu['cx'] - pb['cx'], hu['cy'] - pb['cy'])), 2)
    rows.append(row)
out['screws'] = rows

# ---- 5. rim height -------------------------------------------------------------------------------------------
try:
    prof = json.load(open(f'rim-profile-{re.sub(r"_PRINT.*|-print", "", TAG)}.json'))
    rim = {}
    for wall, p in prof.items():
        s = np.array(p['s']); po = np.array(p['oem'], float); pu = np.array(p['ours'], float)
        d = pu - po; ok = np.isfinite(d)
        rim[wall] = {'n': int(ok.sum()), 'median_ours_minus_oem': round(float(np.median(d[ok])), 2),
                     'within_-0.5..+0.1': round(float(((d[ok] > -0.5) & (d[ok] < 0.1)).mean()), 3),
                     'higher_than_oem_(>+0.1)': int((d[ok] > 0.1).sum()), 'lower_by_>1mm': int((d[ok] < -1).sum())}
    out['rim'] = rim
except FileNotFoundError:
    out['rim'] = 'run diag_rim.py first'

json.dump(out, open(f'dim-check-{TAG}.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))

# ---- figure --------------------------------------------------------------------------------------------------
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(14, 9.2))
img = np.zeros((so.ny, so.nx, 3)) + 1
img[(occ_o & occ_u).T] = [0.82, 0.82, 0.82]; img[(occ_u & ~occ_o).T] = [0.85, 0.1, 0.1]; img[(occ_o & ~occ_u).T] = [0.1, 0.35, 0.9]
ax.imshow(img, extent=[so.x0 - H / 2, so.x0 + so.nx * H - H / 2, so.y0 + so.ny * H - H / 2, so.y0 - H / 2], interpolation='nearest')
for r in rows:
    a = r['oem_screw_axis']; ax.plot(*a, 'k+', ms=14, mew=1.5)
    if r['our_hole']: ax.plot(r['our_hole']['cx'], r['our_hole']['cy'], 'o', mfc='none', mec='r', ms=10, mew=1.5)
    if r['palmrest_boss']: ax.plot(r['palmrest_boss']['cx'], r['palmrest_boss']['cy'], 'gx', ms=10, mew=1.5)
    ax.annotate(f"{r['screw']}\nhole-axis {r.get('our_vs_axis_mm', '-')}", a, xytext=(8, 8), textcoords='offset points', fontsize=8)
ax.set_xlim(-5, W + 5); ax.set_ylim(D + 5, -5); ax.set_aspect('equal'); ax.grid(alpha=0.3)
ax.set_title(f'{TAG}: plan silhouette  grey = both, red = ours only, blue = OEM only | + OEM screw axis, o our hole, x palmrest boss\n'
             'design frame (X = DC-in side -> right, Y = hinge -> front)', fontsize=10)
fig.tight_layout(); fig.savefig(f'dim-check-{TAG}.png', dpi=110)
