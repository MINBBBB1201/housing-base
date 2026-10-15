"""배치도: OEM 03JRFX 하판 안쪽(힌지 쪽이 위, 정상 사용 자세 기준 왼쪽 = DC-in 쪽 = 이미지 왼쪽).
Background: user photo 05 rectified to the Dell frame (faded). Overlays in mm from clips.json, Dell screws, CAD params."""
import json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
PX, MX, MY = 4.0, 6, 8
W, D = 355.32, 226.20
bg = cv2.imread('../../00-input/dell-official-3d/rect-05-interior-dellframe.png')[:, :, ::-1]
bg = (bg * 0.45 + 255 * 0.55).astype(np.uint8)
H0, W0 = bg.shape[:2]; PANEL = 560
im = Image.new('RGB', (W0 + PANEL, H0 + 70), 'white'); im.paste(Image.fromarray(bg), (0, 0))
d = ImageDraw.Draw(im, 'RGBA')
F = lambda s, b=False: ImageFont.truetype('malgunbd.ttf' if b else 'malgun.ttf', s)
f10, f12, f14, f16, f20 = F(11), F(13), F(15), F(17), F(21, True)
P = lambda x, y: ((x + MX) * PX, (y + MY) * PX)
COL = {'A': (0, 150, 60), 'B': (20, 90, 230), 'C': (160, 40, 190), 'X': (130, 130, 130)}
clips = json.load(open('clips.json'))['clips']
# v9 (final fit simulation): B6-B9 heat sink, F2/F4/F6/F10 speaker, R1/R2 I/O board -> removed
# v10 (0.1 mm fine check): F9 speaker 3.5 mm, L3 system board 2.7 mm -> removed; 13 hooks kept
in_cad = {('rear', c) for c in ('B1','B2','B3','B4','B5')} | {('front', c) for c in ('F1','F5','F7')} \
       | {('right', f'R{i}') for i in range(3, 7)} | {('left', 'L5')}
# grid
for mm in range(0, 360, 10):
    x, _ = P(mm, 0); d.line([(x, 0), (x, H0)], fill=(0, 0, 0, 22 if mm % 50 else 60))
    if mm % 50 == 0: d.text((x + 2, 2), str(mm), fill=(0, 0, 0), font=f12)
for mm in range(0, 230, 10):
    _, y = P(0, mm); d.line([(0, y), (W0, y)], fill=(0, 0, 0, 22 if mm % 50 else 60))
    if mm % 50 == 0: d.text((2, y + 2), str(mm), fill=(0, 0, 0), font=f12)
# hinge notches, grille, posts, pin holes
for x0, x1 in ((29.01, 63.81), (291.51, 326.31)):
    d.rectangle([P(x0, -2), P(x1, 11)], outline=(230, 120, 0), width=3); d.text(P(x0 + 1, 11.5), '힌지 홈', fill=(200, 100, 0), font=f12)
d.rectangle([P(219.8, 24.2), P(276.5, 54.4)], outline=(0, 140, 140), width=3); d.text(P(221, 55), '팬 흡기 그릴 X219.8~276.5 Y24.2~54.4', fill=(0, 120, 120), font=f12)
for x in (109, 130, 145, 175, 204, 211):
    cx, cy = P(x, 106 * 226.2 / 235.6); d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(120, 80, 0), width=3)
d.text(P(105, 106), '지지 기둥 6 (기존 사진값)', fill=(120, 80, 0), font=f12)
for x, y in ((57.55, 16.08), (297.55, 16.08), (59.5, 197.5), (295.75, 197.5)):
    cx, cy = P(x, y); d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(200, 0, 200), width=2)
# screws
scr = [('뒤-왼 captive', 20.41, 11.83), ('뒤-중 (속 빈 보스 ~7mm)', 177.66, 11.83), ('뒤-오 captive', 334.91, 11.83),
       ('중-왼', 9.01, 119.63), ('중-오', 346.31, 119.63), ('앞-왼 (사진에 가려짐)', 9.01, 217.14), ('앞-중', 177.66, 217.98), ('앞-오', 346.31, 217.14)]
for n, x, y in scr:
    cx, cy = P(x, y); d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=(220, 0, 0), width=4)
    tx = cx + 14 if x < 300 else cx - 14 - d.textlength(n, font=f12); d.text((tx, cy - 22 if y > 200 else cy + 8), n, fill=(200, 0, 0), font=f12)
# clips
for c in clips:
    x, y = c['x'], c['y']; cad = (c['wall'], c['id']) in in_cad
    col = COL[c['conf']] if cad else COL['X']; cx, cy = P(x, y)
    along = c['wall'] in ('rear', 'front'); w = 5 * PX
    box = [cx - w / 2, cy - 7, cx + w / 2, cy + 7] if along else [cx - 7, cy - w / 2, cx + 7, cy + w / 2]
    d.rectangle(box, fill=col + (170,) if cad else None, outline=col, width=2)
    lab = f"{c['id']} {x:.0f}" if along else f"{c['id']} {y:.0f}"
    if c['wall'] == 'rear': d.text((cx - 16, cy + 9), lab, fill=col, font=f12)
    elif c['wall'] == 'front': d.text((cx - 16, cy - 26), lab, fill=col, font=f12)
    elif c['wall'] == 'left': d.text((cx + 10, cy - 8), lab, fill=col, font=f12)
    else: d.text((cx - 12 - d.textlength(lab, font=f12), cy - 8), lab, fill=col, font=f12)
# panel
x0 = W0 + 18; y = 12
d.text((x0, y), 'OEM 03JRFX 하판 안쪽 배치도', fill=(0, 0, 0), font=f20); y += 34
for t in ['사진 가상 스캔 2026-09-26 · 단위 mm · Dell 3D 가이드 좌표',
          '힌지 쪽 위. 이미지 왼쪽 = 정상 사용 자세 왼쪽(DC-in 쪽).',
          '배경: 사용자 사진 05를 나사·핀 구멍으로 보정(흐리게).']:
    d.text((x0, y), t, fill=(60, 60, 60), font=f14); y += 22
y += 8
for k, t in [('A', 'A  두 사진(05·08) 일치 ±1.5 mm'), ('B', 'B  한 사진, 후크 뚜렷 ±2~3 mm'), ('C', 'C  옆면이 거의 안 보임, 좌우대칭으로만 확인'),
             ('X', '회색 = CAD 미반영 (불확실·납작 탭·v9/v10 충돌 제거)')]:
    d.rectangle([x0, y + 3, x0 + 18, y + 17], fill=COL[k] + (170,), outline=COL[k]); d.text((x0 + 26, y), t, fill=(0, 0, 0), font=f14); y += 24
y += 6
d.text((x0, y), '후크 위치 (벽 따라, mm)', fill=(0, 0, 0), font=F(16, True)); y += 26
for wall, nm, key in (('rear', '뒤 벽 (X)', 'x'), ('front', '앞 벽 (X)', 'x'), ('right', '오른쪽 벽 (Y)', 'y'), ('left', '왼쪽 벽 (Y)', 'y')):
    items = [c for c in clips if c['wall'] == wall]
    d.text((x0, y), nm, fill=(0, 0, 0), font=F(14, True)); y += 21
    line = ''
    for c in items:
        s = f"{c['id']}:{c[key]:.1f}{'' if (wall, c['id']) in in_cad else '*'}  "
        if d.textlength(line + s, font=f14) > PANEL - 40: d.text((x0 + 8, y), line, fill=(30, 30, 30), font=f14); y += 20; line = ''
        line += s
    d.text((x0 + 8, y), line, fill=(30, 30, 30), font=f14); y += 26
d.text((x0, y), '* = CAD 미반영', fill=(90, 90, 90), font=f12); y += 26
for t in ['측정 추가값', '· 탭은 Dell 메시 벽 윗면보다 3.06±0.36 mm 솟음 (사진 08, 6개)',
          '· 뒤-중 나사 보스: 바닥에서 약 7 mm 솟은 속 빈 원통 (두 사진',
          '  삼각측량). Dell 웹 모델에는 없는 형상',
          '· 앞 벽 쌍 X50↔303, 90↔261, 128↔222, 161↔192: 좌우 대칭',
          '  차이 2~6 mm → 앞 벽 오차 추정 근거',
          '',
          '한계', '· 걸림 턱 깊이·후크 두께·보스 내경은 사진으로 못 잼',
          '· 왼쪽 벽은 사진 두 장 모두에서 거의 안 보임',
          '· 발주 전 순정 하판/팜레스트로 시험 조립 필요']:
    d.text((x0, y), t, fill=(0, 0, 0) if t in ('측정 추가값', '한계') else (40, 40, 40), font=F(15, True) if t in ('측정 추가값', '한계') else f14); y += 21
d.text((10, H0 + 10), '원자료: 02-measure/virtual-scan/clips.json · cam05.json · cam08.json  |  CAD 반영: 04-cad/params.scad clips_list (v10: 13개)', fill=(60, 60, 60), font=f14)
d.text((10, H0 + 36), '빨강 = 나사 8 (Dell 좌표)  주황 = 힌지 홈  청록 = 흡기 그릴  갈색 = 지지 기둥  자홍 = 고무발 핀 구멍', fill=(60, 60, 60), font=f14)
im.save('LAYOUT-base-cover-interior.png'); print(im.size)
