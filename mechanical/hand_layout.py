"""Where the fingers, thumb and wrist sit on the palm, and simple forward kinematics.

Pure Python + NumPy, so the layout can be tested without CAD. The CAD modules build solids from it.

Hand frame (left hand by default, the first user's missing side): origin at the centre of the wrist
face of the palm. X points to the fingers, Z to the back of the hand (palm side is -Z), Y completes a
right-handed frame. With the palm facing down a left hand has its thumb at -Y; a right hand is the
mirror image (thumb at +Y). Units: mm, degrees.

Layout numbers marked "design" are UZBIONIC choices, not measurements.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from mechanical.anthropometry import FINGERS, HandSize


def rot_x(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def chain_tip(lengths, angles_deg) -> np.ndarray:
    """Tip of a planar finger chain in its own frame (X along, pin axes along Y, curl towards -Z).
    Matches mechanical.cad.finger.assembled: a positive angle curls towards the palm."""
    x = z = total = 0.0
    for L, a in zip(lengths, angles_deg):
        total += a
        x += L * math.cos(math.radians(total))
        z -= L * math.sin(math.radians(total))
    return np.array([x, 0.0, z])


@dataclass(frozen=True)
class HandLayout:
    size: HandSize = field(default_factory=HandSize)
    side: str = "left"
    palm_thickness: float = 28.0  # design
    # design: how far each MCP joint sits behind the middle finger's MCP (natural knuckle arc)
    mcp_setback: dict = field(default_factory=lambda: {"index": 3.0, "middle": 0.0, "ring": 3.0, "little": 11.0})
    # Thumb (design). The thumb base turns about an axis parallel to X, like a manually positioned
    # thumb on several commercial hands: 0 deg = lateral (beside the index, key grip),
    # thumb_opposed_deg = opposed (pinch / tripod / power).
    thumb_base_x_frac: float = 0.30  # CMC hub position along the palm, fraction of palm length
    thumb_base_z: float = -1.0  # hub axis height (palm side is negative)
    thumb_metacarpal: float = 38.0  # hub axis to thumb MCP pin (design arm length)
    thumb_abduction_deg: float = 39.0  # angle between thumb and X in the lateral position
    thumb_opposed_deg: float = 108.0
    thumb_mcp_bias_deg: float = 13.0  # thumb MCP pin is turned so the thumb curls slightly towards the fingers

    @property
    def mirror(self) -> float:
        """+1 for a right hand, -1 for a left hand: multiplies every Y coordinate."""
        if self.side not in ("left", "right"):
            raise ValueError("side must be 'left' or 'right'")
        return 1.0 if self.side == "right" else -1.0

    @property
    def palm_length(self) -> float:
        return self.size.palm_length

    @property
    def palm_breadth(self) -> float:
        return self.size.hand_breadth

    def mcp(self, finger: str) -> np.ndarray:
        """MCP pin centre of a long finger. Index sits next to the thumb."""
        k = FINGERS.index(finger)
        y = (1.5 - k) * self.size.pitch * self.mirror  # index nearest the thumb side
        return np.array([self.palm_length - self.mcp_setback[finger], y, 0.0])

    def finger_tip(self, finger: str, angles_deg) -> np.ndarray:
        return self.mcp(finger) + chain_tip(self.size.segments(finger), angles_deg)

    # --- thumb ---
    @property
    def thumb_hub(self) -> np.ndarray:
        """Point on the thumb rotation axis (axis parallel to X) at the palm's thumb-side edge."""
        y = self.palm_breadth / 2 * self.mirror  # thumb side: +Y right hand, -Y left hand
        return np.array([self.palm_length * self.thumb_base_x_frac, y, self.thumb_base_z])

    def thumb_frame(self, rotation_deg: float) -> np.ndarray:
        """Rotation from the thumb's own frame (X along the thumb, Y pin axis, curl to -Z) to the hand frame.

        In the lateral position (rotation 0) the thumb lies in the palm plane pointing forward and
        outward, curling sideways towards the index finger. Turning the base swings it under the palm.
        """
        m = self.mirror
        # thumb's own frame for a RIGHT hand at rotation 0: X forward-outward (+Y), curl towards -Y (the index)
        base = rot_z(self.thumb_abduction_deg) @ rot_x(-90.0) @ rot_y(-self.thumb_mcp_bias_deg)
        r = rot_x(-rotation_deg) @ base  # positive rotation brings the thumb under the palm (-Z)
        if m < 0:
            mir = np.diag([1.0, -1.0, 1.0])
            r = mir @ r @ mir
        return r

    def thumb_mcp(self, rotation_deg: float) -> np.ndarray:
        r = self.thumb_frame(rotation_deg)
        return self.thumb_hub + r @ np.array([self.thumb_metacarpal, 0.0, 0.0])

    def thumb_tip(self, rotation_deg: float, angles_deg) -> np.ndarray:
        r = self.thumb_frame(rotation_deg)
        return self.thumb_mcp(rotation_deg) + r @ chain_tip(self.size.segments("thumb"), angles_deg)


def best_pinch(layout: HandLayout, finger: str = "index", step: float = 5.0):
    """Smallest thumb-tip to fingertip distance over a grid of joint angles in the opposed position.
    Returns (distance, thumb_angles, finger_angles, contact_point)."""
    best = (math.inf, None, None, None)
    rng = np.arange(0.0, 90.0 + 1e-9, step)
    finger_tips = {
        (a, b): layout.finger_tip(finger, (a, b, b * 2 / 3)) for a in rng for b in rng
    }  # DIP follows PIP (tendon-coupled, design assumption)
    for t1 in rng:
        for t2 in rng:
            tt = layout.thumb_tip(layout.thumb_opposed_deg, (t1, t2))
            for key, ft in finger_tips.items():
                d = float(np.linalg.norm(tt - ft))
                if d < best[0]:
                    best = (d, (t1, t2), (key[0], key[1], key[1] * 2 / 3), (tt + ft) / 2)
    return best
