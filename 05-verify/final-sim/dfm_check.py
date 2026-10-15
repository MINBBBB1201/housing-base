"""Manufacturability screen of the order STLs (print frame): topology, volume, bbox, local wall thickness.
Thickness = distance from a surface sample, travelling inward along -normal, to the next surface (ray casting).
Thin clusters are reported in design coordinates (x_design = W - x_print) so they can be traced in params.scad.
Usage: python dfm_check.py <print_stl> [more ...]"""
import sys, json, numpy as np, trimesh
from pathlib import Path
CAD = Path(__file__).resolve().parents[2] / '04-cad'; W = 355.32
res = {}
for name in sys.argv[1:]:
    m = trimesh.load(CAD / name, force='mesh')
    r = {'watertight': bool(m.is_watertight), 'winding_consistent': bool(m.is_winding_consistent),
         'bodies': len(m.split(only_watertight=False)), 'triangles': int(len(m.faces)),
         'volume_cm3': round(float(m.volume) / 1000, 1), 'area_cm2': round(float(m.area) / 100, 1),
         'bbox_mm': np.round(m.extents, 2).tolist()}
    pts, fi = trimesh.sample.sample_surface_even(m, 150000, seed=3525)
    nrm = m.face_normals[fi]
    loc, ri, _ = m.ray.intersects_location(pts - nrm * 1e-3, -nrm, multiple_hits=False)
    th = np.full(len(pts), np.nan); th[ri] = np.linalg.norm(loc - pts[ri], axis=1)
    ok = np.isfinite(th)
    r['thickness_mm'] = {'p1': round(float(np.nanpercentile(th, 1)), 2), 'p5': round(float(np.nanpercentile(th, 5)), 2),
                         'median': round(float(np.nanmedian(th)), 2), 'share_below_0.8': round(float((th[ok] < 0.8).mean()), 4),
                         'share_below_1.0': round(float((th[ok] < 1.0).mean()), 4)}
    thin = pts[ok & (th < 0.8)]
    clusters = []
    if len(thin):
        from scipy.cluster.hierarchy import fcluster, linkage
        sub = thin[np.random.default_rng(0).choice(len(thin), min(len(thin), 4000), replace=False)]
        lab = fcluster(linkage(sub[:, :2], 'single'), 3.0, 'distance')
        for k in np.unique(lab):
            q = sub[lab == k]
            clusters.append({'n': int(len(q)), 'x_design': [round(float(W - q[:, 0].max()), 1), round(float(W - q[:, 0].min()), 1)],
                             'y': [round(float(q[:, 1].min()), 1), round(float(q[:, 1].max()), 1)],
                             'z': [round(float(q[:, 2].min()), 1), round(float(q[:, 2].max()), 1)]})
        clusters.sort(key=lambda c: -c['n'])
    r['thin_below_0.8_clusters'] = clusters[:25]
    res[name] = r
    print(name, json.dumps({k: v for k, v in r.items() if k != 'thin_below_0.8_clusters'}, ensure_ascii=False))
    for c in clusters[:25]: print('   thin', c)
json.dump(res, open('dfm-check-v10.json', 'w'), indent=1)
