# INJS2065 Technic Case

**Current revision: v16.47** — open-C retainer (spine + legs) with connected 1.2 mm hex-wall rings and matching clamshell grooves. Envelope X[-7.5,7.5], Z[12.45,24.05] on split_z=18.25. No full-face pad. Shell [-12,28]×[±12]. Side Technic holes unchanged. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_47.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Audit: `node design/validate_clip_hex_walls.cjs`
- Branch: feature branch for v16.47 (previous integration branch `cad-bot/v16.46-current`)
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
