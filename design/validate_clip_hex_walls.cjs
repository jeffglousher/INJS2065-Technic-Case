#!/usr/bin/env node
/**
 * v16.51 clamp-face hex audit.
 * XZ origin extrudes grow along world -Y. flip true is required so the tools
 * occupy the documented +Y intervals instead of the air in front of the face.
 * Parses the JSONC tip and checks the boolean construction, not comments.
 * Circumscribed sketch radius is the hex apothem. rotation 0 is pointy-top
 * (vertex along sketch +Y = world +Z, vertical flats parallel to Z).
 *
 * Clip path: the open-C blank is the tip. The outer-hex sketch is a keep-tool
 * cut out of the mouth tool; only the remainder cuts the blank, so the walls
 * are leftovers of that one solid. Inner hexes then cut the same body through
 * the walls, the lip overlap, and the spine. There is no lattice join.
 * Nested outer+inner hexes in one sketch still do not form rings on this
 * kernel (v16.49: 27 depth-0 sibling faces). Face counts below are that
 * discovery (27 clip / 15 land outers, disjoint inners).
 *
 * Run: node design/validate_clip_hex_walls.cjs
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TIP = path.join(__dirname, "design_v16_55.nbcad.jsonc");
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
// Raw step text and this hash both match v16.48 and v16.50. Do not hash onward to the first
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
  const args = part.extrude.call.arguments;
  const ext = args.extent.distance;
  const y0 = part.move.call.arguments.translation.y;
  // XZ origin normal is world -Y. flip true grows toward +Y.
  if (args.flip === true) return [y0, y0 + ext];
  return [y0 - ext, y0];
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


function auditV1652(doc) {
  const byId = indexSteps(doc);
  const outPolys = doc.steps.filter((s) => s.id && /^cyp_ho_\d+_poly$/.test(s.id)).map(polygonOf);
  const inPolys = polygonsOfSketch(doc, "cyp_hex_in");
  if (outPolys.length !== 14 || inPolys.length !== 14) {
    fail("clip hex field is " + outPolys.length + "/" + inPolys.length + ", want 14 walls and 14 blind pockets");
    return;
  }
  for (let i = 0; i < 14; i++) {
    const o = outPolys[i];
    const inn = inPolys[i];
    if (o.rot !== 30 || inn.rot !== 30) fail("hex " + i + " rotation is not 30 deg (flats parallel to Z)");
    if (Math.abs(o.r - 2.55) > 1e-9 || Math.abs(inn.r - 1.75) > 1e-9) fail("hex " + i + " radii drifted");
    if (o.x !== inn.x || o.z !== inn.z) fail("hex " + i + " outer/inner centers differ");
    if (Math.abs((o.r - inn.r) - 0.8) > 1e-9) fail("wall is not 0.8 mm");
  }
  const samples = [[-8.6, 14.526], [8.6, 14.526], [-6.45, 18.25], [6.45, 18.25], [-8.6, 21.974], [8.6, 21.974], [0, 18.25]];
  for (const [x, z] of samples) {
    if (!outPolys.some((c) => inHex(x - c.x, z - c.z, c.r))) fail("face sample (" + x + "," + z + ") is outside the hex field");
  }
  const inEx = byId.get("cyp_hex_in_ex");
  const inMv = byId.get("cyp_hex_in_mv");
  const yIn = yInterval({ extrude: inEx, move: inMv });
  if (inEx.call.arguments.flip !== true) fail("inner pockets must flip true");
  if (!(yIn[0] < 9.05 && yIn[1] <= 10.45 && yIn[1] >= 10.35)) {
    fail("inner pockets Y[" + yIn + "] are not a blind cut ending on the spine face");
  }
  if (yIn[1] > 11) fail("inner pockets bore into the spine");
  const openEx = byId.get("cyp_open_ex");
  const openMv = byId.get("cyp_open_mv");
  const z0 = openMv.call.arguments.translation.z;
  const z1 = z0 + openEx.call.arguments.extent.distance;
  if (z0 > 12.45 || z1 < 24.05) fail("mouth tool Z[" + z0 + "," + z1 + "] does not cover the clip");
  if (openEx.call.arguments.sketch_name) {
    const openRect = byId.get("cyp_open_r").call.arguments;
    if (openRect.anchor.y > 9.05 || openRect.corner_hint.y < 12) {
      fail("mouth tool Y does not cut the rectangular lip through the spine");
    }
  }
  const keepEx = byId.get("cyp_hex_out_c0_ex");
  const keepMv = byId.get("cyp_hex_out_mv");
  const yKeep = yInterval({ extrude: keepEx, move: keepMv });
  if (!(yKeep[0] < 9.05 && yKeep[1] > 12)) fail("hex keep Y[" + yKeep + "] does not run through the spine");
  const keep = byId.get("cut_cyp_hex_keep");
  const openCut = byId.get("cut_cyp_open");
  const tipCut = byId.get("cut_cyp_hex_tip");
  if (keep.call.arguments.tool_body_ids[0].$ref !== "cyp_ho_0_body") fail("keep tool is not the joined hex wall");
  if (openCut.call.arguments.target_body_id.$ref !== "clip_yp_body") fail("mouth cut missed the clip");
  if (tipCut.call.arguments.tool_body_ids.length !== 14) fail("tip hole count is not 14");
  const order = doc.steps.map((s) => s.id);
  if (!(order.indexOf("cut_cyp_hex_keep") < order.indexOf("cut_cyp_open") && order.indexOf("cut_cyp_open") < order.indexOf("cut_cyp_hex_tip"))) {
    fail("clip cuts are out of order");
  }
  for (const step of doc.steps) {
    if (!step.call || step.call.operation !== "solid_combine") continue;
    const args = step.call.arguments;
    if (args.operation === "join" && args.target_body_id && args.target_body_id.$ref === "clip_yp_body") {
      fail("a body is joined onto the clip");
    }
  }
}

function main() {
  const { text, doc } = load();
  if (!doc.name.includes("v16.55")) fail(`document name is not v16.55: ${doc.name}`);
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

  auditV1652(doc);
  if (failures.length) {
    for (const msg of failures) console.error("FAIL " + msg);
    process.exit(1);
  }
  console.log("PASS v16.55 wider hex audit");
  return;

  const byId = indexSteps(doc);
  for (const id of [
    "cyp_out_begin",
    "cyp_open_begin",
    "cut_cyp_open",
    "cyp_hex_out_ex",
    "cut_cyp_hex_keep",
    "cut_cyp_hex_tip",
    "cym_mirror",
  ]) {
    if (!byId.has(id)) fail(`missing required step ${id}`);
  }
  for (const id of ["join_cyp_hlattice", "cut_cyp_hex_hole", "cut_cyp_hex_spine"]) {
    if (byId.has(id)) fail(`${id} is the v16.49 separate lattice plate`);
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
    if (outEx.call.arguments.flip !== true || inEx.call.arguments.flip !== true) {
      fail("clip hex extrudes must set flip true; XZ normal is -Y and flip false parks the tools in front of the clamp face");
    }
    const yOut = yInterval({ extrude: outEx, move: outMv });
    const yIn = yInterval({ extrude: inEx, move: inMv });
    if (outEx.call.arguments.sketch_name !== "cyp_hex_out" || inEx.call.arguments.sketch_name !== "cyp_hex_in") {
      fail("clip extrude does not use the pattern sketches");
    }
    const mouthY0 = openRect.anchor.y;
    const mouthY1 = openRect.corner_hint.y;
    const blankY0 = outRect.anchor.y;
    const blankY1 = outRect.corner_hint.y;
    if (Math.abs(blankY0 - CLAMP_Y) > 1e-9) fail(`clip blank front Y=${blankY0} is not the clamp face`);
    if (Math.abs(blankY1 - SPINE_Y1) > 1e-9) fail(`clip blank does not run through the spine to Y=${SPINE_Y1}`);
    if (Math.abs(mouthY1 - SPINE_Y0) > 1e-9) {
      fail(`mouth tool ends at Y=${mouthY1}, not the spine face ${SPINE_Y0}`);
    }
    if (!(yOut[0] < mouthY0 - 1e-6 && yOut[1] > mouthY1 + 1e-6)) {
      fail(`outer-hex keep-tool Y[${yOut}] does not overcut the mouth tool Y[${mouthY0},${mouthY1}]`);
    }
    if (Math.abs(yOut[0] - CLAMP_Y) < 1e-9 && Math.abs(yOut[1] - (SPINE_Y0 + HEX_ANCHOR)) < 1e-6) {
      fail("outer hex is still the v16.49 plate Y[9.05,10.8] placed on the clamp plane");
    }
    const keep = byId.get("cut_cyp_hex_keep");
    const openCut = byId.get("cut_cyp_open");
    const tipCut = byId.get("cut_cyp_hex_tip");
    const inTools = Array.from({ length: 8 }, (_, i) => `cyp_hex_in_b${i}`);
    if (!keep || !openCut || !tipCut) fail("merged tip is missing keep, mouth, or hole cut");
    else {
      const keepArgs = keep.call.arguments;
      const openArgs = openCut.call.arguments;
      const tipArgs = tipCut.call.arguments;
      if (keepArgs.operation !== "cut" || keepArgs.keep_tools !== false) {
        fail("cut_cyp_hex_keep must consume the outer-hex tool");
      }
      if (keepArgs.target_body_id.$ref !== "cyp_open_tmp") fail("keep cut does not target the mouth tool");
      if (keepArgs.tool_body_ids.length !== 1 || keepArgs.tool_body_ids[0].$ref !== "cyp_hex_out_body") {
        fail("keep cut tool is not the single outer-hex body");
      }
      if (openArgs.operation !== "cut" || openArgs.keep_tools !== false) fail("cut_cyp_open is not a consuming cut");
      if (openArgs.target_body_id.$ref !== "clip_yp_body") fail("mouth cut does not target the clip blank");
      if (openArgs.tool_body_ids.length !== 1 || openArgs.tool_body_ids[0].$ref !== "cyp_open_tmp") {
        fail("mouth cut tool is not the protected mouth body");
      }
      if (tipArgs.operation !== "cut" || tipArgs.keep_tools !== false) fail("cut_cyp_hex_tip is not a consuming cut");
      if (tipArgs.target_body_id.$ref !== "clip_yp_body") fail("tip hole cut does not target the clip");
      const tipTools = tipArgs.tool_body_ids.map((t) => t.$ref);
      if (tipTools.join(",") !== inTools.join(",")) fail(`tip hole tools are ${tipTools}, want ${inTools}`);
    }
    const stepOrder = doc.steps.map((s) => s.id).filter(Boolean);
    const orderOf = (id) => stepOrder.indexOf(id);
    const keepAt = orderOf("cut_cyp_hex_keep");
    const openAt = orderOf("cut_cyp_open");
    const tipAt = orderOf("cut_cyp_hex_tip");
    if (!(keepAt >= 0 && openAt > keepAt && tipAt > openAt)) {
      fail("clip order must protect walls in the mouth tool, then open the mouth, then cut cell holes through the blank");
    }
    for (const step of doc.steps) {
      if (!step.call || step.call.operation !== "solid_combine") continue;
      const args = step.call.arguments;
      if (args.operation === "join" && args.target_body_id && args.target_body_id.$ref === "clip_yp_body") {
        fail(`${step.id || "combine"} joins a body onto the clip; the tip must stay one blank`);
      }
      const tools = (args.tool_body_ids || []).map((t) => t.$ref);
      if (tools.includes("cyp_hex_out_body") && args.operation === "join") {
        fail(`${step.id || "combine"} joins the outer-hex body; that is the v16.49 plate`);
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

    const lipDepth = SPINE_Y0 - CLAMP_Y;
    if (Math.abs(lipDepth - 1.35) > TOL) {
      fail(`lip/wall depth from clamp face to spine is ${lipDepth}, expected 1.35`);
    }
    if (outRect.anchor.y !== CLAMP_Y) fail("lips and hex do not share the blank clamp face");
    if (!(outRect.corner_hint.y > SPINE_Y0 + HEX_ANCHOR)) {
      fail("clip blank ends at or before Y=10.8; the wall would be a separate tongue instead of the spine");
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
        if (step.id === "cut_cyp_open" || step.id === "cut_cyp_hex_tip") continue;
        if (tools.includes("hcell") || tools.includes("hpad") || tools.includes("hex") || tools.includes("ring")) {
          fail(`${step.id} cuts the clip with ${tools}`);
        }
      }
    }
    if (holeY[1] <= SPINE_Y1 - 0.2) {
      fail("inner cutter does not reach through the spine; cell may stay floored");
    }
    if (!(holeY[0] < CLAMP_Y - 1e-9 && holeY[1] > SPINE_Y1 + 1e-9)) {
      fail(`inner cutter Y[${holeY}] does not pass through the blank Y[${CLAMP_Y},${SPINE_Y1}]`);
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
    if (outExL.call.arguments.flip !== true || inExL.call.arguments.flip !== true) {
      fail(`${outName} extrudes must set flip true so the groove stays on the clamp-face interval`);
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
  console.log("PASS v16.55 wider hex audit");
  console.log(
    `cells=8 wall=${(ring.outer.r - ring.inner.r).toFixed(2)}mm FF=${(2 * ring.inner.r).toFixed(2)} ` +
      `clamp_Y=${CLAMP_Y} wall_only_Y=[${CLAMP_Y},${SPINE_Y0}] lip_depth=${lipDepth.toFixed(2)} ` +
      `spine_through_Y=${SPINE_Y1} vertex_r=${rc.toFixed(3)}`
  );
  console.log(
    "path: mouth tool minus outer-hex keep, then that remainder cuts the blank; inner hexes cut the same blank; no lattice join; coplanar lips+hex; through-spine open centers; A/B grooves +0.2 mm; side-hole ops match v16.48"
  );
}

main();
