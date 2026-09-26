# Session handover — v16.51

## Construction (this cut)
- **Jeff 2026-09-22 reject:** v16.49 is a clip plus a hex plate. The mouth is empty Y[9.05, 10.4]; the lattice Y[9.05, 10.8] is joined on. Not proud of the clamp plane. Proud of the spine, as a separate plate (0.4 mm tongue; middle row misses both legs).
- **Path:** one blank (`cyp_out`). Outer hexes are a keep-tool (27 faces, `join` into one tool body) cut out of the mouth tool, with 0.05 mm Y overcut. `cut_cyp_open` then removes only the mouth outside those walls. `cut_cyp_hex_tip` cuts the eight inner hexes through that same blank (walls, lip overlap, spine). No lattice join.
- **Jeff 2026-09-25:** v16.50 shots have no hex on the clamp face. XZ normal is world -Y. Those extrudes now set flip true so the keep-tool is Y[8.5,10.45] and the inner cutters are Y[8.85,12.25]. Land extrudes use the same flip so the grooves sit on the specified intervals.
- **Nested sketch:** still not rings on noBS CAD 0.2.0 (v16.49 discovery). Out and in stay two sketches. The out sketch is only the keep-tool.
- **Land:** unchanged. Same doctrine per A/B half. Middle cells 3 and 4 in both halves.
- **−Y:** `solid_mirror` of the finished +Y clip. Side Technic untouched.
- Review explode only: `design/design_v16_51_review_explode.nbcad.jsonc` (±14 Y). Not SoT.

## Geometry
- **Clip Z:** mate-centered `split_z=18.25`; `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B; `CLIP_X=[-7.5, 7.5]`.
- **Open C:** spine face Y=10.4, spine outer Y=12. Legs Z[12.45, 14.05] and Z[22.45, 24.05] are the same blank as the walls. No inner xbars. No detents. No full-face pad.
- **One clamp face:** blank front **Y=9.05**. Wall-only depth = lip depth = **1.35 mm** (to the spine face). The wall footprint continues as the spine through Y=12, including the old anchor plane Y=10.8, so that plane is not the back of a joined plate.
- **Through-spine open centers:** `cut_cyp_hex_tip` on `clip_yp_body`.
- **Hex:** 8 pointy-top cells, rotation 0, circumscribed apothem. Open FF 2.2 (R 1.1), wall 1.2 (outer R 2.3), pitch 3.4. Centers X {-3.4, 0, 3.4} / {-1.7, 1.7}, Z {15.3055, 18.25, 21.1945}.
- **Land grooves:** outer R 2.5 minus inner R 0.9 (+0.2 mm). +Y Y[9.05, 10.55], −Y Y[-10.55, -9.05]. Bottom row → A, top row → B, middle row → both.
- **Print:** YZ on the bed, build +X.

## Parent next
1. Blank-doc script replay `design/design_v16_51.nbcad.jsonc` on Thunder (`cad_interface` action `script`, mode `fast`).
2. Live-check one body: clamp face is lips + hex walls, no separate plate in the mouth, eight open centers through the spine, A/B grooves nest, no full-face pad.
3. `node design/validate_clip_hex_walls.cjs` passes offline. It does not replace a Thunder replay.

## VERIFY (nominal)
| Item | Value | Notes |
|------|-------|-------|
| Clamp face Y | **9.05** | blank front; lips and hex walls |
| Wall-only / lip depth | **1.35 mm** | Y[9.05, 10.4], flush with spine face |
| Wall footprint | through Y=12 | same solid as the spine; no plate back at 10.8 |
| Through-spine centers | yes | `cut_cyp_hex_tip` |
| Nozzle / wall | 0.4 mm → **1.2 mm** | perimeter and shared walls |
| Open cell FF / R_ap | 2.2 / 1.1 mm | through wall + spine |
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
