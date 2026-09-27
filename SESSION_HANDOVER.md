# Session handover — v16.57

## Geometry
- Source of truth: `design/design_v16_57.nbcad.jsonc`
- Clip face: 14 hex cells, rotation 30° (flats parallel to Z), wall 0.8 mm, open flat-to-flat 3.5 mm (R 1.75, outer R 2.55). Pockets are blind and stop at the spine face. The hex outline is the clip edge.
- Shell floor keeps the matching hex bosses. Only the wall rings are cut, 0.2 mm loose (outer R 2.75, inner R 1.55).
- Locating pins: near X=-8.4 and far X=24.4, Y=±9.4.
- Shell X=[-12, 28], Y=±12. Clip Z=[12.45, 24.05], X=[-7.5, 7.5], split_z=18.25.
- Side Technic holes unchanged. Print clips YZ on the bed, build +X.
- Review explode only: `design/design_v16_57_review_explode.nbcad.jsonc` (±14 mm Y).

## Check
1. Replay `design/design_v16_57.nbcad.jsonc` on a blank document.
2. `node design/validate_clip_hex_walls.cjs`
