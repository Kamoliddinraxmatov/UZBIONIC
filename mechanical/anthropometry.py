"""Standard (population-average) hand sizes, used until the first user's own hand is measured.

Segment lengths are percentages of hand length (wrist crease to middle fingertip), as tabulated from
Freivalds (32 subjects) in: "A Functional Anatomy Based Kinematic Human Hand Model with Simple Size
Adaptation", DLR, Table II (https://core.ac.uk/download/11151516.pdf).

The default hand length and breadth sit inside the range a prosthetic hand should match to look like a
normal adult hand, 180-198 mm long and 75-90 mm wide (Belter et al. 2013, J. Rehabil. Res. Dev. 50(5),
"Mechanical design and performance specifications of anthropomorphic prosthetic hands: a review").

Everything else here (finger widths and heights, fingertip pad, palm thickness) is a UZBIONIC design
value, marked as such, to be checked against the measured hand. Units: mm.
"""

from __future__ import annotations

from dataclasses import dataclass

# Percent of hand length: (proximal, middle, distal). Thumb has no middle phalanx.
SEGMENT_PERCENT = {
    "thumb": (17.1, 12.1),
    "index": (21.8, 14.1, 8.6),
    "middle": (24.5, 15.8, 9.8),
    "ring": (22.2, 15.3, 9.7),
    "little": (17.7, 10.8, 8.6),
}

FINGERS = ("index", "middle", "ring", "little")

# Design values (not from a source): finger width as a fraction of the finger pitch (palm breadth / 4),
# and height as a fraction of width.
WIDTH_OF_PITCH = {"thumb": 0.90, "index": 0.84, "middle": 0.84, "ring": 0.80, "little": 0.72}
HEIGHT_OF_WIDTH = 0.85


@dataclass(frozen=True)
class HandSize:
    hand_length: float = 190.0  # inside Belter et al. 180-198 mm
    hand_breadth: float = 85.0  # inside Belter et al. 75-90 mm
    # Design value: the source lengths stop at the bone/joint; a soft fingertip pad is added to the distal segment.
    tip_pad: float = 4.0

    @property
    def pitch(self) -> float:
        return self.hand_breadth / 4

    def segments(self, finger: str) -> tuple[float, ...]:
        lengths = [self.hand_length * pct / 100 for pct in SEGMENT_PERCENT[finger]]
        lengths[-1] += self.tip_pad
        return tuple(round(v, 2) for v in lengths)

    def width(self, finger: str) -> float:
        return round(self.pitch * WIDTH_OF_PITCH[finger], 2)

    def height(self, finger: str) -> float:
        return round(self.width(finger) * HEIGHT_OF_WIDTH, 2)

    @property
    def middle_finger_length(self) -> float:
        return sum(self.segments("middle")) - self.tip_pad

    @property
    def palm_length(self) -> float:
        """Wrist crease to the middle finger's MCP joint."""
        return self.hand_length - self.middle_finger_length
