# INJS2065 v16.37 — far-tab encapsulate + denser face Technic

Grows shell **+X** so both servo locating tabs are fully pocketed; adds mid-face and +X-growth Technic pins on an 8 mm pitch. Carries v16.35/36 fits.

Envelope **36 × 24 × 34 mm** face at Z42 (shell X [-12,24], Y ±12, split_z 18.25, shell_z0 8). Assembly remains **one-direction into upper_cover**. Journal **Ø7.94** into BRG_ID 8.0. Friction open-C clips (no snaps).

## Why this revision

Jeff approved: fully encapsulate **both** servo tabs (far ear was open); more Technic connection points on the business face for strong brick attachment.

### Depth / envelope table

| Item | v16.36 (before) | v16.37 (after) | Notes |
|------|-----------------|----------------|-------|
| shell_x | [-12, **12**] | [-12, **24**] | Minimal +X growth that closes far tip |
| shell_y | ±12 | ±12 | Unchanged (Jeff: wouldn’t get much larger) |
| far_end_open | **true** | **false** | Closing wall past nest tip |
| near_ear_trapped | true | true | Unchanged |
| ear_near / nest_near | [-9.2,-5.8] / [-9.6,-5.55] | same | TIP_WALL+ROOT_PAD refs |
| ear_far / nest_far | [17.2,20.6] / *(none)* | [17.2,20.6] / **[16.95,21.0]** | New far nest both A/B |
| Outer wall past far nest | n/a (open) | **3.0 mm** (24−21) | ≥2–2.4 PETG target |
| cav_x | [-6.0, 12.5] | [-6.0, **17.4**] | Clear body to 17.2 |
| Face Technic count | **4** corners (±8,±8) | **8** | + (16,±8) + (0,±8) |
| Technic depth / pin Ø | 8.0 / 5.05 | 8.0 / 5.05 | Module + FDM class |
| JOURNAL / FACE_HOLE / BRG | 7.94 / 8.15 / 12.3 | same | OutputHub mates kept |
| CROSS_DEPTH / dome | 8.0 / into solid | same | |

### Shared named refs (not magic dupes)

- **Ear nest:** `TIP_WALL=0.4`, `TAB_CLR=0.15`, `ROOT_PAD=0.25`, `NEST_Y=6.65`, `EAR_NEAR/FAR`, `NEST_NEAR_X/FAR_X`
- **Face Technic:** `PITCH=8.0`, `PIN_D=5.05`, `DEPTH=8.0`, `TECHNIC_TOP` list
- **CLIP↔POCKET** unchanged from v16.34+

### Technic depth policy

Technic **module depths are 8.0**. Lead-in rings **Ø6.2×0.9** and tip rings **Ø6.2×1.2** are intentional **local features inside the 8.0 bore**.

## Assembly (mandatory)

1. Bearing into **upper_cover** alone (from split → face).
2. OutputHub into that stack (flange → constant OD column → journal through bearing → Technic cross).
3. Servo into hub spline.
4. Lower clam over servo (both tabs into nests).
5. Open-C clips last.

## Source of truth (JSONC)

- **Canonical:** `design/design_v16_37.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.37`).
- **Deprecated:** `gen_v*.py` — deleted; do not recreate as SoT.
- Live CAD MCP: Thunder `machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d` — parent live-replays after pull.
