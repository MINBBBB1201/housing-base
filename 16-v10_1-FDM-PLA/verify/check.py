"""v10.1-FDM verification: display-chin sweep, Dell part interference (vs v10.1 baseline), sections, mesh.

Frames: Dell guide scene (x same as CAD design frame, y hinge->front, z_dell points DOWN, OEM flat exterior z_dell=10.06)
        -> CAD design frame z = zp(y) + (10.06 - z_dell).  Design-frame STLs (print_frame=false) only.
usage:  python check.py <new_body.stl> <baseline_v10_1_body.stl>
"""
import sys, json, numpy as np, trimesh
from pathlib import Path
HERE = Path(__file__).resolve().parent
HB = HERE.parents[1]
sys.path.insert(0, str(HB / '15-v11-flat-internal/Dell3525-PLA-FDM-hooks-v11/verification'))
from fs_common import load_stl, sample_surface, ColumnSolid as _CS    # generic helpers (frame constants unused)

class ColumnSolid(_CS):
    """Same exact column test, with the per-call search key cached (low-memory machine)."""
    def inside(self, P):
        if not hasattr(self, '_key'): self._key = self.c.astype(np.float64) * 1000.0 + self.z
        cell = self.cell_of(P[:, 0], P[:, 1]); ok = np.where(cell >= 0)[0]
        res = np.zeros(len(P), bool); depth = np.zeros(len(P))
        if not len(ok): return res, depth
        cc = cell[ok]; zz = P[ok, 2]; s = self.start[cc]; n = self.count[cc]
        below = np.searchsorted(self._key, cc * 1000.0 + zz) - s
        ins = (below % 2 == 1) & (n % 2 == 0)
        top = self.z[np.clip(s + below, 0, len(self.z) - 1)]
        res[ok] = ins; depth[ok] = np.where(ins, top - zz, 0.0)
        return res, depth
PARTS = HB / '00-input/dell-official-3d/parts'
W, D, ZREF = 355.32, 226.20, 10.06
HINGE_YZ = (4.87, 4.66)            # Dell frame; fitted to both hinge barrels (see chin_sweep in report)

def frame(wy0, wedge_d, h_rear=20.0, h_front=4.0):
    b = (h_rear - h_front) / wedge_d; a = h_rear + b * wy0
    return lambda y: a - b * y
ZP_NEW = frame(16.6, D - 5.6 - 16.6)
ZP_OLD = frame(5.6, 215.0)
def to_cad(P, zp):
    Q = P.copy(); Q[..., 2] = zp(P[..., 1]) + (ZREF - P[..., 2]); return Q

def display_exterior(spacing=0.3):
    A0 = load_stl(PARTS / 'Ins_15_3525_Display_Assembly_GP.stl')
    A3 = load_stl(PARTS / 'Ins_15_3525_Display_Assembly_GP_(3).stl')
    T = A0[np.abs(A3 - A0).max(axis=(1, 2)) < 0.01]          # parts that stay put in the guide = lid/bezel
    T = T[T[:, :, 1].min(1) < 16]
    q = sample_surface(T, spacing, rng=np.random.default_rng(1)); q = q[q[:, 1] < 16]
    return q[(q[:, 1] < -0.3) | (q[:, 2] < -2.3)]             # outside the closed base envelope only

def sweep(q, angles):
    yc, zc = HINGE_YZ
    for th in angles:
        t = np.radians(th); dy = q[:, 1] - yc; dz = q[:, 2] - zc
        r = q.copy(); r[:, 1] = yc + dy * np.cos(t) + dz * np.sin(t); r[:, 2] = zc - dy * np.sin(t) + dz * np.cos(t)
        yield th, r

def chin_check(body_tris, zp, label):
    cs = ColumnSolid(body_tris, x0=-4, y0=-6, x1=360, y1=40, h=0.2)
    q = display_exterior()
    hits = {}; n_tot = 0; worst = None; clear_rows = []
    for th, r in sweep(q, np.arange(0, 135.01, 0.5)):
        c = to_cad(r, zp); del r; m = (c[:, 1] > -6) & (c[:, 1] < 40)
        c = c[m]
        ins, dep = cs.inside(c)
        if ins.any():
            hits[float(th)] = int(ins.sum()); n_tot += int(ins.sum())
            k = np.argmax(dep);
            if worst is None or dep[k] > worst[0]: worst = (float(dep[k]), float(th), c[k].round(2).tolist())
    return {'label': label, 'angles_with_hits': len(hits), 'hit_samples': n_tot, 'worst_depth_mm_angle_pt': worst,
            'first_hit_angles': sorted(hits)[:5], 'last_hit_angles': sorted(hits)[-5:]}

def chin_clearance(body, zp, xs=(80, 150, 200, 240)):
    """Vertical gap between the swept chin (lowest-envelope side) and the body underside, per y, at given x columns."""
    q = display_exterior()
    out = {}
    for x in xs:
        qq = q[np.abs(q[:, 0] - x) < 1.0]
        env = {}
        for th, r in sweep(qq, np.arange(0, 135.01, 0.5)):
            c = to_cad(r, zp)
            for y, z in zip(np.round(c[:, 1] * 2) / 2, c[:, 2]):
                if 0 <= y <= 20: env[y] = max(env.get(y, -99), z)       # highest swept chin point per y
        rows = []
        for y in sorted(env):
            o = np.array([[x, y, 80.0]]); d = np.array([[0, 0, -1.0]])
            loc, _, _ = body.ray.intersects_location(o, d)
            if len(loc):
                zs = np.sort(loc[:, 2]); below = zs[zs <= env[y] + 30]
                # body underside above the chin = lowest body surface that is above env
                above = zs[zs > env[y]]
                gap = float(above.min() - env[y]) if len(above) else None
                inside = int((zs > env[y]).sum()) % 2 == 1           # chin point inside body?
                rows.append((float(y), round(gap, 2) if gap is not None else None, inside))
        out[x] = rows
    return out

def part_interference(body_tris, zp, spacing=0.4):
    cs = ColumnSolid(body_tris, x0=-4, y0=-6, x1=360, y1=234, h=0.25)
    res = {}
    for f in sorted(PARTS.glob('*.stl')):
        n = f.stem
        if any(k in n for k in ['Base_Cover', 'Basecover', '_(', 'Display_Assembly']): continue
        P = to_cad(sample_surface(load_stl(f), spacing, rng=np.random.default_rng(7)), zp)
        ins, dep = cs.inside(P)
        if ins.any():
            res[n] = {'n': int(ins.sum()), 'max_depth': round(float(dep[ins].max()), 2),
                      'bbox': [P[ins].min(0).round(1).tolist(), P[ins].max(0).round(1).tolist()]}
    return res

def mesh_report(p):
    m = trimesh.load_mesh(p)
    return {'file': Path(p).name, 'watertight': bool(m.is_watertight), 'winding': bool(m.is_winding_consistent),
            'bodies': len(m.split(only_watertight=False)), 'faces': len(m.faces), 'volume_cm3': round(m.volume / 1000, 1),
            'bounds': m.bounds.round(2).tolist()}

def sections(body_new, body_old, png):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    q = display_exterior(0.25)
    xs = [71, 150, 200, 45]
    fig, axs = plt.subplots(len(xs), 1, figsize=(15, 3.6 * len(xs)))
    for ax, x in zip(axs, xs):
        for mesh, col, lab, zp in [(body_old, '#bbbbbb', 'v10.1 (MJF)', ZP_OLD), (body_new, '#1f5fbf', 'v10.1-FDM', ZP_NEW)]:
            sec = mesh.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
            if sec is None: continue
            for e in sec.discrete:   # draw both relative to the same laptop (new frame): shift old by zp_new - zp_old
                ax.plot(e[:, 1], e[:, 2] + ZP_NEW(e[:, 1]) - zp(e[:, 1]), color=col, lw=1.4 if col != '#bbbbbb' else 1.0)
            ax.plot([], [], color=col, label=lab)
        qq = q[np.abs(q[:, 0] - x) < 0.6]
        pts = np.vstack([to_cad(r, ZP_NEW) for _, r in sweep(qq, np.arange(0, 135.01, 3))])
        pts = pts[(pts[:, 1] > -12) & (pts[:, 1] < 45)]
        ax.scatter(pts[:, 1], pts[:, 2], s=0.3, c='#e8590c', alpha=0.25)
        ax.plot([], [], color='#e8590c', label='display chin sweep 0-135° (new frame)')
        ax.set_xlim(-12, 45); ax.set_ylim(-1, 30); ax.set_aspect('equal'); ax.grid(alpha=.3)
        ax.set_title(f'section x = {x} mm (design frame, Y from hinge edge)'); ax.set_xlabel('Y mm'); ax.set_ylabel('Z mm (desk = 0)')
        ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout(); plt.savefig(png, dpi=110)

if __name__ == '__main__':
    new, old = sys.argv[1], sys.argv[2]
    bn, bo = trimesh.load_mesh(new), trimesh.load_mesh(old)
    tn, to = np.asarray(bn.triangles), np.asarray(bo.triangles)
    rep = {'mesh': [mesh_report(new)] + [mesh_report(p) for p in sys.argv[3:]]}
    rep['chin_new'] = chin_check(tn, ZP_NEW, 'v10.1-FDM'); print(rep['chin_new'], flush=True)
    rep['chin_old'] = chin_check(to, ZP_OLD, 'v10.1 MJF baseline'); print(rep['chin_old'], flush=True)
    rep['chin_clearance_new'] = chin_clearance(bn, ZP_NEW)
    if len(sys.argv) > 3:   # lid vs body (design frame): lid surface samples inside the body deeper than 0.05 mm
        cs = ColumnSolid(tn, x0=-4, y0=-6, x1=360, y1=234, h=0.2)
        lid = trimesh.load_mesh(sys.argv[3]); P = sample_surface(np.asarray(lid.triangles), 0.3)
        ins, dep = cs.inside(P); deep = ins & (dep > 0.05)
        rep['lid_in_body'] = {'samples': int(len(P)), 'inside_gt_0p05': int(deep.sum()), 'max_depth': round(float(dep[ins].max()), 3) if ins.any() else 0}
        print('lid', rep['lid_in_body'], flush=True)
    rep['parts_new'] = part_interference(tn, ZP_NEW); print('new', rep['parts_new'], flush=True)
    rep['parts_old'] = part_interference(to, ZP_OLD); print('old', rep['parts_old'], flush=True)
    sections(bn, bo, HERE / 'sections.png')
    (HERE / 'check-report.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print('done')
