# INJS2065 v16.35 — tighter journal + face hole (adapter force constraint)

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Assembly remains **one-direction into upper_cover** (v16.25). Journal **Ø7.94** into BRG_ID 8.0. Friction open-C clips (no snaps).

## Why this revision

Jeff: business adapter fit very loose — tighten to constrain forces (PETG 0.4/0.2 FDM).

### Fit table (before → after)

| Interface | Before | After | Notes |
|-----------|--------|-------|-------|
| JOURNAL | **7.90** | **7.94** | slight running clearance vs BRG_ID |
| BRG_ID | 8.00 | 8.00 | unchanged |
| Journal diametral clr | 0.10 | **0.06** | radial 0.05 → **0.03** |
| FACE_HOLE_D / retain lip / `cb_jnl` | **8.50** | **8.15** | still clears poke-out; no journal interference |
| Face vs journal diametral | 0.60 | **0.21** | constrains radial force at face |
| BRG_POCKET | 12.3 | 12.3 | leave (bearing OD seat) |
| BRG_OD | 12.0 | 12.0 | leave |
| CROSS_DEPTH / pin depths | 8.0 | 8.0 | Technic module |
| Lead-in rings | Ø6.2×0.9 | Ø6.2×0.9 | local feature inside 8.0 bore |
| Tip rings | Ø6.2×1.2 | Ø6.2×1.2 | local feature inside 8.0 bore |
| Strength dome | into solid (+Z) | unchanged | |

### Technic depth policy

Technic **module depths are 8.0**. Lead-in rings **Ø6.2×0.9** and tip rings **Ø6.2×1.2** are intentional **local features inside the 8.0 bore** — not separate Technic depths.

Carried from v16.34: shared CLIP↔POCKET refs; side face `$select` with normal+origin Y=±12; dome apex into solid.

## Assembly (mandatory)

1. Bearing into **upper_cover** alone (from split → face).
2. OutputHub into that stack (flange → constant OD column → journal through bearing → Technic cross).
3. Servo into hub spline.
4. Lower clam over servo.
5. Open-C clips last.

## Source of truth (JSONC)

- **Canonical:** `design/design_v16_35.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.35`).
- **Deprecated:** `gen_v*.py` — deleted; do not recreate as SoT.
- Live CAD MCP: Thunder `machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d` — parent live-replays after pull.
