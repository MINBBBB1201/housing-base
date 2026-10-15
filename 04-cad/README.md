# 04-cad — 교체 하판 연구 모델 (2026-09-25, 발주 금지)

2026-09-26 재검토: Dell의 [Inspiron 3525 공식 3D 수리 가이드](https://www.dell.com/support/product-details/en-us/product/inspiron-15-3525-laptop/resources/3dguides)에서 추출한 경량 메시를 참조해 `params.scad`의 연구 외곽을 **355.32×226.20 mm**로, 힌지 노치·나사 XY를 해당 모델값으로 교체했다. 사용자 자 측정(폭 약 355, 깊이 약 227)과 부합한다. 이는 **공차가 없는 웹 가이드용 메시**이므로 제조용 체결 치수로 승인한 것이 아니다. OEM 나사 자리 홈 깊이 약 **1.7 mm** 역시 자 측정이다. 기존 `base_cover.stl`과 미리보기는 더 오래된 233 mm/1.9 mm 출력이므로 사용·발주하지 않는다.

**후속 연구 수정:** `base_cover.scad`의 내부 차집합 천장을 외부보다 2 mm 낮추고 빈 공간이 전방으로 무한히 이어지지 않게 제한해 중앙 지붕을 만들었다. v1 메시의 두 번째 경계는 분리된 플라스틱이 아니라 끝부분 **밀폐 공동**으로 재판정했다. `y=150` 횡리브를 제거한 v2는 단일 연결 경계·열린 모서리 0이다. OEM 내부 곡면은 여전히 복제하지 않았다. [사진 대체모델/메시 검사](../05-verify/SURROGATE-SIM-2026-09-25.md)를 따른다.

**v3에서 드러난 추가 충돌:** 공식 웹 모델의 나사 XY를 반영하니 현재 7 mm 드라이버 우물 5곳이 C03 쐐기의 측면/전방 외곽을 가로지른다([수치 감사](../05-verify/OFFICIAL-3D-REFERENCE-AUDIT-2026-09-26.md)). STL의 watertight 판정은 기능적 수납·체결 합격이 아니다.

**v4 연구 수정:** v3에서는 중앙 쐐기가 뒤쪽 힌지 홈의 일부를 다시 메웠다. 최종 합집합을 자르는 `hinge_cut()`을 추가하고 v4 STL로 렌더했다. [공식 모델 대비 XY 오버레이](../05-verify/official-v4-plan-overlay.png)의 실루엣 일치도는 99.732%지만, 5개 나사 우물·OEM 내면·v4 부품 수납 미해결이므로 **여전히 발주 금지**다.

**v5 연구 수정:** 340 mm 외형 안에 가장자리 나사 5개의 완전한 원형 우물을 둘 수 없어, 쐐기에 국부적인 반경 6 mm 홈과 링벽을 만들고 OEM 높이 좌면 섬을 남겼다. [통합 수납·메시 검사](../05-verify/INTEGRATED-V4-SIM-2026-09-26.md)상 단일 닫힌 STL이지만, 실제 나사 강도·좌면 Z와 전자부품 수납은 미검증/불합격이다. **최신 v5도 발주 금지.**

**v6 사진 후크 반영 (2026-09-26):** 30 mm 균일 간격 추정 후크를 [사진 가상 스캔](../02-measure/virtual-scan/VIRTUAL-SCAN.md)으로 측정한 25개 위치(`params.scad` `clips_list`, 등급 A/B/C, 폭 상한 5 mm)로 교체했다. `use_measured_clips = false`면 이전 방식. 불확실한 후크 4개는 넣지 않았다(없는 후크는 조립을 막음). 위치 오차 ±1.5~3 mm, 걸림 턱 형상은 미측정. 나머지 v5 미해결 사항 그대로 → **v6도 발주 금지.**

**v7 긴급 수정 (2026-09-26):** v6의 바닥 흡기 슬롯은 쐐기 내부 공동으로만 이어지고 노트북 팬 쪽 지붕이 막혀 있었다. 사진 기반 실제 팬 개방부(참조 X219.8~276.5, Y24.2~54.4) 안쪽인 X223~274, Y25~52에 관통구를 뚫고 2 mm 두께의 내부 덕트벽으로 전자부품 공동과 분리했다. 바닥 슬롯 약 810 mm², 위쪽 개구부 1377 mm²는 **명목 기하 면적**일 뿐 풍량이 아니다. [v7 광선·메시 검사](../05-verify/v7-airpath-results.json)는 통로 존재와 닫힌 단일 메시만 확인했다. [긴급 발주 판단](../06-order/URGENT-2H-HANDOFF-ko.md)의 위험 조건을 따르며 **v7도 노트북 결합/열/v4 수납 승인 파일이 아니다.**

**v10 치수 대조 반영 (2026-09-26, 최신):** [치수 대조](../05-verify/final-sim/DIM-CHECK-2026-09-26.md)에서 **설계 좌표(X 왼쪽→오른쪽, Y 힌지→앞, Z 위)가 왼손 좌표계**임을 확인했다. v9까지의 STL은 출력하면 좌우 거울상(흡기 그릴·eDP 통로·DC 구멍이 반대편)이다. `base_cover.scad` 기본 출력을 `print_frame = true`(x → 355.32 − x, 실물 방향)로 바꿨다. 시뮬레이션용 설계 좌표 STL만 `-D print_frame=false`로 만든다. 0.2 mm 정밀 격자 재검사에서 드러난 후크 2개 충돌(앞 X261 스피커 3.5 mm, 왼쪽 Y95.7 메인보드 2.7 mm)을 제거해 13개가 남았다. 힌지 홈 깊이는 순정 11.77에 맞췄다. 외곽·나사 8개·힌지 홈 X는 순정 메시와 0.01 mm 이내다. 뒤 모서리는 순정 직각 대신 R6을 유지했다(직각이면 팜레스트와 더 겹침). [v10 기하 검사](../05-verify/v10-check-results.json) 통과. **발주 파일 = `dell3525_basecover_v10_PRINT_*.stl`.**

**v9 최종 적합 시뮬레이션 반영 (2026-09-26, v10으로 대체 — v9 STL은 거울상, 발주 금지):** Dell 3D 조립 모델 내부 부품 20개 그룹과의 간섭 시뮬레이션([보고서](../05-verify/final-sim/FINAL-SIM-2026-09-26.md))에서 v8 둘레 벽(6 mm 일정)이 포트·팜레스트·힌지에 2~5 mm 파고드는 것을 확인하고 고쳤다: 벽 높이 = 순정 프로파일 − 0.2 mm, 후크 끝 = 순정 벽 + 3.06 mm, 부품과 충돌하는 후크 10개 제거(15개 유지), 힌지 홈 둘레 벽 제거, 좌우 아래 모서리 3.2 mm 모따기, 나사별 머리 자리·받침 높이(`screw_spec`: 뒤 M2×8, 앞 M2×6, 옆 순정 M2×5), 뚜껑은 **나사 없는 스냅 6개**(인서트 없음, 선택용 자가태핑 구멍), GPIO 버튼 Ø3.8·LED Ø3.1. 결과: 모든 내부 부품과의 겹침이 순정 하판 이하(후크 끝 1.39 mm는 모델에 걸림 홈 없음). [v9 기하 검사](../05-verify/v9-check-results.json) 통과. **여전히 실물 결합·열 검증 전.** 조립 재료·4일 일정: [ASSEMBLY-BOM-ko.md](../06-order/ASSEMBLY-BOM-ko.md).

**v8 정비 뚜껑·배선 통로 (2026-09-26, v9로 대체):** v7의 전자부품 공동은 바닥·지붕이 한 몸인 **닫힌 상자**라 보드 삽입·배선·분말 제거가 불가능했다. 쐐기 바닥을 M2×6 나사 10개 **뚜껑**으로 분리(본체 기둥 10개, M2 열압입 인서트 Ø3.2×4)하고, 팬 덕트·뒤 나사 우물·가장자리 나사 섬은 본체에 남겼다. C03 제안 왼쪽 DC/버튼/LED 구멍, 왼쪽 케이블 창·환기, 지붕 eDP 통로, 리브 배선 홈을 추가했다. 노트북 나사 구멍은 Ø2.8 + X 장공 + M2 와셔 자리(Ø5.4)로 PA12 수축을 흡수한다. `split_lid`/`v8_openings = false`면 v7 형상. [v8 검사](../05-verify/v8-check-results.json): 두 부품 각각 닫힌 단일 메시, 본체∩뚜껑 빈 집합. 공동 높이·후크 걸림·좌면 Z·열은 v7과 같이 미검증 → **완제품 승인 아님**, 발주 조건은 [긴급 판단](../06-order/URGENT-2H-HANDOFF-ko.md).

| 파일 | 내용 |
|---|---|
| [params.scad](params.scad) | **모든 치수 + 출처 태그.** 실측값은 여기만 고친다 |
| [dell3525_basecover_v10_PRINT_body.stl](dell3525_basecover_v10_PRINT_body.stl) | **v10 본체 — 발주 파일 (실물 방향).** 12,768 삼각형, 열린 모서리 0, 연결 덩어리 1, 355.32×226.20×27.25 |
| [dell3525_basecover_v10_PRINT_lid.stl](dell3525_basecover_v10_PRINT_lid.stl) | **v10 스냅 뚜껑 — 발주 파일 (실물 방향).** 3,332 삼각형, 337.2×122.3×10.0 |
| [base_cover_research_226p2mm_v10_body.stl](base_cover_research_226p2mm_v10_body.stl) / [_lid](base_cover_research_226p2mm_v10_lid.stl) | v10 설계 좌표 (시뮬레이션 전용, **출력 금지** — 거울상) |
| [preview_v10_top.png](preview_v10_top.png) / [preview_v10_exploded_bottom.png](preview_v10_exploded_bottom.png) | v10 PRINT 미리보기 (`preview_v10.scad`). top = 키보드 쪽에서 내려다본 정상 자세 |
| [base_cover_research_226p2mm_v9_body.stl](base_cover_research_226p2mm_v9_body.stl) | v9 본체 (**거울상, 발주 금지**). 12,832 삼각형, 열린 모서리 0, 연결 덩어리 1, 355.32×226.20×27.25 |
| [base_cover_research_226p2mm_v9_lid.stl](base_cover_research_226p2mm_v9_lid.stl) | v9 스냅 뚜껑 (**거울상, 발주 금지**). 3,332 삼각형, 열린 모서리 0, 연결 덩어리 1, 337.2×122.3×10.0 |
| [preview_v9_exploded_bottom.png](preview_v9_exploded_bottom.png) / [preview_v9_top.png](preview_v9_top.png) / [preview_v9_left_side.png](preview_v9_left_side.png) | v9 미리보기 (`preview_v9.scad`). 제작 승인 이미지 아님 |
| [base_cover_research_226p2mm_v8_body.stl](base_cover_research_226p2mm_v8_body.stl) | v8 본체 (v9로 대체, 노트북에 닫히지 않음). 12,100 삼각형, 열린 모서리 0, 연결 덩어리 1, 355.32×226.20×28.47 |
| [base_cover_research_226p2mm_v8_lid.stl](base_cover_research_226p2mm_v8_lid.stl) | **v8 정비 뚜껑.** 3,132 삼각형, 열린 모서리 0, 연결 덩어리 1, 335.4×121.4×5 |
| [preview_v8_exploded_bottom.png](preview_v8_exploded_bottom.png) / [preview_v8_top.png](preview_v8_top.png) / [preview_v8_left_side.png](preview_v8_left_side.png) | v8 미리보기 (`preview_v8.scad`로 STL을 불러와 렌더). 제작 승인 이미지 아님 |
| [base_cover_research_226p2mm_v6_photoclips.stl](base_cover_research_226p2mm_v6_photoclips.stl) | v5 + 사진 측정 후크 25개. 8,304 삼각형, 열린 모서리 0, 연결 덩어리 1. **발주 금지** |
| [preview_research_226p2mm_v6_photoclips.png](preview_research_226p2mm_v6_photoclips.png) | v6 미리보기 (제작 승인 이미지 아님) |
| [base_cover_research_226p2mm_v7_fan_duct.stl](base_cover_research_226p2mm_v7_fan_duct.stl) | v6 + 팬 관통 덕트. 8,316 삼각형, 열린 모서리 0, 연결 덩어리 1. **연구/긴급 시제품 전용, 완제품 승인 아님** |
| [preview_research_226p2mm_v7_fan_duct.png](preview_research_226p2mm_v7_fan_duct.png) | 노트북 쪽 면의 팬 개구부 미리보기 |
| [base_cover.scad](base_cover.scad) | 형상 (OEM 둘레 + C03 쐐기 통합) |
| base_cover.stl | 과거 연구 출력(233 mm / 1.9 mm). **현 파라미터와 불일치·발주 금지** |
| base_cover_research_227mm.stl | 227 mm/1.7 mm v1 연구 렌더. **밀폐 공동에 분말이 갇힐 수 있어 발주 금지** |
| base_cover_research_227mm_v2.stl | 227 mm/1.7 mm v2 연구 렌더. 밀폐 공동 해소, OEM 내면·v4 수납 미검증으로 **발주 금지** |
| base_cover_research_226p2mm_v3.stl | Dell 가이드 참조 외곽·나사 XY·힌지 노치를 적용한 v3 연구 렌더. 단일 연결 경계, 열린 모서리 0. **발주 금지** |
| [base_cover_research_226p2mm_v4.stl](base_cover_research_226p2mm_v4.stl) | 힌지 홈 재메움 오류를 고친 이전 연구 렌더. 7,536 삼각형, 단일 연결 경계, 열린 모서리 0. **발주 금지** |
| [base_cover_research_226p2mm_v5.stl](base_cover_research_226p2mm_v5.stl) | 가장자리 나사 5곳의 쐐기 홈을 만든 현 연구 렌더. 8,368 삼각형, 단일 연결 경계, 열린 모서리 0. **발주 금지** |
| [preview_research_226p2mm_v5.png](preview_research_226p2mm_v5.png) | v5 미리보기 (제작 승인 이미지 아님) |
| [preview_research_226p2mm_v5_bottom.png](preview_research_226p2mm_v5_bottom.png) | v5 외부 바닥면 미리보기 (제작 승인 이미지 아님) |
| [preview_research_226p2mm_v4.png](preview_research_226p2mm_v4.png) | v4 미리보기 (제작 승인 이미지 아님) |
| preview_research_226p2mm_v3.png | v3 상면 미리보기 (제작 승인 이미지 아님) |
| preview_research_227mm_v2.png | v2 상면 미리보기 (제작 승인 이미지 아님) |
| preview_top.png / preview_bottom.png | 미리보기 |
| section.scad | 단면 확인용 |

주의: params.scad / base_cover.scad를 PowerShell `Set-Content -Encoding utf8`로 저장하면 BOM이 붙어 OpenSCAD가 읽지 못한다. 편집기나 UTF-8(BOM 없음)으로 저장.

## 과거 rev1.1 기록의 효력

과거 출력은 358.5 × 233.0 mm, 나사 홈 1.9 mm, 사진 추정 32개 클립으로 만들었다. 과거 STL 수직선 검사에서는 일부 나사 구멍이 관통했고 단일 연결 형상이었다. 그러나 **중앙 상판이 제거되는 결함과 OEM 내부 곡면 불일치**가 뒤늦게 확인되어 이 결과를 조립 검증으로 사용하지 않는다. 과거 약 204 g / 316위안 계산도 최종 물량·견적이 아니다. 227 mm v1의 밀폐 공동 문제는 v2에서 해소했고, 226.20 mm v3는 Dell 웹 모델 참조 좌표를 반영했다. 두 연구 메시 모두 조립/수납 검증 전이므로 발주 금지다.

## 아직 확정 안 된 것 (params `[MEAS]`)

| 변수 | 무엇 | 어떻게 확정 |
|---|---|---|
| `W`, `D`, `hinge_notches`, `screws` | Dell 3D 가이드 경량 메시 참조값 | 실물 하판·상대 팜레스트 스캔 및 비통전 시험 체결로 제조값 확인 |
| `clip_*`, `clips_list` | 클립 높이 약 7 mm, 위치는 사진 가상 스캔(±1.5~3) | 걸림 턱·팔 두께는 순정 하판 대조(SLA 시험 출력) 필요 |
| `t_oem`, `lip_h` | OEM 판 두께, 둘레 벽 높이 | 자로 대략, 또는 SLA 맞춤 출력 |
| `seat_t` | 나사머리 자리 위 재료 두께 | SLA 맞춤 출력으로 확인 (두꺼우면 하판이 덜 닫힘) |
| `R_corner` | 모서리 둥글기 | 대략이면 충분 |
| captive 고정, 도전 개스킷 | D1-C8, C9 | 부자재로 해결 (TAOBAO-KEYWORDS.md) |

`cbore_depth`의 약 1.7 mm도 자 측정값이다. 이전 임의의 1.9 mm는 폐기했고, OEM 나사의 실제 머리 형상·좌면 두께·물림 길이는 확인되지 않았다. **원본 하판 또는 예비 하판을 3D 스캔하고 외주가 비통전 결합 지그에서 조립성을 검수하기 전에는 최종 CAD/STEP/STL을 승인하지 않는다.**
