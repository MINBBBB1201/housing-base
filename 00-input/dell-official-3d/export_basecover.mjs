import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
import fs from 'fs'; import path from 'path';
const DIR = process.argv[2];
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder': await draco3d.createDecoderModule()});
const src = path.join(DIR,'base-cover.glb');
const raw = fs.readFileSync(src); const jl = raw.readUInt32LE(12); const J = JSON.parse(raw.subarray(20,20+jl).toString('utf8'));
const doc = await io.read(src); const R = doc.getRoot();
const nodes = R.listNodes(), meshes = R.listMeshes();
const parentOf = new Map(); nodes.forEach(n=>n.listChildren().forEach(c=>parentOf.set(c,n)));
const pathOf = n => { const p=[]; for(let x=n;x;x=parentOf.get(x)) p.unshift(x.getName()); return p.join('/'); };
// installed state = 02_locking
const pick = nodes.map((n,i)=>({n,i,p:pathOf(n)})).filter(o=>o.n.getMesh() && (o.p.includes('/02_locking/Inspiron_3525_Basecover_Assembly-1/') || /\/0[34]_removal_screws\/(part\/)?(Inspiron_3525_Basecover_Screws-1\/)?Body_[0-9_]+$/.test(o.p)));
const toCAD = ([x,y,z]) => [x*1000, -z*1000, y*1000]; // glTF Y-up m -> CAD Z-up mm
async function trisFor(o){
  const mi = meshes.indexOf(o.n.getMesh()); const prog = J.meshes[mi].extensions?.NEEDLE_progressive;
  let mesh = o.n.getMesh(), src='embedded';
  if (prog?.lods?.[0]) { const f=path.join(DIR,'lod0',prog.lods[0].path); if (fs.existsSync(f)) { const d2=await io.read(f); mesh=d2.getRoot().listMeshes()[0]; src='LOD0'; } }
  const W=o.n.getWorldMatrix(); const tris=[];
  for (const p of mesh.listPrimitives()) { const a=p.getAttribute('POSITION'), ix=p.getIndices(); const v=[0,0,0];
    const P=[]; for(let i=0;i<a.getCount();i++){a.getElement(i,v); P.push(toCAD([W[0]*v[0]+W[4]*v[1]+W[8]*v[2]+W[12],W[1]*v[0]+W[5]*v[1]+W[9]*v[2]+W[13],W[2]*v[0]+W[6]*v[1]+W[10]*v[2]+W[14]]));}
    const I = ix ? Array.from(ix.getArray()) : [...P.keys()];
    for(let k=0;k<I.length;k+=3) tris.push([P[I[k]],P[I[k+1]],P[I[k+2]]]); }
  return {tris, src, verts: mesh.listPrimitives().reduce((s,p)=>s+p.getAttribute('POSITION').getCount(),0)};
}
function writeSTL(file, tris){ const b=Buffer.alloc(84+50*tris.length); b.write('Dell Inspiron 3525 base cover (Dell 3D guide, mm)',0); b.writeUInt32LE(tris.length,80);
  tris.forEach((t,k)=>{ const o=84+50*k; const [a,c,d]=t; const u=[c[0]-a[0],c[1]-a[1],c[2]-a[2]], w=[d[0]-a[0],d[1]-a[1],d[2]-a[2]];
    let nx=u[1]*w[2]-u[2]*w[1], ny=u[2]*w[0]-u[0]*w[2], nz=u[0]*w[1]-u[1]*w[0]; const L=Math.hypot(nx,ny,nz)||1;
    [nx/L,ny/L,nz/L,...a,...c,...d].forEach((f,j)=>b.writeFloatLE(f,o+4*j)); }); fs.writeFileSync(file,b); }
const body=[], screws=[], report=[]; const seen=new Set();
for (const o of pick) { const r=await trisFor(o); const isScrew=/screw/i.test(o.p); const _f=r.tris.flat(); const key=(isScrew?'S':'B')+[0,1,2].map(k=>((Math.min(..._f.map(p=>p[k]))+Math.max(..._f.map(p=>p[k])))/2).toFixed(0)).join(','); if(seen.has(key)) continue; seen.add(key);
  (isScrew?screws:body).push(...r.tris);
  const xs=r.tris.flat(); const mn=[0,1,2].map(k=>Math.min(...xs.map(p=>p[k]))), mx=[0,1,2].map(k=>Math.max(...xs.map(p=>p[k])));
  report.push({part:o.p.split('/').slice(-2).join('/'), src:r.src, verts:r.verts, min:mn.map(x=>+x.toFixed(2)), max:mx.map(x=>+x.toFixed(2)), size:mx.map((m,k)=>+(m-mn[k]).toFixed(2)), center:mx.map((m,k)=>+((m+mn[k])/2).toFixed(2))}); }
// normalize: origin at body bbox min corner (X left->right, Y front->back as seen from CAD top), Z=0 bottom
const all=body.flat(); const o0=[0,1,2].map(k=>Math.min(...all.map(p=>p[k])));
const sh = t=>t.map(p=>p.map((c,k)=>c-o0[k]));
writeSTL(path.join(DIR,'dell3525-basecover-body.stl'), body.map(sh));
writeSTL(path.join(DIR,'dell3525-basecover-screws.stl'), screws.map(sh));
report.forEach(r=>{r.min=r.min.map((c,k)=>+(c-o0[k]).toFixed(2)); r.max=r.max.map((c,k)=>+(c-o0[k]).toFixed(2)); r.center=r.center.map((c,k)=>+(c-o0[k]).toFixed(2));});
fs.writeFileSync(path.join(DIR,'dell3525-basecover-parts.json'), JSON.stringify({units:'mm',axes:'X=width, Y=depth, Z=height (Z-up); origin=body bbox min corner', source:'Dell 3D Guide CB040153525000201A (Kaalo/Needle viewer), LOD0', parts:report},null,1));
console.log(`body tris=${body.length} screws tris=${screws.length}`); report.forEach(r=>console.log(r.src.padEnd(8),r.part.padEnd(45),'size',r.size.join(' x '),' center',r.center.join(', ')));
