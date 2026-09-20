# INJS2065 Technic Clamshell Case

Private design pack for Injora **INJS2065** Technic clamshell (noBS-CAD).

**Current revision: v16.36** — fix hub entry chamfer select for Ø7.94 (r=3.97); drop brittle clip entry chamfers for blank-doc replay; journal Ø7.94 / face Ø8.15 / Technic 8.0 kept. See `design/`.

| Path | What |
|------|------|
| `design/` | Versioned `.nbcad.jsonc` SoT, `.nbcad` exports, meta, validators, README |
| `skills/` | Cad Bot workflow checklists used on this part |
| `FIT_DECISION.md` | Face setback / pin clearance decision notes |
| `SESSION_HANDOVER.md` | Handover for agents / next session |
| `AGENTIC.md` | JSONC / MCP iteration process |

## Workflow
- Edit under `design/` only.
- Versions = **git commits / PRs**, not `v16.N` folders.
- **SoT:** `design/design_v16_36.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
