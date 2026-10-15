# 노트북 전체 가상 스캔 — Dell Inspiron 15 3525 (2026-09-28)

**한 줄 요약:** Dell 공식 3D 수리 가이드에서 뽑은 **노트북 전체 3D 조립 모델**을 실물 방향으로 정리했다. 인터넷에서 모은 실제 사진·Dell 공식 그림과 겹쳐 보니 외형·포트·내부 부품 배치가 맞는다. 요약 그림은 [`VIRTUAL-SCAN-FULL-sheet.png`](VIRTUAL-SCAN-FULL-sheet.png)이다.

> 저작권: Dell 3D 데이터와 수집한 사진(Dell, LaptopMedia)은 **개인 설계 참고용**이다. 업체에 보내거나 공개하지 않는다. 업체에는 우리가 만든 하판 STL만 보낸다.

## 1. 3D 자료 (수치가 아니라 형상 데이터)

| 파일 | 내용 |
|---|---|
| `dell3525_full_laptop_virtualscan.glb` | 노트북 전체 22개 부품 그룹, 부품별 색. Windows 3D 뷰어·Blender로 열린다 |
| `dell3525_full_laptop_virtualscan.stl` | 같은 모델, 한 덩어리 STL (삼각형 299,474) |
| `dell3525_exterior_shell.stl` | 외형만 (하판 + 팜레스트/키보드 + 디스플레이) |
| `parts_phys/*.stl` | 부품별 STL 22개 (하판, 팜레스트, 디스플레이, 좌우 힌지, 메인보드, 팬, 방열판, 배터리, SSD, WLAN, 메모리, I/O 보드, DC 잭, 전원 버튼, 터치패드, 스피커, eDP/WLAN 케이블, 하판 나사) |
| `full_laptop_view.scad` | 부품 색·분해도 보기 (`-D mode="exploded"`, `-D hide=[...]`) |
| `render-*.png` | 앞 왼쪽·뒤 오른쪽 등각 모습, 분해도, 하판 뺀 아래 모습 |

- **좌표**: 실물 방향 오른손 좌표계. X = 사용자 왼쪽(DC-in) → 오른쪽, Y = 앞 → 힌지, Z = 책상 → 위. 덮개를 닫은 상태다.
- **크기**: 358.67 × 235.84 × 20.15 mm (고무발 포함).
- **원본**: Dell 3D Guides 뷰어의 glTF(LOD0 고해상도 메시, 137개). 추출 기록은 [`../../00-input/dell-official-3d/README.md`](../../00-input/dell-official-3d/README.md)에 있다.

## 2. 인터넷에서 모은 사진·그림

| 폴더 | 출처 | 수량 |
|---|---|---|
| `00-input/web-photos/dell-manual/` | Dell 공식 Setup & Specifications: 왼쪽(두 가지), 오른쪽, 위, 아래, 디스플레이 뷰, 1800 px | 13 |
| `00-input/web-photos/dell-service-manual/` | Dell 공식 서비스 매뉴얼 63쪽의 분해 그림 (하판 분리, 배터리, 팬, 방열판, 힌지, I/O 보드, 나사 목록 등), 최대 2662 px | 55 |
| `00-input/web-photos/laptopmedia-vostro3525/` | LaptopMedia의 Vostro 15 3525 리뷰 실물 사진: 내부(하판 분리), 좌·우 옆면, 윗면, 배터리·SSD·RAM·냉각 | 21 |

Vostro 15 3525는 Inspiron 3525와 외형·내부 배치가 같은 계열이다. 다만 **오른쪽에 RJ45 유선랜 포트가 있어** 그쪽 옆면은 다르다(Inspiron은 SD·USB 2.0·이어폰만 있음). 그래서 오른쪽 옆면 검증에는 Dell 공식 Inspiron 그림을 썼다.

**웹 사진으로 포토그래메트리를 하지 않은 이유:** 사진마다 카메라·조명·기종이 다르고, 같은 물체를 겹치게 찍은 여러 각도의 사진이 없다(대부분 정면 한 장씩). 그래서 3D 재구성이 되지 않는다. 대신 Dell 공식 3D가 이미 있으므로, 사진은 **3D 모델이 실물과 맞는지 검증하는 기준**으로 썼다.

## 3. 검증 결과

| 검증 | 방법 | 결과 |
|---|---|---|
| 전체 크기 | 모델 vs Dell 공개 제원 358.50 × 235.56 | 358.67 × 235.84 (차이 0.17 / 0.28 mm) |
| 두께 비율 | 실제 옆면 사진 2장의 높이/길이 비 | 사진 0.0844·0.0834 vs 모델 0.0854 → 두께 19.7~19.9 vs 20.1 mm (사진 원근 오차 1~2% 이내) |
| **왼쪽 포트** | 실제 옆면 사진·Dell 그림 위에 모델 옆모습 윤곽을 겹침 | DC 잭, LED, HDMI, USB-A, USB-C 윤곽이 실제 포트와 겹친다. DC-in 중심은 모델 17.5 mm, Dell 그림 약 18 mm(뒤 끝 기준) |
| **오른쪽 포트** | Dell 그림 vs 모델 I/O 보드 커넥터 | USB 2.0: 모델 34.5 / 그림 약 35 mm. SD: 모델 48~72 / 그림 중심 약 61 mm. 모델의 팜레스트 오른쪽 벽에는 포트 구멍이 생략돼 있다(경량 모델) |
| 옆모습 윤곽·발 위치 | 같은 겹침 | 뚜껑·팜레스트·하판 층과 앞뒤 고무발 위치가 일치 |
| **내부 부품** | 하판을 뗀 실제 사진을 외곽선 기준으로 펴서(원근 보정) 모델 윤곽과 겹침. 부품마다 사진 가장자리에 가장 잘 맞는 이동량을 계산 | 팬 1.4·2.0, SSD 0.8·2.2, 팜레스트 0.6·1.6, 힌지 0.6~2.2 mm. 대부분 +Y로 약 2 mm 쏠려 있다. 부품이 외곽선보다 약 2 cm 카메라에 가까워서 생기는 원근 효과로 보이며, 실제 위치 오차는 이보다 작다 |
| 좌우 방향 | 실제 사진의 DC-IN 표기·팬 위치 | 모델과 같다(DC-in 왼쪽, 팬 오른쪽 뒤). 발주 PRINT 파일의 방향이 맞다는 추가 확인이다 |

부품별 수치는 [`offsets-internals42.json`](offsets-internals42.json), 겹침 그림은 `overlay-internals42.png`, `side-*.png`에 있다.

## 4. 하판 설계(v10.1)에 주는 의미

- 설계와 시뮬레이션의 기준인 Dell 3D 모델이 실제 사진·공식 그림과 맞는다는 것을 독립적으로 확인했다. 외곽, 포트 위치, 내부 부품 배치가 모두 맞다.
- 측면 모따기 구간(Y ≤ 111, 힌지 기준)은 실제 포트 범위(DC 13.6 ~ 왼쪽 두 번째 USB 약 90 mm, 오른쪽 SD 72 mm까지)를 덮는다.
- **여전히 못 얻은 것**: 하판 후크 걸림턱 형상, 나사 보스 내부 치수. 웹 사진에도 이 부분의 치수 자료는 없다.

## 5. 재현

```
python build_full_model.py                       # 전체 모델(glb/stl) + full-model-info.json
python photo_overlay.py <내부사진> overlay-internals42.png
python part_offsets.py overlay-internals42-photo-rectified.png overlay-internals42.json offsets-internals42.json
python side_overlay.py <옆면사진> left|right <out.png> [밝기 임계값]
```
