# INJS2065 Technic case

The current editable design is [current.nbcad](design/current.nbcad), with its matching [native model](design/current.model.json): 374 features and seven bodies. The CAD construction remains editable.

Use [assembly-petg.3mf](print/assembly-petg.3mf) for all five printed parts, or [fit-test-petg.3mf](print/fit-test-petg.3mf) for both complete clamshells and both clips. Both projects use Bambu X2D, 0.4 mm nozzle, Bambu PETG Basic and printing by object. Both projects have no supports, support paint, brims or skirts. Fresh native slices estimate 2 h 21 min / 22.77 g for the assembly and 1 h 46 min / 21.54 g for the fit test. No print job was sent.

This is a fit-test candidate. Elastic preload, holding force and insertion/holding strain remain unqualified. See [design specification and remaining checks](DESIGN.md) and [sources and reuse guidance](REFERENCES.md).

The resumed review passes CAD replay, export preflight, mesh/settings checks and a fresh assembly GUI slice. Recommendation: run the complete-shell fit test before mechanical acceptance. Bambu Studio is open on the assembly preview; no print was sent. [The current report](DESIGN.md#current-review-and-print-decision) includes the decision, cavity/rear/section views and slicer evidence.

The [contact-path follow-up](DESIGN.md#contact-path-follow-up) now checks 20 exact rigid poses on both sides: the installed seat has substantially less nominal overlap than the withdrawal obstruction. Whole-clip inward motion is blocked by supporting geometry, so strain analysis must model local corner flex. The current version has not yet been physically tested.

![Current assembled and exploded printable parts](review/current/assembly.png)

![Current clip and detent corner](review/current/clip-and-corner.png)

Run `node tools/verify-current.mjs` to replay and check the seven current meshes, topologies and assembly contacts against [the current reference](review/current/cad-reference.json). This regression check establishes repeatability, not mechanical qualification. Current section data, mesh checks, toolpath checks, file hashes and native slicing receipts are in [review/current](review/current).

Run `python tools/verify-print.py` to check saved project hashes, native-model consistency, mesh closure/winding, absence of supports/brims/skirts, object overrides and matching slice receipts without a printer connection. To regenerate the current mesh renders, use `python tools/render-review.py --scene scene.json` with an actual `solid_scene` response from the canonical model; the renderer requires Pillow. Inspect all generated views before presenting them.

The locally user-modified `review/hub-orientation-20261010/flipped-no-support.3mf` is preserved at its original path. It is separate from the current print projects above.
