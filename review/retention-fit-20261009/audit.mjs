import fs from 'node:fs/promises';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/retention-fit-20261009',c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000),sha=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
try {
 await c.start();const raw=await fs.readFile(out+'/candidate.model.json','utf8'),m=JSON.parse(raw),base=JSON.parse(await fs.readFile(out+'/baseline.model.json','utf8'));
 const loaded=await c.call('cad_load_project_model',{model_json:raw}),s=await c.call('solid_scene'),old=JSON.parse(await fs.readFile(out+'/baseline-scene.json','utf8'));
 assert.deepEqual(s.errors,[]);assert.equal(s.bodies.length,7);assert.equal(loaded.document.features.length,390);assert(loaded.document.features.every(f=>f.status.state==='ok'));
 const preserved=[1,53,54];for(const id of preserved)assert.equal(sha(s.bodies.find(b=>b.id===id).mesh),sha(old.bodies.find(b=>b.id===id).mesh));
 assert.deepEqual(m.assembly,base.assembly);assert.deepEqual(m.views,base.views);
 const sections=[];
 for(const id of [173,267,8,18])for(const mag of [9.8,10.05,10.14240656,10.55,12]){
  const y=id===267?-mag:mag,r=await c.call('solid_section_review',{body_id:id,plane:'xz',offset_mm:y,deflection_mm:.001});await fs.writeFile(out+`/section-${id}-${mag}.json`,JSON.stringify(r));sections.push({body:id,Y_mm:y,outcome:r.outcome});
 }
 for(const [id,x] of [[173,-.85],[18,-.85],[173,-1.0366025403784445],[18,-1.0366025403784445]])await fs.writeFile(out+`/side-${id}-${x}.json`,JSON.stringify(await c.call('solid_section_review',{body_id:id,plane:'yz',offset_mm:x,deflection_mm:.001,include_cutaway:true,keep_positive:true})));
 const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});assert.deepEqual(fit.pairs.filter(p=>p.interfering).map(p=>[p.body_a,p.body_b]),[[8,173],[8,267],[18,173],[18,267]]);
 const travel=[];for(const dy of [1.4,1.0,.75,.5,.3,.1,0]){await c.call('assembly_set_occurrence_pose',{occurrence_id:273,local_pose:{translation:[0,dy,0],rotation:[0,0,0,1]}});const f=await c.call('assembly_interference_check',{occurrence_ids:[268,269,273],clearance_threshold_mm:0});travel.push({translation_Y_mm:dy,interfering_pairs:f.pairs.filter(x=>x.interfering)});}
 await fs.writeFile(out+'/insertion.json',JSON.stringify(travel,null,2));
 const report={all_390_features_ok:true,body_count:7,preserved_exact_mesh_body_ids:preserved,assembly_and_named_views_unchanged:true,fit,sections,bodies:s.bodies.map(b=>({id:b.id,topologySignature:b.topology_signature,meshSha256:sha(b.mesh)}))};await fs.writeFile(out+'/geometry-audit.json',JSON.stringify(report,null,2));
 console.log('PASS 390 features, seven bodies, three untouched exact meshes, original assembly/views, four intended contact pairs.');
 // Save a separate native coupon. Keep the complete clip to reproduce its frame stiffness.
 await c.call('cad_load_project_model',{model_json:raw});for(const id of [8,18])await c.call('solid_box',{name:`Coupon crop body ${id}`,origin:[-8,6,8],size:[29,6,19.6],operation:'intersect',target_body_ids:[id]});
 const coupon=await c.call('solid_scene');assert.deepEqual(coupon.errors,[]);await fs.writeFile(out+'/coupon.model.json',await c.call('cad_project_model'));await fs.writeFile(out+'/coupon-scene.json',JSON.stringify(coupon));
 for(const id of [8,18]){const stl=await c.call('solid_export_stl',{body_ids:[id],scope:'definition',linear_deflection:.0005,angular_deflection:.04});await fs.writeFile(out+`/coupon-${id}.stl`,Buffer.from(stl.bytes_base64,'base64'));}
 console.log('PASS native coupon crops; full clip retained; clamshell halves kept separate for their original build directions.');
}finally {c.close();}
