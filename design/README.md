## v16.52

- Thin hex walls cover the whole clip face (27 cells). Inner pockets are blind and stop at the spine. Rotation 30° so flats run along Z. Land grooves share those centers, +0.2 mm. No lattice join. Side Technic unchanged.
- Review explode (not SoT): `design/design_v16_52_review_explode.nbcad.jsonc` moves clips ±14 mm in Y.
- Audit: `node design/validate_clip_hex_walls.cjs`

## v16.51

- **Jeff 2026-09-25:** v16.50 live shots are an open C with no hex on the clamp face. The XZ keep-tool and hole cutters were extruded along -Y into the air, so they never met the blank.
- flip true on the clip hex extrudes and the land-groove extrudes. Same translations now occupy outer keep Y[8.5,10.45], inner holes Y[8.85,12.25], land +Y[9.05,10.55] and -Y[-10.55,-9.05].
- Walls stay leftovers of the one blank. No lattice join. Wall-only depth Y[9.05,10.4]. Side Technic unchanged.
- Review explode (not SoT): `design/design_v16_51_review_explode.nbcad.jsonc` moves clips ±14 mm in Y.
- Audit: `node design/validate_clip_hex_walls.cjs`

## v16.50

- Superseded by v16.51. The keep-tool boolean was the right shape, but flip false parked it in front of the clamp face.

- **Jeff 2026-09-22 reject of v16.49:** the clip was an open C plus a separate hex-pattern extrusion. `cyp_open` emptied the mouth in front of the spine, then a lattice Y[9.05, 10.8] was joined on. That lattice is a plate in the mouth (0.4 mm spine tongue; middle row never meets a leg). It does not stick past the clamp plane.
- **Merge:** outer hexes are a keep-tool cut out of the mouth tool (0.05 mm Y overcut). Only the remainder cuts the blank, so the walls are leftovers of the open-C tip. Inner hexes cut that same body through the walls and the spine. No lattice join. Lips and hex share the blank face Y=9.05.
- Wall-only depth equals the lip, Y[9.05, 10.4] = 1.35 mm. The wall footprint continues as the spine to Y=12, so the old plate back face at Y=10.8 is inside one solid.
- Nested outer+inner hexes in one sketch still do not form rings (noBS CAD 0.2.0, v16.49 discovery: 27 depth-0 faces). Out and in stay two sketches; the out sketch is only the keep-tool.
- Land grooves unchanged (+0.2 mm), same per-half doctrine. Middle cells 3 and 4 in both halves. −Y clip stays `solid_mirror`. Side Technic unchanged.
- Review explode (not SoT): `design/design_v16_50_review_explode.nbcad.jsonc` moves clips ±14 mm in Y.
- Audit: `node design/validate_clip_hex_walls.cjs`

## v16.49

- Superseded by v16.50. One out-pattern join plus one in-pattern cut produced the separate lattice plate Jeff rejected. Nested rings in one sketch still fail profile discovery on this kernel.

## v16.48

- **Jeff 2026-09-22:** v16.47 was the wrong class — hex rings stuck on the recessed spine face (tips ~9.2 on shelf 10.4) while lips tipped at 9.05 → two layers.
- **One coplanar clamp face** at Y=9.05: lips and hex walls grow the same depth to the spine (1.35 mm) from that face. Hex solid Y[9.05, 10.8] (+0.4 mm spine anchor).
- Through-spine open centers (`cut_cyp_ringN_spine`) — no recessed floor in the cells between the lips. Open C kept; no full-face pad; no inner xbars.
- Land grooves updated: +Y[9.05, 10.55], −Y[-10.55, -9.05], +0.2 mm wall clearance, A/B split at z=18.25. Side Technic unchanged.
- Audit: `node design/validate_clip_hex_walls.cjs`

## v16.47

- **Reject v16.46** full-face `cyp_hpad`. Open-C + eight hex-wall rings Y[9.2, 10.8] on spine face. Superseded by v16.48 coplanar clamp face.

## v16.45

- **Jeff correction:** reject v16.44 solid hex bosses/pockets. Honeycomb **wall lattice** (shared walls, open cells) on locking-tab clamp face.
- Wall **1.2 mm** (3 FDM perimeters @ 0.4 mm nozzle; document allow 0.8–1.6). Depth 1.2 mm (= former lip height) pad on clip inner face Y[9.2,10.4], then cut open hex cells.
- Hex **pointy-top / vertical flats // Z** (`rotation_deg: 0`); cell FF 2.8; staggered 8-cell field on CLIP face 15×11.6.
- Land: matching shallow open hex cuts FF 3.0 (+0.2 CLR) depth 1.35 so patterns nest.
- Keep outer-edge open-C lip; no inner xbars; Thunder-safe −Y `solid_mirror`; mate-centered CLIP envelope unchanged.

## v16.44

- Remove inner engagement lips/teeth (`cyp_xbar0`, `cyp_xbar2` + joins). Keep outer-edge lip of open-C (`cyp_out` after `cyp_open`).
- Add AM hex/honeycomb bosses on clip↔land clamp faces: circumscribed R=1.4 (flat-to-flat 2.8), proud **1.2 mm** (= former xbar Y engage), flat-top rot 30°, 2×3 grid at Z={16.5,20.0} × X={±4.5,0}.
- Matching land hex pockets: R=1.55 (FF 3.1), depth 1.35, cut into ClamshellA/B ±Y spine faces.
- Keep mate-centered envelope: `CLIP_Z=[12.45,24.05]` / `split_z=18.25`, `CLIP_X=[-7.5,7.5]`; Thunder-safe −Y `solid_mirror`; no green-envelope long clip; no x=0 side recesses.

## v16.43

- Drop leftover side-pin lead-in/tip recesses at x=0,z=30 (`upper_pin_2_*` entry+tip on both ±Y). Through-holes already gone in v16.41; recesses were still cutting.
- Widen mate-centered open-C clip: `CLIP_X=[-7.5, 7.5]` (15 mm, was 7.5). Keep `CLIP_Z=[12.45, 24.05]` / `split_z=18.25` equal ±5.8 A/B — do not lengthen onto green.
- Update `POCKET_X=[-7.55, 7.55]`, land spine/leg pockets ±7.46, `cyp_out` / `cyp_open` / `cyp_xbar0`+`cyp_xbar2`. Keep 2-tooth (no xbar1); Thunder-safe −Y `solid_mirror`.
- No hex interlocking face this cut — slide-fit first.

## v16.42

- Recenter BuckleClip on clamshell join/mate `split_z=18.25`: `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B (revert v16.41 green-envelope centering ~29).
- Keep v16.41 two-tooth (`cyp_xbar0`+`cyp_xbar2`, no middle xbar1) + no side Technic through-holes at x=0.
- Keep `solid_mirror` xz for −Y clip (no `cut_cym_open`).
- Headless replay target: full completion.

## v16.40

- Thunder 0.2.0 failed at `cut_cym_open` (step 1024/1067). Replaced duplicated −Y clip construction with `solid_mirror` of finished +Y clip across origin XZ.
- Clip placement unchanged: outer ±Y lands, Z centered on `split_z` 18.25.
- Headless replay target: full completion.

# INJS2065 v16.39 — tight Technic floor + external clips

Jeff feedback on v16.38: cut oversized 8–16 mm margins to half-pitch **4 mm** Technic edge; restore `shell_y ±12` so clip pockets sit on outer ±Y again (not buried).

| Item | v16.38 (before) | v16.39 (after) | Notes |
|------|-----------------|----------------|-------|
| shell_x | [-16, 32] | **[-12, 28]** | 40 mm = 5×8; 4 mm past x=−8; 4 mm past x=+24 |
| shell_y | ±16 | **±12** | 24 mm = 3×8; side-face origin ±12; clips external |
| Face Technic | (±8,±8), (16,±8), (24,±8) | same | No (0,±8) bearing clash |
| Side Technic (green only) | x={−8,0,8,16,24} @ z=30 blind into ±16 cheek | same grid @ ±12 | Depth 8.0 into ~5.3 mm cheek → **through** |
| Far tip wall | 11.0 mm (32−21) | **7.0 mm** (28−21) | Still ≥3 mm; ears encapsulated |
| Near ear wall | 6.8 mm past tip (−16+9.2) | **2.8 mm** (−12+9.2) | ≥2.4–3 mm OK |
| CLIP / pocket | buried inside ±16 cheeks | **external again** | BuckleClip geom untouched; land/spine at y=12 |
| Hub mates | 7.94 / 8.15 / 12.3 / CROSS 8 | same | OutputHub mates unchanged |
| Ends ±X Technic | — | deferred | −X nest/cav risk; +X clear but no prior template |

## Replay
- **Canonical:** `design/design_v16_52.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.52`).
- Audit: `node design/validate_clip_hex_walls.cjs`
