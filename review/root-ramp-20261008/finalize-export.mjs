import fs from 'node:fs/promises';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/root-ramp-20261008',c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try{
 await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile(out+'/candidate.model.json','utf8')});const before=await c.call('solid_scene');
 const model=JSON.parse(await c.call('cad_project_model'));
 for(const f of model.document.history.features.filter(f=>f.id>=786&&!['construction_plane','sketch'].includes(f.kind))){
  const name=f.name.replace('Root support seed','Root bevel cutter').replace('root support seed','root bevel cutter').replace('root supports','root bevel cutters').replace('supports to','bevel cutters to');
  if(name!==f.name)await c.call('solid_rename_feature',{feature_id:f.id,name});
 }
 const scene=await c.call('solid_scene');assert.deepEqual(scene.errors,[]);for(const b of before.bodies)assert.deepEqual(b.mesh,scene.bodies.find(n=>n.id===b.id).mesh);
 const raw=await c.call('cad_project_model');await fs.writeFile(out+'/candidate.model.json',raw);await fs.writeFile(out+'/candidate-scene.json',JSON.stringify(scene));
 await fs.writeFile(out+'/candidate-fit.json',JSON.stringify(await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1}),null,2));
 for(const [name,id,x] of [['lower',8,-3.8],['upper',18,-.85]]){
  const stl=await c.call('solid_export_stl',{body_ids:[id],scope:'definition',linear_deflection:.0005,angular_deflection:.04});await fs.writeFile(out+'/root-ramp-'+id+'.stl',Buffer.from(stl.bytes_base64,'base64'));
  await fs.writeFile(out+'/'+name+'-root-section.json',JSON.stringify(await c.call('solid_section_review',{body_id:id,plane:'yz',offset_mm:x,deflection_mm:.002}),null,2));
 }
 const audit=JSON.parse(await fs.readFile(out+'/build-audit.json','utf8'));audit.candidate_model_sha256=crypto.createHash('sha256').update(raw).digest('hex');audit.export_linear_deflection_mm=.0005;audit.export_angular_deflection_rad=.04;audit.named_views=JSON.parse(raw).views.map(v=>v.name);await fs.writeFile(out+'/build-audit.json',JSON.stringify(audit,null,2));console.log('PASS fresh replay and fine exports; all seven meshes preserved during naming');
}finally{c.close()}
