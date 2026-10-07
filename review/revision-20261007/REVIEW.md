# Tangent corner relief and hidden receiver revision - 7 October 2026

The authorized changes are now in `design/current.model.json` and its matching native archive. Full walls and all eight blind hex pockets remain on each clip. The visible housing hex recess mouths have unchanged area, perimeter and wire counts. The servo, bearing and output hub meshes are unchanged. All 403 features replay without native errors.

## Geometry

The four pocket-side flex regions now use a 2.00 mm radial footprint and a tangent two-arc bowl, with 0.45 mm additional floor depth. The bowl joins the existing floor tangentially. Native 0.25 mm fillets blend its side-wall intersections. Relief centers move away from the exterior roof to retain the previous 0.897584 mm minimum in-plane wall. The deepest relief leaves 1.00 mm broad-face backing. This is still a continuous backed frame, not an isolated free-ended beam.

The nub remains symmetric about Y = +/-9.80 mm and retains its 0.20 mm protrusion and 1.44 mm meridian span. Its central crest radius increases from 0.60 to 0.80 mm, with tangent 0.40 mm outer arcs. The four confirmed span centers and exterior clip perimeter remain fixed. No isolation groove, detached tongue or special exterior housing notch was introduced.

The hidden receiver retains a 0.50 mm radial maximum. Its cylindrical portion runs from |Y| = 9.12 to 9.65 mm and ends in a spherical cap at |Y| = 10.15 mm. It replaces the previous abrupt flat end at 9.95 mm. This rounds the axial approach to contact; the cap/hex-flank intersection still exists and is not claimed to be a fully tangent 3D contact surface.

At the crest center the revised seat has 0.076970 mm radial clearance. At each diagonal housing flank, the exact plane distance from the nub axis remains b = 0.373205081 mm. The receiver cap reaches that flank at |Y| = 9.982743096 mm. The nub central meridian is r(Y) = -0.40 + sqrt(0.80^2 - (Y - 9.80)^2), in mm. The resulting local rigid-envelope inward shift is 0.022571061 mm, versus 0.027301820 mm previously. It is a geometric clearance target, not measured elastic preload.

The crest still overruns an unrelieved flank by 0.026794919 mm in the radial direction. This radial overrun must not be relabeled as inward Y travel or peak insertion deformation.

## Native geometry and export checks

The fine clip export has 159,442 triangles and positive volume 667.649878 mm3, versus STEP volume 667.647975 mm3. Fine clip and both housing meshes have exactly two incident triangles per welded edge at 0.00001 mm quantization. The STEP clip is one connected solid. Eight planar hex pocket floors remain on each clip. The minimum wall follows the surviving exterior roof plane and R2 cylindrical relief envelope; the concave blends add material at the junctions.

Exact native assembly checking finds only the four intended housing/clip contact groups, approximately 0.00002936 mm3 each. Other pair clearances remain as recorded in the new independent reference. Historical `local-corner-flex.json` and cleanup audits remain unchanged. The new reference is `review/tangent-corner-flex.json`.

Images are rendered from native mesh exports. Section contours and cutaway solids come directly from `solid_section_review`; the center and diagonal flank are shown separately because a center-only section misses engagement. Exploded translations are display offsets only, not stored assembly changes. No deformed/contact-solved surface is drawn.

## PETG Basic screening

Material basis remains Bambu PETG Basic V3: XY Young's modulus 2780 MPa, Z modulus 2550 MPa; Poisson ratio 0.38 is assumed. The manufacturer values are printed coupon data, not calibrated constitutive data for these X2D parts. A scalar E change scales force/stress at prescribed displacement and leaves the isotropic strain result unchanged. [Manufacturer technical data sheet](https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf).

New STEP geometry was meshed at two nominal levels. The coarse optimized mesh has 37,910 nodes / 171,688 tetrahedra; the fine mesh has 71,966 / 345,298 and explicitly refines nub faces to 0.035 mm. Minimum SICN is 0.09866 and 0.09773 respectively, with no inverted elements. Scripts validate affine elasticity, positive volume, residual, force/moment balance, work/energy and compliance reciprocity. Fine axial forces change at most 2.51% from coarse, but local peaks do not converge.

At the revised 0.02257 mm holding target, the fine axial cases give 4.15-5.04 N per nub, compared with 7.35-8.69 N previously. This is an assumed-patch screening reaction, not withdrawal force or measured snap force. At matched old travel the revised wide-patch force is approximately 5.42-6.06 N per nub versus 8.12-8.52 N: compliance improves even after separating out the smaller new travel.

Fine peak absolute principal strains, across the two assumed supports:

- Crest patch: previous 2.15-2.22%; revised 3.17-3.60%.
- Wide flank patches: previous 3.41-3.49%; revised 3.15-3.57%.
- Narrow flank patches: previous 7.24-7.43%; revised 4.29-4.38%.

These are local elastic-model peaks, not physical bounds. The improvement is not uniform. At matched old travel the revised wide-patch peaks are approximately 3.82-4.32%, so reducing reaction force must not be presented as a general strength improvement. Coarse-to-fine peak changes reach 38% in axial cases. Existing floor support edges remain stress-sensitive.

A separate inclined-pressure sensitivity uses the rounded cap's inward/radial normal ratio, prescribing the same mean inward Y movement. Fully clamped-floor cases predict 3.58-4.87% local strain and 3.70-4.29 N axial reaction per nub. Those local stresses exceed the credible linear elastic strength range. Normal-only floor cases react tangential loads at three rigid-mode anchors; their 15-17% peaks sit at an artificial anchor and are not PETG failure predictions. Both supports are bilateral idealizations rather than solved housing contact.

No physically credible peak dynamic insertion strain is established. The rigid press-on occurrence audit detects a retaining obstruction throughout approach, but cannot determine whether the actual frame bends inward, sideways, or contacts elsewhere. An assumed 0.05 mm inward movement would scale this linear holding case by 2.215; that is a displacement sensitivity, not a solved insertion prediction. Do not use it as an insertion safety factor.

## Native slicing

All three parts generated toolpaths with Bambu Studio, Bambu Lab X2D 0.4 nozzle and the actual resolved Bambu PETG Basic filament preset. Main layers are 0.12 mm, first layer 0.20 mm, Classic walls, four requested wall loops, 25% gyroid, supports off. The clip prints with its outer broad face on the plate and pockets up. Shells use their existing external broad-face orientations. The native results report return_code 0 and no plate warning. The clip CLI child required bounded shutdown after successful export; this is recorded separately from native slicing success. No print was sent.

The updated clip toolpath's nominal outer-wall capsule envelope gives 0.0107-0.0137 mm flank overrun in the layer containing the hidden receiver boundary, on all eight flanks. This uses commanded line width and an unsliced housing plane. Housing toolpaths were generated too, but are not included in that envelope comparison; physical paired preload is still unestablished. Slicer steps, seams, material shrinkage, flow and tolerances can exceed this small engagement. Four requested loops do not mean four loops fit in a 0.898 mm wall.

The reviewed unsliced 3MF projects are `clip-fine.3mf`, `lower-fine.3mf` and `upper-fine.3mf`. They reference the geometry checked here. G-code is retained in the external review directory; its hashes are saved in `native-slicing.json`.

## Decision

Keep this as the revised fit-test candidate. It implements the smooth relief and broader nub/receiving approach while preserving wall minimums and external housing appearance. It passes CAD replay, export integrity and native toolpath generation. It is not a strength, insertion-path, preload, creep or fatigue qualification.

Before repeated service use, test an actual Bambu PETG Basic clip/receiver pair in the specified orientations. Check seating, required bending direction, insertion and removal forces, permanent set, rattle and holding force after dwell. Neither a cantilever formula nor a generic PETG elongation-at-break value establishes acceptance here. PLA remains unqualified.

External meshes, mesh fields, logs and toolpaths: `D:/noBS-CAD-Reviews/INJS2065-Technic-Case/revision-20261007`. Archived earlier studies remain valid evidence for the earlier geometry only.
