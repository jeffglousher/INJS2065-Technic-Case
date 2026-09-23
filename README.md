# INJS2065 Technic Case

**Current revision: v16.49** — same coplanar open-C clamp as v16.48, rebuilt as one hex-pattern sketch plus one extrude (out-pattern join, then in-pattern cut). Lips and 1.2 mm hex walls tip together at Y=9.05; through-spine open centers. Envelope X[-7.5,7.5], Z[12.45,24.05] on split_z=18.25. Matching A/B land grooves, same single-sketch doctrine per half. No full-face pad. Shell [-12,28]×[±12]. Side Technic holes unchanged. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_49.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Audit: `node design/validate_clip_hex_walls.cjs`
- Branch: `cursor/v16-49-single-sketch-hex-3694` (parent tip `cursor/v16-48-coplanar-clamp-face-e0a9`)
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
