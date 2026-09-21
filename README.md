# INJS2065 Technic Case

**Current revision: v16.39** — tight Technic floor `shell_x=[-12,28]` `shell_y=[-12,12]`; clips external on ±Y again; face pins keep no `(0,±8)`; green side pins through-class; journal Ø7.94 / face Ø8.15 / Technic 8.0 kept; BuckleClip geom untouched. See `design/`.

## Parts
- ClamshellA (blue lower), ClamshellB (green upper), OutputHub, BuckleClipYP/YM
- Purchased proxies: Servo body, MR128 bearing

## Process
- **SoT:** `design/design_v16_39.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
- Branch: `cad-bot/v16.23-current`
- Fits: journal **Ø7.94**, face hole **Ø8.15**, BRG pocket **12.3**, CROSS_DEPTH **8.0**
