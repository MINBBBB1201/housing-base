"""Calibrate photo 08 (oblique) from SIFT matches to photo 05. Matched 05 pixels -> Dell floor XY via the
05 homography, Z from the Dell mesh inner surface -> 3D points -> PnP + focal search for camera 08."""
import json, numpy as np, cv2
from vs_common import zstack
from calib_camera import calibrate
P = '../../00-input/photos/'
a = cv2.imread(P + '05-own-cover-interior.jpg', 0); b = cv2.imread(P + '08-interior-perspective.jpg', 0)
H05 = np.array(json.load(open('../../00-input/dell-official-3d/rect-05-interior-dellframe.json'))['H_photo_to_dell_mm'])
sift = cv2.SIFT_create(8000)
ka, da = sift.detectAndCompute(a, None); kb, db = sift.detectAndCompute(b, None)
m = cv2.BFMatcher().knnMatch(da, db, k=2); good = [x for x, y in m if x.distance < 0.75 * y.distance]
pa = np.float32([ka[g.queryIdx].pt for g in good]); pb = np.float32([kb[g.trainIdx].pt for g in good])
Hab, inl = cv2.findHomography(pa, pb, cv2.RANSAC, 6.0); inl = inl.ravel().astype(bool)
print('SIFT matches', len(good), 'floor-homography inliers', int(inl.sum()))
pa, pb = pa[inl], pb[inl]
xy = cv2.perspectiveTransform(pa[None], H05)[0]
obj, img = [], []
for (x, y), p in zip(xy, pb):
    if not (8 < x < 347 and 20 < y < 205): continue
    z = zstack(x, y)
    if len(z): obj.append((x, y, z[0])); img.append(p)
obj = np.array(obj); img = np.array(img)
print('3D floor correspondences', len(obj), 'Z range', obj[:, 2].min().round(2), obj[:, 2].max().round(2))
cal = calibrate(obj, img, (1440, 1080), (600, 4000))
# robust refit: drop worst 10 %
per = np.array(cal['per_point_px']); keep = per < np.percentile(per, 90)
cal = calibrate(obj[keep], img[keep], (1440, 1080), (600, 4000)); cal.pop('per_point_px')
cal['n_points'] = int(keep.sum())
print('photo 08: f', cal['f'], 'rms px', round(cal['rms_px'], 2), 'camera centre', np.round(cal['cam_center_mm'], 1))
for f in (cal['f'] * 0.8, cal['f'] * 1.25):
    c2 = calibrate(obj[keep], img[keep], (1440, 1080), (f, f + 5)); print(f'  f={f:.0f}: rms {c2["rms_px"]:.2f}')
json.dump(cal, open('cam08.json', 'w'), indent=1)
