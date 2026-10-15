// v8 미리보기 전용: 렌더된 STL을 불러와 색을 입힌다. mode = "exploded" | "assembly" | "body"
mode = is_undef(mode) ? "exploded" : mode;
color([0.33,0.36,0.40]) import("base_cover_research_226p2mm_v8_body.stl");
if (mode != "body") color([0.95,0.55,0.10]) translate([0, 0, mode == "exploded" ? -30 : 0]) import("base_cover_research_226p2mm_v8_lid.stl");
