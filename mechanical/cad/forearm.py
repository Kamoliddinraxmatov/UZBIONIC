"""UZBIONIC forearm shell v0.1: the outer forearm from the wrist ring to the elbow (2026-10-30).

Our own design (decision D-14, owner's choice 2026-10-30: "our own design, in that style"). The style
follows the owner's reference images as ideas only: glossy white shell, a soft perforated panel, a grey
grip panel with contour grooves, a graphite wrist ring and a visible elbow hub. No shape was copied.

Frame: the hand frame of mechanical.hand_layout. The forearm runs along -X behind the wrist rotator
(x < 0), Z towards the back of the hand. For the left hand the thumb (radial) side is -Y.

SIZES ARE DESIGN PLACEHOLDERS until the first user's right forearm is measured (length elbow to
wrist, circumference at the wrist and at the widest point) and mirrored. Only the wrist end is fixed by
our own parts: it must slide over the wrist stator (mechanical.cad.wrist).

Parts:
- forearm_shell(p): white hollow shell, open at both ends, with windows for the two panels.
- mesh_panel(p): perforated panel on the back of the forearm.
- grip_panel(p): grey panel on the ulnar side, with contour grooves.
- elbow_hub(p): elbow joint housing (envelope only; the elbow mechanism is a later phase).
- wrist_cuff(p): white cuff fixed to the palm shell that blends the round wrist into the flat palm.
Units: mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq

from mechanical.cad.wrist import WristParams


@dataclass(frozen=True)
class ForearmParams:
    wrist: WristParams = WristParams()
    length: float = 250.0  # placeholder: wrist joint (x=0) to elbow axis
    wall: float = 2.0
    clearance: float = 0.3
    start_x: float = -36.0  # front edge; the stator in front of this shows as the wrist ring
    # outer half-widths (Y) and half-heights (Z) along the forearm, as fractions of length (placeholders)
    stations: tuple = ((0.144, 31.6, 30.6), (0.30, 34.0, 31.5), (0.55, 39.0, 35.0), (0.78, 41.0, 36.5), (0.93, 39.5, 36.0))
    mesh_from: float = 0.24  # perforated panel extent along the forearm (fractions of length)
    mesh_to: float = 0.86
    mesh_half_angle: float = 42.0  # deg either side of the back (+Z)
    hole_diameter: float = 1.2
    hole_pitch: float = 3.6
    panel_recess: float = 0.8
    grip_center: float = 0.58  # grey panel on the ulnar side (+Y for the left hand)
    grip_length: float = 110.0
    grip_height: float = 34.0
    grip_rings: int = 4
    hub_radius: float = 30.0
    side: str = "left"

    def __post_init__(self) -> None:
        r0 = min(self.stations[0][1], self.stations[0][2])
        need = self.wrist.outer_diameter / 2 + self.clearance + self.wall
        if r0 < need:
            raise ValueError(f"wrist end too small for the stator: {r0} < {need}")

    @property
    def ulnar(self) -> float:
        return 1.0 if self.side == "left" else -1.0

    def section(self, x: float) -> tuple[float, float]:
        """Outer half-width and half-height at x (linear between stations)."""
        pts = [(-f * self.length, a, b) for f, a, b in self.stations]
        if x >= pts[0][0]:
            return pts[0][1], pts[0][2]
        for (x0, a0, b0), (x1, a1, b1) in zip(pts, pts[1:]):
            if x1 <= x <= x0:
                t = (x0 - x) / (x0 - x1)
                return a0 + t * (a1 - a0), b0 + t * (b1 - b0)
        return pts[-1][1], pts[-1][2]


def _loft(p: ForearmParams, grow: float, x_front: float, x_back: float) -> cq.Workplane:
    """Smooth elliptical loft from x_front back to x_back, sections grown by `grow`."""
    xs = [x_front] + [-f * p.length for f, _, _ in p.stations[1:]] + [x_back]
    xs = sorted(set(round(x, 4) for x in xs if x_back <= x <= x_front), reverse=True)
    wires = []
    for x in xs:
        a, b = p.section(x)
        wires.append(cq.Wire.makeEllipse(a + grow, b + grow, cq.Vector(x, 0, 0), cq.Vector(1, 0, 0), cq.Vector(0, 1, 0)))
    return cq.Workplane("XY").add(cq.Solid.makeLoft(wires, False))


def _x_back(p: ForearmParams) -> float:
    return -p.stations[-1][0] * p.length


def _mesh_zone(p: ForearmParams, inset: float = 0.0) -> cq.Workplane:
    """Lens-shaped zone on the back, seen from above: a prism along Z (above the axis) whose outline
    follows the forearm's width, pointed at both ends. `inset` shrinks it all round."""
    x0, x1 = -p.mesh_from * p.length - inset, -p.mesh_to * p.length + inset
    s = math.sin(math.radians(p.mesh_half_angle))
    n = 32
    top = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        a, _ = p.section(x)
        top.append((x, max(math.sin(math.pi * t) ** 0.55 * a * s - inset, 0.05)))
    outline = [(x, y) for x, y in top] + [(x, -y) for x, y in reversed(top[1:-1])]
    return cq.Workplane("XY").polyline(outline).close().extrude(80)


def _grip_zone(p: ForearmParams, scale: float = 1.0, depth: float = 80.0) -> cq.Workplane:
    """Elliptical prism along Y on the ulnar side."""
    xc = -p.grip_center * p.length
    e = cq.Workplane("XZ").ellipse(p.grip_length / 2 * scale, p.grip_height / 2 * scale).extrude(-depth)
    return e.translate((xc, 0, 0)) if p.ulnar > 0 else e.mirror("XZ").translate((xc, 0, 0))


def forearm_shell(p: ForearmParams = ForearmParams()) -> cq.Workplane:
    x_back = _x_back(p)
    outer = _loft(p, 0.0, p.start_x, x_back)
    inner = _loft(p, -p.wall, p.start_x + 1, x_back - 1)
    shell = outer.cut(inner)
    shell = shell.cut(_mesh_zone(p))
    shell = shell.cut(_grip_zone(p))
    # UZBIONIC on the radial side, near the elbow
    xc = -0.80 * p.length
    a, _ = p.section(xc)
    text = (
        cq.Workplane("XZ", origin=(0, 0, 0))
        .text("UZBIONIC", 6.5, 1.2, combine=False, halign="center", valign="center")
        .translate((xc, 0, 6))
    )
    if p.ulnar > 0:  # radial side is -Y: the XZ text plane extrudes towards -Y, mirror to read from outside
        text = text.mirror("YZ", (xc, 0, 0)).translate((0, -(a - 0.6), 0))
    else:
        text = text.mirror("XZ").translate((0, a - 0.6, 0))
    return shell.cut(text)


def mesh_panel(p: ForearmParams = ForearmParams()) -> cq.Workplane:
    """Perforated panel filling the back window, recessed by panel_recess."""
    x_back = _x_back(p)
    outer = _loft(p, -p.panel_recess, p.start_x, x_back)
    inner = _loft(p, -p.panel_recess - 1.4, p.start_x + 1, x_back - 1)
    panel = outer.cut(inner).intersect(_mesh_zone(p, inset=p.clearance))
    holes = []
    x0, x1 = -p.mesh_from * p.length, -p.mesh_to * p.length
    nx = int((x0 - x1) / p.hole_pitch)
    for i in range(1, nx):
        x = x0 - i * p.hole_pitch
        a, b = p.section(x)
        r = (a + b) / 2
        da = p.hole_pitch / r
        k = int(math.radians(p.mesh_half_angle) / da) + 1
        off = 0.5 if i % 2 else 0.0
        for jj in range(-k, k + 1):
            w = (jj + off) * da
            d = cq.Vector(0, math.sin(w), math.cos(w))
            base = cq.Vector(x, 0, 0) + d * (r - 8)
            holes.append(cq.Solid.makeCylinder(p.hole_diameter / 2, 16, base, d))
    return panel.cut(cq.Workplane("XY").add(cq.Compound.makeCompound(holes)))


def grip_panel(p: ForearmParams = ForearmParams()) -> cq.Workplane:
    """Grey pad in the ulnar window, standing 0.6 mm proud, with concentric contour grooves."""
    x_back = _x_back(p)
    outer = _loft(p, 0.6, p.start_x, x_back)
    inner = _loft(p, -p.wall, p.start_x + 1, x_back - 1)
    pad = outer.cut(inner).intersect(_grip_zone(p, 1.0 - 1.2 / (p.grip_height / 2)))
    groove_outer = _loft(p, 1.0, p.start_x, x_back)
    groove_inner = _loft(p, 0.0, p.start_x, x_back)
    band = groove_outer.cut(groove_inner)
    for i in range(1, p.grip_rings + 1):
        s = 1.0 - i / (p.grip_rings + 1)
        ring = _grip_zone(p, s).cut(_grip_zone(p, s - 0.035))
        pad = pad.cut(band.intersect(ring))
    return pad


def elbow_hub(p: ForearmParams = ForearmParams()) -> cq.Workplane:
    """Elbow housing envelope at the back end: a drum across the arm (axis along Y). Its front fits
    inside the open back of the shell, so the shell wraps over it like a forearm over the elbow."""
    xe = -p.length
    a, _ = p.section(_x_back(p))
    width = 2 * (a - p.wall - p.clearance)
    drum = cq.Workplane("XZ").circle(p.hub_radius).extrude(width / 2, both=True).translate((xe, 0, 0))
    # inside the shell the drum keeps to the shell's inner room; behind the shell it is free
    x_back = _x_back(p)
    room = _loft(p, -p.wall - p.clearance, p.start_x, x_back - 1)
    behind = cq.Workplane("XY").box(200, 200, 200).translate((x_back - 100, 0, 0))
    front = cq.Workplane("XY").box(200, 200, 200).translate((x_back + 100, 0, 0))
    drum = drum.intersect(front).intersect(room).union(drum.intersect(behind))
    cap = cq.Workplane("XZ").circle(p.hub_radius * 0.55).extrude(1.5, both=True).translate((xe, 0, 0))
    return drum.union(cap.translate((0, width / 2 + 1.5, 0))).union(cap.translate((0, -width / 2 - 1.5, 0)))


def _superellipse(x: float, a: float, b: float, zc: float = 0.0, n: float = 4.0, k: int = 48) -> cq.Wire:
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k
        c, s = math.cos(t), math.sin(t)
        pts.append(cq.Vector(x, a * math.copysign(abs(c) ** (2 / n), c), zc + b * math.copysign(abs(s) ** (2 / n), s)))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def wrist_cuff(p: ForearmParams = ForearmParams(), palm_half_width: float = 44.0, palm_z: tuple = (-15.5, 18.0),
               overlap_to: float = 16.0) -> cq.Workplane:
    """White cuff that turns with the hand: blends the round wrist rotor into the flat palm shell, so
    hand and forearm read as one form. Printed with (or glued to) the palm shell, which it overlaps
    from its back edge to x = overlap_to. palm_* are the palm shell's outer bounds (shell.palm_shell)."""
    w = p.wrist
    r = w.outer_diameter / 2 + p.clearance + p.wall
    zc, b = (palm_z[0] + palm_z[1]) / 2, (palm_z[1] - palm_z[0]) / 2
    x_end = -(w.flange_thickness + w.clearance) + 0.4  # just in front of the stator's front face
    wires = [
        cq.Wire.makeCircle(r, cq.Vector(x_end, 0, 0), cq.Vector(1, 0, 0)),
        cq.Wire.makeCircle(r, cq.Vector(1.0, 0, 0), cq.Vector(1, 0, 0)),
        _superellipse(overlap_to, palm_half_width + 0.01, b + 0.01, zc),
    ]
    outer = cq.Workplane("XY").add(cq.Solid.makeLoft(wires, False))
    rotor_room = cq.Workplane("YZ").circle(w.outer_diameter / 2 + p.clearance).extrude(6).translate((x_end - 1, 0, 0))
    palm_room = cq.Workplane("XY").box(overlap_to + 10, 2 * palm_half_width, palm_z[1] - palm_z[0]).translate(((overlap_to + 10) / 2 - 0.01, 0, zc))
    return outer.cut(rotor_room).cut(palm_room)


def forearm_parts(p: ForearmParams = ForearmParams()) -> dict[str, cq.Workplane]:
    return {
        "forearm_shell": forearm_shell(p),
        "forearm_mesh": mesh_panel(p),
        "forearm_grip": grip_panel(p),
        "elbow_hub": elbow_hub(p),
        "forearm_cuff": wrist_cuff(p),
    }


__all__ = ["ForearmParams", "elbow_hub", "forearm_parts", "forearm_shell", "grip_panel", "mesh_panel", "wrist_cuff"]
