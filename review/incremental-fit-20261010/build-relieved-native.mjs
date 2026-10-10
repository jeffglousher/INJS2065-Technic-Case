import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010';
const protrusion=Number(process.argv[2]||'.26'),holding=Number(process.argv[3]||'.02');
const tag=process.argv[4]||'candidate',c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000),receipts=[];
const z=24.703961852410437,crest=.2+protrusion,R=.8,base=.16,b=.373205080756889;
const rise=crest-base,outerR=Math.max(.2,(.72**2+rise**2)/(2*rise)-R),dx=Math.sqrt((R+outerR)**2-(R+outerR-rise)**2);
const seatStart=9.809663461670024;
async function apply(name,args={}) {
  try {const r=await c.call(name,args);receipts.push({name,args});return r;}
  catch(e){const scene=await c.call('solid_scene');assert(scene.errors.length&&scene.errors.every(x=>[782,783].includes(x.feature_id)&&['referenced fillet edge no longer exists','OCCT could not build the selected solid fillet'].includes(x.message)),e.message);receipts.push({name,args,known_stale_fillet:true});return null;}
}
async function line(a,b){await apply('sketch_add_line',{from:{x:a[0],y:a[1]},to_raw:{x:b[0],y:b[1]},ctrl_held:true});}
async function arc(a,mid,b){await apply('sketch_add_arc_3pt',{p1:{x:a[0],y:a[1]},p2:{x:mid[0],y:mid[1]},p3:{x:b[0],y:b[1]},ctrl_held:true});}
async function replace(sketchId,revolveId,draw) {
 const m=JSON.parse(await c.call('cad_project_model')),s=m.sketches.find(x=>x.feature_id===sketchId),r=m.revolves.find(x=>x.feature_id===revolveId);
 await apply('sketch_edit',{name:s.name});await apply('sketch_delete_entities',{entity_ids:s.snapshot.entities.map(x=>x[0])});await draw();await apply('sketch_finish');
 const profiles=await c.call('sketch_profiles'),p=profiles.find(x=>x.sketch_name===s.name);assert.equal(p.profiles.length,1);
 const {axis_origin,axis_direction,angle_deg,flip,operation,target_body_ids}=r;
 await apply('solid_edit_revolve',{feature_id:revolveId,revolve:{sketch_name:s.name,profile_indices:[p.profiles[0].index],axis_origin,axis_direction,angle_deg,flip,operation,target_body_ids}});
}
try {
 await fs.mkdir(out,{recursive:true});await c.start();
 const raw=await fs.readFile(process.argv[5]||root+'/design/current.model.json','utf8'),original=JSON.parse(raw);
 await apply('cad_load_project_model',{model_json:raw});if(!process.argv[5]){await fs.writeFile(out+'/baseline.model.json',raw);await fs.writeFile(out+'/baseline-scene.json',JSON.stringify(await c.call('solid_scene')));}
 const s=original.sketches.find(x=>x.feature_id===518),points=s.snapshot.entities.filter(x=>x[1].type==='point');assert.equal(points.length,48);assert.equal(s.snapshot.constraints.length,0);
 const first=points.slice(0,6).map(x=>x[1].position.x),half=(Math.max(...first)-Math.min(...first))/2;assert(Math.abs(half-1.95)<1e-8||Math.abs(half-1.85)<1e-8);
 if(Math.abs(half-1.95)<1e-8){await apply('sketch_edit',{name:s.name});
 for(let i=0;i<48;i+=6){const pp=points.slice(i,i+6),cx=pp.reduce((sum,p)=>sum+p[1].position.x,0)/6,cy=pp.reduce((sum,p)=>sum+p[1].position.y,0)/6;for(const [id,e] of pp)await apply('sketch_move_point',{point_id:id,to_raw:{x:cx+(e.position.x-cx)*1.85/1.95,y:cy+(e.position.y-cy)*1.85/1.95},ctrl_held:true,phase:'single'});}
 await apply('sketch_finish');const e=original.extrudes.find(x=>x.feature_id===519),{sketch_name,profile_indices,operation,extent,taper_angle_deg,flip,target_body_ids}=e;
 await apply('solid_edit_extrude',{feature_id:519,extrude:{sketch_name,profile_indices,operation,extent,taper_angle_deg,flip,target_body_ids}});}
 await replace(755,756,async()=>{
  const x0=9.8-dx,x1=9.8+dx,jx=dx*R/(R+outerR),jr=crest-R+R*(R+outerR-rise)/(R+outerR);
  const theta=Math.atan2(jr-base-outerR,dx-jx),mid=(-Math.PI/2+theta)/2;
  await arc([x0,z+base],[x0+outerR*Math.cos(mid),z+base+outerR+outerR*Math.sin(mid)],[9.8-jx,z+jr]);
  await arc([9.8-jx,z+jr],[9.8,z+crest],[9.8+jx,z+jr]);
  await arc([9.8+jx,z+jr],[x1-outerR*Math.cos(mid),z+base+outerR+outerR*Math.sin(mid)],[x1,z+base]);
  await line([x1,z+base],[x1,z]);await line([x1,z],[x0,z]);await line([x0,z],[x0,z+base]);
 });
 await replace(765,766,async()=>{
  await line([9.12,z],[9.12,z+.52]);await line([9.12,z+.52],[seatStart,z+.52]);
  await arc([seatStart,z+.52],[seatStart+.52/Math.sqrt(2),z+.52/Math.sqrt(2)],[seatStart+.52,z]);await line([seatStart+.52,z],[9.12,z]);
 });
 for(const [body_id,feature_id] of [[173,782],[267,783]]) {
  const scene=await c.call('solid_scene'),body=scene.bodies.find(x=>x.id===body_id);
  if(!scene.errors.some(x=>x.feature_id===feature_id))continue;
  const edges=body.edges.filter(e=>{const adj=body.faces.filter(f=>f.edge_keys.includes(e.key)),zs=e.points.map(p=>p.z);return adj.some(f=>f.plane&&Math.abs(f.plane.normal[1])<1e-6)&&adj.some(f=>!f.plane)&&e.points.every(p=>Math.abs(p.y)>9.0499&&Math.abs(p.y)<10.5501)&&((Math.min(...zs)>20.5&&Math.max(...zs)<23.62)||(Math.max(...zs)<16&&Math.min(...zs)>12.88));});
  assert.equal(edges.length,8,JSON.stringify(edges.map(x=>x.key)));
  await apply('solid_edit_fillet',{feature_id,fillet:{body_id,edge_ids:edges.map(x=>x.id),radius:.25,tangent_chain:false}});
 }
 const scene=await c.call('solid_scene'),m=JSON.parse(await c.call('cad_project_model'));assert.deepEqual(scene.errors,[]);assert.equal(m.document.history.features.length,374);assert(m.document.history.features.every(f=>f.status.state==='ok'));assert.deepEqual(m.assembly,original.assembly);assert.deepEqual(m.views,original.views);
 await fs.writeFile(out+'/'+tag+'.model.json',await c.call('cad_project_model'));await fs.writeFile(out+'/'+tag+'-scene.json',JSON.stringify(scene));
 for(const id of [8,18,173,267,54]){const stl=await c.call('solid_export_stl',{body_ids:[id],scope:'definition',linear_deflection:.0005,angular_deflection:.04});await fs.writeFile(out+`/${tag}-${id}.stl`,Buffer.from(stl.bytes_base64,'base64'));}
 const step=await c.call('solid_export_step',{body_ids:[173]});await fs.writeFile(out+'/'+tag+'.step',Buffer.from(step.bytes_base64,'base64'));
 const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});await fs.writeFile(out+'/'+tag+'-fit.json',JSON.stringify(fit,null,2));
 const report={nub_protrusion_mm:protrusion,crest_radius_from_axis_mm:crest,crest_curve_radius_mm:R,outer_blend_radius_mm:outerR,meridian_span_mm:2*dx,holding_clearance_movement_mm:9.8+Math.sqrt(R**2-(b+R-crest)**2)-seatStart-Math.sqrt(.52**2-b**2),receiver_cap_start_abs_y_mm:seatStart,receiver_end_abs_y_mm:seatStart+.52,inner_hex_clearance_per_flat_mm:.10,corner_min_wall_mm:.897584,backing_mm:1.45,features:374,expected_interfering_pairs:fit.pairs.filter(p=>p.interfering).map(p=>[p.body_a,p.body_b,p.overlap_volume_mm3])};
 await fs.writeFile(out+'/'+tag+'-parameters.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}catch(e){await fs.writeFile(out+'/'+tag+'-failed.model.json',await c.call('cad_project_model'));await fs.writeFile(out+'/'+tag+'-failed-scene.json',JSON.stringify(await c.call('solid_scene')));throw e;}finally {await fs.writeFile(out+'/'+tag+'-receipts.json',JSON.stringify(receipts,null,2));c.close();}
