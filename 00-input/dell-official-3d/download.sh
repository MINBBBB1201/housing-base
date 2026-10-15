#!/bin/sh
# Re-download Dell's Inspiron 3525 3D-guide assets (public, no login) + high-res LOD0 meshes.
# Source viewer: https://www.dell.com/support/product-details/en-us/product/inspiron-15-3525-laptop/resources/3dguides
set -e
B="https://dellarassistant.glare.kaalo.com/CB04015352500/assets"
REF="https://dellarassistant.glare.kaalo.com/index.html?mid=CB040153525000201AEN"
get() { curl -sf --retry 3 --max-time 120 -A "Mozilla/5.0" -e "$REF" -o "$2" "$B/$1"; }
get "1__Inspiron3525_FinalSource_Priority1_Base%20Cover_1.glb" base-cover.glb
get mySceneClone.glb scene.glb
get 3525.json 3525.json
mkdir -p lod0
python - <<'PY' | tr -d '\r' | xargs -P 8 -I{} sh -c 'test -s "lod0/{}" || curl -sf --retry 3 --max-time 120 -A Mozilla/5.0 -e "'"$REF"'" -o "lod0/{}" "'"$B"'/{}"'
import json, struct
for f in ("base-cover.glb", "scene.glb"):
    b = open(f, "rb").read(); j = json.loads(b[20:20 + struct.unpack("<I", b[12:16])[0]].decode("utf-8"))
    for m in j["meshes"]:
        p = m.get("extensions", {}).get("NEEDLE_progressive")
        if p and p.get("lods"): print(p["lods"][0]["path"])
PY
echo "done: $(ls lod0 | wc -l) LOD0 files"
