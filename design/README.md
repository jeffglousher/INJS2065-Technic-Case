# INJS2065 v16.31 — OutputHub strengthen + clip visual mass on split_z

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Assembly remains **one-direction into upper_cover** (v16.25). Journal **Ø7.90** into BRG_ID 8.0. Friction open-C clips (no snaps).

## Why this revision

### A) Clip visual centering
Numeric v16.30 already had `clip_z_center == split_z == 18.25`, but Jeff’s live front photo (Design History ~298, proportions matching **v16.29**) showed the clip mid at ~20.25 → **+2 mm into upper/green**. Root cause: **stale JSONC / stale live replay**, not the v16.30 math.

v16.31:
1. Confirms HEAD `gen_meta` clip mid == `split_z`.
2. Regenerates JSONC from `gen_v16_31.py` (SoT) so disk matches.
3. Places **3 cross-bars** with visual-mass centroid on `split_z` (middle rung straddles the green/blue line).
4. Meta note for parent live replay: **equal clip height above/below split_z** in front view.

### B) OutputHub structural failure
Printed hub shed thin rings / spaghetti. Changes:
1. **Larger servo mate** — flange Ø11.2→**Ø12.0**, T 2.0→**2.8**.
2. **More solid column** — constant OD Ø12.0 from flange through column to bearing inner stop; horn wall **2.58→2.98 mm**.
3. **Small dome** at blind end of horn socket (H=1.0, not flat).
4. Supports left to Jeff; structure first.

## Hub before / after

| Dim | v16.30 | v16.31 |
|-----|--------|--------|
| Flange D | 11.2 | **12.0** |
| Flange T | 2.0 | **2.8** |
| Column OD | 11.2 | **12.0** (constant to inner stop) |
| Horn wall | 2.575 | **2.975** |
| Horn dome H | 0 (flat) | **1.0** |
| Cross depth | 8.0 | 8.0 |
| Journal | 7.90 | 7.90 |
| Spline depth | ~3.9 | ~3.9 |

Schematic: `design/shots/v16.31-hub-section-schematic.png`

## Clip Z (unchanged datum, regenerated + visual mass)

| | v16.29 (stale live) | v16.30/31 |
|--|---------------------|-----------|
| Datum | pocket mid ~20.25 | **split_z 18.25** |
| Clip mid | 20.25 (+2 into green) | **18.25** |
| Engage A/B | 3.8 / 7.8 | **5.8 / 5.8** |
| Cross-bars | 0 | **3** (mass on split_z) |

**Expected front view (parent live):** equal clip height above/below the green/blue split line. If Design History ≈298 or mid sits in green, reload this JSONC.

## Assembly (mandatory)

1. Bearing into **upper_cover** alone (from split → face).
2. OutputHub into that stack (flange → constant OD column → journal through bearing → Technic cross).
3. Servo into hub spline.
4. Lower clam over servo.
5. Open-C clips last.

## Generator

```bash
python3 design/gen_v16_31.py
```

Writes `injs2065-technic-clamshell.nbcad.jsonc` + `gen_meta.json`. Live CAD MCP not on this box — parent replays on Thunder `machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`.
