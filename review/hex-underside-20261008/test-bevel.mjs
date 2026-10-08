import fs from 'node:fs/promises';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008';
await fs.mkdir(out,{recursive:true});
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try {
 await c.start();
 await c.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});
 const before=await c.call('solid_scene');await fs.writeFile(out+'/before-scene.json',JSON.stringify(before));
 const selected=[];
 for(const id of [8,18]){
  const b=before.bodies.find(b=>b.id===id),flip=id===8?1:-1;
  const ids=new Set();
  for(const f of b.faces){
   if(!f.plane||f.plane.normal[2]*flip>-.8)continue;
   const centroid=f.signature?.centroid;
   if(!centroid||Math.abs(centroid.y)<8.8||centroid.z<10||centroid.z>28)continue;
   for(const key of f.edge_keys){const e=b.edges.find(e=>e.key===key);const p=e.points;
    if(p.length!==2)continue;
    if(Math.abs(p[0].y-p[1].y)<1e-6&&Math.abs(p[0].y)>10.5)ids.add(e.id);
   }
  }
  selected.push({body_id:id,edge_ids:[...ids],distance:.2,tangent_chain:false});
 }
 await fs.writeFile(out+'/equal-bevel-input.json',JSON.stringify(selected,null,2));
 for(const req of selected){console.log('Bevel',req.body_id,req.edge_ids.length);await c.call('solid_chamfer',req);}
 const after=await c.call('solid_scene');await fs.writeFile(out+'/equal-bevel-scene.json',JSON.stringify(after));
 await fs.writeFile(out+'/equal-bevel.model.json',await c.call('cad_project_model'));
 await fs.writeFile(out+'/equal-bevel-fit.json',JSON.stringify(await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1}),null,2));
 for(const id of [8,18]){const result=await c.call('solid_export_stl',{body_ids:[id],scope:'definition',linear_deflection:.002,angular_deflection:.08});await fs.writeFile(out+'/equal-bevel-'+id+'.stl',Buffer.from(result.bytes_base64,'base64'));}
 console.log('Saved experimental equal-distance bevel; canonical untouched');
}finally{c.close()}
