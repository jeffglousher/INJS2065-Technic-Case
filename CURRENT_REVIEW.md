# Current honeycomb detent assembly — 2026-10-05

Editable project: [design/current.nbcad](design/current.nbcad). Canonical history: [design/current.model.json](design/current.model.json). The native archive and JSON payload were compared and match exactly.

## Local corner flex relief

Each clip retains eight blind hex pockets in two rows of four, full continuous walls and four symmetric S-curve nubs centered on the confirmed spans. Nub center Y = ±9.80 mm; apex rise = 0.20 mm. No isolation groove or through-cut was added.

Four rounded pocket-side reliefs thin only the nub-bearing corner regions of each clip. One shared R1.6 spherical profile is copied to the four positions and mirrored across Y = 0. The +Y centers are (-0.85, 9.40, 22.02), (16.85, 9.40, 22.02), (-3.80, 9.40, 14.48) and (13.90, 9.40, 14.48), in mm. The nominal minimum corner wall is 0.8976 mm, from the relief-to-outer-roof plane distance; minimum backing is 1.00 mm. The relief fades into thicker material away from its center. Its section meets the existing pocket without the small roof ledge found in the initial trial.

The detent exterior, clip perimeter, outer broad face and all five non-clip bodies are unchanged. Only the two clip bodies changed. The history now has 401 features: the previous 392 plus nine native construction features.

Both housing interfaces retain their existing rounded receiving seats. Receiver radius is 0.50 mm; axial limits are |Y| = 9.12–9.95 mm. The outer recess mouths retain their uniform hex outlines. The geometric residual inward-travel target remains approximately 0.0273 mm. This is not a measured preload force or a verified elastic deformation model.

## Checks and images

[Four corner closeups](review/corner-closeups/corner-closeups.png), [pocket ISO](review/local-corner-flex/01-pocket-iso.png), [pocket front](review/local-corner-flex/03-pocket-front.png), [outer ISO](review/local-corner-flex/06-outer-iso.png), [backing section](review/local-corner-flex/05-backing-section.png), [four corner extrusion paths](review/local-corner-flex/04-four-corner-toolpaths.png).

The follow-up audit found a clean design working tree and no newer uncommitted INJS2065 geometry in the CAD session snapshots. Native replay passed again. A fresh fine STL export matches the mesh used for the recorded slicer checks byte for byte. The new corner closeups use depth-tested orthographic rendering of that verified CAD mesh; no design geometry was changed. [Render provenance](review/corner-closeups/render-provenance.json) and [audit evidence](review/corner-closeups/work-audit.json) record the reviewed sources. Reproduce the images with `tools/render-corners.py` and a fine native STL export of body 173.

[Current native validation](review/local-corner-flex.json) records seven bodies, zero native errors, the five unchanged non-clip meshes, expected assembly contacts and both exported clip mesh audits. Each fine clip STL has 110,580 triangles, one connected component and two incident triangles per welded edge. The four intentional clip/housing contact groups remain approximately 0.0000358 mm³ each; no new interference was introduced.

Bambu Studio 2.8.2.61 successfully sliced the updated +Y clip with the Bambu X2D 0.4 mm profile in PETG at 0.16 and 0.12 mm layers, and PLA at 0.16 mm. The mirrored clip has matching volume and passed its own connected/manifold mesh audit. Each inspected normal section on both flanks of all four thin corner walls retains the pocket and exterior boundary paths; Classic adds narrow gap fill between them. [Path audit](review/local-corner-flex/thin-wall-toolpath-audit.json) samples layer tops ≥2.0 mm, where the relief approaches its maximum width. The path images show centerlines, not measured printed surfaces.

Print orientation: clip outer broad face on the build plate, pockets up. Saved settings use a 0.20 mm first layer, four requested wall loops, Classic walls, 0.42/0.45 mm outer/inner widths, 25% gyroid and supports off. The thin zones necessarily have fewer wall paths than the requested four loops. PETG and PLA produced matching local paths at 0.16 mm; this establishes slicer feasibility rather than equal mechanical behavior.

External review projects, fine meshes, G-code and scripts are preserved at D:/noBS-CAD-Reviews/INJS2065-Technic-Case/local-corner-flex-20261005.

## Qualification status

Ready for a fit-test print. Inward deflection, insertion force, retained force, rattle, creep and repeated insertion still need physical testing. The walls remain coupled to the backing; this revision has no free-standing cantilever and has not undergone a validated flexure simulation. PLA fatigue remains unqualified. No printer job was started.

## Historical cleanup

The earlier geometry-preserving cleanup reduced 476 features to 392 with identical meshes, topology and assembly contacts. Its [equality evidence](review/history-cleanup.json), [reference mappings](review/history-dedup-map.json) and [receiving-seat validation](review/seat-validation.json) remain unchanged. The new local corner reference explicitly records the authorized geometry change and does not replace that historical evidence.
