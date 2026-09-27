# Session handover — v16.58

## Geometry
- Source of truth: `design/design_v16_58.nbcad.jsonc`
- Clip face: 14 hex cells, rotation 30° (flats parallel to Z), wall 0.8 mm, open flat-to-flat 3.5 mm. Pockets are blind and stop at the spine face.
- Clamshell B bearing bore: one 12.3 mm cylinder from Z=26 to Z=37.95. Face hole is 8.15 mm through the outer wall.
- Servo cavity X=[-6.3, 17.4], Y=±6.68, on both shells.
- Locating pins: X=-8.4 and X=24.4, Y=±9.4.
- Shell X=[-12, 28], Y=±12. Clip Z=[12.45, 24.05], X=[-7.5, 7.5], split_z=18.25.
- Review explode only: `design/design_v16_58_review_explode.nbcad.jsonc` (±14 mm Y).

## Check
1. Replay `design/design_v16_58.nbcad.jsonc` on a blank document.
2. `node design/validate_clip_hex_walls.cjs`
