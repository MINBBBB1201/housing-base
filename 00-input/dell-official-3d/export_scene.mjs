// Export every *_GP part group (first occurrence of each name = first guide-step state) (plus hinge groups) of Dell's Inspiron 3525 3D-guide scene to mm STL (Z-up),
// using the high-res NEEDLE_progressive LOD0 meshes. Usage: node export_scene.mjs <dir> [--write]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
import fs from 'fs'; import path from 'path';
const DIR = process.argv[2], WRITE = process.argv.includes('--write');
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder': await draco3d.createDecoderModule()});
const src = path.join(DIR,'scene.glb'); const raw = fs.readFileSync(src);
const J = JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString('utf8'));
const doc = await io.read(src); const R = doc.getRoot(); const meshes = R.listMeshes();
const SKIP = /arrow|screwdriver|spudger|pry_line|tag\(|flag|plane|text|image|highlight|tool|hand/i;
const toCAD = ([x,y,z]) => [x*1000, -z*1000, y*1000];
const lodCache = new Map();
async function meshTris(n){
  const mi = meshes.indexOf(n.getMesh()); const prog = J.meshes[mi]?.extensions?.NEEDLE_progressive;
  let mesh = n.getMesh();
  const f = prog?.lods?.[0] && path.join(DIR,'lod0',prog.lods[0].path);
  if (f && fs.existsSync(f)) { if(!lodCache.has(f)) lodCache.set(f,(await io.read(f)).getRoot().listMeshes()[0]); mesh = lodCache.get(f); }
  const W = n.getWorldMatrix(); const out=[];
  for (const p of mesh.listPrimitives()) { const a=p.getAttribute('POSITION'); if(!a) continue; const ix=p.getIndices(); const v=[0,0,0]; const P=[];
    for(let i=0;i<a.getCount();i++){a.getElement(i,v); P.push(toCAD([W[0]*v[0]+W[4]*v[1]+W[8]*v[2]+W[12],W[1]*v[0]+W[5]*v[1]+W[9]*v[2]+W[13],W[2]*v[0]+W[6]*v[1]+W[10]*v[2]+W[14]]));}
    const I = ix ? ix.getArray() : P.map((_,k)=>k); for(let k=0;k+2<I.length;k+=3) out.push([P[I[k]],P[I[k+1]],P[I[k+2]]]); }
  return out;
}
async function groupTris(g){ const t=[]; const walk=async n=>{ if(SKIP.test(n.getName())) return; if(n.getMesh()) t.push(...await meshTris(n)); for(const c of n.listChildren()) await walk(c); }; await walk(g); return t; }
function bbox(t){ const mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9]; for(const tri of t) for(const p of tri) for(let k=0;k<3;k++){ if(p[k]<mn[k])mn[k]=p[k]; if(p[k]>mx[k])mx[k]=p[k]; } return {mn,mx}; }
function writeSTL(file,t,o){ const b=Buffer.alloc(84+50*t.length); b.write('Dell Inspiron 3525 3D guide part (mm, Z-up)',0); b.writeUInt32LE(t.length,80);
  t.forEach((tri,k)=>{ const [a,c,d]=tri.map(p=>p.map((x,j)=>x-o[j])); const u=[c[0]-a[0],c[1]-a[1],c[2]-a[2]], w=[d[0]-a[0],d[1]-a[1],d[2]-a[2]];
    let nx=u[1]*w[2]-u[2]*w[1], ny=u[2]*w[0]-u[0]*w[2], nz=u[0]*w[1]-u[1]*w[0]; const L=Math.hypot(nx,ny,nz)||1;
    [nx/L,ny/L,nz/L,...a,...c,...d].forEach((f,j)=>b.writeFloatLE(f,84+50*k+4*j)); }); fs.writeFileSync(file,b); }
const groups = R.listNodes().filter(n=>/_GP( \(\d\))?$|_Hinges$|_Display_Cable$|_WLAN_Cable$|^Inspiron_3525_Basecover-1\.002$|^Inspiron_3525_Basecover_(Remove|Loosen)_Screws$/.test(n.getName()));
const res=[];
const seenNames=new Set();
for (const g of groups){ if(seenNames.has(g.getName())) continue; seenNames.add(g.getName()); const t=await groupTris(g); if(!t.length) continue; const {mn,mx}=bbox(t); res.push({name:g.getName(),t,mn,mx}); }
// common origin: installed base cover body bbox min corner (so every part shares the base-cover frame)
const bc = res.find(r=>r.name==='Ins_15_3525_Base_Cover_GP'); const O = bc.mn;
const rows = res.map(r=>({part:r.name, tris:r.t.length, min:r.mn.map((v,k)=>+(v-O[k]).toFixed(1)), max:r.mx.map((v,k)=>+(v-O[k]).toFixed(1)), size:r.mx.map((v,k)=>+(v-r.mn[k]).toFixed(1))}));
rows.forEach(r=>console.log(r.part.padEnd(38), String(r.tris).padStart(6),' size',r.size.join(' x ').padEnd(24),' min',r.min.join(', ')));
if (WRITE){ const out=path.join(DIR,'parts'); fs.mkdirSync(out,{recursive:true});
  for (const r of res) writeSTL(path.join(out, r.name.replace(/[^\w()-]+/g,'_').replace(/_+$/,'')+'.stl'), r.t, O);
  fs.writeFileSync(path.join(out,'parts-index.json'), JSON.stringify({units:'mm', axes:'X=width, Y=depth (0 = hinge/rear edge), Z=height; origin = base-cover bbox min corner', source:'Dell 3D Guide scene CB04015352500 (dellarassistant.glare.kaalo.com), NEEDLE_progressive LOD0', parts:rows},null,1)); console.log('written to', out); }
