---
name: AM snap-fit design
description: >-
  Use when designing or reviewing FDM/AM clips, latches, toggles, or cantilever
  snap-fits — before committing pocket depth, beam thickness, or seat geometry.
---
# AM / snap-fit design

Numeric clearance gates are necessary but not sufficient. A clip can pass gap checks and still print as an artifact, or a deep seat can consume the cavity wall.

## Before modeling
1. Name the **mechanism class**: cantilever snap, annular snap, latch/catch, living hinge, friction detent — pick one.
2. Name **roles** for every mating surface: flexure beam, hook/barb, seat/shoulder, relief cut, stop face. Do not reuse one thickness for all roles.
3. State **print orientation intent** for the flexure (layer planes vs bend axis). Prefer bending across layers only with explicit risk acceptance.
4. Pull local KB / MCP knowledge first (`nbcad://knowledge/...`, DFM / fits topics). Web search is escape hatch with citations.

## Geometry rules of thumb (starting guidance — confirm with coupon)
1. **Beam thickness** ≥ process min wall for material/nozzle; keep uniform; avoid necks thinner than adjacent walls without a designed hinge.
2. **Seat / pocket depth** must leave remaining wall ≥ min wall on *every* side after the seat is cut. Compute: `remaining = parent_wall - seat_depth - opposite_feature`. If remaining < min wall → redesign (shallower seat, boss, or thicker parent).
3. **Deflection space**: hook needs free travel; do not let the seat “eat” the cavity so the beam cannot flex.
4. **Lead-ins** on entry faces; avoid knife edges on printed barbs.
5. Prefer **role-based fits** (slip / locate / press) over a single global XY compensation.

## Validate before commit
1. Section the seat/cavity: prove remaining wall numerically and visually.
2. Print or replay a **fit/flex coupon** for the snap region alone when the joint is load-critical.
3. Run mesh/artifact audit on export candidates (no clip shards, no zero-volume spikes).
4. Do **not** treat “clearance ≥ X” alone as ship criteria.

## MCP / script
- Novel snap geometry → MCP step-by-step; `solid_scene` after cuts.
- Proven coupon pattern → script replay on a **blank** document only.
