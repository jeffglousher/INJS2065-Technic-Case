# v11 plan — drop-in numbers (from GD&T pass)

**Source of truth:** `/workspace/servo-case/v10/GDT-PASS.md`  
**This file:** short pointer for `gen_v11_*` — no CAD in the GD&T task.

## Decisions locked

| Topic | v11 choice |
|-------|------------|
| Clamp | **M2 heat-set × 4** at `(±9, ±9)` — **not** snap (snap = alternate only) |
| Servo body | **Loose interference:** `BODY_CLR = 0.10` (was 0.40) |
| Tabs | Y clearance **~0.30/side**; pocket height **~2.70** |
| Bearing | **8×12×3.5** confirmed; pocket **12.10**; journal **7.88**; lead 0.8; shoulder 1.2 |
| Hub spline | Socket **Ø6.20**; cross **5.20 × 2.20**; depth 5.5 |
| Alignment | **2×** molded pin **Ø2.50** / socket **Ø2.70** |
| Technic | Ø5.05 @ 8; sides X `{−8,0,+8}` if eligible; **Z_A=14.0, Z_B=26.0**; checklist + keep-outs |
| Heads | Recess below `face_z` so Technic stays flush |

## Constants to change first in gen_v11

```text
BODY_CLR          = 0.10
BRG_POCKET        = 12.10
JOURNAL           = 7.88
SPLINE_SOCKET     = 6.20          # was SPLINE_D+0.12
AXLE_SPAN         = 5.20
AXLE_ARM          = 2.20
INSERT_THREAD     = "M2"
INSERT_POCKET_D   = 3.2
INSERT_POCKET_DEPTH = 3.8
M_SCREW_CLEAR     = 2.35
boss_xy           = ((±9, ±9))    # four corners
ca_tech_z / cb    = 14.0 / 26.0
+ molded align pins
+ head recess from face_z
```

## Explicit non-goals for first v11 gen

- No snap geometry unless Jeff overrides M2.
- No teardrop hole print hacks yet.
- No envelope change (±12 shell, face_z 34.05 stack intent).

## Next implementation step

Implement `gen_v11_*.py` from v10 bodyclamp architecture using the table in **GDT-PASS.md §10**; run interference; confirm soft body/tab clearances and zero hard interferes.
