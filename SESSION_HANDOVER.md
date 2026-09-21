# Session handover — v16.38

## Geometry (this cut)
- **shell_x:** [-12, 24] → **[-16, 32]** (48 mm = 6×8). Margin past x=−8 hole = **8 mm**; past x=+16 = **16 mm** (x=24 column with 8 mm outer margin).
- **shell_y:** ±12 → **±16** (32 mm = 4×8). Side-face `$select` origin/1 ±16.
- **Ears:** unchanged nests; far tip wall 21→32 = **11 mm** (≥3). `far_end_open: false`, `near_ear_trapped: true`.
- **Face Technic @ Z42:** keep (±8,±8), (16,±8); **remove (0,±8)**; **add (24,±8)**. Blind depth 8.0; lead-in Ø6.2×0.9; tip Ø6.2×1.2.
- **Side Technic (ClamshellB only):** x={−8,0,8,16,24} @ z=30 on ±Y. No Technic on ClamshellA.
- **CLIP:** BuckleClip / pocket **untouched**.

## Fits (unchanged)
- Journal **Ø7.94**; FACE_HOLE **Ø8.15**; BRG pocket **12.3**; CROSS_DEPTH **8.0**; split_z **18.25**.

## Schematic
```
SHELL_X0=-16 ------------------------- X=0 -------------------- SHELL_X1=32
|  nest_near     cav/body          nest_far   | tip wall 11mm |
| [-9.6,-5.55]  [-6 .. 17.4]     [16.95,21]   |               |
SHELL_Y=±16

Face @ Z42:  y=±8 × x={-8,+8,+16,+24}   (no x=0 near hub)
Side @ Z30 green: x={-8,0,8,16,24} on ±Y
```

## Parent next
1. `git pull` on Thunder `C:\Users\jeffg\dev\INJS2065-Technic-Case` branch `cad-bot/v16.23-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_38.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: shell ≈[-16,32]×[±16]; face 8 pins without (0,±8) with (24,±8); green sides 5×2; no blue Technic; CLIP unchanged; journal 7.94 / face 8.15 / BRG 12.3.
