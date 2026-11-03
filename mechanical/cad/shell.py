"""UZBIONIC outer shell v0.1: the covers that make the mechanism look like a hand (2026-10-30).

Our own design (decision D-14). The style follows the owner's references, as ideas only: a white,
smooth shell; dark joints left visible between the covers; grey grip pads on the fingertips and palm.

Parts:
- finger_cover(fp, i): sleeve over phalanx i, rounded, ending in a rounded fingertip on the distal one.
  Covers stop short of each joint, so the joints stay visible and can turn.
- tip_pad(fp): grey pad on the palm side of a fingertip.
- palm_shell(pp): rounded shell around the palm and its back cover, open at the knuckles, the wrist and
  the thumb's path. The UZBIONIC name is engraved on the back of the hand.
- palm_pads(pp): grey grip pads on the palm side.
- thumb_cover(pp, rotation): sleeve over the thumb metacarpal arm.
- dressed(pp, grip): every skeleton and shell part, placed for a grip.

Intended material: covers in TPU or PLA, pads in TPU. How the covers are split and clipped on for
printing is not designed yet. Units: mm.
"""

from __future__ import annotations

import math

import cadquery as cq

from mechanical.anthropometry import FINGERS
from mechanical.cad.finger import FingerParams
from mechanical.cad.hand import Grip, PalmParams, _rotate_thumb, assembled, place

WALL = 1.2  # design
GAP = 0.3  # between a skeleton part and its cover
JOINT_GAP = 1.0  # extra room left open at each joint


def _rounded_box(lx, ly, lz, r_long, r_ends=0.0, x0=0.0):
    """Box from x0 to x0+lx, centred in Y and Z, with long edges rounded (and ends, if asked)."""
    b = cq.Workplane("XY").box(lx, ly, lz, centered=(False, True, True)).translate((x0, 0, 0))
    for r in (r_long, r_long * 0.7, r_long * 0.4):
        try:
            b = b.edges("|X").fillet(r)
            break
        except Exception:  # fillet too large for this size: try a smaller one
            continue
    if r_ends:
        for r in (r_ends, r_ends * 0.6, r_ends * 0.3):
            try:
                b = b.faces("<X or >X").edges().fillet(r)
                break
            except Exception:
                continue
    return b


def _outer_radius(fp: FingerParams) -> float:
    return fp.height / 2 + GAP + WALL


def _child_sweep(fp: FingerParams, reach: float) -> cq.Workplane:
    """Space the next phalanx's body passes through near a pin at the origin, over -5..95 deg of flexion."""
    sweep = None
    for a in range(-5, 100, 5):
        # a little taller than the body, to cover the cusps between the 5 degree steps
        b = cq.Workplane("XY").box(reach, fp.width + 2 * GAP, fp.height + 2 * GAP + 0.6, centered=(False, True, True))
        # the extension-stop lip sits behind the pin and swings up past the cover as the joint bends
        x0, x1, z0, z1 = fp.lip_box
        lip = cq.Workplane("XY").box(x1 - x0 + 1.0, fp.tongue_width + 2 * GAP, z1 - z0 + 1.0, centered=(False, True, False))
        b = b.union(lip.translate((x0 - 0.5, 0, z0 - 0.5)))
        b = b.rotate((0, 0, 0), (0, 1, 0), a)
        sweep = b if sweep is None else sweep.union(b)
    return sweep


def joint_cap_cover(fp: FingerParams, x0: float, width: float | None = None) -> cq.Workplane:
    """Cover from x0 up to a pin at the origin, ending in a round cap around the pin.

    The cap keeps inside a circle of the outer radius around the pin, and the next cover starts outside
    that circle, so neighbouring covers can never touch however the joint turns. The cap is cut where
    the next phalanx's body passes, so from the back the joint looks closed, like a knuckle."""
    w = fp.width if width is None else width
    h = fp.height
    ro = _outer_radius(fp)
    ow, oh = w + 2 * (GAP + WALL), h + 2 * (GAP + WALL)
    outer = _rounded_box(-x0, ow, oh, oh * 0.45, x0=x0)
    cap = cq.Workplane("XZ").circle(ro).extrude(ow / 2, both=True)
    try:
        cap = cap.edges().fillet(min(WALL * 1.5, ow * 0.1))
    except Exception:
        pass
    outer = outer.union(cap)
    inner = cq.Workplane("XY").box(-x0 + 1, w + 2 * GAP, h + 2 * GAP, centered=(False, True, True)).translate((x0 - 1, 0, 0))
    inner = inner.union(cq.Workplane("XZ").circle(h / 2 + GAP).extrude(w / 2 + GAP, both=True))
    return outer.cut(inner).cut(_child_sweep(fp, ro + 4.0))


def cover_start(fp: FingerParams) -> float:
    """Where a phalanx cover begins: just outside the parent's cap circle."""
    return _outer_radius(fp) + 0.6


def finger_cover(fp: FingerParams, index: int) -> cq.Workplane:
    """Cover over one phalanx, in the phalanx's own frame (proximal pin at the origin)."""
    L, w, h = fp.lengths[index], fp.width, fp.height
    is_tip = index == len(fp.lengths) - 1
    x0 = cover_start(fp)
    ow, oh = w + 2 * (GAP + WALL), h + 2 * (GAP + WALL)
    if is_tip:
        x1 = L + GAP + WALL
        outer = _rounded_box(x1 - x0, ow, oh, oh * 0.45, x0=x0)
        try:
            outer = outer.faces(">X").edges().fillet(min(ow, oh) * 0.42)
        except Exception:  # keep the square end if the big fillet fails
            pass
        inner = cq.Workplane("XY").box(L + GAP - x0 + 1, w + 2 * GAP, h + 2 * GAP, centered=(False, True, True)).translate((x0 - 1, 0, 0))
        return outer.cut(inner)
    return joint_cap_cover(fp, x0 - L).translate((L, 0, 0))


def tip_pad(fp: FingerParams) -> cq.Workplane:
    """Grey grip pad on the palm side of the fingertip (distal phalanx frame)."""
    L, w, h = fp.lengths[-1], fp.width, fp.height
    length = 0.5 * L
    pad = _rounded_box(length, w * 0.72, 2.0, 0.9, r_ends=0.9, x0=L - length - 1.5)
    return pad.translate((0, 0, -(h / 2 + GAP + WALL) - 1.0))  # sits on the cover's surface


def _place_chain(fp: FingerParams, local_parts: list[cq.Workplane | None], angles) -> list[cq.Workplane | None]:
    """Place parts given in each phalanx's frame, the same way mechanical.cad.finger.assembled does."""
    out, x, z, total = [], 0.0, 0.0, 0.0
    for i, part in enumerate(local_parts):
        total += angles[i]
        out.append(None if part is None else part.rotate((0, 0, 0), (0, 1, 0), total).translate((x, 0, z)))
        x += fp.lengths[i] * math.cos(math.radians(total))
        z -= fp.lengths[i] * math.sin(math.radians(total))
    return out


def _palm_extent(pp: PalmParams) -> tuple[float, float, float]:
    """Front x, half breadth and top z of the palm including its back cover."""
    L = pp.layout
    return pp.front, L.palm_breadth / 2, L.palm_thickness / 2 + pp.wall


def palm_shell(pp: PalmParams = PalmParams()) -> cq.Workplane:
    L = pp.layout
    front, half_b, top = _palm_extent(pp)
    bottom = -L.palm_thickness / 2
    t = GAP + WALL
    x0, x1 = 0.0, front + 1.0
    outer = cq.Workplane("XY").box(x1 - x0, 2 * (half_b + t), top - bottom + 2 * t, centered=(False, True, False))
    outer = outer.translate((x0, 0, bottom - t))
    outer = outer.edges("|Z").fillet(pp.corner_radius + t)
    for r in (12.0, 9.0, 6.0, 4.0):
        try:
            outer = outer.edges("|Y or |X").fillet(r)
            break
        except Exception:
            continue
    inner = cq.Workplane("XY").box(x1 - x0 + 10, 2 * (half_b + GAP), top - bottom + 2 * GAP, centered=(False, True, False))
    inner = inner.translate((x0 - 5, 0, bottom - GAP))
    inner = inner.edges("|Z").fillet(pp.corner_radius + GAP)
    shell = outer.cut(inner)
    # thumb: the arm's whole travel plus the hub lugs
    hub = L.thumb_hub
    lug_len = pp.hub_length + 2 * (pp.lug_thickness + pp.clearance) + 2 * t
    lugs = cq.Workplane("YZ").circle(pp.hub_radius + pp.wall + t).extrude(lug_len).translate((hub[0] - lug_len / 2, hub[1], hub[2]))
    shell = shell.cut(lugs).cut(_grown_sweep(pp, t))
    # name on the back of the hand
    try:
        text = (
            cq.Workplane("XY").workplane(offset=top + t - 0.6)
            .center(front * 0.45, 0)
            .text("UZBIONIC", 7.0, 1.0, combine=False, halign="center", valign="center")
        )
        shell = shell.cut(text)
    except Exception:  # no font available: leave the name off
        pass
    return shell


def _grown_sweep(pp: PalmParams, grow: float) -> cq.Workplane:
    from mechanical.cad.hand import thumb_metacarpal
    import numpy as np

    angles = np.arange(-6.0, pp.layout.thumb_opposed_deg + 6.0 + 1e-9, 6.0)
    sweep = None
    for a in angles:
        s = thumb_metacarpal(pp, float(a), grow=pp.clearance * 2 + grow)
        sweep = s if sweep is None else sweep.union(s)
    return sweep


def palm_pads(pp: PalmParams = PalmParams()) -> cq.Workplane:
    """Grey pads on the palm side: one large palm pad and a bar under the knuckles."""
    L = pp.layout
    front, half_b, _ = _palm_extent(pp)
    z = -L.palm_thickness / 2 - GAP - WALL - 1.2  # sits on the shell's surface
    big = _rounded_box(front * 0.5, half_b * 1.15, 2.4, 1.1, r_ends=1.1, x0=front * 0.22).translate((0, L.mirror * -half_b * 0.12, z))
    bar = _rounded_box(9.0, half_b * 1.7, 2.4, 1.1, r_ends=1.1, x0=front - 12.0).translate((0, 0, z))
    return big.union(bar)


def thumb_cover(pp: PalmParams = PalmParams(), rotation_deg: float = 0.0) -> cq.Workplane:
    """Cover over the thumb metacarpal arm, from near the hub to a cap around the thumb's MCP joint."""
    L = pp.layout
    tp = pp.thumb_params()
    sleeve = joint_cap_cover(tp, -L.thumb_metacarpal + pp.hub_radius + 4.0)
    sleeve = place(sleeve, L.thumb_frame(0.0), L.thumb_mcp(0.0))
    # stay clear of the hub lugs, like the metacarpal itself (see hand.thumb_metacarpal)
    hub = L.thumb_hub
    for xa in (hub[0] - pp.hub_length / 2 - pp.lug_thickness - 10, hub[0] + pp.hub_length / 2):
        sleeve = sleeve.cut(cq.Workplane("YZ").circle(pp.hub_radius + 6).extrude(pp.lug_thickness + 10).translate((xa, hub[1], hub[2])))
    return _rotate_thumb(sleeve, L, rotation_deg)


def dressed(pp: PalmParams = PalmParams(), grip: Grip = Grip()) -> dict[str, cq.Workplane]:
    """Skeleton plus shell, placed for a grip. Shell part names start with 'shell_' or 'pad_'."""
    parts = assembled(pp, grip)
    L = pp.layout
    parts["shell_palm"] = palm_shell(pp)
    parts["pad_palm"] = palm_pads(pp)
    parts["shell_thumb_metacarpal"] = thumb_cover(pp, grip.thumb_rotation)
    for f in FINGERS:
        fp = pp.finger_params(f)
        m = L.mcp(f)
        x0 = pp.front + 1.0 + GAP - m[0]  # starts just past the front of the palm shell
        parts[f"shell_{f}_knuckle"] = joint_cap_cover(fp, x0).translate(tuple(m))
    for f in FINGERS + ("thumb",):
        fp = pp.thumb_params() if f == "thumb" else pp.finger_params(f)
        angles = grip.thumb if f == "thumb" else grip.fingers[f]
        covers = _place_chain(fp, [finger_cover(fp, i) for i in range(len(fp.lengths))], angles)
        pad = _place_chain(fp, [None] * (len(fp.lengths) - 1) + [tip_pad(fp)], angles)[-1]
        if f == "thumb":
            r, pos = L.thumb_frame(grip.thumb_rotation), L.thumb_mcp(grip.thumb_rotation)
            covers = [place(c, r, pos) for c in covers]
            pad = place(pad, r, pos)
        else:
            covers = [c.translate(tuple(L.mcp(f))) for c in covers]
            pad = pad.translate(tuple(L.mcp(f)))
        for name, c in zip(fp.names, covers):
            parts[f"shell_{f}_{name}"] = c
        parts[f"pad_{f}_tip"] = pad
    return parts
