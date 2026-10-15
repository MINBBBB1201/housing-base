process = is_undef(process) ? "MJF" : process;
mode = is_undef(mode) ? "exploded" : mode;
color([0.33, 0.36, 0.40]) import(str(process, "_B12_external_body.stl"));
if (mode != "body")
    color([0.95, 0.55, 0.10])
        translate([0, 0, mode == "exploded" ? -30 : 0])
            import(str(process, "_B12_external_lid.stl"));
