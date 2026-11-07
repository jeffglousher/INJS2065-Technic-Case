// Export only the reviewed model in an isolated headless process; never attach to a desktop.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { Client, cadExecutable } from './mcp-client.mjs';

const base = new URL('../', import.meta.url);
const source = await fs.readFile(new URL('design/current.model.json', base));
const reference = JSON.parse(await fs.readFile(new URL('docs/model-reference.json', base)));
assert.equal(crypto.createHash('sha256').update(source).digest('hex'), reference.canonicalModelSha256);
const client = new Client(cadExecutable(), 180000);
try {
  await client.start();
  await client.call('cad_load_project_model', {model_json: source.toString()});
  const scene = await client.call('solid_scene');
  assert.deepEqual(scene.errors, []);
  assert.equal(scene.bodies.length, reference.bodyCount);
  // Printable render geometry comes from the exact reviewed 3MF, not a rebuild.
  // Require the two purchased reference bodies to retain their original meshes.
  for (const expected of reference.bodies.filter(b => [1,53].includes(b.id))) {
    const body = scene.bodies.find(b => b.id === expected.id);
    assert(body, `Missing body ${expected.id}`);
    assert.equal(crypto.createHash('sha256').update(JSON.stringify(body.mesh)).digest('hex'), expected.meshSha256,
      `Body ${expected.id} differs from the reviewed source`);
  }
  const raw = JSON.stringify(scene);
  assert(Buffer.byteLength(raw) < 50 * 1024 * 1024, 'Gallery scene exceeds its 50 MiB budget');
  await fs.mkdir(new URL('local/', base), {recursive:true});
  await fs.writeFile(new URL('local/readme-gallery-scene.json', base), raw);
  await fs.writeFile(new URL('local/readme-gallery-proof.json', base), JSON.stringify({
    scene_sha256:crypto.createHash('sha256').update(raw).digest('hex'),
    model_sha256:reference.canonicalModelSha256,
    hardware_mesh_sha256:Object.fromEntries(reference.bodies.filter(b => [1,53].includes(b.id)).map(b => [b.id,b.meshSha256])),
  },null,2));
  console.log(`Verified both hardware reference meshes; exported a temporary ${scene.bodies.length}-body scene (${Buffer.byteLength(raw)} bytes). Use the reviewed 3MF for printable geometry.`);
} finally {
  client.close();
}
