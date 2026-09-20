# INJS2065 v16.24 — inside bearing insert, outer retaining lip, thicker hub ledge

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Lower side holes stay removed. Technic top sockets and side through paths keep the 6.2 mm entrance recess / 5.05 mm land / tip relief. Buckle clips remain **friction-only open C** (no new snap/clip geometry).

## Assembly sequence (correct)

1. Open the clamshell (split at Z18.25).
2. Seat the **MR128** (proxy Ø12 × ID8 × W3.5) into the **inside** pocket from the open cavity / split — not from the outer face.
3. Install the **OutputHub** from inside: servo-horn spline socket toward the servo; journal through the bearing bore; Technic cross toward the face.
4. Close the clamshell. The **outer face lip** (hole Ø8.5 < bearing OD 12) **retains** the bearing outer ring; the hub journal pokes out on a **clearance** fit (not a press through a Ø12.3 front pocket).
5. Slide on the open-C friction clips over the retained shell lands.
6. Physical PETG fit / axial load still require print confirmation.

## What changed vs v16.23

| Feature | v16.23 (wrong) | v16.24 |
|--------|----------------|--------|
| Bearing insertion | `front` — Ø12.3 open Z34.35→42.1 | `inside` — pocket h=3.6 only (Z34.35→37.95) |
| Outer face | Ø12.3 through (bearing can sit in outer pocket) | Ø8.5 poke-out; lip retains OD |
| Hub flange (servo ledge) | T=1.0 mm, then thin neck Ø8.3 | T=2.0 mm thick wall, step/taper to neck Ø8.5 |
| Clearance above seat | 12.3 to face | 12.3 through bearing width, then 8.5 to face |
| Side-sleeve nominal wall | 1.075 mm at Ø8.8 throat | unchanged (throat still Ø8.8) |

Bearing seat Z34.35 and face Z42 are unchanged. Hub overall height remains 15.7 mm; cross depth 8 mm flush at Z42; journal Ø8.02.

## Geometry roles (fits)

- **Housing shoulder (inner, Ø10.9):** supports bearing outer ring axially toward the cavity.
- **Outer retaining lip (Ø8.5 < OD 12):** blocks outward escape when the shell is closed.
- **Hub journal through bore:** Ø8.02 in bearing ID 8 (light transition/clearance intent; qualify on PETG).
- **Face poke-out:** diametral clearance `FACE_HOLE_D − JOURNAL = 0.48 mm` (radial 0.24 mm) — clearance class, not press.
- Say **radial** vs **diametral** explicitly when changing allowances.

## Hub profile

- **Thick flange** Ø11.2 × 2.0 mm parks on the servo (servo ledge / step).
- Taper to **neck** Ø8.5 through the side-sleeve Z band (preserves ~1.075 mm shell walls at Technic side bores).
- **Collar** Ø10.4 under the seat, then journal through the bearing; Technic cross preserved.

## Validation

- Numeric: pocket height 3.6; no Ø12.3 path Z37.95→42; face hole 8.5; flange T 2.0; neck 8.5.
- Live CAD: blank-doc JSONC replay + section through bearing axis preferred; see `validation_results.json`.
- Wall mins near Technic side bores: clearance throat remains Ø8.8 (not collapsed vs v16.23).

## Generator

Edit `gen_v16_24.py`, then run it to regenerate `injs2065-technic-clamshell.nbcad.jsonc` and `gen_meta.json`. Keep this README in sync.

## Open questions for Jeff

1. Exact MR128 designation / seal style (ZZ vs rubber) if not the proxy 12×8×3.5.
2. PETG poke-out allowance: keep diametral 0.48 mm, or open face hole after a coupon?
