# INJS2065 Technic Case

**Current revision: v16.38** — Technic envelope `shell_x=[-16,32]` `shell_y=[-16,16]`; face pins drop bearing-adjacent `(0,±8)`, add `(24,±8)`; denser green side pins; journal Ø7.94 / face Ø8.15 / Technic 8.0 kept; CLIP untouched. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_38.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Branch: `cad-bot/v16.23-current`
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
