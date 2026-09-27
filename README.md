# INJS2065 Technic Case

**Current revision: v16.57** — 14-cell clip hex (0.8 mm walls, 3.5 mm openings, blind to the spine). The shell floor keeps matching hex bosses with 0.2 mm wall clearance. Locating pins are at the corners. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_57.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Audit: `node design/validate_clip_hex_walls.cjs`
- Branch: repo default `cad-bot/v16.8-session-handover`
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
