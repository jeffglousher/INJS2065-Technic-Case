# Current design and print specification

The native CAD and both print projects describe the current fit-test candidate. Dimensions below are millimetres unless stated otherwise. [dimensions.json](review/current/dimensions.json) contains the current geometric values; it deliberately leaves qualified elastic preload, force and strain unset.

## Current review and print decision

The resumed review passes CAD replay, export preflight, saved-project mesh/settings checks and a fresh assembly slice in Bambu Studio. The CAD geometry and both canonical print projects are unchanged. The supported full hex posts, 0.28 mm nubs and 0.205 mm radial aperture clearance remain the current candidate.

Recommendation: proceed with the complete-shell PETG fit test, subject to the user's final go/no-go. Final mechanical acceptance remains pending. Print [fit-test-petg.3mf](print/fit-test-petg.3mf) first (about 1 h 47 min / 21.65 g), clean the support interfaces without shaving the retaining surfaces, and check both clips for full seating, a snap, no loose sliding or wobble, and no whitening or permanent set. A loose or damaged fit fails this test; measure the printed features before making another dimensional adjustment. Then check the hub's friction fit and bearing-supported rotation as described below. PETG results do not qualify PLA.

[Export preflight](review/current/export-preflight.json) reports no timeline errors and five printable occurrences; the servo and bearing are intentionally excluded. Its layout check uses conservative mesh bounds, not exact sequential-print head collision analysis. The saved assembled, exploded and print-by-object CAD views remain present; the hub is flipped in both the CAD print view and the slicer layout.

[Saved-project verification](review/current/print-project-check.json) confirms five closed, connected, positive-volume assembly meshes with consistent edge winding, matching four-part fit-test meshes/support paint, and the object settings described below. The native CAD file's model matches the canonical JSON, and the slice receipts match the current 3MF hashes. Portable CAD export does not carry these Bambu process overrides: use the prepared print projects.

The fresh GUI slice shows all five objects, shell-only local interfaces, the flipped support-free hub, and an estimate of 2 h 23 min / 22.88 g. Bambu Studio is left open on that preview. This used the saved X2D 0.4 mm profile; live printer/AMS configuration was not synchronized. No printer job was sent.

![Current sliced assembly layout](review/current/slicer-layout.png)

## Current inspection views

These renders use the current CAD/export meshes, with a depth buffer; they do not alter geometry. Exploded offsets are for inspection and exclude the reference servo and bearing. The enlarged corner and native OCCT sections below show the critical mating details; deformation is not simulated.

![Current assembled and exploded printable parts](review/current/assembly.png)

![Current clip pocket and rear faces](review/current/clip-front-back.png)

![Current clamshell cavities and full hex posts](review/current/clamshell-inside.png)

![Current detent corner detail](review/current/clip-and-corner.png)

## Clip, detent and housing

Each clip has two rows of four blind hex pockets, full walls, flat pocket floors and four centered rounded nubs. All 16 housing hex posts retain their full 1.70 mm projection, without underside bevels. There are no detent grooves or backing indents.

The nub protrusion is 0.28 mm, with a 0.80 mm crest curve radius, 0.20 mm blend radius and 1.4664 mm meridian span. The minimum corner wall in the clip plane is 0.897584 mm; flat backing is 1.45 mm. Inner hex clearance is 0.10 mm per flat. The receiving seat has a 0.50 mm radius and 0.020 mm crest-center relief; its cap starts at absolute CAD Y = 9.809663 and ends at 10.309663.

The intended flex is inward toward the pocket, perpendicular to the clip's broad face. This is a backed, closed frame, not an isolated free cantilever. Undeformed local holding clearance movement is 0.056926 mm and the flank-crossing axial geometric envelope is 0.39933 mm. Neither is an accepted elastic deformation or an actual dynamic insertion displacement. Rigid installed geometry has four expected clip/housing overlap pairs of about 0.002292 mm³ each; overlap volume is not a force prediction.

The sampled extrusion-envelope check has 24 nominal contacting path pairs. A hypothetical 0.02 mm setback on each contacting surface loses none; 0.03 mm loses four. This is a sensitivity check, not a measured printer tolerance or proof of retention.

## Hub and rotating clearances

The servo socket matches the garden auger's trial dimensions: smooth Ø5.70 × 3.70 mm, friction fit only, with 0.15 mm entry chamfer and 3.55 mm straight engagement. It has no added tabs, center screw or separate horn. The confirmed Technic cross has 4.85 mm overall span, 1.85 mm arms and 8.00 mm depth. The separating web is 3.80 mm.

The hub journal is Ø7.94 mm and stationary housing aperture Ø8.35 mm: 0.205 mm radial clearance. The Ø8.00 mm bearing bore gives 0.030 mm nominal journal clearance. Overall housing-to-hub minimum clearance is 0.150 mm, a different measurement from aperture clearance. A checked Z = 40 section has 4.614 mm remaining material; this is not a global minimum-wall or strength result.

![Current native OCCT sections](review/current/sections.png)

## Saved print settings

Both projects use Bambu X2D, a 0.4 mm nozzle, Bambu PETG Basic and a textured plate at 70 °C. Nozzle temperatures are 245 °C initially and 250 °C thereafter. [bambu-petg-basic.json](print/bambu-petg-basic.json) preserves the resolved material settings for native command-line slicing.

The main process requests 0.16 mm layers, 0.20 mm first layer, four walls and 25% gyroid infill. The narrow clips slice solid. The output hub alone uses 0.08 mm layers, six walls, 100% infill, outer walls at 30 mm/s and inner walls at 60 mm/s. It is oriented servo rim down and Technic cross up. Its 5.70 mm roof bridges without supports, using thin bridges, bridge flow 0.90 and bridge speed 25 mm/s.

Both shells have native painted support enforcement on the downward hex flanks: 32 enforced triangles per shell, with other faces blocked. Normal manual snug supports may start on the housing; three top interface layers use 0.20 mm interface spacing. Top/bottom Z gaps are 0.20 mm and XY gap is 0.35 mm, with two bottom interface layers. Small-overhang removal and bridge suppression are disabled for the shells. Native slicing places interface paths under all 16 posts below their first sampled tip layers, with support confined to the shells and no brim or skirt. The configured support gap is not a measured printed gap; support removal can affect mating surfaces.

![Inspected Bambu Studio preview of local hex supports](review/current/print-preview.png)

Fresh Bambu Studio 02.08.02.61 slicing succeeds for both projects without a reported warning. Assembly prediction is 8556.93 seconds and 22.8841 g; the four-part complete-shell fit test is 6444.97 seconds and 21.6548 g. Native receipts are [assembly-slice.json](review/current/assembly-slice.json) and [fit-test-slice.json](review/current/fit-test-slice.json).

## Mechanical confidence and remaining checks

### Contact-path follow-up

The current 0.28 mm candidate has not yet been printed, as confirmed by the user. A new [native contact-path audit](review/current/contact-path.json) moves both clips along their opposing CAD Y directions in a disposable headless document. It samples 20 poses with exact OCCT overlap queries, then restores the installed poses and checks all seven source meshes/topologies against the current reference. The saved CAD and print projects are unchanged.

At the installed pose, total rigid overlap across the four shell/clip pairs is 0.009168 mm³. Outward movement increases it to a sampled plateau of approximately 0.323544 mm³ at 0.8, 1.2 and 1.6 mm; it falls again near exit. The 2.5 mm sample still overlaps (0.008671 mm³ total), whereas the 2.6, 2.7 and 2.8 mm samples are clear. Opposing clips agree within 0.000001 mm³ at every sampled pose. This establishes a nominal geometric obstruction on this straight withdrawal path and a comparatively relieved seat. It does not establish a continuous collision boundary, elastic energy barrier, insertion force, holding force or actual deformation distance. Small numerical differences across the plateau do not identify a meaningful unique peak position.

Moving the *whole* clips inward 0.02 mm instead produces 3.398258 mm³ total overlap; at 0.05 mm it produces 8.487109 mm³. This is consistent with substantial supporting surfaces blocking rigid inward motion. The intended deformation must therefore be local, not a whole-clip translation. These whole-solid overlaps neither prove that local flex is impossible nor quantify its available travel. A local nonlinear contact model must allow actual floor/contact release rather than prescribing inward movement to the entire clip.

Recommendation remains to print the prepared complete-shell fit test before increasing the nubs or thinning any more material. If it remains loose, inspect and measure the printed nubs and seats, including damage from support removal. If it is difficult to seat, inspect the corner motion and backing/post contact before attributing the problem to PETG stiffness. Record each clip's seating, snap, wobble, removal behavior and visible permanent set. Quantitative force/strain results remain unset; the rigid sweep does not replace them.

Reproduce this screen with `node tools/audit-contact-path.mjs`. It is specific to the reviewed canonical model hash and fails on missing contact pairs, asymmetric overlap, source-mesh changes or failure to reach a sampled clear pose.

There is no accepted structural solve for the current geometry. Overconstrained floor/contact studies do not qualify this backed-frame detent, and their force and strain predictions are not carried forward. Bambu PETG Basic V3 reports tensile coupon modulus of 2780 ± 65 MPa in XY and 2550 ± 100 MPa in Z; these are screening inputs, not printed-detent stiffness or allowable cyclic strain. Poisson ratio 0.38 is an assumption.

A useful structural solve must represent unilateral housing contact, the actual flex mode, possible pocket-floor release and the seated state. It needs mesh/contact convergence, deformed-solid penetration checks and insertion-path refinement. Quasi-static insertion is distinct from impact dynamics; creep and fatigue need separate treatment and printed calibration.

Before accepting the part, remove support cleanly and check full seating, a perceptible snap, closed seams without hand restraint, no loose sliding or wobble, and no whitening or permanent set. Check hub rotation with the bearing fitted, full servo engagement, friction-fit axial retention and torque transmission. Repeat insertion cycles and a holding dwell, then measure printed nub and seat dimensions before any further increase. No printer job has been started by this review.

The regression check replays all 374 features with no native errors and preserves seven current meshes/topologies plus expected assembly contacts. All five exported print meshes are closed, connected and positive-volume at the recorded tolerance; this is not an exhaustive self-intersection check. The native saved project's model matches the canonical JSON. These checks establish geometric consistency and sliceability, not mechanical qualification.
