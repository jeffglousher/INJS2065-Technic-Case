#!/usr/bin/env node
/**
 * v16.57 clip hex audit.
 * 14 cells, rotation 30 deg, wall 0.8 mm, open flat-to-flat 3.5 mm.
 * Inner pockets are blind and stop at the spine face.
 * XZ origin extrudes grow along world -Y; flip true is required.
 * Run: node design/validate_clip_hex_walls.cjs
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const TIP = path.join(__dirname, "design_v16_57.nbcad.jsonc");
// Technic side-hole steps, in document order. Hash is the v16.48 baseline.
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
  if (!doc.name.includes("v16.57")) fail(`document name is not v16.57: ${doc.name}`);
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
  console.log("PASS v16.57 hex-floor audit");
}

main();
