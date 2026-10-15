"""Z-buffer height maps (4 px/mm) of any part STL in the shared base-cover frame.
Usage: python depthmap.py <stl> <view:+z|-z> <out.png> [title]"""
import struct, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
PX, MX, MY = 4.0, 6, 8
def load(p):
    b = open(p, 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v'].astype(float)
def zbuffer(tris, view, W, H):
    zb = np.full((H, W), -np.inf)
    s = 1 if view == '+z' else -1
    for t in tris:
        c = (t[:, 0] + MX) * PX; r = (t[:, 1] + MY) * PX; d = s * t[:, 2]
        cmin, cmax = int(max(np.floor(c.min()), 0)), int(min(np.ceil(c.max()), W - 1))
        rmin, rmax = int(max(np.floor(r.min()), 0)), int(min(np.ceil(r.max()), H - 1))
        if cmax < cmin or rmax < rmin: continue
        den = (r[1] - r[2]) * (c[0] - c[2]) + (c[2] - c[1]) * (r[0] - r[2])
        if abs(den) < 1e-12: continue
        cc, rr = np.meshgrid(np.arange(cmin, cmax + 1) + .5, np.arange(rmin, rmax + 1) + .5)
        w0 = ((r[1] - r[2]) * (cc - c[2]) + (c[2] - c[1]) * (rr - r[2])) / den
        w1 = ((r[2] - r[0]) * (cc - c[2]) + (c[0] - c[2]) * (rr - r[2])) / den
        w2 = 1 - w0 - w1; m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        z = w0 * d[0] + w1 * d[1] + w2 * d[2]; sub = zb[rmin:rmax + 1, cmin:cmax + 1]; m &= z > sub; sub[m] = z[m]
    return s * zb  # back to real Z (nan-free: -inf/+inf where empty)
if __name__ == '__main__':
    stl, view, out = sys.argv[1:4]; title = sys.argv[4] if len(sys.argv) > 4 else stl
    t = load(stl); W, H = int((362 + 2 * MX) * PX), int((232 + 2 * MY) * PX)
    z = zbuffer(t, view, W, H); np.save(out.replace('.png', '.npy'), z)
    ok = np.isfinite(z); lo, hi = np.percentile(z[ok], [1, 99])
    v = np.clip((z - lo) / (hi - lo + 1e-9), 0, 1)
    # turbo-ish colormap
    import colorsys
    rgb = np.zeros(z.shape + (3,)); hue = (1 - v) * 0.7
    for i, h in enumerate(np.linspace(0, 0.7, 64)):
        sel = ok & (np.abs(hue - h) <= 0.7 / 126 + 1e-9); rgb[sel] = colorsys.hsv_to_rgb(h, 0.85, 0.95)
    # hillshade for relief
    gy, gx = np.gradient(np.where(ok, z, np.nanmedian(z[ok])))
    shade = np.clip(0.75 + 0.9 * (gx - gy), 0.35, 1.2)[..., None]
    img = np.where(ok[..., None], np.clip(rgb * shade, 0, 1), 1.0)
    im = Image.fromarray((img * 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('arial.ttf', 15)
    except OSError: f = ImageFont.load_default()
    for mm in range(0, 361, 10):
        x = (mm + MX) * PX; dr.line([(x, 0), (x, 6 if mm % 50 else 14)], fill=(0, 0, 0))
        if mm % 50 == 0: dr.text((x + 2, 12), str(mm), fill=(0, 0, 0), font=f)
    for mm in range(0, 231, 10):
        y = (mm + MY) * PX; dr.line([(0, y), (6 if mm % 50 else 14, y)], fill=(0, 0, 0))
        if mm % 50 == 0: dr.text((16, y - 7), str(mm), fill=(0, 0, 0), font=f)
    dr.text((10, H - 22), f'{title} | view {view} | color: Z {hi:.1f} (red) .. {lo:.1f} (blue) mm | X right, Y down (0 = hinge)', fill=(0, 0, 0), font=f)
    im.save(out); print(out, im.size, 'Z', round(lo, 2), round(hi, 2))
