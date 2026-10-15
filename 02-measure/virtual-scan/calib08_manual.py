"""Calibrate photo 08 from hand-picked floor landmarks (grille, labels) seen in both photos.
Photo-05 side: rectified-mm pick -> raw 05 pixel (H^-1) -> ray from camera 05 -> hit on Dell mesh = 3D point."""
import json, numpy as np, cv2
from vs_common import ray_mesh
from calib_camera import calibrate, pixel_ray
H05 = np.array(json.load(open('../../00-input/dell-official-3d/rect-05-interior-dellframe.json'))['H_photo_to_dell_mm'])
cam05 = json.load(open('cam05.json'))
# (rectified-05 X, Y mm)  <->  photo-08 pixel
pairs = {
 'grille-hiX-loY': ((276.5, 24.2), (203.3, 237.7)), 'grille-hiX-hiY': ((275.8, 54.4), (333.3, 235.7)),
 'grille-loX-hiY': ((220.2, 54.0), (321.7, 333.3)), 'grille-loX-loY': ((219.8, 24.2), (166.7, 341.7)),
 'ce-hiX-hiY': ((313.9, 180.5), (796.7, 170.7)), 'ce-loX-hiY': ((284.6, 182.6), (825.0, 207.3)), 'ce-loX-loY': ((281.8, 142.75), (685.0, 216.7)),
 'qr-hiX-loY': ((287.5, 186.5), (836.7, 204.0)), 'qr-hiX-hiY': ((287.5, 199.7), (888.3, 200.7)),
 'qr-loX-hiY': ((262.3, 199.7), (909.3, 236.0)), 'qr-loX-loY': ((262.3, 186.5), (860.0, 239.3)),
 'ht-hiX-loY': ((257.9, 194.5), (896.0, 245.0)), 'ht-hiX-hiY': ((257.9, 200.7), (920.0, 243.3)),
 'ht-loX-hiY': ((237.9, 200.7), (945.0, 275.0)), 'ht-loX-loY': ((237.9, 194.5), (920.0, 276.7)),
 'ap-hiX-loY': ((234.2, 187.3), (900.0, 286.0)), 'ap-hiX-hiY': ((234.2, 198.25), (935.0, 281.7)),
 'ap-loX-hiY': ((199.6, 198.25), (993.3, 343.3)), 'ap-loX-loY': ((199.6, 187.3), (950.0, 351.7)),
}
Hi = np.linalg.inv(H05); obj, img, names = [], [], []
for k, ((x, y), p8) in pairs.items():
    q = Hi @ np.array([x, y, 1.0]); u, v = q[:2] / q[2]
    o, d = pixel_ray(cam05, u, v); hit = ray_mesh(o, d)
    if hit is None: print('miss', k); continue
    obj.append(hit); img.append(p8); names.append(k)
obj = np.array(obj); img = np.array(img)
cal = calibrate(obj, img, (1440, 1080), (500, 4000))
print('photo 08: f', cal['f'], '| rms px', round(cal['rms_px'], 2), '| camera centre', np.round(cal['cam_center_mm'], 1))
for n, e in zip(names, cal['per_point_px']): print(f'  {n:16s} {e:5.1f} px')
for f in (cal['f'] * 0.85, cal['f'] * 1.18):
    c2 = calibrate(obj, img, (1440, 1080), (f, f + 5)); print(f'  f={f:.0f}: rms {c2["rms_px"]:.2f}')
cal['points'] = {n: {'xyz': o.tolist(), 'px': list(p)} for n, o, p in zip(names, obj, img)}
json.dump(cal, open('cam08.json', 'w'), indent=1)
