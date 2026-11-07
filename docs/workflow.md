# Limo CAD to a PETG print

For the active latch experiment, use the separate
[retention trial workflow](retention-trial.md). Its editable source, coupon
plates, full A housing and validation record are linked there. The files below
remain the control design.

## Files to open

Open [current.nbcad](../design/current.nbcad) in Limo CAD for the editable design.
Its matching [model JSON](../design/current.model.json) contains 374 features and
seven bodies. The saved views include **Assembled ISO**, **Exploded assembly**
and **PETG print by object**.

Open [servo-holder.3mf](../print/servo-holder.3mf) in Bambu Studio for all five
printable parts. The native model owns editable geometry; the 3MF owns the
saved printer, filament, placement and process settings. A new CAD export does
not automatically inherit Bambu settings.

## Print settings and checks

The project uses Bambu X2D, a 0.4 mm nozzle and Bambu PETG Basic, printing by
object. It uses Arachne for the shells and Classic for the clips and hub.
Shell detail bands request 0.12 mm layers, with a 0.16 mm main layer height and
0.20 mm first layer. The hub uses 0.08 mm layers. Shell speed limits apply to
each whole shell. There are no modifier volumes, supports, support paint,
brims or skirts. Both clips slice solid.

The native estimate is about 3 h 25 min and 22.49 g. It is not a printer runtime
guarantee. Live printer and AMS configuration were not synchronized, and no
printer job was sent. Read [assembly and acceptance](assembly.md) before use.

[validation.json](validation.json) records the project/model hashes, mesh checks,
native slice and toolpath checks. These commands run without a printer connection:

```text
uv run python tools/verify-print.py
uv run python tools/slice-print.py
```

The first verifies the saved model and five prepared meshes against the recorded
hashes, process settings and receipt. The second performs a fresh native slice
in a temporary directory, checking all five objects, solid clips, shell detail
layers, end-wall continuity probes and absence of support/brim/skirt paths.
Add `--update-evidence` to refresh the receipt only after those checks pass.
Set `--slicer` to the installed Bambu Studio executable if needed.

## Gallery

The gallery renders the exact prepared print meshes, with rigid display
transforms to place them in the assembly. Servo and bearing reference meshes
are checked against [model-reference.json](model-reference.json). The turntable
rotates the whole assembly for inspection; it does not simulate servo operation,
bearing contact or snap deformation. Display offsets are not assembly clearances.

The exploded views use saved assembly translations, with the bearing and hub
lifted further in Z for visibility. The plate image renders the saved 3MF
placement and shows its matched native estimate. Colors identify parts, not
filament changes. Sources and asset hashes are in
[gallery-sources.json](gallery-sources.json).

To regenerate the hardware source and gallery:

```text
node tools/export-gallery-scene.mjs
uv run --with pillow python tools/render-readme.py
```

The exporter uses the installed Limo CAD in a separate headless process and
refuses changed hardware hashes. The renderer uses Pillow and the saved print
meshes. Its ignored `local/` input is bounded to 50 MiB. No current desktop model
is changed. CAD replay must be qualified before replacing prepared print meshes;
exact native shell mesh hashes are build-dependent and are not certified by the
gallery. The saved native model and JSON are consistent.
