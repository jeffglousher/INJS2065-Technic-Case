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

## Parent next
1. Blank-doc script replay `design/design_v16_47.nbcad.jsonc` on Thunder (`cad_interface` action `script`, mode `fast`).
2. Live-check the boolean solid: open C silhouette, eight open hex rings joined to the spine and to each other, grooves in A and B (and −Y) with land centers still present, no full-face pad.
3. `node design/validate_clip_hex_walls.cjs` already passes offline. It does not replace a Thunder replay.

## VERIFY (nominal)
| Item | Value | Notes |
|------|-------|-------|
| Nozzle / wall | 0.4 mm → **1.2 mm** | perimeter and shared walls |
| Open cell FF / R_ap | 2.2 / 1.1 mm | through the ring |
| Outer R_ap | 2.3 mm | perimeter wall 1.2 |
| Groove R_ap | 0.9 / 2.5 | +0.2 mm each side |
| Rotation | **0° pointy-top** | vertical flats // Z |
| Ring Y | [9.2, 10.8] | 0.4 mm anchor into spine |
| Groove Y | +[9.05, 10.5], −[-10.5, -9.05] | floor 0.15 mm past the tip |
| Face span | 15 × 11.6 mm | CLIP_X × CLIP_Z |
| Cells | 8 staggered | S=3.4; middle row on split_z |

# Session handover — v16.45

## Geometry (this cut)
- **Clip Z:** mate-centered `split_z=18.25`; `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B; `CLIP_X=[-7.5, 7.5]` (15 mm).
- **Inner lips:** REMOVED (`cyp_xbar0`/`cyp_xbar2`). Outer-edge open-C lip KEPT (Y≈[10.4,12.0] after `cyp_open`).
- **Honeycomb WALL lattice (Jeff correction):** reject v16.44 solid hex bosses/pockets.
  - Clip: rectangular pad on clamp face depth **1.2 mm** → Y[9.2,10.4], then cut open hex cells leaving shared walls.
  - Wall **1.2 mm** (=3 FDM perimeters @ **0.4 mm** nozzle; allow 0.8–1.6).
  - Cell FF **2.8** (R_ap 1.4), **pointy-top rot 0°** (vertical flats // Z).
  - Staggered field **8 cells**: X even {-4,0,4} / odd {-2,2}; Z {14.786, 18.25, 21.714}; S=4.0, row_pitch≈3.464.
  - Land: matching shallow open-hex cuts FF **3.0** (+0.2 CLR), depth **1.35**, same centers/rotation on ClamshellA/B ±Y.
- **Pockets envelope:** POCKET_X=[-7.55,7.55]; land spine/leg ±7.46; shared CLIP refs.
- **Side Technic:** no x=0; green sides x={-8,8,16,24} @ z=30 on ±Y.
- **-Y clip:** Thunder-safe `solid_mirror` of +Y (no `cut_cym_open`).
- **shell:** [-12, 28] × [±12].
- **Print orient:** clip YZ on bed, build along +X; vertical hex flats // Z for strength.

## Parent next
1. `git pull` on Thunder `C:\\Users\\jeffg\\dev\\INJS2065-Technic-Case` branch `cad-bot/v16.45-current`.
2. Blank-doc script replay `design/design_v16_45.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: magenta clip mid on split_z 18.25; no inner xbar; outer lip present; **open honeycomb walls** (not solid bosses) on clamp face; land hex openings nestable; solid_mirror -Y; shell ≈[-12,28]×[±12].
4. Box MCP was Not connected this cut for live replay — validate Complete count on Thunder.

## VERIFY (nominal)
| Item | Value | Notes |
|------|-------|-------|
| Nozzle / wall | 0.4 mm → **1.2 mm** (3 perimeters) | allow 0.8–1.6 |
| Cell FF / R_ap | 2.8 / 1.4 mm | open cell |
| Rotation | **0° pointy-top** | vertical flats // Z |
| Lattice depth | 1.2 mm | pad Y[9.2,10.4] |
| Face span | 15 × 11.6 mm | CLIP_X × CLIP_Z |
| Cell counts | 3×3 staggered (8) | S=4.0, row_pitch≈3.464 |
| Land CLR / FF / depth | +0.2 → FF 3.0 / R 1.5 / 1.35 | nest openings |
| Print orient | YZ bed, build +X | flats // Z |
