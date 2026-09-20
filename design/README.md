# INJS2065 v16.26 — constant OutputHub OD until servo flange step

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Side Technic row is **blind 8.2 mm** from each outer Y. Buckle clips remain **friction-only open C** (no new snap/clip geometry). Assembly remains **one-direction into upper_cover** (v16.25 rules).

## Half naming (locked)

| Jeff name | Body / component | Role |
|-----------|------------------|------|
| **upper_cover** | ClamshellB (green) | Business face, bearing pocket, Technic top/side, higher Z (split→face) |
| **lower_clam** | ClamshellA (blue) | Servo nest, lower Z (shell_z0→split) |

## Assembly sequence (mandatory — one-direction into upper)

1. Slot the **bearing** into the **upper cover** (alone — lower clam not present). Seat from the open/split side toward the business face, against the outer face lip.
2. Slot the **business-end adapter** (OutputHub: servo horn socket + Technic cross) into that bearing/stack — same open side: thick servo-step flange → **constant Ø11.2 column** → journal through bearing → Technic cross toward face.
3. Plug the **servo** in behind the adapter (spline into hub).
4. Add the **lower clamshell** over the servo body / remaining nest.
5. Attach the **side clips** (friction open-C last).

**Not allowed:** closing both halves around a stack assembled “inside,” or installing the bearing from the outer face through a full-depth Ø12.3 tunnel.

## What changed vs v16.25

| Feature | v16.25 | v16.26 |
|--------|--------|--------|
| Hub mid OD | flange→neck loft (Ø11.2→Ø8.5) + free-standing riser lip Ø10.4 | **one continuous Ø11.2** from servo-step flange to bearing inner stop |
| Bearing support on hub | proud outer riser lip | **small inner journal shoulder** at Z≈34.15 (gap 0.20 under seat) |
| Insert path / face lip | Ø12.3 Z26→seat; face Ø8.5 | unchanged |
| Assembly mode | one_direction_into_upper | unchanged |
| Clips / snaps | open-C friction only | unchanged (no new snaps) |

## Hub profile

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo-step ledge) at Z26.3–28.3.
- **Constant OD column** Ø11.2 from flange through former neck/riser band up to **inner stop** Z34.15.
- **Journal** Ø8.02 continues through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: insert path ≥12.3 Z26→34.35; pocket h=3.6; no Ø12.3 Z37.95→42; face 8.5; flange T 2.0; **HUB_COLUMN_D = HUB_FLANGE_D = 11.2**; no mid lip; flange/column ≤ insert path.
- Live CAD: blank-doc JSONC replay + section through hub/bearing axis; see `validation_results.json` and `design/shots/`.

## Generator

Edit `gen_v16_26.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. PETG poke-out allowance: keep diametral 0.48 mm, or open face hole after a coupon?
4. Physical PETG fit / axial load still require print confirmation.
