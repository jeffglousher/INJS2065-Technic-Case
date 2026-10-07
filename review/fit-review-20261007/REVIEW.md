# Current detent fit, deformation and CAD sanity review

Reviewed 7 October 2026. Geometry unchanged. Native replay of the committed
`design/current.model.json` passed: 401 features, seven bodies, no native errors,
all seven reviewed mesh hashes and topology signatures unchanged. Assembly
interference pairs exactly reproduce the previous accepted record. Source model
SHA-256: `947a3531683decb6a92b62c1aadef36e00d2a1eab6c0a574cb4d0b49fef7b593`.
The starting private design commit was `3a7eb79763dbf19b5ce109530f35f957d6c87175`.

These are fresh depth-tested renderings of native CAD STL exports, not generated
illustrations or deformed/contact-solved shapes. See [provenance](provenance.json).
The renderer used 0.002 mm linear and 0.08 rad angular tessellation settings.
Exact kinematic calculations below use saved analytic arcs and native OCCT face
planes, rather than infer micrometre clearances from the rendered pixels.

## Current clip and receiving pocket

[Clip and housing ISO](clip-housing-iso.png), [four corner closeups](detent-corners.png),
[installed center sections](installed-sections.png), [loaded flank sections](flank-contact.png).

Each clip has eight blind hex pockets in two rows of four, full continuous walls,
and four centered symmetric S-curve nubs. The nominal nub rise above its ridge is
0.20 mm. Its saved meridian uses tangent R0.60 mm arcs and spans Y = 9.08–10.52 mm,
centered at Y = 9.80 mm on the +Y clip. The shared rounded inner relief is R1.60 mm;
the minimum in-plane corner wall is 0.8976 mm, minimum broad-face-normal backing
is 1.00 mm, and full clip thickness is 2.95 mm. This is a backed continuous frame,
not an isolated free-ended beam.

The hidden housing receiving seat has radius 0.50 mm and extends over
|Y| = 9.12–9.95 mm, an axial length of 0.83 mm. Its recess mouths retain uniform
hex outlines. A nub's crest radius measured from the revolve axis is 0.40 mm;
this is distinct from its 0.20 mm height above the ridge.

## What the fresh three-dimensional check confirms

The center slice shows 0.10 mm radial crest-to-seat clearance. This initially
suggested a missing installed contact, but that slice misses the two diagonal
flanks. At the receiver's trailing end those flanks have 0.0077424 mm of radial
overrun into the adjacent housing planes. The current native geometry therefore
supports the intended mostly-relieved seat with small remaining flank engagement.
This is a geometric observation, not a proven contact-pressure distribution.

All four corners were checked independently against their actual native roof
plane equations. Their normal distance from the nub axis is b = 0.373205080756889 mm.
For the nub's trailing circular arc, radial envelope r(Y) is

    r(Y) = -0.20 + sqrt(0.60^2 - (Y - 9.80)^2) mm

At the receiving-seat end Y = 9.95 mm, r = 0.380947501931 mm. Translating this
local envelope inward toward smaller Y until its trailing flank just clears gives

    delta_Y = sqrt(0.60^2 - (b + 0.20)^2) - (9.95 - 9.80)
            = 0.027301820054 mm

The value agrees at all four nubs and independently reproduces the historical
holding-travel target. The new [exact geometry audit](contact-kinematics.json)
records source face IDs and each result. Actual elastic movement need not be a
rigid translation, and the housing may also deform. Neither this calculation nor
the tiny assembly overlap volumes measure actual preload force.

At the crest, the radial overrun relative to an unrelieved diagonal housing flank
would be 0.40 - b = 0.0267949 mm. This is useful geometric obstruction information;
it is **not** a 0.0268 mm inward-Y insertion deflection. The contact path, local
rotation and mixed deformation must be solved to connect those directions.

## Static holding surrogate

The archived actual-clip linear Tet4 model uses E = 1460 MPa and assumed nu = 0.38,
with 42,190 nodes and 208,626 tetrahedra. Its simultaneous four-patch load case
scales equal loads until the *mean* inward movement is 0.02730182 mm. It reports:

- Normal floor restraint: 4.39635 N per patch and 2.17894% maximum absolute principal strain.
- Clamped floor restraint: 4.51622 N per patch and 2.23789% maximum absolute principal strain.

These are supported screening calculations, not solved installed reactions,
withdrawal force or a repeated-use strain allowance. The two floor constraints
are support idealizations, not proven bounds on real unilateral housing contact.
Force refinement is about 1.6%; local maximum strain convergence is unestablished.

The newer four-independent-load-case experiment solves C F = delta for *equal
prescribed* movements. At the same target it gives 4.333–4.461 N per patch with
normal floor support and 4.468–4.565 N with clamped support. These forces belong
to a different loading prescription; the earlier equal-load strain peaks must
not be relabelled as its strain solution. See the archived
[fresh mechanics review](../analysis/DETENT-MECHANICS-FRESH-PASS.md).

Bambu's [manufacturer-hosted PETG Basic TDS V3.0](https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf),
rechecked 7 October, reports XY tensile E = 2780 MPa and Z tensile E = 2550 MPa.
The old model used the V2.0 XY value of 1460 MPa. Substituting the V3 XY value into
the same isotropic displacement-controlled surrogate scales the original patch
forces to 8.371–8.599 N, with unchanged strain. This is material sensitivity,
not a calibrated orthotropic printed-clip prediction. The user confirmed Bambu
Lab PETG Basic; the current estimate uses the manufacturer-hosted V3 data as its
main material case. The archived V2 case remains historical sensitivity evidence.
Coupon conditions differ from the actual clip profile.

## Dynamic insertion and tolerance gaps

No actual moving-contact insertion simulation has established peak inward-Y
travel, peak insertion strain, insertion force or the fraction of deformation
relieved after seating. The nominal 0.0273 mm holding shift and the 0.20 mm radial
nub height cannot substitute for those missing results. Public Rust/Rapier beam
experiments do not qualify this clip's assembly/contact behavior.

For illustration only, if a future contact solve found 0.050 mm movement under
the *same* original linear load pattern, its strain would scale to about
3.99–4.10%. This is conditional linear scaling, not a dynamic result or safety limit.

The installed contact has a particularly small tolerance margin. Increasing the
local housing flank-plane distance by just 0.0077424 mm would remove this nominal
flank preload. In the rigid-envelope calculation, a +0.005 mm change reduces the
holding-travel target from 0.02730 to 0.01025 mm; a -0.010 mm change increases it to
0.05688 mm. These are geometric sensitivity examples, not a predicted printer
error distribution. Nozzle diameter does not itself establish dimensional accuracy.

The fresh closeups also show that a round relief cutter does not create tangent
transitions where it meets the existing floor and walls. The archived native
surface-normal audit likewise has nonzero normal mismatches; its raw orientations
are not all certified outward dihedral angles. Keep this junction-blend issue
open; no geometry was altered in this review.

## Updated PETG Basic estimates and design recommendations

The follow-up uses the existing verified mesh for new load-footprint experiments
with current PETG Basic XY tensile stiffness E = 2780 MPa and assumed nu = 0.38.
It runs both the 0.12 and 0.09 mm local mesh levels, three finite pressure footprints
and two floor-support prescriptions. Equal inward displacement of 0.02730182 mm
is prescribed in the area-weighted sense at each of the four patches. Forces and
strains now belong to that same prescription. The original simultaneous equal-load
case was separately reproduced at each mesh/support to roundoff after modulus
scaling, confirming that the new code and boundary extraction retain the old model.

At the finer mesh, the assumed loading cases give:

- Broad crest footprint: 8.25–8.69 N per patch; 2.15–2.22% peak absolute principal strain.
- Wider paired flank footprints: 8.12–8.52 N per patch; 3.41–3.49% peak strain.
- Narrower paired flank footprints: 7.35–7.71 N per patch; 7.23–7.43% peak strain.

These are **load-patch sensitivities, not solved physical contact forces or actual
strain bounds**. The flank patches are padded beyond the true nominal engagement
band and still prescribe axial pressure. They do not solve normal contact,
friction, seating motion or flexible housing. This improves the assessment of
the old crest-load assumption, without substituting it for contact analysis.

Each solve checks affine elasticity, positive element volumes, imported volume
agreement, force/moment balance, free equilibrium, energy/work, positive reciprocal
compliance, and achieved target displacement. Final-level force changes remain
below 1.9% in these cases. The narrower-patch strain peak rises 10.7–11.3% between
levels and shifts position; it is not converged. Its footprint has only 12–14
boundary triangles per nub on the finer mesh. Even a low force change cannot
qualify its local maximum strain.

Maximum tensile principal elastic stress ranges from approximately 74 to 182 MPa
across these cases, above even the manufacturer's 51 MPa XY tensile-strength
coupon figure. This warns that the linear elastic/contact-footprint assumptions
cannot support physical peak predictions at the imposed travel. It does not
establish actual yield, fracture or a strength safety factor for the clip.
The manufacturer supplies neither a calibrated nonlinear printed constitutive
law nor a repeated-snap strain allowance in that sheet.

The elevated strains are highly localized: the volume-weighted 99th percentile
over the entire clip is approximately 0.19–0.22%. That metric differs from the old
unweighted element percentile and must not be directly compared with it.
About 15–26% of model strain energy lies in the small descriptive nub region used
by this study. These numbers support investigating local load transfer and the
backed frame; they do not excuse a high local surface strain.

Using the published Z tensile modulus of 2550 MPa as a separate isotropic
sensitivity scales the above forces by 2550/2780, about 0.917, with unchanged
displacement-controlled strains. Across these cases that gives 6.74–7.97 N per
patch. It is not an orthotropic model or a proven bound: shear properties and
printed directional behavior remain uncalibrated.

### Native slicing with the correct material preset

The previous saved tests used `Generic PETG @BBL X2D 0.4 nozzle`. New isolated
native CLI slices explicitly replace that filament with the installed
`Bambu PETG Basic @BBL X2D 0.4 nozzle` preset while preserving the reviewed mesh,
printer, orientation and process settings. Both 0.16 and 0.12 mm layer cases
complete with native return code 0. Effective config identifies Bambu Lab, density
1.25 g/cm³, flow ratio 0.95, main nozzle 250 °C and first layer 245 °C. No print was
sent and no user's active project or system profile was overwritten.

The nominal lateral bead-envelope check adds half the commanded extrusion width
to the saved outer/overhang wall paths at the layer crossing the receiver end.
Against the exact **unsliced** housing flank plane, it gives:

- 0.16 mm layers: 0.00156–0.00457 mm nominal flank overrun across the eight flanks.
- 0.12 mm layers: 0.00821–0.01055 mm nominal flank overrun.

The newly sliced Basic preset has the same checked boundary envelopes as the
Generic baseline. Material temperature/flow changes are still meaningful to
physical printing, but they do not correct this nominal geometry sensitivity.
The comparison models commanded bead widths and constant layer slabs. Real bead
cross sections, shrinkage, flow, seam and housing extrusion geometry can change
the result. It is **not** a printed fit measurement or a paired housing/clip
toolpath-interference qualification. In this print orientation, the nub's axial
S-curve varies through the layers, so unsliced 0.0273 mm clearance travel should
not silently become a prediction for the stepped printed surface.

See the [comparison figure](../petg-update-20261007/petg-estimate-update.png),
[checked result summary](../petg-update-20261007/summary.json),
[fine patch study](../petg-update-20261007/patch-sensitivity-0.09.json),
[second mesh level](../petg-update-20261007/patch-sensitivity-0.12.json),
[correct-material native receipts](../petg-update-20261007/native-basic-slicing.json),
and [Basic bead-envelope audit](../petg-update-20261007/bead-envelope.json).
The scripts and a labelled Generic baseline remain alongside them. Native Basic
G-code, resolved preset/config and logs are preserved at
`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007`.

### Design actions supported by these findings

1. Preserve the full walls, nub midpoint, symmetric S-curve and current minimum
   wall/backing for the next candidate. The evidence does not justify further
   blanket thinning of a region already relying on two printable boundary paths.
2. Replace the inner relief's floor/wall creases with tangent transitions and
   study a longer, gradual local relief along the nub-bearing span. Keep the
   minimum 0.90 mm corner wall and 1.00 mm backing until a candidate's native
   section, load path and slicer paths establish a better choice. A larger smooth
   compliant region is a candidate, not a proven stiffness reduction.
3. Smooth the hidden receiving edge and study a broader rounded flank contact.
   Keep the visible housing hex recess unchanged. The smoothing must preserve a
   withdrawal barrier and be evaluated together with the nub; adding a fillet
   alone could remove the small existing engagement.
4. Fix the next controlled clip test at 0.12 mm layers with the Basic preset.
   Retune nub and receiver together against the intended deposited geometry and
   measured fit. The current 7.7 µm CAD flank overrun, or smaller 0.16 mm nominal
   bead margin, is too fragile to assume reliable continuous preload without a
   measured manufacturing tolerance window.
5. Use measured insertion/holding travel, force and free play to calibrate actual
   unilateral contacts and printed stiffness. Then evaluate contact-patch spread,
   insertion and withdrawal motion, relaxation and repeated use. No peak dynamic
   insertion strain or lifetime prediction has been established here.

These are recommendations for the next geometry iteration. The current model
and native archive remain unchanged; smoothing radii, added relief length and
new preload dimensions have not been silently selected or qualified.

## Current decision

The nubs, full walls and hidden seats retain their intended nominal engagement.
The follow-up supports a geometry revision to improve local transitions and
contact distribution, and establishes 0.12 mm as the more consistent of the two
checked clip bead envelopes for a controlled fit test. It does not establish
reliable minor preload, insertion, creep, fatigue or PLA endurance. Preserve the
minimum wall/backing while studying the recommended geometry changes; use actual
contact and printed-fit evidence before assigning new preload dimensions.

Reproduction sources and native exports are preserved at
`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/fit-review-20261007`. Exact copies of the
three scripts are included in this folder for traceability. The native tool used
does not expose `solid_section_review`; the displayed sections interpolate its
fresh STL triangles. No screenshot is being passed off as an exact section result.
