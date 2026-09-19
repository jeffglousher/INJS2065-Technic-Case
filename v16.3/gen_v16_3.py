#!/usr/bin/env python3
"""INJS2065 Technic CLAMSHELL-IS-MOUNT v16.2 — square inward tooth, straight 35° lead.

v16.2 changes ONLY the buckle clip (shell, ledges, nubs, bearing, hub unchanged):
- No cylinder lead, no root gusset, no radii on the clip.
- Square inward catch: 0.60 mm past the pocket floor, HOOK_Z=2.20 flat retention.
- 35° trapezoid lead in the YZ profile. Sharp step, not a fillet.
- Knurl ribs only on the min-Z and max-Z pinch faces, along X, |Y|<=12.
- Outer face flush at |Y|=12. Grid snap stays off while sketch numbers are entered.

Keep locked: loft nubs Ø2.2/engage 0.70, ear trap, shell ±12, BODY_CLR,
axle 5×2, bearing pocket, Injora dims, 4-corner alternating blind socks.
Flush outer face |Y|=12. Exactly BuckleClipYP + BuckleClipYM. Spine ≥1.6.
Wall pocket-floor → cavity ≥3.0. Do not shrink the bar (Z span ≥ v16's 8.30).

v16.1 (Jeff: v16's B catch is a 0.67 mm lip bridging 4.70 mm):
- The lip the hook bears on is a real rail, ≥2.4 mm. Not the main wall.
- A: side rails, center open for the spine, supported (split on the bed).
- B: full-width rail outboard of the pocket, printed as solid layers (no bridge).

v14 (Jeff rejected v13.1 deep seat ~0.05 mm wall):
- DELETE deep SEAT_RECESS toward cavity (no Y≈6.6 pocket)
- Shallow outer grooves GROOVE_DEPTH=2.0 → floor |Y|=10.0; wall to cav 3.45 mm
- Separate U-clip straddles A|B split; hooks catch ledges; flex in clip
- CATCH_UNDER~0.55 PETG hold; web Z-interference clamps A against B
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# --- Injora INJS2065 ---
BODY_X, BODY_Y, BODY_Z = 23.0, 13.0, 25.8
TAB_SPAN, TAB_T, TAB_FROM_BASE = 29.8, 2.5, 17.0
SPLINE_FROM_EDGE = 5.8
BODY_CLR = 0.05  # friction PLA/PETG (was 0.10 slip)
BRG_OD, BRG_ID, BRG_W = 12.0, 8.0, 3.5
BRG_POCKET = 12.10
BRG_LEAD = 0.8
SHOULDER_T = 1.2
FACE_EXTRA = 5.5  # shortened vs v12.5 (was 8.0); still gap≥1.5
JOURNAL = 7.88
TECHNIC, PITCH = 5.05, 8.0
HUB_FLANGE_D = 10.6
HUB_FLANGE_T = 2.0
SPLINE_SOCKET = 6.20
AXLE_SPAN = 5.00
AXLE_ARM = 2.00
CROSS_DEPTH = 5.5
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

# External straddling U-clip on shallow outer grooves (v14) — NO deep seat
CLIP_W = 8.50              # groove / clip width in X (8–9 mm)
GROOVE_DEPTH = 2.00        # max 2.2; floor at |Y|=SHELL_Y-DEPTH=10.0
LEDGE_PROUD = 0.85         # rail from groove floor toward outer
LEDGE_T = 1.75             # Z thickness of catch shoulder
LEDGE_X_INSET = 0.35       # ledge narrower than groove → side clearance
# U-clip arms (flex in clip; print flat so bend is in XY)
TAB_W = 6.40               # arm / hook width in X (< CLIP_W)
ARM_T = 0.55               # arm wall thickness in Y (bend direction)
WEB_T = 1.00               # outer web thickness in Y (flush outer face)
CATCH_UNDER = 0.55         # PETG ~0.4–0.8; real hold (was soft 0.22)
CATCH_Z = 0.55             # undercut Z band
LEAD_ANGLE_DEG = 35.0      # FDM snap lead-in 30–40°
LEAD_IN_Y = CATCH_Z / math.tan(math.radians(LEAD_ANGLE_DEG))  # ~0.785
Z_HOOK_CLEAR = 0.10
FACE_OUTER_PROUD = 0.0     # FLUSH with SHELL_Y=±12 when seated
FACE_CLEAR_Y = 0.12        # air between web inner and ledge outer when seated
HOOK_DEPTH = 0.70          # Z height of hook body below/above ledge
FILLET_R = 0.40            # outer vertical corners
ROOT_FILLET_R = 0.0        # v14.1: no box stub roots (was 0.30 blob)
FACE_TEX_PROUD = 0.0       # v14.1: clean flush outer (no thin rib slivers)
FACE_TEX_N = 0
FACE_TEX_W = 0.35
FACE_TEX_EDGE = 0.60
WEB_OVERLAP = 0.08         # hook solid overlaps into web for manifold union
ROOT_BLEND_R = 0.35        # smooth quarter-cyl arm root (not a box stub)
# Clamp: free span between A-hook top and B-hook bottom undersized vs ledge gap
CLAMP_Z_INTERF = 0.20      # clip squeezes A↑B↓ across split
# Derived
GROOVE_FLOOR = 12.0 - GROOVE_DEPTH  # 10.0; wall to cav = 10.0-6.55 = 3.45
CATCH_INTERF = CATCH_UNDER
# Back-compat names used sparsely in comments / meta
SEAT_RECESS = GROOVE_DEPTH  # NOT a deep seat — alias for groove depth only
FACE_T = WEB_T
ROOT_EMBED = 0.0
TAB_BEAM_T = ARM_T
TAB_LEN = 4.0              # Z half-arm target for L/t (~4.0/0.55≈7.3)
WALL = 2.6
GAP = BODY_CLR

# Shaft-near flange EAR nest (A). Real ears = body width ±6.50, not ±6.15 bar.
EAR_HALF_Y = BODY_Y / 2.0  # 6.50
TAB_CLR = 0.12             # /side to ear
NEST_Y = EAR_HALF_Y + TAB_CLR  # 6.62
TAB_Z_CLR = 0.10
TIP_WALL = 0.40             # solid tip wall beyond ear tip
NEST_R = 0.35               # gentle ear-corner fillet (not R0.8 bar cradle)
EAR_BLEND = 0.25            # pocket slightly into body at x0
SLOT_D = 3.80               # optional U-slot Ø on ears

# Over/under finger scoops (axis // X) — light grip near grooves (≤GROOVE_DEPTH)
OU_R = 2.80
OU_DEPTH = 1.60            # stays outboard of groove floor → cav wall intact
OU_HALF_X = 3.60
OU_Z_A = 15.40             # below A ledge
OU_Z_B = 25.20             # above B ledge

x0 = -SPLINE_FROM_EDGE          # -5.8
x1 = BODY_X - SPLINE_FROM_EDGE  # +17.2
y0, y1 = -BODY_Y / 2.0, BODY_Y / 2.0
OVERHANG = (TAB_SPAN - BODY_X) / 2.0  # 3.4
tab_x0 = x0 - OVERHANG          # -9.2
tab_x1 = x1 + OVERHANG          # +20.6
tab_z0 = TAB_FROM_BASE          # 17.0
tab_z1 = TAB_FROM_BASE + TAB_T  # 19.5
split_z = tab_z1 + 0.50         # 20.0

# Short uniform brick — BOTH halves. Far body/tab exit +X at 12.
SHELL_X0, SHELL_X1 = -12.0, 12.0
SHELL_Y0, SHELL_Y1 = -12.0, 12.0
SHELL_Z0 = 8.0

cav_y0, cav_y1 = y0 - GAP, y1 + GAP          # ±6.55 with BODY_CLR=0.05
# Near ear footprint (shaft end); far ear exits shell at +X
ear_near_x0, ear_near_x1 = tab_x0, x0        # -9.2 → -5.8
ear_far_x0, ear_far_x1 = x1, tab_x1          # 17.2 → 20.6
cav_x0 = ear_near_x0 - TIP_WALL              # -9.6 tip wall
cav_x1 = SHELL_X1 + 0.50                     # 12.5 open +X (far ear/body out)
body_cav_x0 = x0 - 0.20                      # body friction cavity starts near x0
EAR_NEST_X1 = ear_near_x1 + EAR_BLEND        # -5.55 pocket into body blend

flange_z0 = BODY_Z + 0.5                     # 26.3 (flange parked on servo)
flange_z1 = flange_z0 + HUB_FLANGE_T         # 28.3
deck_z0 = flange_z1 + 0.25                   # 28.55
tower_t = BRG_LEAD + BRG_W + SHOULDER_T + FACE_EXTRA  # was 13.5 → 11.0
face_z = deck_z0 + tower_t                   # was 42.05 → 39.55
brg_seat_z = deck_z0 + BRG_LEAD
JOURNAL_LEN = face_z - flange_z1             # was ~13.75 → ~11.25

CLIP_X = 0.0
ca_tech_z = 14.0
cb_tech_z = 26.0
side_x = (-PITCH, PITCH)  # ±8
top_xy = ((PITCH, PITCH), (PITCH, -PITCH), (-PITCH, PITCH), (-PITCH, -PITCH))
# 4-corner alternating nubs on mating split (inboard of outer wall, clear of CLIP_W=8.5).
# A nubs at (+8,+9.3)&(-8,-9.3); A sockets at (+8,-9.3)&(-8,+9.3); B inverse.
# Inboard of Technic X=±8 (edge≈5.53); |x|≥5.0 clears seat±3.75+SOCK_R.
# Y toward outer wall for thick deck over Technic roof (closed blind SOCK_DEPTH).
nub_xy_A = ((8.40, 9.40), (-8.40, -9.40))
sock_xy_A = ((8.40, -9.40), (-8.40, 9.40))
# Blind top Technic: through tower deck only; stop well above split_z=20.
TOP_TECH_DEPTH = tower_t - 0.5  # 10.5 — face_z 39.55 → bottom 29.05 ≥ deck_z0+0.5

# v16.1 flush clip + thick catch rails.
# The v16 lip was CHAN_FLOOR-POCKET_FLOOR = 0.67 mm, and that shelf bridged
# the slot on B. A 2.4 mm lip will not stack under a flush 1.68 spine inside
# a 2.45 mm pocket, so the catch is a local rail (lengthen / local boss):
#   lip Y = outer face − pocket floor = 2.45 (the step, NOT the wall to the cavity)
#   lip Z = 3.00 in the direction the hook bears
# A's center stays open (floor = pocket floor, no 0.67 shelf) so the spine
# can cross. The side rails are the catch. B's rail is the uncut wall
# OUTBOARD of the pocket, so it prints as solid layers before the pocket opens.
CLIP_XW = 4.20
SPINE_HALF = CLIP_XW / 2.0                    # 2.10, bar width not reduced
CHAN_HALF = SPINE_HALF + 0.25                 # 2.35 center path through A's rail
HOOK_HALF = CHAN_HALF + 0.65                  # tooth ears only, not a bar
SLOT_HALF = HOOK_HALF + 0.35
SHOE_X = HOOK_HALF
POCKET_FLOOR = 9.55                           # |Y| deep floor; wall to cav = 3.00
CAV_Y_HALF = abs(cav_y1)                      # 6.55
WALL_TO_CAV = POCKET_FLOOR - CAV_Y_HALF
SPINE_T = 1.20                             # flex beam, not a plate
SPINE_OUTER = 12.0                            # flush — do not go proud
SPINE_INNER = SPINE_OUTER - SPINE_T           # 10.80
CHAN_FLOOR = POCKET_FLOOR                     # no shallow shelf; that WAS the 0.67 lip
LIP_Y = SPINE_OUTER - POCKET_FLOOR            # 2.45
LIP_Z = 3.00                                  # loaded section, catch face → into the rail
UNDERCUT = 0.60                       # mm past the pocket floor, into the rail
HOOK_TIP = POCKET_FLOOR + 0.18                # 9.73 shoe inner, clearance above the floor
TOOTH_Y = POCKET_FLOOR - UNDERCUT             # 8.95 inward face; steps in from the shoe
TOOTH_JOIN_Y = SPINE_INNER + 0.20          # overlaps the thin beam, no shoe
BITE_TOP = TOOTH_Y                            # inward face of the square catch
KNURL_W = 0.80
KNURL_PROUD = 0.40
KNURL_EMBED = 0.12
Z_INTERF = 0.50
HOOK_Z = 2.20
LEAD_ANGLE_DEG = 35.0
LEAD_Z = 0.70
LEAD_Y = LEAD_Z / math.tan(math.radians(LEAD_ANGLE_DEG))
ROOT_R = 0.0          # v16.2: no root radius — sharp step
ROOT_REACH = 0.42
ROOT_Z = 0.36
ARM_T = SPINE_T
ARM_INNER = SPINE_INNER
HOOK_OUTER = SPINE_OUTER
RAIL_Y = LIP_Y                                # the lip, not the wall down to the cavity
RAIL_Z = LIP_Z
ARM_SPAN = LIP_Z
STOCK_WALL_Y = LIP_Y
A_CATCH_Z = split_z - LIP_Z                   # 17.00  A's rail is [17, 20], toward the split
B_CATCH_Z = 24.20                             # B's rail starts here and runs +Z (outboard)
A_HOOK_TOP = A_CATCH_Z + Z_INTERF             # 17.50
A_TOOTH_Z0 = A_HOOK_TOP - HOOK_Z              # 15.30
B_HOOK_TOP = B_CATCH_Z + Z_INTERF             # 24.70
B_TOOTH_Z0 = B_HOOK_TOP - HOOK_Z              # 22.50
SPINE_Z0 = A_TOOTH_Z0
SPINE_Z1 = B_CATCH_Z - 0.16                   # 24.04, stays out of B's solid rail
CLIP_Z0 = A_TOOTH_Z0
CLIP_Z1 = B_HOOK_TOP
CLIP_SPAN_Z = CLIP_Z1 - CLIP_Z0               # 9.40, longer than v16's 8.30
HALF_SPAN = CLIP_SPAN_Z / 2.0
A_HOOK_BOT = A_TOOTH_Z0
B_HOOK_BOT = B_TOOTH_Z0
CLIP_X0 = -CLIP_XW / 2.0
CLIP_X1 = CLIP_XW / 2.0
SHOE_X0 = -SHOE_X
SHOE_X1 = SHOE_X
A_POCKET_Z0 = A_TOOTH_Z0 - 0.40
A_POCKET_Z1 = A_CATCH_Z
B_POCKET_Z0 = split_z - 0.08
B_POCKET_Z1 = B_CATCH_Z
A_CHAN_Z0 = A_CATCH_Z - 0.06
A_CHAN_Z1 = split_z + 0.08
B_LIP_Z1 = B_CATCH_Z + LIP_Z                  # 27.20 designed boss; shell continues, supported
# Square shoes stop so the 35° lead owns the last LEAD_Z of the pocket.
A_SHOE_Z1 = A_CATCH_Z - LEAD_Z + 0.06
B_SHOE_Z1 = B_CATCH_Z - LEAD_Z + 0.06
POCKET_Y_OVER = 0.35

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



def add_ear_nest(target: str, tag: str, z0: float, z1: float) -> str:
    """Shaft-near flange EAR pocket via Z-band cut + tip fillets.

    Body cavity (friction 23×13) is separate. Ear pocket is cut only in the
    ear Z band so floor (under) and ceiling (over) remain solid — positive
    trap. Tip wall is brick solid for x < cav_x0. Shape matches ear footprint
    (not a long R0.8 bar cradle).
    """
    x_lo, x_hi = cav_x0, EAR_NEST_X1
    ear_z0 = tab_z0 - TAB_Z_CLR
    ear_z1 = tab_z1 + TAB_Z_CLR
    ear_h = ear_z1 - ear_z0
    # Exact ear envelope + clr (Y/Z). Floor below ear_z0 and ceiling above ear_z1 stay.
    last_l = cut_rect(
        target, f"{tag}_pocket",
        x_lo, -NEST_Y, x_hi, NEST_Y,
        ear_h, ear_z0,
    )
    # Gentle tip-corner fillets (small R) — keep ear-shaped, not bar cradle
    if NEST_R > 0.15:
        r = NEST_R
        tip_x = cav_x0 + r
        # Local pads then scoop so tip corners are rounded inside pocket
        last_l = add_rect(
            target, f"{tag}_cyp",
            cav_x0, NEST_Y - r, cav_x0 + r, NEST_Y,
            r, ear_z0,
        )
        last_l = add_rect(
            target, f"{tag}_cym",
            cav_x0, -NEST_Y, cav_x0 + r, -NEST_Y + r,
            r, ear_z0,
        )
        last_l = cut_cyl(
            target, f"{tag}_fyp",
            2.0 * r, tip_x, NEST_Y - r, r + 0.05, ear_z0 - 0.02,
        )
        last_l = cut_cyl(
            target, f"{tag}_fym",
            2.0 * r, tip_x, -(NEST_Y - r), r + 0.05, ear_z0 - 0.02,
        )
    return last_l


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

# Side Technic BEFORE seats so ±Y faces stay the outer brick walls
face_axis_let("f_ca_yp", last, "clamshell_a", 1, 1)
last = "ca_ty0"
hole(last, "clamshell_a", "f_ca_yp", [side_x[0], SHELL_Y1, ca_tech_z], TECHNIC)
face_axis_let("f_ca_ypb", last, "clamshell_a", 1, 1)
last = "ca_ty1"
hole(last, "clamshell_a", "f_ca_ypb", [side_x[1], SHELL_Y1, ca_tech_z], TECHNIC)
face_axis_let("f_ca_ym", last, "clamshell_a", 1, -1)
last = "ca_tm0"
hole(last, "clamshell_a", "f_ca_ym", [side_x[0], SHELL_Y0, ca_tech_z], TECHNIC)
face_axis_let("f_ca_ymb", last, "clamshell_a", 1, -1)
last = "ca_tm1"
hole(last, "clamshell_a", "f_ca_ymb", [side_x[1], SHELL_Y0, ca_tech_z], TECHNIC)

# v16 pockets. Channel (shallow) lets the flush spine cross the split.
# Deep pocket stops on the catch face so the rail (catch → split) stays thick.
def cut_yp_ym(shell, tag, y_floor, z0, z1, x_half=None):
    xh = SLOT_HALF if x_half is None else x_half
    h = z1 - z0
    if h <= 0.05:
        raise SystemExit(f"bad pocket {tag} h={h}")
    cut_rect(
        shell, f"{tag}_yp",
        -xh, y_floor,
        xh, SHELL_Y1 + POCKET_Y_OVER,
        h, z0,
    )
    return cut_rect(
        shell, f"{tag}_ym",
        -xh, SHELL_Y0 - POCKET_Y_OVER,
        xh, -y_floor,
        h, z0,
    )

# A: deep pocket for the tooth, then a CENTER slot only through the rail.
# Side rails ( |X| > CHAN_HALF ) stay full thickness: lip = 2.45, loaded Z = 3.00.
# Channel floor == pocket floor, so there is no 0.67 mm shelf anywhere.
last = cut_yp_ym("clamshell_a", "ca_pkt", POCKET_FLOOR, A_POCKET_Z0, A_POCKET_Z1)
last = cut_yp_ym("clamshell_a", "ca_chn", POCKET_FLOOR, A_CHAN_Z0, A_CHAN_Z1, x_half=CHAN_HALF)

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

appearance("ca_color", "clamshell_a", {"r": 40, "g": 125, "b": 210, "a": 255}, "ClamshellA PETG blue")

# =============================================================================
# 3) ClamshellB — SAME XY envelope, deck + open +X + OU scoops
# =============================================================================
upper_h = face_z - split_z  # was 22.05 → 19.55
last = new_rect("clamshell_b", "cb", SHELL_X0, SHELL_Y0, SHELL_X1, SHELL_Y1, upper_h, split_z)

drop_h = deck_z0 - split_z
# Body cavity; open +X. Near-ear Z lives in A (floor/ceil/tip). B lip added AFTER holes
# so it cannot steal let_face_z(+Z) from the tower top (face_z).
last = cut_rect(
    "clamshell_b", "cb_cav",
    body_cav_x0, cav_y0, cav_x1, cav_y1,
    drop_h + 0.3, split_z - 0.1,
)

let_face_z("cb_out", last, "clamshell_b", 1)
last = "cb_jnl"
hole(last, "clamshell_b", "cb_out", [0.0, 0.0, face_z], 8.20)
# Explicit boolean counterbore — solid_hole on cb_in never produced Ø12.10 pocket wall
last = cut_cyl(
    "clamshell_b", "cb_brg_pocket",
    BRG_POCKET, 0.0, 0.0, BRG_LEAD + BRG_W, deck_z0,
)

# Side Technic upper row
face_axis_let("f_cb_yp", last, "clamshell_b", 1, 1)
last = "cb_ty0"
hole(last, "clamshell_b", "f_cb_yp", [side_x[0], SHELL_Y1, cb_tech_z], TECHNIC)
face_axis_let("f_cb_ypb", last, "clamshell_b", 1, 1)
last = "cb_ty1"
hole(last, "clamshell_b", "f_cb_ypb", [side_x[1], SHELL_Y1, cb_tech_z], TECHNIC)
face_axis_let("f_cb_ym", last, "clamshell_b", 1, -1)
last = "cb_tm0"
hole(last, "clamshell_b", "f_cb_ym", [side_x[0], SHELL_Y0, cb_tech_z], TECHNIC)
face_axis_let("f_cb_ymb", last, "clamshell_b", 1, -1)
last = "cb_tm1"
hole(last, "clamshell_b", "f_cb_ymb", [side_x[1], SHELL_Y0, cb_tech_z], TECHNIC)

# Top four corners — BLIND (depth through tower only; no underside openings)
let_face_z("cb_top", last, "clamshell_b", 1)
face = "cb_top"
for i, (xi, yi) in enumerate(top_xy):
    sid = f"cb_top{i}"
    hole(sid, "clamshell_b", face, [xi, yi, face_z], TECHNIC, depth=TOP_TECH_DEPTH)
    last = sid
    face = f"cb_tf{i}"
    let_face_z(face, sid, "clamshell_b", 1)

# B: pocket is toward the split. The rail is the uncut wall outboard of B_CATCH,
# so with the Technic face on the bed the rail prints as solid layers first.
# No channel through that rail — no bridge, no 0.67 mm lip.
last = cut_yp_ym("clamshell_b", "cb_pkt", POCKET_FLOOR, B_POCKET_Z0, B_POCKET_Z1)

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

# Bilateral ear lip LAST (after holes) — overhang only (x <= x0), not into body XY
# (EAR_NEST_X1 past x0 overlaps servo body → IFC).
last = add_rect(
    "clamshell_b", "cb_ear_lip",
    cav_x0, -NEST_Y, ear_near_x1, NEST_Y,
    0.50, split_z,
)

appearance("cb_color", "clamshell_b", {"r": 35, "g": 170, "b": 100, "a": 255}, "ClamshellB PETG green")

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

_spline_depth = max((TOTAL_TO_SPLINE - flange_z0) + 0.6, HUB_FLANGE_T + 4.0)
last = cut_cyl("hub_body", "hs", SPLINE_SOCKET, 0, 0, _spline_depth + 0.4, -0.2)

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
# 6) v16 flush pocket clips ×2 — BuckleClipYP / BuckleClipYM ONLY
#    Profile lives in YZ (printer XY when printed on the side, build = X).
#    Spine outer face is flush with SHELL_Y. No combined body.
# =============================================================================
def combine_intersect(sid: str, target: str, tool: str) -> None:
    call(
        sid,
        "solid/body",
        "solid_combine",
        {
            "target_body_id": body_ptr(target),
            "tool_body_ids": [body_ptr(tool)],
            "operation": "intersect",
            "keep_tools": False,
        },
    )


def yspan(y_sign: float, mag_a: float, mag_b: float):
    ya, yb = y_sign * mag_a, y_sign * mag_b
    return (min(ya, yb), max(ya, yb))


def _seg_end(frm, length, angle_deg):
    a = math.radians(angle_deg)
    return (frm[0] + math.cos(a) * length, frm[1] + math.sin(a) * length)


def locked_line(sid: str, frm, length: float, angle_deg: float, length_text: str | None, angle_text: str) -> tuple:
    """Driving length/angle. Returns the endpoint the kernel will commit."""
    end = _seg_end(frm, length, angle_deg)
    args = {
        "from": {"x": frm[0], "y": frm[1]},
        "to_hint": {"x": end[0], "y": end[1]},
        "length_mm": length,
        "angle_deg": angle_deg,
        "angle_text": angle_text,
        "ctrl_held": True,
    }
    if length_text is not None:
        args["length_text"] = length_text
    call(sid, "sketch/draw", "sketch_add_line_locked", args)
    return end


def hook_segments(y_sign: float, z0: float):
    """YZ snap hook. Sketch x = world Y, sketch y = world Z.

    Neck overlaps the thin beam. Square tooth steps inward 0.60 mm.
    The 35 degree lead is only on the tooth, not a ramp up the whole arm.
    No arcs.
    """
    y_join = y_sign * TOOTH_JOIN_Y
    y_tooth = y_sign * TOOTH_Y
    z_ret = z0 + HOOK_Z
    # Lead spans the undercut only, so the tooth face stays thick.
    lead_dy = UNDERCUT
    lead_dz = lead_dy * math.tan(math.radians(LEAD_ANGLE_DEG))
    if HOOK_Z - lead_dz < 1.2:
        raise SystemExit(f"tooth face too thin {HOOK_Z - lead_dz}")
    # +Y tooth is toward -Y in world, so the lead walks back toward +Y and -Z.
    y_lead = y_tooth + (lead_dy if y_sign > 0 else -lead_dy)
    z_lead = z_ret - lead_dz
    pts = [
        (y_join, z0),
        (y_join, z_ret),
        (y_tooth, z_ret),
        (y_tooth, z_lead),
        (y_lead, z0),
    ]
    segs = []
    for i, frm in enumerate(pts):
        to = pts[(i + 1) % len(pts)]
        dx, dz = to[0] - frm[0], to[1] - frm[1]
        length = math.hypot(dx, dz)
        angle = math.degrees(math.atan2(dz, dx))
        segs.append((frm, length, angle, None, f"{angle:.4f}", f"s{i}"))
    return segs, {
        "undercut": UNDERCUT,
        "root_z": HOOK_Z,
        "tooth_y": TOOTH_Y,
        "join_y": TOOTH_JOIN_Y,
        "lead_ang": -LEAD_ANGLE_DEG if y_sign > 0 else -(180.0 - LEAD_ANGLE_DEG),
        "tooth_face": HOOK_Z - lead_dz,
    }


def add_hook(target: str, tag: str, y_sign: float, z0: float) -> str:
    """Prismatic along X. Trapezoid tooth in YZ. No cylinder, no fillet."""
    segs, _info = hook_segments(y_sign, z0)
    sketch_begin_plane(tag, "yz")
    call(f"{tag}_nosnap", "sketch/selection", "sketch_set_grid_snap", {"enabled": False})
    for i, (frm, length, angle, length_text, angle_text, _label) in enumerate(segs):
        locked_line(f"{tag}_l{i}", frm, length, angle, length_text, angle_text)
    # Re-enable while the sketch is still open. After finish there is no active sketch.
    call(f"{tag}_snap", "sketch/selection", "sketch_set_grid_snap", {"enabled": True})
    finish(tag)
    # Symmetric about X=0: walls parallel to X, no overhang along the build.
    call(
        f"{tag}_ex",
        "solid/build",
        "solid_extrude",
        {
            "sketch_name": tag,
            "profile_indices": [0],
            "operation": "new_body",
            "extent": {"type": "symmetric", "distance": HOOK_HALF * 2.0},
            "taper_angle_deg": 0,
            "flip": False,
            "target_body_ids": [],
        },
    )
    let_last_feature(f"{tag}_feat", f"{tag}_ex")
    let_body(f"{tag}_tmp", f"{tag}_ex", f"{tag}_feat")
    sid = f"join_{tag}"
    combine_join(sid, target, f"{tag}_tmp")
    return sid


def add_knurl_rib(target: str, tag: str, y_sign: float, mag_a: float, mag_b: float, z0: float, z1: float) -> str:
    """Rib along X, proud in Z only. Stays inside |Y|<=12. Not on the outer Y face."""
    if max(mag_a, mag_b) > SPINE_OUTER + 1e-9:
        raise SystemExit(f"knurl past |Y|=12: {mag_a} {mag_b}")
    y0, y1 = yspan(y_sign, mag_a, mag_b)
    return add_rect(target, tag, CLIP_X0, y0, CLIP_X1, y1, z1 - z0, z0)


def build_clip(tag: str, y_sign: float, body_var: str) -> str:
    """Flush spine |Y|=12. Shoes in the pockets. Square tooth steps inward.

    Lead is a straight 35° trapezoid in the YZ profile, extruded along X.
    Knurl is only on the min-Z and max-Z ends. No outer-Y step, no radius.
    """
    sy0, sy1 = yspan(y_sign, SPINE_INNER, SPINE_OUTER)
    fy0, fy1 = yspan(y_sign, HOOK_TIP, SPINE_OUTER)
    last_l = new_rect(
        body_var, f"{tag}_sp",
        CLIP_X0, sy0, CLIP_X1, sy1,
        SPINE_Z1 - SPINE_Z0, SPINE_Z0,
    )
    # Snap: thin beam, hook only at each end. No full-length shoe.
    last_l = add_hook(body_var, f"{tag}_ah", y_sign, A_TOOTH_Z0)
    last_l = add_hook(body_var, f"{tag}_bh", y_sign, B_TOOTH_Z0)
    # Pinch knurl. A face is the shoe's min Z (in the pocket). B face is the
    # tooth retention, which is the clip's max Z. Ribs run along X.
    for i, (a, b) in enumerate(((10.00, 10.80), (11.15, 11.95))):
        last_l = add_knurl_rib(
            body_var, f"{tag}_ka{i}", y_sign, a, b,
            A_TOOTH_Z0 - KNURL_PROUD, A_TOOTH_Z0 + KNURL_EMBED,
        )
    last_l = add_knurl_rib(
        body_var, f"{tag}_kb", y_sign, 9.08, 9.88,
        B_HOOK_TOP - KNURL_EMBED, B_HOOK_TOP + KNURL_PROUD,
    )
    return last_l


# Close both signs before any solid is emitted.
for _s in (1.0, -1.0):
    _segs, _info = hook_segments(_s, A_TOOTH_Z0)
    assert abs(_info["undercut"] - 0.60) < 1e-12
    assert abs(_info["root_z"] - 2.20) < 1e-12
    assert _info["tooth_face"] >= 1.2
print(
    "v16.2 tooth",
    f"innerY={TOOTH_Y:.2f} under={UNDERCUT:.2f} hookZ={HOOK_Z:.2f} joinY={TOOTH_JOIN_Y:.2f} shoeY={HOOK_TIP:.2f}",
)

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
call("final_scene", "solid/check", "solid_scene", {})
call("final_asm", "assembly/joints", "assembly_document", {})

_sock_r = SOCK_D / 2.0
_loc_x = min(abs(px) for px, _py in list(nub_xy_A) + list(sock_xy_A))
_gap_x = _loc_x - _sock_r - SLOT_HALF
assert WALL_TO_CAV >= 3.0 - 1e-9, WALL_TO_CAV
assert LIP_Y >= 2.4 and LIP_Z >= 2.4, (LIP_Y, LIP_Z)
assert abs(CHAN_FLOOR - POCKET_FLOOR) < 1e-9, (CHAN_FLOOR, POCKET_FLOOR)
assert HOOK_Z >= 1.6 and CLIP_XW >= 4.0
assert 1.05 <= SPINE_T <= 1.40, SPINE_T
assert 0.50 <= UNDERCUT <= 0.65, UNDERCUT
assert 30.0 <= LEAD_ANGLE_DEG <= 40.0
assert _gap_x >= 2.0, _gap_x
assert split_z - A_CATCH_Z >= 2.4, split_z - A_CATCH_Z
assert B_LIP_Z1 - B_CATCH_Z >= 2.4, B_LIP_Z1 - B_CATCH_Z
assert CLIP_SPAN_Z >= 8.30, CLIP_SPAN_Z  # do not shrink the bar
assert abs(SPINE_OUTER - 12.0) < 1e-9
assert abs((POCKET_FLOOR - TOOTH_Y) - UNDERCUT) < 1e-9
assert TOOTH_Y < HOOK_TIP - 0.50
assert HOOK_Z >= 1.6
assert KNURL_W >= 0.70 and KNURL_PROUD >= 0.30
assert TOOTH_JOIN_Y < SPINE_OUTER
assert HOOK_TIP >= POCKET_FLOOR + 0.10, (HOOK_TIP, POCKET_FLOOR)
assert SPINE_Z1 < B_CATCH_Z - 0.05
assert A_SHOE_Z1 < A_CATCH_Z - 0.2
assert B_SHOE_Z1 < B_CATCH_Z - 0.2
assert HOOK_HALF > CHAN_HALF + 0.4
print(
    f"v16.2 dims wall={WALL_TO_CAV:.3f} lipY={LIP_Y:.2f} toothY={TOOTH_Y:.2f} under={UNDERCUT:.2f} "
    f"spine={SPINE_T} spanZ={CLIP_SPAN_Z:.2f} clipX={CLIP_XW} shoeX={SHOE_X*2:.2f} "
    f"slot={SLOT_HALF*2:.2f} gapX={_gap_x:.2f} outer={SPINE_OUTER} "
    f"Arail=[{A_CATCH_Z:.2f},{split_z:.2f}] Brail=[{B_CATCH_Z:.2f},{B_LIP_Z1:.2f}] "
    f"tip={HOOK_TIP:.2f} bite={BITE_TOP:.2f} floor={POCKET_FLOOR} chanHalf={CHAN_HALF}"
)

doc = {
    "version": 1,
    "name": "INJS2065 Technic clamshell-IS-mount v16.3 narrow snap",
    "starting_state": "empty",
    "steps": steps,
    "exports": {"final_model": True, "final_scene": True, "final_solution": True},
}

header = (
    "// INJS2065 Technic CLAMSHELL-IS-MOUNT v16.2 — square inward tooth, straight 35 deg lead. mm.\n"
    f"// Envelope A=B: X=[{SHELL_X0}, {SHELL_X1}] Y=[{SHELL_Y0}, {SHELL_Y1}] "
    f"Z_A=[{SHELL_Z0}, {split_z}] Z_B=[{split_z}, {face_z}].\n"
    f"// Near EAR trapped; far open +X. BODY_CLR={BODY_CLR} BRG_POCKET={BRG_POCKET} axle {AXLE_SPAN}x{AXLE_ARM}.\n"
    f"// Nubs A{list(nub_xy_A)} sock{list(sock_xy_A)} D={NUB_D} eng={NUB_ENGAGE} sockD={SOCK_D} d={SOCK_DEPTH}.\n"
    f"// v16.2 clip: lipY={LIP_Y:.2f} floor={POCKET_FLOOR} under={UNDERCUT} toothY={TOOTH_Y:.2f} hookZ={HOOK_Z} "
    f"rail_Z={ARM_SPAN} under={UNDERCUT} arm={ARM_T} hookZ={HOOK_Z} Zif={Z_INTERF} "
    f"lead={LEAD_ANGLE_DEG:.0f}deg/{LEAD_Y:.2f} rootR={ROOT_R} clipX={CLIP_XW}.\n"
    "// PRINT: clips ON THEIR SIDE — hook/flex profile (model YZ) in printer XY, build dir = model X\n"
    "//        (layer lines ALONG the beam, not across it). Clamshells Z-up, split plane horizontal.\n"
    f"// Printed: ClamshellA, ClamshellB, OutputHub, BuckleClipYP, BuckleClipYM. NO combined BuckleClip. No M2/M3.\n"
)

out_dir = Path("/workspace/servo-case/v16.3")
out = out_dir / "injs2065-technic-clamshell.nbcad.jsonc"
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
    "architecture": "clamshell_is_technic_mount_v16_2_square_tooth",
    "clamp_path": "flush_pocket_clip",
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
    "technic_side_z_A": ca_tech_z,
    "technic_side_z_B": cb_tech_z,
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
    "bearing": {
        "BRG_POCKET": BRG_POCKET,
        "JOURNAL": JOURNAL,
        "brg_seat_z": brg_seat_z,
        "pocket_method": "cut_cyl",
        "pocket_h": BRG_LEAD + BRG_W,
        "deck_z0": deck_z0,
    },
    "hub": {
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
        "CROSS_DEPTH": CROSS_DEPTH,
        "hub_height": HUB_FLANGE_T + JOURNAL_LEN,
        "spline_depth": max((TOTAL_TO_SPLINE - flange_z0) + 0.6, HUB_FLANGE_T + 4.0),
    },
    "buckle": {
        "style": "flush_square_inward_tooth",
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
        "undercut": UNDERCUT,
        "tooth_inner_y": TOOTH_Y,
        "tooth_join_y": TOOTH_JOIN_Y,
        "lead_style": "straight_35_trapezoid",
        "knurl": {"width": KNURL_W, "proud": KNURL_PROUD, "faces": ["min_z", "max_z"], "along": "x"},
        "arm_t": ARM_T,
        "hook_z": HOOK_Z,
        "z_interf": Z_INTERF,
        "lead_angle_deg": LEAD_ANGLE_DEG,
        "lead_y": LEAD_Y,
        "lead_z": LEAD_Z,
        "root_r": ROOT_R,
        "clip_xw": CLIP_XW,
        "shoe_x": SHOE_X * 2.0,
        "hook_tip_y": HOOK_TIP,
        "bite_top_y": BITE_TOP,
        "arm_inner_y": ARM_INNER,
        "hook_outer_y": HOOK_OUTER,
        "A_catch_z": A_CATCH_Z,
        "B_catch_z": B_CATCH_Z,
        "B_lip_z1": B_LIP_Z1,
        "A_pocket_z": [A_POCKET_Z0, A_POCKET_Z1],
        "B_pocket_z": [B_POCKET_Z0, B_POCKET_Z1],
        "A_chan_z": [A_CHAN_Z0, A_CHAN_Z1],
        "A_hook_z": [A_HOOK_BOT, A_HOOK_TOP],
        "B_hook_z": [B_HOOK_BOT, B_HOOK_TOP],
        "min_section_mm": min(ARM_T, HOOK_Z, CLIP_XW),
        "clip_span_z": CLIP_SPAN_Z,
        "spine_t": SPINE_T,
        "spine_outer_y": SPINE_OUTER,
        "chan_floor": CHAN_FLOOR,
        "stock_wall_y": STOCK_WALL_Y,
        "hook_tip_clearance": HOOK_TIP - POCKET_FLOOR,
        "slot_span_x": SLOT_HALF * 2.0,
        "probes": {
            "rail_x": round((CHAN_HALF + SHOE_X) / 2.0, 3),
            "lip_y_sample": round((HOOK_TIP + BITE_TOP) / 2.0, 3),
            "A_z": round(0.5 * (A_CATCH_Z + split_z), 3),
            "B_z": round(0.5 * (B_CATCH_Z + B_LIP_Z1), 3),
            "A_z_face": A_CATCH_Z,
            "B_z_face": B_CATCH_Z,
            "floor": POCKET_FLOOR,
        },
        "pockets": [
            [-SLOT_HALF, POCKET_FLOOR, A_POCKET_Z0, SLOT_HALF, 12.0 + POCKET_Y_OVER, A_POCKET_Z1],
            [-SLOT_HALF, -(12.0 + POCKET_Y_OVER), A_POCKET_Z0, SLOT_HALF, -POCKET_FLOOR, A_POCKET_Z1],
            [-CHAN_HALF, POCKET_FLOOR, A_CHAN_Z0, CHAN_HALF, 12.0 + POCKET_Y_OVER, A_CHAN_Z1],
            [-CHAN_HALF, -(12.0 + POCKET_Y_OVER), A_CHAN_Z0, CHAN_HALF, -POCKET_FLOOR, A_CHAN_Z1],
            [-SLOT_HALF, POCKET_FLOOR, B_POCKET_Z0, SLOT_HALF, 12.0 + POCKET_Y_OVER, B_POCKET_Z1],
            [-SLOT_HALF, -(12.0 + POCKET_Y_OVER), B_POCKET_Z0, SLOT_HALF, -POCKET_FLOOR, B_POCKET_Z1],
        ],
        "print_orientation": (
            "Clips print on their side: the hook profile (model YZ) lies in the printer XY plane; "
            "build direction is model X so layer lines run along the beam. "
            "Clamshells print Z-up, split horizontal (A: split on the bed; B: Technic face on the bed). "
            "B catch is NOT a bridge: the rail is uncut shell outboard of the pocket, so it prints "
            "as solid layers before the pocket is opened. The lip is a 2.45 mm step, loaded section 3.0 mm in Z."
        ),
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
