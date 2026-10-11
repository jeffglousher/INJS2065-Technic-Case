// Exact rigid-solid geometry screen, not a deformation or force solver.
// All pose changes occur in this disposable headless document, never the saved CAD.
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import { Client } from './mcp-client.mjs';

const root = new URL('../', import.meta.url);
const source = new URL('design/current.model.json', root);
const bytes = await fs.readFile(source);
const hash = buffer => crypto.createHash('sha256').update(buffer).digest('hex');
const reference = JSON.parse(await fs.readFile(new URL('review/current/cad-reference.json', root), 'utf8'));
assert.equal(hash(bytes), reference.canonicalModelSha256, 'Canonical source changed: review the study before rerunning');
const client = new Client(process.env.NBCAD_MCP_EXE || 'C:/Users/jeffg/AppData/Local/limo-cad/bevy/Limo-CAD.exe', 180000);
const offsets = [-.05, -.02, 0, .02, .04, .06, .08, .1, .2, .4, .6, .8, 1.2, 1.6, 2, 2.4, 2.5, 2.6, 2.7, 2.8];
const setOffset = async displacement => {
  for (const [id, sign] of [[273, 1], [274, -1]]) {
    await client.call('assembly_set_occurrence_pose', {
      occurrence_id: id,
      local_pose: {translation: [0, sign * displacement, 0], rotation: [0, 0, 0, 1]},
    });
  }
};

try {
  await client.start();
  const load = await client.call('cad_load_project_model', {model_json: bytes.toString('utf8')});
  assert(load.document.features.every(f => f.status.state === 'ok'));
  const samples = [];
  for (const offset of offsets) {
    await setOffset(offset);
    const fit = await client.call('assembly_interference_check', {
      occurrence_ids: [268, 269, 273, 274], clearance_threshold_mm: 0,
    });
    const pairs = fit.pairs.filter(p => [173, 267].includes(p.body_b) && [8, 18].includes(p.body_a));
    assert.equal(pairs.length, 4, 'Missing housing/clip pair; cannot interpret absent data as clear');
    assert(pairs.every(p => Number.isFinite(p.overlap_volume_mm3) && p.overlap_volume_mm3 >= 0));
    for (const shell of [8, 18]) {
      const positive = pairs.find(p => p.body_a === shell && p.body_b === 173);
      const negative = pairs.find(p => p.body_a === shell && p.body_b === 267);
      assert(Math.abs(positive.overlap_volume_mm3 - negative.overlap_volume_mm3) < 1e-6, 'Opposing clips disagree at the same rigid offset');
    }
    samples.push({outward_translation_mm: offset, pairs});
    if (samples.length % 5 === 0) console.log(`Checked ${samples.length}/${offsets.length} exact rigid poses on both sides.`);
  }
  await setOffset(0);
  const scene = await client.call('solid_scene');
  assert.deepEqual(scene.errors, []);
  for (const b of reference.bodies) {
    const actual = scene.bodies.find(x => x.id === b.id);
    assert.equal(actual.topology_signature, b.topologySignature);
    assert.equal(hash(JSON.stringify(actual.mesh)), b.meshSha256);
  }
  const seated = samples.find(s => s.outward_translation_mm === 0);
  for (const pair of seated.pairs) {
    const expected = reference.assemblyInterference.find(p => p.body_a === pair.body_a && p.body_b === pair.body_b);
    assert.equal(pair.overlap_volume_mm3, expected.overlap_volume_mm3, 'Seated contact changed');
  }
  const totals = samples.map(s => ({outward_translation_mm: s.outward_translation_mm,
    total_overlap_mm3: s.pairs.reduce((sum, p) => sum + p.overlap_volume_mm3, 0)}));
  const outward = totals.filter(s => s.outward_translation_mm >= 0);
  const peak = outward.reduce((a, b) => a.total_overlap_mm3 >= b.total_overlap_mm3 ? a : b);
  const clear = outward.find(s => s.total_overlap_mm3 === 0);
  assert(clear, 'Extend the sampling range before declaring a fully cleared pose');
  const peakPlateau = outward.filter(s => Math.abs(s.total_overlap_mm3 - peak.total_overlap_mm3) < 1e-6);
  assert.equal(hash(await fs.readFile(source)), hash(bytes), 'Saved source changed during audit');
  const result = {canonical_model_sha256: hash(bytes), method: 'Native OCCT exact overlap at 20 rigid poses; both clips translated along opposing CAD Y directions in an isolated document.',
    limits: 'Sampled translation path only, not a continuous collision proof. Whole-clip motion is not local corner flex. Overlap volume is not travel, strain, elastic energy, preload or force. No friction, deformation, material law or print tolerances are simulated.',
    geometry_changed: false, samples, totals, sampled_outward_peak: peak,
    sampled_peak_plateau_mm: peakPlateau.map(s => s.outward_translation_mm),
    first_sampled_clear_pose: clear};
  await fs.writeFile(new URL('review/current/contact-path.json', root), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({seated: totals.find(s => s.outward_translation_mm === 0), sampled_outward_peak: peak, first_sampled_clear_pose: clear}));
} finally { client.close(); }
