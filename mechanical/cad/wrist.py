"""UZBIONIC wrist rotator v0.1: turns the whole hand about the forearm axis (pronation / supination).

Our own design (decision D-14). The idea of a powered wrist rotator sitting between hand and forearm is
common to commercial arms; the geometry here is drawn from scratch.

Two parts on the hand's X axis, behind the palm (x < 0):
- stator: cup fixed to the forearm. Holds the drive motor (coaxial) and a bearing at its front.
- rotor: sits in the bearing, takes the motor shaft at its centre and carries the palm on three screws.
A tab under the rotor flange runs in a groove in the stator rim and hits a stop block at the end of
travel, so the hand can never turn further than rotation_range_deg (no cable wind-up).
Cables pass the motor at the side and go through an arc slot in the rotor.

MOTOR AND BEARING SIZES ARE PLACEHOLDER ENVELOPES. Set them from the datasheets of the parts actually
bought (decision D-04) before printing. Units: mm, degrees.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class WristParams:
    outer_diameter: float = 56.0  # design
    stator_length: float = 52.0  # design; must hold bearing, cable gap, motor and back wall
    wall: float = 2.5
    # placeholder envelopes (see module docstring)
    motor_diameter: float = 24.0
    motor_length: float = 30.0
    cable_gap: float = 6.0  # space between motor face and rotor where cables turn into the rotor slot
    shaft_diameter: float = 4.0
    bearing_od: float = 42.0  # e.g. a thin-section 6806 class bearing; confirm from the chosen part
    bearing_id: float = 30.0
    bearing_width: float = 7.0
    # travel and stop (design). Some commercial wrists turn 180 deg; we start with +/-90.
    rotation_range_deg: float = 180.0
    groove_inner: float = 22.5  # radius, outside the bearing
    groove_outer: float = 25.5  # radius
    groove_depth: float = 3.0
    stop_block_deg: float = 140.0
    tab_deg: float = 40.0  # tab_deg + stop_block_deg + range = 360 (checked)
    flange_thickness: float = 4.0
    # interface with the palm (must match mechanical.cad.hand.PalmParams)
    bolt_circle: float = 36.0
    bolt_diameter: float = 2.5  # tap / self-tapping hole for M3 in the rotor
    cable_slot_radius: float = 10.0
    cable_slot_width: float = 5.0
    cable_slot_deg: float = 70.0
    clearance: float = 0.3

    def __post_init__(self) -> None:
        total = self.rotation_range_deg + self.stop_block_deg + self.tab_deg
        if abs(total - 360.0) > 1e-6:
            raise ValueError(f"range + stop block + tab must be 360 deg, got {total}")
        if self.groove_outer + self.wall > self.outer_diameter / 2:
            raise ValueError("groove too close to the outer wall")
        if self.groove_inner < self.bearing_od / 2 + 1.0:
            raise ValueError("groove must sit outside the bearing seat")
        back_wall = self.stator_length - self.flange_thickness - self.clearance - self.bearing_width - self.cable_gap - self.motor_length
        if back_wall < 2.0:
            raise ValueError(f"stator too short for the motor envelope (back wall {back_wall:.1f} mm)")


def _sector(r_in: float, r_out: float, a0: float, a1: float, height: float) -> cq.Workplane:
    """Annular sector in the YZ plane (angles from +Y towards +Z), extruded along +X by height."""
    n = max(8, int(abs(a1 - a0) / 4))
    outer = [(r_out * math.cos(math.radians(a0 + (a1 - a0) * k / n)), r_out * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    inner = [(r_in * math.cos(math.radians(a1 - (a1 - a0) * k / n)), r_in * math.sin(math.radians(a1 - (a1 - a0) * k / n))) for k in range(n + 1)]
    return cq.Workplane("YZ").polyline(outer + inner).close().extrude(height)


def stator(p: WristParams = WristParams()) -> cq.Workplane:
    """Cup from x = -stator_length to x = -flange_thickness; its front rim faces the rotor flange."""
    R, L, c = p.outer_diameter / 2, p.stator_length, p.clearance
    x_front = -p.flange_thickness - c
    body = cq.Workplane("YZ").circle(R).extrude(L - p.flange_thickness - c).translate((-L, 0, 0))
    # bearing seat at the front, motor pocket behind it, cable channel beside the motor
    seat = cq.Workplane("YZ").circle(p.bearing_od / 2).extrude(p.bearing_width + 1).translate((x_front - p.bearing_width, 0, 0))
    x_gap = x_front - p.bearing_width - p.cable_gap
    gap = cq.Workplane("YZ").circle(p.bearing_id / 2).extrude(p.cable_gap + 0.01).translate((x_gap, 0, 0))
    motor = cq.Workplane("YZ").circle(p.motor_diameter / 2 + c).extrude(p.motor_length + 0.01).translate((x_gap - p.motor_length, 0, 0))
    # cable channel along the motor, from the back face into the gap
    cable = cq.Workplane("YZ").center(0, p.motor_diameter / 2 + 3).rect(10, 5).extrude(L + x_gap + 2).translate((-L - 1, 0, 0))
    body = body.cut(gap)
    body = body.cut(seat).cut(motor).cut(cable)
    # groove in the front rim, leaving the stop block (centred on 180 deg, opposite the rotor tab)
    half = p.stop_block_deg / 2
    groove = _sector(p.groove_inner, p.groove_outer, 180 + half, 180 + 360 - half, p.groove_depth + 1)
    body = body.cut(groove.translate((x_front - p.groove_depth, 0, 0)))
    # rear screw holes for the forearm (design: 3 x M3 on the same circle)
    for k in range(3):
        a = math.radians(30 + 120 * k)
        hole = cq.Workplane("YZ").center(p.bolt_circle / 2 * math.cos(a), p.bolt_circle / 2 * math.sin(a)).circle(1.25).extrude(8)
        body = body.cut(hole.translate((-L - 0.01, 0, 0)))
    return body


def rotor(p: WristParams = WristParams(), angle_deg: float = 0.0) -> cq.Workplane:
    """Flange (x = -flange_thickness .. 0) that the palm bolts to, a collar in the bearing bore and the
    stop tab in the stator groove. angle_deg turns it about X (0 = centre of travel)."""
    c = p.clearance
    flange = cq.Workplane("YZ").circle(p.outer_diameter / 2).extrude(p.flange_thickness).translate((-p.flange_thickness, 0, 0))
    collar_len = p.bearing_width
    collar = cq.Workplane("YZ").circle(p.bearing_id / 2).extrude(collar_len + 0.01).translate((-p.flange_thickness - c - collar_len, 0, 0))
    half = p.tab_deg / 2
    # the tab's tip stays one clearance above the groove floor
    tab = _sector(p.groove_inner + c, p.groove_outer - c, -half, half, p.groove_depth + 0.01)
    tab = tab.translate((-p.flange_thickness - p.groove_depth, 0, 0))
    body = flange.union(collar).union(tab)
    # motor shaft bore (round placeholder; make it a D or add a set screw once the motor is known)
    body = body.cut(cq.Workplane("YZ").circle(p.shaft_diameter / 2 + c / 2).extrude(30).translate((-20, 0, 0)))
    # cable slot and palm screw holes
    hw = p.cable_slot_width / 2
    slot = _sector(p.cable_slot_radius - hw, p.cable_slot_radius + hw, 90 - p.cable_slot_deg / 2, 90 + p.cable_slot_deg / 2, 40)
    body = body.cut(slot.translate((-30, 0, 0)))
    for k in range(3):
        a = math.radians(90 + 120 * k)
        hole = cq.Workplane("YZ").center(p.bolt_circle / 2 * math.cos(a), p.bolt_circle / 2 * math.sin(a)).circle(p.bolt_diameter / 2).extrude(p.flange_thickness + 2)
        body = body.cut(hole.translate((-p.flange_thickness - 1, 0, 0)))
    if angle_deg:
        body = body.rotate((0, 0, 0), (1, 0, 0), angle_deg)
    return body
