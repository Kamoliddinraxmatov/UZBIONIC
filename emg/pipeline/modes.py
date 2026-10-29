"""Mode switching for a multi-function hand driven by two EMG sites.

A short co-contraction (biceps and triceps together, then both released) steps to the next mode:
POWER -> PINCH -> POINT -> WRIST -> POWER. In a grip mode the close/open signals move the fingers of
that grip; in WRIST mode they rotate the wrist. Holding the co-contraction longer than the pulse
window does nothing (the hand just stops). After a switch the hand stays stopped for a short lockout
so that muscles relaxing unevenly cannot start a movement. Any fault latches SAFE until reset().

The timing values are tunable design parameters, not measured requirements; they need checking with
the user and a prosthetist.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .state_machine import Command

THUMB, INDEX, MIDDLE, RING, LITTLE, WRIST_ROT = range(6)
ACTUATOR_NAMES = ("thumb", "index", "middle", "ring", "little", "wrist")


class Mode(Enum):
    POWER = "power"  # all fingers: holding a bottle, a handle
    PINCH = "pinch"  # thumb + index: small objects
    POINT = "point"  # all but index: pressing buttons, typing
    WRIST = "wrist"  # close signal rotates one way, open signal the other

    def next(self) -> "Mode":
        order = list(Mode)
        return order[(order.index(self) + 1) % len(order)]


# Actuators driven in each mode.
MODE_ACTUATORS = {
    Mode.POWER: (THUMB, INDEX, MIDDLE, RING, LITTLE),
    Mode.PINCH: (THUMB, INDEX),
    Mode.POINT: (THUMB, MIDDLE, RING, LITTLE),
    Mode.WRIST: (WRIST_ROT,),
}


@dataclass(frozen=True)
class ModeTiming:
    pulse_min_ms: float = 50.0
    pulse_max_ms: float = 800.0
    lockout_ms: float = 300.0


class ModeController:
    def __init__(self, fs: float, timing: ModeTiming = ModeTiming(), mode: Mode = Mode.POWER) -> None:
        self.pulse_min = round(timing.pulse_min_ms * fs / 1000.0)
        self.pulse_max = round(timing.pulse_max_ms * fs / 1000.0)
        self.lockout_len = round(timing.lockout_ms * fs / 1000.0)
        self.mode = mode
        self.safe = False
        self._both = 0  # samples of continuous co-contraction
        self._lockout = 0

    def reset(self) -> None:
        """Operator reset: leaves SAFE, keeps the current mode."""
        self.safe = False
        self._both = 0
        self._lockout = 0

    def step(
        self,
        close_active: bool,
        open_active: bool,
        fault: bool = False,
        open_limit: bool = False,
        closed_limit: bool = False,
    ) -> Command:
        if fault or self.safe:
            self.safe = True
            return Command.SAFE_STOP

        if close_active and open_active:
            self._both += 1
            return Command.STOP

        if self._both:
            if self.pulse_min <= self._both <= self.pulse_max:
                self.mode = self.mode.next()
                self._lockout = self.lockout_len
            self._both = 0

        if self._lockout:
            self._lockout -= 1
            return Command.STOP

        if close_active and not closed_limit:
            return Command.CLOSE
        if open_active and not open_limit:
            return Command.OPEN
        return Command.STOP

    def actuators(self) -> tuple[int, ...]:
        return MODE_ACTUATORS[self.mode]
