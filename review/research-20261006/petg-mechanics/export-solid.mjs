import fs from 'node:fs/promises';
import { Client } from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const root='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005';
const client=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/nbcad-mcp.exe',180000);
try {
  await client.start();
  const tools=await client.call('cad_list_all_tools',{});
  await client.call('cad_load_project_model',{model_json:await fs.readFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json','utf8')});
  const scene=await client.call('solid_scene',{});
  await fs.writeFile(root+'/scene.json',JSON.stringify(scene));
  const result=await client.call('solid_export_step',{body_ids:[173]});
  console.log(JSON.stringify({keys:Object.keys(result)}));
  await fs.writeFile(root+'/current.step',Buffer.from(result.bytes_base64,'base64'));
} finally {client.close();}
