#!/usr/bin/env node
/**
 * v16.58 clip hex audit.
 * 14 cells, rotation 30 deg, wall 0.8 mm, open flat-to-flat 3.5 mm.
 * Inner pockets are blind and stop at the spine face.
 * XZ origin extrudes grow along world -Y; flip true is required.
 * Run: node design/validate_clip_hex_walls.cjs
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TIP = path.join(__dirname, "design_v16_58.nbcad.jsonc");
// Technic side-hole steps, in document order. Hash is the v16.48 baseline.
const SIDE_IDS = [
  "Side hole x-8 +Y",
  "Side hole x8 +Y",
  "Side hole x-8 -Y",
  "Side hole x8 -Y",
  "Side hole x16 +Y",
  "Side hole x24 +Y",
  "Side hole x16 -Y",
  "Side hole x24 -Y",
];
const SIDE_SHA256 = "b22b63a87f1e6f83501a6a1ff087a265313f0a465c69aca571483e48b373caa8";

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
    if (step.id && step.id.startsWith("Side hole ")) return true;
    if (step.let && Object.keys(step.let).some((key) => key.startsWith("Side hole ") && key.endsWith(" face"))) {
      return true;
    }
    return false;
  });
}

function inHex(dx, dz, apothem) {
  const ax = Math.abs(dx);
  const az = Math.abs(dz);
  const bound = 0.5 * ax + (Math.sqrt(3) / 2) * az;
  return Math.max(ax, bound) <= apothem + 1e-9;
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

function sketchBounds(doc, sketchName) {
  const begin = doc.steps.findIndex(
    (s) => s.call && s.call.operation === "sketch_begin" && s.call.arguments.name === sketchName
  );
  const finish = doc.steps.findIndex(
    (s, index) => index > begin && s.call && s.call.operation === "sketch_finish"
  );
  return { begin, finish };
}

function polygonsOfSketch(doc, sketchName) {
  const { begin, finish } = sketchBounds(doc, sketchName);
  if (begin < 0 || finish < begin) {
    fail(`sketch ${sketchName} is missing begin/finish`);
    return [];
  }
  const beginName = doc.steps[begin].call.arguments.name;
  if (!beginName) fail(`${sketchName} sketch has no name`);
  const used = doc.steps.some(
    (step) => step.call && step.call.arguments && step.call.arguments.sketch_name === beginName
  );
  if (!used) fail(`${sketchName} sketch name ${beginName} is not used by a feature`);
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


function featureFor(doc, sketchName, operation) {
  return doc.steps.find(
    (step) => step.call && step.call.operation === operation && step.call.arguments.sketch_name === sketchName
  );
}

function moveAfter(doc, feature) {
  const index = doc.steps.indexOf(feature);
  return doc.steps.slice(index + 1).find((step) => step.call && step.call.operation === "solid_move_copy");
}

function auditV1652(doc) {
  const outPolys = [];
  for (let n = 1; n <= 14; n++) outPolys.push(...polygonsOfSketch(doc, "Clip +Y hex wall " + n));
  const inPolys = polygonsOfSketch(doc, "Clip +Y hex pockets");
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
  const inEx = featureFor(doc, "Clip +Y hex pockets", "solid_extrude");
  const inMv = moveAfter(doc, inEx);
  const yIn = yInterval({ extrude: inEx, move: inMv });
  if (inEx.call.arguments.flip !== true) fail("inner pockets must flip true");
  if (!(yIn[0] < 9.05 && yIn[1] <= 10.45 && yIn[1] >= 10.35)) {
    fail("inner pockets Y[" + yIn + "] are not a blind cut ending on the spine face");
  }
  if (yIn[1] > 11) fail("inner pockets bore into the spine");
  const openEx = featureFor(doc, "Clip +Y mouth", "solid_extrude");
  const openMv = moveAfter(doc, openEx);
  const z0 = openMv.call.arguments.translation.z;
  const z1 = z0 + openEx.call.arguments.extent.distance;
  if (z0 > 12.45 || z1 < 24.05) fail("mouth tool Z[" + z0 + "," + z1 + "] does not cover the clip");
  if (openEx.call.arguments.sketch_name) {
    const openRect = doc.steps.find(
      (step) => step.call && step.call.operation === "sketch_add_rectangle_locked" && step.id.startsWith("Clip +Y mouth")
    ).call.arguments;
    if (openRect.anchor.y > 9.05 || openRect.corner_hint.y < 12) {
      fail("mouth tool Y does not cut the rectangular lip through the spine");
    }
  }
  const keepEx = featureFor(doc, "Clip +Y hex wall 1", "solid_extrude");
  const keepMv = doc.steps.find((step) => step.id === "Move Clip +Y hex walls");
  const yKeep = yInterval({ extrude: keepEx, move: keepMv });
  if (!(yKeep[0] < 9.05 && yKeep[1] > 12)) fail("hex keep Y[" + yKeep + "] does not run through the spine");
  const keep = doc.steps.find((step) => step.id === "Keep Clip +Y hex walls");
  const openCut = doc.steps.find((step) => step.id === "Cut Clip +Y mouth");
  const tipCut = doc.steps.find((step) => step.id === "Cut Clip +Y hex pockets");
  if (keep.call.arguments.tool_body_ids[0].$ref !== "Clip +Y hex wall 1 body") fail("keep tool is not the joined hex wall");
  if (openCut.call.arguments.target_body_id.$ref !== "Buckle clip +Y") fail("mouth cut missed the clip");
  if (tipCut.call.arguments.tool_body_ids.length !== 14) fail("tip hole count is not 14");
  const order = doc.steps.map((s) => s.id);
  if (!(order.indexOf("Keep Clip +Y hex walls") < order.indexOf("Cut Clip +Y mouth") && order.indexOf("Cut Clip +Y mouth") < order.indexOf("Cut Clip +Y hex pockets"))) {
    fail("clip cuts are out of order");
  }
  for (const step of doc.steps) {
    if (!step.call || step.call.operation !== "solid_combine") continue;
    const args = step.call.arguments;
    if (args.operation === "join" && args.target_body_id && args.target_body_id.$ref === "Buckle clip +Y") {
      fail("a body is joined onto the clip");
    }
  }
}

function main() {
  const { text, doc } = load();
  if (!doc.name.includes("v16.58")) fail(`document name is not v16.58: ${doc.name}`);
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
    fail(`Technic side-hole ops changed (hash ${sideHash})`);
  }

  auditV1652(doc);
  if (failures.length) {
    for (const msg of failures) console.error("FAIL " + msg);
    process.exit(1);
  }
  console.log("PASS v16.58 hex-floor audit");
}

main();
