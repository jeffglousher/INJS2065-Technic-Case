import fs from 'node:fs/promises';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try{await c.start();await c.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});await fs.writeFile('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008/before-section.json',JSON.stringify(await c.call('solid_section_review',{body_id:8,plane:'yz',offset_mm:-3.8,deflection_mm:.002}),null,2));}finally{c.close()}
