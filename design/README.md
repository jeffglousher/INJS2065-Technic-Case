## v16.41

- Lengthen BuckleClip onto green ClamshellB envelope: CLIP_Z [16.45, 41.55] center 29.0 (was [12.45, 24.05] on split_z).
- Remove middle tooth (`cyp_xbar1`); keep end teeth `cyp_xbar0` @19.25 and `cyp_xbar2` @37.55.
- Extend B spine/leg pockets to seat longer clip; raise A pocket bottom to 16.0.
- Remove side Technic holes at x=0 (`cb_side_1_1_2`, `cb_side_1_-1_2`) — shaft visibility.
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
- **Canonical:** `design/design/design_v16_41.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.41`).
