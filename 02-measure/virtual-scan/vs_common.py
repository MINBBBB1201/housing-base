"""Shared helpers for the photo 'virtual scan': Dell base-cover mesh (scene frame, mm) + ray casting."""
import struct, numpy as np
DELL = '../../00-input/dell-official-3d'
def load_stl(p):
    b = open(p, 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v'].astype(np.float64)
BODY = load_stl(f'{DELL}/parts/Inspiron_3525_Basecover-1_002.stl')   # scene frame: interior faces -Z (palmrest side)
def zstack(x, y, tris=BODY):
    """All surface Z values of the mesh on the vertical line through (x, y)."""
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(den) > 1e-12; den = np.where(ok, den, 1)
    w0 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / den
    w1 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / den
    m = ok & (w0 >= 0) & (w1 >= 0) & (w0 + w1 <= 1)
    return np.sort((w0 * a[:, 2] + w1 * b[:, 2] + (1 - w0 - w1) * c[:, 2])[m])
def ray_mesh(o, d, tris=BODY):
    """Möller–Trumbore: first hit distance and point of ray o + t d with the mesh (None if miss)."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    e1, e2 = v1 - v0, v2 - v0; p = np.cross(d, e2); det = e1 @ np.zeros(3) if False else np.einsum('ij,ij->i', e1, p)
    ok = np.abs(det) > 1e-12; inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
    s = o - v0; u = np.einsum('ij,ij->i', s, p) * inv
    q = np.cross(s, e1); v = (q @ d) * inv; t = np.einsum('ij,ij->i', e2, q) * inv
    m = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
    if not m.any(): return None
    k = np.argmin(np.where(m, t, np.inf)); return o + t[k] * d
