# Session handover — v16.44

## Geometry (this cut)
- **Clip Z:** mate-centered `split_z=18.25`; `CLIP_Z=[12.45, 24.05]` equal ±5.8 A/B; `CLIP_X=[-7.5, 7.5]` (15 mm).
- **Inner lips:** REMOVED (`cyp_xbar0`/`cyp_xbar2`). Outer-edge open-C lip KEPT (Y≈[10.4,12.0] after `cyp_open`).
- **AM hex clamp faces:** 6 flat-top hex bosses on clip inner face (XZ sketch → extrude −Y), proud 1.2 mm to Y[9.2,10.4]; mirrored to −Y with clip.
- **Land receptacles:** shallow hex pockets FF 3.1 / depth 1.35 on ±Y spine lands of ClamshellA/B (FDM clearance vs boss FF 2.8 / depth 1.2).
- **Pockets envelope:** POCKET_X=[-7.55,7.55]; land spine/leg ±7.46; shared CLIP refs.
- **Side Technic:** no x=0; green sides x={-8,8,16,24} @ z=30 on ±Y.
- **-Y clip:** Thunder-safe `solid_mirror` of +Y (no `cut_cym_open`).
- **shell:** [-12, 28] × [±12].

## Parent next
1. `git pull` on Thunder `C:\\Users\\jeffg\\dev\\INJS2065-Technic-Case` branch `cad-bot/v16.44-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_44.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: magenta clip mid on split_z 18.25; no inner xbar teeth; outer lip present; hex texture on clamp face; land hex pockets; solid_mirror -Y; shell ≈[-12,28]×[±12].
4. MCP on box was Not connected this cut — validate on Thunder.

## VERIFY (nominal)
| Item | Value | Notes |
|------|-------|-------|
| Former xbar Y engage (removed) | 1.2 mm (Y 9.2→10.4) | matched by hex proud |
| Hex boss FF / R_circ | 2.8 / 1.4 mm | flat-top rot 30° |
| Hex boss depth | 1.2 mm | = lip height |
| Pocket FF / R_circ | 3.1 / 1.55 mm | +0.15/side FDM clearance |
| Pocket depth | 1.35 mm | +0.15 vs boss |
| Hex centers X | −4.5, 0, 4.5 | within CLIP_X ±7.5 |
| Hex centers Z | 16.5, 20.0 | A/B spine land bands |
