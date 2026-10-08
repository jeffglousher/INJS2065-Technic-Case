# Complete PETG print set

Open [assembly-petg.3mf](assembly-petg.3mf) in Bambu Studio. One plate contains lower shell (body 8), upper shell (18), both actual mirrored clips (173 and 267), and output hub (54). Servo and bearing are purchased reference hardware. Geometry is unchanged from canonical design commit 5c66688; only print orientation, placement and hub-specific support settings were prepared.

Bambu Studio 2.8.2.61: X2D 0.4 mm nozzle, Bambu PETG Basic, 0.12 mm main layers, 0.20 mm first layer, Classic walls, four requested walls and 25% gyroid. Both clips have outside broad faces down; the shells keep the reviewed outside-face-down orientations. The hub has its Z42 output face down, with tree supports restricted to the build plate and a requested 5 mm outer brim. Supports are disabled on the other four objects. Requested wall count does not imply four loops fit everywhere.

Native slicing returned success (CLI exit 0 and native return code 0), all five expected names/triangle counts/heights matched, and no plate warning was reported. Native G-code contains extrusion for five objects. Support and interface extrusion is confined to the hub region. Estimated total time: 8667 seconds (2 h 24 min); material: 22.97 g. This is a controlled fit-test candidate; mechanical strength, insertion, retention, preload and creep remain unqualified. No printer job was sent.

[Native first-layer layout](plate-layout.png), [project/source geometry evidence](assembly-project.json), [native slicing evidence](native-slice.json), [toolpath audit](toolpath-audit.json).

The saved 3MF is editable and unsliced. G-code and native temporary outputs remain at `D:/noBS-CAD-Reviews/INJS2065-Technic-Case/assembly-print-20261008/slice`; its SHA-256 is recorded in native-slice.json. Saved scripts preserve the local export, preparation and validation procedure. The existing three reviewed mesh entries were reused with globally unique production-extension object IDs. The additional mirrored clip and hub were exported from the unchanged canonical native source. Native object counts, names, triangle counts and bounds were checked after import to guard against mesh aliasing across 3MF object resources.

An initial package with duplicate cross-file object IDs was rejected after native import aliased its mesh resources. The IDs were made globally unique and all intended meshes were verified. Bambu CLI sliced the corrected project, but its optional --export-3mf operation reported an export failure; the final native check omits that optional operation and succeeds. Neither rejected output is the reviewed file.

## Hub axle socket

The existing cross-shaped axle socket spans 4.85 mm with 1.85 mm arms and is 8.0 mm deep. Its closed end is world Z34, separated from the servo-side recess floor at Z30.2 by a 3.8 mm web. It is not a through-hole. [Native OCCT socket and axial sections](hub-socket-sections.png) and [toolpath interior sample audit](hub-socket-audit.json) document this. Lines spanning the cross at its closed end make the socket floor; the central socket interior before that floor contains no extrusion in the sampled audit. No hub geometry change was made.
