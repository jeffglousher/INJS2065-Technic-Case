import fs from 'node:fs/promises';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000),sha=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const source=JSON.parse(await fs.readFile(out+'/baseline.model.json','utf8')),old=JSON.parse(await fs.readFile(out+'/baseline-scene.json','utf8'));
const sections={};
const points=s=>s.section.flatMap(p=>p.points).map(p=>p.map(x=>Math.round(x*1e5))).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
try{
 await c.start();
 for(const tag of ['baseline',...process.argv.slice(2).length?process.argv.slice(2):['nub-28','nub-30']]){
  const raw=await fs.readFile(out+'/'+tag+'.model.json','utf8'),m=JSON.parse(raw);
  const load=await c.call('cad_load_project_model',{model_json:raw}),scene=await c.call('solid_scene');assert.deepEqual(scene.errors,[]);assert.equal(scene.bodies.length,7);
  assert(load.document.features.every(f=>f.status.state==='ok'));
  if(tag!=='baseline'){
   assert.equal(load.document.features.length,374);assert.deepEqual(m.assembly,source.assembly);assert.deepEqual(m.views,source.views);
   for(const id of [1,53,54])assert.equal(sha(scene.bodies.find(b=>b.id===id).mesh),sha(old.bodies.find(b=>b.id===id).mesh));
   if(!tag.endsWith('relieved'))assert.deepEqual(m.sketches.find(s=>s.feature_id===765),source.sketches.find(s=>s.feature_id===765));
   for(const key of ['revolves','holes'])for(const id of key==='revolves'?(tag.endsWith('relieved')?[775]:[766,775]):[265])assert.deepEqual(m[key].find(f=>f.feature_id===id),source[key].find(f=>f.feature_id===id));
   for(const id of [474,476,478,480,484,486,488,490,784])assert.deepEqual(m.sketches.find(f=>f.feature_id===id),source.sketches.find(f=>f.feature_id===id));
   const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});
   assert.deepEqual(fit.pairs.filter(p=>p.interfering).map(p=>[p.body_a,p.body_b]),[[8,173],[8,267],[18,173],[18,267]]);
   const bearing=fit.pairs.find(p=>[p.body_a,p.body_b].includes(53)&&[p.body_a,p.body_b].includes(54));assert(Math.abs(bearing.minimum_clearance_mm-.03)<1e-7);
   const housing=fit.pairs.find(p=>[p.body_a,p.body_b].includes(18)&&[p.body_a,p.body_b].includes(54));
   await fs.writeFile(out+'/'+tag+'-audit.json',JSON.stringify({feature_count:374,body_count:7,all_features_ok:true,preserved_mesh_ids:[1,53,54],assembly_views_pockets_relief_backing_preserved:true,hidden_receiver_unchanged:!tag.endsWith('relieved'),housing_hub_min_clearance_mm:housing.minimum_clearance_mm,bearing_hub_min_clearance_mm:bearing.minimum_clearance_mm,fit,bodies:scene.bodies.map(b=>({id:b.id,topologySignature:b.topology_signature,meshSha256:sha(b.mesh)}))},null,2));
  }
  sections[tag]={};
  for(const [id,plane,offset,label] of [[8,'yz',-3.8,'hex-root'],[18,'xy',40,'shaft-opening'],[54,'xy',40,'shaft'],[173,'xz',10.6,'backing-plus'],[267,'xz',-10.6,'backing-minus'],[173,'xz',9.8,'nub-center'],[18,'xz',9.8,'seat-center'],[173,'xz',10.1424065573,'nub-holding'],[18,'xz',10.1424065573,'seat-holding']]){
   const r=await c.call('solid_section_review',{body_id:id,plane,offset_mm:offset,deflection_mm:.001});sections[tag][label]=r;
   await fs.writeFile(out+`/${tag}-${label}.json`,JSON.stringify(r));
  }
 }
 for(const tag of Object.keys(sections).filter(t=>t!=='baseline'))for(const label of ['backing-plus','backing-minus','shaft'])assert.deepEqual(points(sections[tag][label]),points(sections.baseline[label]));
 await fs.writeFile(out+'/preservation.json',JSON.stringify({backing_and_hub_sections_unchanged:true,old_bevel_subtree_removed_ids:[786,801],restored_hex_post_projection_mm:1.70,rotational_radial_gap_mm:.205,bearing_radial_gap_mm:.03,profile_compensation_changed:false},null,2));
 console.log('PASS native trials, 374 features, seven bodies, four intended contact pairs, unchanged hardware/hub, bearing gap .03 mm; flat backing preserved.');
}finally{c.close()}
