"""Side-view comparison: orthographic render of the 3D model (left or right side) vs a side photo/drawing.
Registration: bbox of the laptop silhouette in the image <-> model side silhouette bbox (uniform scale from length).
Usage: python side_overlay.py <image> <left|right> <out.png> [thr]"""
import sys, numpy as np, cv2, trimesh
from pathlib import Path
img_p, side, out = sys.argv[1], sys.argv[2], sys.argv[3]; thr = int(sys.argv[4]) if len(sys.argv) > 4 else 200
S = 8.0
parts = {p.stem: trimesh.load(p, force='mesh') for p in Path('parts_phys').glob('*.stl')}
V = np.concatenate([m.vertices for m in parts.values()]); Y0, Y1, Z0, Z1 = V[:, 1].min(), V[:, 1].max(), V[:, 2].min(), V[:, 2].max()
W, H = int((Y1 - Y0) * S) + 1, int((Z1 - Z0) * S) + 1
names = sorted(parts); lab = np.zeros((H, W), np.int16); shade = np.full((H, W, 3), 255, np.uint8)
T = np.concatenate([parts[n].vertices[parts[n].faces] for n in names]); ids = np.concatenate([[k] * len(parts[n].faces) for k, n in enumerate(names)])
N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
if side == 'left':  u = lambda t: (Y1 - t[:, 1]) * S; depth = T[:, :, 0].min(1); order = np.argsort(-depth); lit = np.abs(N[:, 0])   # viewer at -X: front at right
else:               u = lambda t: (t[:, 1] - Y0) * S; depth = -T[:, :, 0].max(1); order = np.argsort(-depth); lit = np.abs(N[:, 0])  # viewer at +X: front at left
for i in order:
    t = T[i]; p = np.stack([u(t), (Z1 - t[:, 2]) * S], 1).astype(np.int32)
    g = int(60 + 150 * lit[i]); cv2.fillConvexPoly(shade, p, (g, g, g)); cv2.fillConvexPoly(lab, p, int(ids[i]) + 1)
edges = cv2.Canny((lab * 23 % 255).astype(np.uint8), 1, 2)
im = cv2.imread(img_p); gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
m = (gray < thr).astype(np.uint8); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, cc, st, _ = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
x, y, w, h = st[k, :4]
sc = W / w                                    # uniform scale from length
im2 = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
ox, oy = int(x * sc), int(y * sc)
canvas = np.full((H + 200, W, 3), 255, np.uint8)
crop = im2[max(oy - 100, 0): oy + H + 100, ox: ox + W]
canvas[: crop.shape[0], : crop.shape[1]] = crop
top = 100 if oy >= 100 else oy                # model placed so that silhouettes' top edges coincide
ov = canvas.copy(); ys, xs = np.nonzero(edges); ov[ys + top, xs] = (0, 200, 255)
stack = np.vstack([ov, np.full((20, W, 3), 255, np.uint8), np.pad(shade, ((0, 0), (0, 0), (0, 0)))])
cv2.imwrite(out, stack)
print(f'image laptop bbox px {x},{y},{w},{h} -> height/length image {h / w:.4f} vs model {(Z1 - Z0) / (Y1 - Y0):.4f}; model {Y1 - Y0:.1f} x {Z1 - Z0:.1f} mm; image height implies {h * (Y1 - Y0) / w:.1f} mm')
