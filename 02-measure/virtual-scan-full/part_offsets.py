"""Per-part misalignment between the Dell 3D model render and a rectified real photo (same pixel grid, S px/mm).
For each visible part: edge pixels of its label region vs photo Canny edges; best integer shift (+-6 mm) minimising the
mean distance to the nearest photo edge (chamfer). Reports shift in mm and chamfer before/after."""
import sys, json, numpy as np, cv2, trimesh
from pathlib import Path
rect = cv2.imread(sys.argv[1]); meta = json.load(open(sys.argv[2])); S = meta['S_px_per_mm']
EXCL = {'Ins_15_3525_Base_Cover_GP', 'Inspiron_3525_Basecover_Remove_Screws', 'Inspiron_3525_Basecover_Loosen_Screws'}
parts = {p.stem: trimesh.load(p, force='mesh') for p in Path('parts_phys').glob('*.stl') if p.stem not in EXCL}
names = sorted(parts); X1, Y1 = meta['X1'], meta['Y1']; H, W = rect.shape[:2]
lab = np.zeros((H, W), np.int16)
T = np.concatenate([parts[n].vertices[parts[n].faces] for n in names]); ids = np.concatenate([[k] * len(parts[n].faces) for k, n in enumerate(names)])
order = np.argsort(-T[:, :, 2].min(1))
for t, k in zip(T[order], ids[order]):
    cv2.fillConvexPoly(lab, np.stack([(X1 - t[:, 0]) * S, (Y1 - t[:, 1]) * S], 1).astype(np.int32), int(k) + 1)
g = cv2.GaussianBlur(cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY), (5, 5), 0)
pe = cv2.Canny(g, 40, 120); dt = cv2.distanceTransform((pe == 0).astype(np.uint8), cv2.DIST_L2, 3)
R = int(6 * S); res = {}
for k, n in enumerate(names):
    m = (lab == k + 1).astype(np.uint8)
    if m.sum() < 2000: continue
    e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)); ys, xs = np.nonzero(e)
    ok = (xs > R) & (xs < W - R) & (ys > R) & (ys < H - R); xs, ys = xs[ok], ys[ok]
    if len(xs) < 200: continue
    best = (1e9, 0, 0); c0 = float(dt[ys, xs].mean())
    for dy in range(-R, R + 1, 2):
        for dx in range(-R, R + 1, 2):
            c = float(dt[ys + dy, xs + dx].mean())
            if c < best[0]: best = (c, dx, dy)
    # refine
    c, bx, by = best
    for dy in range(by - 2, by + 3):
        for dx in range(bx - 2, bx + 3):
            cc = float(dt[ys + dy, xs + dx].mean())
            if cc < c: c, bx, by = cc, dx, dy
    # photo-frame shift (right/down in image) -> physical: image right = -X, image down = -Y
    res[n] = {'visible_px': int(m.sum()), 'chamfer_mm_at_0': round(c0 / S, 2), 'chamfer_mm_best': round(c / S, 2),
              'shift_mm_image_right_down': [round(bx / S, 2), round(by / S, 2)], 'shift_mm_physical_XY': [round(-bx / S, 2), round(-by / S, 2)]}
for n, r in sorted(res.items(), key=lambda kv: -kv[1]['visible_px']):
    print(f"{n.replace('Ins_15_3525_','').replace('Inspiron_3525_',''):28s} vis {r['visible_px']:7d}px  edge dist {r['chamfer_mm_at_0']:.2f} -> {r['chamfer_mm_best']:.2f} mm  best shift XY {r['shift_mm_physical_XY']}")
json.dump(res, open(sys.argv[3], 'w'), indent=1)
