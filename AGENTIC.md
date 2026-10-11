# Working on the INJS2065 design

Use `design/current.model.json` and its matching saved native project `design/current.nbcad`. Keep construction features, IDs, profiles, dimensions, assembly poses and named views intact during geometry-preserving cleanup. Do not flatten the editable feature tree to eliminate process archives.

The current print outputs are `print/assembly-petg.3mf` and `print/fit-test-petg.3mf`; the latter has both complete shells and both clips. Use `DESIGN.md`, `REFERENCES.md` and `review/current` for current evidence and remaining qualification limits. Keep useful findings consolidated here instead of retaining dated experiment trees or duplicate output files. Put disposable experiments and build caches outside the repository.

After an authorized CAD edit, export `cad_project_model` and save the native project together. For replay use `cad_load_project_model` with the canonical JSON. Run `node tools/verify-current.mjs`: all 374 current features must replay without errors, and seven meshes/topologies plus assembly contacts must match the current reference. This candidate-generated reference checks regression, not independently approved mechanics. Intentional changes require a newly reviewed reference; do not update an audit merely to hide a failure.

There is no qualified elastic preload, holding force or insertion/holding strain result for the current geometry. Use the physical checks in `DESIGN.md` before accepting retention. Do not start a printer job without an instruction to print.

The locally user-modified `review/hub-orientation-20261010/flipped-no-support.3mf` must remain byte-identical during our cleanup and must not be included in our cleanup commit. Preserve other agents' worktrees, unknown files, installed runtimes and reused build caches. A directory's old task name alone does not establish current ownership. Publish reviewed design changes through PRs to `main`; do not rewrite shared remote history as a disk cleanup shortcut.
