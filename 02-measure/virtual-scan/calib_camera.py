"""Pinhole camera pose + focal from Dell-model 3D reference points (scene frame, mm) and pixel picks.
Principal point = image centre, square pixels, no distortion (phone JPEG). Focal found by 1-D search + PnP."""
import json, sys, numpy as np, cv2
def calibrate(obj, img, size, f_range=(600, 3000)):
    obj = np.float64(obj); img = np.float64(img); cx, cy = size[0] / 2, size[1] / 2
    best = None
    for f in np.arange(*f_range, 5):
        K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]])
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok: continue
        pr, _ = cv2.projectPoints(obj, rv, tv, K, None); e = np.sqrt(np.mean(np.sum((pr[:, 0] - img) ** 2, 1)))
        if best is None or e < best[0]: best = (e, f, rv, tv, K)
    e, f, rv, tv, K = best
    ok, rv, tv = cv2.solvePnP(obj, img, K, None, rv, tv, useExtrinsicGuess=True, flags=cv2.SOLVEPNP_ITERATIVE)
    pr, _ = cv2.projectPoints(obj, rv, tv, K, None); per = np.sqrt(np.sum((pr[:, 0] - img) ** 2, 1))
    R, _ = cv2.Rodrigues(rv); C = (-R.T @ tv).ravel()
    return {'f': float(f), 'K': K.tolist(), 'rvec': rv.ravel().tolist(), 'tvec': tv.ravel().tolist(), 'cam_center_mm': C.tolist(),
            'rms_px': float(np.sqrt(np.mean(per ** 2))), 'per_point_px': per.round(2).tolist()}
def pixel_ray(cal, u, v):
    """World-frame origin and unit direction of the viewing ray through pixel (u, v)."""
    K = np.array(cal['K']); R, _ = cv2.Rodrigues(np.array(cal['rvec'])); t = np.array(cal['tvec'])
    d = R.T @ (np.linalg.inv(K) @ np.array([u, v, 1.0])); o = -R.T @ t
    return o, d / np.linalg.norm(d)
if __name__ == '__main__':
    refs = json.load(open('p05-refs.json'))
    pts = {  # name: (X, Y, Z scene frame), pixel in photo 05
        'pin-RL': ((57.55, 16.08, 7.92), refs['pin-RL']['refined']), 'pin-RR': ((297.55, 16.08, 7.93), refs['pin-RR']['refined']),
        'pin-FL': ((59.5, 197.5, 8.26), refs['pin-FL']['refined']), 'pin-FR': ((295.75, 197.5, 8.26), refs['pin-FR']['refined']),
        'mid-L': ((9.01, 119.63, 8.00), (67.5, 554.0)), 'mid-R': ((346.31, 119.63, 7.24), (1377.5, 564.0)),
        'front-R': ((346.31, 217.14, 4.53), (1371.0, 935.0)), 'front-C': ((177.66, 217.98, 3.79), (730.0, 942.5))}
    cal = calibrate([p[0] for p in pts.values()], [p[1] for p in pts.values()], (1440, 1080))
    cal['points'] = {k: {'xyz': v[0], 'px': v[1]} for k, v in pts.items()}
    # leave-one-out: predict each point's pixel from the other seven
    names = list(pts); loo = {}
    for k in names:
        rest = [n for n in names if n != k]
        c = calibrate([pts[n][0] for n in rest], [pts[n][1] for n in rest], (1440, 1080))
        pr, _ = cv2.projectPoints(np.float64([pts[k][0]]), np.array(c['rvec']), np.array(c['tvec']), np.array(c['K']), None)
        loo[k] = round(float(np.hypot(*(pr[0, 0] - np.array(pts[k][1])))), 1)
    cal['leave_one_out_px'] = loo
    json.dump(cal, open('cam05.json', 'w'), indent=1)
    print('f =', cal['f'], 'px | RMS', round(cal['rms_px'], 2), 'px | per point', cal['per_point_px'])
    print('camera centre (mm, scene frame):', np.round(cal['cam_center_mm'], 1))
    print('leave-one-out px:', loo)
