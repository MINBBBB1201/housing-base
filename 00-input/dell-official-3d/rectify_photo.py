"""Rectify the user's own cover-interior photo into the Dell base-cover frame (mm) using the screw centres
as control points. Interior view, hinge edge at top => image column ~ +X, image row ~ +Y.
Outputs: rect-05-interior-dellframe.png (4 px/mm, Dell outline + screws + 10 mm grid) and residual report."""
import json, numpy as np, cv2
from scipy import ndimage
PX, MX, MY = 4.0, 6, 8
# --- Dell reference: screws (from Dell 3D guide) ---
dell = {'rear-L': (20.41, 11.83), 'rear-C': (177.66, 11.83), 'rear-R': (334.91, 11.83),
        'mid-L': (9.01, 119.63), 'mid-R': (346.31, 119.63), 'front-R': (346.31, 217.14), 'front-C': (177.66, 217.98)}
# --- pixel picks in 00-input/photos/05-own-cover-interior.jpg (1440x1080), picked on 2x zoom crops ---
px = {'rear-L': (112.0, 130.0), 'rear-C': (738.5, 130.0), 'rear-R': (1342.5, 150.0),
      'mid-L': (67.5, 554.0), 'mid-R': (1377.5, 564.0), 'front-R': (1371.0, 935.0), 'front-C': (730.0, 942.5)}
# independent check points: rubber-foot pin holes (rear pair) located in the photo
check_px = {'pin-rear-L': (261.5, 144.0), 'pin-rear-R': (1201.0, 165.0)}
# locate the pin holes in the Dell interior height map (small deep dots near Y~16)
z = np.load('bc-interior-depth.npy'); ok = np.isfinite(z)
floor = ndimage.median_filter(np.where(ok, z, 0), size=15)
holes = ok & (z > floor + 0.5)          # deeper than surroundings (Z grows toward exterior)
lab, n = ndimage.label(holes); dell_pins = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    area = (lab[sl] == i).sum()
    if 5 < area < 400:
        cy, cx = ndimage.center_of_mass(lab == i); X, Y = cx / PX - MX, cy / PX - MY
        if Y < 40 and 40 < X < 320: dell_pins.append((round(X, 2), round(Y, 2), int(area)))
dell_pins.sort()
print('Dell rear pin-hole candidates (X, Y, area px):', dell_pins)
src = np.float32([px[k] for k in dell]); dst = np.float32([dell[k] for k in dell])
H, _ = cv2.findHomography(src, dst, 0)
def fwd(p): q = H @ np.array([p[0], p[1], 1.0]); return q[:2] / q[2]
res = {k: float(np.hypot(*(fwd(px[k]) - np.array(dell[k])))) for k in dell}
print('control-point residuals (mm):', {k: round(v, 2) for k, v in res.items()}, 'RMS', round(float(np.sqrt(np.mean(np.square(list(res.values()))))), 2))
# leave-one-out: how well does each screw get predicted from the other six?
loo = {}
for k in dell:
    ks = [j for j in dell if j != k]
    Hk, _ = cv2.findHomography(np.float32([px[j] for j in ks]), np.float32([dell[j] for j in ks]), 0)
    q = Hk @ np.array([*px[k], 1.0]); loo[k] = round(float(np.hypot(*(q[:2] / q[2] - np.array(dell[k])))), 2)
print('leave-one-out prediction error (mm):', loo)
chk = {k: [round(float(v), 2) for v in fwd(p)] for k, p in check_px.items()}
print('photo pin holes mapped to Dell frame:', chk)
# --- rectified image ---
img = cv2.imread('../photos/05-own-cover-interior.jpg')
S = np.array([[PX, 0, MX * PX], [0, PX, MY * PX], [0, 0, 1]])
W, Hh = int((355.32 + 2 * MX) * PX), int((226.2 + 2 * MY) * PX)
out = cv2.warpPerspective(img, S @ H, (W, Hh), flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255))
# overlay Dell outline (from the interior height map footprint), grid, screws
fp = ok.astype(np.uint8)[:Hh, :W]
cnts, _ = cv2.findContours(fp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(out, cnts, -1, (0, 255, 255), 1)
for mm in range(0, 360, 10):
    x = int((mm + MX) * PX); cv2.line(out, (x, 0), (x, 6 if mm % 50 else 14), (0, 0, 255), 1)
    if mm % 50 == 0: cv2.putText(out, str(mm), (x + 2, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
for mm in range(0, 230, 10):
    y = int((mm + MY) * PX); cv2.line(out, (0, y), (6 if mm % 50 else 14, y), (0, 0, 255), 1)
    if mm % 50 == 0: cv2.putText(out, str(mm), (16, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
for k, (X, Y) in dell.items():
    c = (int((X + MX) * PX), int((Y + MY) * PX)); cv2.circle(out, c, 10, (0, 0, 255), 2)
for X, Y, _ in dell_pins:
    cv2.circle(out, (int((X + MX) * PX), int((Y + MY) * PX)), 6, (255, 0, 255), 2)
cv2.putText(out, 'User photo 05 rectified to Dell 3D-guide frame (mm). Yellow = Dell outline, red = Dell screws, magenta = Dell pin holes.',
            (8, Hh - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)
cv2.imwrite('rect-05-interior-dellframe.png', out)
json.dump({'H_photo_to_dell_mm': H.tolist(), 'control_residual_mm': res, 'leave_one_out_mm': loo,
           'pin_holes_photo_mapped': chk, 'pin_holes_dell': dell_pins,
           'note': 'Planar homography; walls/clips at other heights carry parallax error. Front-left screw hidden in photo.'},
          open('rect-05-interior-dellframe.json', 'w'), indent=1)
print('saved rect-05-interior-dellframe.png', out.shape)
