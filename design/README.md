# INJS2065 v16.27 — open-C clips centered 50/50 in clamshell slot

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Side Technic row is **blind 8.2 mm** from each outer Y. Buckle clips remain **friction-only open C** (no new snap/clip geometry). Assembly remains **one-direction into upper_cover** (v16.25 rules). Hub keeps **v16.26 constant Ø11.2 OD**.

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

## What changed vs v16.26

| Feature | v16.26 | v16.27 |
|--------|--------|--------|
| Clip X in pocket | `SLOT_HALF = SPINE_HALF - 0.02` (0.04 total width interference) — clip looked biased in blue pocket | **Equal X side gaps 0.10 mm each**; clip X center == pocket X center (`CLIP_X = 0`) |
| Clip / pocket X bounds | clip `[−3.60, +3.60]` vs pocket `[−3.58, +3.58]` | clip `[−3.60, +3.60]` vs pocket `[−3.70, +3.70]` |
| Hub OD / assembly / snaps | constant Ø11.2; one-direction; open-C friction | **unchanged** |

## Clip centering (success gate)

- Shared center: `CLIP_X = 0`
- Clip X bounds: `CLIP_X ± CLIP_XW/2` → `[−3.60, +3.60]`
- Pocket X bounds: `CLIP_X ± SLOT_HALF` → `[−3.70, +3.70]`
- Side gaps: **0.10 mm** on −X and +X (equal within 0.05 mm)
- Friction remains Y-clamp open-C over retained lands (no new snaps/hooks/detents)

## Hub profile (unchanged from v16.26)

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo-step ledge) at Z26.3–28.3.
- **Constant OD column** Ø11.2 from flange through former neck/riser band up to **inner stop** Z34.15.
- **Journal** Ø8.02 continues through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: clip/pocket X centers match within 0.05 mm; equal side gaps; hub constant OD gates from v16.26 retained.
- Live CAD: blank-doc JSONC replay; see `validation_results.json` and `design/shots/`.

## Generator

Edit `gen_v16_27.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. PETG poke-out allowance: keep diametral 0.48 mm, or open face hole after a coupon?
4. Physical PETG fit / axial load still require print confirmation.
5. Confirm 0.10 mm X side gap feels right on print (was 0.04 interference in v16.26).
