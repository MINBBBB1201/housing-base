"""Diagnostics: (1) plan map of v8 interference points by part, (2) OEM rim/wall-top profile vs our constant lip,
unrolled along the perimeter, both in CAD heights above the OEM exterior plane (zp)."""
import sys, json, numpy as np
sys.path.insert(0, '.')
from fs_common import *
from final_sim import PARTS, ZREF
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
body = ColumnSolid(load_stl(CAD / sys.argv[1]), h=0.5)
import re; TAG = (re.search(r'_(v\d+(?:_\d+)?)_', sys.argv[1]) or re.search(r'(.*)', 'cad')).group(1)
oemT = dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover-1_002.stl'), ZREF)
oem = ColumnSolid(oemT, h=0.5)
fig, ax = plt.subplots(figsize=(13, 8.6))
cols = plt.cm.tab20(np.linspace(0, 1, len(PARTS)))
for p, c in zip(PARTS, cols):
    S = sample_surface(dell_to_cad(load_stl(DELL / f'{p}.stl'), ZREF), 0.5)
    ins, dep = body.inside(S)
    if ins.sum() > 20:
        ax.scatter(S[ins, 0], S[ins, 1], s=2, color=c, label=f"{p.replace('Ins_15_3525_', '').replace('Inspiron_3525_', '')} ({ins.sum()})")
ax.plot([0, W, W, 0, 0], [0, 0, D, D, 0], 'k-', lw=0.8)
ax.set_xlim(-5, W + 5); ax.set_ylim(D + 5, -5); ax.set_aspect('equal'); ax.grid(alpha=0.3)
ax.set_title('body: internal-part surfaces inside our solid (CAD XY; top = hinge/rear, left = DC-in side)')
ax.legend(fontsize=8, loc='center', markerscale=6); fig.tight_layout(); fig.savefig(f'{TAG}-interference-map.png', dpi=110)
# perimeter profile: OEM wall-top height above zp vs ours (top-most solid in a 4 mm band inside the outline)
def band_top(solid, pts):
    top = solid.column_top(); out = []
    for x, y in pts:
        i = int(round((x - solid.x0) / solid.h)); j = int(round((y - solid.y0) / solid.h))
        out.append(top[i, j] - zp(y) if 0 <= i < solid.nx and 0 <= j < solid.ny else np.nan)
    return np.array(out)
def wall_profile(solid, wall, s_list, depth=(0.5, 3.5)):
    res = []
    for s in s_list:
        vals = []
        for q in np.arange(depth[0], depth[1] + 0.01, 0.5):
            x, y = {'rear': (s, q), 'front': (s, D - q), 'left': (q, s), 'right': (W - q, s)}[wall]
            vals.append(band_top(solid, [(x, y)])[0])
        vals = np.array(vals); res.append(np.nanmax(vals) if np.isfinite(vals).any() else np.nan)
    return np.array(res)
prof = {}
fig, axs = plt.subplots(4, 1, figsize=(13, 11))
for ax, (wall, L) in zip(axs, (('rear', W), ('front', W), ('left', D), ('right', D))):
    s = np.arange(1, L - 1, 1.0)
    po, pu = wall_profile(oem, wall, s), wall_profile(body, wall, s)
    prof[wall] = {'s': s.tolist(), 'oem': np.round(po, 2).tolist(), 'ours': np.round(pu, 2).tolist()}
    ax.plot(s, po, 'g-', label='OEM wall top above exterior plane (Dell guide mesh)')
    ax.plot(s, pu, 'r-', label='our wall/clip top above zp')
    ax.set_title(f'{wall} wall ({"X" if wall in ("rear", "front") else "Y"} mm)'); ax.grid(alpha=0.3); ax.set_ylabel('mm')
axs[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(f'rim-profile-oem-vs-{TAG}.png', dpi=100)
json.dump(prof, open(f'rim-profile-{TAG}.json', 'w'))
for wall in prof:
    po = np.array(prof[wall]['oem'], float); pu = np.array(prof[wall]['ours'], float)
    print(f"{wall:5s} OEM wall top: min {np.nanmin(po):5.2f} median {np.nanmedian(po):5.2f} max {np.nanmax(po):5.2f} | v8: median {np.nanmedian(pu):5.2f}")
