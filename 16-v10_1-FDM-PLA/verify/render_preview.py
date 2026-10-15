"""Previews from the PRINT STLs (real orientation). top: looking down from the keyboard side, hinge at top."""
import numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path
P = Path(__file__).resolve().parents[1]
body = trimesh.load_mesh(P / 'dell3525_basecover_v10_1_FDM_PLA_PRINT_body.stl')
lid = trimesh.load_mesh(P / 'dell3525_basecover_v10_1_FDM_PLA_PRINT_lid.stl')
def shade(m, base, light=(0.3, -0.5, 0.8)):
    l = np.array(light) / np.linalg.norm(light); k = 0.45 + 0.55 * np.clip(m.face_normals @ l, 0, 1)
    return np.clip(np.array(base)[None, :] * k[:, None], 0, 1)
def view(ax, parts, elev, azim, title):
    for m, col, dz in parts:
        tri = m.triangles.copy(); tri[:, :, 2] += dz
        pc = Poly3DCollection(tri, facecolors=shade(m, col), edgecolors='none', linewidths=0); ax.add_collection3d(pc)
    ax.set_xlim(0, 355); ax.set_ylim(0, 226); ax.set_zlim(-60, 60); ax.set_box_aspect((355, 226, 60))
    ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, fontsize=11)
def flat(ax, m, col, title, from_below=False):
    tri = m.triangles.copy()
    order = np.argsort(tri[:, :, 2].mean(1)); order = order[::-1] if from_below else order
    t2 = tri[order][:, :, :2].copy()
    if not from_below: t2[:, :, 0] = 355.32 - t2[:, :, 0]; t2[:, :, 1] = 226.2 - t2[:, :, 1]   # rotate 180: hinge at top
    else: t2[:, :, 1] = 226.2 - t2[:, :, 1]                                                     # seen from below: hinge at top
    from matplotlib.collections import PolyCollection
    n = m.face_normals[order]; k = 0.35 + 0.65 * np.abs(n[:, 2]) * (0.6 + 0.4 * (tri[order][:, :, 2].mean(1) / 30))
    ax.add_collection(PolyCollection(t2, facecolors=np.clip(np.array(col)[None, :] * k[:, None], 0, 1), edgecolors='none'))
    ax.set_xlim(-5, 360); ax.set_ylim(-5, 231); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, fontsize=10)
fig, axs = plt.subplots(1, 3, figsize=(21, 5.6))
flat(axs[0], body, (0.55, 0.6, 0.68), 'BODY from keyboard side (hinge = top).\neDP window upper-LEFT, fan grille upper-RIGHT. Opposite = mirrored, reject.')
flat(axs[1], body, (0.55, 0.6, 0.68), 'BODY from below / desk side (hinge = top). Lid opening, feet', from_below=True)
flat(axs[2], lid, (0.93, 0.55, 0.12), 'SERVICE LID from below (hinge side = top). 10 x M2 screw holes', from_below=True)
for ax in axs[:2]: ax.axhline(226.2 - 16.6, color='#e8590c', lw=0.8, ls='--'); ax.text(3, 226.2 - 14.5, 'wedge starts Y16.6 (v10.1: 5.6)', color='#e8590c', fontsize=8)
plt.tight_layout(); plt.savefig(P / 'preview_v10_1_FDM.png', dpi=95); print('ok')
