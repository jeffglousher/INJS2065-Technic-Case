# Session handover — resume at v16.23 (2026-09-20)

## Current
- Source of truth: `design/` (= Codex `...\v16.23` on Thunder).
- Repo branch for this park: `cad-bot/v16.23-current`.
- Jeff is **printing this copy**; do not claim print release until physical results land.

## Pending (do not paper over)
1. Physical pin grip / retention
2. Hub local neck strength (~1.125 mm) — CAD does not prove fatigue
3. Bearing axial retention (front install, no separate cap)
4. Unobstructed **live** visual review of final bearing-access geometry (blocked once by Windows Security / tests.test)
5. Clip friction lands vs IFC overlaps — confirm with print; do not invent new snaps without Jeff

## Why Python / validators existed
Agents forked `gen_v16_N.py` and mesh `.cjs` probes because MCP one-step is slow for this model and wall/bore tools were missing. Stop adding version folders; change `design/gen_v16_23.py` (or rename later) and commit.

## MCP / tooling gaps (product)
- Wall thickness / section sweep as first-class inspect
- Bore / pin-corridor completeness checks
- Viewport PNG export from MCP
- Long script replay reliability
- True solid sections

## Next edit session
Resume in `design/`; open PR for changes; delete no new `v16.24` directories on disk.
