# Session handover — v16.33 (2026-09-20)

## Current
- Source of truth: **JSONC** at **v16.33** — edit/replay `design/design_v16_33.nbcad.jsonc` (plus `design/gen_meta.json`). Do **not** edit Python generators.
- Branch: `cad-bot/v16.23-current` (push only; leave draft PR #1 alone).
- Hub: flange Ø12.0×2.8, constant OD column, horn wall ~2.98, **strength dome H1.0 apex into solid (+Z)** (identity rot @ z=spline_depth).
- Technic cross: **CROSS_DEPTH 10.0** (was 8.0) — slot bottom local z=**5.7** (was 7.7); +2 mm into mid column; min wall above horn floor 1.8 mm.
- Clip: mid == split_z 18.25; 3 cross-bars with visual mass on split_z.
- Dome invert: `horn_dome_flip` rotation identity (was QX180); tip +Z into blind wall, not into horn cavity.

## Pending (parent)
1. Live CAD reload + viewport shots on Thunder (`machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Confirm hub section: dome arches into column; Technic slot deeper into mid.
3. Confirm front view: equal clip height above/below green/blue split line.
4. Jeff reprints OutputHub (add supports as needed); structure first.

## Next
Pull branch on Thunder → blank-doc replay `design/design_v16_33.nbcad.jsonc` → screenshot hub section (dome + cross depth) + clip vs split_z.
