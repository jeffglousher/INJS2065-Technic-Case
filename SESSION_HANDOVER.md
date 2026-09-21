# Session handover — v16.39

## Geometry (this cut)
- **shell_x:** [-16, 32] → **[-12, 28]** (40 mm = 5×8). Margin past x=−8 = **4 mm**; past x=+24 = **4 mm**. Near ear tip wall **2.8 mm**; far nest tip wall **7.0 mm**.
- **shell_y:** ±16 → **±12** (24 mm = 3×8). Side-face `$select` origin/1 ±12. Clips external again (frame_y_outer / spine at 12).
- **Ears:** unchanged nests; `far_end_open: false`, `near_ear_trapped: true`.
- **Face Technic @ Z42:** keep (±8,±8), (16,±8), (24,±8); **no (0,±8)**. Blind depth 8.0; lead-in Ø6.2×0.9; tip Ø6.2×1.2.
- **Side Technic (ClamshellB only):** x={−8,0,8,16,24} @ z=30 on ±Y. Depth 8.0 into ~5.32 mm cheek → **through** into cavity. No Technic on ClamshellA.
- **Ends ±X:** deferred this cut.
- **CLIP:** BuckleClip geom **untouched**; shell/pocket/land Y restores external straddle.

## Fits (unchanged)
- Journal **Ø7.94**; FACE_HOLE **Ø8.15**; BRG pocket **12.3**; CROSS_DEPTH **8.0**; split_z **18.25**.

## Schematic
```
SHELL_X0=-12 ------------------------- X=0 -------------------- SHELL_X1=28
|  nest_near     cav/body          nest_far   | tip wall 7mm |
| [-9.6,-5.55]  [-6 .. 17.4]     [16.95,21]   |               |
SHELL_Y=±12  (clips on outer ±Y)

Face @ Z42:  y=±8 × x={-8,+8,+16,+24}   (no x=0 near hub)
Side @ Z30 green: x={-8,0,8,16,24} on ±Y — through-class
```

## Parent next
1. `git pull` on Thunder `C:\Users\jeffg\dev\INJS2065-Technic-Case` branch `cad-bot/v16.23-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_39.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: shell ≈[-12,28]×[±12]; clips external on ±Y; face 8 pins without (0,±8); green sides 5×2 through; no blue Technic; BuckleClip geom unchanged; journal 7.94 / face 8.15 / BRG 12.3.
