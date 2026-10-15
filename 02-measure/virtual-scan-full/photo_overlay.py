"""Register a real top-down interior photo (base cover removed, hinges at top) to the Dell 3D model and overlay.
Model view: from below, hinge at top -> u = (Xmax - X) * s, v = (Ymax - Y) * s  (physical frame of build_full_model.py)."""
import sys, json, numpy as np, cv2, trimesh
from pathlib import Path
PH = Path(sys.argv[1]); OUT = sys.argv[2]
S = 5.0                                                   # px per mm in the model render
EXCL = {'Ins_15_3525_Base_Cover_GP', 'Inspiron_3525_Basecover_Remove_Screws', 'Inspiron_3525_Basecover_Loosen_Screws'}
info = json.load(open('full-model-info.json'))
parts = {p.stem: trimesh.load(p, force='mesh') for p in Path('parts_phys').glob('*.stl') if p.stem not in EXCL}
V = np.concatenate([m.vertices for m in parts.values()]); X1, Y1 = V[:, 0].max(), V[:, 1].max(); X0, Y0 = V[:, 0].min(), V[:, 1].min()
W, H = int((X1 - X0) * S) + 1, int((Y1 - Y0) * S) + 1
def uv(P): return np.stack([(X1 - P[:, 0]) * S, (Y1 - P[:, 1]) * S], 1)
# painter's render (lowest Z drawn last = visible from below)
img = np.full((H, W, 3), 255, np.uint8); lab = np.zeros((H, W), np.int16)
tris, cols, ids = [], [], []
pal = {n: tuple(int(c) for c in np.random.default_rng(i).integers(40, 230, 3)) for i, n in enumerate(sorted(parts))}
for k, (n, m) in enumerate(sorted(parts.items())):
    T = m.vertices[m.faces]; tris.append(T); ids += [k] * len(T)
T = np.concatenate(tris); ids = np.array(ids); order = np.argsort(-T[:, :, 2].min(1))
names = sorted(parts)
for t, k in zip(T[order], ids[order]):
    p = uv(t).astype(np.int32)
    cv2.fillConvexPoly(img, p, pal[names[k]]); cv2.fillConvexPoly(lab, p, int(k) + 1)
cv2.imwrite('model-bottom-view.png', img)
edges = cv2.Canny((lab * 13 % 255).astype(np.uint8), 1, 2)
# photo: laptop silhouette = non-background
ph = cv2.imread(str(PH)); g = cv2.cvtColor(ph, cv2.COLOR_BGR2GRAY)
mask = (g < 235).astype(np.uint8); mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cnts, key=cv2.contourArea)
box = cv2.boxPoints(cv2.minAreaRect(c))
def order4(b):
    s = b.sum(1); d = b[:, 0] - b[:, 1]
    return np.array([b[np.argmin(s)], b[np.argmax(d)], b[np.argmax(s)], b[np.argmin(d)]], np.float32)   # tl, tr, br, bl
src = order4(box)
mm = (lab > 0).astype(np.uint8); cm, _ = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
dst = order4(cv2.boxPoints(cv2.minAreaRect(max(cm, key=cv2.contourArea))))
Hm = cv2.getPerspectiveTransform(src, dst)
warp = cv2.warpPerspective(ph, Hm, (W, H), borderValue=(255, 255, 255))
ov = warp.copy(); ov[edges > 0] = (0, 255, 255)
cv2.imwrite(OUT, ov); cv2.imwrite(OUT.replace('.png', '-photo-rectified.png'), warp)
print('photo box px', np.round(src).tolist(), 'model box px', np.round(dst).tolist(), 'model mm', np.round([(dst[1]-dst[0])[0]/S, (dst[3]-dst[0])[1]/S], 1).tolist())
json.dump({'S_px_per_mm': S, 'X1': float(X1), 'Y1': float(Y1), 'H': Hm.tolist()}, open(OUT.replace('.png', '.json'), 'w'))
