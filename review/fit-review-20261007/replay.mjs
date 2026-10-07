import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { Client } from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const repo='C:/Users/jeffg/dev/INJS2065-Technic-Case';
const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/fit-review-20261007';
const client=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/nbcad-mcp.exe',180000);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
try {
  await fs.mkdir(out,{recursive:true});
  await client.start();
  const model=await fs.readFile(repo+'/design/current.model.json','utf8');
  const ref=JSON.parse(await fs.readFile(repo+'/review/local-corner-flex.json','utf8'));
  const load=await client.call('cad_load_project_model',{model_json:model});
  const scene=await client.call('solid_scene');
  assert.deepEqual(scene.errors,[]);
  assert.equal(load.document.features.length,401);
  assert(load.document.features.every(f=>f.status.state==='ok'));
  for(const expected of ref.bodies){
    const body=scene.bodies.find(b=>b.id===expected.id);
    assert.equal(sha(JSON.stringify(body.mesh)),expected.meshSha256);
    assert.equal(body.topology_signature,expected.topologySignature);
  }
  await fs.writeFile(out+'/scene.json',JSON.stringify(scene));
  const fit=await client.call('assembly_interference_check',{occurrence_ids:[268,269,270,271,272,273,274],clearance_threshold_mm:.1});
  assert.deepEqual(fit.pairs,ref.assemblyInterference);
  const files=[];
  for(const [name,ids] of [['clip',[173]],['housing',[8,18]]]){
    const result=await client.call('solid_export_stl',{body_ids:ids,scope:'definition',linear_deflection:.002,angular_deflection:.08});
    const bytes=Buffer.from(result.bytes_base64,'base64');
    await fs.writeFile(out+'/'+name+'.stl',bytes);
    files.push({file:name+'.stl',sha256:sha(bytes),triangles:bytes.readUInt32LE(80)});
  }
  const report={reviewedAt:new Date().toISOString(),canonicalModelSha256:sha(model),featureCount:401,bodyCount:scene.bodies.length,nativeErrors:[],geometryModified:false,allReviewedMeshAndTopologySignaturesMatch:true,tessellation:{linear_deflection_mm:.002,angular_deflection_rad:.08},assemblyInterference:fit.pairs,files};
  await fs.writeFile(out+'/replay.json',JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{client.close();}
