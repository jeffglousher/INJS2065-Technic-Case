# Current honeycomb detent assembly — 2026-10-04

Editable project: [design/current.nbcad](design/current.nbcad). Canonical history: [design/current.model.json](design/current.model.json).

Each clip retains eight blind hex pockets in two rows of four, full continuous walls, no isolation grooves, and four symmetric S-curve nubs centered on the confirmed cantilever spans. Nub center Y = ±9.80 mm; apex rise = 0.20 mm. The accepted clip geometry is unchanged.

Both housing interfaces have rounded receiving seats at the eight matching locations. Receiver radius is 0.50 mm; axial limits are |Y| = 9.12–9.95 mm. The outer recess mouths retain their uniform hex outlines. The geometric residual inward-travel target at the retaining lip is approximately 0.0273 mm. This is not a measured preload force or a verified elastic deformation model.

## Geometry-preserving cleanup

476 history features became 392: 68 duplicate sketches share exact definitions, 15 duplicate datum planes share exact definitions, and one identity move was removed. Geometry parameters and body IDs were retained. The seven replayed bodies have byte-identical mesh arrays, unchanged topology signatures and exactly unchanged assembly contact results. Native history reports zero errors.

[Equality evidence](review/history-cleanup.json), [reference mappings](review/history-dedup-map.json) and [receiving-seat validation](review/seat-validation.json) are retained. The seat validation contains 224 successful local wall probes; minimum sampled radial remaining housing wall is 2.42 mm. All four exported shell/clip meshes passed the manifold audit. This is sampled wall evidence, not a global minimum-wall proof.

## Review images

[Installed isometric](review/installed-isometric.png), [rear](review/installed-rear.png), [housing recesses](review/housing-seats.png), [preload section](review/preload-section.png), [joint cutaway](review/joint-cutaway.png). The section images are temporary review cuts; the saved model is complete.

## Print status

Default intent: Bambu X2D, 0.4 mm nozzle, PETG, 0.16 mm layers, 0.20 mm first layer, four wall loops, Classic walls, 0.42/0.45 mm outer/inner widths, 25% gyroid. Clip outer broad face on the build plate, pockets up. PLA is desired but unqualified.

The final receiving-seat revision has not yet been sliced or physically tested. Previous sliced projects are archived and are not proof for this revision. Insertion travel, inward flex, retained force, rattle, creep and repeated insertion remain to be checked on printed parts. No printer job was started.
