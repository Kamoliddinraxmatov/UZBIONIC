"""UZBIONIC look v0.2: brand model closer to the owner's references (2026-10-30).

Our own design (decision D-14). The owner asked for the look of a set of concept-art images; we take
their visual language only and draw every shape ourselves:
- fingers: the phalanges stay visible as bright metal, with white pads on their back and palm side, a
  white rounded fingertip and a grey grip pad;
- palm: perforated back, a white hard frame along the thumb side, grey terraced ("contour line") pads
  on the thenar and hypothenar areas and a ribbed bar under the knuckles;
- forearm: a perforated sleeve wrapping diagonally round the back and the thumb side, a white hard
  frame on the little-finger side with a terraced grey pad, and a large open window in the sleeve
  showing the dark inner liner.

Everything is built from the v0.1 parts (mechanical.cad.shell, mechanical.cad.forearm), so the
skeleton, motors and clearances are unchanged. The perforation is drawn by the renderer only (a
surface pattern); whether printed parts get real holes is decided with the print tests.

Material of each part is given by material_v2(name). Units: mm, degrees.
"""

from __future__ import annotations

import math

import cadquery as cq

from mechanical.anthropometry import FINGERS
from mechanical.cad.forearm import ForearmParams, _loft, _x_back, elbow_hub, wrist_cuff
from mechanical.cad.hand import Grip, PalmParams, assembled, place
from mechanical.cad.shell import GAP, WALL, _outer_radius, joint_cap_cover, _palm_extent, _place_chain, cover_start, finger_cover, palm_shell, thumb_cover, tip_pad

# ---------------------------------------------------------------- fingers


def finger_pads(fp, index: int) -> list[cq.Workplane]:
    """White pads on the back and palm side of a phalanx (phalanx frame), cut from its v0.1 cover, so
    they keep its proven clearances. The distal phalanx keeps its whole rounded tip cover."""
    cover = finger_cover(fp, index)
    if index == len(fp.lengths) - 1:
        return [cover]
    L, h = fp.lengths[index], fp.height
    x0 = cover_start(fp) + 0.8
    x1 = L - _outer_radius(fp) - 0.8
    out = []
    for z0 in (h * 0.22, -100.0 - h * 0.22):
        box = cq.Workplane("XY").box(x1 - x0, 100, 100, centered=(False, True, False)).translate((x0, 0, z0))
        out.append(cover.intersect(box))
    return out


# ---------------------------------------------------------------- palm


def _terraced(a: float, b: float, levels: int, step: float, base: float, taper: float = 0.17) -> cq.Workplane:
    """Pad of stacked ellipses getting smaller towards the top: looks like contour lines. Grows +Z from 0."""
    pad = cq.Workplane("XY").ellipse(a, b).extrude(base)
    for i in range(1, levels):
        s = 1.0 - taper * i
        pad = pad.union(cq.Workplane("XY").ellipse(a * s, b * s).extrude(base + step * i))
    return pad


def palm_shell_parts(pp: PalmParams) -> dict[str, cq.Workplane]:
    """v0.1 palm shell split into the perforated back and the white frame (sides, thumb side, palm)."""
    shell = palm_shell(pp)
    L = pp.layout
    front, half_b, top = _palm_extent(pp)
    # back of the hand, except a strip along the thumb side that stays white (the "frame")
    m = L.mirror  # the thumb is on the side where m * y > 0
    y_edge = m * half_b * 0.55
    y_lo, y_hi = (y_edge, 100.0) if m < 0 else (-100.0, y_edge)
    back_zone = cq.Workplane("XY").box(200, y_hi - y_lo, 100, centered=(True, False, False)).translate((0, y_lo, 5.0))
    back = shell.intersect(back_zone)
    return {"shell_palm_back": back, "shell_palm_frame": shell.cut(back_zone)}


def palm_pads_v2(pp: PalmParams) -> cq.Workplane:
    """Grey terraced pads on the palm side: thenar (thumb side), hypothenar, and a ribbed knuckle bar."""
    L = pp.layout
    front, half_b, _ = _palm_extent(pp)
    m = L.mirror
    z = -L.palm_thickness / 2 - GAP - WALL  # palm-side surface of the shell
    pads = []
    # thenar: thumb side towards the wrist; hypothenar: little-finger side
    x_min = 16.0 + 1.5  # the wrist cuff covers the palm shell up to x = 16 (forearm.wrist_cuff)
    # the thenar pad stays clear of the opposed thumb
    for (fx, fy, a, b) in ((0.36, 0.30, 16.0, 11.0), (0.44, -0.48, 18.0, 11.0)):
        p = _terraced(a, b, 5, 0.45, 0.8).mirror("XY")  # grow towards -Z
        pads.append(p.translate((max(front * fx, x_min + a), m * half_b * fy, z)))
    bar = None
    for i in range(4):
        rib = cq.Workplane("XY").box(2.0, half_b * 1.55, 2.0 + 0.4 * (i % 2)).translate((front - 13.0 + i * 2.6, 0, 0))
        bar = rib if bar is None else bar.union(rib)
    base = cq.Workplane("XY").box(10.5, half_b * 1.6, 0.8).translate((front - 9.1, 0, 0))
    bar = base.union(bar).translate((0, 0, z - 1.25))  # ribs reach up to 0.05 mm short of the shell
    return pads[0].union(pads[1]).union(bar)


# ---------------------------------------------------------------- forearm


def _twisted_sector(p: ForearmParams, theta0, theta1, x_front: float, x_back: float, n: int = 6) -> cq.Workplane:
    """Solid sector about the X axis between angles theta0(t) and theta1(t) (deg from +Z towards the
    little-finger side), t = 0 at x_front and 1 at x_back. The angles may change along X, so the
    boundary wraps round the forearm diagonally."""
    wires = []
    side = p.ulnar
    for k in range(n + 1):
        t = k / n
        x = x_front + (x_back - x_front) * t
        a0, a1 = math.radians(theta0(t)), math.radians(theta1(t))
        pts = [cq.Vector(x, 0, 0)]
        for j in range(13):
            a = a0 + (a1 - a0) * j / 12
            pts.append(cq.Vector(x, side * 90 * math.sin(a), 90 * math.cos(a)))
        wires.append(cq.Wire.makePolygon(pts, close=True))
    return cq.Workplane("XY").add(cq.Solid.makeLoft(wires, True))


def _frame_zone(p: ForearmParams) -> cq.Workplane:
    """Where the forearm stays hard white plastic: the little-finger side, wrapping up over the back
    towards the elbow."""
    return _twisted_sector(p, lambda t: 70 - 45 * t, lambda t: 200 - 10 * t, p.start_x + 1, _x_back(p) - 1)


def _window_zone(p: ForearmParams) -> cq.Workplane:
    """Large open window in the sleeve, on the back / thumb side towards the elbow."""
    x0, x1 = -0.42 * p.length, -0.90 * p.length
    n = 28
    top = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        top.append((x, max(math.sin(math.pi * t) ** 0.7 * 17.0, 0.05)))
    outline = [(x, y) for x, y in top] + [(x, -y) for x, y in reversed(top[1:-1])]
    lens = cq.Workplane("XY").polyline(outline).close().extrude(80)
    # centre it at -55 deg (towards the thumb side) and lean it along the wrap
    return lens.rotate((0, 0, 0), (1, 0, 0), 55 * p.ulnar)


def forearm_v2(p: ForearmParams = ForearmParams()) -> dict[str, cq.Workplane]:
    x_back = _x_back(p)
    outer = _loft(p, 0.0, p.start_x, x_back)
    inner = _loft(p, -p.wall, p.start_x + 1, x_back - 1)
    shell = outer.cut(inner)
    frame = _frame_zone(p)
    window = _window_zone(p)
    sleeve = shell.cut(frame).cut(window)
    hard = shell.intersect(frame)
    # grey terraced pad on the hard side, standing proud of it
    xc, length, height = -0.56 * p.length, 120.0, 38.0
    pad = None
    for i in range(5):
        s = 1.0 - 0.16 * i
        layer = _loft(p, 0.7 + 0.45 * i, p.start_x, x_back).cut(_loft(p, 0.0, p.start_x, x_back))
        prism = cq.Workplane("XZ").ellipse(length / 2 * s, height / 2 * s).extrude(-80).translate((xc, 0, -4))
        if p.ulnar < 0:
            prism = prism.mirror("XZ")
        piece = layer.intersect(prism)
        pad = piece if pad is None else pad.union(piece)
    # name on the hard side, near the wrist
    xt = -0.22 * p.length
    a, _ = p.section(xt)
    text = cq.Workplane("XZ").text("UZBIONIC", 6.0, 1.2, combine=False, halign="center", valign="center").translate((xt, 0, 0))
    # the XZ text faces -Y; mirror it to read from +Y, then sink it 1 mm into the surface
    text = text.mirror("YZ", (xt, 0, 0)).translate((0, a + 0.2, 0)) if p.ulnar > 0 else text.translate((0, -(a + 0.2) + 1.2, 0))
    hard = hard.cut(text)
    # dark liner inside the sleeve, seen through the window (textile or printed lattice)
    # stops short of the elbow hub, which sits in the same room
    x_liner = -p.length + p.hub_radius + p.clearance
    # (same loft stations as the shell's inner surface, so the two surfaces stay parallel)
    room = _loft(p, -p.wall - p.clearance, p.start_x + 1, x_back - 1)
    liner = room.cut(_loft(p, -p.wall - p.clearance - 1.2, p.start_x + 1, x_back - 1))
    liner = liner.intersect(cq.Workplane("XY").box(-56.0 - x_liner, 200, 200, centered=(False, True, True)).translate((x_liner, 0, 0)))
    return {
        "forearm_sleeve": sleeve,
        "forearm_frame": hard,
        "forearm_pad": pad,
        "forearm_liner": liner,
        "elbow_hub": elbow_hub(p),
        "forearm_cuff": wrist_cuff(p),
    }


# ---------------------------------------------------------------- whole arm


def dressed_v2(pp: PalmParams = PalmParams(), grip: Grip = Grip()) -> dict[str, cq.Workplane]:
    """Skeleton (shown as metal), v0.2 covers and pads, placed for a grip. Hand only; add forearm_v2()."""
    parts = assembled(pp, grip)
    L = pp.layout
    parts.update(palm_shell_parts(pp))
    parts["pad_palm"] = palm_pads_v2(pp)
    parts["shell_thumb_metacarpal"] = thumb_cover(pp, grip.thumb_rotation)
    for f in FINGERS:  # white knuckle caps, as in v0.1
        fp, m = pp.finger_params(f), L.mcp(f)
        parts[f"shell_{f}_knuckle"] = joint_cap_cover(fp, pp.front + 1.0 + GAP - m[0]).translate(tuple(m))
    for f in FINGERS + ("thumb",):
        fp = pp.thumb_params() if f == "thumb" else pp.finger_params(f)
        angles = grip.thumb if f == "thumb" else grip.fingers[f]
        for i, name in enumerate(fp.names):
            local = [None] * len(fp.lengths)
            for k, piece in enumerate(finger_pads(fp, i)):
                local[i] = piece
                placed = _place_chain(fp, local, angles)[i]
                placed = place(placed, L.thumb_frame(grip.thumb_rotation), L.thumb_mcp(grip.thumb_rotation)) if f == "thumb" else placed.translate(tuple(L.mcp(f)))
                parts[f"shell_{f}_{name}_{k}"] = placed
        tip = _place_chain(fp, [None] * (len(fp.lengths) - 1) + [tip_pad(fp)], angles)[-1]
        tip = place(tip, L.thumb_frame(grip.thumb_rotation), L.thumb_mcp(grip.thumb_rotation)) if f == "thumb" else tip.translate(tuple(L.mcp(f)))
        parts[f"pad_{f}_tip"] = tip
    return parts


def material_v2(name: str) -> str:
    if name in ("shell_palm_back", "forearm_sleeve"):
        return "mesh"
    if name == "forearm_liner":
        return "fabric"
    if name.startswith(("pad_", "forearm_pad")):
        return "pad"
    if name.startswith(("shell_", "forearm_frame", "forearm_cuff")):
        return "shell"
    if name.startswith(("wrist", "elbow")):
        return "ring"
    if name in ("palm", "palm_cover"):
        return "inner"
    return "chrome"


__all__ = ["dressed_v2", "finger_pads", "forearm_v2", "material_v2", "palm_pads_v2", "palm_shell_parts"]
