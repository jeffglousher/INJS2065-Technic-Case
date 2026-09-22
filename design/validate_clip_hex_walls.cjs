#!/usr/bin/env node
/**
 * v16.48 clip coplanar clamp-face audit.
 * Parses the JSONC tip and checks the boolean construction, not comments.
 * Circumscribed sketch radius is the hex apothem. rotation 0 is pointy-top
 * (vertex along sketch +Y = world +Z, vertical flats parallel to Z).
 *
 * Run: node design/validate_clip_hex_walls.cjs
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TIP = path.join(__dirname, "design_v16_48.nbcad.jsonc");
const SPLIT_Z = 18.25;
const CLIP_X0 = -7.5;
const CLIP_X1 = 7.5;
const CLIP_Z0 = 12.45;
const CLIP_Z1 = 24.05;
const SPINE_Y0 = 10.4;
const SPINE_Y1 = 12.0;
const LEG_Y0 = 9.05; // clamp face / lip tip plane
const OPEN_Z0 = 14.05;
const OPEN_Z1 = 22.45;
const CLAMP_Y = LEG_Y0;
const HEX_ANCHOR = 0.4;
const TOL = 0.02;
// Side-hole block through the feature immediately before the land grooves.
// Captured from v16.46; this cut must not touch it.
const SIDE_SHA256 = "3c7e4da4550058276a0c118658d0f8e3e6906e26823cb43fe4ecb64388d6ded8";

const failures = [];
function fail(msg) {
  failures.push(msg);
}

function parseJsonc(text) {
  const body = text
    .split(/\r?\n/)
    .filter((line) => !line.trim().startsWith("//"))
    .join("\n");
  return JSON.parse(body);
}

function inHex(dx, dz, apothem) {
  const ax = Math.abs(dx);
  const az = Math.abs(dz);
  const bound = 0.5 * ax + (Math.sqrt(3) / 2) * az;
  return Math.max(ax, bound) <= apothem + 1e-9;
}

function hexAt(cells, x, z, apothem) {
  for (const c of cells) {
    if (inHex(x - c.x, z - c.z, apothem)) return c;
  }
  return null;
}

function yInterval(part) {
  const ext = part.extrude.call.arguments.extent.distance;
  const y0 = part.move.call.arguments.translation.y;
  return [y0, y0 + ext];
}

function load() {
  const text = fs.readFileSync(TIP, "utf8");
  const doc = parseJsonc(text);
  return { text, doc };
}

function indexSteps(doc) {
  const byId = new Map();
  for (const step of doc.steps) {
    if (step.id) byId.set(step.id, step);
  }
  return byId;
}

function polygonOf(step) {
  const args = step.call.arguments;
  return {
    x: args.center.x,
    z: args.center.y,
    r: Number(args.radius_text),
    rot: args.rotation_deg,
    mode: args.mode,
    edges: args.edge_count,
  };
}

function pairRing(byId, prefix) {
  const outHex = byId.get(`${prefix}_out_hex`);
  const inHex = byId.get(`${prefix}_in_hex`);
  const outEx = byId.get(`${prefix}_out_ex`);
  const inEx = byId.get(`${prefix}_in_ex`);
  const outMv = byId.get(`${prefix}_out_mv`);
  const inMv = byId.get(`${prefix}_in_mv`);
  const hole = byId.get(`cut_${prefix}_hole`);
  if (!outHex || !inHex || !outEx || !inEx || !outMv || !inMv || !hole) {
    fail(`missing ring steps for ${prefix}`);
    return null;
  }
  const outer = polygonOf(outHex);
  const inner = polygonOf(inHex);
  const yOut = yInterval({ extrude: outEx, move: outMv });
  const yIn = yInterval({ extrude: inEx, move: inMv });
  const profiles = outEx.call.arguments.profile_indices;
  const inProfiles = inEx.call.arguments.profile_indices;
  if (profiles.length !== 1 || profiles[0] !== 0 || inProfiles.length !== 1 || inProfiles[0] !== 0) {
    fail(`${prefix} extrude is not a single profile 0 (multi-profile on overlapping hexes is unstable)`);
  }
  if (outEx.call.arguments.operation !== "new_body" || inEx.call.arguments.operation !== "new_body") {
    fail(`${prefix} extrude is not new_body`);
  }
  if (outer.edges !== 6 || inner.edges !== 6 || outer.mode !== "circumscribed" || inner.mode !== "circumscribed") {
    fail(`${prefix} is not a circumscribed hex`);
  }
  if (outer.rot !== 0 || inner.rot !== 0) {
    fail(`${prefix} rotation is not 0 (pointy-top, vertical flats // Z)`);
  }
  if (outer.x !== inner.x || outer.z !== inner.z) {
    fail(`${prefix} inner and outer centers differ`);
  }
  const holeArgs = hole.call.arguments;
  if (holeArgs.operation !== "cut") {
    fail(`${prefix} hole op is not a cut`);
  }
  if (holeArgs.target_body_id.$ref !== `${prefix}_out_body`) {
    fail(`${prefix} hole does not target its outer body`);
  }
  if (holeArgs.tool_body_ids.length !== 1 || holeArgs.tool_body_ids[0].$ref !== `${prefix}_in_body`) {
    fail(`${prefix} hole tool is not its own inner body`);
  }
  if (!(yIn[0] < yOut[0] - 1e-9 && yIn[1] > yOut[1] + 1e-9)) {
    fail(`${prefix} inner cutter Y[${yIn}] does not pass through outer Y[${yOut}] (blind cell)`);
  }
  if (!(inner.r < outer.r - 0.2)) {
    fail(`${prefix} inner apothem ${inner.r} is not a real opening inside outer ${outer.r}`);
  }
  return { prefix, outer, inner, yOut, yIn, holeKeep: holeArgs.keep_tools };
}

function auditMultiProfile(doc) {
  let multi = 0;
  for (const step of doc.steps) {
    const call = step.call;
    if (!call || call.operation !== "solid_extrude") continue;
    const idx = call.arguments.profile_indices || [];
    if (idx.length > 1) {
      multi += 1;
      fail(
        `${step.id} extrudes ${idx.length} profiles; v16.44 replay showed that returns N bodies and overlapping hexes do not keep stable indices`
      );
    }
  }
  return multi;
}

function raster(cells, outerR, innerR) {
  const step = 0.04;
  const x0 = -8;
  const x1 = 8;
  const z0 = 12.2;
  const z1 = 24.3;
  const nx = Math.round((x1 - x0) / step);
  const nz = Math.round((z1 - z0) / step);
  const solid = new Uint8Array(nx * nz);
  let solidCount = 0;
  for (let iz = 0; iz < nz; iz++) {
    const z = z0 + (iz + 0.5) * step;
    for (let ix = 0; ix < nx; ix++) {
      const x = x0 + (ix + 0.5) * step;
      let on = false;
      const inEnvelope = x >= CLIP_X0 && x <= CLIP_X1 && z >= CLIP_Z0 && z <= CLIP_Z1;
      const inLeg = inEnvelope && (z <= OPEN_Z0 || z >= OPEN_Z1);
      if (inLeg) on = true;
      const hit = hexAt(cells, x, z, outerR);
      if (hit && !inHex(x - hit.x, z - hit.z, innerR)) on = true;
      if (hit && inHex(x - hit.x, z - hit.z, innerR)) {
        let filledByOther = false;
        for (const c of cells) {
          if (c === hit) continue;
          if (inHex(x - c.x, z - c.z, outerR) && !inHex(x - c.x, z - c.z, innerR)) {
            filledByOther = true;
            break;
          }
        }
        on = filledByOther || inLeg;
      }
      if (on) {
        solid[iz * nx + ix] = 1;
        solidCount += 1;
      }
    }
  }
  return { solid, nx, nz, step, x0, z0, solidCount };
}

function indexOf(grid, x, z) {
  const ix = Math.floor((x - grid.x0) / grid.step);
  const iz = Math.floor((z - grid.z0) / grid.step);
  if (ix < 0 || iz < 0 || ix >= grid.nx || iz >= grid.nz) return -1;
  return iz * grid.nx + ix;
}

function floodComponents(grid) {
  const { solid, nx, nz } = grid;
  const comp = new Int32Array(solid.length);
  comp.fill(-1);
  let n = 0;
  const stack = [];
  for (let i = 0; i < solid.length; i++) {
    if (!solid[i] || comp[i] !== -1) continue;
    stack.push(i);
    comp[i] = n;
    while (stack.length) {
      const k = stack.pop();
      const ix = k % nx;
      const iz = (k - ix) / nx;
      const nbrs = [
        ix > 0 ? k - 1 : -1,
        ix + 1 < nx ? k + 1 : -1,
        iz > 0 ? k - nx : -1,
        iz + 1 < nz ? k + nx : -1,
      ];
      for (const nb of nbrs) {
        if (nb >= 0 && solid[nb] && comp[nb] === -1) {
          comp[nb] = n;
          stack.push(nb);
        }
      }
    }
    n += 1;
  }
  return { comp, n };
}

function floodEmpty(grid) {
  const { solid, nx, nz } = grid;
  const comp = new Int32Array(solid.length);
  comp.fill(-1);
  let n = 0;
  const stack = [];
  for (let i = 0; i < solid.length; i++) {
    if (solid[i] || comp[i] !== -1) continue;
    stack.push(i);
    comp[i] = n;
    while (stack.length) {
      const k = stack.pop();
      const ix = k % nx;
      const iz = (k - ix) / nx;
      const nbrs = [
        ix > 0 ? k - 1 : -1,
        ix + 1 < nx ? k + 1 : -1,
        iz > 0 ? k - nx : -1,
        iz + 1 < nz ? k + nx : -1,
      ];
      for (const nb of nbrs) {
        if (nb >= 0 && !solid[nb] && comp[nb] === -1) {
          comp[nb] = n;
          stack.push(nb);
        }
      }
    }
    n += 1;
  }
  return { comp, n };
}

function main() {
  const { text, doc } = load();
  if (!doc.name.includes("v16.48")) fail(`document name is not v16.48: ${doc.name}`);
  if (text.includes('"id": "cyp_hpad') || text.includes('"name": "cyp_hpad')) {
    fail("cyp_hpad full-face pad is still a feature");
  }
  if (text.includes("cyp_hcell") || text.includes("land_hcell")) {
    fail("v16.46 solid-cell cutter ids are still present");
  }
  if (text.includes("cyp_xbar")) fail("inner crossbar ids returned");

  const sideA = text.indexOf('"id": "cb_side_1_1_0"');
  const sideB = text.indexOf('"id": "land_');
  const sideBlob = text.slice(sideA, sideB);
  const sideHash = crypto.createHash("sha256").update(sideBlob).digest("hex");
  if (sideHash !== SIDE_SHA256) {
    fail("Technic side-hole region hash changed; that decision was out of scope");
  }

  const byId = indexSteps(doc);
  for (const id of ["cyp_out_begin", "cyp_open_begin", "cut_cyp_open", "cym_mirror", "join_cyp_hlattice"]) {
    if (!byId.has(id)) fail(`missing required step ${id}`);
  }

  const outRect = byId.get("cyp_out_r").call.arguments;
  const openRect = byId.get("cyp_open_r").call.arguments;
  if (outRect.anchor.x !== -7.5 || outRect.anchor.y !== 9.05 || outRect.width_mm !== 15 || outRect.corner_hint.y !== 12) {
    fail(`cyp_out rectangle changed: ${JSON.stringify(outRect.anchor)} ${outRect.width_mm}`);
  }
  if (openRect.anchor.x !== -7.55 || openRect.anchor.y !== 8.55 || openRect.corner_hint.y !== 10.4) {
    fail("cyp_open rectangle changed");
  }
  const outMoveZ = byId.get("cyp_out_mv").call.arguments.translation.z;
  const openMoveZ = byId.get("cyp_open_mv").call.arguments.translation.z;
  const outLen = byId.get("cyp_out_ex").call.arguments.extent.distance;
  const openLen = byId.get("cyp_open_ex").call.arguments.extent.distance;
  if (Math.abs(outMoveZ - 12.45) > 1e-9 || Math.abs(outMoveZ + outLen - 24.05) > 1e-6) {
    fail(`open-C Z envelope is not [12.45,24.05] (move ${outMoveZ} len ${outLen})`);
  }
  if (Math.abs(openMoveZ - 14.05) > 1e-6 || Math.abs(openLen - 8.4) > 1e-6) {
    fail(`cyp_open cut is not Z[14.05,22.45] (move ${openMoveZ} len ${openLen})`);
  }

  auditMultiProfile(doc);

  const clipRings = [];
  for (let i = 0; i < 8; i++) {
    const ring = pairRing(byId, `cyp_ring${i}`);
    if (ring) clipRings.push(ring);
  }
  if (clipRings.length !== 8) fail(`expected 8 clip rings, found ${clipRings.length}`);

  // Fuse chain: rings 1..7 join onto ring 0, then ring 0 joins the clip.
  for (let i = 1; i < 8; i++) {
    const join = byId.get(`join_cyp_ring${i}_web`);
    if (!join) {
      fail(`missing join_cyp_ring${i}_web`);
      continue;
    }
    const args = join.call.arguments;
    if (args.operation !== "join" || args.keep_tools !== false) fail(`join_cyp_ring${i}_web is not a consuming join`);
    if (args.target_body_id.$ref !== "cyp_ring0_out_body") fail(`join_cyp_ring${i}_web does not target ring 0`);
    if (args.tool_body_ids.length !== 1 || args.tool_body_ids[0].$ref !== `cyp_ring${i}_out_body`) {
      fail(`join_cyp_ring${i}_web tool is not ring ${i}`);
    }
  }
  const stepOrder = doc.steps.map((s) => s.id).filter(Boolean);
  const orderOf = (id) => stepOrder.indexOf(id);
  for (let i = 0; i < 8; i++) {
    const holeAt = orderOf(`cut_cyp_ring${i}_hole`);
    const spineAt = orderOf(`cut_cyp_ring${i}_spine`);
    const joinAt = i === 0 ? orderOf("join_cyp_hlattice") : orderOf(`join_cyp_ring${i}_web`);
    if (holeAt < 0 || joinAt < 0 || holeAt > joinAt) {
      fail(`ring ${i} hole cut is not before its join`);
    }
    if (spineAt < 0) fail(`missing cut_cyp_ring${i}_spine through-spine open-center cut`);
    else {
      if (!(holeAt < spineAt && spineAt < joinAt)) {
        fail(`ring ${i} spine through-cut is not between hole and join`);
      }
      const spine = byId.get(`cut_cyp_ring${i}_spine`).call.arguments;
      if (spine.operation !== "cut" || spine.keep_tools !== false) {
        fail(`cut_cyp_ring${i}_spine is not a consuming cut`);
      }
      if (spine.target_body_id.$ref !== "clip_yp_body") {
        fail(`cut_cyp_ring${i}_spine does not target the open-C body`);
      }
      if (spine.tool_body_ids.length !== 1 || spine.tool_body_ids[0].$ref !== `cyp_ring${i}_in_body`) {
        fail(`cut_cyp_ring${i}_spine tool is not ring ${i} inner`);
      }
    }
    if (clipRings[i] && clipRings[i].holeKeep !== true) {
      fail(`cut_cyp_ring${i}_hole must keep_tools so the inner can also open the spine`);
    }
  }
  const lattice = byId.get("join_cyp_hlattice");
  if (lattice) {
    const args = lattice.call.arguments;
    if (args.operation !== "join") fail("join_cyp_hlattice is not a join");
    if (args.target_body_id.$ref !== "clip_yp_body") fail("lattice is not joined onto the open-C body");
    if (args.tool_body_ids.length !== 1 || args.tool_body_ids[0].$ref !== "cyp_ring0_out_body") {
      fail("lattice join tool is not the fused ring web");
    }
  }

  if (clipRings.length === 8) {
    const r0 = clipRings[0];
    const wall = r0.outer.r - r0.inner.r;
    if (Math.abs(wall - 1.2) > TOL) fail(`perimeter wall ${wall} mm is not 1.2`);

    // Coplanar clamp face: hex tip == lip tip.
    if (Math.abs(r0.yOut[0] - CLAMP_Y) > 1e-9) {
      fail(`hex tip Y=${r0.yOut[0]} is not coplanar with clamp/lip face Y=${CLAMP_Y}`);
    }
    const lipDepth = SPINE_Y0 - CLAMP_Y;
    const hexDepthToSpine = SPINE_Y0 - r0.yOut[0];
    if (Math.abs(hexDepthToSpine - lipDepth) > 1e-9) {
      fail(`hex depth-to-spine ${hexDepthToSpine} != lip depth ${lipDepth}`);
    }
    if (Math.abs(lipDepth - 1.35) > TOL) {
      fail(`lip/hex depth from clamp face to spine is ${lipDepth}, expected 1.35`);
    }
    const yOverlap = Math.min(r0.yOut[1], SPINE_Y1) - Math.max(r0.yOut[0], SPINE_Y0);
    if (yOverlap < HEX_ANCHOR - TOL) {
      fail(`ring anchor into spine is only ${yOverlap} mm (need ~${HEX_ANCHOR})`);
    }
    if (Math.abs(r0.yOut[1] - (SPINE_Y0 + HEX_ANCHOR)) > TOL) {
      fail(`ring back Y=${r0.yOut[1]} is not spine+anchor ${SPINE_Y0 + HEX_ANCHOR}`);
    }
    // Reject the v16.47 class: rings that tip proud of a recessed shelf while lips tip elsewhere.
    if (Math.abs(r0.yOut[0] - 9.2) < 1e-9) {
      fail("hex tip is still at Y=9.2 (v16.47 recessed-shelf ring placement)");
    }

    for (const ring of clipRings) {
      if (ring.outer.r !== r0.outer.r || ring.inner.r !== r0.inner.r) fail(`${ring.prefix} radius differs`);
      if (ring.yOut[0] !== r0.yOut[0] || ring.yOut[1] !== r0.yOut[1]) fail(`${ring.prefix} Y span differs`);
      const rc = ring.outer.r * (2 / Math.sqrt(3));
      const zMin = ring.outer.z - rc;
      const zMax = ring.outer.z + rc;
      const xMin = ring.outer.x - ring.outer.r;
      const xMax = ring.outer.x + ring.outer.r;
      if (zMin < CLIP_Z0 - 1e-6 || zMax > CLIP_Z1 + 1e-6 || xMin < CLIP_X0 - 1e-6 || xMax > CLIP_X1 + 1e-6) {
        fail(`${ring.prefix} leaves the clip envelope XZ (x ${xMin},${xMax} z ${zMin},${zMax})`);
      }
    }

    const fused = [clipRings[0]];
    for (let i = 1; i < clipRings.length; i++) {
      const ring = clipRings[i];
      let best = Infinity;
      for (const prev of fused) {
        const d = Math.hypot(ring.outer.x - prev.outer.x, ring.outer.z - prev.outer.z);
        if (d < best) best = d;
      }
      const overlap = 2 * ring.outer.r - best;
      if (overlap < 0.4) {
        fail(`ring ${i} overlap with the fused web is ${overlap.toFixed(3)} mm (floating island)`);
      }
      fused.push(ring);
    }

    let sharedChecked = 0;
    for (let i = 0; i < clipRings.length; i++) {
      for (let j = i + 1; j < clipRings.length; j++) {
        const a = clipRings[i];
        const b = clipRings[j];
        const d = Math.hypot(a.outer.x - b.outer.x, a.outer.z - b.outer.z);
        if (Math.abs(d - 3.4) < 0.02) {
          const shared = d - 2 * a.inner.r;
          if (Math.abs(shared - 1.2) > 0.02) fail(`shared wall ${a.prefix}-${b.prefix} is ${shared} mm`);
          const mx = (a.outer.x + b.outer.x) / 2;
          const mz = (a.outer.z + b.outer.z) / 2;
          if (!inHex(mx - a.outer.x, mz - a.outer.z, a.outer.r) || inHex(mx - a.outer.x, mz - a.outer.z, a.inner.r)) {
            fail(`shared-wall sample of ${a.prefix} is not in the ring material`);
          }
          sharedChecked += 1;
        }
      }
    }
    if (sharedChecked < 8) fail(`only ${sharedChecked} shared walls found; lattice is not connected honeycomb`);

    const cells = clipRings.map((r) => ({ x: r.outer.x, z: r.outer.z }));
    const grid = raster(cells, r0.outer.r, r0.inner.r);
    const solids = floodComponents(grid);
    if (solids.n !== 1) fail(`proud-face solid has ${solids.n} components (want 1 connected clip+web)`);
    const voids = floodEmpty(grid);
    const exteriorIdx = indexOf(grid, 7.3, 18.25);
    if (exteriorIdx < 0 || grid.solid[exteriorIdx]) fail("mouth sample (7.3, 18.25) is not open — full-face pad or sheet is back");
    const exteriorComp = voids.comp[exteriorIdx];
    const centerComps = new Set();
    for (const c of cells) {
      const k = indexOf(grid, c.x, c.z);
      if (k < 0 || grid.solid[k]) fail(`cell center (${c.x}, ${c.z}) is solid`);
      else {
        if (voids.comp[k] === exteriorComp) {
          fail(`cell center (${c.x}, ${c.z}) opens to the exterior (broken ring)`);
        }
        centerComps.add(voids.comp[k]);
      }
    }
    if (centerComps.size !== 8) fail(`open centers collapsed into ${centerComps.size} voids (want 8)`);

    const envelopeCells = Math.round(((CLIP_X1 - CLIP_X0) * (CLIP_Z1 - CLIP_Z0)) / (grid.step * grid.step));
    if (grid.solidCount > envelopeCells * 0.8) {
      fail(`proud slice is too solid (${grid.solidCount} px vs envelope ${envelopeCells}); looks like a pad`);
    }

    for (const c of cells) {
      if (c.x < CLIP_X0 || c.x > CLIP_X1 || c.z < CLIP_Z0 || c.z > CLIP_Z1) {
        fail(`center (${c.x},${c.z}) is outside the spine footprint`);
      }
    }
    const holeY = clipRings[0].yIn;
    // Through-spine cuts are required; other ring/hpad cuts on the clip are not.
    for (const step of doc.steps) {
      if (!step.id || !step.call || step.call.operation !== "solid_combine") continue;
      const args = step.call.arguments;
      if (args.operation === "cut" && args.target_body_id.$ref === "clip_yp_body") {
        const tools = args.tool_body_ids.map((t) => t.$ref).join(",");
        if (step.id.startsWith("cut_cyp_ring") && step.id.endsWith("_spine")) continue;
        if (tools.includes("hcell") || tools.includes("hpad")) {
          fail(`${step.id} cuts the clip with ${tools}`);
        }
        if (tools.includes("ring") && !step.id.endsWith("_spine")) {
          fail(`${step.id} cuts the clip with ${tools} (only *_spine through-cuts are allowed)`);
        }
      }
    }
    if (holeY[1] <= SPINE_Y1 - 0.2) {
      fail("inner cutter does not reach through the spine; cell may stay floored");
    }
  }

  // Land grooves. Bottom row A only, top row B only, middle both. ±Y.
  const expectedHalf = [
    ["yp", "a", [0, 1, 2, 3, 4], "clamshell_a", 9.05, 10.55],
    ["yp", "b", [3, 4, 5, 6, 7], "clamshell_b", 9.05, 10.55],
    ["ym", "a", [0, 1, 2, 3, 4], "clamshell_a", -10.55, -9.05],
    ["ym", "b", [3, 4, 5, 6, 7], "clamshell_b", -10.55, -9.05],
  ];
  for (const [side, half, idxs, shell, y0, y1] of expectedHalf) {
    for (const i of idxs) {
      const prefix = `land_${side}_${half}_r${i}`;
      const ring = pairRing(byId, prefix);
      if (!ring) continue;
      if (Math.abs(ring.outer.r - 2.5) > 1e-9 || Math.abs(ring.inner.r - 0.9) > 1e-9) {
        fail(`${prefix} groove radii ${ring.inner.r}/${ring.outer.r} are not 0.9/2.5`);
      }
      if (Math.abs(ring.yOut[0] - y0) > 1e-9 || Math.abs(ring.yOut[1] - y1) > 1e-9) {
        fail(`${prefix} Y[${ring.yOut}] is not [${y0},${y1}]`);
      }
      // Groove mouth coplanar with clamp face (±).
      const mouth = side === "yp" ? ring.yOut[0] : ring.yOut[1];
      const mouthExpected = side === "yp" ? CLAMP_Y : -CLAMP_Y;
      if (Math.abs(mouth - mouthExpected) > 1e-9) {
        fail(`${prefix} groove mouth Y=${mouth} is not clamp face ${mouthExpected}`);
      }
      const clip = clipRings[i];
      if (clip && (ring.outer.x !== clip.outer.x || ring.outer.z !== clip.outer.z)) {
        fail(`${prefix} center does not match clip ring ${i}`);
      }
      const clrOut = ring.outer.r - (clip ? clip.outer.r : 2.3);
      const clrIn = (clip ? clip.inner.r : 1.1) - ring.inner.r;
      if (Math.abs(clrOut - 0.2) > 1e-9 || Math.abs(clrIn - 0.2) > 1e-9) {
        fail(`${prefix} clearance is not 0.2 mm (out ${clrOut}, in ${clrIn})`);
      }
      if (!inHex(0.4, 0, ring.inner.r)) fail(`${prefix} center island would be cut away`);
      if (!inHex(1.7, 0, ring.outer.r) || inHex(1.7, 0, ring.inner.r)) {
        fail(`${prefix} does not clear the clip wall at local x=1.7`);
      }
      if (!inHex(2.4, 0, ring.outer.r)) fail(`${prefix} missing outer clearance band`);
      if (inHex(2.7, 0, ring.outer.r)) fail(`${prefix} groove reaches too far out`);
      const cut = byId.get(`cut_land_${side}_${half}_r${i}`);
      if (!cut) fail(`missing clamshell cut for ${prefix}`);
      else {
        const args = cut.call.arguments;
        if (args.operation !== "cut" || args.target_body_id.$ref !== shell) {
          fail(`${cut.id} does not cut ${shell}`);
        }
        if (args.tool_body_ids.length !== 1 || args.tool_body_ids[0].$ref !== `${prefix}_out_body`) {
          fail(`${cut.id} tool is not the grooved ring`);
        }
      }
      const rc = ring.outer.r * (2 / Math.sqrt(3));
      const crosses = ring.outer.z - rc < SPLIT_Z - 0.02 && ring.outer.z + rc > SPLIT_Z + 0.02;
      const onlyA = ring.outer.z + rc < SPLIT_Z - 0.02;
      const onlyB = ring.outer.z - rc > SPLIT_Z + 0.02;
      if (onlyA && half !== "a") fail(`${prefix} is entirely below the split but cut into ${half}`);
      if (onlyB && half !== "b") fail(`${prefix} is entirely above the split but cut into ${half}`);
      if (!onlyA && !onlyB && !crosses) {
        fail(`${prefix} Z extent is ambiguous against split_z (${ring.outer.z} ± ${rc})`);
      }
    }
    for (let i = 0; i < 8; i++) {
      if (!idxs.includes(i) && byId.has(`land_${side}_${half}_r${i}_out_hex`)) {
        fail(`land_${side}_${half} includes cell ${i} which does not belong on that half`);
      }
    }
  }

  for (const side of ["yp", "ym"]) {
    for (const i of [3, 4]) {
      if (!byId.has(`land_${side}_a_r${i}_out_hex`) || !byId.has(`land_${side}_b_r${i}_out_hex`)) {
        fail(`middle cell ${i} ${side} is not split across clamshell A and B`);
      }
    }
    for (const i of [0, 1, 2]) {
      if (byId.has(`land_${side}_b_r${i}_out_hex`)) fail(`bottom cell ${i} was cut into clamshell B`);
    }
    for (const i of [5, 6, 7]) {
      if (byId.has(`land_${side}_a_r${i}_out_hex`)) fail(`top cell ${i} was cut into clamshell A`);
    }
  }

  if (failures.length) {
    console.error(`FAIL ${failures.length}`);
    for (const f of failures) console.error(" - " + f);
    process.exit(1);
  }
  const ring = clipRings[0];
  const rc = ring.outer.r * (2 / Math.sqrt(3));
  const lipDepth = SPINE_Y0 - CLAMP_Y;
  console.log("PASS v16.48 coplanar clamp-face audit");
  console.log(
    `rings=8 wall=${(ring.outer.r - ring.inner.r).toFixed(2)}mm FF=${(2 * ring.inner.r).toFixed(2)} ` +
      `clamp_Y=${CLAMP_Y} hex_Y=[${ring.yOut[0]},${ring.yOut[1]}] lip_depth=${lipDepth.toFixed(2)} ` +
      `anchor=${(ring.yOut[1] - SPINE_Y0).toFixed(2)} vertex_r=${rc.toFixed(3)}`
  );
  console.log(
    "open C kept; coplanar lips+hex; through-spine open centers; A/B grooves +0.2 mm; side-hole region unchanged"
  );
}

main();
