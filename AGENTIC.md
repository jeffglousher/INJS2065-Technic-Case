# Agentic CAD process (INJS2065)

## Source of truth
- Current design: `design/` (v16.23).
- Prefer editing `design/injs2065-technic-clamshell.nbcad.jsonc` for non-trivial changes, then replay on a **blank** document (`cad_interface` action `script`, `mode: fast`).
- Open `design/INJS2065-v16.23.nbcad` for live inspection / tiny MCP tweaks.
- Do **not** create new `v16.N` folders — commit on git branches instead.

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
