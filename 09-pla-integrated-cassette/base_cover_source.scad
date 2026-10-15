// Inspiron 15 3525 FDM/PLA integrated-cassette candidate.
// OEM-facing shell is retained from v10.1; only blind cassette anchors and a
// service-lid cable slot are added. Geometry is not a real-machine fit proof.
include <params.scad>

$fn = 32;
b = (h_rear - h_front) / wedge_d;   // 경사 (mm/mm)
a = h_rear + b * wy0;               // y=0에서의 OEM 체결면 높이
function zp(y) = a - b * y;         // OEM 하판 바닥면(=체결면) 높이

// 경사면을 따르는 판: 두께 t, 체결면 아래로
module sloped(x0, y0, w, d, t, up = 0) {
    multmatrix([[1,0,0,0],[0,1,0,0],[0,-b,1,a]])
        translate([x0, y0, -t + up]) cube([w, d, t]);
}

// v10: 순정처럼 뒤 모서리 직각(R_corner_rear), 앞 모서리 R_corner
module plan2d() {
    hull() {
        for (x = [R_corner_rear, W - R_corner_rear]) translate([x, R_corner_rear])
            if (R_corner_rear > 0) circle(R_corner_rear); else square(0.01, center = true);
        for (x = [R_corner, W - R_corner]) translate([x, D - R_corner]) circle(R_corner);
    }
}
module outline2d() {
    difference() {
        plan2d();
        for (n = hinge_notches) translate([n[0], -1]) square([n[1] - n[0], hinge_notch_d + 1]);
    }
}

// 1) 둘레 판 + 측벽 (OEM 인터페이스 영역)
// v9: 벽 윗면 = zp + 순정 벽 높이(y) − wall_clear. 높이는 y에만 의존 → Y-Z 단면을 X로 밀어낸 절단체로 자른다.
function wall_H(y) = let(s = lookup(y, oem_wall_side))
    y < 3 ? min(s, oem_wall_rear) : (y > D - 3 ? min(s, oem_wall_front) : s);   // v10 검토: 앞 벽을 순정 8.74 − 0.2로 올리면 팜레스트·스피커 겹침 증가 → v9 그대로(순정보다 약 0.4 낮음)
module wall_cap() {
    pts = concat([for (y = [-2 : 1 : D + 2]) [y, zp(max(0, min(D, y))) + wall_H(max(0, min(D, y))) - wall_clear]],
                 [[D + 2, -30], [-2, -30]]);
    translate([-10, 0, 0]) rotate([90, 0, 90]) linear_extrude(W + 20) polygon(pts);   // 2D (u=y, v=z) → 3D (X 압출, Y=u, Z=v)
}
module outline2d_nonotch() { plan2d(); }
module rim_walls() {
    difference() {
        sloped(0, 0, W, D, use_oem_wall_profile ? 14 : lip_h, use_oem_wall_profile ? 14 : lip_h);
        // notch_walls = false: 벽은 바깥 둘레에만. 홈은 나중에 hinge_cut()이 판째 잘라 낸다
        translate([0,0,-50]) linear_extrude(200) offset(delta = -wall) if (notch_walls) outline2d(); else outline2d_nonotch();
    }
}
// v9: 좌우 바깥 아래 모서리 45° 모따기 (x ≤ side_chamfer 구간에서 z − zp < side_chamfer − x 제거)
module side_edge_chamfer() {
    c = side_chamfer;
    for (m = [0, 1]) translate([m * W, 0, 0]) mirror([m, 0, 0])
        multmatrix([[1,0,0,0],[0,1,0,0],[0,-b,1,a]])
            translate([0, side_feature_y, 0]) rotate([90, 0, 0]) linear_extrude(side_feature_y + 5)   // v10: 포트 구간만 (y ≤ side_feature_y)
                polygon([[-1, -2], [c + 2, -2], [-1, c + 1]]);
}
// v10 발주본: 좌우 벽 뿌리 보강. 3.2 mm 모따기 면이 2 mm 벽의 안쪽 아래 모서리를 정확히 지나
// 뒤쪽 옆벽(y 5~141)이 바닥판에 두께 0인 선으로만 붙어 있었다 → 좌우 벽만 안쪽으로 side_wall_t까지 두껍게.
module side_wall_root() {
    if (side_wall_t > wall && use_oem_wall_profile) intersection() {
        union() for (m = [0, 1]) translate([m * W, 0, 0]) mirror([m, 0, 0]) translate([-1, -1, -50]) cube([side_wall_t + 1, side_feature_y + 1, 200]);
        sloped(0, 0, W, D, 14, 14);
        wall_cap();
        translate([0, 0, -50]) linear_extrude(200) outline2d();
    }
}
module rim() {
    intersection() {
        union() {
            sloped(0, 0, W, D, wall, t_oem);                // 연구용 평면. OEM 곡면과 다르므로 동일한 안쪽 면이 아님
            if (use_oem_wall_profile) intersection() { rim_walls(); wall_cap(); } else rim_walls();
        }
        translate([0,0,-50]) linear_extrude(200) outline2d();
    }
}

// 2) 쐐기 속 빈 상자 (발 위 ~ 체결면)
module wedge_solid(inset = 0) {
    inner_d = inset > 0 ? cavity_end_local - inset : wedge_d - 2*inset;
    hull() {
        translate([wx0 + inset, wy0 + inset, foot_h + (inset > 0 ? floor_t : 0)])
            cube([wedge_w - 2*inset, inner_d, 0.01]);
        // 내부 차집합의 천장은 외부 상면보다 roof_t 낮아야 지붕이 남는다.
        sloped(wx0 + inset, wy0 + inset, wedge_w - 2*inset, inner_d, 0.01, inset > 0 ? -roof_t : 0);
    }
}

module wedge_shell() {
    difference() {
        wedge_solid(0);
        wedge_solid(wall);
        intake_slots();
        fan_roof_open();
        side_intake();
        screw_relief_cut();
    }
}

// The prior bottom slots opened only into the wedge cavity: the continuous
// upper roof still blocked the laptop fan. Open the roof at the photo-derived
// fan window. This is an AIR PATH hypothesis, not an airflow qualification.
module fan_roof_open() {
    translate([intake[0], intake[2], foot_h + floor_t + 0.02])
        cube([intake[1]-intake[0], intake[3]-intake[2], 65]);
}

// Separate the fan's bottom-to-top path from the electronics cavity. Kept
// entirely below the OEM-facing roof so no new boss protrudes into the laptop.
module fan_duct_wall() {
    intersection() {
        wedge_solid(0);
        difference() {
            translate([intake[0]-fan_duct_margin, intake[2]-fan_duct_margin, -1])
                cube([intake[1]-intake[0]+2*fan_duct_margin,
                      intake[3]-intake[2]+2*fan_duct_margin, 65]);
            translate([intake[0]-fan_duct_margin+fan_duct_wall_t,
                       intake[2]-fan_duct_margin+fan_duct_wall_t, -2])
                cube([intake[1]-intake[0]+2*(fan_duct_margin-fan_duct_wall_t),
                      intake[3]-intake[2]+2*(fan_duct_margin-fan_duct_wall_t), 67]);
        }
    }
}

module wedge() {
    wedge_shell();
    fan_duct_wall();
    // 사진 추정 지지 기둥 (OEM 안쪽 면 높이는 아직 미확정)
    for (p = posts) translate([p[0], p[1], foot_h]) cylinder(d = post_d, h = zp(p[1]) + t_oem - foot_h);
    // 연구용 횡리브. y=150 리브는 전방 끝의 밀폐 공동에 분말을 가두므로 제외.
    // 실제 강성 및 배출 경로는 제조사 DFM/시험 출력으로 다시 결정해야 한다.
    for (ry = [80]) intersection() {
        translate([wx0, ry - 0.6, foot_h]) cube([wedge_w, 1.2, 30]);
        difference() { wedge_solid(0); translate([intake[0]-3, intake[2]-3, 0]) cube([intake[1]-intake[0]+6, intake[3]-intake[2]+6, 40]); }
    }
}

module intake_slots() {
    for (x = [intake[0] + 2 : slot_pitch : intake[1] - 2])
        translate([x, intake[2], -1]) cube([slot_w, intake[3] - intake[2], foot_h + floor_t + 2]);
}
module side_intake() {
    for (y = [side_intake_y[0] : slot_pitch : side_intake_y[1]])
        translate([wx0 + wedge_w - wall - 1, y, foot_h + floor_t + 1.5]) cube([wall + 2, slot_w, side_slot_h]);
}

// 3) 나사: OEM과 같은 높이에 나사머리 자리 → 나사 물림 길이 동일
//    자리 면 z_seat = OEM 외부면 + cbore_depth, 그 위 seat_t 두께 = 팜레스트 보스가 닿는 면
function z_seat(y) = zp(y) + cbore_depth;
module wedge_prism() { translate([wx0, wy0, -1]) cube([wedge_w, wedge_d, 60]); }
function edge_screw(s) = min(s[0]-wx0, wx0+wedge_w-s[0], s[1]-wy0, wy0+wedge_d-s[1]) < relief_r;

// Keep the fixed 340-mm pod envelope, but scallop its edge around five screws.
// The inner ring meets the retained OEM-zone plate; it is only a geometry
// hypothesis, not a validated screw load path or ingress seal.
module screw_relief_cut() {
    for (s = screws) if (edge_screw(s))
        translate([s[0], s[1], -1]) cylinder(r = relief_r, h = 65);
}
module screw_relief_wall() {
    for (s = screws) if (edge_screw(s))
        intersection() {
            wedge_solid(0);
            wedge_prism();
            difference() {
                translate([s[0], s[1], -1]) cylinder(r = relief_r + wall, h = 65);
                translate([s[0], s[1], -2]) cylinder(r = relief_r, h = 67);
            }
        }
}

// v8: X 방향 장공. 반길이 = |X − W/2|·slot_k (≤ slot_max). 가운데 나사는 원형.
function sl(s) = min(slot_max, abs(s[0] - W/2) * slot_k);
module slotted(s, d, h) { hull() for (dx = [-sl(s), sl(s)]) translate([s[0] + dx, s[1], 0]) cylinder(d = d, h = h); }

// v9: 나사별 머리 자리/받침 높이 (params screw_spec). is_undef면 v8 방식(cbore_depth + seat_t)
function sp(i) = is_undef(screw_spec) ? [cbore_depth, cbore_depth + seat_t, 0, 0, 0] : screw_spec[i];
function seat_z(i) = zp(screws[i][1]) + sp(i)[0];
module screw_cut() {
    for (i = [0 : len(screws) - 1]) { s = screws[i];
        translate([0, 0, -1]) slotted(s, screw_hole_d, 60);
        translate([0, 0, -1]) slotted(s, screw_cbore_d, seat_z(i) + 1);
        if (!edge_screw(s)) intersection() {   // 가장자리 나사는 쐐기 홈 바깥에서 OEM형 구멍으로 접근
            translate([s[0], s[1], -1]) cylinder(d = well_d, h = seat_z(i) + 1);
            wedge_prism();
        }
    }
}
module screw_tubes() {
    for (i = [0 : len(screws) - 1]) { s = screws[i]; p = sp(i); z0 = zp(s[1]);
        // 넓은 자리 (장공을 감싸도록 같은 방향으로 늘림)
        translate([0, 0, z0 + t_oem - wall]) slotted(s, screw_cbore_d + 2*wall, p[1] - t_oem + wall);
        // 가는 보스: 팜레스트/힌지 보스 바로 아래까지 받쳐 조일 때 판이 휘지 않게
        if (p[2] > p[1]) translate([0, 0, z0 + p[1] - 0.01])
            if (p[4] == 1) slotted(s, 2 * p[3], p[2] - p[1] + 0.01);
            else translate([s[0], s[1], 0]) cylinder(r = p[3], h = p[2] - p[1] + 0.01);
        // 쐐기 안: 우물 벽
        if (!edge_screw(s)) intersection() {
            translate([s[0], s[1], foot_h]) cylinder(d = well_d + 2*wall, h = z0 + p[1] - foot_h);
            wedge_prism();
        }
    }
}

// 4) 발 (네 모서리). v8 분리형이면 뒤쪽 두 발은 뚜껑으로 옮기고 뚜껑 나사·우물과 겹치지 않게 y 30으로 이동
module feet() {
    for (x = [wx0 + 15, wx0 + wedge_w - 45], y = split_lid ? [wy0 + wedge_d - 18] : [wy0 + 10, wy0 + wedge_d - 18])
        translate([x, y, 0]) cube([30, 8, foot_h]);
}
// Two blind M2 anchors on the underside; no through-hole into Dell internals.
// Local design X is mirrored by out_frame() to print X=150 and 330 mm.
cassette_front_anchors = [[W-150,195],[W-330,195]];
module cassette_front_bosses() {
    for (p=cassette_front_anchors) translate([p[0],p[1],0])
        cylinder(d=9,h=3.6);
}
module cassette_front_pilots() {
    for (p=cassette_front_anchors) translate([p[0],p[1],-0.1])
        cylinder(d=1.7,h=4.9);
}
module lid_feet() {
    for (x = [wx0 + 25, wx0 + 285]) translate([x, wy0 + 30, 0]) cube([30, 8, foot_h + 0.01]);
}

// 5) 스냅 클립 후크: 벽 안쪽에 붙어 벽 윗면 위로 솟는 탭 + 끝에 바깥쪽 걸림 턱
//    높이: 안쪽 바닥면(zp + t_oem)에서 clip_top [USER 7 mm]
function in_notch(x) = (x > hinge_notches[0][0]-4 && x < hinge_notches[0][1]+4) || (x > hinge_notches[1][0]-4 && x < hinge_notches[1][1]+4);
function is_screw_near(x, y) = len([for (s = screws) if (abs(s[0]-x) < 6 && abs(s[1]-y) < 6) 1]) > 0;

// 한 개의 후크: 로컬 좌표에서 +Y가 바깥쪽, 원점은 벽 안쪽 면 하단
module hook(zbase, ztop, w = clip_w) {
    translate([-w/2, -clip_t, zbase]) cube([w, clip_t + 0.2, ztop - zbase]);           // 팔 (벽에 0.2 겹침)
    // v10.1: 걸림 턱 윗면을 경사(유도면)로 → 끼울 때 턱이 팜레스트 가장자리를 타고 넘어감. 아랫면(걸림면)은 수평 유지
    hull() {
        translate([-w/2, 0, ztop - clip_catch_h]) cube([w, clip_catch, 0.01]);
        translate([-w/2, 0, ztop - 0.01]) cube([w, 0.01, 0.01]);
    }
}
module clips() { if (use_measured_clips) clips_measured(); else clips_uniform(); }
// 사진 가상 스캔 목록(params.scad clips_list)의 위치에만 후크를 둔다.
// v9: 후크 아래끝은 벽 윗면 1 mm 아래(겹침), 윗끝은 순정 벽 윗면 + clip_above_rim(사진 실측)
function clip_zbase(y) = use_oem_wall_profile ? zp(y) + wall_H(y) - wall_clear - 1 : zp(y) + lip_h - 1;
function clip_ztop(y)  = use_oem_wall_profile ? zp(y) + wall_H(y) + clip_above_rim : zp(y) + t_oem + clip_top;
module clips_measured() {
    for (c = clips_list) {
        w = min(c[2], clip_w_max); s = c[1];
        if (c[0] == 0) translate([s, wall, 0]) mirror([0,1,0]) hook(clip_zbase(wall), clip_ztop(wall), w);
        if (c[0] == 1) translate([s, D - wall, 0]) hook(clip_zbase(D - wall), clip_ztop(D - wall), w);
        if (c[0] == 2) translate([wall, s, 0]) rotate([0,0,90]) hook(clip_zbase(s), clip_ztop(s), w);
        if (c[0] == 3) translate([W - wall, s, 0]) rotate([0,0,-90]) hook(clip_zbase(s), clip_ztop(s), w);
    }
}
module clips_uniform() {
    for (x = [clip_pitch : clip_pitch : W - clip_pitch]) {
        if (!in_notch(x) && !is_screw_near(x, wall))            // 후방 벽 (바깥 = -Y)
            translate([x, wall, 0]) mirror([0,1,0]) hook(zp(wall) + lip_h - 1, zp(wall) + t_oem + clip_top);
        if (!is_screw_near(x, D - wall))                          // 전방 벽 (바깥 = +Y)
            translate([x, D - wall, 0]) hook(zp(D) + lip_h - 1, zp(D) + t_oem + clip_top);
    }
    for (y = [clip_pitch : clip_pitch : D - clip_pitch]) {
        if (!is_screw_near(wall, y))                              // 왼쪽 벽 (바깥 = -X)
            translate([wall, y, 0]) rotate([0,0,90]) hook(zp(y) + lip_h - 1, zp(y) + t_oem + clip_top);
        if (!is_screw_near(W - wall, y))                          // 오른쪽 벽 (바깥 = +X)
            translate([W - wall, y, 0]) rotate([0,0,-90]) hook(zp(y) + lip_h - 1, zp(y) + t_oem + clip_top);
    }
}

module spk_cut() {
    sw = max(wall, side_wall_t);   // v10: 두꺼워진 좌우 벽까지 절개
    for (s = spk) translate([s[0] == 0 ? -1 : W - sw - 1, s[1], 0]) cube([sw + 2, s[2] - s[1], 60]);
}

// A notch cut in rim() alone is insufficient: the added C03 wedge begins
// inside the rear hinge recesses and otherwise fills those openings again.
// Research-only rectangular projection; the actual hinge sweep/clearance is unknown.
module hinge_cut() {
    for (n = hinge_notches)
        translate([n[0], -1, -2]) cube([n[1] - n[0], hinge_notch_d + 1, 65]);
}

// 6) v8 정비 뚜껑 ------------------------------------------------------------
// 본체에 남기는 영역: 팬 덕트(흡기 경로를 한 부품으로 유지), 뒤 나사 우물 3개, 가장자리 나사 섬 5개.
module lid_keepouts2d() {
    for (s = screws) translate([s[0], s[1]])
        circle(r = edge_screw(s) ? relief_r + wall : well_d/2 + wall);
    translate([intake[0] - fan_duct_margin, intake[2] - fan_duct_margin])
        square([intake[1] - intake[0] + 2*fan_duct_margin, intake[3] - intake[2] + 2*fan_duct_margin]);
}
module lid_outline2d(g) {
    difference() {
        // g_eff ≥ 0.05: 본체 절단면이 벽/우물/덕트 외면과 같은 면에 놓이면 비다양체 모서리가 생긴다
        translate([wx0 + wall + max(g, 0.05), wy0 + wall + max(g, 0.05)])
            square([wedge_w - 2*wall - 2*max(g, 0.05), lid_end_local - wall - 2*max(g, 0.05)]);
        offset(delta = max(g, 0.05)) lid_keepouts2d();
    }
}
module body_lid_cut() { translate([0, 0, -1]) linear_extrude(foot_h + floor_t + 1) lid_outline2d(0); }
// 뚜껑 고정 기둥: 뚜껑 윗면~지붕까지 한 덩어리 (지붕 보강 겸용). 아래에서 M2 인서트
module lid_bosses() {
    for (p = lid_bosses_local) intersection() {
        translate([wx0 + p[0], wy0 + p[1], foot_h + floor_t]) cylinder(d = boss_d, h = 60);
        wedge_solid(0);
    }
}
module lid_boss_holes() {
    for (p = lid_bosses_local)
        translate([wx0 + p[0], wy0 + p[1], foot_h + floor_t - 0.01]) cylinder(d = insert_hole_d, h = insert_depth);
}
// v9 스냅: 기준 자세 = 바깥이 −X. 팔 x∈[0, snap_t], 돌기는 −X로 snap_bump.
// 아래면 45° (당기면 풀림), 위면 경사 (밀어 넣으면 휘어 들어감).
module snap_arm_canonical() {
    z0 = foot_h + floor_t - 0.01; zb = snap_zb; bb = snap_bump;
    translate([0, -snap_w/2, z0]) cube([snap_t, snap_w, snap_len + 0.01]);
    rotate([90, 0, 0]) linear_extrude(snap_w, center = true)
        polygon([[0.01, zb], [-bb, zb + bb], [-bb, zb + bb + 0.3], [0.01, zb + bb + 1.8]]);
}
module snap_place(s) {   // 뚜껑 가장자리(벽 안쪽 면 + lid_gap)에 배치
    if (s[0] == 0) translate([wx0 + wall + lid_gap, wy0 + s[1], 0]) children();
    if (s[0] == 1) translate([wx0 + wedge_w - wall - lid_gap, wy0 + s[1], 0]) mirror([1, 0, 0]) children();
    if (s[0] == 2) translate([wx0 + s[1], wy0 + wall + lid_gap, 0]) rotate([0, 0, 90]) children();
}
module snap_arms() { for (s = snaps_local) snap_place(s) snap_arm_canonical(); }
// 벽의 걸림 창 (벽만 관통)
module snap_windows() {
    for (s = snaps_local) snap_place(s)
        translate([-(wall + lid_gap) - 1, -(snap_w + 1)/2, snap_zb - 0.3]) cube([wall + lid_gap + 1.05, snap_w + 1, snap_bump + 2.4]);
}

module lid() {
    difference() {
        union() {
            translate([0, 0, foot_h]) linear_extrude(floor_t) lid_outline2d(lid_gap);
            lid_feet();
            // B12 GPIO-A1 hangs from the service lid. Coordinates come from
            // supplied B12 GPIO origin (56,14) + 3/37,3/32-mm hole insets,
            // mirrored into Dell print frame and then back to design frame.
            // 17-mm pillars keep PCB clear of B12 underneath; no lid penetration.
            for (x=[91.00,125.00], y=[35,64])
                translate([x,y,-14.0]) cylinder(d=6.5,h=17.1);
            if (lid_fix == "snap") snap_arms();
        }
        for (p = lid_bosses_local) translate([wx0 + p[0], wy0 + p[1], foot_h - 1]) {
            cylinder(d = lid_screw_d, h = floor_t + 2);
            cylinder(d = lid_cbore_d, h = 1 + lid_cbore_h);
        }
        hinge_cut();
        // Dell roof eDP opening is X=63.5..110 (design frame). Feed the
        // bundled cables into the attached cassette, clear of the M2 boss.
        hull() for (x=[W-288,W-254], y=[14,27])
            translate([x,y,-1]) cylinder(r=2,h=8);
        for (x=[91.00,125.00], y=[35,64])
            translate([x,y,-14.01]) cylinder(d=1.7,h=5.1);
    }
}

// 7) v8 배선·조작 개구 -------------------------------------------------------
module wall_hole(y, z, d) { translate([wx0 - 1, wy0 + y, z]) rotate([0, 90, 0]) cylinder(d = d, h = wall + 1.4); }
module v8_openings_cut() {
    if (!b12_external) {
        wall_hole(dc_hole[0], dc_hole[1], dc_hole[2]);
        wall_hole(btn_hole[0], btn_hole[1], btn_hole[2]);
        wall_hole(led_hole[0], led_hole[1], led_hole[2]);
    }
    // 왼쪽 벽 케이블 창: 아래가 열려 뚜껑을 닫기 전에 선을 눕혀 넣는다
    translate([wx0 - 1, wy0 + side_cable_slot[0], foot_h - 0.5])
        cube([wall + 1.4, side_cable_slot[1] - side_cable_slot[0], side_cable_slot[2] - foot_h + 0.5]);
    for (y = [left_vent_y[0] : slot_pitch : left_vent_y[1]])
        translate([wx0 - 1, wy0 + y, 6]) cube([wall + 1.4, slot_w, 3]);
    // 노트북 내부 eDP 인터포저 케이블 → 공동 (지붕 관통, 모서리 R2)
    hull() for (x = [edp_passthrough[0] + 2, edp_passthrough[1] - 2], y = [edp_passthrough[2] + 2, edp_passthrough[3] - 2])
        translate([x, y, foot_h + floor_t + 0.5]) cylinder(r = 2, h = 60);
    // y=80 리브 배선 홈
    for (n = rib_cable_notches)
        translate([wx0 + n[0], 79, foot_h - 1]) cube([n[1] - n[0], 2, floor_t + rib_notch_h + 1]);
}

module base_cover() {
    difference() {
        union() {
            difference() {
                rim();
                difference() {
                    translate([0,0,-1]) linear_extrude(60) offset(delta = -wall) translate([wx0, wy0]) square([wedge_w, wedge_d]);
                    // Retain an OEM-height support island around each edge screw.
                    for (s = screws) if (edge_screw(s))
                        translate([s[0], s[1], -2]) cylinder(r = relief_r + wall, h = 65);
                }
            }
            side_wall_root();
            wedge();
            screw_relief_wall();
            screw_tubes();
            feet();
            cassette_front_bosses();
            clips();
            if (split_lid) lid_bosses();
        }
        screw_cut();
        spk_cut();
        hinge_cut();
        if (split_lid) { body_lid_cut(); lid_boss_holes(); if (lid_fix == "snap") snap_windows(); }
        if (v8_openings) v8_openings_cut();
        if (side_chamfer > 0) side_edge_chamfer();
        cassette_front_pilots();
    }
}

// 진단 렌더: -D 'export_component="wedge"' 또는 "rim".
// v8: 기본 = 본체("base"), "lid" = 정비 뚜껑, "assembly" = 둘 다(미리보기용, 출력 파일 아님).
export_component = is_undef(export_component) ? "base" : export_component;
// v10: 설계 좌표(X 왼쪽→오른쪽, Y 힌지→앞, Z 위)는 왼손 좌표계 → 기본 출력은 x → W − x 로 뒤집은 실물 방향(발주용).
//      시뮬레이션용 설계 좌표 STL만 -D 'print_frame=false' 로 내보낸다.
print_frame = is_undef(print_frame) ? true : print_frame;
module out_frame() { if (print_frame) translate([W, 0, 0]) mirror([1, 0, 0]) children(); else children(); }
out_frame()
if (export_component == "wedge") wedge();
else if (export_component == "wedge_shell") wedge_shell();
else if (export_component == "rim") rim();
else if (export_component == "lid") lid();
else if (export_component == "assembly") { color([0.35,0.38,0.42]) base_cover(); color([0.95,0.55,0.1]) lid(); }
else if (export_component == "exploded") { color([0.35,0.38,0.42]) base_cover(); color([0.95,0.55,0.1]) translate([0,0,-25]) lid(); }
else base_cover();
