"""Generate the separate 11 revision; never writes into the supplied 10 revision."""
from pathlib import Path
import re,json,shutil
P=Path(__file__).resolve().parent
SOURCE=P/'verification/source-v10'
HOOKS=[[0,19.7,4,'B',-1,13.2],[0,71,5,'B',1,18],[0,104.4,5,'B',1,18],
 [0,141.4,5,'B',1,18],[0,203.4,4.4,'B',1,18],
 [1,50.3,5,'B',1,18],[1,160.9,5,'B',-1,18],[1,221.7,5,'B',1,18],
 [3,71.6,4,'A',1,18],[3,97.4,4,'A',-1,18],
 [3,136.8,4,'A',-1,18],[3,184.6,4,'A',1,18],[2,136.3,4,'C',-1,18]]
if (P/'hook_config.json').exists():HOOKS=json.loads((P/'hook_config.json').read_text())
(P/'hook_config.json').write_text(json.dumps(HOOKS,indent=2))
params=(SOURCE/'params.scad').read_text(encoding='utf8')
params=re.sub(r'clips_list = \[\];[^\n]*','clips_list = '+json.dumps([h[:4] for h in HOOKS])+'; // 13 original retained positions; FDM geometry in fdm_hooks.scad.',params)
params+='\n// Revision 11: horizontal PLA beams, original catch positions retained.\nfdm_hook_specs = '+json.dumps(HOOKS)+';\nfdm_t=1.8; fdm_h=1.8; fdm_gap=0.6; fdm_root_r=0.9; fdm_catch=0.35;\n'
(P/'params.scad').write_text(params,encoding='utf8')
src=(SOURCE/'base_cover_source.scad').read_text(encoding='utf8')
src=src.replace('include <pod.scad>','include <pod.scad>\ninclude <fdm_hooks.scad>')
src=src.replace('module clips() { if (use_measured_clips) clips_measured(); else clips_uniform(); }','module clips() { fdm_clips(); }')
src=src.replace('module base_cover() {','module base_cover_without_hooks() {')
src=src.replace('            clips();','            // Hooks are added after the relief slots are cut.')
src=src.replace('        screw_cut();','        fdm_reliefs();\n        screw_cut();')
src+='\nmodule base_cover() { union() {base_cover_without_hooks(); fdm_clips();} }\n'
src=src.replace('if (export_component == "wedge")','if (export_component == "hooks") out_frame() fdm_clips();\nelse if (export_component == "hook") out_frame() fdm_clip(fdm_hook_specs[hook_index]);\nelse if (export_component == "none") {}\nelse if (export_component == "wedge")')
(P/'base_cover_source.scad').write_text(src,encoding='utf8')
print('Generated revision 11 source with',len(HOOKS),'hooks')
