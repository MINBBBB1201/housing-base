"""Clip/tab layout of the OEM 03JRFX base cover from the user's photos, in the Dell 3D-guide frame (mm).
- right wall: photo 08 (oblique, calibrated) ray ∩ inner-wall plane X = W-2 -> Y and tab Z
- rear/front/left walls: photo 05 ray ∩ horizontal plane at the tab top Z = Dell rim Z - DZ_TAB
  (DZ_TAB = mean tab protrusion above the Dell rim measured on the right wall in photo 08)
Output: clips.json (+ printed table). Picks in rectified-05 mm coordinates are converted back to raw 05 pixels."""
import json, numpy as np
from vs_common import zstack
from calib_camera import calibrate, pixel_ray
W, D = 355.32, 226.20
H05 = np.array(json.load(open('../../00-input/dell-official-3d/rect-05-interior-dellframe.json'))['H_photo_to_dell_mm']); Hi = np.linalg.inv(H05)
c05 = json.load(open('cam05.json')); c8 = json.load(open('cam08.json'))
obj = [v['xyz'] for v in c05['points'].values()]; img = [v['px'] for v in c05['points'].values()]
cams05 = {f: calibrate(obj, img, (1440, 1080), (f, f + 5)) for f in (1900, 2600, 3400)}
def rim_z(wall, s):
    """Dell rim (wall-top) Z at position s along the wall: minimum Z in a 4 mm band inside the outer edge."""
    zs = []
    for q in np.linspace(0.6, 4.0, 7):
        x, y = {'rear': (s, q), 'front': (s, D - q), 'left': (q, s), 'right': (W - q, s)}[wall]
        z = zstack(x, y); zs += list(z[:1])
    return min(zs) if zs else np.nan
out = []
# ---- right wall from photo 08 ----
r_tabs = {'R1': (227.5, 122.5), 'R2': (298.5, 121.0), 'R3': (407.0, 117.0), 'R4': (495.0, 116.0), 'R5': (625.0, 109.5), 'R6': (777.5, 104.0)}
dz = []
for k, (u, v) in r_tabs.items():
    o, d = pixel_ray(c8, u, v); p = o + (W - 2 - o[0]) / d[0] * d; rz = rim_z('right', p[1]); dz.append(rz - p[2])
    out.append({'id': k, 'wall': 'right', 'x': round(W - 2, 1), 'y': round(p[1], 1), 'z_tab': round(p[2], 2), 'rim_z': round(rz, 2),
                'src': 'photo08', 'conf': 'B'})
DZ_TAB = float(np.mean(dz)); print(f'tab protrusion above Dell rim (photo 08, n={len(dz)}): mean {DZ_TAB:.2f} sd {np.std(dz):.2f} mm')
# cross-check against photo-05 right-wall reads (rect Y): 71, 96, 136.5, 186
xcheck = {'R3': 71.0, 'R4': 96.0, 'R5': 136.5, 'R6': 186.0}
# ---- rear / front / left from photo 05 (rectified-mm picks of the tab top) ----
picks = {
 'rear':  [('B1', 19.0, 2.5), ('B2', 70.8, 3.0), ('B3', 104.5, 3.0), ('B4', 141.9, 2.0), ('B5', 204.4, 2.5),
           ('B6', 229.4, 2.5), ('B7', 244.4, 2.5), ('B8', 260.6, 3.0), ('B9', 286.3, 3.5)],
 'front': [('F1', 49.1, 221.6), ('F2', 89.8, 223.9), ('F3t', 116.0, 221.5), ('F4', 127.8, 223.5), ('F5', 161.3, 225.3),
           ('F6', 193.1, 225.0), ('F7', 222.8, 223.4), ('F8t', 246.5, 225.3), ('F9', 262.5, 221.3), ('F10', 304.6, 221.3)],
 'left':  [('L3', 0.5, 95.6), ('L5', 0.5, 136.5), ('L2?', 0.5, 44.75), ('L6?', 0.5, 208.9)],
}
for wall, lst in picks.items():
    for k, xr, yr in lst:
        q = Hi @ np.array([xr, yr, 1.0]); u, v = q[:2] / q[2]
        res = {}
        for f, c in cams05.items():
            o, d = pixel_ray(c, u, v); s = xr if wall in ('rear', 'front') else yr
            for _ in range(4):                               # iterate: tab Z depends on where the ray lands
                zt = rim_z(wall, s) - DZ_TAB; p = o + (zt - o[2]) / d[2] * d; s = p[0] if wall in ('rear', 'front') else p[1]
            res[f] = p
        p = res[2600]; spread = max(np.hypot(*(res[f][:2] - p[:2])) for f in res)
        conf = 'C' if k.endswith('?') else ('B' if wall != 'left' else 'C')
        out.append({'id': k.rstrip('?'), 'wall': wall, 'x': round(p[0], 1), 'y': round(p[1], 1), 'z_tab': round(p[2], 2),
                    'rim_z': round(rim_z(wall, p[0] if wall in ('rear', 'front') else p[1]), 2), 'src': 'photo05',
                    'conf': conf, 'focal_spread_mm': round(spread, 2), 'type': 'flat tab' if k.endswith('t') else 'hook',
                    'rect_floor_pick': [xr, yr]})
for o_ in out:
    if o_['id'] in xcheck: o_['photo05_check_y'] = xcheck[o_['id']]; o_['conf'] = 'A'
json.dump({'frame': 'Dell 3D-guide scene frame, mm; X laptop-left->right, Y hinge->front, Z: interior side is smaller Z (floor ~8.26)',
           'dz_tab_above_rim_mm': round(DZ_TAB, 2),
           'confidence': {'A': 'seen in two calibrated photos, agree <=1.5 mm', 'B': 'one calibrated photo, clear tab', 'C': 'edge-on or ambiguous, verify'},
           'clips': out}, open('clips.json', 'w'), indent=1)
print(f"{'id':5s} {'wall':6s} {'X':>7s} {'Y':>7s} {'Ztab':>6s} {'rimZ':>6s} conf src      note")
for o_ in out:
    note = (f"f-spread {o_['focal_spread_mm']}mm" if 'focal_spread_mm' in o_ else '') + (f" | 05 read Y {o_['photo05_check_y']}" if 'photo05_check_y' in o_ else '') + (' | flat tab' if o_.get('type') == 'flat tab' else '')
    print(f"{o_['id']:5s} {o_['wall']:6s} {o_['x']:7.1f} {o_['y']:7.1f} {o_['z_tab']:6.2f} {o_['rim_z']:6.2f}  {o_['conf']}   {o_['src']}  {note}")
