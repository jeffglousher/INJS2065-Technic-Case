import fs from 'node:fs/promises';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/assembly-print-20261008';const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try {await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});
for(const [name,plane,offset] of [['hub-axial','xz',0],['hub-socket','xy',40]]){const r=await c.call('solid_section_review',{body_id:54,plane,offset_mm:offset,deflection_mm:.001,include_cutaway:true,keep_positive:true});await fs.writeFile(out+'/'+name+'.json',JSON.stringify(r));console.log(name,Object.keys(r));}
}finally{c.close();}
