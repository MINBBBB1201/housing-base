// v10.1 미리보기 전용: 발주용 PRINT STL(실물 방향)을 불러와 색을 입힌다. mode = "exploded" | "assembly" | "body"
mode = is_undef(mode) ? "exploded" : mode;
color([0.33,0.36,0.40]) import("dell3525_basecover_v10_1_PRINT_body.stl");
if (mode != "body") color([0.95,0.55,0.10]) translate([0, 0, mode == "exploded" ? -30 : 0]) import("dell3525_basecover_v10_1_PRINT_lid.stl");
