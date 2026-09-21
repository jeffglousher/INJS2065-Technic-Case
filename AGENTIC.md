# Agentic CAD process (INJS2065)

## Source of truth
- **SoT = JSONC scripts** — edit `design/*.nbcad.jsonc` directly with normal edit tools. Prefer small chunked JSONC (or chaptered includes when product supports).
- Canonical tip file: `design/design_v16_41.nbcad.jsonc` (filename from VERSION). Replay that path on a **blank** document (`cad_interface` action `script`, `mode: fast`).
- MCP one-step only for tiny live tweaks, then sync JSONC ASAP.
- Open the latest `.nbcad` export (after live save) for live inspection / tiny MCP tweaks.
- Do **not** create new `v16.N` folders — commit on git branches instead.
- Do **not** use Python generators (`gen_v*.py`) as design SoT. No `gen_v*.py` stack.

## Versioning
Version: 16.41
- Working git branch: `cad-bot/v16.41-current` (tracks tip VERSION; formerly `cad-bot/v16.23-current`).
- Keep one authoritative `VERSION` / `DESIGN_VERSION` string: matching one-line `Version: M.N` in this document + embedded in the JSONC header/metadata + `design/gen_meta.json` `version` field. Do not retype divergent strings.
- Filenames from VERSION — preferred `design/design_v{M_N}.nbcad.jsonc` (e.g. `design_v16_41.nbcad.jsonc`). That versioned file is the SoT and the replay entry. Do not keep a parallel unversioned recipe name (`injs2065-technic-clamshell.nbcad.jsonc`) as SoT.
- **Prune on cut** — when cutting a new version, write new `design_vM_N.nbcad.jsonc`, update meta / this Version line, delete prior `design_v*.nbcad.jsonc` and any leftover `gen_v*.py`. Git keeps history. **No gen_v*.py stack.**
- Optional versioned 3MF/`.nbcad` exports may include VERSION in their names when Jeff asks for an export.

## MCP vs JSONC
- Non-trivial: edit versioned JSONC → blank-doc script replay of `design/design_v{M_N}.nbcad.jsonc`.
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
