import fs from 'node:fs/promises';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
const angle=27.5*Math.PI/180,dxSlope=Math.tan(Math.PI/6),k=Math.sqrt(1/Math.tan(angle)**2-dxSlope**2),height=.2,width=height/k;
try{
 await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});
 const profiles=[];
 for(const [i,x] of [-5.55,-3.8,-2.05].entries()){
  const pl=await c.call('construction_plane_offset',{name:'Underside angled trial plane '+i,reference:{type:'origin_plane',plane:'yz'},distance:x});
  console.log('Plane',JSON.stringify(pl).slice(0,700));
  const defs=await c.call('construction_plane_definitions');const datum=defs.at(-1);
  const name='Underside angled trial section '+i;
  await c.call('sketch_begin',{name,plane:{type:'datum_plane',datum_id:datum.datum_id}});
  console.log('Basis',JSON.stringify(await c.call('sketch_active')).slice(0,600));
  const z=13.674499116672216+Math.abs(x+3.8)*dxSlope;
  const points=[[-(10.55-width),z-1],[-10.60,z-1],[-10.60,z+height+.05*k],[-(10.55-width),z]];
  for(let j=0;j<points.length;j++)await c.call('sketch_add_line',{from:{x:points[j][0],y:points[j][1]},to_raw:{x:points[(j+1)%points.length][0],y:points[(j+1)%points.length][1]},ctrl_held:true});
  await c.call('sketch_finish');profiles.push(name);
 }
 for(let i=0;i<2;i++)await c.call('solid_loft',{sections:[{sketch_name:profiles[i],profile_index:0},{sketch_name:profiles[i+1],profile_index:0}],ruled:true,continuity:'g0',operation:'cut',target_body_ids:[8]});
 const scene=await c.call('solid_scene');await fs.writeFile(out+'/angled-bevel-scene.json',JSON.stringify(scene));
 await fs.writeFile(out+'/angled-bevel.model.json',await c.call('cad_project_model'));
 await fs.writeFile(out+'/angled-bevel-fit.json',JSON.stringify(await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1}),null,2));
 await fs.writeFile(out+'/angled-bevel-section.json',JSON.stringify(await c.call('solid_section_review',{body_id:8,plane:'yz',offset_mm:-3.8,include_cutaway:true,deflection_mm:.002}),null,2));
 await fs.writeFile(out+'/angled-bevel-parameters.json',JSON.stringify({new_face_angle_from_vertical_deg:27.5,vertical_setback_mm:height,y_setback_mm:width,protrusion_mm:1.7,remaining_unbeveled_protrusion_mm:1.7-width,full_depth_required_vertical_setback_mm:1.7*k},null,2));
 const stl=await c.call('solid_export_stl',{body_ids:[8],scope:'definition',linear_deflection:.002,angular_deflection:.08});await fs.writeFile(out+'/angled-bevel-8.stl',Buffer.from(stl.bytes_base64,'base64'));
 console.log('Saved one-post angled experiment; canonical untouched');
}finally{c.close()}
