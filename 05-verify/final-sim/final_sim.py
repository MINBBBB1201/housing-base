"""Final fit simulation: Dell 3525 3D-guide internals vs (a) OEM base cover [baseline] and (b) our CAD body.
Interference = internal-part surface samples lying inside the solid. Reported per part, with the depth to the
top of the solid in that column. Zref: OEM flat exterior plane (Dell Z 10.06) == CAD zp(y)."""
import json, sys, numpy as np
sys.path.insert(0, '.')
from fs_common import *
ZREF = 10.06
import os
GH = float(os.environ.get('FS_H', 0.5)); SP = float(os.environ.get('FS_SP', 0.5))   # column grid / sample spacing (mm)
PRINT = '--print-frame' in sys.argv   # body STL in the physical (print) frame: map Dell parts by a proper rotation (x -> W - x)
def mapT(T):
    Q = dell_to_cad(T, ZREF)
    if PRINT: Q[..., 0] = W - Q[..., 0]
    return Q
PARTS = ['Ins_15_3525_Palmrest_GP', 'Ins_15_3525_Battery_3cell_GP', 'Ins_15_3525__Battery_Cable_GP', 'Ins_15_3525_Systemboard_GP',
         'Ins_15_3525_Fan_GP', 'Ins_15_3525_Heatsnk_UMA_GP', 'Ins_15_3525_Speaker_GP', 'Ins_15_3525_SSD_GP', 'Ins_15_3525_WLAN_GP',
         'Ins_15_3525_Memory_Module_GP', 'Ins_15_3525_IO_Board_GP', 'Ins_15_3525_Power_Adapter_Port_GP', 'Ins_15_3525_PowerButtonfbx_GP',
         'Ins_15_3525_Touchpad_GP', 'Ins_15_3525_HDD_GP', 'Inspiron_3525_Display_Right_Hinges', 'Inspiron_3525_Display_Left_Hinges',
         'Inspiron_3525_Display_Cable', 'Inspiron_3525_Display_WLAN_Cable', 'Ins_15_3525_Display_Assembly_GP']
CLIPS = [[0, 19.7, 4.0], [0, 71.0, 5.6], [0, 104.4, 5.6], [0, 141.4, 5.6], [0, 203.4, 4.4], [0, 228.3, 5.0], [0, 243.2, 4.4],
         [0, 259.3, 5.0], [0, 284.8, 4.4], [1, 50.3, 5.6], [1, 90.4, 4.4], [1, 127.8, 8.0], [1, 160.9, 7.5], [1, 192.3, 6.3],
         [1, 221.7, 10.6], [1, 261.0, 8.8], [1, 302.6, 10.6], [3, 20.7, 4.0], [3, 40.5, 4.0], [3, 71.6, 4.0], [3, 97.4, 4.0],
         [3, 136.8, 4.0], [3, 184.6, 4.0], [2, 95.7, 4.0], [2, 136.3, 4.0]]
def at_clip(x, y):
    for w, s, cw in CLIPS:
        hw = min(cw, 5.0) / 2 + 0.6
        if w == 0 and y < 4 and abs(x - s) <= hw: return True
        if w == 1 and y > D - 4 and abs(x - s) <= hw: return True
        if w == 2 and x < 4 and abs(y - s) <= hw: return True
        if w == 3 and x > W - 4 and abs(y - s) <= hw: return True
    return False
def region(x, y):
    if at_clip(x, y): return 'clip tip'
    if y < 4: return 'rear wall'
    if y > D - 4: return 'front wall'
    if x < 4: return 'left wall'
    if x > W - 4: return 'right wall'
    return 'interior'
def run(body_path, label):
    body = load_stl(body_path)
    solid = ColumnSolid(body, h=0.5)
    oem = ColumnSolid(dell_to_cad(load_stl(DELL / 'Inspiron_3525_Basecover-1_002.stl'), ZREF), h=0.5) if label == 'ours' else None
    out = {}
    for p in PARTS:
        T = dell_to_cad(load_stl(DELL / f'{p}.stl'), ZREF)
        S = sample_surface(T, 0.5)
        ins, dep = solid.inside(S)
        rec = {'samples': int(len(S)), 'inside': int(ins.sum())}
        if ins.any():
            P = S[ins]; d = dep[ins]
            regs = {}
            for (x, y, z), dd in zip(P, d):
                r = region(x, y); g = regs.setdefault(r, [0, 0.0, [1e9, 1e9, -1e9, -1e9]])
                g[0] += 1; g[1] = max(g[1], dd); g[2] = [min(g[2][0], x), min(g[2][1], y), max(g[2][2], x), max(g[2][3], y)]
            rec['by_region'] = {r: {'n': g[0], 'max_depth_mm': round(g[1], 2), 'xy_box': [round(v, 1) for v in g[2]]} for r, g in regs.items()}
        out[p] = rec
    return out
if __name__ == '__main__':
    res = {'zref_dell': ZREF}
    res['baseline_oem'] = run(DELL / 'Inspiron_3525_Basecover-1_002.stl', 'oem-in-dell') if False else None
    # baseline: OEM cover mapped to CAD frame with the same transform
    import tempfile, struct as st
    oemT = mapT(load_stl(DELL / 'Inspiron_3525_Basecover-1_002.stl'))
    solid_oem = ColumnSolid(oemT, h=GH)
    solid_our = ColumnSolid(load_stl(CAD / sys.argv[1]), h=GH)
    base, ours = {}, {}
    for p in PARTS:
        T = mapT(load_stl(DELL / f'{p}.stl')); S = sample_surface(T, SP)
        for tag, solid, store in (('oem', solid_oem, base), ('ours', solid_our, ours)):
            ins, dep = solid.inside(S)
            rec = {'samples': int(len(S)), 'inside': int(ins.sum())}
            if ins.any():
                regs = {}
                for (x, y, z), dd in zip(S[ins], dep[ins]):
                    r = region(W - x if PRINT else x, y); g = regs.setdefault(r, [0, 0.0, [1e9, 1e9, -1e9, -1e9]])
                    g[0] += 1; g[1] = max(g[1], dd); g[2] = [min(g[2][0], x), min(g[2][1], y), max(g[2][2], x), max(g[2][3], y)]
                rec['by_region'] = {r: {'n': g[0], 'max_depth_mm': round(g[1], 2), 'xy_box': [round(v, 1) for v in g[2]]} for r, g in regs.items()}
            store[p] = rec
    res['baseline_oem'] = base; res['ours'] = ours; res['body'] = sys.argv[1]; res['grid_mm'] = GH; res['sample_mm'] = SP; res['print_frame'] = PRINT
    json.dump(res, open(sys.argv[2], 'w'), indent=1)
    print(f"{'part':38s} {'OEM inside':>10s} {'OURS inside':>11s}  ours by region (n, max depth mm)")
    for p in PARTS:
        o, u = base[p], ours[p]
        br = '; '.join(f"{r}: {v['n']} / {v['max_depth_mm']}" for r, v in u.get('by_region', {}).items())
        print(f"{p[:38]:38s} {o['inside']:10d} {u['inside']:11d}  {br}")
