# v10 병행 독립 감사 — CAD/발주 설계는 Claude 쪽에서 관리

이 폴더의 검사 스크립트와 결과는 **원본 CAD/STL/발주서를 수정하지 않는다.** `preflight.py`는 실행 시점의 v10 PRINT 본체·뚜껑 해시, 메시 상태, 설계좌표↔실물방향 좌우 반전, 과거 검사 파일의 최신 여부, 기존 v4 후보 부품의 수납 높이 상한을 기록한다. `preflight-current.json`은 스냅샷이며 STL이 바뀌면 재실행해야 한다. `body_lid_overlap.scad`는 OpenSCAD에서 현재 파라메트릭 본체·뚜껑의 불리언 교차를 다시 계산한다.

## 독립 확인으로 확정된 범위

- v10 PRINT 파일은 대응하는 연구좌표 STL을 X=355.32 mm 기준으로 반전한 것과 정점 위치가 약 0.001 mm 이내로 일치한다. 따라서 **출력 방향 변환은 들어 있다.** 이것이 노트북 실물 방향·체결 공차의 독립 증명은 아니다.
- 2026-09-27 최신 `base_cover.scad`의 본체와 뚜껑을 OpenSCAD/CGAL로 다시 교차시킨 결과 `Current top level object is empty`였다(현 PRINT 본체 12,764면·뚜껑 3,340면). **두 CAD 솔리드의 체적 간섭은 없다.** 이것은 끼움 간극·스냅 유지력·실물 체결을 검증하지 않는다. STL이 다시 바뀌면 재실행해야 한다.
- `v10_check.py`는 PRINT가 아닌 연구좌표 STL을 입력으로 사용한다. 따라서 검사 기록의 뚜껑 3,332면과 PRINT 뚜껑 3,340면의 차이 **자체는 오래된 검사라는 증거가 아니다.** 2026-09-27 재실행 결과 연구좌표 메시의 `geometric_screen_pass=true`, 본체·뚜껑 교차 공집합이었다. PRINT 메시의 방향·위상·치수·DFM은 아래 독립 검사로 별도 확인했다. `preflight-current.json`은 각 검사 입력의 삼각형 수를 기준으로 판별한다.
- 기존 Waveshare 1→4 분배기(케이스 83.69×57.4×13.98 mm)와 USB3 캡처(플러그 포함 일부 외형 65.95×25.3×12.65 mm)는 단품을 가장 유리한 후방 끝에 놓아도 현재 C03 연구 공동 높이에서 각각 **5.252 mm, 1.533 mm 부족**하다. HDMI 플러그·전원·마운트·케이블은 계산에서 빠져 있다. v10의 외형/후크 개선이 이 불합격을 바꾸지 않는다.

## 최종품으로 표시하면 안 되는 네 가지 이유

1. **나사 안전:** Dell 공식 정비 문서는 하판용 M2×5 6개와 captive 2개를 지정한다. 현 조립표의 뒤 M2×8·앞 M2×6 대체는 웹 메시 기반 나사 자리 계산이며 상대 팜레스트 보스의 실측 깊이, screw bottom-out, 숨은 부품 접촉을 검증하지 못했다. 길어진 나사를 '순정과 같은 끝'이라고 보장하지 않는다. 조립 시 길이별 가벼운 손체결·깊이 확인 전에는 통전하지 않는다.
2. **v4 전기 기능:** Dell 원패널 전체 suffix·하네스 핀맵, eDP 수신기 출하 리비전/전원/HPD·EDID, 원패널 컨트롤러 펌웨어가 미확정이다. CAD 통로는 신호·전원 호환을 증명하지 않는다. 핀을 추정해 연결하거나 HDMI/USB 전원을 역급전시키지 않는다.
3. **열/공기:** v10 팬 슬롯은 위·아래로 관통한다는 기하 검사가 있으나, 유효 슬롯 개구 약 810 mm²·팬 상부 약 1377 mm²는 **면적**이다. 순정 대비 팬 유량, 단락 재순환, 배터리·SSD·신규 보드 온도, 3시간 성능은 유효한 CFD/열 측정이 없어 미판정이다. 큰 구멍을 추가해도 자동으로 해결되지 않는다.
4. **실물 결합/제조:** Dell 3D 수리 모델은 경량 메시다. 실제 후크 걸림 홈·두께·OEM 체결면 Z, 두 captive 나사 유지 구조와 355 mm 프린트 휨은 없다. JLC PA12-HP의 일반 장변 공차 ±0.4%는 355.32 mm 전체에서 약 ±1.42 mm 수준이며, 이는 정밀 맞춤 보증이 아니다. DFM 샘플 중 일부는 1 mm 아래로 보고돼 프린터가 그 부위의 강도·출력 가능성을 확인해야 한다.

## Claude의 v10 발주 패키지에 전달할 체크

- `06-order/FINAL-ORDER-v10/발주서-최종-ko.md`는 '이 폴더 하나만' 사용하고 STL 두 개를 업로드하라고 한다. 02:06 KST에는 빠져 있었으나 02:15에 두 파일이 추가됐다. 원본 ASCII STL과 패키지 바이너리 STL은 바이트 해시는 다르지만, 독립 비교에서 삼각형 수가 같고 정점 오차는 본체 0.000017 mm·뚜껑 0.000015 mm 이내였다. **현 시점 형상은 일치**한다. 이후 STL이 바뀌면 `preflight.py`로 재확인한다.
- PRINT 본체·PRINT 뚜껑 **두 개만** 출력 대상으로 지정한다. 연구좌표 STL, v9 이전 STL은 섞지 않는다. 두 파일 해시와 수정시각이 검사 기록과 같은지 확인한다.
- 최종 STL 변경 뒤 메시/본체↔뚜껑 교차/좌우방향/치수·부품 간섭/DFM을 **전부 다시** 실행한다. 이전 결과의 `geometric_screen_pass`를 새 파일에 이월하지 않는다.
- 업체에는 장변 휨, 측면 스피커 절개 인근 1 mm 미만 얇은 모서리, 스냅 6개, 팬 덕트 잔류 분말, 총 외곽과 8개 나사 자리를 사진·측정으로 검수하게 한다. 재료 데이터의 1 mm 최소벽은 얇은 모서리나 인쇄 방향의 스냅 내구 보증이 아니다.
- 최종 중국어 메모의 `请勿...加厚`(임의 두께 보정 금지)는 형상 보존에는 적절하지만, 얇은 부위가 업체 DFM에서 경고되면 **그냥 생산**하라는 뜻으로 해석되면 안 된다. 생산 전 문제 부위 이미지/좌표를 받아 승인·수정 결정을 하게 한다. 현재 DFM의 하위 1%가 1.2 mm라는 수치와 별개로, 표본 중 약 0.44%는 1 mm 미만으로 나온다(모서리 샘플링 오차 가능성 포함).
- M2×8/M2×6은 **사전 확정 하드웨어가 아니라 조건부 후보**로 표기하고, 2개의 captive 자리와 별도로 실제 나사 끝·보스 깊이를 확인한다. 불확실하면 기존 순정 나사보다 긴 나사를 강제로 조이지 않는다.
- '노트북 하판 시제품'과 'v4 전체 내부 탑재·3시간 무중단 작동 제품'을 발주 승인 문구에서 분리한다. 후자는 현재 부품 구성으로 기하적으로 불가능하다. 기존 부품을 유지한다면 외부 절연 박스로 빼는 것은 **새 구성 결정**이며, 선재·커넥터·변형 방지·전원·발열을 별도로 설계해야 한다.

## 재현

```powershell
python 05-verify/codex-independent-2026-09-27/preflight.py
& 'C:\Program Files\OpenSCAD\openscad.com' -o 05-verify/codex-independent-2026-09-27/body_lid_overlap.stl 05-verify/codex-independent-2026-09-27/body_lid_overlap.scad
```

OpenSCAD 교차가 `top level object is empty`라면 파라메트릭 모델의 현재 두 부품 사이 **체적 겹침만** 없다. 얇은 간극으로 실제 스냅이 끼워지는지, PA12/레진에서 반복 탈부착 가능한지는 별개다.

### 출처

- Dell Inspiron 15 3525 Service Manual, [나사 목록](https://www.dell.com/support/manuals/en-np/inspiron-15-3525-laptop/inspiron15_3525_sm/screw-list?guid=guid-cc648b28-fbf9-4a6f-bb11-4c6c2fa3d08a&lang=en-us)
- JLC3DP [PA12-HP Nylon](https://jlc3dp.com/help/article/pa12-hp-nylon): 최대 크기, 공차, 최소 벽, 재료 성질. 업체의 현재 견적과 실제 공정 능력은 별도 확인.
- v4 후보 Waveshare [1→4 HDMI splitter 외형](https://www.waveshare.com/img/devkit/accBoard/HDMI-SPLITTER-1IN-4OUT/HDMI-SPLITTER-1IN-4OUT-details-size.jpg), [USB3 capture 외형](https://www.waveshare.com/img/devkit/accBoard/HDMI-to-USB-Adapter/HDMI-to-USB3.0-Adapter-details-size.jpg).
