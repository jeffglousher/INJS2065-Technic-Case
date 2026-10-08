import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
// Rebuild from the canonical native history or a recovered pre-change model.
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000),receipts=[];
async function apply(name,args,allowedStale=[]){try{await c.call(name,args);}catch(error){const scene=await c.call('solid_scene');assert(scene.errors.length>0&&scene.errors.every(e=>allowedStale.includes(e.feature_id)&&e.message==='referenced fillet edge no longer exists'),error.message);}receipts.push({name,args});}
try{
 await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile(process.argv[2]||root+'/design/current.model.json','utf8')});
 let m=JSON.parse(await c.call('cad_project_model')),s=m.sketches.find(s=>s.feature_id===784),name=s.name;
 await apply('sketch_edit',{name});await apply('sketch_delete_entities',{entity_ids:s.snapshot.entities.map(e=>e[0])});
 const pts=[[-.85,10.55],[1.15,10.55],[1.15,9],[-.85,9]];
 for(let i=0;i<4;i++)await apply('sketch_add_line',{from:{x:pts[i][0],y:pts[i][1]},to_raw:{x:pts[(i+1)%4][0],y:pts[(i+1)%4][1]},ctrl_held:true});
 await apply('sketch_finish',{});const p=(await c.call('sketch_profiles')).find(p=>p.sketch_name===name);assert.equal(p.profiles.length,1);
 const r=m.revolves.find(r=>r.feature_id===775),{axis_origin,axis_direction,angle_deg,flip,operation,target_body_ids}=r;
 // Editing the source changes the dependent edge signatures. Rebind only the
 // two known R0.25 sidewall fillets, then require a completely valid replay.
 await apply('solid_edit_revolve',{feature_id:775,revolve:{sketch_name:name,profile_indices:[p.profiles[0].index],axis_origin,axis_direction,angle_deg,flip,operation,target_body_ids}},[782,783]);
 for(const [body_id,feature_id] of [[173,782],[267,783]]){
  const scene=await c.call('solid_scene'),b=scene.bodies.find(b=>b.id===body_id),edges=b.edges.filter(e=>{
   const adjacent=b.faces.filter(f=>f.edge_keys.includes(e.key)),z=e.points.map(p=>p.z);
   return adjacent.some(f=>f.plane&&Math.abs(f.plane.normal[1])<1e-6)&&adjacent.some(f=>!f.plane)&&e.points.every(p=>Math.abs(p.y)>9.0499&&Math.abs(p.y)<10.5501)&&((Math.min(...z)>21&&Math.max(...z)<23.62)||(Math.max(...z)<15.5&&Math.min(...z)>12.88));
  });assert.equal(edges.length,8);
  await apply('solid_edit_fillet',{feature_id,fillet:{body_id,edge_ids:edges.map(e=>e.id),radius:.25,tangent_chain:false}},feature_id===782?[783]:[]);
 }
 await apply('solid_rename_feature',{feature_id:784,name:'Corner wall relief - R2, flat floor, 1.45 mm backing'});
 await apply('solid_rename_feature',{feature_id:775,name:'Form corner wall relief - stop at flat pocket floor'});
 const scene=await c.call('solid_scene');assert.deepEqual(scene.errors,[]);assert.equal(scene.bodies.length,7);m=JSON.parse(await c.call('cad_project_model'));assert.equal(m.document.history.features.length,390);assert(m.document.history.features.every(f=>f.status.state==='ok'));
 await fs.mkdir(out,{recursive:true});await fs.writeFile(out+'/rebuilt.model.json',await c.call('cad_project_model'));await fs.writeFile(out+'/rebuild-receipts.json',JSON.stringify(receipts,null,2));console.log('PASS edited existing cutter; rebound eight blends per clip; no new timeline features');
}finally{c.close()}
