# INJS2065 v16.29 — clip Z 50/50 in clamshell slot + wider/shorter open-C

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Side Technic row is **blind 8.2 mm** from each outer Y. Buckle clips remain **friction-only open C** (no new snap/clip geometry). Assembly remains **one-direction into upper_cover** (v16.25 rules). Hub keeps **v16.26 constant Ø11.2 OD**.

## Clarification (Jeff)

**"Center 50/50 in the clamshell slot"** means **VERTICAL along the mating face (Z)**, **not** side-to-side X.

- v16.27 X-centering (equal X gaps) was the **wrong axis**.
- v16.29 centers the clip in **Z**: mid-clip == mid-slot (±0.05), equal clearance above and below.

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

## VERIFY — clip Z center + wider/shorter (v16.29)

| Fit | Before (v16.28) | After (v16.29) | Notes |
|-----|-----------------|----------------|-------|
| **Clip Z vs slot Z** | clip `[14.05, 26.45]` mid **20.25**; slot `[14.00, 26.50]` mid **20.25**; gaps **0.05 / 0.05** | clip `[14.45, 26.05]` mid **20.25**; slot unchanged mid **20.25**; gaps **0.45 / 0.45** | Mid-clip == mid-slot (±0.05). Equal Z clearance above/below along mating face. Shorter span leaves larger equal end gaps. |
| **Clip Z span** | **12.40** | **11.60** (−0.80) | Slightly shorter — Jeff: wider+shorter = stronger. |
| **Clip X width** | `CLIP_XW` **7.20**; pocket **7.14**; interf **0.06** total (0.03/side) | `CLIP_XW` **7.40**; pocket **7.32**; interf **0.08** total (0.04/side) | Wider clip; tight FDM press kept in ~0.04–0.10 total band; equal side press; centers still match at X=0. |
| Journal / nest / hub OD / assembly / snaps | JOURNAL **7.90**; BODY_CLR **0.18**; TAB_Z_CLR **0.18**; hub Ø11.2; one-direction; open-C | **unchanged** | — |

### Clip Z centering (success gate)

- Slot Z = channel `[CHAN_Z0, CHAN_Z1]` = `[14.00, 26.50]` → mid **20.25**
- Clip Z = frame `[FRAME_Z0, FRAME_Z1]` = `[14.45, 26.05]` → mid **20.25**
- `|clip_zc − slot_zc| = 0.00` ≤ 0.05 **PASS**
- Z gaps below/above = **0.45 / 0.45** (equal)

### Clip X press (kept tight)

- Clip width `CLIP_XW = 7.40`; pocket width `2×SLOT_HALF = 7.32`
- Total X interference = `7.40 − 7.32 = 0.08 mm` (0.04 mm each side)
- Clip X center == pocket X center within 0.05 mm

## Hub profile (unchanged OD from v16.26)

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo-step ledge) at Z26.3–28.3.
- **Constant OD column** Ø11.2 from flange through former neck/riser band up to **inner stop** Z34.15.
- **Journal** Ø**7.90** continues through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: clip Z centers match; equal Z gaps; wider+shorter clip; X press 0.04/side; journal/nest/hub gates retained. See `validation_results.json`.
- Live CAD / MCP IFC: **not connected** on this box — parent to open script on Thunder (`machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`) and send images.
- Schematic: `design/shots/v16.29-clip-z-center-schematic.png`

## Generator

Edit `gen_v16_29.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. Physical PETG: confirm journal 7.90 slides into bearing ID 8.0 without rattle under load.
4. Physical PETG: confirm 0.08 mm total X clip press + shorter/wider Z profile feels right.
5. Nest BODY_CLR 0.18 / TAB_Z_CLR 0.18 — confirm servo ears seat without binding after print shrinkage.
