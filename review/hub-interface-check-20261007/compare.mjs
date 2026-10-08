import fs from 'node:fs/promises';import crypto from 'node:crypto';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-interface-review-20261007';const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try {await c.start();const records=[];
for(const [name,file,id,plane,offset] of [['current-servo-mouth','C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json',54,'xy',27],['auger-servo-mouth',out+'/auger.model.json',216,'xz',151]]) {
 const source=await fs.readFile(file,'utf8');await c.call('cad_load_project_model',{model_json:source});
 const scene=await c.call('solid_scene');const body=scene.bodies.find(b=>b.id===id);if(!body)throw new Error('Missing reference body '+id);
 const section=await c.call('solid_section_review',{body_id:id,plane,offset_mm:offset,deflection_mm:.001,include_cutaway:true,keep_positive:true});
 await fs.writeFile(out+'/'+name+'.json',JSON.stringify(section));
 const cylinders=body.faces.filter(f=>f.cylinder).map(f=>({key:f.key,...f.cylinder}));
 records.push({name,source_sha256:crypto.createHash('sha256').update(source).digest('hex'),body_id:id,mesh_sha256:crypto.createHash('sha256').update(JSON.stringify(body.mesh)).digest('hex'),cylinders});
 console.log(name,section.bounds_mm,'native errors',scene.errors);
}
await fs.writeFile(out+'/comparison-source.json',JSON.stringify(records,null,2));
}finally{c.close();}
