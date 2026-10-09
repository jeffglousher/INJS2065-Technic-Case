import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const repo='C:/Users/jeffg/dev/INJS2065-Technic-Case',out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009';
const bytes=await fs.readFile(repo+'/design/current.model.json','utf8'),ref=JSON.parse(await fs.readFile(repo+'/review/flat-clip-base.json','utf8'));
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
try {
 await c.start();
 const load=await c.call('cad_load_project_model',{model_json:bytes}),scene=await c.call('solid_scene',{});
 const fit=await c.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});
 const report={source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),source_unchanged:crypto.createHash('sha256').update(bytes).digest('hex')===ref.canonicalModelSha256,features:load.document.features.length,all_features_ok:load.document.features.every(f=>f.status.state==='ok'),errors:scene.errors,bodies:scene.bodies.map(b=>{const r=ref.bodies.find(x=>x.id===b.id);return {id:b.id,topology_matches:JSON.stringify(b.topology_signature)===JSON.stringify(r.topologySignature),mesh_matches:crypto.createHash('sha256').update(JSON.stringify(b.mesh)).digest('hex')===r.meshSha256,mesh_sha256:crypto.createHash('sha256').update(JSON.stringify(b.mesh)).digest('hex')}}),assembly_pairs_match:JSON.stringify(fit.pairs)===JSON.stringify(ref.assemblyInterference),fit};
 await fs.writeFile(out+'/replay-audit.json',JSON.stringify(report,null,2));await fs.writeFile(out+'/replay-scene.json',JSON.stringify(scene));console.log(JSON.stringify({all_features_ok:report.all_features_ok,source_unchanged:report.source_unchanged,bodies:report.bodies,assembly_pairs_match:report.assembly_pairs_match},null,2));
}finally{c.close()}
