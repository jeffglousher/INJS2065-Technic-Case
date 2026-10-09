import fs from 'node:fs/promises';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try {
 await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});
 await c.call('solid_box',{name:'Independent local nub crop',origin:[-1.45,9.5,24.103961852410437],size:[1.2,.8,1.2],operation:'intersect',target_body_ids:[173]}); const rows=[];
 for(const dy of [0,-.02,-.025,-.03,-.035,-.04,-.045,-.05,-.06,-.08,-.1,-.2,-.36]) {
  await c.call('assembly_set_occurrence_pose',{occurrence_id:273,local_pose:{translation:[0,dy,0],rotation:[0,0,0,1]}});
  const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,273],clearance_threshold_mm:0});
  rows.push({dy,pairs:fit.pairs.filter(p=>p.body_a===173||p.body_b===173)});
  console.log(JSON.stringify(rows.at(-1)));
 }
 await fs.writeFile('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/retention-fit-20261009/independent-local-nub-translation.json',JSON.stringify(rows,null,2));
}finally{c.close()}
