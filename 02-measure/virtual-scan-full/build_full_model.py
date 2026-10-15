"""Whole-laptop 'virtual scan' model from the Dell 3525 3D-guide meshes (installed state, lid closed).
Output frame = PHYSICAL, right-handed, upright: X = user-left(DC-in side) -> right, Y = FRONT(user) -> HINGE (away from user),
Z = up from desk. (Dell parts frame is right-handed but upside down; rotate 180 deg about the X axis: y -> D - y, z -> -z.)
Dell 3D guide data: personal reference only, do not redistribute."""
import json, numpy as np, trimesh
from pathlib import Path
SRC = Path('../../00-input/dell-official-3d/parts')
D = 226.20
GROUPS = {   # name -> (colour RGBA, include)
 'Ins_15_3525_Base_Cover_GP': (60, 62, 68), 'Ins_15_3525_Palmrest_GP': (150, 152, 158), 'Ins_15_3525_Display_Assembly_GP': (40, 42, 48),
 'Inspiron_3525_Display_Right_Hinges': (190, 170, 90), 'Inspiron_3525_Display_Left_Hinges': (190, 170, 90),
 'Ins_15_3525_Systemboard_GP': (40, 120, 60), 'Ins_15_3525_Battery_3cell_GP': (70, 90, 150), 'Ins_15_3525__Battery_Cable_GP': (200, 60, 60),
 'Ins_15_3525_Heatsnk_UMA_GP': (200, 120, 60), 'Ins_15_3525_Fan_GP': (30, 30, 30), 'Ins_15_3525_Speaker_GP': (100, 60, 130),
 'Ins_15_3525_SSD_GP': (220, 200, 60), 'Ins_15_3525_WLAN_GP': (60, 180, 180), 'Ins_15_3525_Memory_Module_GP': (40, 160, 90),
 'Ins_15_3525_IO_Board_GP': (40, 140, 80), 'Ins_15_3525_Power_Adapter_Port_GP': (230, 130, 40), 'Ins_15_3525_PowerButtonfbx_GP': (120, 120, 120),
 'Ins_15_3525_Touchpad_GP': (110, 110, 115), 'Inspiron_3525_Display_Cable': (220, 60, 160), 'Inspiron_3525_Display_WLAN_Cable': (60, 60, 200),
 'Inspiron_3525_Basecover_Remove_Screws': (180, 180, 190), 'Inspiron_3525_Basecover_Loosen_Screws': (180, 180, 190)}
def load(name):
    m = trimesh.load(SRC / f"{name.replace(' ', '_')}.stl", force='mesh')
    v = m.vertices.copy(); v[:, 1] = D - v[:, 1]; v[:, 2] = -v[:, 2]       # rotate 180 deg about X (det +1)
    m = trimesh.Trimesh(v, m.faces, process=False)
    return m
meshes = {n: load(n) for n in GROUPS}
zmin = min(m.vertices[:, 2].min() for m in meshes.values())
scene = trimesh.Scene(); allm = []
for n, m in meshes.items():
    m.vertices[:, 2] -= zmin
    m.visual.face_colors = list(GROUPS[n]) + [255]
    scene.add_geometry(m, node_name=n, geom_name=n); allm.append(m)
full = trimesh.util.concatenate(allm)
ext = np.round(full.extents, 2)
scene.export('dell3525_full_laptop_virtualscan.glb'); full.export('dell3525_full_laptop_virtualscan.stl')
shell = trimesh.util.concatenate([meshes[k] for k in ('Ins_15_3525_Base_Cover_GP', 'Ins_15_3525_Palmrest_GP', 'Ins_15_3525_Display_Assembly_GP')])
shell.export('dell3525_exterior_shell.stl')
info = {'frame': 'X user-left->right, Y front->hinge, Z up (right-handed, upright, lid closed)', 'extents_mm': ext.tolist(),
        'triangles': int(len(full.faces)), 'parts': {n: {'tris': int(len(m.faces)), 'bbox_min': np.round(m.bounds[0], 2).tolist(), 'bbox_max': np.round(m.bounds[1], 2).tolist()} for n, m in meshes.items()}}
json.dump(info, open('full-model-info.json', 'w'), indent=1)
print('extents', ext, 'tris', len(full.faces))
