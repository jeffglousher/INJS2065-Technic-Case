# Limo CAD to a reviewed PETG print

## Files and views

Open [current.nbcad](../design/current.nbcad) in Limo CAD for the editable design.
Its matching [model JSON](../design/current.model.json) contains 374 features and
seven bodies. The model saves **Assembled ISO**, **Exploded assembly** and
**PETG print by object** views. View offsets separate the parts for inspection;
they are not assembly clearances or a constrained disassembly motion.

Open [assembly-uniform-shells.3mf](../review/grooves-20261105/assembly-uniform-shells.3mf)
in Bambu Studio for the current five-part print candidate. The `.nbcad` owns
editable geometry. The 3MF owns saved printer, filament, placement and process
settings. A new CAD export does not automatically inherit those Bambu overrides.

The older `print/assembly-petg.3mf` and `print/fit-test-petg.3mf` contain the
superseded regional modifiers. The separately preserved
`review/hub-orientation-20261010/flipped-no-support.3mf` is an owner experiment,
not the current candidate.

## What changed after the first print

The owner reported reasonable fit but large grooves at the ends. Native slicing
reproduced end-wall path interruptions at the four regional speed modifiers.
The revised project removes those volumes and applies their speed limits to
the entire shells. All five printable mesh payloads, print placements and shell
layer bands remain unchanged; clip/hub settings remain intact.

The current project uses Arachne for the shells and Classic for clips/hub. Shell
detail bands request 0.12 mm layers, with a 0.16 mm baseline and 0.20 mm first
layer. There are no supports, support paint, brims or skirts. Both clips slice
solid. The native estimate is about 3 h 25 min and 22.49 g; it is not a printer
runtime guarantee. Live printer and AMS configuration were not synchronized.
No printer job was sent.

See [the groove investigation](../review/grooves-20261105/README.md) and
[the latest all-parts review](../review/readiness-20261106/README.md) for exact
project hashes, native results and remaining physical acceptance checks.

## Gallery provenance

The front README follows the presentation of the
[garden-auger project](https://github.com/jeffglousher/garden-auger-technic):
an animated overview, labeled exploded assembly, interior details, print plate
and direct files to open. These are rendered meshes, not application screenshots.
The turntable rotates the whole assembly for inspection; it does not simulate
the servo, bearing contact or snap deformation.

The five printable gallery meshes come directly from the reviewed 3MF and are
checked against its mesh hashes. Rigid transforms undo manufacturing orientation
and centering for the assembled views. Servo and bearing reference meshes come
from an isolated native replay and match their recorded reference hashes. The
newer installed CAD build produces different shell tessellation hashes on replay,
so those rebuilt printable meshes are deliberately excluded from the gallery.
This does not qualify that newer replay as geometrically identical to the saved
print. No editable model, print-project geometry or current desktop was changed.

Explosion translations start with the model's saved **Exploded assembly** view.
The bearing and hub are lifted further in Z for visibility. The published plate
image is generated from the current saved 3MF placement and its matched native
slice receipt, rather than from the old modifier project's screenshot.

Asset hashes and sources are in [gallery-sources.json](gallery-sources.json).
To regenerate the native hardware source and gallery, run from the repository root:

```text
node tools/export-gallery-scene.mjs
uv run --with pillow python tools/render-readme.py
```

The first command runs the installed `Limo-CAD.exe` in a separate headless
process and refuses changed hardware hashes. The second needs Pillow and the
current candidate and readiness receipt. Temporary `local/readme-gallery-scene.json`
belongs to this documentation task, has a 50 MiB ceiling and is excluded from Git;
retain it while gallery work is active, then release it after merge and no consumers.

## Existing validation tools

`tools/verify-print.py` checks the historical projects under `print/`, including
their four regional modifiers. Its success does not approve the revised slice.
`tools/review-readiness.py` audits and renders the revised candidate, using the
locally retained original G-code for the end-wall comparison. Native output is
ignored; clone-only reproduction needs that original comparison slice first.

`tools/verify-current.mjs` replays the CAD and requires the original exact native
mesh/topology hashes. The current installed build does not satisfy its shell mesh
hashes. That is a replay qualification issue, not permission to overwrite the
reviewed model or print geometry to make the check pass. The saved native model
and JSON still match, and all five prepared print meshes retain their reviewed
hashes. Physical snap force, creep, fatigue and loaded retention remain unqualified.
