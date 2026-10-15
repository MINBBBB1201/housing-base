"""Project selected Dell guide meshes through proposed eDP passthrough slots.

The guide meshes are incomplete. Zero ray hits is only a screening result,
not permission to move a real display cable through the laptop internals.
"""
from pathlib import Path
import numpy as np
import trimesh

PARTS = Path(r"C:\Users\mimin\Desktop\k\eDP Capture\prototype-v5\housing-base\00-input\dell-official-3d\parts")
NAMES = ["Ins_15_3525_Systemboard_GP.stl", "Ins_15_3525_Heatsnk_UMA_GP.stl", "Ins_15_3525_Memory_Module_GP.stl", "Inspiron_3525_Display_Cable.stl"]
SLOTS = {"old":(63.5,110,13,31),"forward":(63.5,110,46,61),"forward_left":(58,84,44,61),"side":(50,65,45,72)}

for name in NAMES:
    mesh=trimesh.load(PARTS/name,force="mesh")
    print(name,len(mesh.faces))
    for label,(x0,x1,y0,y1) in SLOTS.items():
        xs=np.arange(x0+0.5,x1,2.0)
        ys=np.arange(y0+0.5,y1,2.0)
        XY=np.array([(x,y) for x in xs for y in ys])
        origins=np.column_stack((XY,np.full(len(XY),-20.0)))
        dirs=np.tile((0,0,1.0),(len(XY),1))
        hits=mesh.ray.intersects_any(origins,dirs)
        print(label,int(hits.sum()),"/",len(hits))
