---
name: Validate before show
description: >-
  Use before showing any CAD review images or claiming a design is ready —
  mandatory inner/behind/section/cutaway shot pack; reject blank or inside-solid
  renders.
---
# Validate before show

Passing numeric gates while shipping bad geometry happened when review cameras sat inside solids or frames were blank. No show without a valid shot pack.

## Mandatory shot pack (all required)
Capture and attach (or MCP viewport equivalents) before human/agent “looks good”:

1. **Outer isometric** — whole part visible, lit, not clipped
2. **Behind / rear** — opposite of primary cosmetic face
3. **Inner / cavity** — look into pockets, seats, wire windows
4. **Section or cutaway** — through critical wall, seat, or bearing bore
5. **Detail of critical joint** — snap, pin, bearing, fastener boss

Optional but recommended: bottom/bed face, exploded mates, fit coupon beside part.

## Automatic reject (do not present)
Reject and recapture if any frame shows:
- **Blank / near-blank** (empty background, no silhouette)
- **Camera inside solid** (cavity flood, back-face soup, silhouette is a blob of interior)
- **Wrong body / empty doc**
- **Clipped so the claim cannot be checked** (e.g. claiming wall thickness with no section)

## Procedure
1. After geometry mutate: `solid_scene` / document inspect — confirm bodies exist.
2. Place cameras **outside** bbox; for inner shots use section plane or intentionally clipped cutaway — not a camera origin inside volume.
3. For each shot: verify silhouette + recognizable features in the PNG before attaching.
4. Adversarial pass: would a hostile reviewer say “this image proves nothing”? If yes, reshoot.
5. Only then send the pack with a one-line claim tied to what the images show.

## Pair with
- Mesh/artifact audit before export
- Research-before-commit (dims cited)
- AM snap-fit section shot when clips/seats are involved
