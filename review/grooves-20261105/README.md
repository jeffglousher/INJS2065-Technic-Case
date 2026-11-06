# End-groove slicer investigation

The operator reports reasonable printed fit with large grooves on the ends.
Open `assembly-uniform-shells.3mf` for the revised assembly candidate.
Canonical projects under `print/` remain the previous version.

The four regional speed modifiers split the shell end perimeters. In the
original native slice, the upper shell at Z=2.0 mm has end-wall centerline
interruptions at Y=169.59–170.01 and 179.99–180.41 mm (0.42 mm each),
on both X=30.21 and X=69.79 mm walls. These align with the modifier
boundaries at local Y=±5.2 mm. Removing those volumes restores continuous
end-wall paths at those locations. Centerline gaps are toolpath evidence,
not a measurement of the printed groove width.

The candidate applies the same slow speed overrides to the whole shells.
It preserves all five printable mesh payloads byte for byte, print placements,
shell layer bands, Arachne, material, and clip/hub object settings. Both
projects slice successfully in installed Bambu Studio. Original: 12,552 s,
23.69 g. Candidate: 12,312 s, 22.49 g. No support, brim or skirt extrusions.
Clip/hub extrusion positions, widths and amounts match; Clip +Y has a small
automatic gap-fill speed difference (example: 62.05 vs 62.117 mm/s).

Run `tools/compare-uniform-shells.py` to recreate the candidate. Native CLI
results are retained beside this report. The local G-code and diagnostic logs
are excluded from Git and retained for review (about 27 MB total output,
owner: this servo-holder task; budget: 50 MB; release after printed review).

The toolpath defect is reproduced and removed in the candidate. A repeat print
is still needed to confirm the resulting surface finish. No print was started.
