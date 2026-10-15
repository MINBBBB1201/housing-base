"""FDM-specific checks on design-frame STLs: wall thickness, cavity height, rear-screw head vs chin.
usage: python fdm_checks.py design_body.stl baseline_v10_1_design_body.stl design_lid.stl
"""
import sys, json, numpy as np, trimesh
from pathlib import Path
_src = open(Path(__file__).with_name('check.py'), encoding='utf-8').read()
exec(_src[:_src.rindex("\nif __name__")])          # shared helpers: frames, display sweep, ColumnSolid
HERE = Path(__file__).resolve().parent

def thickness(mesh, n=60000, seed=5):
    pts, fi = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fi]
    loc, ri, _ = mesh.ray.intersects_location(pts - nrm * 1e-3, -nrm, multiple_hits=False)
    t = np.full(n, np.nan); t[ri] = np.linalg.norm(loc - pts[ri], axis=1)
    ok = ~np.isnan(t)
    return pts[ok], t[ok]

def cavity_height(mesh, zp, x=170.0, ys=range(20, 150, 10)):
    """Free vertical space in the wedge cavity at column x: lid top (foot_h + floor_t = 5) to roof underside."""
    rows = []
    for y in ys:
        loc, _, _ = mesh.ray.intersects_location(np.array([[x, y, 80.0]]), np.array([[0, 0, -1.0]]))
        zs = np.sort(loc[:, 2]) if len(loc) else np.array([])
        roof = zs[zs < zp(y) - 0.5]
        rows.append((y, round(float(roof.max()) - 5.0, 2) if len(roof) else None))
    return rows

def screw_head_vs_chin(zp):
    """Rear screws sit at y 11.83, where the chin sweep ends. Laptop frame (rel = z - zp(y)):
    head bottom = seat 1.61 - ISO 7045 head 1.6 = +0.01; chin = highest rel of swept points within head radius 2.0 + 0.3."""
    q = display_exterior(0.25)
    out = {}
    for sx in (20.41, 177.66, 334.91):
        qq = q[np.abs(q[:, 0] - sx) < 3.0]
        hi = -99.0
        for _, r in sweep(qq, np.arange(0, 135.01, 0.5)):
            c = to_cad(r, zp); rel = c[:, 2] - zp(c[:, 1])
            m = (np.hypot(c[:, 0] - sx, c[:, 1] - 11.83) < 2.3) & (rel < 1.0)
            if m.any(): hi = max(hi, float(rel[m].max()))
        out[str(sx)] = {'chin_highest_rel_under_head': round(hi, 2) if hi > -99 else None, 'head_bottom_rel': 0.01,
                        'clearance_mm': round(0.01 - hi, 2) if hi > -99 else 'chin never under the head'}
    return out

if __name__ == '__main__':
    bn, bo = trimesh.load_mesh(sys.argv[1]), trimesh.load_mesh(sys.argv[2])
    rep = {}
    for lab, m in [('body_new', bn), ('body_v10_1', bo), ('lid_new', trimesh.load_mesh(sys.argv[3]))]:
        p, t = thickness(m)
        rep[f'thickness_{lab}'] = {'samples': int(len(t)), 'pct_lt_0p8': round(100 * float((t < 0.8).mean()), 2),
                                   'pct_lt_1p0': round(100 * float((t < 1.0).mean()), 2), 'pct_lt_1p2': round(100 * float((t < 1.2).mean()), 2),
                                   'p01_mm': round(float(np.percentile(t, 1)), 2)}
        if lab == 'body_new':
            cells = {}
            for q in p[t < 0.8]:
                k = (int(q[0] // 20) * 20, int(q[1] // 20) * 20); cells[k] = cells.get(k, 0) + 1
            rep['thin_lt_0p8_cells_20mm'] = sorted([[k[0], k[1], v] for k, v in cells.items()], key=lambda r: -r[2])[:12]
    rep['cavity_height_new_x170'] = cavity_height(bn, ZP_NEW)
    rep['cavity_height_v10_1_x170'] = cavity_height(bo, ZP_OLD)
    rep['rear_screw_head_vs_chin'] = screw_head_vs_chin(ZP_NEW)
    (HERE / 'fdm-checks.json').write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ['thickness_body_new', 'thickness_body_v10_1', 'thickness_lid_new', 'rear_screw_head_vs_chin']}, indent=1))
