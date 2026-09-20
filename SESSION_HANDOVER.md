# Session handover — v16.37

## Geometry (this cut)
- **shell_x:** [-12, 12] → **[-12, 24]** (Y stays ±12). Far tip wall: NEST_FAR_X1=21.0 → outer 24 → **3.0 mm** PETG wall.
- **Ears:** `ear_near` [-9.2,-5.8] trapped; `ear_far` [17.2,20.6] now pocketed. `far_end_open: false`, `near_ear_trapped: true`.
- **Nests (shared refs):** TIP_WALL=0.4, TAB_CLR=0.15, ROOT_PAD=0.25, NEST_Y=6.65; NEST_NEAR [-9.6,-5.55], NEST_FAR [16.95,21.0]; z_span [16.82,19.68].
- **cav_x:** [-6.0, 12.5] → **[-6.0, 17.4]** (clear body to 17.2 + pad).
- **Face Technic:** 4 corners → **8** on PITCH=8.0: (±8,±8), (16,±8), (0,±8). Blind depth 8.0; lead-in Ø6.2×0.9; tip Ø6.2×1.2. No pin at (0,0) hub.

## Fits (unchanged from v16.35/36)
- Journal **Ø7.94**; FACE_HOLE **Ø8.15**; BRG pocket **12.3**; CROSS_DEPTH **8.0**; dome into solid; CLIP↔POCKET shared; split_z **18.25**.

## Schematic (far-tab wall + face grid)
```
SHELL_X0=-12 ---- body/cav ---- NEST_FAR[16.95,21] | tip wall 3mm | SHELL_X1=24
ear_far tip 20.6 + TIP_WALL 0.4 = nest 21.0; outer wall closes far end.

Face @ Z42:  y=±8 × x={-8,0,8,16}   (8 pins; hub at origin)
```

## Parent next
1. `git pull` on Thunder `C:\Users\jeffg\dev\INJS2065-Technic-Case` branch `cad-bot/v16.23-current` (machineId `4e34e74d-0868-455b-8851-4b5e7ceff85d`).
2. Blank-doc script replay `design/design_v16_37.nbcad.jsonc` (`cad_interface` action `script`, mode `fast`).
3. Live-check: shell +X ≈24; both tab nests; far_end closed; 8 face pins depth 8.0; journal 7.94 / face 8.15 / BRG 12.3.
