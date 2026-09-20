# INJS2065 Technic Clamshell Case

Private design pack for Injora **INJS2065** Technic clamshell (noBS-CAD).

**Current revision: v16.29** — one-direction assembly into **upper_cover** (ClamshellB). See `design/` (v16.29: clip Z-centered in clamshell slot; wider+shorter open-C).

| Path | What |
|------|------|
| `design/` | Current gen script, `.nbcad` / `.nbcad.jsonc`, meta, validators, README |
| `skills/` | Cad Bot workflow checklists used on this part |
| `FIT_DECISION.md` | Face setback / pin clearance decision notes |
| `SESSION_HANDOVER.md` | Handover for agents / next session |
| `AGENTIC.md` | JSONC / MCP iteration process |

## Workflow
- Edit under `design/` only.
- Versions = **git commits / PRs**, not `v16.N` folders.
- Generator `design/gen_v16_29.py` → `injs2065-technic-clamshell.nbcad.jsonc` + `gen_meta.json` (JSONC is SoT for replay).
