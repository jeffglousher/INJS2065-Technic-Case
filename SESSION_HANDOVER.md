# Session handover — v16.42

## Geometry (this cut)
- **Clip Z:** recenter open-C on clamshell join/mate `split_z=18.25` (NOT green ClamshellB envelope mid ~29).
- **CLIP_Z:** [12.45, 24.05] — equal ±5.8 mm A/B engagement; clamshell-join span only (same as v16.40).
- **Pockets:** A_pocket_z≈[12.0, 18.3], B_pocket_z≈[18.2, 24.5]; POCKET = CLIP ± CLR (shared refs).
- **Teeth:** xbar0+xbar2 only (`cyp_xbar1` removed — keep v16.41).
- **Side Technic:** no x=0 shaft exposures (keep v16.41); remaining green sides at x={-8,8,16,24} @ z=30 on ±Y.
- **-Y clip:** Thunder-safe `solid_mirror` of +Y (no `cut_cym_open`) — keep v16.40.
- **shell:** [-12, 28] × [±12] — keep v16.39/40 tight Technic floor.
- **Ears / face Technic / fits:** unchanged (journal Ø7.94; FACE_HOLE Ø8.15; BRG 12.3; CROSS_DEPTH 8.0; split_z 18.25).

## Parent next
1. `git pull` on Thunder `C:\Users\jeffg\dev\INJS2065-Technic-Case` branch `cad-bot/v16.42-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_42.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: magenta clip mid on split_z 18.25 (short span straddling join); equal A/B; two teeth only; no x=0 side holes; solid_mirror -Y; shell ≈[-12,28]×[±12].
