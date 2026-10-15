include <params.scad>
use <base_cover.scad>
// 후방 중앙 나사(B3) 지나는 YZ 단면, 앞 왼쪽 나사(B6) 지나는 YZ 단면
module sec(x) projection(cut=true) rotate([0,-90,0]) translate([-x,0,0]) base_cover();
translate([0,0]) sec(179);
translate([0,-40]) sec(8);
