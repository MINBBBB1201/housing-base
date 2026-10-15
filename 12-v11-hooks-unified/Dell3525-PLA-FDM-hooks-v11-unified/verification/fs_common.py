"""Final fit simulation helpers: exact column-crossing point-in-solid tests and Dell->CAD frame mapping."""
import struct, numpy as np
from pathlib import Path
HB = Path(__file__).resolve().parents[2]                     # housing-base
DELL = HB / '00-input/dell-official-3d/parts'
CAD = HB / '04-cad'
# CAD constants (params.scad): zp(y) = a - b*y is the OEM exterior plane on top of the C03 wedge
W, D = 355.32, 226.20
h_rear, h_front, wedge_d = 20.0, 4.0, 215.0
wy0 = (D - wedge_d) / 2
b = (h_rear - h_front) / wedge_d
a = h_rear + b * wy0
def zp(y): return a - b * y

def load_stl(p):
    raw = open(p, 'rb').read()
    if raw[:5] == b'solid' and b'facet' in raw[:400]:
        import re
        v = np.array(re.findall(rb'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)', raw), dtype=float)
        return v.reshape(-1, 3, 3)
    n = struct.unpack('<I', raw[80:84])[0]
    return np.frombuffer(raw[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v'].astype(float)

def dell_to_cad(P, zref):
    """Dell scene frame (base-cover exterior faces +Z) -> CAD frame (desk up, laptop on the wedge)."""
    Q = P.copy()
    Q[..., 2] = zp(P[..., 1]) + (zref - P[..., 2])
    return Q

class ColumnSolid:
    """Exact crossings of a closed mesh on a regular XY grid of column centres; point-in-solid by parity."""
    def __init__(self, tris, x0=-4.0, y0=-7.0, x1=360.0, y1=234.0, h=0.5):
        self.x0, self.y0, self.h = x0 + 0.0137, y0 + 0.0173, h        # tiny offsets avoid edge-on degeneracies
        self.nx, self.ny = int((x1 - x0) / h) + 1, int((y1 - y0) / h) + 1
        cells, zs = [], []
        for t in tris:
            xs, ys = t[:, 0], t[:, 1]
            i0 = int(np.ceil((xs.min() - self.x0) / h)); i1 = int(np.floor((xs.max() - self.x0) / h))
            j0 = int(np.ceil((ys.min() - self.y0) / h)); j1 = int(np.floor((ys.max() - self.y0) / h))
            if i1 < i0 or j1 < j0: continue
            I, J = np.meshgrid(np.arange(max(i0, 0), min(i1, self.nx - 1) + 1), np.arange(max(j0, 0), min(j1, self.ny - 1) + 1), indexing='ij')
            cx, cy = self.x0 + I * h, self.y0 + J * h
            (ax, ay, az), (bx, by, bz), (qx, qy, qz) = t
            den = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
            if abs(den) < 1e-12: continue
            w0 = ((by - qy) * (cx - qx) + (qx - bx) * (cy - qy)) / den
            w1 = ((qy - ay) * (cx - qx) + (ax - qx) * (cy - qy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not m.any(): continue
            cells.append((I[m] * self.ny + J[m]).ravel()); zs.append((w0 * az + w1 * bz + w2 * qz)[m].ravel())
        c = np.concatenate(cells); z = np.concatenate(zs)
        o = np.lexsort((z, c)); self.c, self.z = c[o], z[o]
        self.start = np.searchsorted(self.c, np.arange(self.nx * self.ny))
        self.count = np.diff(np.append(self.start, len(self.c)))
    def cell_of(self, x, y):
        i = np.rint((x - self.x0) / self.h).astype(int); j = np.rint((y - self.y0) / self.h).astype(int)
        ok = (i >= 0) & (i < self.nx) & (j >= 0) & (j < self.ny)
        return np.where(ok, i * self.ny + j, -1)
    def inside(self, P):
        """P: (N,3). Returns inside mask, and 'depth' = distance from the point up to the solid's top in that column."""
        cell = self.cell_of(P[:, 0], P[:, 1]); ok = cell >= 0
        res = np.zeros(len(P), bool); depth = np.zeros(len(P))
        if not ok.any(): return res, depth
        cc = cell[ok]; zz = P[ok, 2]
        s = self.start[cc]; n = self.count[cc]
        # number of crossings below z within the cell: binary search inside each cell's slice (vectorised via global keys)
        key = self.c.astype(np.float64) * 1000.0 + self.z
        below = np.searchsorted(key, cc * 1000.0 + zz) - s
        ins = (below % 2 == 1) & (n % 2 == 0)
        # depth to the top of the current solid interval
        top_idx = np.clip(s + below, 0, len(self.z) - 1)
        d = np.where(ins, self.z[top_idx] - zz, 0.0)
        res[np.where(ok)[0]] = ins; depth[np.where(ok)[0]] = d
        return res, depth
    def column_top(self):
        """Top-most crossing per column (nan if empty) as an (nx, ny) array."""
        top = np.full(self.nx * self.ny, np.nan)
        has = self.count > 0
        top[has] = self.z[self.start[has] + self.count[has] - 1]
        return top.reshape(self.nx, self.ny)

def sample_surface(tris, spacing=0.5, rng=np.random.default_rng(3525)):
    """Area-weighted random surface samples, about one per spacing^2."""
    e1 = tris[:, 1] - tris[:, 0]; e2 = tris[:, 2] - tris[:, 0]
    A = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
    n = np.maximum(1, np.ceil(A / spacing ** 2).astype(int))
    idx = np.repeat(np.arange(len(tris)), n)
    u = rng.random(len(idx)); v = rng.random(len(idx)); f = u + v > 1; u[f] = 1 - u[f]; v[f] = 1 - v[f]
    return tris[idx, 0] + u[:, None] * e1[idx] + v[:, None] * e2[idx]
