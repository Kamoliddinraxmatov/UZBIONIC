"""UZBIONIC hand v0.2: palm, four fingers, a positionable thumb, on standard (population-average) sizes.

Our own design (decision D-14). Sizes come from mechanical.anthropometry (cited there); the layout,
frames and every "design" number come from mechanical.hand_layout. Units: mm.

Ideas taken from competitors (ideas only, no copied geometry; see docs/10-hand-cad.md):
- one flexor tendon per finger pulled by a motor in the palm, elastic return (common in 3D-printed hands);
- a thumb base that turns about an axis along the palm between a lateral and an opposed position,
  locked by detents (several commercial hands position the thumb rotation by hand, not by a motor);
- a hollow palm with a removable back cover for motors and wiring.

Parts:
- palm(): hollow palm with four knuckle forks, the thumb hub lugs and the wrist bolt pattern.
- palm_cover(): back cover.
- thumb_metacarpal(): hub turning on the thumb axle, arm, and fork for the thumb's proximal phalanx.
- assembled(): every part placed in the hand frame for a given grip.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq
import numpy as np
from OCP.gp import gp_Trsf

from mechanical.anthropometry import FINGERS
from mechanical.cad.finger import FingerParams, fork_block
from mechanical.cad.finger import assembled as finger_assembled
from mechanical.hand_layout import HandLayout


@dataclass(frozen=True)
class PalmParams:
    layout: HandLayout = field(default_factory=HandLayout)
    wall: float = 2.5  # design
    corner_radius: float = 8.0  # design
    knuckle_back: float = 14.0  # length of each knuckle block behind its pin
    # thumb hub (design)
    hub_radius: float = 7.0
    hub_length: float = 16.0
    lug_thickness: float = 4.0
    axle_diameter: float = 4.0  # hollow axle: the thumb flexor tendon runs through it
    detent_diameter: float = 2.0
    detent_radius: float = 4.8  # from the axle centre
    thumb_cover_allowance: float = 1.6  # room for the outer shell sleeve over the thumb arm (mechanical.cad.shell)
    # wrist interface (must match mechanical.cad.wrist.WristParams)
    bolt_circle: float = 36.0
    bolt_diameter: float = 3.2  # clearance for M3 screws
    cable_hole: float = 26.0  # covers the wrist rotor cable slot
    clearance: float = 0.3

    def finger_params(self, finger: str) -> FingerParams:
        s = self.layout.size
        return FingerParams(lengths=s.segments(finger), width=s.width(finger), height=s.height(finger))

    def thumb_params(self) -> FingerParams:
        s = self.layout.size
        return FingerParams(
            lengths=s.segments("thumb"), width=s.width("thumb"), height=s.height("thumb"),
            names=("proximal", "distal"),
        )

    @property
    def front(self) -> float:
        """X of the palm body's front face; the knuckle blocks continue from it to the MCP pins."""
        L = self.layout
        return min(L.mcp(f)[0] - self.knuckle_back for f in FINGERS) + 2.0


def place(shape: cq.Workplane, rot: np.ndarray, pos) -> cq.Workplane:
    """Rotate a part by the 3x3 matrix rot about the origin, then move it to pos."""
    t = gp_Trsf()
    r = rot
    t.SetValues(
        float(r[0, 0]), float(r[0, 1]), float(r[0, 2]), float(pos[0]),
        float(r[1, 0]), float(r[1, 1]), float(r[1, 2]), float(pos[1]),
        float(r[2, 0]), float(r[2, 1]), float(r[2, 2]), float(pos[2]),
    )
    return cq.Workplane("XY").add(shape.val().moved(cq.Location(t)))


def _hub_x_range(pp: PalmParams) -> tuple[float, float]:
    hx = pp.layout.thumb_hub[0]
    return hx - pp.hub_length / 2, hx + pp.hub_length / 2


def _detent_angles(pp: PalmParams) -> tuple[float, float]:
    return 0.0, pp.layout.thumb_opposed_deg


def palm(pp: PalmParams = PalmParams()) -> cq.Workplane:
    L = pp.layout
    B, T, w, c = L.palm_breadth, L.palm_thickness, pp.wall, pp.clearance
    front = pp.front
    body = cq.Workplane("XY").box(front, B, T, centered=(False, True, True))
    body = body.edges("|Z").fillet(pp.corner_radius)
    cavity = cq.Workplane("XY").box(front - 2 * w, B - 2 * w, T, centered=(False, True, False))
    body = body.cut(cavity.translate((w, 0, -T / 2 + w)))  # open at the back (+Z) for the cover

    # knuckle forks
    for f in FINGERS:
        fp = pp.finger_params(f)
        m = L.mcp(f)
        back = m[0] - front + w  # flush with the inner face of the front wall
        body = body.union(fork_block(fp, back).translate(tuple(m)))
        # tendon holes from the fork through the front wall into the cavity
        for z in (-fp.height / 2 + fp.tendon_offset, fp.height / 2 - fp.tendon_offset):
            hole = cq.Workplane("YZ").center(m[1], z).circle(fp.tendon_diameter / 2).extrude(back + 2)
            body = body.cut(hole.translate((m[0] - back - 1, 0, 0)))

    # thumb hub: pocket in the side wall, two lugs carrying the axle
    hub = L.thumb_hub
    x0, x1 = _hub_x_range(pp)
    pocket = cq.Workplane("YZ").circle(pp.hub_radius + 2 * c).extrude(x1 - x0 + 2 * c).translate((x0 - c, hub[1], hub[2]))
    swing = cq.Workplane("XY").box(x1 - x0 + 2 * c, 2 * pp.hub_radius + 4 * c, T + 2, centered=(False, True, True))
    # the arm sweeps through the half-space on the thumb side of the axle
    swing = swing.translate((x0 - c, hub[1] + L.mirror * (pp.hub_radius + 2 * c), 0))
    body = body.cut(pocket).cut(swing)
    lug_r = pp.hub_radius
    for xa in (x0 - c - pp.lug_thickness, x1 + c):
        lug = cq.Workplane("YZ").circle(lug_r).extrude(pp.lug_thickness).translate((xa, hub[1], hub[2]))
        web = cq.Workplane("XY").box(pp.lug_thickness, lug_r + w, 2 * lug_r, centered=(False, True, True))
        web = web.translate((xa, hub[1] - L.mirror * (lug_r + w) / 2, hub[2]))
        body = body.union(lug).union(web)
    axle = cq.Workplane("YZ").circle(pp.axle_diameter / 2 + c / 2).extrude(x1 - x0 + 2 * pp.lug_thickness + 4)
    body = body.cut(axle.translate((x0 - pp.lug_thickness - 2, hub[1], hub[2])))
    # detent holes in the front lug's inner face, one per thumb position
    for a in _detent_angles(pp):
        ang = math.radians(a)
        y = hub[1] + L.mirror * pp.detent_radius * math.cos(ang)
        z = hub[2] - pp.detent_radius * math.sin(ang)
        hole = cq.Workplane("YZ").center(y, z).circle(pp.detent_diameter / 2).extrude(1.5)
        body = body.cut(hole.translate((x1 + c, 0, 0)))

    # running clearance for the thumb arm over its whole travel; the lugs are added back afterwards
    lug_zone = None
    for xa in (x0 - c - pp.lug_thickness, x1 + c):
        slab = cq.Workplane("YZ").circle(pp.hub_radius + w).extrude(pp.lug_thickness).translate((xa, hub[1], hub[2]))
        lug_zone = slab if lug_zone is None else lug_zone.union(slab)
    lugs = body.intersect(lug_zone)
    body = body.cut(thumb_sweep(pp)).union(lugs)

    # wrist interface on the back face (x = 0): bolt pattern and cable hole
    face = cq.Workplane("YZ").circle(pp.cable_hole / 2).extrude(w + 1).translate((-0.5, 0, 0))
    body = body.cut(face)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        bolt = cq.Workplane("YZ").center(pp.bolt_circle / 2 * math.cos(a), pp.bolt_circle / 2 * math.sin(a))
        body = body.cut(bolt.circle(pp.bolt_diameter / 2).extrude(w + 1).translate((-0.5, 0, 0)))
    return body


def palm_cover(pp: PalmParams = PalmParams()) -> cq.Workplane:
    """Back cover that closes the palm cavity (sits on the rim at z = +T/2)."""
    L = pp.layout
    w, c = pp.wall, pp.clearance
    plate = cq.Workplane("XY").box(pp.front, L.palm_breadth, w, centered=(False, True, False))
    plate = plate.edges("|Z").fillet(pp.corner_radius)
    # locating lips along the two long sides only, so the front and back rows of motors have room
    lip = cq.Workplane("XY").box(pp.front - 2 * w - 2 * c, L.palm_breadth - 2 * w - 2 * c, w, centered=(False, True, False))
    lip = lip.cut(cq.Workplane("XY").box(pp.front, L.palm_breadth - 4 * w, w, centered=(False, True, False)).translate((-w, 0, 0)))
    cover = plate.translate((0, 0, L.palm_thickness / 2)).union(lip.translate((w + c, 0, L.palm_thickness / 2 - w)))
    # keep the thumb hub area clear
    x0, x1 = _hub_x_range(pp)
    keep_out = cq.Workplane("XY").box(x1 - x0 + 2 * pp.lug_thickness + 4, 2 * pp.hub_radius + 6, 40, centered=(False, True, True))
    return cover.cut(keep_out.translate((x0 - pp.lug_thickness - 2, L.thumb_hub[1], L.thumb_hub[2])))


def thumb_metacarpal(pp: PalmParams = PalmParams(), rotation_deg: float = 0.0, grow: float = 0.0) -> cq.Workplane:
    """Hub on the thumb axle plus the arm to the thumb MCP fork, placed in the hand frame.
    grow > 0 gives a fattened copy, used to cut running clearance into the palm."""
    L = pp.layout
    tp = pp.thumb_params()
    hub = L.thumb_hub
    x0, x1 = _hub_x_range(pp)
    r0 = L.thumb_frame(0.0)
    # arm in the thumb's own frame (pin of the thumb MCP at x = metacarpal length)
    if grow:
        h, wd = tp.height + 2 * grow, tp.width + 2 * grow
        arm = cq.Workplane("XY").box(L.thumb_metacarpal + h / 2, wd, h, centered=(False, True, True))
        arm = arm.translate((-L.thumb_metacarpal, 0, 0))
    else:
        arm = fork_block(tp, L.thumb_metacarpal)
    part = place(arm, r0, L.thumb_mcp(0.0))
    hub_cyl = cq.Workplane("YZ").circle(pp.hub_radius + grow).extrude(x1 - x0).translate((x0, hub[1], hub[2]))
    part = part.union(hub_cyl)
    # trim anything that would rub on the lugs, then bore the axle and the detent pin hole
    for xa, length in ((x0 - pp.lug_thickness - 10, pp.lug_thickness + 10), (x1, pp.lug_thickness + 10)):
        part = part.cut(cq.Workplane("YZ").circle(pp.hub_radius + 6).extrude(length).translate((xa, hub[1], hub[2])))
    if grow:
        return _rotate_thumb(part, L, rotation_deg)
    part = part.cut(cq.Workplane("YZ").circle(pp.axle_diameter / 2 + pp.clearance / 2).extrude(x1 - x0 + 2).translate((x0 - 1, hub[1], hub[2])))
    pin = cq.Workplane("YZ").center(hub[1] + L.mirror * pp.detent_radius, hub[2]).circle(pp.detent_diameter / 2)
    part = part.cut(pin.extrude(x1 - x0 + 2).translate((x0 - 1, 0, 0)))
    return _rotate_thumb(part, L, rotation_deg)


def _rotate_thumb(part: cq.Workplane, L: HandLayout, rotation_deg: float) -> cq.Workplane:
    if not rotation_deg:
        return part
    hub = L.thumb_hub
    # positive rotation swings the thumb under the palm; mirror the sense for a left hand
    return part.rotate(tuple(hub), (hub[0] + 1, hub[1], hub[2]), -rotation_deg * L.mirror)


def thumb_sweep(pp: PalmParams, step_deg: float = 6.0) -> cq.Workplane:
    """Space the thumb metacarpal (plus clearance) sweeps between the lateral and opposed positions."""
    angles = np.arange(-step_deg, pp.layout.thumb_opposed_deg + step_deg + 1e-9, step_deg)
    grow = pp.clearance * 2 + pp.thumb_cover_allowance
    sweep = thumb_metacarpal(pp, float(angles[0]), grow=grow)
    for a in angles[1:]:
        sweep = sweep.union(thumb_metacarpal(pp, float(a), grow=grow))
    return sweep


@dataclass(frozen=True)
class Grip:
    thumb_rotation: float = 0.0
    thumb: tuple[float, float] = (0.0, 0.0)
    fingers: dict = field(default_factory=lambda: {f: (0.0, 0.0, 0.0) for f in FINGERS})


def assembled(pp: PalmParams = PalmParams(), grip: Grip = Grip()) -> dict[str, cq.Workplane]:
    """All hand parts placed in the hand frame. Keys: palm, thumb_metacarpal, <finger>_<phalanx>."""
    L = pp.layout
    parts = {"palm": palm(pp), "thumb_metacarpal": thumb_metacarpal(pp, grip.thumb_rotation)}
    for f in FINGERS:
        fp = pp.finger_params(f)
        for name, part in zip(fp.names, finger_assembled(fp, grip.fingers[f])):
            parts[f"{f}_{name}"] = part.translate(tuple(L.mcp(f)))
    tp = pp.thumb_params()
    r = L.thumb_frame(grip.thumb_rotation)
    for name, part in zip(tp.names, finger_assembled(tp, grip.thumb)):
        parts[f"thumb_{name}"] = place(part, r, L.thumb_mcp(grip.thumb_rotation))
    return parts
