# INJS2065 Technic Case

**Current revision: v16.55** — hex field is one column wider on each side. Clamshell grooves are clipped to the pocket and split at Z=18.25. Side Technic holes unchanged. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_55.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Audit: `node design/validate_clip_hex_walls.cjs`
- Branch: repo default `cad-bot/v16.8-session-handover`
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
