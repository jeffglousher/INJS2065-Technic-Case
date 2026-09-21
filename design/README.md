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
- **Canonical:** `design/design_v16_43.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.44`).
