# Dell 3525 교체 하판 + prototype-v4 통합 정적 검증 — 2026-09-26

**판정: 연구 CAD 개정 v5 생성·메시 검사 완료, v4 전체 수납 및 열/전기 적합성은 NO-GO/미판정. 발주 파일 아님.** 여기의 CAD `v5`와 전자회로 `prototype-v4`는 다른 버전 체계다. 실물 체결·통전 시험은 사용자 요청대로 범위에서 제외했다. 제외한 시험의 합격을 암시하지 않는다.

## 1. 검증에 사용한 실제 설계 범위

`prototype-v4/hardware/INTERFACE-DESIGN.md`의 eDP RX → 전원형 HDMI 분배기 → 원 LCD 컨트롤러와 UVC 캡처 → Pi/Linux 호스트 경로를 기준으로 했다. 여기에 GPIO 보드, 별도 전원, HDMI/eDP/USB/FFC 선재 및 고정물을 빠뜨리지 않았다. 그러나 v4 BOM은 **구매가 확정된 조립품 목록이 아니라 후보 표**다. 아래 박스 검사는 보드/케이스 제조사가 치수를 공개한 부품만 계산하며, 서로 다른 물체를 실제로 한 번에 배치했다는 뜻이 아니다.

| 후보 | 제조사 확인 외형 | 확인 범위 | C03 이상적 단품 높이 여유 | CAD v5 단품 높이 여유 |
|---|---:|---|---:|---:|
| [Waveshare 1→4 HDMI splitter](https://www.waveshare.com/img/devkit/accBoard/HDMI-SPLITTER-1IN-4OUT/HDMI-SPLITTER-1IN-4OUT-details-size.jpg) | 83.69×57.40×13.98 mm | 케이스, HDMI/전원 플러그 제외 | **−3.25 mm** | **−5.25 mm** |
| [Waveshare USB3 UVC capture](https://www.waveshare.com/img/devkit/accBoard/HDMI-to-USB-Adapter/HDMI-to-USB3.0-Adapter-details-size.jpg) | 65.95×25.30×12.65 | USB-A 돌출부 포함, HDMI/호스트 연결 제외 | +0.47 mm | **−1.53 mm** |
| [VSLCD VS-RTD2556HM-V1](https://www.vslcd.com/D000079-30Pin-EDP-Micro-Lcd-Driver-Board.html) | 82×60×5 | **맨 PCB만**. 12V 전원·mini HDMI·패널 FFC·OSD 제외 | +5.54 mm | +3.54 mm (조립 합격 아님) |
| [Geekworm/Seenku eDP RX](https://wiki.geekworm.com/images/9/9d/S.EDP-HDMI-4K2K.V1.2-Specifications.pdf) | **43.03×57.05 mm** | 제조사 기구도 PCB 외곽. 완성품 Z/HDMI·FFC 돌출 미제공 | 미판정 | 미판정 |
| [Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) | **65×30 mm** | 보드 XY만. USB 전원·OTG·헤더·microSD 돌출 미포함 | 미판정 | 미판정 |
| v4 GPIO 보드 | 40×35 mm | PCB XY만. LED/스위치/헤더 높이 미포함 | 미판정 | 미판정 |
| 전원 변환·케이블·고정부 | SKU 미선정 | 최대 외형·발열·굽힘 반경·출구 미확정 | 미판정 | 미판정 |

계산은 각 박스를 가장 유리한 후방 Y=0에 놓고 X/Y 90° 회전 둘 다 검사했다. 실제 C03 내부는 Y≈1부터 시작하므로 이는 **낙관적 상한**이다. [재현 코드](assembly_envelope_sim.py), [JSON 입력/출력](v4-assembly-sim-results.json), [높이 그림](v4-envelope-screen.png). 슬로프는 16/215 mm/mm, 내부 높이는 C03 이상적 `15−16y/215`, CAD v5 `13−16y/215` mm. 실제 v5 STL 중앙 수직선 4곳에서 바닥 Z=3/5, 천장 Z=`18−16y/215`/`20−16y/215`를 **최대 0.005 mm 이내**로 재확인했다(메시 수치 반올림 포함).

현재 Waveshare 분배기의 높이만 통과하려면 후방 유효 높이가 **최소 18.25 mm**여야 한다(케이스·직교 배치, 플러그와 여유 0). C03 이상적 15 mm보다 3.25 mm 크다. CAD v5와의 겹침을 선형 지붕/직육면체로 적분하면 **약 14,968 mm³**다. USB3 캡처는 CAD에서 약 **1,041 mm³** 겹친다. 실제 플라스틱 불리언 겹침 부피가 아니라, 내부 지붕면에 대한 낙관적 박스 침입 하한이다. 세부 커넥터/전원 추가는 결과를 개선하지 않는다.

별도로 [원본 파라메트릭 CAD와 박스의 불리언 교차](v5_box_interference.scad)도 실행했다. 분배기와 USB3 박스를 서로 겹치지 않게 후방 X에 두고, 바닥/후방의 수치적 동면을 피하려 0.01 mm 이동한 연구 배치다. [닫힌 교차 STL의 부피 검사](v5-boolean-clash-results.json)에서 프린트 플라스틱과 **분배기 10,288 mm³**, **USB3 캡처 2,807 mm³**가 겹친다. 두 교차 메시 모두 열린 모서리 0이다. 이 값은 **플라스틱과 겹친 부분만** 세므로 위 내부 천장 초과량과 같을 필요가 없고, 지붕 바깥의 노트북 부품과의 추가 충돌은 포함하지 않는다. 위치를 바꿔도 위의 독립 최선 높이 불합격 판정은 변하지 않는다.

추가로 치수가 공개된 [Erard 7970 1→2](https://www.erard.com/en/repartiteurs/891-repartiteur-hdmi-1-vers-2-full-hd.html) 84×45×15와 [PROTECH 2PET0102D-C 1→2](https://www.protechet.com/products/2pet0102d-c) 65.5×55.5×16은 C03 이상적 높이에서도 각각 **−3.35, −5.13 mm**다. 현재 검증한 케이스형 후보 3종의 불합격이지 모든 시장 제품의 불가능 증명은 아니다. 케이스를 임의로 제거한 회로는 높이·절연·EMI·전기 성능이 전부 새 검증 대상이다.

**조건부로 더 나은 1→2 후보를 찾았다.** 제조사 [Goobay/Wentronic 58480](https://www.wentronic.com/en/hdmi-splitter-1-to-2-58480)은 케이스 **65×64.8×7.45 mm**, 1080p60 지원으로 현 CAD의 케이스 단독 높이 여유가 **+0.73 mm**다. [제조사 2쪽 기구도](../01-research/source-pdfs/wentronic-58480-product-datasheet.pdf)는 HDMI 입력+5V Micro-USB가 한 면, 출력 HDMI 2개가 반대 면에 있음을 보여 준다. [DIGITUS DS-45322](https://products.digitus.com/AV-medijska-tehnologija/AV-razdjelnik/Ultra-Slim-HDMI-Splitter-1x2-4K-60-Hz.html) **83×40×9 mm**는 케이스 단독 **+1.02 mm**다. 이 두 값은 3개 HDMI 플러그·전원 플러그·고정/절연 여유가 **모두 빠진 상태**다. Wentronic은 높이가 그대로라고 가정해도 앞뒤 커넥터가 차지할 수 있는 추가 Y의 합계가 **9.8 mm 미만**, DIGITUS는 **13.7 mm 미만**이어야 한다(후방 Y=0이라는 낙관적 배치). 표준 케이블을 꽂은 실제 외형이 이 조건을 만족하는지 아직 자료가 없어 **수납 합격으로 승격하지 않는다.**

[Waveshare USB2 버전](https://www.waveshare.com/product/hdmi-to-usb-adapter.htm)은 공식 사양상 1080p30 출력 후보라 USB3 부품 교체 가능성을 검토할 가치는 있다. 다만 제조사에서 **완성 높이·플러그 결합 외형**을 확인하지 못해 현재는 수납 통과 후보가 아니다. [제조사 문의 초안](../06-order/COMPONENT-DIMENSION-RFQ-ko.md)에 필요한 질문을 정리했다.

## 2. 나사와 고정 340-mm 쐐기 폭의 충돌 및 CAD 수정

Dell 가이드 참조 중간/앞 측면 나사 좌우 축 간 거리는 **337.30 mm**다. 수직의 완전한 Ø7 드라이버 우물 2개를 모두 쐐기 안에 넣으려면 최소 **344.30 mm**, Ø4.6 머리 자리만 계산해도 **341.90 mm** 폭이 필요해 고정 340 mm와 양립하지 않는다. 단순히 쐐기를 좌우로 이동하는 방식은 해결책이 아니다.

[`base_cover.scad`](../04-cad/base_cover.scad)의 CAD 개정 v5에서는 나사 5곳의 쐐기 가장자리를 반경 6 mm로 **안쪽으로 파내고**, 그 주위에 2 mm 연구용 링벽을 두며, OEM 높이의 좌면 섬을 남겼다. 쐐기의 최대 X/Y 외곽은 340×215로 유지한다. [XY 기준/홈 위치](v5-interface-plan.png) 및 [v5 미리보기](../04-cad/preview_research_226p2mm_v5.png). OpenSCAD CGAL 렌더 성공, [v5 STL](../04-cad/base_cover_research_226p2mm_v5.stl) 8,368 삼각형·연결 성분 1·열린/비다양체 모서리 0, 전체 외곽 355.32×226.20×28.47 mm(상부 클립 포함). Dell 가이드와 XY 윤곽 IoU 0.997320로 유지된다. **링벽의 체결 강도, 좌면 접촉, 스크루드라이버 실제 삽입각, 먼지/EMI 밀폐는 미검증**이다.

## 3. 열 민감도 계산 — 실제 온도 예측이 아님

[3시간 열 시나리오 그림](v4-thermal-sensitivity.png)은 `T(t)=25°C+Q·Rθ·(1−e^(−t/τ))`라는 단일 열용량 RC 모델에서 **Q=3/6/10 W, Rθ=2/5/10 K/W, τ=1 h를 임의로 넣은 것**이다. 예로 Q=6 W·Rθ=5 K/W이면 3시간 값은 53.5°C, Q=10 W·Rθ=10 K/W이면 120°C다. 이 큰 차이가 의미하는 것은 **실측 발열·흡기 유량·열저항 없이는 결론이 매우 민감하다**는 점이다. 이 값은 노트북 CPU, 배터리, PA12, 개별 모듈의 온도 예측이 아니며 3시간 안전 인증으로 사용하지 않는다. [Raspberry Pi 공식 사양](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)과 [VSLCD 페이지](https://www.vslcd.com/D000079-30Pin-EDP-Micro-Lcd-Driver-Board.html)의 전원 정격도 소비전력/열원 실측값이 아니다.

## 4. 여전히 컴퓨터 안에서 확정할 수 없는 항목

- Dell 웹 모델은 수리 안내용 경량 메시다. 하판의 실제 후크·내부 곡면·좌면 Z·상대 팜레스트 공차와 열/흡기 유로를 제공하지 않는다. 그래서 **실물 노트북 결합 시뮬레이션**을 완료했다고 할 수 없다. 외곽 XY 중첩과 STL 단면 검사는 그 일부만 검증한다.
- v4 회로의 eDP 패널 suffix/하네스 핀맵·RX revision/EDID/HPD, LCD 컨트롤러의 패널 적합성, 최종 전원 경로는 전자적 설계 게이트다. 하판 CAD가 맞아도 시스템이 동작한다는 근거가 되지 않는다.
- 구리 테이프는 무차별 부착하면 단락 위험이 있으며, 기존 순정 차폐/개스킷의 접촉 경로를 대신한다고 증명되지 않았다. 프린트 재료는 검정 PA12 SLS/MJF를 후보로 유지하되 특정 업체·grade·후처리의 물성/공차 인증은 없다.

**다음 설계 결정:** C03 외형을 고정하고 prototype-v4 전체를 내부에 넣으려면 지금의 Waveshare 1→4 분배기와 USB3 캡처를 그대로 쓸 수 없다. Wentronic/DIGITUS 분배기와 USB2 캡처는 조사할 **조건부 대체 후보**지만, 플러그 포함 실장 높이·영상/EDID·전원·발열 검증이 선행돼야 한다. 모델 안에 임의의 얇은 가상 부품을 넣어 수납 통과로 표시하지 않는다.
