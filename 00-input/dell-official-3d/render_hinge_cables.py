"""Plan view from the keyboard side (normal user view, hinge edge at top, laptop-left on image left)
showing which hinge each display-side cable passes. Silhouettes only (no depth)."""
import struct, numpy as np
from PIL import Image, ImageDraw, ImageFont
PX, MX, MY = 4.0, 8, 12       # px/mm, margins (mm)
def stl(name):
    b = open(f'parts/{name}.stl', 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v']
layers = [  # (file, fill RGBA, label)
    ('Ins_15_3525_Palmrest_GP', (215, 215, 215, 255), None),
    ('Ins_15_3525_Fan_GP', (120, 170, 190, 255), 'Fan'),
    ('Ins_15_3525_Power_Adapter_Port_GP', (40, 160, 70, 255), 'DC-in port'),
    ('Ins_15_3525_IO_Board_GP', (150, 120, 60, 255), 'I/O board (SD, USB2)'),
    ('Ins_15_3525_PowerButtonfbx_GP', (140, 60, 170, 255), 'Power button'),
    ('Inspiron_3525_Display_Right_Hinges', (240, 150, 30, 200), 'Dell name: "Right_Hinges"'),
    ('Inspiron_3525_Display_Left_Hinges', (240, 150, 30, 200), 'Dell name: "Left_Hinges"'),
    ('Inspiron_3525_Display_WLAN_Cable', (30, 90, 230, 255), 'WLAN antenna cable'),
    ('Inspiron_3525_Display_Cable', (225, 20, 20, 255), 'eDP display cable'),
]
W, H = int((360 + 2 * MX) * PX), int((232 + 2 * MY) * PX)
im = Image.new('RGBA', (W, H), (255, 255, 255, 255)); dr = ImageDraw.Draw(im, 'RGBA')
try: f = ImageFont.truetype('arialbd.ttf', 20); fs = ImageFont.truetype('arial.ttf', 15)
except OSError: f = fs = ImageFont.load_default()
to = lambda p: ((p[0] + MX) * PX, (p[1] + MY) * PX)
boxes = []
for name, col, lab in layers:
    t = stl(name)
    for tri in t: dr.polygon([to(p) for p in tri], fill=col)
    if lab: boxes.append((lab, t[..., 0].min(), t[..., 0].max(), t[..., 1].min(), t[..., 1].max(), col))
for mm in range(0, 361, 50):
    dr.line([to((mm, -MY)), to((mm, -MY + 3))], fill=(0, 0, 0), width=2); dr.text((to((mm, 0))[0] + 2, 2), f'X{mm}', fill=(0, 0, 0), font=fs)
ys = {}
for lab, x0, x1, y0, y1, col in boxes:
    cx = (x0 + x1) / 2; ty = y1 + 4 if 'Hinge' not in lab else y1 + 2
    key = round(cx / 60); ty += 7 * ys.get(key, 0); ys[key] = ys.get(key, 0) + 1
    dr.rectangle([to((x0, y0)), to((x1, y1))], outline=col[:3] + (255,), width=2)
    dr.text((to((x0, ty))[0], to((x0, ty))[1]), f'{lab}  X{x0:.0f}~{x1:.0f}', fill=col[:3] + (255,), font=f)
dr.text((10, H - 52), 'VIEW FROM KEYBOARD SIDE (user view): hinge edge at top, laptop LEFT = image left.', fill=(0, 0, 0), font=f)
dr.text((10, H - 26), 'Left/right anchored by DC-in (left side per MEASURE-TABLE) + power button (top-right on 3525). Source: Dell 3D guide model.', fill=(60, 60, 60), font=fs)
im.convert('RGB').save('render-hinge-cables.png'); print(im.size)
