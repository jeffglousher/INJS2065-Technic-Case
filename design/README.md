# INJS2065 v16.38 — Technic envelope + face/side pin revise

Jeff markup (GO): grow both X ends + Y cheeks to Technic module margins; remove face holes near hub; add +X face column; denser green side pins; CLIP leave-as-is.

| Item | v16.37 (before) | v16.38 (after) | Notes |
|------|-----------------|----------------|-------|
| shell_x | [-12, 24] | **[-16, 32]** | 48 mm = 6×8; margin past x=−8 = 8 mm; past x=+16 = 16 mm (room for x=24 column) |
| shell_y | ±12 | **±16** | 32 mm = 4×8; side-face origin ±16 |
| Face Technic | (±8,±8), (16,±8), **(0,±8)** | (±8,±8), (16,±8), **(24,±8)** | Removed bearing-adjacent; added grown +X column |
| Side Technic (green only) | x={−8,+8} @ z=30 | x={−8,0,8,16,24} @ z=30 | Yellow scribble; nothing on blue |
| Far tip wall | 3.0 mm (24−21) | **11.0 mm** (32−21) | Still ≥3 mm; ears encapsulated |
| CLIP / pocket | — | **untouched** | BuckleClip geometry unchanged |
| Hub mates | 7.94 / 8.15 / 12.3 / CROSS 8 | same | OutputHub mates unchanged |

## Replay
- **Canonical:** `design/design_v16_38.nbcad.jsonc` — edit with normal tools; blank-doc replay this path.
- Companion: `gen_meta.json` (`version` must match AGENTIC `Version: 16.38`).
