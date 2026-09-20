# INJS2065 Technic Clamshell Case

Private design pack for Injora **INJS2065** Technic clamshell (noBS-CAD).

**Current revision: v16.37** — encapsulate both servo locating tabs (shell +X → 24); denser face Technic 8-hole 8 mm grid; journal Ø7.94 / face Ø8.15 / Technic 8.0 kept. See `design/`.

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
- **SoT:** `design/design_v16_37.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
