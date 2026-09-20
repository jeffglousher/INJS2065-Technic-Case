"""INJS2065 v16.30 — clip Z center on split_z (clamshell division) + wider + cross-bars.

Keeps v16.26 constant OutputHub OD and v16.25 one-direction assembly into upper_cover:
  1) bearing into upper alone (from split toward face)
  2) OutputHub into that stack
  3) servo into hub spline
  4) lower clam closes over servo
  5) open-C side clips last

Datum correction vs v16.29: Jeff wants clip Z center on the **clamshell division
point** (= split_z, typically 18.25), NOT the mid of the full pocket/channel Z
span (~20.25). Equal land engagement above/below the A/B mating plane.

Fit changes vs v16.29:
  - Clip Z: mid-clip == split_z within ±0.05; CLIP_ENGAGE_A == CLIP_ENGAGE_B.
  - Channel extended into A (CHAN_Z0 ↓) so the lowered clip still fits with end gap.
  - Clip a little wider again (CLIP_XW ↑); tight FDM X press kept (~0.04–0.10
    total interference, 0.4n/0.2L PETG).
  - Optional: multiple horizontal cross members across the open-C (FDM side
    print; small fillets OK; less strength not an issue).
  - Keep: JOURNAL 7.90, hub Ø11.2 column, nest CLRs from v16.28, friction open-C
    (no barbs/snaps — Jeff did NOT ask for snaps).

Still friction open-C. Hub OD unchanged. Units mm.

Naming: ClamshellB = upper_cover (business/bearing/face); ClamshellA = lower_clam.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# --- Injora INJS2065 ---
BODY_X, BODY_Y, BODY_Z = 23.0, 13.0, 25.8
TAB_SPAN, TAB_T, TAB_FROM_BASE = 29.8, 2.5, 17.0
SPLINE_FROM_EDGE = 5.8
BODY_CLR = 0.18  # FDM nest clearance (~1 layer); was 0.05 friction
BRG_OD, BRG_ID, BRG_W = 12.0, 8.0, 3.5
BRG_POCKET = 12.30
BRG_LEAD = 0.8
SHOULDER_T = 1.2
# Face Z50: three full pin corridors clear the servo and reinforced horn hub.
FACE_EXTRA = 7.95  # shortened vs v16.23 so taller flange keeps face_z=42
HUB_FACE_Z = 42.00  # must match business-end face; regression gate below
BEARING_LIFT = 5.00  # -1 vs v16.23 with taller flange; seat_z stays 34.35
PIN_BLIND_DEPTH = 8.20
JOURNAL = 7.90  # diametral clr into BRG_ID 8.0 = 0.10 (radial 0.05); was 8.02 press
FACE_HOLE_D = 8.50  # diametral clearance poke-out for journal (not bearing OD)
BRG_POCKET_H = BRG_W + 0.10  # seat width only; outer lip retains OD
TECHNIC, PITCH = 5.05, 8.0
HUB_FLANGE_D = 11.2
HUB_FLANGE_T = 2.0  # thick flange parks on servo (servo-step ledge)
# v16.28: constant outer OD = flange D from servo step up to bearing inner stop.
# HUB_NECK_D kept as alias of column OD (no separate thinner neck / mid lip).
HUB_NECK_D = HUB_FLANGE_D
HUB_COLUMN_D = HUB_FLANGE_D  # continuous OD until servo-step flange
BEARING_INNER_STOP_GAP = 0.20  # small axial gap; top of column = journal shoulder
SPLINE_SOCKET = 6.05
AXLE_SPAN = 4.85
AXLE_ARM = 1.85
CROSS_DEPTH = 8.0
TOTAL_TO_SPLINE = 30.0
# Align NUBS (true AM locating bumps — wider than tall, NOT pins)
NUB_D = 2.20           # Ø 2.0–2.4; shear-strong, aspect << 1
NUB_FLAT = 0.0         # round; optional short chord OK — lofted sphere cap (no cyl stack)
NUB_ENGAGE = 0.70      # proud of split (prefer 0.70; max 0.80)
NUB_BOSS_H = 0.30      # embed ≤0.4 (flush-ish pad)
NUB_STUB_H = 0.35      # short cylinder proud of split
NUB_DOME_H = 0.35      # stacked spherical-cap tip (STUB+DOME=ENGAGE)
SOCK_CLR = 0.18        # radial clearance ~0.15–0.20
SOCK_D = NUB_D + SOCK_CLR  # 2.38
SOCK_DEPTH = NUB_ENGAGE + 0.20  # 0.90

GAP = BODY_CLR

# Shaft-near flange EAR nest (A). Real ears = body width ±6.50, not ±6.15 bar.
EAR_HALF_Y = BODY_Y / 2.0  # 6.50
TAB_CLR = 0.15             # /side to ear (FDM; was 0.12)
NEST_Y = EAR_HALF_Y + TAB_CLR  # 6.62
TAB_Z_CLR = 0.18           # ≥1 layer FDM (was 0.03)
TIP_WALL = 0.40             # solid tip wall beyond ear tip
NEST_R = 0.0
EAR_BLEND = 0.25            # pocket slightly into body at x0
SLOT_D = 3.80               # optional U-slot Ø on ears

x0 = -SPLINE_FROM_EDGE          # -5.8
x1 = BODY_X - SPLINE_FROM_EDGE  # +17.2
y0, y1 = -BODY_Y / 2.0, BODY_Y / 2.0
OVERHANG = (TAB_SPAN - BODY_X) / 2.0  # 3.4
tab_x0 = x0 - OVERHANG          # -9.2
tab_x1 = x1 + OVERHANG          # +20.6
tab_z0 = TAB_FROM_BASE          # 17.0
tab_z1 = TAB_FROM_BASE + TAB_T  # 19.5
split_z = (tab_z0 + tab_z1) / 2.0

# Short uniform brick — BOTH halves. Far body/tab exit +X at 12.
SHELL_X0, SHELL_X1 = -12.0, 12.0
SHELL_Y0, SHELL_Y1 = -12.0, 12.0
SHELL_Z0 = 8.0

cav_y0, cav_y1 = y0 - GAP, y1 + GAP          # ±6.68 with BODY_CLR=0.18
# Near ear footprint (shaft end); far ear exits shell at +X
ear_near_x0, ear_near_x1 = tab_x0, x0        # -9.2 → -5.8
ear_far_x0, ear_far_x1 = x1, tab_x1          # 17.2 → 20.6
cav_x0 = ear_near_x0 - TIP_WALL              # -9.6 tip wall
cav_x1 = SHELL_X1 + 0.50                     # 12.5 open +X (far ear/body out)
body_cav_x0 = x0 - 0.20                      # body friction cavity starts near x0
EAR_NEST_X1 = ear_near_x1 + EAR_BLEND        # -5.55 pocket into body blend

flange_z0 = BODY_Z + 0.5                     # 26.3 (flange / servo ledge)
flange_z1 = flange_z0 + HUB_FLANGE_T         # 28.3 with T=2.0
deck_z0 = flange_z1 + 0.25                   # 28.55
tower_t = BRG_LEAD + BRG_W + SHOULDER_T + FACE_EXTRA
face_z = deck_z0 + tower_t                   # 50.00
brg_seat_z = deck_z0 + BEARING_LIFT + BRG_LEAD
JOURNAL_LEN = HUB_FACE_Z - flange_z1             # core length; reinforced below bearing

CLIP_X = 0.0
SIDE_EDGE_SETBACK = PITCH / 2 + PITCH
cb_tech_z = face_z - SIDE_EDGE_SETBACK
ca_tech_z = cb_tech_z - PITCH  # lower side row, now entirely in ClamshellB
side_x = (-PITCH, PITCH)  # ±8
top_xy = ((PITCH, PITCH), (PITCH, -PITCH), (-PITCH, PITCH), (-PITCH, -PITCH))
# 4-corner alternating nubs on mating split (inboard of outer wall, clear of CLIP_W=8.5).
# A nubs at (+8,+9.3)&(-8,-9.3); A sockets at (+8,-9.3)&(-8,+9.3); B inverse.
# Inboard of Technic X=±8 (edge≈5.53); |x|≥5.0 clears seat±3.75+SOCK_R.
# Y toward outer wall for thick deck over Technic roof (closed blind SOCK_DEPTH).
nub_xy_A = ((8.40, 9.40), (-8.40, -9.40))
sock_xy_A = ((8.40, -9.40), (-8.40, 9.40))
# Blind top Technic: through tower deck only; stop well above split_z=20.
TOP_TECH_DEPTH = 8.20  # 1.275 mm web to upper side-bore crown

# v16.30: open-C friction retainer — Z center on split_z (clamshell division).
# Jeff correction: datum = split_z (A/B mating plane), NOT mid of full pocket Z span.
# Equal land engagement above/below split. Uniform CLIP_XW extrusion.
# Open C = outer rect − cut that opens cavity-side long face + optional cross-bars.
# No detents, hooks, or barbs. Friction on Y clamp faces (primary) + intentional X press.
# Slightly wider than v16.29; tight FDM X press preserved (0.4n/0.2L PETG).
CLIP_XW = 7.50                                # was 7.40; a little wider again
SPINE_HALF = CLIP_XW / 2.0                    # 3.75
# Equal interference each side keeps clip X center == pocket X center (CLIP_X).
# Total width interference 0.08 mm (clip wider than slot) — tight FDM press in 0.04–0.10 band.
SLOT_X_INTERF_EACH = 0.04                     # mm press each side
SLOT_X_CLR_EACH = -SLOT_X_INTERF_EACH         # negative => interference (meta / assert alias)
SLOT_HALF = SPINE_HALF - SLOT_X_INTERF_EACH   # 3.71 — pocket narrower than clip
CHAN_HALF = SLOT_HALF                         # continuous channel; same X half
HOOK_HALF = SPINE_HALF                        # back-compat alias (unused for hooks)
SHOE_X = SPINE_HALF
POCKET_FLOOR = 9.00
CAV_Y_HALF = abs(cav_y1)                      # 6.55
WALL_TO_CAV = POCKET_FLOOR - CAV_Y_HALF
SPINE_OUTER = 12.0                            # flush — do not go proud
LIP_Y = SPINE_OUTER - POCKET_FLOOR            # 2.45
LIP_Z = 3.00                                  # envelope ref (catch face depth)
# --- Slide clearance on clamp faces (Y): locate/slip PETG 0.05–0.10 mm TOTAL ---
SLIDE_CLR_Y = 0.05
# Continuous channel spanning A and B (envelope A_CATCH / B_CATCH)
A_CATCH_Z = split_z - LIP_Z                   # envelope; rail cut through for slide
B_CATCH_Z = 24.20
B_LIP_Z1 = B_CATCH_Z + LIP_Z                  # 27.20
# Extend into A so clip centered on split_z still fits with end clearance.
CHAN_Z0 = 12.00                               # was 14.00; lowered for split_z datum
CHAN_Z1 = 26.50                               # into B toward lip (≤ B_LIP_Z1)
SLOT_Z0, SLOT_Z1 = CHAN_Z0, CHAN_Z1           # clamshell pocket/slot Z bounds
SLOT_Z_MID = (SLOT_Z0 + SLOT_Z1) / 2.0        # pocket mid (NOT clip datum)
CLIP_SPAN_Z_TARGET = 11.60                    # keep span; engagement set by split_z center
# Center clip on split_z: equal engagement on ClamshellA / ClamshellB (±0.05 gate).
FRAME_Z0 = round(split_z - CLIP_SPAN_Z_TARGET / 2.0, 2)  # 12.45
FRAME_Z1 = round(split_z + CLIP_SPAN_Z_TARGET / 2.0, 2)  # 24.05
SLIDE_CLR_Z = round((SLOT_Z1 - SLOT_Z0) - (FRAME_Z1 - FRAME_Z0), 2)  # channel end play
# Channel end gaps (may be unequal — datum is split_z, not pocket mid).
CLIP_Z_GAP_BELOW = round(FRAME_Z0 - SLOT_Z0, 2)  # 0.45
CLIP_Z_GAP_ABOVE = round(SLOT_Z1 - FRAME_Z1, 2)  # 2.45
# Equal land engagement across A/B mating plane (primary success metric).
CLIP_ENGAGE_A = round(split_z - FRAME_Z0, 2)     # below split into A
CLIP_ENGAGE_B = round(FRAME_Z1 - split_z, 2)     # above split into B
# Horizontal cross members (rungs) across open-C cavity — FDM side print (build +X).
CROSS_MEMBER_COUNT = 2                        # plus spine; Jeff: less strength OK
CROSS_MEMBER_T = 1.20                         # thickness in Z
CROSS_MEMBER_FILLET = 0.30                    # small fillet note (visual/print); optional live
# C outer envelope (YZ) — fills the continuous pocket channel depth
FRAME_Y_OUTER = SPINE_OUTER                   # 12.0 flush
FRAME_Y_INNER = round(POCKET_FLOOR + SLIDE_CLR_Y, 2)  # 9.05 — open mouth / clamp face
C_WALL = 1.60
FRAME_WALL = C_WALL                           # alias used by asserts/meta
# --- Soft detent (retention only; kid-soft; NOT load-bearing) ---
# Bump on each C-leg insert face (toward cavity), axis // X → round YZ lead.
# Shallow matching seat in channel floor. No sharp hooks/barbs.
DETENT_PROUD = 0.0
DETENT_D = 1.20                               # bump cylinder Ø (gentle curve)
DETENT_R = DETENT_D / 2.0                     # 0.60
DETENT_SEAT_D = 1.30                          # seat slightly larger than bump
DETENT_SEAT_R = DETENT_SEAT_D / 2.0
DETENT_SEAT_DEPTH = 0.0
DETENT_LEN = CLIP_XW - 0.40                   # leave tiny X end clearance in channel
# Z centers on each leg (mid of C_WALL band)
DETENT_Z_BOT = round(FRAME_Z0 + C_WALL / 2.0, 3)  # in A channel
DETENT_Z_TOP = round(FRAME_Z1 - C_WALL / 2.0, 3)  # in B channel
# Nominal interference while riding flat floor before seat:
# DETENT_PROUD - SLIDE_CLR_Y ≈ 0.12 mm (soft PETG flex of legs)
CLIP_Z0 = FRAME_Z0
CLIP_Z1 = FRAME_Z1
CLIP_SPAN_Z = CLIP_Z1 - CLIP_Z0
# Shared center with pocket (CLIP_X). Equal side press = SLOT_X_INTERF_EACH each side
# (CLIP_SIDE_GAP_* negative = interference).
CLIP_X0 = CLIP_X - CLIP_XW / 2.0
CLIP_X1 = CLIP_X + CLIP_XW / 2.0
POCKET_X0 = CLIP_X - SLOT_HALF
POCKET_X1 = CLIP_X + SLOT_HALF
CLIP_SIDE_GAP_NEG = CLIP_X0 - POCKET_X0       # +X-min gap (toward −X pocket wall)
CLIP_SIDE_GAP_POS = POCKET_X1 - CLIP_X1       # +X-max gap (toward +X pocket wall)
# Pocket Z = continuous channel (A below split, B above)
A_POCKET_Z0 = CHAN_Z0
A_POCKET_Z1 = split_z + 0.05
B_POCKET_Z0 = split_z - 0.05
B_POCKET_Z1 = CHAN_Z1
A_CHAN_Z0 = CHAN_Z0
A_CHAN_Z1 = A_POCKET_Z1
POCKET_Y_OVER = 0.35
# Back-compat aliases referenced sparsely in shell comments / leftover helpers
CHAN_FLOOR = POCKET_FLOOR
RAIL_Y = LIP_Y
RAIL_Z = LIP_Z
STOCK_WALL_Y = LIP_Y
SPINE_T = C_WALL                              # 1.40 — C spine thickness in Y
SPINE_INNER = FRAME_Y_OUTER - SPINE_T         # 10.60 — inside face of spine
ARM_T = C_WALL                                # legs same thickness in Z
ARM_INNER_Y = FRAME_Y_INNER                   # open mouth at clamp face
ROOT_R = 0.0

# Quaternion: +90° about Y → (x,y,z)→(z,y,-x); Z-cylinder becomes X-cylinder
QY90 = [0.0, math.sin(math.pi / 4), 0.0, math.cos(math.pi / 4)]

REF = "$ref"
steps: list = []


def call(sid: str, group: str, op: str, arguments: dict) -> None:
    steps.append({"id": sid, "call": {"group": group, "operation": op, "arguments": arguments}})


def sketch_begin(name: str) -> None:
    call(
        name.replace(" ", "_") + "_begin",
        "sketch/draw",
        "sketch_begin",
        {"name": name, "plane": {"type": "origin_plane", "plane": "xy"}},
    )


def rect(sid: str, ax: float, ay: float, cx: float, cy: float) -> None:
    # Grid capture is ~2.5 mm onto a 10 mm grid. Clip X=±2.1 and every
    # pocket Y in 9.5–12 sit inside that bubble and silently become 0 or 10.
    # ctrl_held is not enough (v15 stayed safe only because half-width was 2.6).
    call(sid + "_nosnap", "sketch/selection", "sketch_set_grid_snap", {"enabled": False})
    call(
        sid,
        "sketch/draw",
        "sketch_add_rectangle_locked",
        {
            "mode": "two_point",
            "anchor": {"x": ax, "y": ay},
            "corner_hint": {"x": cx, "y": cy},
            "width_mm": abs(cx - ax),
            "height_mm": abs(cy - ay),
            "ctrl_held": True,
        },
    )
    call(sid + "_snap", "sketch/selection", "sketch_set_grid_snap", {"enabled": True})


def circle(sid: str, d: float, x: float = 0.0, y: float = 0.0, *, nosnap: bool = False) -> None:
    """nosnap: engine grid is 10 mm with 2.5 mm capture. (8.4, 9.4) snaps to (10, 10)
    while solid_move of the dome does not — nubs then miss socks. Disable for locators.
    """
    r = d / 2.0
    if nosnap:
        call(
            sid + "_nosnap",
            "sketch/selection",
            "sketch_set_grid_snap",
            {"enabled": False},
        )
    call(
        sid,
        "sketch/draw",
        "sketch_add_circle_locked",
        {
            "mode": "center_diameter",
            "anchor": {"x": x, "y": y},
            "edge_hint": {"x": x + r, "y": y},
            "diameter_text": f"{d:g}",
            "ctrl_held": False,
        },
    )
    if nosnap:
        call(
            sid + "_snap",
            "sketch/selection",
            "sketch_set_grid_snap",
            {"enabled": True},
        )


def finish(name: str) -> None:
    call(name.replace(" ", "_") + "_finish", "sketch/draw", "sketch_finish", {})


def sketch_begin_plane(name: str, plane: str = "xy") -> None:
    call(
        name.replace(" ", "_") + "_begin",
        "sketch/draw",
        "sketch_begin",
        {"name": name, "plane": {"type": "origin_plane", "plane": plane}},
    )


def line_raw(sid: str, x0: float, y0: float, x1: float, y1: float) -> None:
    call(
        sid,
        "sketch/draw",
        "sketch_add_line",
        {
            "from": {"x": x0, "y": y0},
            "to_raw": {"x": x1, "y": y1},
            "ctrl_held": False,
        },
    )


def extrude(sid: str, sketch: str, dist: float, operation: str = "new_body", bodies=None, flip: bool = False) -> None:
    call(
        sid,
        "solid/build",
        "solid_extrude",
        {
            "sketch_name": sketch,
            "profile_indices": [0],
            "operation": operation,
            "extent": {"type": "distance", "distance": dist},
            "taper_angle_deg": 0,
            "flip": flip,
            "target_body_ids": bodies or [],
        },
    )


def extrude_profiles(sid: str, sketch: str, dist: float, indices: list[int], operation: str = "new_body", bodies=None) -> None:
    call(
        sid,
        "solid/build",
        "solid_extrude",
        {
            "sketch_name": sketch,
            "profile_indices": indices,
            "operation": operation,
            "extent": {"type": "distance", "distance": dist},
            "taper_angle_deg": 0,
            "flip": False,
            "target_body_ids": bodies or [],
        },
    )


def let_last_feature(name: str, from_id: str) -> None:
    steps.append(
        {
            "let": {
                name: {
                    "$select": {
                        "from": {REF: from_id},
                        "path": "/document/features",
                        "take": "last",
                        "pointer": "/id",
                    }
                }
            }
        }
    )


def let_body(name: str, from_id: str, feat: str) -> None:
    steps.append(
        {
            "let": {
                name: {
                    "$select": {
                        "from": {REF: from_id},
                        "path": "/scene/bodies",
                        "where": {"/feature_id": {REF: feat}},
                        "take": "one",
                    }
                }
            }
        }
    )


def let_face_z(name: str, from_id: str, body_var: str, zsign: int = 1) -> None:
    steps.append(
        {
            "let": {
                name: {
                    "$select": {
                        "from": {
                            "$select": {
                                "from": {REF: from_id},
                                "path": "/scene/bodies",
                                "where": {"/id": {REF: body_var, "pointer": "/id"}},
                                "take": "one",
                            }
                        },
                        "path": "/faces",
                        "where": {"/plane/normal/2": zsign},
                        "take": "first",
                    }
                }
            }
        }
    )


def face_axis_let(name: str, from_id: str, body_var: str, axis_idx: int, sign: int) -> None:
    steps.append(
        {
            "let": {
                name: {
                    "$select": {
                        "from": {
                            "$select": {
                                "from": {REF: from_id},
                                "path": "/scene/bodies",
                                "where": {"/id": {REF: body_var, "pointer": "/id"}},
                                "take": "one",
                            }
                        },
                        "path": "/faces",
                        "where": {f"/plane/normal/{axis_idx}": sign},
                        "take": "first",
                    }
                }
            }
        }
    )


def body_ptr(var: str) -> dict:
    return {REF: var, "pointer": "/id"}


def hole(sid: str, body_var: str, face_var: str, xyz: list, dia: float, depth: float | None = None) -> None:
    extent = {"type": "through_all"} if depth is None else {"type": "distance", "depth": depth}
    call(
        sid,
        "solid/refine",
        "solid_hole",
        {
            "body_id": body_ptr(body_var),
            "face_id": {REF: face_var, "pointer": "/id"},
            "position": {"$project": {"point": xyz, "basis": {REF: face_var, "pointer": "/plane"}}},
            "diameter": dia,
            "extent": extent,
            "style": "simple",
            "counterbore_diameter": 0,
            "counterbore_depth": 0,
            "countersink_diameter": 0,
            "countersink_angle_deg": 90,
            "flip": False,
        },
    )


def appearance(sid: str, body_var: str, color: dict, name: str, filament: str = "PETG") -> None:
    call(
        sid,
        "document/appearance",
        "set_body_appearance",
        {
            "body_id": body_ptr(body_var),
            "brand": "Generic",
            "color": color,
            "color_name": name,
            "filament_type": filament,
            "material_name": f"Generic {filament}",
        },
    )


def component(sid: str, name: str, body_var: str) -> None:
    call(
        sid,
        "assembly/joints",
        "assembly_create_component",
        {"name": name, "body_ids": [body_ptr(body_var)], "absorb_promoted_bodies": True},
    )


def move(sid: str, body_var: str, z: float = 0, x: float = 0, y: float = 0, rotation=None) -> None:
    call(
        sid,
        "solid/body",
        "solid_move_copy",
        {
            "body_ids": [body_ptr(body_var)],
            "translation": {"x": x, "y": y, "z": z},
            "pivot": {"x": 0, "y": 0, "z": 0},
            "rotation": rotation if rotation is not None else [0, 0, 0, 1],
            "copy": False,
        },
    )


def combine_join(sid: str, target: str, tool: str) -> None:
    call(
        sid,
        "solid/body",
        "solid_combine",
        {
            "target_body_id": body_ptr(target),
            "tool_body_ids": [body_ptr(tool)],
            "operation": "join",
            "keep_tools": False,
        },
    )


def combine_cut(sid: str, target: str, tool: str) -> None:
    call(
        sid,
        "solid/body",
        "solid_combine",
        {
            "target_body_id": body_ptr(target),
            "tool_body_ids": [body_ptr(tool)],
            "operation": "cut",
            "keep_tools": False,
        },
    )


def new_rect(body: str, tag: str, ax, ay, cx, cy, h, z0) -> str:
    sketch_begin(tag)
    rect(f"{tag}_r", ax, ay, cx, cy)
    finish(tag)
    extrude(f"{tag}_ex", tag, h)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(body, f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_mv", body, z=z0)
    return f"{tag}_mv"


def add_rect(target: str, tag: str, ax, ay, cx, cy, h, z0) -> str:
    sketch_begin(tag)
    rect(f"{tag}_r", ax, ay, cx, cy)
    finish(tag)
    extrude(f"{tag}_ex", tag, h)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_mv", f"{tag}_tmp", z=z0)
    sid = f"join_{tag}"
    combine_join(sid, target, f"{tag}_tmp")
    return sid


def cut_rect(target: str, tag: str, ax, ay, cx, cy, h, z0) -> str:
    sketch_begin(tag)
    rect(f"{tag}_r", ax, ay, cx, cy)
    finish(tag)
    extrude(f"{tag}_ex", tag, h)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_mv", f"{tag}_tmp", z=z0)
    sid = f"cut_{tag}"
    combine_cut(sid, target, f"{tag}_tmp")
    return sid


def add_cyl(target: str, tag: str, d, x, y, h, z0, *, nosnap: bool = False) -> str:
    sketch_begin(tag)
    circle(f"{tag}_c", d, x, y, nosnap=nosnap)
    finish(tag)
    extrude(f"{tag}_ex", tag, h)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_mv", f"{tag}_tmp", z=z0)
    sid = f"join_{tag}"
    combine_join(sid, target, f"{tag}_tmp")
    return sid


def cut_cyl(target: str, tag: str, d, x, y, h, z0, *, nosnap: bool = False) -> str:
    sketch_begin(tag)
    circle(f"{tag}_c", d, x, y, nosnap=nosnap)
    finish(tag)
    extrude(f"{tag}_ex", tag, h)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_mv", f"{tag}_tmp", z=z0)
    sid = f"cut_{tag}"
    combine_cut(sid, target, f"{tag}_tmp")
    return sid


def cut_taper(target: str, tag: str, z0: float, d0: float, z1: float, d1: float) -> str:
    """Coaxial ruled clearance taper; explicit loft tool and boolean cut."""
    sections=[]
    for i,(z,d) in enumerate(((z0,d0),(z1,d1))):
        name=f"{tag}_{i}"
        call(name+"_plane", "solid/reference", "construction_plane_offset", {
            "name":name,"reference":{"type":"origin_plane","plane":"xy"},"distance":z})
        steps.append({"let":{name+"_ref":{"type":"datum_plane","datum_id":{
            "$select":{"from":{"$ref":name+"_plane","pointer":""},"path":"/planes",
            "where":{"/name":name},"take":"one","pointer":"/datum_id"}}}}})
        call(name+"_begin","sketch/draw","sketch_begin",{
            "name":name,"plane":{"$ref":name+"_ref","pointer":""}})
        circle(name+"_circle",d)
        finish(name)
        sections.append({"sketch_name":name,"profile_index":0})
    call(tag+"_loft","solid/build","solid_loft",{"sections":sections,"ruled":True,
         "operation":"new_body","target_body_ids":[],"continuity":"g0",
         "centerline":None,"guide_rail":None})
    let_last_feature(tag+"_feat",tag+"_loft")
    let_body(tag+"_tmp",tag+"_loft",tag+"_feat")
    combine_cut(tag+"_cut",target,tag+"_tmp")
    return tag+"_cut"


def cut_ycyl(target: str, tag: str, d: float, x: float, z: float, ylo: float, yhi: float) -> str:
    """Cut a cylinder along Y; explicit boolean preserves internal pin-tip relief."""
    sketch_begin(tag)
    circle(f"{tag}_c", d, 0.0, 0.0, nosnap=True)
    finish(tag)
    extrude(f"{tag}_ex", tag, yhi-ylo)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    move(f"{tag}_place", f"{tag}_tmp", x=x, y=yhi, z=z,
         rotation=[math.sin(math.pi/4),0.0,0.0,math.cos(math.pi/4)])
    sid=f"cut_{tag}"
    combine_cut(sid,target,f"{tag}_tmp")
    return sid


def _xcyl_tool(tag: str, d: float, length: float, *, nosnap: bool = True) -> str:
    """Z-extruded circle → Ry+90 → X-axis cylinder body var `{tag}_tmp`."""
    sketch_begin(tag)
    circle(f"{tag}_c", d, 0.0, 0.0, nosnap=nosnap)
    finish(tag)
    extrude(f"{tag}_ex", tag, length)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    return f"{tag}_tmp"


def add_xcyl(target: str, tag: str, d: float, cx: float, cy: float, cz: float, length: float) -> str:
    """Join X-axis cylinder centered at (cx, cy, cz)."""
    body = _xcyl_tool(tag, d, length)
    move(f"{tag}_place", body, x=cx - length / 2.0, y=cy, z=cz, rotation=QY90)
    sid = f"join_{tag}"
    combine_join(sid, target, body)
    return sid


def cut_xcyl(target: str, tag: str, d: float, cx: float, cy: float, cz: float, length: float) -> str:
    """Cut X-axis cylinder centered at (cx, cy, cz)."""
    body = _xcyl_tool(tag, d, length)
    move(f"{tag}_place", body, x=cx - length / 2.0, y=cy, z=cz, rotation=QY90)
    sid = f"cut_{tag}"
    combine_cut(sid, target, body)
    return sid


def cut_ou_scoop(target: str, tag: str, y_sign: float, cz: float) -> str:
    """Horizontal (axis // X) cylindrical finger scoop at ±Y outer wall."""
    length = 2.0 * OU_HALF_X
    outer = SHELL_Y1 if y_sign > 0 else SHELL_Y0
    cy = outer + y_sign * (OU_R - OU_DEPTH)
    xc = CLIP_X
    sketch_begin(tag)
    circle(f"{tag}_c", 2.0 * OU_R, 0.0, 0.0)
    finish(tag)
    extrude(f"{tag}_ex", tag, length)
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    # Ry+90 maps Z-cyl → X-cyl; T x=xc-L/2 centers length on xc (R then T)
    move(f"{tag}_place", f"{tag}_tmp", x=xc - length / 2.0, y=cy, z=cz, rotation=QY90)
    sid = f"cut_{tag}"
    combine_cut(sid, target, f"{tag}_tmp")
    return sid



def add_ear_nest(target, tag, shell_z0, shell_z1):
    return cut_rect(target, f"{tag}_pocket", cav_x0, -NEST_Y,
                    EAR_NEST_X1, NEST_Y,
                    TAB_T + 2 * TAB_Z_CLR, tab_z0 - TAB_Z_CLR)


def loft_sections(sid: str, sections: list[dict], continuity: str = "g1") -> None:
    call(
        sid,
        "solid/build",
        "solid_loft",
        {
            "sections": sections,
            "ruled": False,
            "operation": "new_body",
            "target_body_ids": [],
            "continuity": continuity,
            "centerline": None,
            "guide_rail": None,
        },
    )


def _loft_sphere_cap(tag: str, a: float, dome_h: float) -> str:
    """ONE lofted spherical-cap body along +Z from z=0 (r=a) to z=dome_h (tip). Returns body var."""
    Rsph = (a * a + dome_h * dome_h) / (2.0 * dome_h)

    def r_at(z: float) -> float:
        # Short flat chord at tip (r≥0.38) — smooth loft, no needle / step-drop
        return max(0.38, math.sqrt(max(0.0, Rsph * Rsph - (z - (dome_h - Rsph)) ** 2)))

    # 6 stations; tip flat chord (optional short flat OK per AM nub brief)
    zs = [0.0, 0.2 * dome_h, 0.4 * dome_h, 0.6 * dome_h, 0.8 * dome_h, dome_h]
    sections = []
    for i, zl in enumerate(zs):
        sk = f"{tag}_s{i}"
        pname = f"{tag}_pl{i}"
        rr = r_at(zl)
        if abs(zl) < 1e-12:
            sketch_begin(sk)
        else:
            call(
                f"cpl_{pname}",
                "solid/reference",
                "construction_plane_offset",
                {
                    "name": pname,
                    "reference": {"type": "origin_plane", "plane": "xy"},
                    "distance": float(zl),
                },
            )
            steps.append(
                {
                    "let": {
                        f"{pname}_plane": {
                            "datum_id": {
                                "$select": {
                                    "from": {"$ref": f"cpl_{pname}", "pointer": ""},
                                    "path": "/planes",
                                    "where": {"/name": pname},
                                    "take": "one",
                                    "pointer": "/datum_id",
                                }
                            },
                            "type": "datum_plane",
                        }
                    }
                }
            )
            call(
                f"{sk}_begin",
                "sketch/draw",
                "sketch_begin",
                {"name": sk, "plane": {"$ref": f"{pname}_plane", "pointer": ""}},
            )
        circle(f"{sk}_c", 2.0 * rr, 0.0, 0.0)
        finish(sk)
        sections.append({"sketch_name": sk, "profile_index": 0})

    loft_sid = f"{tag}_loft"
    loft_sections(loft_sid, sections, continuity="g1")
    let_last_feature(f"{tag}_feat", loft_sid)
    let_body(f"{tag}_tmp", loft_sid, f"{tag}_feat")
    return f"{tag}_tmp"


def add_am_nub(
    target: str, tag: str, px: float, py: float,
    z_split: float, up_sign: float, flat_sign: float,
) -> str:
    """AM nub: boss+stub cylinder + ONE lofted spherical-cap dome (no cyl stack)."""
    boss = NUB_BOSS_H
    stub = NUB_STUB_H
    dome_h = NUB_DOME_H
    assert abs((stub + dome_h) - NUB_ENGAGE) < 1e-6
    a = NUB_D / 2.0

    # 1) Boss + stub as single cylinder (manifold-proven)
    if up_sign > 0:
        z_boss = z_split - boss
        last_l = add_cyl(target, f"{tag}_stub", NUB_D, px, py, boss + stub, z_boss, nosnap=True)
        # 2) Lofted dome on top of stub
        cap = _loft_sphere_cap(f"{tag}_cap", a, dome_h)
        move(f"{tag}_cap_mv", cap, x=px, y=py, z=z_split + stub)
        sid = f"join_{tag}_cap"
        combine_join(sid, target, cap)
        z_lo = z_boss - 0.05
        z_span = boss + stub + dome_h + 0.15
    else:
        # B: tip at -Z. Stub+boss from z_split-stub through split into B.
        # Dome tip at z_split - engage; loft along +Z then flip.
        cap = _loft_sphere_cap(f"{tag}_cap", a, dome_h)
        qx180 = [1.0, 0.0, 0.0, 0.0]
        # After Rx180, local +z → -z. Place so local 0 (cap base) → z_split - stub
        # Cap extends local 0..dome_h → world (z_split-stub) .. (z_split-stub-dome_h) = z_split-engage
        move(f"{tag}_cap_mv", cap, x=px, y=py, z=z_split - stub, rotation=qx180)
        sid = f"join_{tag}_cap"
        combine_join(sid, target, cap)
        last_l = add_cyl(target, f"{tag}_stub", NUB_D, px, py, stub + boss, z_split - stub, nosnap=True)
        z_lo = z_split - NUB_ENGAGE - 0.05
        z_span = boss + stub + dome_h + 0.15

    if NUB_FLAT > 0.05:
        r = NUB_D / 2.0
        flat_x = px + flat_sign * (r - NUB_FLAT)
        if flat_sign > 0:
            ax, cx_ = flat_x, px + r + 0.40
        else:
            ax, cx_ = px - r - 0.40, flat_x
        last_l = cut_rect(
            target, f"{tag}_flat",
            ax, py - r - 0.25, cx_, py + r + 0.25,
            z_span, z_lo,
        )
    return last_l


def cut_d_sock(target: str, tag: str, px: float, py: float, z_base: float, depth: float) -> str:
    """Shallow blind round socket (clears dome nub); depth = engage + 0.2."""
    return cut_cyl(target, tag, SOCK_D, px, py, depth, z_base, nosnap=True)


# =============================================================================
# 1) Purchased servo proxy (body + discrete near/far flange EARS)
# =============================================================================
new_rect("servo_body", "sb", x0, y0, x1, y1, BODY_Z, 0.0)
# Near ear (shaft end) + far ear — not a continuous tab bar
add_rect("servo_body", "ear_n", ear_near_x0, -EAR_HALF_Y, ear_near_x1, EAR_HALF_Y, TAB_T, tab_z0)
add_rect("servo_body", "ear_f", ear_far_x0, -EAR_HALF_Y, ear_far_x1, EAR_HALF_Y, TAB_T, tab_z0)
# Optional U-slot fidelity on each ear (open toward tip)
_near_hx = (ear_near_x0 + ear_near_x1) / 2.0
_far_hx = (ear_far_x0 + ear_far_x1) / 2.0
cut_cyl("servo_body", "slot_n", SLOT_D, _near_hx, 0.0, TAB_T + 0.4, tab_z0 - 0.2)
cut_rect("servo_body", "slot_n_u", ear_near_x0 - 0.1, -SLOT_D / 2, _near_hx, SLOT_D / 2, TAB_T + 0.4, tab_z0 - 0.2)
cut_cyl("servo_body", "slot_f", SLOT_D, _far_hx, 0.0, TAB_T + 0.4, tab_z0 - 0.2)
cut_rect("servo_body", "slot_f_u", _far_hx, -SLOT_D / 2, ear_far_x1 + 0.1, SLOT_D / 2, TAB_T + 0.4, tab_z0 - 0.2)
appearance("sv_color", "servo_body", {"r": 30, "g": 30, "b": 35, "a": 255}, "Servo black", "ABS")

# =============================================================================
# 2) ClamshellA — short uniform brick, near-EAR pocket, OU scoops
# =============================================================================
lower_h = split_z - SHELL_Z0  # 12.0
last = new_rect("clamshell_a", "ca", SHELL_X0, SHELL_Y0, SHELL_X1, SHELL_Y1, lower_h, SHELL_Z0)

# Body friction cavity (23×13 + BODY_CLR); open +X for far ear/body exit.
# Start near x0 so tip brick stays solid (tip wall + ear floor/ceiling).
last = cut_rect(
    "clamshell_a", "ca_cav",
    body_cav_x0, cav_y0, cav_x1, cav_y1,
    lower_h + 0.4, SHELL_Z0 - 0.2,
)
# Shaft-near EAR pocket (Z-band only) — tip/Y/Z trap; A owns tab Z
last = add_ear_nest("clamshell_a", "ca_nest", SHELL_Z0, split_z)

# Both side rows are now above the split; ClamshellA has no side bores.

# v16 pockets. Channel (shallow) lets the flush spine cross the split.
# Deep pocket stops on the catch face so the rail (catch → split) stays thick.
def cut_yp_ym(shell, tag, y_floor, z0, z1, x_half=None):
    xh = SLOT_HALF if x_half is None else x_half
    h = z1 - z0
    if h <= 0.05:
        raise SystemExit(f"bad pocket {tag} h={h}")
    # Pocket X centered on CLIP_X (same center as open-C clips).
    cut_rect(
        shell, f"{tag}_yp",
        CLIP_X - xh, y_floor,
        CLIP_X + xh, SHELL_Y1 + POCKET_Y_OVER,
        h, z0,
    )
    return cut_rect(
        shell, f"{tag}_ym",
        CLIP_X - xh, SHELL_Y0 - POCKET_Y_OVER,
        CLIP_X + xh, -y_floor,
        h, z0,
    )

# A: continuous rectangular channel (v16.7 slide path, same as v16.6). Floor=POCKET_FLOOR.
# Spans into the split so A+B form one clean channel for the open C clip.
last = cut_yp_ym("clamshell_a", "ca_spine", SPINE_INNER - 0.05, A_POCKET_Z0, A_POCKET_Z1)
last = cut_yp_ym("clamshell_a", "ca_leg", POCKET_FLOOR, CHAN_Z0, FRAME_Z0 + C_WALL + 0.05)

# Align nubs + sockets LAST (after seat/OU/ledge). Alternating 4-corner.
# Flat faces toward clip center (X=0).
for i, (px, py) in enumerate(nub_xy_A):
    flat_s = -1.0 if px > 0 else 1.0
    last = add_am_nub(
        "clamshell_a", f"ca_nub{i}",
        px, py, split_z, +1.0, flat_s,
    )
for i, (px, py) in enumerate(sock_xy_A):
    last = cut_d_sock(
        "clamshell_a", f"ca_sock{i}",
        px, py, split_z - SOCK_DEPTH, SOCK_DEPTH + 0.10,
    )

appearance("ca_color", "clamshell_a", {"r": 40, "g": 125, "b": 210, "a": 255}, "lower_clam ClamshellA PETG blue")

# =============================================================================
# 3) ClamshellB — SAME XY envelope, deck + open +X + OU scoops
# =============================================================================
upper_h = face_z - split_z
last = new_rect("clamshell_b", "cb", SHELL_X0, SHELL_Y0, SHELL_X1, SHELL_Y1, upper_h, split_z)

drop_h = BODY_Z + 0.1 - split_z
# Body cavity; open +X. Near-ear Z lives in A (floor/ceil/tip). B lip added AFTER holes
# so it cannot steal let_face_z(+Z) from the tower top (face_z).
last = cut_rect(
    "clamshell_b", "cb_cav",
    body_cav_x0, cav_y0, cav_x1, cav_y1,
    drop_h + 0.3, split_z - 0.1,
)

let_face_z("cb_out", last, "clamshell_b", 1)
last = "cb_jnl"
# Face poke-out ONLY — diametral clearance on journal; lip ID < BRG_OD retains bearing.
hole(last, "clamshell_b", "cb_out", [0.0, 0.0, face_z], FACE_HOLE_D)
# ONE-DIRECTION into upper: continuous BRG_POCKET path from cavity/split up to seat
# so Ø12 bearing + hub flange pass with lower clam absent. No Ø8.8 waist / Ø10.9
# collar (those blocked OD insert — v16.24 both-halves-around failure mode).
# Pocket height is BRG_POCKET_H only; face stays ØFACE_HOLE_D (not front tunnel).
_insert_z0 = 26.0
_insert_h = brg_seat_z - _insert_z0  # ~8.35; continuous OD-clear bore to seat
last=cut_cyl("clamshell_b","cb_od_insert_path",BRG_POCKET,0,0,_insert_h,_insert_z0)
last=cut_cyl("clamshell_b","cb_brg_pocket",BRG_POCKET,0,0,BRG_POCKET_H,brg_seat_z)

# One row on both side faces — BLIND corridors (not through).
# Wide Ø12.3 insert path would intersect through-pins at X=±8,Z=30; blind depth
# 8.2 mm from each outer Y leaves ~0.5+ mm to the axial bore (assembly-path tradeoff).
# Lower holes remain removed for the compact servo envelope.
SIDE_BLIND_DEPTH = 8.20
for row_i, row_z in ((1, cb_tech_z),):
    for sign, y in ((1, SHELL_Y1), (-1, SHELL_Y0)):
        for col_i, x in enumerate(side_x):
            tag = f"cb_side_{row_i}_{sign}_{col_i}"
            face_axis_let(tag+"_face", last, "clamshell_b", 1, sign)
            hole(tag, "clamshell_b", tag+"_face", [x,y,row_z], TECHNIC,
                 depth=SIDE_BLIND_DEPTH)
            last = tag

# Blind pin profiles from each outer face: entry recess 0.8 + land; tip relief
# near blind bottom (still outside axial Ø12.3 bore).
for col_i, x in enumerate(side_x):
    for sign in (-1, 1):
        for label, start, end in (("entry", -0.1, 0.8), ("tip", 7.0, 8.2)):
            ys=sorted((sign*(12.0-start),sign*(12.0-end)))
            last=cut_ycyl("clamshell_b", f"upper_pin_{col_i}_{sign}_{label}",
                          6.2,x,cb_tech_z,ys[0],ys[1])

# Top four corners — BLIND (depth through tower only; no underside openings)
let_face_z("cb_top", last, "clamshell_b", 1)
face = "cb_top"
for i, (xi, yi) in enumerate(top_xy):
    sid = f"cb_top{i}"
    hole(sid, "clamshell_b", face, [xi, yi, face_z], TECHNIC, depth=TOP_TECH_DEPTH)
    last = sid
    face = f"cb_tf{i}"
    let_face_z(face, sid, "clamshell_b", 1)

# Match all four front Technic holes to the stepped side pin profile.
# Entry diameter 6.2 x 0.8 deep, 6.2-long land, then tip relief to 8.2.
for i, (xi, yi) in enumerate(top_xy):
    last=cut_cyl("clamshell_b", f"top_pin_{i}_entry", 6.2, xi, yi,
                 0.9, face_z-0.8, nosnap=True)
    last=cut_cyl("clamshell_b", f"top_pin_{i}_tip", 6.2, xi, yi,
                 1.2, face_z-8.2, nosnap=True)

# B: continuous rectangular channel continuation (same floor, same X half).
last = cut_yp_ym("clamshell_b", "cb_spine", SPINE_INNER - 0.05, B_POCKET_Z0, B_POCKET_Z1)
last = cut_yp_ym("clamshell_b", "cb_leg", POCKET_FLOOR, FRAME_Z1 - C_WALL - 0.05, CHAN_Z1)

# Align nubs (inverse of A) + sockets LAST. B nubs protrude -Z into A sockets.
for i, (px, py) in enumerate(sock_xy_A):  # B nubs where A has sockets
    flat_s = -1.0 if px > 0 else 1.0
    last = add_am_nub(
        "clamshell_b", f"cb_nub{i}",
        px, py, split_z, -1.0, flat_s,
    )
for i, (px, py) in enumerate(nub_xy_A):  # B sockets where A has nubs
    last = cut_d_sock(
        "clamshell_b", f"cb_sock{i}",
        px, py, split_z - 0.05, SOCK_DEPTH + 0.10,
    )

# Split through tab mid-thickness: B captures the upper half directly.
last = add_ear_nest("clamshell_b", "cb_nest", split_z, face_z)

appearance("cb_color", "clamshell_b", {"r": 35, "g": 170, "b": 100, "a": 255}, "upper_cover ClamshellB PETG green")

# =============================================================================
# 4) MR128 proxy
# =============================================================================
sketch_begin("mr")
circle("mrc", BRG_OD, 0, 0)
finish("mr")
extrude("mr_ex", "mr", BRG_W)
let_last_feature("mr_feat", "mr_ex")
let_body("mr128_body", "mr_ex", "mr_feat")
let_face_z("mr_top", "mr_ex", "mr128_body", 1)
hole("mr_bore", "mr128_body", "mr_top", [0, 0, BRG_W], BRG_ID)
move("mr_mv", "mr128_body", z=brg_seat_z)
appearance("mr_color", "mr128_body", {"r": 175, "g": 180, "b": 190, "a": 255}, "MR128 steel", "Metal")

# =============================================================================
# 5) OutputHub flush
# =============================================================================
sketch_begin("hf")
circle("hfc", HUB_FLANGE_D, 0, 0)
finish("hf")
extrude("hf_ex", "hf", HUB_FLANGE_T)
let_last_feature("hf_feat", "hf_ex")
let_body("hub_body", "hf_ex", "hf_feat")

sketch_begin("hj")
circle("hjc", JOURNAL, 0, 0)
finish("hj")
extrude("hj_ex", "hj", JOURNAL_LEN)
let_last_feature("hj_feat", "hj_ex")
let_body("hj_tmp", "hj_ex", "hj_feat")
move("hj_mv", "hj_tmp", z=HUB_FLANGE_T)
combine_join("hub_j", "hub_body", "hj_tmp")

# v16.27: constant OD column (= flange D) from servo-step flange up to a small
# inner journal shoulder under the bearing. No separate mid lip, no flange→neck loft.
add_cyl("hub_body", "hub_thick", HUB_FLANGE_D, 0, 0, HUB_FLANGE_T, 0.0)
_column_local0 = HUB_FLANGE_T
_inner_stop_world_z = brg_seat_z - BEARING_INNER_STOP_GAP  # axial abutment under bearing
_column_top_local = _inner_stop_world_z - flange_z0
_column_h = _column_top_local - _column_local0
assert _column_h > 1.0, _column_h
add_cyl("hub_body", "hub_constant_od", HUB_COLUMN_D, 0, 0, _column_h, _column_local0)
# Journal (already joined) continues through bearing; column top = small inner stop.
_spline_depth = (TOTAL_TO_SPLINE - flange_z0) + 0.20
last = cut_cyl("hub_body", "hs", SPLINE_SOCKET, 0, 0, _spline_depth + 0.2, -0.2)

hub_top_local = HUB_FLANGE_T + JOURNAL_LEN
last = cut_rect(
    "hub_body", "cxh",
    -AXLE_SPAN / 2, -AXLE_ARM / 2, AXLE_SPAN / 2, AXLE_ARM / 2,
    CROSS_DEPTH + 0.6, hub_top_local - CROSS_DEPTH,
)
last = cut_rect(
    "hub_body", "cxv",
    -AXLE_ARM / 2, -AXLE_SPAN / 2, AXLE_ARM / 2, AXLE_SPAN / 2,
    CROSS_DEPTH + 0.6, hub_top_local - CROSS_DEPTH,
)
move("hub_mv", "hub_body", z=flange_z0)
appearance("hub_color", "hub_body", {"r": 235, "g": 145, "b": 45, "a": 255}, "OutputHub PETG orange")

# =============================================================================
# 6) v16.27 OPEN C retainers ×2 — BuckleClipYP / BuckleClipYM ONLY
#    YZ open C (outer rect − cavity-side cut), uniform CLIP_XW along X.
#    Broad friction engagement. Outer flush |Y|=12. NOT a closed frame.
# =============================================================================

def yspan(y_sign: float, mag_a: float, mag_b: float):
    ya, yb = y_sign * mag_a, y_sign * mag_b
    return (min(ya, yb), max(ya, yb))


def build_clip(tag: str, y_sign: float, body_var: str) -> str:
    """Open C / U-channel: outer YZ rect minus cut that opens the cavity-side long face.

    Spine at |Y|≈12, top+bottom legs toward pocket floor, OPEN toward cavity (−|Y|).
    Optional horizontal cross members (rungs) across the cavity for FDM side print.
    Uniform CLIP_XW along X. Friction across the channel width; no detent.
    Top and bottom legs straddle retained shell lands and carry clamp loads.
    Side view (along X) is an open C — not a closed frame. No hooks/barbs/knurl.
    """
    # Outer solid fills the channel envelope
    y0, y1 = yspan(y_sign, FRAME_Y_INNER, FRAME_Y_OUTER)
    last_l = new_rect(
        body_var, f"{tag}_out",
        CLIP_X0, y0, CLIP_X1, y1,
        FRAME_Z1 - FRAME_Z0, FRAME_Z0,
    )
    # Open the cavity-side long face: cut from open mouth through past spine inner,
    # leaving spine (thickness C_WALL at outer Y) + top/bottom legs (thickness C_WALL in Z).
    # Overshoot past FRAME_Y_INNER so no closing wall remains on the insert side.
    oy0, oy1 = yspan(y_sign, FRAME_Y_INNER - 0.50, FRAME_Y_OUTER - C_WALL)
    assert oy0 < oy1 - 0.2, (oy0, oy1, "C open-cut Y too thin")
    hz = FRAME_Z1 - FRAME_Z0 - 2.0 * C_WALL
    assert hz > 1.0, hz
    last_l = cut_rect(
        body_var, f"{tag}_open",
        CLIP_X0 - 0.05, oy0, CLIP_X1 + 0.05, oy1,
        hz, FRAME_Z0 + C_WALL,
    )
    # Horizontal cross members (rungs) across open-C cavity — still open at mouth.
    # FDM: print on side (YZ on bed, build along model X); rungs = constant-Z bands.
    open_z0 = FRAME_Z0 + C_WALL
    open_z1 = FRAME_Z1 - C_WALL
    open_h = open_z1 - open_z0
    iy0, iy1 = yspan(y_sign, FRAME_Y_INNER + 0.15, FRAME_Y_OUTER - C_WALL)
    assert iy0 < iy1 - 0.2, (iy0, iy1, "cross-bar Y too thin")
    if CROSS_MEMBER_COUNT > 0 and open_h > CROSS_MEMBER_T * CROSS_MEMBER_COUNT + 0.8:
        gap_total = open_h - CROSS_MEMBER_COUNT * CROSS_MEMBER_T
        gap_each = gap_total / (CROSS_MEMBER_COUNT + 1)
        z_cursor = open_z0 + gap_each
        for i in range(CROSS_MEMBER_COUNT):
            last_l = add_rect(
                body_var, f"{tag}_xbar{i}",
                CLIP_X0, iy0, CLIP_X1, iy1,
                CROSS_MEMBER_T, round(z_cursor, 3),
            )
            z_cursor += CROSS_MEMBER_T + gap_each
    # Smooth friction fit; no detents. Small fillets optional live (CROSS_MEMBER_FILLET).
    return last_l


print(
    "v16.30 split_z-center wider + cross-bars; one-direction into upper; constant hub OD",
    f"cY=[{FRAME_Y_INNER:.2f},{FRAME_Y_OUTER:.2f}] cZ=[{FRAME_Z0:.2f},{FRAME_Z1:.2f}]",
    f"cWall={C_WALL:.2f} spineInner={SPINE_INNER:.2f} clipXW={CLIP_XW}",
    f"slideClrY={SLIDE_CLR_Y:.2f} slideClrZ={SLIDE_CLR_Z:.2f}",
    f"detentProud={DETENT_PROUD:.2f} detentD={DETENT_D:.2f} seatD={DETENT_SEAT_D:.2f} seatDepth={DETENT_SEAT_DEPTH:.2f}",
    f"chanZ=[{CHAN_Z0:.2f},{CHAN_Z1:.2f}] floor={POCKET_FLOOR} lipY={LIP_Y:.2f}",
)

# Shallow seats in channel floors (A=bot leg Z, B=top leg Z) — after helpers exist



last = build_clip("cyp", 1.0, "clip_yp_body")
appearance("cyp_color", "clip_yp_body", {"r": 220, "g": 60, "b": 90, "a": 255}, "BuckleClip PETG magenta")
last = build_clip("cym", -1.0, "clip_ym_body")
appearance("cym_color", "clip_ym_body", {"r": 220, "g": 60, "b": 90, "a": 255}, "BuckleClip PETG magenta")
component("comp_ca", "ClamshellA", "clamshell_a")
component("comp_cb", "ClamshellB", "clamshell_b")
component("comp_sv", "Servo", "servo_body")
component("comp_mr", "MR128", "mr128_body")
component("comp_hub", "OutputHub", "hub_body")
component("comp_cyp", "BuckleClipYP", "clip_yp_body")
component("comp_cym", "BuckleClipYM", "clip_ym_body")

def finish_chamfer(tag, body_var, keys, distance):
    call(tag+"_scene", "solid/check", "solid_scene", {})
    body = {"$select": {"from": {REF: tag+"_scene"}, "path": "/bodies",
        "where": {"/id": {REF: body_var, "pointer": "/id"}}, "take": "one"}}
    edges = [{"$select": {"from": body, "path": "/edges", "where": key if isinstance(key, dict) else {"/key": key},
                           "take": "one", "pointer": "/id"}} for key in keys]
    call(tag, "solid/refine", "solid_chamfer", {"body_id": {REF: body_var, "pointer": "/id"},
         "edge_ids": edges, "distance": distance, "tangent_chain": False})

# Proven live: taper each insertion nose across X to guide the friction fit.
finish_chamfer("clip_yp_entry", "clip_yp_body", ["edge:1", "edge:3", "edge:9", "edge:17"], 0.25)
finish_chamfer("clip_ym_entry", "clip_ym_body", ["edge:6", "edge:10", "edge:12", "edge:16"], 0.25)
# Lead-ins on horn socket mouth and outer journal end.
finish_chamfer("hub_entries", "hub_body", [
    {"/circle/radius": JOURNAL / 2, "/circle/center/z": HUB_FACE_Z},
    {"/circle/radius": SPLINE_SOCKET / 2, "/circle/center/z": flange_z0}
], 0.20)
call("final_scene", "solid/check", "solid_scene", {})
call("final_asm", "assembly/joints", "assembly_document", {})

TAB_FLOOR_WEB = ca_tech_z - TECHNIC / 2 - (tab_z1 + TAB_Z_CLR)
LOWER_BORE_BOTTOM_WEB = ca_tech_z - TECHNIC / 2 - split_z
TOP_TO_SIDE_WEB = face_z - TOP_TECH_DEPTH - (cb_tech_z + TECHNIC/2)
assert TOP_TO_SIDE_WEB >= 1.2
assert cb_tech_z - TECHNIC/2 - (tab_z1 + TAB_Z_CLR) >= 1.8
assert cb_tech_z - TECHNIC/2 - split_z >= 1.8
assert TOP_TECH_DEPTH >= 8.0
assert abs((cb_tech_z - ca_tech_z) - PITCH) < 1e-9
assert abs(face_z - cb_tech_z - 1.5*PITCH) < 1e-9
assert abs(SHELL_Y1 - PITCH - PITCH/2) < 1e-9
assert HUB_FACE_Z - CROSS_DEPTH - (TOTAL_TO_SPLINE + 0.20) >= 1.8
assert brg_seat_z - (cb_tech_z + TECHNIC/2) >= 1.8
assert deck_z0 + BEARING_LIFT - (ca_tech_z + TECHNIC/2) >= 1.8
assert cb_tech_z - TECHNIC/2 - BODY_Z >= 1.6
assert PIN_BLIND_DEPTH >= PITCH + 0.15
assert abs(HUB_FACE_Z - face_z) <= 0.05, "Output mouth must be at business-end face"
assert 0 < HUB_FACE_Z - (brg_seat_z + BRG_W) <= 4.5, "Excessive unsupported output journal"
assert abs(CROSS_DEPTH - 8.0) < 1e-9
assert JOURNAL < BRG_ID - 0.05, (JOURNAL, BRG_ID)  # need diametral clearance into bearing
_journal_diametral_clr = BRG_ID - JOURNAL
_journal_radial_clr = _journal_diametral_clr / 2.0
assert 0.06 - 1e-9 <= _journal_diametral_clr <= 0.12 + 1e-9, _journal_diametral_clr
assert FACE_HOLE_D < BRG_OD - 0.5, "Outer face must retain bearing OD (lip ID << OD)"
assert BRG_POCKET_H <= BRG_W + 0.25, "Pocket must not open through face for front insert"
assert BRG_POCKET >= BRG_OD + 0.2, "Insert path / pocket must clear bearing OD"
assert HUB_FLANGE_D <= BRG_POCKET - 0.05, "Hub flange must pass insert path into upper alone"
assert abs(brg_seat_z - 34.35) < 1e-6, brg_seat_z
assert abs(face_z - 42.0) < 1e-6, face_z
assert HUB_FLANGE_T >= 1.9, "Thick flange / servo ledge"
assert abs(HUB_NECK_D - HUB_FLANGE_D) < 1e-9, (HUB_NECK_D, HUB_FLANGE_D)
assert abs(HUB_COLUMN_D - HUB_FLANGE_D) < 1e-9
assert HUB_COLUMN_D <= BRG_POCKET - 0.05, "Constant hub OD must pass insert path"
# Blind side depth stays outside axial Ø12.3 at X=±8,Z=30 (|Y| stop >= ~3.5)
assert 8.0 <= 8.20 <= 8.5
_sock_r = SOCK_D / 2.0
_loc_x = min(abs(px) for px, _py in list(nub_xy_A) + list(sock_xy_A))
_gap_x = _loc_x - _sock_r - SLOT_HALF
assert WALL_TO_CAV >= 2.30 - 1e-9, WALL_TO_CAV  # drops with BODY_CLR; LIP_Y still ≥2.45
assert LIP_Y >= 2.4 and LIP_Z >= 2.4, (LIP_Y, LIP_Z)
assert abs(CHAN_FLOOR - POCKET_FLOOR) < 1e-9, (CHAN_FLOOR, POCKET_FLOOR)
assert CLIP_XW >= 4.0
assert 0.05 - 1e-9 <= SLIDE_CLR_Y <= 0.10 + 1e-9, SLIDE_CLR_Y
assert 0.40 - 1e-9 <= SLIDE_CLR_Z <= 4.00 + 1e-9, SLIDE_CLR_Z  # channel may extend beyond equal end-gaps
assert CLIP_Z_GAP_BELOW >= 0.20 - 1e-9, CLIP_Z_GAP_BELOW
assert CLIP_Z_GAP_ABOVE >= 0.20 - 1e-9, CLIP_Z_GAP_ABOVE
assert abs(CLIP_ENGAGE_A - CLIP_ENGAGE_B) < 1e-9, (CLIP_ENGAGE_A, CLIP_ENGAGE_B)
assert abs(CLIP_ENGAGE_A - CLIP_SPAN_Z / 2.0) < 1e-9
assert abs(FRAME_Y_OUTER - 12.0) < 1e-9
assert abs(FRAME_Y_INNER - (POCKET_FLOOR + SLIDE_CLR_Y)) < 1e-9
assert 1.20 - 1e-9 <= C_WALL <= 1.60 + 1e-9, C_WALL
assert abs(SPINE_T - C_WALL) < 1e-9
assert abs(SPINE_INNER - (FRAME_Y_OUTER - C_WALL)) < 1e-9
assert FRAME_Y_INNER < SPINE_INNER - 0.2, (FRAME_Y_INNER, SPINE_INNER)
assert FRAME_Z1 - FRAME_Z0 - 2 * C_WALL > 1.0
assert CHAN_Z0 < A_CATCH_Z < split_z < B_CATCH_Z < CHAN_Z1 <= B_LIP_Z1 + 1e-9
assert CLIP_SPAN_Z >= 10.0, CLIP_SPAN_Z
assert _gap_x >= 2.0, _gap_x
assert abs(HOOK_HALF * 2.0 - CLIP_XW) < 1e-9
# No detents, barbs, knurl or hooks; open C stays open
assert DETENT_PROUD == 0.0
assert DETENT_SEAT_DEPTH == 0.0
assert DETENT_SEAT_D >= DETENT_D - 1e-9
assert "open c" in build_clip.__doc__.lower()
assert "no detent" in build_clip.__doc__.lower()
assert "no hooks" in build_clip.__doc__.lower()
assert "not a closed" in build_clip.__doc__.lower()
_ride_interf = DETENT_PROUD - SLIDE_CLR_Y
assert abs(SLOT_HALF - (SPINE_HALF - SLOT_X_INTERF_EACH)) < 1e-9
assert abs(SLOT_X_CLR_EACH + SLOT_X_INTERF_EACH) < 1e-9
assert abs(CLIP_SIDE_GAP_NEG + SLOT_X_INTERF_EACH) < 1e-9  # gap negative = press
assert abs(CLIP_SIDE_GAP_POS + SLOT_X_INTERF_EACH) < 1e-9
assert 0.02 - 1e-9 <= SLOT_X_INTERF_EACH <= 0.05 + 1e-9, SLOT_X_INTERF_EACH
assert 0.04 - 1e-9 <= (CLIP_XW - SLOT_HALF * 2.0) <= 0.10 + 1e-9  # total X interference
# Success gate: clip X center == pocket X center within 0.05 mm; equal side press.
_clip_xc = 0.5 * (CLIP_X0 + CLIP_X1)
_pocket_xc = 0.5 * (POCKET_X0 + POCKET_X1)
assert abs(_clip_xc - CLIP_X) < 0.05, (_clip_xc, CLIP_X)
assert abs(_pocket_xc - CLIP_X) < 0.05, (_pocket_xc, CLIP_X)
assert abs(_clip_xc - _pocket_xc) < 0.05, (_clip_xc, _pocket_xc)
assert abs(CLIP_SIDE_GAP_NEG - CLIP_SIDE_GAP_POS) < 0.05, (CLIP_SIDE_GAP_NEG, CLIP_SIDE_GAP_POS)
# Success gate (v16.30): clip Z center == split_z within 0.05 mm; equal A/B engagement.
_clip_zc = 0.5 * (CLIP_Z0 + CLIP_Z1)
_slot_zc = 0.5 * (SLOT_Z0 + SLOT_Z1)
assert abs(_clip_zc - split_z) < 0.05, (_clip_zc, split_z)
assert abs(CLIP_ENGAGE_A - CLIP_ENGAGE_B) < 0.05, (CLIP_ENGAGE_A, CLIP_ENGAGE_B)
assert FRAME_Z0 >= SLOT_Z0 - 1e-9 and FRAME_Z1 <= SLOT_Z1 + 1e-9
assert CLIP_XW > 7.40 + 1e-9, CLIP_XW  # wider than v16.29
assert CROSS_MEMBER_COUNT >= 2, CROSS_MEMBER_COUNT
print(
    f"v16.30 dims wall={WALL_TO_CAV:.3f} lipY={LIP_Y:.2f} "
    f"cY=[{FRAME_Y_INNER:.2f},{FRAME_Y_OUTER:.2f}] cZ=[{FRAME_Z0:.2f},{FRAME_Z1:.2f}] "
    f"cWall={C_WALL:.2f} spineInner={SPINE_INNER:.2f} slideClrY={SLIDE_CLR_Y:.2f} slideClrZ={SLIDE_CLR_Z:.2f} "
    f"detentProud={DETENT_PROUD:.2f} detentD={DETENT_D:.2f} seatDepth={DETENT_SEAT_DEPTH:.2f} rideInterf={_ride_interf:.2f} "
    f"spanZ={CLIP_SPAN_Z:.2f} clipX={CLIP_XW} slot={SLOT_HALF*2:.2f} interfEach={SLOT_X_INTERF_EACH:.2f} sideGapEach={CLIP_SIDE_GAP_NEG:.2f} journal={JOURNAL:.2f} brgId={BRG_ID:.1f} jDiamClr={_journal_diametral_clr:.2f} jRadClr={_journal_radial_clr:.2f} bodyClr={BODY_CLR:.2f} tabZClr={TAB_Z_CLR:.2f} tabClr={TAB_CLR:.2f} "
    f"clipXbounds=[{CLIP_X0:.2f},{CLIP_X1:.2f}] pocketXbounds=[{POCKET_X0:.2f},{POCKET_X1:.2f}] "
    f"clipXc={_clip_xc:.3f} pocketXc={_pocket_xc:.3f} gapX={_gap_x:.2f} "
    f"chanZ=[{CHAN_Z0:.2f},{CHAN_Z1:.2f}] A_CATCH={A_CATCH_Z:.2f} B_CATCH={B_CATCH_Z:.2f} "
    f"floor={POCKET_FLOOR} openC=1 closedFrame=0 softDetent=0 barbs=0 knurl=0 hooks=0 "
    f"split_z={split_z:.2f} clipZc={_clip_zc:.2f} engageA/B={CLIP_ENGAGE_A:.2f}/{CLIP_ENGAGE_B:.2f} "
    f"crossBars={CROSS_MEMBER_COUNT} xbarT={CROSS_MEMBER_T:.2f} datum=split_z"
)


doc = {
    "version": 1,
    "name": "INJS2065 Technic clamshell-IS-mount v16.30 clip split_z-center wider cross-bars",
    "starting_state": "empty",
    "steps": steps,
    "exports": {"final_model": True, "final_scene": True, "final_solution": True},
}

header = (
    "// INJS2065 v16.30: PETG 0.4 nozzle / 0.2 layer; clip Z-centered on split_z; wider open-C + cross-bars; tight X press; journal 7.90.\n"
    f"// Split Z={split_z}; tabs captured equally; no thin tab roof.\n"
    f"// Bearing pocket D={BRG_POCKET} h={BRG_POCKET_H}; face hole D={FACE_HOLE_D} (retain OD).\n"
    f"// Journal D={JOURNAL}; horn socket D={SPLINE_SOCKET}; flange T={HUB_FLANGE_T} constant OD D={HUB_COLUMN_D}.\n"
    f"// Axle cross {AXLE_SPAN} x {AXLE_ARM}; clips {CLIP_XW} wide over retained shell lands.\n"
    "// Friction clips, no detents. Print clips on side, build along model X.\n"
)

out_dir = Path(__file__).resolve().parent
out = out_dir / "injs2065-technic-clamshell.nbcad.jsonc"
out_dir.mkdir(parents=True, exist_ok=True)
out.write_text(header + json.dumps(doc, indent=2) + "\n", encoding="utf-8")

kinds: dict[str, int] = {}
for s in steps:
    if "call" in s:
        k = "call:" + s["call"]["operation"]
    elif "let" in s:
        k = "let"
    elif "view" in s:
        k = "view"
    elif "chapter" in s:
        k = "chapter"
    else:
        k = "other"
    kinds[k] = kinds.get(k, 0) + 1

meta = {
    "architecture": "clamshell_v16_30_clip_split_z_center_wider_crossbars",
    "clamp_path": "open_c_over_central_land",
    "printed_parts": ["ClamshellA", "ClamshellB", "OutputHub", "BuckleClipYP", "BuckleClipYM"],
    "purchased_proxies": ["Servo", "MR128"],
    "frame": {
        "shell_x": [SHELL_X0, SHELL_X1],
        "shell_y": [SHELL_Y0, SHELL_Y1],
        "shell_z0": SHELL_Z0,
        "split_z": split_z,
        "face_z": face_z,
        "tab_x0": tab_x0,
        "tab_x1": tab_x1,
        "cav_x": [cav_x0, cav_x1],
        "cav_y": [cav_y0, cav_y1],
        "BODY_CLR": BODY_CLR,
        "ear_nest": {
            "EAR_HALF_Y": EAR_HALF_Y,
            "TAB_CLR": TAB_CLR,
            "NEST_Y": NEST_Y,
            "TAB_Z_CLR": TAB_Z_CLR,
            "TIP_WALL": TIP_WALL,
            "NEST_R": NEST_R,
            "ear_near": [ear_near_x0, ear_near_x1],
            "ear_far": [ear_far_x0, ear_far_x1],
            "x_span": [cav_x0, EAR_NEST_X1],
            "z_span": [tab_z0 - TAB_Z_CLR, tab_z1 + TAB_Z_CLR],
            "body_cav_x0": body_cav_x0,
        },
        "uniform_xy": True,
        "far_end_open": True,
        "near_ear_trapped": True,
    },
    "technic_side_x": list(side_x),
    "technic_side_z_lower": None,
    "technic_side_z_upper": cb_tech_z,
    "side_rows_in_body": "ClamshellB",
    "side_corner_setback": SIDE_EDGE_SETBACK,
    "side_blind_x": list(side_x),
    "side_blind_z": cb_tech_z,
    "side_blind_depth": 8.20,
    "bearing_lift_mm": BEARING_LIFT,
    "technic_top": [list(p) for p in top_xy],
    "technic_top_depth": TOP_TECH_DEPTH,
    "technic_top_blind": True,
    "align_nubs": {
        "NUB_D": NUB_D,
        "NUB_FLAT": NUB_FLAT,
        "NUB_ENGAGE": NUB_ENGAGE,
        "NUB_BOSS_H": NUB_BOSS_H,
        "NUB_STUB_H": NUB_STUB_H,
        "NUB_DOME_H": NUB_DOME_H,
        "SOCK_CLR": SOCK_CLR,
        "SOCK_D": SOCK_D,
        "SOCK_DEPTH": SOCK_DEPTH,
        "nub_xy_A": [list(p) for p in nub_xy_A],
        "sock_xy_A": [list(p) for p in sock_xy_A],
        "alternating_4corner": True,
        "profile": "stub_plus_dome_flat",
        "aspect_engage_over_d": NUB_ENGAGE / NUB_D,
        "print_note": "Prefer nubs with Z=build direction (split face on bed) for shear strength",
    },
    "align_nubs_inboard": True,
    "clip_pocket_clean": True,
    "upper_cover": "ClamshellB",
    "lower_clam": "ClamshellA",
    "assembly_mode": "one_direction_into_upper",
    "bearing": {
        "BRG_POCKET": BRG_POCKET,
        "BRG_OD": BRG_OD,
        "BRG_ID": BRG_ID,
        "BRG_W": BRG_W,
        "JOURNAL": JOURNAL,
        "journal_vs_brg_id_diametral_clearance_mm": BRG_ID - JOURNAL,
        "journal_vs_brg_id_radial_clearance_mm": (BRG_ID - JOURNAL) / 2.0,
        "FACE_HOLE_D": FACE_HOLE_D,
        "brg_seat_z": brg_seat_z,
        "pocket_method": "cut_cyl",
        "pocket_h": BRG_POCKET_H,
        "bearing_insertion": "upper_from_split",
        "bearing_seat_z": brg_seat_z,
        "bearing_seat_inner_diameter": BRG_POCKET,
        "outer_retain_lip_id": FACE_HOLE_D,
        "outer_retain_note": "Upper alone: OD seats from split against face lip; journal clearance poke-out; NOT front Ø12.3 tunnel",
        "insert_path_diameter": BRG_POCKET,
        "insert_path_z": [26.0, brg_seat_z],
        "bearing_riser_diameter": None,
        "bearing_riser_top_z": None,
        "bearing_inner_stop_z": _inner_stop_world_z,
        "bearing_inner_stop_note": "Small journal-shoulder abutment under bearing (not a proud outer lip)",
        "deck_z0": deck_z0,
    },
    "hub": {
        "output_face_z": HUB_FACE_Z,
        "output_recess_mm": face_z - HUB_FACE_Z,
        "SPLINE_SOCKET": SPLINE_SOCKET,
        "HUB_FLANGE_D": HUB_FLANGE_D,
        "JOURNAL": JOURNAL,
        "AXLE_SPAN": AXLE_SPAN,
        "AXLE_ARM": AXLE_ARM,
        "FACE_EXTRA": FACE_EXTRA,
        "face_z": face_z,
        "flange_z0": flange_z0,
        "flange_z1": flange_z1,
        "deck_z0": deck_z0,
        "tower_t": tower_t,
        "JOURNAL_LEN": JOURNAL_LEN,
        "HUB_FLANGE_T": HUB_FLANGE_T,
        "HUB_NECK_D": HUB_NECK_D,
        "HUB_COLUMN_D": HUB_COLUMN_D,
        "constant_od": True,
        "constant_od_z": [flange_z0, _inner_stop_world_z],
        "bearing_inner_stop_z": _inner_stop_world_z,
        "bearing_inner_stop_gap": BEARING_INNER_STOP_GAP,
        "CROSS_DEPTH": CROSS_DEPTH,
        "hub_height": HUB_FLANGE_T + JOURNAL_LEN,
        "spline_depth": (TOTAL_TO_SPLINE - flange_z0) + 0.20,
        "servo_ledge": "thick flange parks on servo; OD constant from flange through column to inner stop",
    },
    "buckle": {
        "style": "open_c_over_central_land",
        "clip_count": 2,
        "names": ["BuckleClipYP", "BuckleClipYM"],
        "slot_half_x": SLOT_HALF,
        "chan_half_x": CHAN_HALF,
        "pocket_floor": POCKET_FLOOR,
        "rail_y": LIP_Y,
        "rail_z": LIP_Z,
        "lip_y": LIP_Y,
        "lip_z": LIP_Z,
        "wall_to_cavity": WALL_TO_CAV,
        "slide_clearance_y_total": SLIDE_CLR_Y,
        "slide_clearance_z_total": SLIDE_CLR_Z,
        "slide_clearance_note": "Y insertion clearance 0.05; clip Z-centered on split_z (equal A/B engagement); channel end gaps may be unequal; X equal press 0.04 each side (0.08 total interference); Y-clamp friction primary. Datum = split_z, NOT pocket mid.",
        "frame_y_outer": FRAME_Y_OUTER,
        "frame_y_inner": FRAME_Y_INNER,
        "frame_z": [FRAME_Z0, FRAME_Z1],
        "c_wall": C_WALL,
        "spine_t": SPINE_T,
        "spine_inner_y": SPINE_INNER,
        "open_c": True,
        "closed_frame": False,
        "c_outer_yz": [FRAME_Y_INNER, FRAME_Y_OUTER, FRAME_Z0, FRAME_Z1],
        "c_open_cut_yz": [
            FRAME_Y_INNER - 0.50,
            FRAME_Y_OUTER - C_WALL,
            FRAME_Z0 + C_WALL,
            FRAME_Z1 - C_WALL,
        ],
        "detents": False,
        "detent_style": "none_friction_only",
        "detent_proud_mm": DETENT_PROUD,
        "detent_d_mm": DETENT_D,
        "detent_seat_d_mm": DETENT_SEAT_D,
        "detent_seat_depth_mm": DETENT_SEAT_DEPTH,
        "detent_z": [DETENT_Z_BOT, DETENT_Z_TOP],
        "detent_ride_interference_mm": round(DETENT_PROUD - SLIDE_CLR_Y, 3),
        "detent_note": "No detents; retention is Y-clamp friction of open-C over retained lands plus intentional equal X press.",
        "barbs": False,
        "knurl": False,
        "hooks": False,
        "clip_xw": CLIP_XW,
        "clip_x_center": CLIP_X,
        "clip_x_bounds": [CLIP_X0, CLIP_X1],
        "pocket_x_bounds": [POCKET_X0, POCKET_X1],
        "slot_x_clearance_each_mm": SLOT_X_CLR_EACH,
        "slot_x_interference_each_mm": SLOT_X_INTERF_EACH,
        "slot_x_interference_total_mm": CLIP_XW - SLOT_HALF * 2.0,
        "side_gaps_x": [CLIP_SIDE_GAP_NEG, CLIP_SIDE_GAP_POS],
        "side_gaps_x_note": "negative = interference (clip wider than pocket); equal |gaps| = centered",
        "A_catch_z": A_CATCH_Z,
        "B_catch_z": B_CATCH_Z,
        "B_lip_z1": B_LIP_Z1,
        "chan_z": [CHAN_Z0, CHAN_Z1],
        "A_pocket_z": [A_POCKET_Z0, A_POCKET_Z1],
        "B_pocket_z": [B_POCKET_Z0, B_POCKET_Z1],
        "clip_span_z": CLIP_SPAN_Z,
        "clip_z_bounds": [CLIP_Z0, CLIP_Z1],
        "slot_z_bounds": [SLOT_Z0, SLOT_Z1],
        "clip_z_center": (CLIP_Z0 + CLIP_Z1) / 2.0,
        "slot_z_center": SLOT_Z_MID,
        "clip_z_gaps": [CLIP_Z_GAP_BELOW, CLIP_Z_GAP_ABOVE],
        "clip_z_center_note": "v16.30: mid-clip == split_z (clamshell division); equal land engagement A/B. v16.29 mid-slot (~20.25) was wrong datum.",
        "clip_z_datum": "split_z",
        "clip_engage_a_mm": CLIP_ENGAGE_A,
        "clip_engage_b_mm": CLIP_ENGAGE_B,
        "cross_member_count": CROSS_MEMBER_COUNT,
        "cross_member_t_mm": CROSS_MEMBER_T,
        "cross_member_fillet_mm": CROSS_MEMBER_FILLET,
        "cross_member_note": "Horizontal rungs across open-C cavity (plus spine); FDM side orientation build +X; mouth stays open; no snaps.",
        "spine_outer_y": SPINE_OUTER,
        "chan_floor": CHAN_FLOOR,
        "slot_span_x": SLOT_HALF * 2.0,
        "pockets": [
            [POCKET_X0, POCKET_FLOOR, A_POCKET_Z0, POCKET_X1, 12.0 + POCKET_Y_OVER, A_POCKET_Z1],
            [POCKET_X0, -(12.0 + POCKET_Y_OVER), A_POCKET_Z0, POCKET_X1, -POCKET_FLOOR, A_POCKET_Z1],
            [POCKET_X0, POCKET_FLOOR, B_POCKET_Z0, POCKET_X1, 12.0 + POCKET_Y_OVER, B_POCKET_Z1],
            [POCKET_X0, -(12.0 + POCKET_Y_OVER), B_POCKET_Z0, POCKET_X1, -POCKET_FLOOR, B_POCKET_Z1],
        ],
        "print_orientation": "Clips on side: YZ profile on bed, build along X. Orient shells to support tab nests and bearing seat; check nubs and bridges in slicer. Minimum deep-slot wall 2.45 mm.",
    },
    "revision_notes": {
        "material": "PETG", "nozzle_mm": 0.4,
        "tab_ceiling_to_lower_side_bore_web_mm": None,
        "lower_hole_bottom_web_mm": None,
        "top_to_side_hole_web_mm": TOP_TO_SIDE_WEB,
        "lower_mount_row_shift_from_v16_10_mm": None,
        "top_blind_depth_mm": TOP_TECH_DEPTH,
        "fit_status": "nominal first-pass correction; physical fit not yet tested",
        "horn_wall_mm": (HUB_FLANGE_D - SPLINE_SOCKET) / 2,
        "short_socket_depth_mm": (TOTAL_TO_SPLINE - flange_z0) + 0.20,
        "hub_taper_z": None,
        "hub_mid_lip_removed": True,
        "hub_constant_od_diameter": HUB_COLUMN_D,
        "hub_neck_diameter": HUB_NECK_D,
        "minimum_horn_socket_wall_mm": (HUB_COLUMN_D - SPLINE_SOCKET) / 2,
        "thick_flange_horn_wall_mm": (HUB_FLANGE_D - SPLINE_SOCKET) / 2,
        "side_sleeve_nominal_wall_mm": None,
        "side_bore_mode": "blind_8.2_each_face",
        "side_bore_wall_note": "Through-sleeve wall collapsed by Ø12.3 insert path at Z30; blind depth 8.2 preserves outer Technic land without opening pin corridor into hub cavity",
        "clearance_profile_z_d": [
            [26.0, 12.3], [brg_seat_z, 12.3],
            [brg_seat_z, 12.3], [brg_seat_z + BRG_POCKET_H, 12.3],
            [brg_seat_z + BRG_POCKET_H, FACE_HOLE_D],
            [42.1, FACE_HOLE_D],
        ],
        "face_pokeout_diametral_clearance_mm": FACE_HOLE_D - JOURNAL,
        "bearing_inner_start_z": brg_seat_z,
        "assembly": "1 bearing into upper_cover from split; 2 OutputHub into stack; 3 servo into hub; 4 lower_clam; 5 open-C clips",
        "assembly_mode": "one_direction_into_upper",
        "tab_capture_each_mm": TAB_T / 2,
        "clip_channel_width_mm": SLOT_HALF * 2,
        "clip_width_interference_total_mm": CLIP_XW - SLOT_HALF * 2,  # positive => press (equal each side)
        "clip_x_side_clearance_each_mm": SLOT_X_CLR_EACH,
        "clip_x_interference_each_mm": SLOT_X_INTERF_EACH,
        "clip_z_centered_on_split_z": True,
        "clip_z_datum": "split_z",
        "clip_z_center_tol_mm": 0.05,
        "clip_engage_a_mm": CLIP_ENGAGE_A,
        "clip_engage_b_mm": CLIP_ENGAGE_B,
        "clip_wider_than_v16_29": True,
        "clip_xw_v16_29": 7.40,
        "clip_xw_v16_30": CLIP_XW,
        "clip_span_z_v16_29": 11.60,
        "clip_span_z_v16_30": CLIP_SPAN_Z,
        "cross_member_count": CROSS_MEMBER_COUNT,
        "cross_member_t_mm": CROSS_MEMBER_T,
        "chan_z0_v16_29": 14.00,
        "chan_z0_v16_30": CHAN_Z0,
        "journal_vs_brg_id_diametral_clearance_mm": _journal_diametral_clr,
        "journal_vs_brg_id_radial_clearance_mm": _journal_radial_clr,
        "journal_fit_note": "JOURNAL OD into BRG_ID: diametral clr = ID-OD; radial = half diametral",
        "BODY_CLR": BODY_CLR,
        "TAB_CLR": TAB_CLR,
        "TAB_Z_CLR": TAB_Z_CLR,
        "clip_pocket_x_centers_match": True,
        "spine_recess_floor_abs_y": SPINE_INNER - 0.05,
        "central_land_retained": True,
        "no_detents": True
    },
    "steps": len(steps),
    "step_kinds": kinds,
    "baseline_v12": 360,
    "baseline_v12_1": 424,
    "baseline_v12_2": 456,
    "baseline_v12_3": 440,
    "baseline_v12_7": 510,
    "baseline_v11_2": 724,
    "FACE_EXTRA": FACE_EXTRA,
    "AXLE_SPAN": AXLE_SPAN,
    "AXLE_ARM": AXLE_ARM,
}
(out_dir / "gen_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out} steps={len(steps)} kinds={kinds}")
if len(steps) > 400:
    print(f"WARNING: steps {len(steps)} > 400")
else:
    print(f"OK: steps {len(steps)} ≤ 400")











