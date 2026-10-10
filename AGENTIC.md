# Working on the INJS2065 design

## Current source

Use `design/current.model.json` as the canonical editable native feature history. `design/current.nbcad` is its native saved project. Old versioned JSONC generators and review/exploded recipes are historical and have been archived. Do not replay them as the current design.

Open the native project for CAD editing. After an authorized edit, export `cad_project_model` and save the native project together so both files represent the same history. For automated replay use the documented `cad_load_project_model` operation with the canonical JSON. Use a blank document for recipe playback.

## Scope and validation

The [current incremental revision](review/incremental-fit-20261010/README.md) removes all underside hex bevels, grows nubs to 0.28 mm and opens the stationary shaft aperture to Ø8.35 mm. Its current regression reference is candidate-generated and checks repeatability, not independently approved mechanics. The [independent adversarial review](review/adversarial-retention-20261009/README.md) and [corrected contact experiment](review/contact-fix-20261009/README.md) remain historical evidence of unqualified mechanics. Use the updated complete-shell registered project in the current revision, not older 0.26 mm or cropped tests. No replacement force/strain prediction is valid until its solve and convergence checks pass; physical retention and insertion remain to verify.

Follow Jeff's current instructions. Historical handovers describe earlier designs and must not override current direction. The 2026-10-04 cleanup was explicitly geometry preserving; future geometry changes depend on the user's requested scope.

For further cleanup, preserve feature/body/component IDs and all dimensions, profile identities and assembly poses. Only share profiles when their complete geometry, constraints, plane basis and profile identities match. Only remove operations that are provably redundant. Never simplify a solid by its feature name alone.

Run `node tools/verify-current.mjs` for the active design check. It compares the seven meshes, topology signatures and assembly contacts to `review/incremental-fit.json`, and verifies the unchanged servo, bearing and hub against `review/retention-fit.json`. All **374 features** must replay without errors. This is a fit-test candidate, not a mechanically qualified release; earlier references remain unchanged. An intentional future geometry change requires a new reviewed reference; do not silently update an existing audit.

Use the native CAD review workflow and the local skills for sections, wall measurements, export audits and inspected images. CAD equality does not establish printed snap force or fatigue life. Do not start a printer job without an instruction to print.

## Organization

One active source and one working branch: `design/current-honeycomb-detents`. Git retains committed history; the external archive retains pre-cleanup dirty work and removed local branch refs. Keep experiments outside the active source tree until reviewed. Do not publish, push or rewrite remote history as part of local cleanup.
