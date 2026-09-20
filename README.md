# INJS2065 Technic Clamshell Case

Private design pack for Injora **INJS2065** Technic clamshell (noBS-CAD).

**Current revision: v16.33** — deeper Technic CROSS_DEPTH 10.0 + strength dome apex into solid (+Z); flange Ø12.0×2.8 + clip visual mass on **split_z**. See `design/`.

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
- **SoT:** `design/design_v16_33.nbcad.jsonc` — edit JSONC directly; replay that file on a blank document. Companion meta: `design/gen_meta.json`. No `gen_v*.py`.
