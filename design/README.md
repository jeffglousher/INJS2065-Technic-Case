# INJS2065 v16.28 — FDM GD&T fit pass (0.4 mm nozzle / 0.2 mm layers, PETG)

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

## VERIFY — critical fits (v16.28)

| Fit | Before (v16.27) | After (v16.28) | Notes |
|-----|-----------------|----------------|-------|
| **Hub journal vs BRG_ID** | JOURNAL **8.02** into ID **8.0** → **−0.02 mm diametral** (press / interference) | JOURNAL **7.90** into ID **8.0** → **+0.10 mm diametral** / **+0.05 mm radial** clearance | Diametral = ID − OD; radial = half diametral. Needed for FDM assembly into bearing. |
| **Clip X in pocket** | Equal **+0.10 mm clearance**/side (pocket wider); centers match | Equal **−0.03 mm**/side = **0.06 mm total interference** (clip wider); centers still match (`CLIP_X=0`) | Intentional tight FDM press; Y-clamp still primary retention. Negative side gap = interference. |
| **Clip / pocket X bounds** | clip `[−3.60,+3.60]` vs pocket `[−3.70,+3.70]` | clip `[−3.60,+3.60]` vs pocket `[−3.57,+3.57]` | Centered equal press. |
| **Servo body nest (BODY_CLR)** | **0.05** → cav Y ±6.55 | **0.18** → cav Y ±6.68 | ~1 layer FDM clearance. |
| **Ear nest TAB_CLR (Y)** | **0.12** → NEST_Y 6.62 | **0.15** → NEST_Y 6.65 | Slight bump for PETG. |
| **Ear nest TAB_Z_CLR** | **0.03** → z `[16.97,19.53]` | **0.18** → z `[16.82,19.68]` | ≥1 layer FDM. |
| Hub OD / assembly / snaps | Ø11.2 constant; one-direction; open-C | **unchanged** | — |

### Diametral vs radial (journal)

- **Diametral clearance** = bearing ID − journal OD = `8.0 − 7.90 = 0.10 mm`
- **Radial clearance** = diametral / 2 = `0.05 mm` (gap on each side of the shaft)

### Clip X interference (centered)

- Clip width `CLIP_XW = 7.20`; pocket width `2×SLOT_HALF = 7.14`
- Total X interference = `7.20 − 7.14 = 0.06 mm` (0.03 mm each side)
- Clip X center == pocket X center within 0.05 mm

### Side effect noted

- `WALL_TO_CAV` = pocket floor − cav Y half = **2.32 mm** (was 2.45 with BODY_CLR 0.05). Outer deep-slot lip `LIP_Y` still **3.00 mm**. Blind side Technic depth **unchanged** (8.2 mm).

## Hub profile (unchanged OD from v16.26)

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo-step ledge) at Z26.3–28.3.
- **Constant OD column** Ø11.2 from flange through former neck/riser band up to **inner stop** Z34.15.
- **Journal** Ø**7.90** continues through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: journal diametral clr 0.10; clip X centers match; equal X press 0.03/side; nest clearances; hub constant OD gates retained. See `validation_results.json`.
- Live CAD / MCP IFC: **not connected** on this box — parent to open script on Thunder (`machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`) and send images.
- Schematic: `design/shots/v16.28-hub-clip-fit-schematic.png`

## Generator

Edit `gen_v16_28.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. Physical PETG: confirm journal 7.90 slides into bearing ID 8.0 without rattle under load.
4. Physical PETG: confirm 0.06 mm total X clip press feels right (vs looser 0.10 clr/side or tighter 0.10 interf total).
5. Nest BODY_CLR 0.18 / TAB_Z_CLR 0.18 — confirm servo ears seat without binding after print shrinkage.
