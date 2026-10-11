# INJS2065 servo holder for LEGO Technic

A printable clamshell holder for the INJS2065 servo, with Technic mounting holes, two hex-pattern retaining clips and a bearing-supported output adapter. The adapter friction-fits the servo shaft and provides a Technic cross socket on the other side.

![Assembled and exploded servo holder](review/current/assembly.png)

Teal: upper and lower clamshells. Red: the two retaining clips. Light grey: the output hub. Dark grey: the reference servo and MR128 bearing, which are purchased hardware and are excluded from the print projects. The exploded image separates the parts for visibility; these display offsets are not assembly clearances.

Print five parts: both clamshells, both clips and the output hub. Seat the servo and bearing in their modeled locations, fit the hub onto the servo shaft, close the shells and slide the clips onto the side hex features. Check the fits and retention described in [DESIGN.md](DESIGN.md) before putting the holder into service.

## Files to open

The current editable design is [current.nbcad](design/current.nbcad), with its matching [native model](design/current.model.json): 374 features and seven bodies. The CAD construction remains editable.

The native project includes **Assembled ISO**, **Exploded assembly** and **PETG print by object** named views.

Use [assembly-petg.3mf](print/assembly-petg.3mf) for all five printed parts, or [fit-test-petg.3mf](print/fit-test-petg.3mf) for both complete clamshells and both clips. Both projects use Bambu X2D, 0.4 mm nozzle, Bambu PETG Basic and printing by object. Both projects have four local rail quality modifiers and 0.12 mm shell detail bands, with Arachne on shells and Classic on clips/hub. There are no supports, support paint, brims or skirts. Fresh native slices estimate 3 h 29 min / 23.69 g for the assembly and 2 h 54 min / 22.46 g for the fit test. No print job was sent.

This is a fit-test candidate. Elastic preload, holding force and insertion/holding strain remain unqualified. See [design specification and remaining checks](DESIGN.md) and [sources and reuse guidance](REFERENCES.md).

CAD replay, export preflight, mesh/settings checks and independent native slices pass. Run the complete-shell fit test before mechanical acceptance. [The current report](DESIGN.md#current-review-and-print-decision) includes the decision, cavity/rear/section views and reviewed slicer evidence.

![Current clip and detent corner](review/current/clip-and-corner.png)

## Validation and remaining checks

The [contact-path follow-up](DESIGN.md#contact-path-follow-up) checks 20 exact rigid poses on both sides: the installed seat has substantially less nominal overlap than the withdrawal obstruction. Whole-clip inward motion is blocked by supporting geometry, so strain analysis must model local corner flex. The current version has not yet been physically tested.

Run `node tools/verify-current.mjs` to replay and check the seven current meshes, topologies and assembly contacts against [the current reference](review/current/cad-reference.json). This regression check establishes repeatability, not mechanical qualification. Current section data, mesh checks, toolpath checks, file hashes and native slicing receipts are in [review/current](review/current).

Run `python tools/verify-print.py` to check saved project hashes, native-model consistency, mesh closure/winding, absence of supports/brims/skirts, object overrides and matching slice receipts without a printer connection. To regenerate the current mesh renders, use `python tools/render-review.py --scene scene.json` with an actual `solid_scene` response from the canonical model; the renderer requires Pillow. Inspect all generated views before presenting them.

Run `python tools/slice-print.py` for fresh Bambu native slices and actual rail path checks. Use `--update-evidence` to refresh matching receipts after both projects pass. It sends no printer job.

The locally user-modified `review/hub-orientation-20261010/flipped-no-support.3mf` is preserved at its original path. It is separate from the current print projects above.

[Final adversarial review](review/current/final-review.json) records the resolved findings and validation limits.
