---
name: MCP vs script replay
description: >-
  Use as the primary how-to for driving noBS CAD via MCP — connect/--mcp,
  attach, one-step vs script replay, blank-doc rule, inspect-between-mutates.
  Not for problem-set design (snaps, fits).
---
# MCP vs script replay (CAD program workflow)

Primary skill for **how to work with noBS CAD** via MCP. Problem-set design skills come later.

## Delivery note
Canonical teaching text should live in-repo (`docs/agentic/`, `knowledge/concepts/`) and ship as MCP resources (`nbcad://knowledge/...`) embedded at build time. This Cursor skill is a checklist mirror until that lands.

## Connect
- Packaged: point the client at the installed CAD executable with `args: ["--mcp"]` (stdio). Same release as the desktop.
- Live window work: open CAD normally, then `cad_list_sessions` → `cad_attach` to the intended document. Unattached MCP owns a separate headless doc.
- Do not invent tool names — `cad_list_all_tools` or focus packs. Disclosure is guidance, not a jail (STEERABLE_MCP).

## Decision table

| Situation | Mode |
|-----------|------|
| New geometry, unsure IDs/planes, debugging a failed feature | **MCP one-step** — one tool at a time |
| Proven pattern / bundled lesson / coupon | **Script replay** via `cad_interface` |
| Mix | Novel bits via MCP; proven chunks as script on a **blank** doc |

## Hard rules
1. Scripts need a **blank** document. Never replay `.nbcad.jsonc` / recipe over an existing model.
2. After every one-step mutate: inspect (`solid_scene` / document) before the next mutate. Trust IDs from the last successful response only.
3. Prefer `_edit_*` / definitions over delete+rebuild so history stays replayable.
4. In scripts prefer `$select` / `$project` / `$ref` over hard-coded numeric IDs.
5. Prefer `solid_export_3mf` after `solid_export_preflight` for print handoff.

## Canonical one-step order
sketch_begin → draw/constrain → sketch_finish → solid_extrude → hole/combine/fillet|chamfer → datums → inspect → export.

## Script replay
`cad_interface`: `{"action":"recipes"}` to discover; `{"action":"script","recipe"|"path"|"source":…,"mode":"fast"|"present"}` to run.

## First-part smoke (product docs)
Attach to live CAD (or headless), run `fillet-basics` in a new design, edit extrude 12→18 mm, inspect — same path as Install → Connect an MCP agent.

## Knowledge pointers (after rebuild)
- `nbcad://knowledge/index.md`
- Parametric primitives primer when present: `nbcad://knowledge/concepts/parametric-primitives.md`
- In-repo: `docs/agentic/STEERABLE_MCP.md`, `mcp-server/README.md`, `docs/native-scripts.md`
