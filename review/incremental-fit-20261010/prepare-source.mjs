import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out=new URL('./',import.meta.url);
const raw=await fs.readFile(root+'/design/current.model.json','utf8'),m=JSON.parse(raw);
await fs.writeFile(new URL('baseline.model.json',out),raw);
assert.equal(m.document.history.features.length,390);
const removed=m.document.history.features.filter(f=>f.id>=786);assert.equal(removed.length,16);assert.equal(removed.at(-1).id,801);
// The complete terminal subtree exists only to make and consume 16 bevel cutters.
// Remove its history and definitions together, retaining all pre-existing IDs.
m.document.history.features=m.document.history.features.filter(f=>f.id<786);
m.document.history.rollback_index=m.document.history.features.length;
for(const key of ['sketches','datum_planes','lofts','body_features'])m[key]=m[key].filter(f=>f.feature_id<786);
const hole=m.holes.find(h=>h.feature_id===94);assert.equal(hole.diameter,8.15);hole.diameter=8.35;
await fs.writeFile(new URL('base-unbeveled.model.json',out),JSON.stringify(m));
console.log('Prepared removal of 16 terminal bevel features and housing aperture 8.15 -> 8.35 mm');
