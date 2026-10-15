"""Orthographic render of the Dell 3D-guide base cover STL, oriented like the user's photos
(hinge/rear edge at the top). 4 px/mm, grid every 10 mm, labels every 50 mm."""
import json, struct, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1] if len(sys.argv) > 1 else '.'
PX = 4.0
def load_stl(p):
    b = open(p, 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v'].astype(np.float64)
body = load_stl(f'{D}/dell3525-basecover-body.stl'); screws = load_stl(f'{D}/dell3525-basecover-screws.stl')
parts = json.load(open(f'{D}/dell3525-basecover-parts.json'))['parts']
X0, X1 = body[..., 0].min(), body[..., 0].max(); Y1 = body[..., 1].max()
W, H = int((X1 - X0) * PX) + 1, int(Y1 * PX) + 1

def render(tris_list, side):
    zb = np.full((H, W), -np.inf); img = np.zeros((H, W, 3))
    light = np.array([-0.4, -0.5, 0.77]); light /= np.linalg.norm(light)
    for tris, base in tris_list:
        for t in tris:
            if side == 'ext': c = (X1 - t[:, 0]) * PX; d = t[:, 2]
            else:             c = (t[:, 0] - X0) * PX; d = -t[:, 2]
            r = t[:, 1] * PX
            n = np.cross(t[1] - t[0], t[2] - t[0]); ln = np.linalg.norm(n)
            if ln == 0: continue
            n /= ln
            if side == 'int': n = n * np.array([1, 1, -1])
            shade = 0.35 + 0.65 * abs(n @ light)
            cmin, cmax = int(max(np.floor(c.min()), 0)), int(min(np.ceil(c.max()), W - 1))
            rmin, rmax = int(max(np.floor(r.min()), 0)), int(min(np.ceil(r.max()), H - 1))
            if cmax < cmin or rmax < rmin: continue
            cc, rr = np.meshgrid(np.arange(cmin, cmax + 1) + .5, np.arange(rmin, rmax + 1) + .5)
            den = (r[1] - r[2]) * (c[0] - c[2]) + (c[2] - c[1]) * (r[0] - r[2])
            if abs(den) < 1e-12: continue
            w0 = ((r[1] - r[2]) * (cc - c[2]) + (c[2] - c[1]) * (rr - r[2])) / den
            w1 = ((r[2] - r[0]) * (cc - c[2]) + (c[0] - c[2]) * (rr - r[2])) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            z = w0 * d[0] + w1 * d[1] + w2 * d[2]
            sub = zb[rmin:rmax + 1, cmin:cmax + 1]; m &= z > sub
            sub[m] = z[m]; img[rmin:rmax + 1, cmin:cmax + 1][m] = np.array(base) * shade
    bg = zb == -np.inf; img[bg] = 1.0
    return Image.fromarray((img * 255).clip(0, 255).astype(np.uint8))

try: font = ImageFont.truetype('arial.ttf', 22); small = ImageFont.truetype('arial.ttf', 14)
except OSError: font = small = ImageFont.load_default()
# photo label mapping (exterior view, hinge at top): see README in this folder
screw_parts = [p for p in parts if 'crew' in p['part']]
def label_for(p):
    x, y = p['center'][0], p['center'][1]
    row = 'top' if y < 60 else ('mid' if y < 170 else 'bot')
    ext_side = 'L' if x > 250 else ('R' if x < 100 else 'C')  # exterior view: X mirrored
    return {('top', 'L'): 'C2', ('top', 'C'): 'C3', ('top', 'R'): 'C1', ('mid', 'L'): 'C5', ('mid', 'R'): 'C4',
            ('bot', 'L'): 'C6', ('bot', 'C'): 'C7', ('bot', 'R'): 'C8'}[(row, ext_side)]
for side in ('ext', 'int'):
    im = render([(body, (0.55, 0.58, 0.62)), (screws, (0.85, 0.35, 0.2))], side)
    dr = ImageDraw.Draw(im)
    for mm in range(0, int(X1 - X0) + 1, 10):
        dr.line([(mm * PX, 0), (mm * PX, H)], fill=(200, 180, 0) if mm % 50 else (220, 40, 40), width=1)
        if mm % 50 == 0: dr.text((mm * PX + 3, 3), str(mm), fill=(220, 40, 40), font=small)
    for mm in range(0, int(Y1) + 1, 10):
        dr.line([(0, mm * PX), (W, mm * PX)], fill=(200, 180, 0) if mm % 50 else (220, 40, 40), width=1)
        if mm % 50 == 0: dr.text((3, mm * PX + 3), str(mm), fill=(220, 40, 40), font=small)
    for p in screw_parts:
        x, y = p['center'][:2]
        c = (X1 - x) * PX if side == 'ext' else (x - X0) * PX; r = y * PX
        dr.ellipse([c - 14, r - 14, c + 14, r + 14], outline=(230, 0, 0), width=3)
        label = label_for(p)
        # Long rear-centre screw mesh is NOT captive. Dell specifies two
        # captive screws at the rear corners; all six others are removed.
        kind = 'captive' if label in ('C1', 'C2') else 'remove'
        dr.text((c + 16, r - 12), f"{label} {kind}", fill=(230, 0, 0), font=font)
    title = 'EXTERIOR (feet side) - hinge edge at top' if side == 'ext' else 'INTERIOR (cover off) - hinge edge at top'
    dr.text((W // 2 - 260, H - 30), f'Dell 3D guide model  |  {title}  |  4 px/mm', fill=(0, 0, 160), font=small)
    im.save(f'{D}/render-{side}.png')
    print('saved', f'render-{side}.png', im.size)
