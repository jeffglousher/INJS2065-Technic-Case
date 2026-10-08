import fs from 'node:fs/promises';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {Client} from 'file:///C:/Users/jeffg/dev/INJS2065-Technic-Case/tools/mcp-client.mjs';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-friction-20261007';
const c=new Client('C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe',180000);
const norm=points=>{const p=points.map(v=>v.map(x=>Math.round(x*1e7)));return [JSON.stringify(p),JSON.stringify([...p].reverse())].sort()[0]};
try{await c.start();const bytes=await fs.readFile(root+'/design/current.model.json');await c.call('cad_load_project_model',{model_json:bytes.toString()});
const section=await c.call('solid_section_review',{body_id:54,plane:'xy',offset_mm:40,deflection_mm:.001,include_cutaway:false,keep_positive:true});
const old=JSON.parse(await fs.readFile(root+'/review/assembly-print-20261007/hub-socket.json'));
const cross=d=>d.section.filter(e=>e.points.every(p=>Math.max(Math.abs(p[0]),Math.abs(p[1]))<=2.42500001)).map(e=>norm(e.points)).sort();
assert.equal(cross(section).length,12);assert.deepEqual(cross(section),cross(old));
const axial=JSON.parse(await fs.readFile(root+'/review/hub-friction-20261007/hub-axial.json'));const priorAxial=JSON.parse(await fs.readFile(root+'/review/assembly-print-20261007/hub-axial.json'));
const innerAxial=d=>d.section.filter(e=>e.points.every(p=>Math.abs(p[0])<=2.42500001&&p[1]>=33.999999)).map(e=>norm(e.points)).sort();assert.equal(innerAxial(axial).length,3);assert.deepEqual(innerAxial(axial),innerAxial(priorAxial));
await fs.writeFile(out+'/confirmed-technic-section.json',JSON.stringify(section));
await fs.writeFile(out+'/native-interface-confirmation.json',JSON.stringify({canonicalModelSha256:crypto.createHash('sha256').update(bytes).digest('hex'),crossSectionPlane:'world Z40 mm',crossProfileEdgeCount:12,normalizedNativeSectionMatchesPrevious:true,axialCrossSocketEdgesMatchPrevious:true,crossSpanMm:4.85,crossArmWidthMm:1.85,crossSocketDepthMm:8.0,nativeGeometryChanged:false},null,2));
console.log('PASS: native 12-edge Technic cross profile and 8 mm axial socket match the previous reviewed geometry');
}finally{c.close()}
