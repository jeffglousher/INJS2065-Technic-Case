# INJS2065 Technic servo cage (FDM)

Trap-style case for **Injora INJS2065** (7 kg, 25T Ø5.9 spline) with **MR128-2RS** (8×12×3.5) output bearing and **LEGO Technic** 8 mm grid mounts. Tabs stay on the servo — slide in from the rear, trap with the cover.

## BOM

| Item | Qty | Notes |
|------|----:|-------|
| Printed `injs2065_case_PRINT.stl` | 1 | Use the `_PRINT` file (bearing face on bed) |
| Printed `injs2065_cover.stl` | 1 | Outer face on bed |
| Printed `injs2065_horn_adapter.stl` | 1 | Journal standing or flange on bed |
| Printed `injs2065_fit_coupon.stl` | 1 | **Print first** |
| MR128-2RS bearing | 1 | 8×12×3.5, 2RS seals |
| Stock 25T horn + horn screw | 1 | Adapter bolts to horn |
| M2×6–8 mm screws | 4 | Cover → case bosses |
| M2×6 mm (adapter→horn) | 2 | Match your horn hole pattern |
| Technic pins / axles | as needed | Ø4.8 pins into Ø5.05 holes |

## Published dims used

| Feature | Value | Source |
|---------|------:|--------|
| Body | 23.1 × 13.0 × 25.9 mm | ServoDatabase / Injora (~23×13×25.8) |
| Spline | 25T, Ø5.9 | Injora |
| MR128-2RS | 8 × 12 × 3.5 | Catalog |

## VERIFY on your servo (calipers) before trusting tab fit

| Measurement | CAD default | Your reading |
|-------------|------------:|--------------|
| Tab tip-to-tip (X) | 32.0 | |
| Tab thickness (Y) | 2.0 | |
| Tab height (Z) | 12.5 | |
| M2 hole CTC | 28.0 | |
| Tab midplane from shaft face | 6.0 | |
| Horn M2 hole CTC | 7.0 | |

If any VERIFY row is off by >0.3 mm, say so and we regenerate the tab pocket / horn pattern.

## Fits (role-based, 0.4 mm nozzle — from your print-kit lessons)

| Joint | Role | CAD |
|-------|------|-----|
| Servo body → case | Insert slip | +0.35/side |
| Tabs → pockets | Slip + clamp by cover | +0.25–0.3 |
| Bearing OD → case | Light press + 0.8 lead-in on bed face | pocket Ø12.12 |
| Journal → bearing ID | Friction locate | Ø7.90 (sand/ream if tight) |
| Technic pin → hole | Running | Ø5.05 on 8 mm pitch |
| Cover M2 | Clearance / pilot | Ø2.25 / Ø1.7 pilots |

Do **not** apply one global XY hole compensation in the slicer; these numbers already encode roles. Optional: 0.8 mm lead-in already modeled on the bearing mouth.

## Architecture

```
Technic pin/axle ── cross-hole in journal
         │
   horn_adapter journal ──► MR128 inner race
   MR128 outer ──► case front pocket (bed face when printing)
   adapter flange ── M2 ──► stock 25T horn ──► servo
   servo body + tabs ── slide in from rear ── trapped by cover
```

## Print orientation (minimal support)

| Part | Orientation | Why |
|------|-------------|-----|
| **Case** | `injs2065_case_PRINT.stl` — bearing face on bed, open rear up | Accurate bearing seat; cavity needs no support |
| **Cover** | Outer (countersink) face on bed | Flat, no support |
| **Horn adapter** | Flange on bed, journal up | Round journal layers stack as circles; tip lead-in printable |
| **Coupon** | Flat on bed | Fast verify |

Suggested: PETG for case/cover/adapter (tough, Technic abuse). PLA OK for coupon. 4 walls, 25–40% gyroid, 0.2 mm layers. Dry PETG.

## Assembly

1. Print **fit coupon**. Press bearing into coupon pocket; try both journal plugs in the bearing ID. Confirm body slip on the pocket.
2. Press MR128-2RS into case front (bed face) until flush/seated on the shoulder of the pocket.
3. Bolt horn adapter to the stock horn (M2×2). Install horn on servo with the stock horn screw.
4. Feed the servo wire through the bottom window. Slide servo in from the rear so the journal enters the bearing; tabs ride the side pockets.
5. Install cover; snug 4× M2 into the rear bosses. Cover ribs clamp the tabs — servo cannot pull out toward the shaft.
6. Drop Technic pins through the 8 mm grid as needed.

## DFAM details baked in

- Bearing seat printed on the bed (elephant-foot helps press fit; lead-in modeled).
- Open-rear cavity → no internal support maze.
- Trap cover instead of cutting tabs (keeps stock servo intact / waterproof ears).
- Dissimilar roles for metal↔plastic vs plastic↔plastic.
- Technic pitch locked to 8 mm so beams/pins line up with stock LEGO.
- Wire window on −Z so the loom exits away from the Technic faces you are most likely to stack.

## Files

| File | Use |
|------|-----|
| `injs2065_case_PRINT.stl` | Print this case |
| `injs2065_case.stl` | Installed orientation (reference / CAD) |
| `injs2065_cover.stl` | Print |
| `injs2065_horn_adapter.stl` | Print |
| `injs2065_fit_coupon.stl` | Print first |
| `../src/injs2065_technic_case.py` | Parametric source (build123d) |

## Next tweaks (after coupon)

- Retune tab pocket from your caliper sheet
- Optional heat-set M2 inserts in cover bosses
- Optional second MR128 on a longer through-shaft if you want dual-bearing Technic axle
- Native `.nbcad` rebuild inside noBS CAD once you want associative drawings
