# INJS2065 v16.30 — clip Z center on split_z + wider open-C + cross-bars

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Side Technic row is **blind 8.2 mm** from each outer Y. Buckle clips remain **friction-only open C** (no snaps/barbs — Jeff did **not** ask for snaps). Assembly remains **one-direction into upper_cover** (v16.25 rules). Hub keeps **v16.26 constant Ø11.2 OD**.

## Datum correction (Jeff)

**Clip Z center datum = `split_z` (clamshell division / A/B mating plane), typically 18.25 — NOT the mid of the full pocket/channel Z span.**

| Version | Datum used | Clip mid | Δ vs split_z |
|---------|------------|----------|--------------|
| v16.29 | pocket mid (CHAN mid ≈ 20.25) | **20.25** | **+2.00** (wrong) |
| v16.30 | **split_z** | **18.25** | **0.00** |

Equal land engagement above/below the A/B mating plane: `CLIP_ENGAGE_A == CLIP_ENGAGE_B`.

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

## VERIFY — clip on split_z + wider + cross-bars (v16.30)

| Fit | Before (v16.29) | After (v16.30) | Notes |
|-----|-----------------|----------------|-------|
| **Clip Z vs split_z** | clip `[14.45, 26.05]` mid **20.25**; Δ to split **+2.00** | clip `[12.45, 24.05]` mid **18.25**; Δ to split **0.00** | Mid-clip == split_z (±0.05). Equal A/B engagement **5.80 / 5.80**. |
| **Channel Z** | `[14.00, 26.50]` | `[12.00, 26.50]` | Extended into A so lowered clip still fits (end gap below 0.45). |
| **Clip X width** | `CLIP_XW` **7.40**; pocket **7.32**; interf **0.08** total | `CLIP_XW` **7.50**; pocket **7.42**; interf **0.08** total (0.04/side) | A little wider; tight FDM press kept in ~0.04–0.10 band. |
| **Cross members** | spine only (0 rungs) | **2** horizontal rungs + spine | FDM side print (build +X); mouth stays open; no snaps. |
| Journal / nest / hub OD / assembly / snaps | JOURNAL **7.90**; BODY_CLR **0.18**; TAB_Z_CLR **0.18**; hub Ø11.2; one-direction; open-C | **unchanged** | — |

### Clip Z centering (success gate)

- Datum `split_z` = **18.25** (tab mid = (17.0+19.5)/2)
- Clip Z = frame `[FRAME_Z0, FRAME_Z1]` = `[12.45, 24.05]` → mid **18.25**
- `|clip_zc − split_z| = 0.00` ≤ 0.05 **PASS**
- Engagement A/B = **5.80 / 5.80** (equal across mating plane)

### Clip X press (kept tight)

- Clip width `CLIP_XW = 7.50`; pocket width `2×SLOT_HALF = 7.42`
- Total X interference = `7.50 − 7.42 = 0.08 mm` (0.04 mm each side)
- Clip X center == pocket X center within 0.05 mm

## Hub profile (unchanged OD from v16.26)

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo-step ledge) at Z26.3–28.3.
- **Constant OD column** Ø11.2 from flange through former neck/riser band up to **inner stop** Z34.15.
- **Journal** Ø**7.90** continues through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: clip Z center == split_z; equal A/B engagement; wider clip; 2 cross-bars; X press 0.04/side; journal/nest/hub gates retained. See `validation_results.json`.
- Live CAD / MCP IFC: **not connected** on this box — parent to open script on Thunder (`machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`) and send images.
- Schematic: `design/shots/v16.30-clip-split-z-center-schematic.png`

## Generator

Edit `gen_v16_30.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. Physical PETG: confirm journal 7.90 slides into bearing ID 8.0 without rattle under load.
4. Physical PETG: confirm 0.08 mm total X clip press + split_z-centered engagement feels right.
5. Cross-bar count/thickness (2 × 1.20 mm) — adjust if print/assembly prefers more/fewer.
6. Nest BODY_CLR 0.18 / TAB_Z_CLR 0.18 — confirm servo ears seat without binding after print shrinkage.
