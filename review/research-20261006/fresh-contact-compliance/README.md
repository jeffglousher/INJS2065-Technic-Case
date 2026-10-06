# Four-patch compliance experiment

Fresh experiment, 2026-10-06. No design geometry changed. This is a private
part-specific screening study, separate from application dependencies.

`compliance.py` adapts the archived Gmsh/linear Tet4 assembly from
`D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005/fem.py`.
It imports the same archived body STEP, keeps E=1460 MPa and assumed nu=0.38,
and uses the same finite nub-patch selection and two idealized floor supports.
It applies four independent single-patch inward loads. A sparse LU factorization
is reused for four right-hand sides under each support condition.

The report records the source STEP and script hashes, mesh volume and quality,
library versions, patch node counts, actual area-weighted load-patch centroids,
areas and bounds, and the separate relief reference centers. The run gates
positive finite SICN, mesh volume within 0.1% of the imported OCCT volume,
free equilibrium, constrained-DOF reaction force and moment balance, elastic
work, reciprocal compliance, positive eigenvalues and an independently solved
summed-load superposition check. `C_ij` is inward area-weighted displacement
of patch i from one newton applied to patch j; mm/N. Displacement sampling and
load weighting use the same patch weights, making C symmetric by reciprocal
linear elasticity.

An illustrative calculation solves C F = g with all four g equal to the historical
0.027301820054 mm geometric target. It is only linear algebra with prescribed
patch displacements. It does **not** solve installed housing contact, contact gaps,
friction, insertion, housing flexibility or the changing patch/normal during
assembly. It cannot establish actual forces or permanent preload.

Run with an interpreter containing gmsh, numpy and scipy, or the original
experiment's `python-libs` directory:

```powershell
python compliance.py --source PATH_TO_ARCHIVED_PETG_MECHANICS --level 0.12
```

`--source` must contain `current.step` with the asserted SHA-256 recorded in the
script and the original `fem.py`. The script writes `compliance-LEVEL.json` beside
itself and does not modify the source directory. The source files have been
archived separately with the research package; large vendor wheels are not
required if dependencies are installed in the interpreter.

The run is monitored externally; sparse factorization has no in-process
cancellation or hard memory limit. Do not use this harness as an application
worker or trust it to bound arbitrary user models. The reviewed machine handled
the three specified mesh levels without exceeding the selected run budget.

The exact mesh can depend on Gmsh state/version. Compare physical quantities and
record node/element counts rather than asserting that a newly generated mesh is
identical to an earlier run. Original archived reports remain intact. The finer
0.12 mm run reproduces the earlier simultaneous-load deflection results through
superposition to floating-point roundoff.

Findings and limits are discussed in `../../analysis/DETENT-MECHANICS-FRESH-PASS.md`.

Run `python summarize.py` to regenerate `summary.json` from the three recorded
reports. That summary uses the absolute off-diagonal row sum as well as the
individual force comparison, so signed cross-patch effects cannot cancel and
mislead the coupling assessment. The finest normal-floor/clamped-floor absolute
row coupling ratios are 0.1240%/0.0938%; last-refinement maximum illustrative
force changes are 1.8825%/1.8149%. These are measured numerical screening
differences under the selected supports, not contact or material qualification.
