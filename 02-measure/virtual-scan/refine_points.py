"""Predict reference-hole pixels in a photo from an initial homography, refine to the darkest blob nearby,
and write a verification mosaic. Usage: python refine_points.py <photo> <H_json> <out_prefix>"""
import sys, json, numpy as np, cv2
photo, hjson, out = sys.argv[1:4]
H = np.array(json.load(open(hjson))['H_photo_to_dell_mm']); Hi = np.linalg.inv(H)
img = cv2.imread(photo); g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0).astype(float)
pts = {'pin-RL': (57.55, 16.08), 'pin-RR': (297.55, 16.08), 'notch-L': (64.07, 3.02), 'notch-R': (291.18, 3.02),
       'pin-FL': (59.5, 197.5), 'pin-FR': (295.75, 197.5)}
res = {}; tiles = []
for k, (x, y) in pts.items():
    p = Hi @ np.array([x, y, 1.0]); u, v = p[:2] / p[2]
    r = 14; x0, y0 = int(u) - r, int(v) - r
    win = g[y0:y0 + 2 * r + 1, x0:x0 + 2 * r + 1]
    j, i = np.unravel_index(np.argmin(win), win.shape)
    # sub-pixel centroid of the dark core
    thr = win.min() + 0.35 * (np.median(win) - win.min()); m = win <= thr
    n, lab = cv2.connectedComponents(m.astype(np.uint8)); core = lab == lab[j, i]
    yy, xx = np.nonzero(core); uc, vc = x0 + xx.mean(), y0 + yy.mean()
    res[k] = {'pred': [round(u, 1), round(v, 1)], 'refined': [round(uc, 1), round(vc, 1)], 'shift_px': round(float(np.hypot(uc - u, vc - v)), 1)}
    t = img[int(v) - 30:int(v) + 31, int(u) - 30:int(u) + 31].copy(); t = cv2.resize(t, (244, 244), interpolation=cv2.INTER_NEAREST)
    s = 244 / 61; cv2.circle(t, (int((u - int(u) + 30) * s), int((v - int(v) + 30) * s)), 6, (0, 255, 255), 1)
    cv2.circle(t, (int((uc - int(u) + 30) * s), int((vc - int(v) + 30) * s)), 9, (0, 0, 255), 2)
    cv2.putText(t, k, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1); tiles.append(t)
cv2.imwrite(out + '-check.png', np.hstack(tiles)); json.dump(res, open(out + '-refs.json', 'w'), indent=1)
for k, v in res.items(): print(k, v)
