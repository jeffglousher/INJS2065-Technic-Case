# Working on the INJS2065 holder

Use `design/current.model.json` and its matching `design/current.limo`. Preserve
construction features, identifiers, dimensions, assembly poses and named views
when changing documentation or file organization.

The print project is `print/servo-holder.3mf`. Current references are
`docs/validation.json`, `docs/model-reference.json`, `docs/dimensions.json` and
`docs/gallery-sources.json`. Use `uv run python tools/verify-print.py` for saved artifact
checks and `uv run python tools/slice-print.py` for a fresh native slice. Update evidence
only after checks pass; do not change reference hashes to conceal a failure.

Keep the README concise, with assembly instructions in `docs/assembly.md` and
technical workflow in `docs/workflow.md`. Gallery geometry comes from the prepared
print meshes, with hash-verified reference hardware. Qualify a CAD replay before
replacing those meshes. Printability does not establish force, strain or lifetime.
Do not start a printer job without an instruction to print.

Keep temporary work under ignored `local/` or a system temporary directory.
Preserve unrelated files and active runtimes. Publish changes through PRs to
`main`, preserving shared Git history.
