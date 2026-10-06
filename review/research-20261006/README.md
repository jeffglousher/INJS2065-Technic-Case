# Design research archive and fresh analysis

Archived 2026-10-06 without changing any design geometry. The canonical model
SHA-256 is `947a3531683decb6a92b62c1aadef36e00d2a1eab6c0a574cb4d0b49fef7b593`,
at prior part commit `5ab5f7deca6d3952012dfaf362740f53095cfd7e`.

This private archive preserves detailed part research. The public CAD application
PR [338](https://github.com/jackControls/Limo-CAD/pull/338) holds synthetic Rust
experiments, vendor/library research, review findings and the simulation plan.
Private CAD inputs are retained here instead of copied into that public PR.

## Evidence retained

- `petg-mechanics/`: original linear-Tet4 Python FEM implementation, four
  refinement reports, material assumptions, field summaries, CAD surface/junction
  measurements, diagram and exact exported STEP. The original study is archived
  unchanged, including its force/strain estimates and limitations.
- `clip-meshing/`: original higher-order Gmsh clip-meshing script, STEP and report.
  Initially 20 elements had nonpositive signed quality; high-order optimization
  removed those, but the minimum remaining quality was only 0.04075. No structural
  clip solve was performed in that specific experiment. `issue-report.md` retains
  the historical external-solver proposal; current app research prefers Rust.
- `slicer-challenge/`: original pre-thinning slicer challenge scripts, resolved
  settings, case/results/metric reports and actual toolpath comparison images.
  Its older geometry and findings must not be confused with the newer committed
  `../local-corner-flex/` study. No physical printer job was started by either.
- `section-qa/`: actual native section queries and SVGs, plus Bevy main-CAD cutaway,
  reverse cutaway, inspector diagram and drawing screenshots from the app review.
- `fresh-contact-compliance/`: new four single-patch load cases on the same
  geometry, investigating coupling that the original all-corners-at-once load
  could not separate. Read that study's own methods and limits before using it.
- [Fresh mechanics review](../analysis/DETENT-MECHANICS-FRESH-PASS.md): dimensions,
  contact/load assumptions, material version change, theoretical sensitivities,
  tolerance/relaxation challenge and recommendations before geometry changes.

Every original bundle has `archive-manifest.json`, recording source directory,
exact-byte SHA-256 and sizes. Original reports are not rewritten to hide an old
assumption or replace their numbers with new conclusions. The fresh review
explains which interpretations were corrected.

## Reproduction and retained external artifacts

The archival scripts preserve their original local paths and environment
assumptions; they are **not portable application features**. `fem.py` uses
Gmsh/NumPy/SciPy in the original isolated `python-libs` environment and the copied
`current.step`; optional field plotting uses Matplotlib and regenerated `.npz`
fields. Run from a disposable copy or explicit new output directory. Its first
argument selects the local mesh target, e.g. `0.2`. Do not silently replace its
historical material or boundary conditions when reproducing.

`clip_mesh.py` originally obtained STEP using the headless CAD MCP client prefix
from `D:/noBS-CAD-builds/bevy-section-review-20261006/qa_driver.py`. The exact STEP
is retained, so the meshing portion can be repeated without re-exporting current
CAD. Imported Gmsh tags are not persistent OCCT face IDs. `build-tests.py` and
the slicer analyses use the original 3MF template, exported STLs, Bambu Studio CLI
and configured local paths. Those dependencies are recorded in the scripts and
`cases.json`; copied reports alone do not promise one-command reproduction.

`external-artifact-inventory.json` binds the large regenerable mesh/field/sliced
3MF/G-code inputs/outputs still retained locally by path, byte count and hash.
Third-party environments, solver binaries, package archives and parsed-path caches
are not added to Git. The research code, numerical reports, relevant exact STEP
inputs, analysis and images are versioned; this archive does not claim every
historical local binary is tracked.

## Interpretation corrections

The 0.8976 mm minimum in-plane wall and 1.0 mm Y backing measure different axes.
The requested flex is in Y, perpendicular to the broad face. Closed walls and
backing form a coupled frame/plate, not four independent free cantilevers.

The historical FEM applies 1 N to **all four** nub patches simultaneously. Its
inverse deflection values are effective simultaneous-load responses, not diagonal
single-nub stiffnesses. It scales this equal-force pattern to an average nominal
travel; it does not impose that travel independently at each nub. The 0.0273 mm
value is a historical geometric travel estimate, not measured installed preload
or verified peak insertion travel. Small CAD overlap volume is not a force result.

The historical material sheet was Bambu PETG Basic V2.0. The current manufacturer
V3.0 describes an upgraded formulation with different stiffness and specimen
conditions. Neither sheet alone establishes the properties of the user's spool,
the sliced wall arrangement, repeated-snap allowable strain or long-term creep.
