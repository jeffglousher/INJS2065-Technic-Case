# Session handover — v16.35

## Locked
- Journal **Ø7.94** (was 7.90); diametral clr vs BRG_ID 8.00 = **0.06** (radial 0.03).
- FACE_HOLE / outer retain lip / `cb_jnl` **Ø8.15** (was 8.50); diametral clr vs journal ≈ **0.21**.
- Kept: BRG_POCKET 12.3, BRG_OD 12.0, CROSS_DEPTH 8.0, pin depths 8.0, lead-in Ø6.2×0.9, tip Ø6.2×1.2, dome into solid.
- Technic module depths **8.0**; lead-in/tip rings are local features inside the 8.0 bore (not separate Technic depths).

## Parent live-replay
1. Pull `cad-bot/v16.23-current` on Thunder (`C:\Users\jeffg\dev\INJS2065-Technic-Case`, machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_35.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: journal OD ~7.94; face hole ~8.15; bearing pocket still 12.3; Technic bores still depth 8.0.
4. No new PRs (draft #1 ok).
