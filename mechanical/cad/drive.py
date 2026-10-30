"""Finger drive v0.1: five gearmotors with tendon spools inside the palm (decision D-04, 2026-10-30).

Motor chosen by the owner: Pololu 380:1 Micro Metal Gearmotor HPCB 6V with 12 CPR encoder, side
connector (Pololu #5201). Envelope numbers below are from Pololu's micro metal gearmotor dimension
drawing (gearbox 10 x 12 mm, gearbox length 9 mm, overall length without shaft up to 32.5 mm for the
encoder versions, output shaft 9 mm long, 3 mm D-shaft) and the product page. The encoder end is
modelled as a box reaching 14 mm across with the side connector; check it against the motor in hand.

Layout (design): the motors lie across the palm (axis along Y) in five rows along X, rear to front:
thumb, little, ring, middle, index. Each spool sits right behind its finger's knuckle (same Y), so the
flexor tendon runs straight back along X, under the other motors, and winds onto the bottom of its
spool. A carrier plate under the palm cover holds a rib per motor (shaft through the rib, gearbox face
against it); the encoder connectors point up through slots in the plate.

Units: mm.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq

from mechanical.anthropometry import FINGERS
from mechanical.cad.hand import PalmParams

ROW_ORDER = ("thumb", "little", "ring", "middle", "index")  # rear (wrist) to front (knuckles)


@dataclass(frozen=True)
class MotorEnvelope:
    """Pololu micro metal gearmotor with encoder, from the dimension drawing (see module docstring)."""

    width_x: float = 12.0  # gearbox cross section 12 ...
    height_z: float = 10.0  # ... by 10 mm
    body_length: float = 32.5  # gearbox face to back of encoder (max)
    encoder_length: float = 32.5 - 25.6  # encoder versions are this much longer than plain HPCB ones
    connector_reach: float = 14.0  # across the encoder end, including the side connector
    shaft_length: float = 9.0
    shaft_diameter: float = 3.0


@dataclass(frozen=True)
class DriveParams:
    palm: PalmParams = field(default_factory=PalmParams)
    motor: MotorEnvelope = field(default_factory=MotorEnvelope)
    axis_z: float = 4.5  # design: motor axis height in the palm
    spool_core_radius: float = 5.5  # tendon tension = torque / this radius
    spool_flange_radius: float = 6.5
    spool_width: float = 6.0
    flange_thickness: float = 1.0
    rib_thickness: float = 2.5
    plate_thickness: float = 1.6
    clearance: float = 0.3
    thumb_spool_y_abs: float = 35.5  # design: the thumb tendon is turned inwards to here by a guide

    @property
    def row_pitch(self) -> float:
        L = self.palm
        inner = L.front - 2 * L.wall - 2 * self.clearance
        return inner / len(ROW_ORDER)

    def row_x(self, name: str) -> float:
        return self.palm.wall + self.clearance + self.row_pitch * (ROW_ORDER.index(name) + 0.5)

    def spool_y(self, name: str) -> float:
        L = self.palm.layout
        if name == "thumb":
            return L.mirror * self.thumb_spool_y_abs
        return float(L.mcp(name)[1])

    def body_direction(self, name: str) -> float:
        """+1 if the motor body extends towards +Y from its spool, -1 towards -Y (always towards the middle)."""
        return -1.0 if self.spool_y(name) > 0 else 1.0

    @property
    def tendon_z(self) -> float:
        return self.axis_z - self.spool_core_radius

    def finger_tendon_exit_z(self, name: str) -> float:
        fp = self.palm.finger_params(name)
        return -fp.height / 2 + fp.tendon_offset


def motor(dp: DriveParams, name: str) -> cq.Workplane:
    """Motor envelope (gearbox + can + encoder with connector pointing up) for one row."""
    m, x, ys, d = dp.motor, dp.row_x(name), dp.spool_y(name), dp.body_direction(name)
    face = ys + d * (dp.spool_width / 2 + dp.clearance + dp.rib_thickness)
    main = m.body_length - m.encoder_length
    body = cq.Workplane("XY").box(m.width_x, main, m.height_z).translate((x, face + d * main / 2, dp.axis_z))
    enc_y = face + d * (main + m.encoder_length / 2)
    enc = cq.Workplane("XY").box(m.width_x, m.encoder_length, m.connector_reach, centered=(True, True, False))
    enc = enc.translate((x, enc_y, dp.axis_z - m.height_z / 2))
    shaft = cq.Workplane("XZ").circle(m.shaft_diameter / 2).extrude(m.shaft_length)  # extrudes towards -Y
    shaft = shaft.translate((x, 0, dp.axis_z))
    shaft = shaft.mirror("XZ") if d < 0 else shaft
    shaft = shaft.translate((0, face, 0))
    return body.union(enc).union(shaft)


def spool(dp: DriveParams, name: str) -> cq.Workplane:
    """Tendon spool on the motor shaft: core with a flange each side and a cross hole to tie the tendon."""
    x, ys = dp.row_x(name), dp.spool_y(name)
    core_w = dp.spool_width - 2 * dp.flange_thickness

    def disc(r, w, y0):
        return cq.Workplane("XZ").circle(r).extrude(-w).translate((x, y0, dp.axis_z))

    y0 = ys - dp.spool_width / 2
    s = disc(dp.spool_flange_radius, dp.flange_thickness, y0)
    s = s.union(disc(dp.spool_core_radius, core_w, y0 + dp.flange_thickness))
    s = s.union(disc(dp.spool_flange_radius, dp.flange_thickness, y0 + dp.flange_thickness + core_w))
    bore = cq.Workplane("XZ").circle(dp.motor.shaft_diameter / 2 + dp.clearance / 2).extrude(-(dp.spool_width + 2))
    s = s.cut(bore.translate((x, y0 - 1, dp.axis_z)))
    tie = cq.Workplane("XY").circle(0.8).extrude(2 * dp.spool_core_radius + 2).translate((x, ys, dp.axis_z - dp.spool_core_radius - 1))
    return s.cut(tie)


def carrier(dp: DriveParams) -> cq.Workplane:
    """Plate under the cover with one rib per motor; the shaft passes through the rib."""
    pp = dp.palm
    L = pp.layout
    c = dp.clearance
    x0 = pp.wall + c
    x1 = pp.front - pp.wall - c
    width = L.palm_breadth - 2 * pp.wall - 2 * c
    z_top = dp.axis_z + dp.motor.height_z / 2 + c
    plate = cq.Workplane("XY").box(x1 - x0, width, dp.plate_thickness, centered=(False, True, False)).translate((x0, 0, z_top))
    rib_z0 = dp.axis_z - dp.motor.height_z / 2
    for name in ROW_ORDER:
        x, ys, d = dp.row_x(name), dp.spool_y(name), dp.body_direction(name)
        y_rib = ys + d * (dp.spool_width / 2 + c + dp.rib_thickness / 2)
        rib = cq.Workplane("XY").box(dp.motor.width_x, dp.rib_thickness, z_top - rib_z0 + 0.01, centered=(True, True, False))
        rib = rib.translate((x, y_rib, rib_z0))
        hole = cq.Workplane("XZ").circle(dp.motor.shaft_diameter / 2 + c).extrude(dp.rib_thickness + 2, both=True)
        plate = plate.union(rib).cut(hole.translate((x, y_rib, dp.axis_z)))
        # slot for the encoder connector
        enc_y = ys + d * (dp.spool_width / 2 + c + dp.rib_thickness + dp.motor.body_length - dp.motor.encoder_length / 2)
        slot = cq.Workplane("XY").box(dp.motor.width_x + 2 * c, dp.motor.encoder_length + 2 * c, 10).translate((x, enc_y, z_top))
        plate = plate.cut(slot)
        # clearance above the spool flanges
        well = cq.Workplane("XY").box(2 * (dp.spool_flange_radius + c), dp.spool_width + 2 * c, 10).translate((x, ys, z_top))
        plate = plate.cut(well)
    return plate


def tendon(dp: DriveParams, name: str, radius: float = 0.5) -> cq.Workplane:
    """Straight flexor tendon path from the finger's knuckle fork to the bottom of its spool (for checks
    and pictures). The thumb's path, through its hollow axle and a guide, is not modelled yet."""
    if name == "thumb":
        raise ValueError("thumb tendon routing is not modelled yet")
    pp = dp.palm
    m = pp.layout.mcp(name)
    start = cq.Vector(pp.front, m[1], dp.finger_tendon_exit_z(name))
    end = cq.Vector(dp.row_x(name), dp.spool_y(name), dp.tendon_z)
    direction = end - start
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(radius, direction.Length, start, direction.normalized()))


def drive_parts(dp: DriveParams = DriveParams()) -> dict[str, cq.Workplane]:
    parts = {"carrier": carrier(dp)}
    for name in ROW_ORDER:
        parts[f"motor_{name}"] = motor(dp, name)
        parts[f"spool_{name}"] = spool(dp, name)
    return parts


def tendon_tension_n(dp: DriveParams, torque_kgcm: float) -> float:
    """Tendon pull for a motor output torque (kg*cm), on the spool core."""
    return torque_kgcm * 9.80665 / 100 / (dp.spool_core_radius / 1000)


__all__ = ["DriveParams", "MotorEnvelope", "ROW_ORDER", "FINGERS", "carrier", "drive_parts", "motor", "spool", "tendon", "tendon_tension_n"]
