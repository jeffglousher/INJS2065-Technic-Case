# Agentic CAD process (INJS2065)

## Source of truth
- Current design tip: use the version recorded in `design/gen_meta.json` and the single live `design/gen_v16_*.py` generator; do not hard-code a version here.
- Prefer editing `design/injs2065-technic-clamshell.nbcad.jsonc` for non-trivial changes, then replay on a **blank** document (`cad_interface` action `script`, `mode: fast`).
- Open the latest `.nbcad` export (after live save) for live inspection / tiny MCP tweaks.
- Do **not** create new `v16.N` folders — commit on git branches instead.

## Versioning
Version: 16.31
- Keep one authoritative `VERSION = "M.N"` (or `DESIGN_VERSION = "M.N"`) at the top of the current Python generator; for example, `VERSION = "16.31"`.
- Keep a matching one-line `Version: M.N` block in this document for the active generator; update it with the generator, metadata, and JSONC when a new version is cut, and do not guess a concrete version before then.
- The generator filename must match it: `design/gen_v{VERSION with dots→underscores}.py` (for example, `design/gen_v16_31.py`).
- The same VERSION string must appear in the generator, `design/gen_meta.json` in the `version` field, and a header comment or metadata entry in `design/injs2065-technic-clamshell.nbcad.jsonc`.
- Keep only the current `design/gen_v16_*.py` in the working tree. When cutting a new version, write the new generator, regenerate the JSONC and metadata, then delete prior `gen_v16_*.py` files. Git history retains old scripts; do not accumulate them on disk.
- The stable source-of-truth path remains `design/injs2065-technic-clamshell.nbcad.jsonc` (unversioned); the version lives inside that file and in the generator filename.
- Optional versioned 3MF/`.nbcad` exports may include VERSION in their names when Jeff asks for an export.
- This is policy documentation only: do not invent a new design version or prune generators until that version is ready.

## MCP vs JSONC
- Non-trivial: edit JSONC → blank-doc script replay.
- Tiny live tweak: MCP one-step, then sync JSONC ASAP (hand-patch until bi-di export ships in the CAD build you run).
- `cad_script` today = forward MCP call dump only — not a JSONC exporter.
- WIP product branch (source): `jackControls/noBS-CAD` `feat/jsonc-roundtrip-and-script-collections` (includes + `export_script`). **Not** in the installed 0.2.0 release yet — rebuild/restart CAD+MCP from that branch to use it.

## Design feedback loop
1. Jeff reports print / body / clip results (photos OK).
2. Agent attaches live session or opens `design/*.nbcad`.
3. Fix via JSONC (preferred) or tiny MCP + sync.
4. Validate (IFC / wall notes / live shots per skills).
5. Export 3MF when Jeff asks; do not start prints unasked.

## Pending product (does not block design)
- Faithful model.json → JSONC export
- Collections for part isolation in the INJS script
- CAD/MCP rebuild from feature branch
