import fs from 'node:fs/promises';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/root-ramp-20261008';
const raw=await fs.readFile(root+'/design/current.model.json','utf8'),angle=55*Math.PI/180,s=Math.tan(Math.PI/6),k=Math.sqrt(1/Math.tan(angle)**2-s*s),h=1.7*k;
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000),receipts=[];
async function apply(tool,args,label){const prev=await c.call('solid_scene'),ids=new Set(prev.bodies.map(b=>b.id));const r=await c.call(tool,args);const scene=await c.call('solid_scene');assert.deepEqual(scene.errors,[]);const m=JSON.parse(await c.call('cad_project_model')),feature=m.document.history.features.at(-1);if(label)await c.call('solid_rename_feature',{feature_id:feature.id,name:label});const added=scene.bodies.filter(b=>!ids.has(b.id)).map(b=>b.id);receipts.push({tool,args,feature_id:feature.id,added_body_ids:added,label});console.log(label||tool,added);return added;}
try{
 await c.start();await c.call('cad_load_project_model',{model_json:raw});const before=await c.call('solid_scene');await fs.writeFile(out+'/before-scene.json',JSON.stringify(before));const profiles=[];
 for(const [i,x] of [-5.55,-3.8,-2.05].entries()){
  await c.call('construction_plane_offset',{name:'Root support seed plane '+i,reference:{type:'origin_plane',plane:'yz'},distance:x});const defs=await c.call('construction_plane_definitions'),name='Root support seed section '+i;
  await c.call('sketch_begin',{name,plane:{type:'datum_plane',datum_id:defs.at(-1).datum_id}});
  const z=13.674499116672216+Math.abs(x+3.8)*s,points=[[8.85,z-1],[10.56,z-1],[10.56,z+h+.01*k],[8.85,z]];
  for(let j=0;j<points.length;j++)await c.call('sketch_add_line',{from:{x:-points[j][0],y:points[j][1]},to_raw:{x:-points[(j+1)%points.length][0],y:points[(j+1)%points.length][1]},ctrl_held:true});await c.call('sketch_finish');profiles.push(name);
 }
 const halves=[];for(let i=0;i<2;i++)halves.push(...await apply('solid_loft',{sections:[{sketch_name:profiles[i],profile_index:0},{sketch_name:profiles[i+1],profile_index:0}],ruled:true,continuity:'g0',operation:'new_body',target_body_ids:[]},'Form root ramp seed '+(i===0?'left':'right')+' flank - 55 deg'));
 assert.equal(halves.length,2);await apply('solid_combine',{target_body_id:halves[0],tool_body_ids:[halves[1]],operation:'join',keep_tools:false},'Unify root support seed');
 const lowerMinus=[halves[0],...await apply('solid_rectangular_pattern',{body_ids:[halves[0]],direction:{x:1,y:0,z:0},spacing:5.9,count:4},'Repeat four hex root supports')];assert.equal(lowerMinus.length,4);
 const lower=[...lowerMinus,...await apply('solid_mirror',{body_ids:lowerMinus,plane:{type:'origin_plane',plane:'xz'}},'Mirror supports to opposite lower side')];assert.equal(lower.length,8);
 await c.call('construction_plane_offset',{name:'Clamshell symmetry for root supports',reference:{type:'origin_plane',plane:'xy'},distance:18.25});const datum=(await c.call('construction_plane_definitions')).at(-1);
 const upper=await apply('solid_mirror',{body_ids:lower,plane:{type:'datum_plane',datum_id:datum.datum_id}},'Mirror eight supports to upper clamshell');assert.equal(upper.length,8);
 await apply('solid_move_copy',{body_ids:upper,translation:{x:2.95,y:0,z:0},rotation:[0,0,0,1],pivot:{x:0,y:0,z:0},copy:false},'Align upper bevels to staggered hex row');
 await apply('solid_combine',{target_body_id:8,tool_body_ids:lower,operation:'cut',keep_tools:false},'Bevel lower hex undersides from root - 55 deg');
 await apply('solid_combine',{target_body_id:18,tool_body_ids:upper,operation:'cut',keep_tools:false},'Bevel upper hex undersides from root - 55 deg');
 await c.call('recall_named_view',{name:'Assembled ISO'});
 const scene=await c.call('solid_scene'),final=await c.call('cad_project_model'),m=JSON.parse(final);assert.deepEqual(scene.errors,[]);assert.equal(scene.bodies.length,7);assert(m.document.history.features.every(f=>f.status.state==='ok'));const oldAssembly=structuredClone(JSON.parse(raw).assembly),newAssembly=structuredClone(m.assembly);for(const a of [oldAssembly,newAssembly]){delete a.component_structure.next_component_id;delete a.component_structure.next_occurrence_id;}assert.deepEqual(newAssembly,oldAssembly);
 for(const id of [1,53,54,173,267])assert.deepEqual(scene.bodies.find(b=>b.id===id).mesh,before.bodies.find(b=>b.id===id).mesh);
 await fs.writeFile(out+'/candidate.model.json',final);await fs.writeFile(out+'/candidate-scene.json',JSON.stringify(scene));
 const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});await fs.writeFile(out+'/candidate-fit.json',JSON.stringify(fit,null,2));
 const ref=JSON.parse(await fs.readFile(root+'/review/print-layout.json','utf8'));assert.equal(fit.pairs.length,ref.assemblyInterference.length);
 for(const [i,p] of fit.pairs.entries()){const b=ref.assemblyInterference[i];assert.equal(p.interfering,b.interfering);assert.equal(p.below_clearance,b.below_clearance);assert(Math.abs(p.overlap_volume_mm3-b.overlap_volume_mm3)<1e-9,'Additional clip interference');}
 for(const id of [8,18]){const stl=await c.call('solid_export_stl',{body_ids:[id],scope:'definition',linear_deflection:.002,angular_deflection:.08});await fs.writeFile(out+'/root-ramp-'+id+'.stl',Buffer.from(stl.bytes_base64,'base64'));}
 for(const [name,id,x] of [['lower',8,-3.8],['upper',18,-3.8]])await fs.writeFile(out+'/'+name+'-root-section.json',JSON.stringify(await c.call('solid_section_review',{body_id:id,plane:'yz',offset_mm:x,deflection_mm:.002}),null,2));
 await fs.writeFile(out+'/build-audit.json',JSON.stringify({source_model_sha256:crypto.createHash('sha256').update(raw).digest('hex'),candidate_model_sha256:crypto.createHash('sha256').update(final).digest('hex'),source_commit:'f85e290',angle_from_vertical_deg:55,projection_mm:1.7,root_height_mm:h,profile_slope_x:s,profile_slope_y:k,feature_count:m.document.history.features.length,body_count:7,assembly_structure_and_poses_unchanged:true,other_five_bodies_unchanged:true,nominal_contact_volumes_preserved:true,receipts},null,2));
 console.log('PASS all 16 root supports; unchanged expected contacts',m.document.history.features.length);
}finally{c.close()}
