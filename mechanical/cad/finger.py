"""UZBIONIC parametric finger — our own design (decision D-14), drawn from scratch in CadQuery.

Three phalanges joined by pin hinges. Each joint is a tongue on the child phalanx that turns inside
a fork on the parent. A lip behind each pin rests on a bridge in the parent's fork, so a joint can
curl towards the palm but cannot bend backwards past straight (extension stop). A flexor tendon runs through a channel on the palm side, below the pin axes,
so pulling it curls the finger; an elastic cord through the back-side channel opens it again.

Coordinates: X along the finger (base -> tip), Y across the finger (joint pin axis), Z up from the
palm side (-Z) to the back of the hand (+Z). Units: mm.

DEFAULT SIZES ARE PLACEHOLDERS, NOT MEASUREMENTS. They must be replaced with values measured from the
user's other (right) hand and mirrored, before anything is printed for wearing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class FingerParams:
    # Placeholder sizes (see module docstring).
    lengths: tuple[float, float, float] = (42.0, 26.0, 22.0)  # proximal, middle, distal, pin to pin / pin to tip
    width: float = 17.0
    height: float = 15.0
    # Printing / mechanism parameters.
    tongue_width_ratio: float = 0.4  # tongue width as a fraction of finger width
    clearance: float = 0.3  # gap between moving parts for FDM printing
    pin_diameter: float = 2.0  # e.g. 2 mm steel pin or 1.75 mm filament (then set 1.85 here)
    tendon_diameter: float = 1.5  # channel for braided line
    tendon_offset: float = 2.5  # channel centre distance from the palm/back surface
    base_tongue: bool = True  # proximal phalanx gets a tongue to fit the palm fork
    fillet: float = 1.5
    stop_thickness: float = 2.0  # palm-side bridge in the fork and the matching lip on the tongue
    stop_lip_length: float = 2.0
    names: tuple[str, str, str] = field(default=("proximal", "middle", "distal"))
    # cover mounting (2026-10-30): two blind pilot holes on the back of each phalanx for M2 self-tapping
    # screws, so the outer cover (the owner's visual design) screws onto the skeleton
    mount_pilot_diameter: float = 1.6
    mount_depth: float = 4.5
    mount_offset_ratio: float = 0.28  # hole distance from the centre line, as a fraction of width

    @property
    def tongue_width(self) -> float:
        return self.width * self.tongue_width_ratio

    @property
    def tongue_length(self) -> float:
        """Child body starts this far past the pin, outside the parent's rounded fork cheeks."""
        return self.height / 2 + self.clearance

    @property
    def lip_box(self) -> tuple[float, float, float, float]:
        """Extension-stop lip on the child, behind the pin: (x0, x1, z0, z1) in child coordinates."""
        x1 = -(self.height / 2 + self.clearance)
        x0 = x1 - self.stop_lip_length
        z0 = -self.height / 2 + self.stop_thickness + self.clearance
        return x0, x1, z0, z0 + self.stop_thickness

    @property
    def slot_depth(self) -> float:
        """Fork slot depth so the tongue corners and the stop lip clear the slot floor at any flexion angle."""
        x0, _, z0, z1 = self.lip_box
        lip_reach = max(math.hypot(x0, z0), math.hypot(x0, z1))
        return max(math.hypot(self.tongue_length, self.height / 2), lip_reach) + self.clearance


def _tongue(p: FingerParams) -> cq.Workplane:
    """Rounded tongue around the pin at x=0, reaching to x=tongue_length, with the extension-stop lip."""
    h, tw = p.height, p.tongue_width
    disc = cq.Workplane("XZ").circle(h / 2).extrude(tw / 2, both=True)
    bar = cq.Workplane("XY").box(p.tongue_length, tw, h, centered=(False, True, True))
    x0, x1, z0, z1 = p.lip_box
    # lip plus a web joining it to the disc
    lip = cq.Workplane("XY").box(x1 - x0 + h / 2, tw, z1 - z0, centered=(False, True, False)).translate((x0, 0, z0))
    return disc.union(bar).union(lip)


def phalanx(p: FingerParams, index: int) -> cq.Workplane:
    """One phalanx with its proximal pin at the origin. index 0 = proximal, 2 = distal."""
    L, w, h, c = p.lengths[index], p.width, p.height, p.clearance
    is_tip = index == len(p.lengths) - 1
    has_tongue = index > 0 or p.base_tongue
    start = p.tongue_length if has_tongue else 0.0
    min_len = start + (h / 2 if is_tip else p.slot_depth) + 1.0
    if L < min_len:
        raise ValueError(f"{p.names[index]} phalanx length {L} mm is below {min_len:.1f} mm for height {h} mm")

    if is_tip:
        # body ends in a rounded fingertip
        body = cq.Workplane("XY").box(L - start - h / 2, w, h, centered=(False, True, True)).translate((start, 0, 0))
        # only the far half of the cylinder, so the tip never reaches back into the parent's fork
        tip = (
            cq.Workplane("XZ").circle(h / 2).extrude(w / 2, both=True).translate((L - h / 2, 0, 0))
            .intersect(cq.Workplane("XY").box(h / 2, w, h, centered=(False, True, True)).translate((L - h / 2, 0, 0)))
        )
        body = body.union(tip)
    else:
        # body ends in a rounded fork around the next pin at x=L
        body = cq.Workplane("XY").box(L - start, w, h, centered=(False, True, True)).translate((start, 0, 0))
        knuckle = cq.Workplane("XZ").circle(h / 2).extrude(w / 2, both=True).translate((L, 0, 0))
        body = body.union(knuckle)
        slot_w = p.tongue_width + 2 * c
        slot = cq.Workplane("XY").box(p.slot_depth + h, slot_w, h + 2, centered=(False, True, True)).translate(
            (L - p.slot_depth, 0, 0)
        )
        body = body.cut(slot)
        # palm-side bridge across the slot: the child's lip rests on it when the joint is straight
        x_end = L - (p.height / 2 + c)
        bridge = cq.Workplane("XY").box(x_end - (L - p.slot_depth), w, p.stop_thickness, centered=(False, True, False))
        body = body.union(bridge.translate((L - p.slot_depth, 0, -h / 2)))

    try:
        body = body.edges("|Y").fillet(p.fillet)
    except Exception:  # fillet can fail on very small parameter sets; geometry stays valid without it
        pass

    if has_tongue:
        body = body.union(_tongue(p))

    # pin holes
    pin = cq.Workplane("XZ").circle(p.pin_diameter / 2 + c / 2).extrude(w, both=True)
    if has_tongue:
        body = body.cut(pin)
    if not is_tip:
        body = body.cut(pin.translate((L, 0, 0)))

    # tendon channels: flexor on the palm side, elastic return on the back
    reach = L + h
    for z in (-h / 2 + p.tendon_offset, h / 2 - p.tendon_offset):
        chan = cq.Workplane("YZ").center(0, z).circle(p.tendon_diameter / 2).extrude(reach).translate((-h, 0, 0))
        if is_tip:
            chan = chan.intersect(cq.Workplane("XY").box(L - h / 2 + h, w, h, centered=(False, True, True)).translate((-h, 0, 0)))
        body = body.cut(chan)

    if is_tip:
        # cross hole where the tendons are knotted
        x_anchor = L - h / 2
        body = body.cut(cq.Workplane("XY").center(x_anchor, 0).circle(p.tendon_diameter).extrude(h, both=True))

    return body.cut(_mount_holes(p, index))


def mount_points(p: FingerParams, index: int) -> list[tuple[float, float, float]]:
    """Cover screw points on the back of phalanx `index` (phalanx frame; z is the back surface).

    Two holes, set diagonally and off the centre line so they miss the return-tendon channel. They sit
    on the straight body, clear of the tongue and of the fork slot. A cover designed around the skeleton
    puts its screw bosses here."""
    L, h = p.lengths[index], p.height
    has_tongue = index > 0 or p.base_tongue
    a = (p.tongue_length if has_tongue else 0.0) + 2.5
    b = (L - h / 2 - 1.5) if index == len(p.lengths) - 1 else (L - p.slot_depth - 2.5)
    off = p.width * p.mount_offset_ratio
    if b - a < 3.0:  # short body: both holes side by side in the middle
        xm = (a + b) / 2
        return [(xm, off, h / 2), (xm, -off, h / 2)]
    return [(a + (b - a) * 0.2, off, h / 2), (a + (b - a) * 0.8, -off, h / 2)]


def _mount_holes(p: FingerParams, index: int) -> cq.Workplane | None:
    holes = None
    for x, y, z in mount_points(p, index):
        hole = cq.Workplane("XY").circle(p.mount_pilot_diameter / 2).extrude(p.mount_depth + 1).translate((x, y, z - p.mount_depth))
        holes = hole if holes is None else holes.union(hole)
    return holes


def finger(p: FingerParams = FingerParams()) -> list[cq.Workplane]:
    """The three phalanges, each in its own coordinates (pin at origin), ready to print lying on a side."""
    return [phalanx(p, i) for i in range(len(p.lengths))]


def assembled(p: FingerParams = FingerParams(), angles_deg: tuple[float, ...] = (0.0, 0.0, 0.0)) -> list[cq.Workplane]:
    """Phalanges placed in the hand frame, each flexed by angles_deg[i] about its proximal pin
    (positive = curl towards the palm)."""
    parts, x, z, total = [], 0.0, 0.0, 0.0
    for i, part in enumerate(finger(p)):
        total += angles_deg[i]
        placed = part.rotate((0, 0, 0), (0, 1, 0), total).translate((x, 0, z))
        parts.append(placed)
        x += p.lengths[i] * math.cos(math.radians(total))
        z -= p.lengths[i] * math.sin(math.radians(total))
    return parts


def fork_block(p: FingerParams, back: float) -> cq.Workplane:
    """A parent block that receives a phalanx tongue: it runs from x=-back to a rounded knuckle with
    its pin at the origin, with the same slot, extension-stop bridge, pin hole and tendon channels as a
    phalanx fork. Used for the palm knuckles and the thumb metacarpal."""
    w, h, c = p.width, p.height, p.clearance
    if back < p.slot_depth + 1.0:
        raise ValueError(f"fork block needs at least {p.slot_depth + 1.0:.1f} mm behind the pin, got {back}")
    body = cq.Workplane("XY").box(back, w, h, centered=(False, True, True)).translate((-back, 0, 0))
    body = body.union(cq.Workplane("XZ").circle(h / 2).extrude(w / 2, both=True))
    slot = cq.Workplane("XY").box(p.slot_depth + h, p.tongue_width + 2 * c, h + 2, centered=(False, True, True))
    body = body.cut(slot.translate((-p.slot_depth, 0, 0)))
    x_end = -(h / 2 + c)
    bridge = cq.Workplane("XY").box(x_end + p.slot_depth, w, p.stop_thickness, centered=(False, True, False))
    body = body.union(bridge.translate((-p.slot_depth, 0, -h / 2)))
    try:
        body = body.edges("|Y").fillet(p.fillet)
    except Exception:  # see phalanx()
        pass
    body = body.cut(cq.Workplane("XZ").circle(p.pin_diameter / 2 + c / 2).extrude(w, both=True))
    for z in (-h / 2 + p.tendon_offset, h / 2 - p.tendon_offset):
        chan = cq.Workplane("YZ").center(0, z).circle(p.tendon_diameter / 2).extrude(back + h)
        body = body.cut(chan.translate((-back - 1, 0, 0)))
    return body
