I ran an isolated Windows feasibility experiment on 2026-10-06. No solver or mesher dependencies were added to the CAD application, and no source part geometry was changed.

The promising first backend is an external, bounded worker using **Gmsh 4.15.2 + CalculiX 2.23**. Gmsh imports STEP through its OpenCASCADE kernel and provides CAD entity/physical-group and volume-mesh APIs ([official manual](https://gmsh.info/doc/texinfo/)). CalculiX supplies a mature native solver and upstream Windows binaries ([official downloads](https://www.dhondt.de/)). This preserves OCCT as the geometry authority; Bevy would display results rather than implement FEM.

**Beam screening experiment:** exported an OCCT box to STEP, reimported it, tagged clamp/load faces, generated quadratic tetrahedra, mapped their midside-node ordering explicitly to C3D10, and ran the upstream `ccx_static.exe`. Units were mm, N and MPa. Beam 40 × 6 × 2 mm; synthetic isotropic E = 2000 MPa, nu = 0.35; clamped root; total 0.1 N transverse load split equally among tip nodes. This is a software benchmark, not Bambu PETG Basic characterization.

- At target mesh size 1.5 mm: 2,253 nodes / 1,029 elements; mean tip deflection 0.262295 mm.
- At 1.0 mm: 5,411 nodes / 2,836 elements; 0.262668 mm.
- At 0.7 mm: 14,042 nodes / 7,892 elements; 0.263043 mm.
- Euler–Bernoulli reference is 0.266667 mm; the finest result is 1.36% lower. Last refinement changed the mean deflection by about 0.143%. Clamp reaction Z = 0.099999984 N versus 0.1 N applied.
- Minimum signed inverse condition number stayed positive (0.296 on the finest beam). Runtime was about 0.7 / 1.3 / 3.5 seconds with one solver thread.

These results support feasibility, not complete validation. Equal loads per tip node are not a consistent uniform surface traction. Clamp effects, Poisson response, the analytical approximation and load integration must be resolved in a proper benchmark/convergence suite. Stress convergence, energy balance, nonlinear behavior and printed material response were not established.

**Actual clip meshing:** exported source body 173 through the CAD application's existing OCCT STEP exporter, imported one volume / 96 faces into Gmsh, and generated 20,344 nodes / 11,181 quadratic tetrahedra at 0.8 mm target size. Imported volume: 676.340200 mm³. The initial curved mesh had **20 nonpositive quality elements** (minimum minSICN −0.33863). Gmsh high-order optimization removed those nonpositive elements; minimum became +0.04075. Total meshing/optimization time was about 3.5 seconds. The remaining low-quality elements need refinement and quality gates. I deliberately did not solve the clip: no validated supports/contact/loading/material orientation were defined. Source model remained unchanged.

Recommended path:

1. Prototype process orchestration and STEP-to-volume meshing in a separate research harness. Bound time, threads, memory and output; support cancellation. Require positive curved-element Jacobians/quality checks and local refinement before admitting a solve.
2. Preserve a revision-bound manifest mapping OCCT bodies/faces to imported mesh regions. Imported Gmsh face tags alone are not stable CAD references. Validate units and topology/signatures after export/import.
3. Establish consistent distributed loads, constraints and an analytical/reference-solver benchmark suite, including mesh convergence, reactions and energy balance. Start with small-displacement linear elastic screening.
4. Then connect a typed result DTO to Bevy displacement/strain/stress visualization, undeformed outlines, sections and existing drawings/reports. Keep assumptions and provenance visible and invalidate results after model/input edits.
5. For snap-fit PETG/PLA, acquire print-direction coupon data and validate nonlinear contact, large deflection, creep and cyclic behavior separately. Bulk PETG stiffness cannot establish snap reliability.

Packaging/licensing needs an explicit review: upstream CalculiX advertises GPL v2, and Gmsh has its own distribution conditions. An external process boundary does not automatically settle redistribution obligations.

Reproducible local scripts, inputs, hashes, meshes, solver logs and results are retained at `D:/noBS-CAD-builds/bevy-section-review-20261006/structural-spike/` (`benchmark.py`, `clip_mesh.py`, `results.json`, `clip-mesh-results.json`). Use the isolated `venv/Scripts/python.exe`; the solver archive came directly from `https://www.dhondt.de/calculix_2.23_4win.zip`.
