# INJS2065 v16.25 — one-direction assembly into upper cover

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Side Technic row is **blind 8.2 mm** from each outer Y (assembly-path tradeoff — see below). Buckle clips remain **friction-only open C** (no new snap/clip geometry).

## Half naming (locked)

| Jeff name | Body / component | Role |
|-----------|------------------|------|
| **upper_cover** | ClamshellB (green) | Business face, bearing pocket, Technic top/side, higher Z (split→face) |
| **lower_clam** | ClamshellA (blue) | Servo nest, lower Z (shell_z0→split) |

## Assembly sequence (mandatory — one-direction into upper)

1. Slot the **bearing** into the **upper cover** (alone — lower clam not present). Seat from the open/split side toward the business face, against the outer face lip.
2. Slot the **business-end adapter** (OutputHub: servo horn socket + Technic cross) into that bearing/stack — same open side: thick flange → step/neck → journal through bearing → Technic cross toward face.
3. Plug the **servo** in behind the adapter (spline into hub).
4. Add the **lower clamshell** over the servo body / remaining nest.
5. Attach the **side clips** (friction open-C last).

**Not allowed:** closing both halves around a stack assembled “inside,” or installing the bearing from the outer face through a full-depth Ø12.3 tunnel.

## What changed vs v16.24

| Feature | v16.24 (rejected) | v16.25 |
|--------|-------------------|--------|
| Assembly mode | both-halves-around / `inside` | **one_direction_into_upper** / `upper_from_split` |
| Insert path Z26→seat | Ø11.7 → **Ø8.8 waist** → Ø10.9 (blocked OD) | continuous **Ø12.3** (bearing + flange clear) |
| Outer face | Ø8.5 lip | Ø8.5 lip unchanged |
| Bearing pocket | h=3.6 at Z34.35 | unchanged |
| Hub flange / ledge | T=2.0, neck Ø8.5 | preserved |
| Side Technic | through corridors | **blind 8.2 mm** each outer face |

## Geometry implications

- **Outer retaining lip (Ø8.5 < OD 12):** blocks outward escape; hub journal clearance-fit poke-out (`FACE_HOLE_D − JOURNAL = 0.48` diametral).
- **No inner OD shoulder < 12:** would block split-side insert into upper alone.
- **Technic side wall impact:** through-sleeve nominal wall was ~1.075 mm at Ø8.8 throat. Continuous Ø12.3 insert path at Z30 **intersects** X=±8 Technic lands if through. Blind depth 8.2 mm keeps outer pin grip and stops before dumping the corridor into the hub cavity (~0.5 mm radial margin at blind bottom). Documented; assembly path wins over through-sleeve wall.

## Hub profile

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo ledge / step).
- Taper to **neck** Ø8.5; journal Ø8.02 through bearing; Technic cross 8 mm flush at Z42.
- Hub overall height 15.7 mm unchanged.

## Validation

- Numeric: insert path ≥12.3 Z26→34.35; pocket h=3.6; no Ø12.3 Z37.95→42; face 8.5; flange T 2.0; neck 8.5; flange ≤ insert path.
- Live CAD: blank-doc JSONC replay + section through bearing axis; see `validation_results.json` and `design/shots/`.
- Mesh section shots prove bearing into upper from split + lip at face.

## Generator

Edit `gen_v16_25.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Blind side Technic depth 8.2 mm vs restoring through-holes (would open into hub cavity with Ø12.3 path) — confirm preference.
2. Exact MR128 designation / seal style if not the proxy 12×8×3.5.
3. PETG poke-out allowance: keep diametral 0.48 mm, or open face hole after a coupon?
4. Physical PETG fit / axial load still require print confirmation.
