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
not a calibrated orthotropic printed-clip prediction. Spool formulation remains
unidentified; coupon conditions differ from the actual clip profile.

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

## Current decision

The nubs, full walls and hidden seats remain mechanically plausible. The fresh
three-dimensional check confirms the intended flank engagement and nominal
holding clearance target. The design is suitable for a controlled fit-test print,
but is not qualified for reliable minor preload, insertion, creep, fatigue or PLA
endurance. Preserve the current wall thickness pending measured insertion/holding
travel and force, free-play and dwell/cycle checks. Next analysis should use the
actual diagonal contact patches and assembly path, then examine tangent relief
blends and printed tolerance sensitivity before changing the geometry.

Reproduction sources and native exports are preserved at
`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/fit-review-20261007`. Exact copies of the
three scripts are included in this folder for traceability. The native tool used
does not expose `solid_section_review`; the displayed sections interpolate its
fresh STL triangles. No screenshot is being passed off as an exact section result.
