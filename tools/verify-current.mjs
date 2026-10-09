import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { Client } from './mcp-client.mjs';

const base = new URL('../', import.meta.url);
const read = async path => JSON.parse(await fs.readFile(new URL(path, base), 'utf8'));
const modelBytes = await fs.readFile(new URL('design/current.model.json', base));
const model = JSON.parse(modelBytes);
const reference = await read('review/retention-fit.json');
const cleanup = await read(reference.preservedReference);
const binary = process.env.NBCAD_MCP_EXE || 'C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe';
const client = new Client(binary, 180000);

try {
  const modelHash = crypto.createHash('sha256').update(modelBytes).digest('hex');
  assert.equal(modelHash, reference.canonicalModelSha256, 'Canonical model bytes differ from the reviewed source');
  await client.start();
  const load = await client.call('cad_load_project_model', { model_json: JSON.stringify(model) });
  const scene = await client.call('solid_scene', {});
  assert.deepEqual(scene.errors, []);
  assert.equal(scene.bodies.length, reference.bodyCount);
  for (const expected of reference.bodies) {
    const body = scene.bodies.find(item => item.id === expected.id);
    assert(body, 'Missing body ' + expected.id);
    assert.equal(body.topology_signature, expected.topologySignature, 'Topology changed for body ' + body.id);
    const hash = crypto.createHash('sha256').update(JSON.stringify(body.mesh)).digest('hex');
    assert.equal(hash, expected.meshSha256, 'Mesh changed for body ' + body.id);
    if (reference.preservedBodyIds.includes(body.id)) {
      const original = cleanup.bodies.find(item => item.id === body.id);
      assert.equal(hash, original.meshSha256, 'Unrequested geometry change for body ' + body.id);
      assert.equal(body.topology_signature, original.topologySignature);
    }
  }
  assert.equal(load.document.features.length, reference.featureCountAfter);
  assert(load.document.features.every(feature => feature.status.state === 'ok'));
  const fit = await client.call('assembly_interference_check', {
    occurrence_ids: [268, 269, 270, 271, 272, 273, 274],
    clearance_threshold_mm: 0.1,
  });
  assert.deepEqual(fit.pairs, reference.assemblyInterference);
  console.log(`PASS: ${reference.featureCountAfter} features; ${reference.bodyCount} reviewed meshes/topologies; ${reference.preservedBodyIds.length} preserved bodies unchanged; expected assembly contacts; zero native errors.`);
} finally {
  client.close();
}
