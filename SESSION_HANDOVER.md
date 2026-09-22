# Session handover — v16.48

## Geometry (this cut)
- **Clip Z:** mate-centered `split_z=18.25`; `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B; `CLIP_X=[-7.5, 7.5]`.
- **Open C kept:** `cyp_out` minus `cyp_open`. Spine Y[10.4, 12.0]. Legs Z[12.45, 14.05] and Z[22.45, 24.05], Y[9.05, 10.4]. No inner xbars. No detents. No full-face pad.
- **Coplanar clamp face (Jeff 2026-09-22):** lips and hex walls both tip at **Y=9.05**. Hex solid Y[9.05, 10.8] = lip depth to spine (1.35 mm) + 0.4 mm anchor. Rejects v16.47 rings-on-recessed-spine-shelf (tips at 9.2 on face 10.4).
- **Through-spine open centers:** after each ring hole, the same inner hex cuts `clip_yp_body` so cell centers have no recessed spine floor between the lips.
- **Hex:** 8 pointy-top cells, rotation 0, circumscribed apothem. Open FF 2.2 (R 1.1), wall 1.2 (outer R 2.3), pitch 3.4. Centers X {-3.4, 0, 3.4} / {-1.7, 1.7}, Z {15.3055, 18.25, 21.1945}.
- **Land grooves:** outer R 2.5 minus inner R 0.9 (+0.2 mm). +Y Y[9.05, 10.55], −Y Y[-10.55, -9.05]. Bottom row → A, top row → B, middle row → both. Land centers remain. Not a honeycomb sheet in the thick wall.
- **Side Technic:** unchanged from v16.47/v16.46.
- **−Y clip:** `solid_mirror` of the finished +Y clip.
- **Print:** YZ on the bed, build +X.

## Parent next
1. Blank-doc script replay `design/design_v16_48.nbcad.jsonc` on Thunder (`cad_interface` action `script`, mode `fast`).
2. Live-check leftover solid: one clamp face (lips + hex tips coplanar); open C silhouette; eight open centers through the spine; no recessed middle shelf between the lips; A/B grooves nestable; no full-face pad.
3. `node design/validate_clip_hex_walls.cjs` already passes offline. It does not replace a Thunder replay.

## VERIFY (nominal)
| Item | Value | Notes |
|------|-------|-------|
| Clamp face Y | **9.05** | lip tip = hex tip |
| Lip / hex depth to spine | **1.35 mm** | same from clamp face |
| Ring Y | [9.05, 10.8] | +0.4 mm spine anchor |
| Through-spine centers | yes | `cut_cyp_ringN_spine` |
| Nozzle / wall | 0.4 mm → **1.2 mm** | perimeter and shared walls |
| Open cell FF / R_ap | 2.2 / 1.1 mm | through ring + spine |
| Outer R_ap | 2.3 mm | perimeter wall 1.2 |
| Groove R_ap | 0.9 / 2.5 | +0.2 mm each side |
| Groove Y | +[9.05, 10.55], −[-10.55, -9.05] | mouth on clamp face |
| Rotation | **0° pointy-top** | vertical flats // Z |
| Face span | 15 × 11.6 mm | CLIP_X × CLIP_Z |
| Cells | 8 staggered | S=3.4; middle row on split_z |

# Session handover — v16.47

## Geometry (this cut)
- **Clip Z:** mate-centered `split_z=18.25`; `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B; `CLIP_X=[-7.5, 7.5]`.
- **Open C kept:** `cyp_out` minus `cyp_open`. Spine Y[10.4, 12.0]. Legs Z[12.45, 14.05] and Z[22.45, 24.05], Y[9.05, 10.4]. No inner xbars. No detents.
- **Removed:** v16.46 `cyp_hpad` (the 15 × 11.6 × 1.2 mm sheet that closed the C) and the solid hex-cell cutters.
- **Hex rings:** 8 pointy-top cells, rotation 0, circumscribed apothem. Open FF 2.2 (R 1.1), wall 1.2 (outer R 2.3), pitch 3.4. Centers X {-3.4, 0, 3.4} / {-1.7, 1.7}, Z {15.3055, 18.25, 21.1945}.
- **Ring Y[9.2, 10.8]** on +Y (mirror makes −Y). 1.2 mm proud of the spine face, 0.4 mm volumetric bite into the spine. Inner hex is cut through the ring before the ring joins the clip, so cell centers stay open and the spine is not dimpled.
- **Land grooves, not a honeycomb sheet:** outer R 2.5 minus inner R 0.9 (+0.2 mm). +Y Y[9.05, 10.5], −Y Y[-10.5, -9.05]. Bottom row → clamshell A, top row → B, middle row (on the split) → both. Land centers remain.
- **Side Technic:** unchanged from v16.46.
- **−Y clip:** `solid_mirror` of the finished +Y clip.
- **Print:** YZ on the bed, build +X.
