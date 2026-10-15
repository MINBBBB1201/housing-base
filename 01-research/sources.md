# S1–S2 리서치 기록 (2026-09-24)

표기: **[확인]** 1차 자료로 확인 · **[추정]** 사진·정황 기반 추정 (근거 명시)

스크린샷: Dell 사이트는 봇 차단(Akamai) 때문에 헤드리스 저장이 막혀서 `screenshots/`에 파일로 남기지 못했다. 앱 내장 브라우저로 본 화면은 세션 기록에 있다. 아래 URL은 브라우저로 직접 열면 동일하게 보인다.

## 1. 기종·원구성 [확인]

- 사용자 장치 확인 → **Inspiron 15 3525** (Dell 지원 페이지, 실제 장치 식별값은 비공개)
- 출하 구성: Ryzen 5 5625U, **3셀 41 Wh (451-BCWW)**, 256 GB M.2 PCIe NVMe (400-BNIT), 8 GB x1 DDR4, **카본 블랙 (320-BEPX)**, 지문인식 팜레스트 (346-BHYE), 65 W 어댑터 (450-AKPP), Realtek RTL8821CE, FHD 120 Hz
- 2.5인치 HDD는 **출하 구성에 없음**. 사진 [02]의 좌하단 검은 블록 정체는 미확인 (HDD 자리 더미 또는 다른 부품) → 실물 확인 필요
- 규제 라벨: Reg Model P112F, Reg Type P112F006

## 2. 치수 [확인]

출처: Setup and Specifications › Dimensions and weight
https://www.dell.com/support/manuals/en-us/inspiron-15-3525-laptop/inspiron15_3525_ss/dimensions-and-weight?guid=guid-45764026-1a5d-4d14-8308-799f4d102bc7&lang=en-us

| 항목 | 플라스틱 | 알루미늄 |
|---|---|---|
| 앞 높이 | 16.96 | 15.52 |
| 뒤 높이 | 19.00 | 17.50 |
| 폭 | 358.50 | 358.50 |
| 깊이 | 235.60 | 234.90 |

→ **본체를 닫은 상태의 전체 치수**다. 하판 단품 곡면이나 하판 외곽을 직접 알려주지 않는다. 사용자 실측 G3 "36 cm 살짝 안 됨"과 폭이 일치.

## 3. 하판 분리·조립 [확인]

출처: Service Manual › Removing / Installing the base cover, Screw list
- 분리: https://www.dell.com/support/manuals/en-us/inspiron-15-3525-laptop/inspiron15_3525_sm/removing-the-base-cover?guid=guid-ffdf7928-28fa-40bc-9790-8145e722491d&lang=en-us
- 조립: https://www.dell.com/support/manuals/en-us/inspiron-15-3525-laptop/inspiron15_3525_sm/installing-the-base-cover?guid=guid-0ff030a7-688a-45d0-9985-bcb38747ca1a&lang=en-us
- 나사 표: https://www.dell.com/support/manuals/en-us/inspiron-15-3525-laptop/inspiron15_3525_sm/screw-list?guid=guid-cc648b28-fbf9-4a6f-bb11-4c6c2fa3d08a&lang=en-us
- 도해 이미지 (dl.dell.com, 1650 px):
  - 1단계 나사 위치 `GUID-DCB17EEE-8EEF-481B-AAC7-5E018791F61C-low.jpg`
  - 2단계 들어올림 `GUID-3EA4A653-E2DC-42A7-A7E6-A4AC18A5D918-low.jpg`
  - 조립 1단계 (하판 없는 내부) `GUID-5DFD7F77-AD3F-4BA1-B4B8-28DB7D9BDB02-low.jpg`
  - 조립 2단계 스냅 `GUID-960DC06A-E405-4B6B-BE94-037051497A37-low.jpg`
  - 주요 부품 분해도 `GUID-CE51BE75-F8DB-4D05-AEA9-65AC42BCB57F-low.jpg`
  - 경로 접두사: `https://dl.dell.com/content/guides/public/Html/inspiron15_3525_sm/images/`

내용:
- **M2×5 6개 + captive 2개**. 하판에 고정되는 나사는 이것뿐 (나사 표 전체 확인).
- 나사 배치 (힌지를 위로 두고 바깥에서 본 도해 기준):
  - captive 2: 좌·우 **힌지 바로 바깥의 후방 모서리**
  - M2×5 6: **후방 중앙**(중심에서 약간 왼쪽), **좌·우 측면 중간**, **전방 좌·중·우**
- 분리: 후방 고무발 안쪽(힌지 옆)의 **U자 홈**에서 플라스틱 스크라이브로 들어 올린 뒤, 네 변을 바깥으로 벌려 클립 해제 → **외곽 전체에 스냅 클립**
- 조립: 배터리 케이블 연결 → 하판을 눌러 스냅 → captive 2개 조임 → M2×5 6개
- **나사 보스는 팜레스트 쪽에 있다** (조립 1단계 도해의 파란 링, 사용자 사진 [02]에도 같은 위치에 파란 링). → 새 하판에는 보스가 아니라 **관통 구멍 + 나사머리 카운터보어**가 필요하다.

## 4. 하판과 팜레스트의 역할 분담 [확인/추정]

- 분해도: 하판은 전방·좌우를 감싸는 **낮은 측벽이 있는 얕은 트레이** [확인]
- 하판 측벽에는 **포트 구멍이 보이지 않는다** [추정: 분해도 렌더 기준]
- 팜레스트는 측벽이 높고 **포트 구멍과 후방 배기 그릴**이 그 벽에 있다 [확인: 분해도]
- 사용자 사진 [03]: USB-C 포트가 빨간 선(하판) 위쪽에 있음 → 일치
- → **새 하판에 포트 구멍은 필요 없을 가능성이 높다.** 단 DC 플러그와 USB 플러그 몸체가 하판 가장자리에 닿는지는 실측 필요 (FLAWS F10)

## 5. 부품번호와 호환 [확인: 복수 판매처 일치]

- **DP/N 3JRFX / 03JRFX**, 제조사 P/N **AP3LE000301**
- 호환: Inspiron 15 3510 / 3511 / 3515 / 3520 / **3525** / 3530 (Amazon, eBay, Newegg, parts-people, thinkparts 표기)
- 기존 BOM C1 (`../../hardware/BOM.md`)의 부품번호와 일치 → **F8 해소**
- 한 판매처(Deal4GO, Newegg)가 **"W/O Copper Foil"** 버전을 별도 판매 → OEM 내부에 금속 박이 붙어 있다는 정황

## 6. 하판 실물 사진 (중고 OEM, gotlaptopparts.com, eBay 이미지 1600×1200)

상품: https://www.gotlaptopparts.com/products/dell-inspiron-15-6-15-3520-oem-laptop-bottom-case-base-cover-3jrfx-ap3le000301
- 내부 전체: `https://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/n3kAAOSwa4xk-sEP/$_57.JPG`
- 외부 정면: `.../z/J58AAOSwRSlk-sEP/$_57.JPG`
- 외부 비스듬히: `.../z/XJ8AAOSwOYFk-sEP/$_57.JPG`
- 라벨 근접: `.../z/tQ0AAOSwqmxk-sEQ/$_57.JPG`

관찰:
- 라벨: CN-03JRFX, AP3LE000301, **2022/11/17 제조**, 선별 A16 [확인]
- **외곽이 직사각형이 아니다**: 후방에서 두 힌지 사이 중앙부가 뒤로 더 나오고, 힌지 자리는 계단형으로 파여 있다 [확인]
- **내부면 거의 전체에 은색 금속 박** (도전성 천 또는 알루미늄 박) [확인: 사진]. 용도는 EMI 차폐 또는 열 확산 [추정]
- 후방 흡기 그릴 구간은 **검은 시트(마일라 추정)**로 덮여 있고 **팬 위치 부분만 개방** [확인: 사진]. 외부 사진에서도 그릴의 한쪽 일부만 속이 비침 → 실제 흡기 면적은 그릴 전체의 약 1/3 [추정]
- 개방된 흡기부 둘레에 **리브(개스킷/덕트 자리 추정)**
- 좌우 측면 슬롯 안쪽에 **검은 패드** (스피커 개스킷 추정)
- 외곽 가장자리를 따라 **클립 후크**가 일정 간격으로 배치
- 앞 가장자리 한쪽에 **금속 보강 레일**(나사 구멍 포함)
- 한쪽 구역에 **격자형 지지 리브**, 곳곳에 작은 보스와 핀, 긴 슬롯형 리브

## 7. 공개 CAD/STL

- Thingiverse "inspiron 3520": 결과 없음
- Printables: Cloudflare 보안 확인 페이지 → 확인하지 못함 (사용자가 직접 열어보면 확인 가능)
- 결론: 현재 조사에서 **치수와 공차가 있는 제작용 하판/상대 팜레스트 CAD를 확보하지 못했다.** 검색에서 나오지 않았다는 사실을 공개 CAD가 전혀 없다는 단정으로 바꾸지 않는다. [2026-09-25 사진 대체모델 기록](../05-verify/SURROGATE-SIM-2026-09-25.md)

## 8. 아직 못 본 자료

- Dell **3D Guides**: [Inspiron 3525 UMA 팜레스트/키보드 교체](https://www.dell.com/support/resources/en-us/3dviewer/cb040153525002701b/how-to-replace-the-palm-rest-and-keyboard-on-a-inspiron-3525-uma) — 2026-09-25 브라우저에서 3D 장면과 하판 분리 절차 확인. **치수·공차·STEP 다운로드 확인되지 않음**; 제조 CAD의 대체물이 아님.
- 분해 영상 (Dell 공식 "팬 교체" 등 1분 영상) — 클립 해제 순서 확인용

## 9. 2026-09-25 추가 부품·기구 자료

- 사용자 분리 하판 내부 사진 `00-input/photos/05-own-cover-interior.jpg` 라벨 `AP3LE000301` + [3525용 판매 페이지](https://www.gotlaptopparts.com/products/dell-inspiron-15-6-15-3525-genuine-bottom-case-base-cover-3jrfx-ap3le000301)의 `3JRFX/AP3LE000301`: 부품 식별 교차 확인. 판매 설명은 Dell 제조 치수도면이 아니다.
- [Raspberry Pi Zero 2 W 공식 기구도](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf): 보드 외곽 65×30 mm, 완성 케이블 조립체 외곽은 미제공.
- [VSLCD 30핀 eDP 컨트롤러 후보](https://www.vslcd.com/D000079-30Pin-EDP-Micro-Lcd-Driver-Board.html): 보드 82×60×5 mm, 입력 12 V/2 A 이상. Dell 실물 패널용 확정 제품이 아님.
