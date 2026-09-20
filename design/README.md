# INJS2065 v16.34 — uniform Technic 8.0 module + shared CLIP↔POCKET

Envelope remains **24 × 24 × 34 mm** face at Z42 (shell ±12 XY, split_z 18.25, shell_z0 8). Assembly remains **one-direction into upper_cover** (v16.25). Journal **Ø7.90** into BRG_ID 8.0. Friction open-C clips (no snaps).

## Why this revision

### A) Uniform Technic depths → 8.0 mm module
VERIFY: Technic pitch **8.0**, beam ~7.8, pin hole ID ~4.8–5.05 FDM. We standardize **depths on the 8.0 module**:

| Param | v16.33 | v16.34 |
|-------|--------|--------|
| `side_blind_depth` / all `cb_side_*` | 8.2 | **8.0** |
| `technic_top_depth` / all `cb_top*` | 8.2 | **8.0** |
| Hub `CROSS_DEPTH` | 10.0 (non-uniform) | **8.0** |
| Cross slot bottom local z | 5.7 | **7.7** |
| Strength dome apex | into solid (+Z) | unchanged |

### B) Missing center bore on one side hole
Root cause: after `cb_side_1_1_0`, face `$select` with only `/plane/normal/1: 1` + `take: first` could bind the **blind floor** of the first hole (also +Y normal) instead of the outer shell — second hole never opens on the outer face.

Fix: reselect each side face with **`/plane/normal/1` ±1 AND `/plane/origin/1` ±12** (named outer shell). Same diameter/depth/style on both ±X holes on +Y and both on −Y. Top faces similarly gated with `/plane/origin/2: 42`.

### C) Clip pocket from shared CLIP envelope
Clip was correct (`CLIP_Z0/Z1 = 12.45/24.05`); pocket used independent `chan_z` / `B_pocket_z` → **26.5**, leaving an empty recess above the clip in green.

Shared refs (JSONC section comments + `gen_meta.buckle.shared_clip_envelope`):

```
CLIP_Z0 = 12.45; CLIP_Z1 = 24.05   // = frame_z / c_outer_yz / clip_z_bounds
CLIP_X0 = -3.75; CLIP_X1 =  3.75   // = clip_x_bounds
POCKET_Z_CLR = 0.45; POCKET_X_PRESS = 0.04
POCKET_Z = CLIP_Z ± POCKET_Z_CLR = [12.00, 24.50]
POCKET_X = CLIP_X ∓ POCKET_X_PRESS = [-3.71, 3.71]
A_pocket_z = [POCKET_Z0, 18.3]; B_pocket_z = [18.2, POCKET_Z1]
```

No orphan cavity above/below the clip. Mating pocket cites CLIP ± named clearances only.

## Depth audit (v16.34)

| Feature | Depth (mm) | Notes |
|---------|------------|-------|
| Side Technic (`cb_side_*`) | **8.0** | module; dia 5.05 |
| Top Technic (`cb_top*`) | **8.0** | module; dia 5.05 |
| Hub axle cross | **8.0** | slot z0 local 7.7; dome into solid |
| VERIFY pin ID | ~4.8–5.05 | FDM |
| VERIFY pitch / beam | 8.0 / ~7.8 | Lego Technic |

## Assembly (mandatory)

1. Bearing into **upper_cover** alone (from split → face).
2. OutputHub into that stack (flange → constant OD column → journal through bearing → Technic cross).
3. Servo into hub spline.
4. Lower clam over servo.
5. Open-C clips last.

## Source of truth (JSONC)

- **Canonical:** `design/design_v16_34.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.34`).
- **Deprecated:** `gen_v*.py` — deleted; do not recreate as SoT.
- Live CAD MCP: Thunder `machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d` — parent live-replays after pull.
