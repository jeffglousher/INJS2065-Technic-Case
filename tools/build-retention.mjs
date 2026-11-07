// Experimental retention geometry. Uses a separate native process, never a desktop.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {Client} from './mcp-client.mjs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFile(new URL(path, root), 'utf8');
const write = (path, value) => fs.writeFile(new URL(path, root), typeof value === 'string' ? value : JSON.stringify(value));
const source = await read('design/current.model.json');
const controlEvidence=JSON.parse(await read('docs/validation.json'));
assert.equal(crypto.createHash('sha256').update(source).digest('hex'),controlEvidence.model_sha256,
  'Control model changed; qualify it before generating another trial');
await fs.mkdir(new URL('local/retention/', root), {recursive:true});
const client = new Client(process.env.NBCAD_MCP_EXE || 'C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe', 180000);
const calls = [];
async function call(name, args={}) {
  const result = await client.call(name,args);
  calls.push({name,arguments:args});
  return result;
}
const model = async () => JSON.parse(await call('cad_project_model'));
async function exportMesh(path, ids) {
  const result=await call('solid_export_3mf',{body_ids:ids,scope:'definition',linear_deflection:0.005,angular_deflection:0.1});
  await fs.writeFile(new URL(path,root),Buffer.from(result.bytes_base64,'base64'));
}
async function plane(name, orientation, distance) {
  await call('construction_plane_offset',{name,reference:{type:'origin_plane',plane:orientation},distance});
  const m = await model();
  return {type:'datum_plane',datum_id:m.datum_planes.at(-1).datum_id};
}
async function sketch(name, orientation, distance) {
  const p = await plane(name+' plane',orientation,distance);
  await call('sketch_begin',{name,plane:p});
  await call('sketch_set_grid_snap',{enabled:false});
}
async function finishExtrude(name, depth, operation, target) {
  await call('sketch_finish');
  const profiles = await call('sketch_profiles');
  await write('local/retention/last-profiles.json',profiles);
  await call('solid_extrude',{sketch_name:name,profile_indices:[0],operation,
    extent:{type:'distance',distance:depth},taper_angle_deg:0,flip:false,target_body_ids:[target]});
}
async function box(name, bounds, operation, target) {
  const [x0,y0,z0,x1,y1,z1] = bounds;
  await sketch(name,'xy',z0);
  await call('sketch_add_rectangle',{mode:'two_point',p1:{x:x0,y:y0},p2:{x:x1,y:y1},ctrl_held:true});
  await finishExtrude(name,z1-z0,operation,target);
}
async function slot(name, x0,x1,z0,z1,target,sign) {
  // XZ normal points toward -Y. Rounded closed root, square open free end.
  await sketch(name,'xz',sign===1 ? -12.1 : 7.9);
  await call('sketch_add_rectangle',{mode:'two_point',p1:{x:x0,y:z0},p2:{x:x1,y:z1},ctrl_held:true});
  await finishExtrude(name,4.2,'cut',target);
  const round = name+' root radius';
  await sketch(round,'xz',sign===1 ? -12.1 : 7.9);
  await call('sketch_add_circle_locked',{mode:'center_diameter',anchor:{x:x0,y:(z0+z1)/2},edge_hint:{x:x0+(z1-z0)/2,y:(z0+z1)/2},diameter_mm:z1-z0,ctrl_held:true});
  await finishExtrude(round,4.2,'cut',target);
}
async function hook(name, bottom, target,sign) {
  await sketch(name,'yz',5.0);
  // Coordinates are Y,Z; insertion is -Y and release flex is -Z.
  const points = [[7.95,bottom],[10.95,bottom],[10.95,20.2],[8.65,20.2],
    [8.65,20.65],[8.4,20.65],[7.95,20.2]];
  for(let i=0;i<points.length;i++) {
    const a=points[i],b=points[(i+1)%points.length];
    await call('sketch_add_line',{from:{x:sign*a[0],y:a[1]},to_raw:{x:sign*b[0],y:b[1]},ctrl_held:true});
  }
  await finishExtrude(name,1.5,'join',target);
}
async function latch(thickness) {
  const bottom=20.2-thickness;
  for(const [target,sign] of [[173,1],[267,-1]]) {
    const suffix=sign===1 ? ' +Y' : ' -Y';
    const b=(name,v,op,id)=>box(name+suffix,sign===1?v:[v[0],-v[4],v[2],v[3],-v[1],v[5]],op,id);
    await slot('Latch lower flex clearance'+suffix,-3.5,7.1,bottom-.6,bottom,target,sign);
    await slot('Latch upper flex clearance'+suffix,-3.5,7.1,20.2,20.8,target,sign);
    await b('Latch free tip clearance',[6.5,7.9,18.4,7.1,12.1,20.8],'cut',target);
    await b('Latch backing separation',[-3.5,7.9,bottom,6.5,10.8,20.2],'cut',target);
    await hook('Latch ramp and retaining shoulder'+suffix,bottom,target,sign);
    await b('Upper latch travel pocket',[4.8,7.7,18.3,6.7,10.8,20.25],'cut',18);
    await b('Upper latch captured hook pocket',[4.8,7.7,20.25,6.7,8.8,20.85],'cut',18);
  }
}
try {
  await client.start();
  for(const [label,thickness] of [['control',null],['A',1.2],['B',1.0]]) {
    await call('cad_load_project_model',{model_json:source});
    if(thickness) await latch(thickness);
    await call('cad_set_document_name',{name:thickness ? `INJS2065 experimental latch ${label} ${thickness} mm` : 'INJS2065 retention control'});
    const full=await model();
    await write(`local/retention/${label}-full.model.json`,JSON.stringify(full,null,2)+'\n');
    const scene=await call('solid_scene');
    assert.deepEqual(scene.errors,[]);
    await write(`local/retention/${label}-full-scene.json`,scene);
    await exportMesh(`local/retention/${label}-full.3mf`,[8,18,173,267,54]);
    if(label==='A') {
      await fs.mkdir(new URL('design/retention/',root),{recursive:true});
      await write('design/retention/latch.model.json',JSON.stringify(full,null,2)+'\n');
    }
    // Keep the entire +Y rail at its original XYZ and both original registration
    // features. These are fit-screening coupons, not a stiffness-equivalent assembly.
    for(const id of [8,18]) await box(`Coupon retain registered Y rail ${id}`,[-12.1,7.6,7.9,28.1,12.1,42.1],'intersect',id);
    const coupon=await call('solid_scene');
    assert.deepEqual(coupon.errors,[]);
    await write(`local/retention/${label}-coupon-scene.json`,coupon);
    await write(`local/retention/${label}-coupon.model.json`,await call('cad_project_model'));
    await exportMesh(`local/retention/${label}-coupon.3mf`,[8,18,173]);
    console.log(`Built ${label}: full model and registered rail coupon`);
  }
  // Do not retain large model payloads in the replay log.
  await write('local/retention/calls.json',calls.filter(c=>c.name!=='cad_load_project_model'));
} finally {client.close();}
