#!/usr/bin/env node
/**
 * v16.49 clip single-sketch hex-pattern audit.
 * Parses the JSONC tip and checks the boolean construction, not comments.
 * Circumscribed sketch radius is the hex apothem. rotation 0 is pointy-top
 * (vertex along sketch +Y = world +Z, vertical flats parallel to Z).
 *
 * Topology: one outer-pattern sketch + one join extrude, then one inner-pattern
 * sketch + one cut. Face counts are what noBS CAD 0.2.0 profile discovery
 * emits for these overlapping outers (27 clip / 15 land) and disjoint inners.
 *
 * Run: node design/validate_clip_hex_walls.cjs
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TIP = path.join(__dirname, "design_v16_49.nbcad.jsonc");
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
// Eight Technic side holes plus the face selects that feed them, in document order.
// Baseline is canonical JSON (sorted keys) of those steps from v16.48 (af2ffdc).
// Raw step text and this hash both match v16.49. Do not hash onward to the first
// "id": "land_" — that span includes the hex/land construction.
const SIDE_IDS = [
  "cb_side_1_1_0",
  "cb_side_1_1_1",
  "cb_side_1_-1_0",
  "cb_side_1_-1_1",
  "cb_side_1_1_3",
  "cb_side_1_1_4",
  "cb_side_1_-1_3",
  "cb_side_1_-1_4",
];
const SIDE_SHA256 = "407e95783a0fa9c1d3468c1684bdb170f06a1d2b3c5342d3136fb108d99d79ee";

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

function canonicalJson(value) {
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(",") + "]";
  if (value && typeof value === "object") {
    return (
      "{" +
      Object.keys(value)
        .sort()
        .map((key) => JSON.stringify(key) + ":" + canonicalJson(value[key]))
        .join(",") +
      "}"
    );
  }
  return JSON.stringify(value);
}

function sideHoleOps(doc) {
  return doc.steps.filter((step) => {
    if (step.id && /^cb_side/.test(step.id)) return true;
    if (step.let && Object.keys(step.let).some((key) => /^cb_side/.test(key))) return true;
    return false;
  });
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

const CLIP_OUT_FACES = 27;
const LAND_OUT_FACES = 15;

function expectIndices(step, n, label) {
  const idx = step.call.arguments.profile_indices || [];
  const want = Array.from({ length: n }, (_, i) => i);
  if (idx.length !== want.length || idx.some((v, i) => v !== want[i])) {
    fail(`${label} profile_indices are not 0..${n - 1}`);
  }
}

function polygonsOfSketch(doc, sketchName) {
  const begin = doc.steps.findIndex((s) => s.id === `${sketchName}_begin`);
  const finish = doc.steps.findIndex((s) => s.id === `${sketchName}_finish`);
  if (begin < 0 || finish < begin) {
    fail(`sketch ${sketchName} is missing begin/finish`);
    return [];
  }
  const beginName = doc.steps[begin].call.arguments.name;
  if (beginName !== sketchName) fail(`${sketchName} begin name is ${beginName}`);
  const plane = doc.steps[begin].call.arguments.plane;
  if (!plane || plane.plane !== "xz") fail(`${sketchName} is not an XZ sketch`);
  const polys = [];
  for (const step of doc.steps.slice(begin + 1, finish)) {
    if (step.call && step.call.operation === "sketch_polygon") {
      polys.push({ id: step.id, ...polygonOf(step) });
    }
  }
  return polys;
}

function assertHex(poly, label) {
  if (poly.edges !== 6 || poly.mode !== "circumscribed") fail(`${label} is not a circumscribed hex`);
  if (poly.rot !== 0) fail(`${label} rotation is not 0 (pointy-top, vertical flats // Z)`);
}

function auditPatternExtrudes(doc) {
  const allowed = new Map([
    ["cyp_hex_out_ex", { op: "join", n: CLIP_OUT_FACES }],
    ["cyp_hex_in_ex", { op: "new_body", n: 8 }],
    ["land_yp_a_out_ex", { op: "join", n: LAND_OUT_FACES }],
    ["land_yp_b_out_ex", { op: "join", n: LAND_OUT_FACES }],
    ["land_ym_a_out_ex", { op: "join", n: LAND_OUT_FACES }],
    ["land_ym_b_out_ex", { op: "join", n: LAND_OUT_FACES }],
    ["land_yp_a_in_ex", { op: "new_body", n: 5 }],
    ["land_yp_b_in_ex", { op: "new_body", n: 5 }],
    ["land_ym_a_in_ex", { op: "new_body", n: 5 }],
    ["land_ym_b_in_ex", { op: "new_body", n: 5 }],
  ]);
  for (const step of doc.steps) {
    const call = step.call;
    if (!call || call.operation !== "solid_extrude") continue;
    const idx = call.arguments.profile_indices || [];
    const spec = allowed.get(step.id);
    if (idx.length > 1 && !spec) {
      fail(`${step.id} extrudes ${idx.length} profiles outside the hex-pattern sketches`);
    }
    if (spec) {
      if (call.arguments.operation !== spec.op) {
        fail(`${step.id} operation is ${call.arguments.operation}, want ${spec.op}`);
      }
      expectIndices(step, spec.n, step.id);
      if (spec.op === "join" && (call.arguments.target_body_ids || []).length !== 0) {
        fail(`${step.id} join targets a body; pattern join must fuse profiles into one new body`);
      }
    }
  }
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
  if (!doc.name.includes("v16.49")) fail(`document name is not v16.49: ${doc.name}`);
  if (text.includes('"id": "cyp_hpad') || text.includes('"name": "cyp_hpad')) {
    fail("cyp_hpad full-face pad is still a feature");
  }
  if (text.includes("cyp_hcell") || text.includes("land_hcell")) {
    fail("v16.46 solid-cell cutter ids are still present");
  }
  if (text.includes("cyp_xbar")) fail("inner crossbar ids returned");

  const sideOps = sideHoleOps(doc);
  const sideIds = sideOps.filter((step) => step.id).map((step) => step.id);
  if (sideIds.join(",") !== SIDE_IDS.join(",")) {
    fail(`Technic side-hole ids are [${sideIds.join(", ")}], want the v16.48 eight`);
  }
  const sideHash = crypto.createHash("sha256").update(canonicalJson(sideOps)).digest("hex");
  if (sideHash !== SIDE_SHA256) {
    fail(`Technic side-hole ops differ from the v16.48 baseline (hash ${sideHash})`);
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

  auditPatternExtrudes(doc);
  if (text.includes("cyp_ring") || /land_[a-z]+_[ab]_r\d+_/.test(text)) {
    fail("per-cell hex sketch ids are still present");
  }

  const outPolys = polygonsOfSketch(doc, "cyp_hex_out");
  const inPolys = polygonsOfSketch(doc, "cyp_hex_in");
  if (outPolys.length !== 8) fail(`cyp_hex_out has ${outPolys.length} hexes, want 8`);
  if (inPolys.length !== 8) fail(`cyp_hex_in has ${inPolys.length} hexes, want 8`);
  const outEx = byId.get("cyp_hex_out_ex");
  const inEx = byId.get("cyp_hex_in_ex");
  const outMv = byId.get("cyp_hex_out_mv");
  const inMv = byId.get("cyp_hex_in_mv");
  if (!outEx || !inEx || !outMv || !inMv) fail("clip pattern extrude/move is missing");
  let clipRings = [];
  if (outEx && inEx && outMv && inMv && outPolys.length === 8 && inPolys.length === 8) {
    const yOut = yInterval({ extrude: outEx, move: outMv });
    const yIn = yInterval({ extrude: inEx, move: inMv });
    if (outEx.call.arguments.sketch_name !== "cyp_hex_out" || inEx.call.arguments.sketch_name !== "cyp_hex_in") {
      fail("clip extrude does not use the pattern sketches");
    }
    const hole = byId.get("cut_cyp_hex_hole");
    const spine = byId.get("cut_cyp_hex_spine");
    if (!hole || !spine) fail("clip pattern is missing the hole cut or the through-spine cut");
    else {
      const holeArgs = hole.call.arguments;
      const spineArgs = spine.call.arguments;
      if (holeArgs.operation !== "cut" || holeArgs.keep_tools !== true) {
        fail("cut_cyp_hex_hole must be a cut that keeps the inner tools for the spine");
      }
      if (holeArgs.target_body_id.$ref !== "cyp_hex_out_body") fail("hole cut does not target the outer lattice");
      const inTools = Array.from({ length: 8 }, (_, i) => `cyp_hex_in_b${i}`);
      const holeTools = holeArgs.tool_body_ids.map((t) => t.$ref);
      const spineTools = spineArgs.tool_body_ids.map((t) => t.$ref);
      if (holeTools.join(",") !== inTools.join(",")) fail(`hole tools are ${holeTools}, want ${inTools}`);
      if (spineArgs.operation !== "cut" || spineArgs.keep_tools !== false) {
        fail("cut_cyp_hex_spine is not a consuming cut");
      }
      if (spineArgs.target_body_id.$ref !== "clip_yp_body") fail("spine cut does not target the open-C body");
      if (spineTools.join(",") !== inTools.join(",")) fail(`spine tools are ${spineTools}, want ${inTools}`);
    }
    const stepOrder = doc.steps.map((s) => s.id).filter(Boolean);
    const orderOf = (id) => stepOrder.indexOf(id);
    const holeAt = orderOf("cut_cyp_hex_hole");
    const spineAt = orderOf("cut_cyp_hex_spine");
    const joinAt = orderOf("join_cyp_hlattice");
    if (!(holeAt >= 0 && spineAt > holeAt && joinAt > spineAt)) {
      fail("clip order must be hole cut, then through-spine cut, then lattice join");
    }
    const lattice = byId.get("join_cyp_hlattice");
    if (lattice) {
      const args = lattice.call.arguments;
      if (args.operation !== "join" || args.keep_tools !== false) fail("join_cyp_hlattice is not a consuming join");
      if (args.target_body_id.$ref !== "clip_yp_body") fail("lattice is not joined onto the open-C body");
      if (args.tool_body_ids.length !== 1 || args.tool_body_ids[0].$ref !== "cyp_hex_out_body") {
        fail("lattice join tool is not the single outer pattern body");
      }
    }
    for (let i = 0; i < 8; i++) {
      const outer = outPolys[i];
      const inner = inPolys[i];
      assertHex(outer, outer.id);
      assertHex(inner, inner.id);
      if (outer.x !== inner.x || outer.z !== inner.z) fail(`${outer.id} center does not match its inner hex`);
      if (Math.abs(outer.r - 2.3) > 1e-9 || Math.abs(inner.r - 1.1) > 1e-9) {
        fail(`${outer.id} radii ${inner.r}/${outer.r} are not 1.1/2.3`);
      }
      clipRings.push({ prefix: outer.id, outer, inner, yOut, yIn });
    }
  }

  if (clipRings.length === 8) {
    const r0 = clipRings[0];
    const wall = r0.outer.r - r0.inner.r;
    if (Math.abs(wall - 1.2) > TOL) fail(`perimeter wall ${wall} mm is not 1.2`);

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
    for (const step of doc.steps) {
      if (!step.id || !step.call || step.call.operation !== "solid_combine") continue;
      const args = step.call.arguments;
      if (args.operation === "cut" && args.target_body_id.$ref === "clip_yp_body") {
        const tools = args.tool_body_ids.map((t) => t.$ref).join(",");
        if (step.id === "cut_cyp_hex_spine") continue;
        if (tools.includes("hcell") || tools.includes("hpad") || tools.includes("hex") || tools.includes("ring")) {
          fail(`${step.id} cuts the clip with ${tools}`);
        }
      }
    }
    if (holeY[1] <= SPINE_Y1 - 0.2) {
      fail("inner cutter does not reach through the spine; cell may stay floored");
    }
    if (!(holeY[0] < r0.yOut[0] - 1e-9 && holeY[1] > r0.yOut[1] + 1e-9)) {
      fail(`inner cutter Y[${holeY}] does not pass through lattice Y[${r0.yOut}]`);
    }
  }

  const expectedHalf = [
    ["yp", "a", [0, 1, 2, 3, 4], "clamshell_a", 9.05, 10.55],
    ["yp", "b", [3, 4, 5, 6, 7], "clamshell_b", 9.05, 10.55],
    ["ym", "a", [0, 1, 2, 3, 4], "clamshell_a", -10.55, -9.05],
    ["ym", "b", [3, 4, 5, 6, 7], "clamshell_b", -10.55, -9.05],
  ];
  const clipByIndex = new Map();
  clipRings.forEach((ring, i) => clipByIndex.set(i, ring));
  for (const [side, half, idxs, shell, y0, y1] of expectedHalf) {
    const outName = `land_${side}_${half}_out`;
    const inName = `land_${side}_${half}_in`;
    const outHexes = polygonsOfSketch(doc, outName);
    const inHexes = polygonsOfSketch(doc, inName);
    if (outHexes.length !== idxs.length || inHexes.length !== idxs.length) {
      fail(`${outName} has ${outHexes.length}/${inHexes.length} hexes, want ${idxs.length}`);
      continue;
    }
    const outExL = byId.get(`${outName}_ex`);
    const inExL = byId.get(`${inName}_ex`);
    const outMvL = byId.get(`${outName}_mv`);
    const inMvL = byId.get(`${inName}_mv`);
    if (!outExL || !inExL || !outMvL || !inMvL) {
      fail(`${outName} extrude/move missing`);
      continue;
    }
    const yOut = yInterval({ extrude: outExL, move: outMvL });
    const yIn = yInterval({ extrude: inExL, move: inMvL });
    if (Math.abs(yOut[0] - y0) > 1e-9 || Math.abs(yOut[1] - y1) > 1e-9) {
      fail(`${outName} Y[${yOut}] is not [${y0},${y1}]`);
    }
    if (!(yIn[0] < yOut[0] - 1e-9 && yIn[1] > yOut[1] + 1e-9)) {
      fail(`${outName} inner cutter Y[${yIn}] does not pass through groove Y[${yOut}]`);
    }
    const mouth = side === "yp" ? yOut[0] : yOut[1];
    const mouthExpected = side === "yp" ? CLAMP_Y : -CLAMP_Y;
    if (Math.abs(mouth - mouthExpected) > 1e-9) {
      fail(`${outName} groove mouth Y=${mouth} is not clamp face ${mouthExpected}`);
    }
    const seen = [];
    for (let k = 0; k < idxs.length; k++) {
      const outer = outHexes[k];
      const inner = inHexes[k];
      const cell = Number(String(outer.id).match(/(\d+)$/)[1]);
      const cellIn = Number(String(inner.id).match(/(\d+)$/)[1]);
      seen.push(cell);
      assertHex(outer, outer.id);
      assertHex(inner, inner.id);
      if (cell !== cellIn || outer.x !== inner.x || outer.z !== inner.z) {
        fail(`${outer.id} does not match its inner hex`);
      }
      if (Math.abs(outer.r - 2.5) > 1e-9 || Math.abs(inner.r - 0.9) > 1e-9) {
        fail(`${outer.id} groove radii ${inner.r}/${outer.r} are not 0.9/2.5`);
      }
      const clip = clipByIndex.get(cell);
      if (clip && (outer.x !== clip.outer.x || outer.z !== clip.outer.z)) {
        fail(`${outer.id} center does not match clip cell ${cell}`);
      }
      const clrOut = outer.r - (clip ? clip.outer.r : 2.3);
      const clrIn = (clip ? clip.inner.r : 1.1) - inner.r;
      if (Math.abs(clrOut - 0.2) > 1e-9 || Math.abs(clrIn - 0.2) > 1e-9) {
        fail(`${outer.id} clearance is not 0.2 mm (out ${clrOut}, in ${clrIn})`);
      }
      if (!inHex(0.4, 0, inner.r)) fail(`${outer.id} center island would be cut away`);
      if (!inHex(1.7, 0, outer.r) || inHex(1.7, 0, inner.r)) {
        fail(`${outer.id} does not clear the clip wall at local x=1.7`);
      }
      if (!inHex(2.4, 0, outer.r)) fail(`${outer.id} missing outer clearance band`);
      if (inHex(2.7, 0, outer.r)) fail(`${outer.id} groove reaches too far out`);
      const rc = outer.r * (2 / Math.sqrt(3));
      const crosses = outer.z - rc < SPLIT_Z - 0.02 && outer.z + rc > SPLIT_Z + 0.02;
      const onlyA = outer.z + rc < SPLIT_Z - 0.02;
      const onlyB = outer.z - rc > SPLIT_Z + 0.02;
      if (onlyA && half !== "a") fail(`${outer.id} is entirely below the split but cut into ${half}`);
      if (onlyB && half !== "b") fail(`${outer.id} is entirely above the split but cut into ${half}`);
      if (!onlyA && !onlyB && !crosses) {
        fail(`${outer.id} Z extent is ambiguous against split_z (${outer.z} ± ${rc})`);
      }
    }
    seen.sort((a, b) => a - b);
    if (seen.join(",") !== idxs.join(",")) fail(`${outName} cells ${seen} are not ${idxs}`);
    const hole = byId.get(`cut_land_${side}_${half}_hole`);
    const cut = byId.get(`cut_land_${side}_${half}`);
    if (!hole || hole.call.arguments.operation !== "cut" || hole.call.arguments.keep_tools !== false) {
      fail(`cut_land_${side}_${half}_hole is not a consuming ring cut`);
    } else if (hole.call.arguments.target_body_id.$ref !== `${outName}_body`) {
      fail(`cut_land_${side}_${half}_hole does not target the outer pattern`);
    } else if (hole.call.arguments.tool_body_ids.length !== idxs.length) {
      fail(`cut_land_${side}_${half}_hole does not use every inner body`);
    }
    if (!cut) fail(`missing clamshell cut for ${outName}`);
    else {
      const args = cut.call.arguments;
      if (args.operation !== "cut" || args.target_body_id.$ref !== shell) {
        fail(`${cut.id} does not cut ${shell}`);
      }
      if (args.tool_body_ids.length !== 1 || args.tool_body_ids[0].$ref !== `${outName}_body`) {
        fail(`${cut.id} tool is not the grooved pattern`);
      }
    }
  }

  for (const side of ["yp", "ym"]) {
    const idsOf = (half) =>
      polygonsOfSketch(doc, `land_${side}_${half}_out`).map((p) => Number(String(p.id).match(/(\d+)$/)[1]));
    const a = new Set(idsOf("a"));
    const b = new Set(idsOf("b"));
    for (const i of [3, 4]) {
      if (!a.has(i) || !b.has(i)) fail(`middle cell ${i} ${side} is not split across clamshell A and B`);
    }
    for (const i of [0, 1, 2]) {
      if (b.has(i)) fail(`bottom cell ${i} was cut into clamshell B`);
    }
    for (const i of [5, 6, 7]) {
      if (a.has(i)) fail(`top cell ${i} was cut into clamshell A`);
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
  console.log("PASS v16.49 single-sketch hex-pattern audit");
  console.log(
    `cells=8 wall=${(ring.outer.r - ring.inner.r).toFixed(2)}mm FF=${(2 * ring.inner.r).toFixed(2)} ` +
      `clamp_Y=${CLAMP_Y} hex_Y=[${ring.yOut[0]},${ring.yOut[1]}] lip_depth=${lipDepth.toFixed(2)} ` +
      `anchor=${(ring.yOut[1] - SPINE_Y0).toFixed(2)} vertex_r=${rc.toFixed(3)}`
  );
  console.log(
    "path: one out-pattern join + one in-pattern new_body cut (clip; land same per A/B half); open C kept; coplanar lips+hex; through-spine open centers; A/B grooves +0.2 mm; side-hole ops match v16.48"
  );
}

main();
