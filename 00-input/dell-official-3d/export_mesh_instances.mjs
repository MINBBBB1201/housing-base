// Export every placed instance of one mesh (by NEEDLE_progressive guid prefix) from a Dell 3D-guide glb, LOD0, mm Z-up.
// Usage: node export_mesh_instances.mjs <glb> <lod0dir> <guidPrefix> <outPrefix>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
import fs from 'fs'; import path from 'path';
const [src, lodDir, guid, outp] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder': await draco3d.createDecoderModule()});
const raw = fs.readFileSync(src); const J = JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString('utf8'));
const doc = await io.read(src); const R = doc.getRoot(); const meshes = R.listMeshes();
const parentOf = new Map(); R.listNodes().forEach(n=>n.listChildren().forEach(c=>parentOf.set(c,n)));
const pathOf = n => { const p=[]; for(let x=n;x;x=parentOf.get(x)) p.unshift(x.getName()); return p.join('/'); };
const seen = new Set(); let k = 0;
for (const n of R.listNodes()) {
  const m = n.getMesh(); if (!m) continue; const prog = J.meshes[meshes.indexOf(m)]?.extensions?.NEEDLE_progressive;
  if (!prog || !prog.guid.startsWith(guid)) continue;
  const lod = (await io.read(path.join(lodDir, prog.lods[0].path))).getRoot().listMeshes()[0];
  const W = n.getWorldMatrix(); const tris = [];
  for (const p of lod.listPrimitives()) { const a=p.getAttribute('POSITION'), ix=p.getIndices(), v=[0,0,0], P=[];
    for (let i=0;i<a.getCount();i++){ a.getElement(i,v); const w=[W[0]*v[0]+W[4]*v[1]+W[8]*v[2]+W[12],W[1]*v[0]+W[5]*v[1]+W[9]*v[2]+W[13],W[2]*v[0]+W[6]*v[1]+W[10]*v[2]+W[14]]; P.push([w[0]*1000,-w[2]*1000,w[1]*1000]); }
    const I = ix ? ix.getArray() : P.map((_,q)=>q); for (let q=0;q+2<I.length;q+=3) tris.push([P[I[q]],P[I[q+1]],P[I[q+2]]]); }
  const mn=[Infinity,Infinity,Infinity], mx=[-Infinity,-Infinity,-Infinity]; for (const t of tris) for (const p of t) for (let c=0;c<3;c++){ if(p[c]<mn[c])mn[c]=p[c]; if(p[c]>mx[c])mx[c]=p[c]; }
  const key = mn.concat(mx).map(v=>v.toFixed(0)).join(','); if (seen.has(key)) continue; seen.add(key);
  const b = Buffer.alloc(84+50*tris.length); b.writeUInt32LE(tris.length,80);
  tris.forEach((t,q)=>{ const [A,B,C]=t.map(p=>p.map((c,j)=>c-mn[j])); const u=[B[0]-A[0],B[1]-A[1],B[2]-A[2]], w=[C[0]-A[0],C[1]-A[1],C[2]-A[2]];
    let nx=u[1]*w[2]-u[2]*w[1], ny=u[2]*w[0]-u[0]*w[2], nz=u[0]*w[1]-u[1]*w[0]; const L=Math.hypot(nx,ny,nz)||1;
    [nx/L,ny/L,nz/L,...A,...B,...C].forEach((f,j)=>b.writeFloatLE(f,84+50*q+4*j)); });
  const out = `${outp}-${k++}.stl`; fs.writeFileSync(out, b);
  console.log(out, 'tris', tris.length, 'size', mx.map((v,j)=>(v-mn[j]).toFixed(2)).join(' x '), '|', pathOf(n).split('/').slice(-4).join('/'));
}
