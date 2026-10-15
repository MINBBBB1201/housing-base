"""Side-on orthographic depth maps of the palmrest perimeter walls (looking at each wall from outside),
with the measured clip positions overlaid. 6 px/mm along the wall, 10 px/mm in Z."""
import json, numpy as np, cv2
from vs_common import load_stl
P = load_stl('../../00-input/dell-official-3d/parts/Ins_15_3525_Palmrest_GP.stl')
B = load_stl('../../00-input/dell-official-3d/parts/Inspiron_3525_Basecover-1_002.stl')
clips = json.load(open('clips.json'))['clips']
SA, SZ = 6.0, 10.0; Z0, Z1 = -2.5, 9.0
def raster(T, along, depth_sign, depth_axis, s0, s1):
    Wd, Hd = int((s1 - s0) * SA), int((Z1 - Z0) * SZ)
    zb = np.full((Hd, Wd), -np.inf)
    for t in T:
        c = (t[:, along] - s0) * SA; r = (t[:, 2] - Z0) * SZ; d = depth_sign * t[:, depth_axis]
        cmin, cmax = int(max(np.floor(c.min()), 0)), int(min(np.ceil(c.max()), Wd - 1)); rmin, rmax = int(max(np.floor(r.min()), 0)), int(min(np.ceil(r.max()), Hd - 1))
        if cmax < cmin or rmax < rmin: continue
        den = (r[1] - r[2]) * (c[0] - c[2]) + (c[2] - c[1]) * (r[0] - r[2])
        if abs(den) < 1e-12: continue
        cc, rr = np.meshgrid(np.arange(cmin, cmax + 1) + .5, np.arange(rmin, rmax + 1) + .5)
        w0 = ((r[1] - r[2]) * (cc - c[2]) + (c[2] - c[1]) * (rr - r[2])) / den; w1 = ((r[2] - r[0]) * (cc - c[2]) + (c[0] - c[2]) * (rr - r[2])) / den
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (1 - w0 - w1 >= -1e-6); z = w0 * d[0] + w1 * d[1] + (1 - w0 - w1) * d[2]
        sub = zb[rmin:rmax + 1, cmin:cmax + 1]; m &= z > sub; sub[m] = z[m]
    return zb
walls = {'right': (1, +1, 0, 0, 226.2), 'left': (1, -1, 0, 0, 226.2), 'rear': (0, -1, 1, 0, 355.3), 'front': (0, +1, 1, 0, 355.3)}
for wall, (al, sg, dax, s0, s1) in walls.items():
    zp = raster(P, al, sg, dax, s0, s1)
    ok = np.isfinite(zp); lo, hi = np.percentile(zp[ok], [2, 98])
    v = np.clip((zp - lo) / (hi - lo + 1e-9), 0, 1)
    img = np.where(ok[..., None], (cv2.applyColorMap((v * 255).astype(np.uint8), cv2.COLORMAP_TURBO)), 255).astype(np.uint8)
    for c in clips:
        if c['wall'] != wall: continue
        s = c['y'] if wall in ('left', 'right') else c['x']; x = int((s - s0) * SA)
        col = {'A': (0, 160, 0), 'B': (0, 0, 255), 'C': (160, 0, 160)}[c['conf']]
        cv2.line(img, (x, 0), (x, img.shape[0] - 1), col, 1); cv2.putText(img, c['id'], (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, col, 1)
    for mm in range(int(s0), int(s1) + 1, 10):
        x = int((mm - s0) * SA); cv2.line(img, (x, img.shape[0] - 8), (x, img.shape[0] - 1), (0, 0, 0), 1)
        if mm % 50 == 0: cv2.putText(img, str(mm), (x + 2, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.imwrite(f'palm-side-{wall}.png', img); print(wall, img.shape, 'depth', round(lo, 1), round(hi, 1))
