# Corner detent mechanics: independent fresh pass

Reviewed 2026-10-06. Research and derived screening only; no CAD geometry changed.
This document contains private part dimensions and belongs in the private
INJS2065-Technic-Case repository. It must not be published in the public CAD
application repository. The application research index can reference its private
commit and carry generic methodological lessons.

## What this pass establishes

The hidden receiving pocket, minor residual contact and inward flex direction
remain a coherent mechanism. The evidence supports a fit-test print, not a
qualified retention, fatigue or creep design. Three gaps matter more than another
blind thickness reduction: the actual assembly/contact displacement, the supported
closed-frame compliance, and which PETG Basic formulation is on the spool.

The largest new material finding is that the manufacturer now publishes a V3.0
PETG Basic sheet with substantially higher tensile modulus than the V2.0 sheet
used by the earlier study. The earlier calculation must remain recorded as a V2
surrogate; it should not silently become a current-material prediction.

## Evidence and provenance

The reviewed private design repository was at commit
`5ab5f7deca6d3952012dfaf362740f53095cfd7e`. A fresh SHA-256 calculation of
`design/current.model.json` returned
`947a3531683decb6a92b62c1aadef36e00d2a1eab6c0a574cb4d0b49fef7b593`, matching
both the corner-relief validation and the earlier mechanics report.

The earlier mechanics STEP SHA-256 is recorded as
`16fcea27f5cef85e050fe2aea1bd8deab5011b71e94501e7192e2e4fc7dcb79a`.
Its original evidence directory is
`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005`.
The original reports and scripts are historical evidence; this pass read them
and recomputed scalar relationships without modifying them. A new four-load-case
experiment then reused their assembly method, as described below.

Read sources in the private repository: `CURRENT_REVIEW.md`, `FIT_DECISION.md`,
`review/local-corner-flex.json`, `review/seat-validation.json`,
`review/local-corner-flex/thin-wall-toolpath-audit.json`, and the snap-fit skill.
Read external evidence: `mechanics-review.json`, `material-assumptions.json`,
`fem.py`, all four `fem-*.json` reports, `field-summary.json`,
`relief-junctions.json`, and `validate-relief.py`.

Recorded geometry, with meanings kept separate:

- Nub radial apex rise: 0.20 mm; center Y = +/-9.80 mm.
- Local minimum corner wall: 0.8975842277 mm, measured in the clip plane.
- Minimum remaining backing: 1.00 mm in the broad-face normal direction.
- Full clip thickness: 2.95 mm; spherical pocket-side relief radius: 1.60 mm.
- Housing receiving radius: 0.50 mm, with axial extent |Y| = 9.12–9.95 mm.
- Historical `nominalYTravelToClearLip_mm`: 0.027301820054 mm.

The last quantity is an undeformed geometric clearance/travel result from the
receiving-seat audit. The accepted fit note calls it a nominal residual inward
travel target. Neither source establishes the actual installed elastic
deflection, peak insertion deflection, contact normal, or preload force.
The 0.20 mm radial nub rise is not the required 0.20 mm inward travel: those
dimensions are along different directions.

The part has full continuous hex walls coupled to a backing sheet. It has no
isolated free-ended cantilever. There is no verified effective beam span or
beam width in the evidence; choosing one from the relief diameter would be an
unsupported assumption.

## Manufacturer guidance and material version

The [Covestro snap-fit design guide](https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1556891135.pdf?hash=0B0654C1EA0B882DEB401F521C4E87DE&rev=75179dfd38264e398477a19a84601af5)
describes temporary deformation into an undercut, recovery after assembly,
root stress concentration, and friction/lead-angle effects. Its repeated-use
guidance reduces one-time strain allowances. Those molding-resin allowances
are not printed PETG or PLA limits. Its curved-beam and two-flexible-part
discussion also makes a simple rigid-root cantilever substitution inappropriate
for this coupled frame.

[BASF's own tools page](https://pmtools-na.basf.com/services.php) describes its
revised short-cantilever algorithm; this corroborates that conventional rigid-root
beam formulas are insufficient for short, wall-coupled snaps. Its calculator was
not run here.

The earlier study used the manufacturer's [PETG Basic TDS V2.0, preserved by
Additive-X](https://www.additive-x.com/shop/media/mageplaza/product_attachments/attachment_file/b/a/bambu_petg_basic_technical_data_sheet_18.pdf):
Young's modulus XY 1460 +/-190 MPa, Z 1120 +/-130 MPa; XY bending modulus
1790 +/-120 MPa. It reports solid specimens annealed/dried at 65 C for eight hours.
The [manufacturer-hosted TDS V3.0](https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf),
accessed 2026-10-06, describes an upgraded formulation and reports Young's modulus
XY 2780 +/-65 MPa, Z 2550 +/-100 MPa; XY bending modulus 1950 +/-50 MPa and Z
1740 +/-40 MPa. Its tests use 100% infill and specified X1-Carbon conditions;
annealing is not recommended there. These are coupon values, not the printed
clip's constitutive law. Neither sheet supplies its long-term relaxation or
cyclic endurance data. Break elongation is not a repeated-snap allowable strain.

Consequently, the material name alone no longer identifies the same dataset.
Keep sheet version and spool/formulation evidence with the print record. Use a
printed flex coupon in the actual orientation/profile to calibrate stiffness;
do not replace Young's modulus with bending modulus without labelling that as a
different surrogate.

## What the earlier actual-clip FEM does and does not show

The archived custom linear Tet4 continuum model used E = 1460 MPa, assumed
Poisson ratio 0.38, and two floor-support variants. Its finest mesh has 208,626
tetrahedra and 42,190 nodes. Its affine patch check passed; free-equilibrium
relative residuals were approximately 9e-13. On the final refinement the
force changed approximately 1.6%. These are meaningful numerical checks.

At the 0.02730182 mm average displacement target, the reported equal load per
nub is 4.39635 N with normal floor restraint and 4.51622 N with clamped floor
restraint. The reported maximum absolute principal strain is 2.1789% and
2.2379%, respectively. This is sufficient reason to investigate the load path
and contact patch before claiming the installed pressure is mechanically tiny.
It is not a measurement of insertion force or a validated strain allowance.

Fresh code inspection exposes a crucial interpretation detail: `fem.py` loads
all four nub patches simultaneously with 1 N each, computes four displacement
responses, then scales all four forces equally until their **mean** displacement
matches the target. The values named `stiffness_N_per_mm` are effective responses
to that simultaneous load case. They are not four independently measured
diagonal spring stiffnesses. The four finest normal-floor responses span
0.0061203–0.0063003 mm/N, so even that symmetric target is not an imposed equal
displacement at every nub.

The scalar mean effective stiffness is 161.0279 N/mm per simultaneously loaded
nub for normal-floor restraint, and approximately 165.417 N/mm for clamped-floor
restraint. Four individual patch load cases form the 4x4 compliance matrix C,
with u_i = sum(C_ij F_j); this pass actually computed them below. Next solve the installed
contact gaps and nonnegative reactions together. A closed contact requires its
gap to close; an open contact has zero reaction. Friction and the evolving
insertion contact require more than that static matrix. Equal force at every
nub need not describe the real sequence.

The two support variants differ only about 2.7% in this chosen load case. This
does not bound uncertainty from the true unilateral housing contacts, flexible
housing, assembly pose, friction, or a different nub load patch.

## New four-load-case experiment and a useful confirmation

`review/research-20261006/fresh-contact-compliance/compliance.py` independently applies each patch load,
reusing one sparse LU factorization per floor-support case. Actual runs used
local target mesh sizes 0.20, 0.12 and 0.09 mm. The finest run has 42,190 nodes
and 208,626 Tet4 elements, with minimum SICN 0.20289 and no negative-quality
elements. All three runs passed the affine patch check, force balance, free
equilibrium, constrained-DOF reaction force/moment balance, elastic work,
compliance reciprocity, positive compliance eigenvalues and an independently
solved summed-load superposition check. Finite positive SICN and mesh volume
within 0.1% of imported OCCT volume were gated before solving. Metadata keeps
actual area-weighted patch centroids, areas and bounds distinct from the relief
reference centers. The final finest run took approximately 46 seconds on this
machine; factorization/solve time is not a production worker benchmark.

The 0.12 and 0.09 mm matrices reproduce the archived simultaneous-load responses
to roundoff through C times the all-ones force vector. The 0.20 mm run generated
a slightly different mesh and differs about 0.23% in mean response. All original
reports remain intact.

The strongest fresh confirmation is that inter-patch coupling is small **under
the prescribed floor supports**: the finest maximum absolute off-diagonal row
sum divided by its diagonal is 0.1240% for normal-floor restraint and 0.0938%
for clamped-floor restraint. Absolute sums avoid hiding positive/negative
cancellation. In the illustrative equal-displacement calculation, ignoring
coupling changes the predicted patch forces by at most 0.0819% and 0.0657%,
respectively. Thus the earlier independent-spring interpretation was imprecise,
but this particular surrogate is almost decoupled. The largest unknown is the
real mating/support/contact condition, not this surrogate's off-diagonal terms.

Solving C F = g for four equal prescribed patch displacements of 0.02730182 mm
gives 4.3333–4.4610 N per patch with normal-floor restraint and 4.4681–4.5646 N
with clamped-floor restraint. These positive forces are mathematically consistent
with that prescribed displacement problem. They are **not installed contact
forces**: actual gaps, housing contact normals and unilateral contact were not
solved. The floor restrictions are bilateral constraints and are not proven
bounds on the unilateral installed-contact problem. The largest force change
from 0.12 to 0.09 mm is 1.8825% and 1.8149%,
respectively. That is a measured last-refinement difference, not an asymptotic
error bound or proof of local peak-strain convergence.

Full matrices, diagnostics, input/script hashes and a reproducible scalar
summary are in `review/research-20261006/fresh-contact-compliance/compliance-*.json`,
`summary.json` and `summarize.py` in that directory. This new study extends the prior numerical evidence without
changing the material surrogate, CAD model or qualification status.

## New theoretical sensitivities derived from the archived model

All derivations below retain the same geometry, fixed Poisson ratio, support
and load-pattern assumptions. They are screening statements, not new clip
simulation results.

For a homogeneous linear model K(E) = E K0. With a prescribed displacement,
force is proportional to E while displacement shape and strain are unchanged.
Substituting the V3 XY Young's modulus as an isotropic scalar gives the factor
2780/1460 = 1.90411. The old 4.396–4.516 N/nub result would therefore become
8.371–8.599 N/nub for that same displacement target. V3 Z Young's modulus as a
separate scalar sensitivity gives 7.679–7.888 N/nub. These are not an orthotropic
analysis or an uncertainty interval; they demonstrate that the material-version
gap is much larger than the last 1.6% mesh refinement.

With the old normal-floor surrogate, a +0.020 mm change in effective installed
travel gives 7.6169 N/nub instead of 4.3964 N/nub; a -0.020 mm change gives
1.1758 N/nub. A negative travel error exceeding 0.02730182 mm removes nominal
contact in a one-contact idealization. The perturbation is hypothetical; no
claim is made that this printer's error is +/-0.020 mm.

Define actual signed effective installed travel as
g_actual = g_nominal + e_relative - set_loss, where e_relative includes both
part geometry errors, assembly pose, wear and thermal effects. For a maximum
relative error magnitude T and maximum permanent set S, guaranteed contact
needs g_nominal - T - S > 0. An allowed long-term displacement g_allow also
requires g_nominal + T <= g_allow. Hence a feasible guaranteed-preload window
requires g_allow > 2T + S. Neither T, S nor g_allow has been measured here.
Small nominal overlap alone cannot establish reliable anti-rattle preload.

For the four equal-load surrogate at the mean travel target, elastic work is
U = 0.5 sum(F_i u_i) = 2 F mean(u). The normal-floor V2 value is 0.240057 N mm,
or 0.240057 mJ per clip. This is installed stored energy for that assumed
load case, not the snap-through energy barrier. A retaining barrier depends on
the difference between the seated and maximum passage states, which remain
unverified.

For a uniform rectangular free-ended beam, elementary bending gives
k = E b t^3/(4 L^3) and maximum strain = 1.5 t delta/L^2. For a beam of the same
full span supported rigidly at both ends and loaded at its midpoint,
k = 16 E b t^3/L^3 and maximum strain = 12 t delta/L^2. The corresponding
ratios are 64 in stiffness and eight in maximum strain at the same displacement.
These are idealized different boundary conditions, **not bounds on this clip**.
They show why silently treating the closed hex frame as a free-ended beam can
produce a large mistake.

The cubic thickness t belongs to the direction across the bending section.
Because requested flex is perpendicular to the broad face, the 0.8976 mm
**in-plane** wall is not automatically that t. It may act as section width,
while the 1 mm backing and its coupling to taller wall regions change the
three-dimensional bending/torsion response. Reducing a pure beam's width by
10% reduces stiffness by 10%; reducing its bending thickness by 10% reduces
stiffness by 27.1%. Do not apply the latter percentage to this corner-wall
dimension without identifying its neutral axis and load path.

Likewise, a 10% longer free beam gives approximately 24.9% lower stiffness and
17.4% lower bending strain at the same travel. A smoother, longer compliant
transition is therefore a credible candidate when needed; the percentages
must not be claimed for this coupled frame without an updated solve.

## Relief junctions, deformation mode and printed structure

The spherical cutter is round but its intersections need not be tangent. The
archived face-normal samples report raw changes of approximately 44.05,
55.88 and 102.64 degrees at relief boundaries. The script does not establish
consistent outward face-normal orientation, so 102.64 degrees is not a
certified dihedral angle. Even allowing reversal, these samples show nonzero
normal mismatch and cannot establish G1 continuity. A spherical relief alone
does not resolve the user's concern about a visible extra line or a sharp
junction.

Force convergence also does not certify local peak strain. Between the last
two meshes, the normal-floor peak moves from the upper nub to a lower nub;
global p99 strain changes nonmonotonically through refinement. The archived
0.12 mm mesh's regional field summary has approximately 1.08% maximum strain
in its selected relief region, 1.21% in the selected ridge and 2.23% near the
selected nub/load region. Sampling boxes and a finite prescribed load patch
affect those values. The pattern challenges the assumption that deformation
is dominated only by the desired long flexing span; local nub/ridge bending
and imposed contact concentration may matter. Use contact-patch sensitivity,
local mesh convergence and tangent transition geometry before ranking peaks.

The archived slicer audit preserves both boundary paths plus narrow gap fill
at its inspected thin-zone sections. This is stronger evidence than measuring
wall thickness alone. It does not establish bead bonding, void fraction,
anisotropic stiffness or fatigue. The 0.20 mm nub rise is an in-plane detail
in the intended outer-face-down orientation; its reproduction is governed by
wall paths and bead width as well as layer height. It should not be rejected
or accepted by dividing 0.20 mm by the layer height.

## Retention, preload and long-term behavior

The almost-relieved installed state agrees with the snap-fit principle, while
the user's requested slight retained contact can reduce free play. These are
compatible goals if the tolerance window exists. The receiving edge should
provide a geometric withdrawal barrier; continuous polymer spring pressure
should not be the only retention mechanism.

For a smooth profile delta(s), a frictionless one-degree-of-freedom model gives
U(s) = 0.5 k delta(s)^2 and axial force dU/ds = k delta(s) d(delta)/ds.
A longer S-curve lowers slope and can reduce peak insertion force without
changing peak travel. A symmetric profile in a geometrically symmetric mating
path also gives symmetric insertion/withdrawal energy barriers. Thus symmetry
and a stronger spring alone cannot guarantee easy insertion with much harder
removal. The housing edge/seat, contact sequence and friction can create that
asymmetry; they need explicit evaluation.

The primary paper [Yoshida and Wada, Mechanics of a snap-fit](https://arxiv.org/abs/2003.13566v2)
combines elasticity, friction and geometry to explain operational asymmetry
for a thin shell around a rigid cylinder. It supports investigating all three
effects; its cylinder-shell formulas do not certify this hex detent.

Under an idealized maintained deformation, a linear viscoelastic spring's
reaction tracks its relaxation modulus: F(t)/F(0) = E_relax(t)/E_relax(0).
Under maintained force, displacement instead grows with creep compliance.
This is a theoretical distinction, not a fitted PETG model. Actual assembly
has evolving contacts, so both relaxation and permanent set can change its
preload and barrier. No numerical PETG lifetime or temperature-dependent
margin can be inferred from a room-temperature Young's modulus, break
elongation or a heat-deflection-temperature number.

## Recommendations and next decisive measurements

1. Preserve the present geometry for a fit-test coupon or part. The evidence
   does not justify another blind thinning pass, or declare the 0.9 mm wall
   mechanically sufficient. Record spool/formulation and measured profile.
2. Measure peak inward passage travel, installed travel, insertion/removal
   force and free play. Establish acceptable values before optimizing them.
   Use the actual four-corner sequence, not four independent spring guesses.
3. Use the newly computed four-load-case compliance as a checked screening
   foundation, then add actual contact gaps and the retaining-edge path,
   distinguish clip/housing deformation and test
   multiple contact-patch sizes. A linear model can screen supports before a
   nonlinear/contact solve; it cannot replace it.
4. If force or strain requires revision, first evaluate a longer smooth local
   relief and tangent blends at the actual sphere/floor/wall intersections,
   preserving full walls, the nub envelope and the minimum backing. The old
   0.4–0.6 mm blend suggestion is a candidate study, not a validated dimension.
5. Check mesh quality, displacement/reactions/work and local strain convergence,
   then reslice each candidate. For the 0.4 mm nozzle, retain two robust boundary
   paths and inspect seam/gap-fill behavior rather than optimizing CAD thickness
   independently of extrusion.
6. Run retention/free-play measurements immediately after insertion and after
   representative dwell times, temperatures and cycles. Validate PLA separately:
   matching toolpaths establish geometric feasibility, not matching endurance.

This fresh pass confirms useful design logic and exposes testable sensitivities.
It does not establish a safe repeated-snap strain, a strong-retention target,
the peak installation displacement, or guaranteed long-term anti-rattle contact.
