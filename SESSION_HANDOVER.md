# Session handover — resume at v16.29 (2026-09-20)

## Current
- Source of truth: `design/` at **v16.29** (`gen_v16_29.py` + JSONC + `gen_meta.json`).
- Branch: `cad-bot/v16.23-current`.
- Fix: clip centered **vertically (Z)** in clamshell slot (not X). Wider CLIP_XW=7.40, shorter span Z=11.60, X press 0.08 total.

## Pending
1. Live CAD reload + viewport shots on Thunder (`machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Physical PETG fit of wider/shorter clip press.

## Next
Pull branch on Thunder → replay `design/injs2065-technic-clamshell.nbcad.jsonc` → screenshot clip vs pocket Z.
