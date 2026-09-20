# Session handover — v16.36

## Fits (unchanged from v16.35)
- Journal **Ø7.94** (diametral clr vs BRG_ID 8.00 = **0.06**).
- FACE_HOLE / retain lip / `cb_jnl` **Ø8.15** (diametral clr vs journal ≈ **0.21**).
- Technic depths **8.0**; dome into solid kept.

## Replay fix
- **Failed:** blank-doc replay ~**826/831** chamfer `$select` — `clip_yp_entry` (825) / `clip_ym_entry` (827) used brittle `/key` `edge:N`; `hub_entries` (829) still selected journal circle **r=3.95** (Ø7.90) after v16.35 tighten to Ø7.94.
- **Fix:** drop clip YP/YM entry chamfers (cosmetic 0.25); keep hub 0.2 entry chamfer with **r=3.97** @ z=42 + spline r=3.025 @ z=26.3.
- Steps **831 → 827**.

## Parent next
1. `git pull` on Thunder `C:\Users\jeffg\dev\INJS2065-Technic-Case` branch `cad-bot/v16.23-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_36.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: journal OD ~7.94; face hole ~8.15; bearing pocket 12.3; Technic bores depth 8.0; hub face entry chamfer present; clips unchamfered at mouth OK.
