"""Grip control state machine (MVP: muscle active -> close, relaxed -> open).

Any fault (signal loss, over-current, E-stop, watchdog) forces SAFE. SAFE is left only by an
explicit reset(). What the motor does in SAFE (open, hold or freeze) is decision D-07; here SAFE
commands the motor to stop.
"""

from __future__ import annotations

from enum import Enum


class State(Enum):
    INIT = "init"
    IDLE = "idle"  # hand open, motor stopped
    CLOSING = "closing"
    HOLD = "hold"  # hand closed, motor stopped
    OPENING = "opening"
    SAFE = "safe"


class Command(Enum):
    STOP = "stop"
    OPEN = "open"
    CLOSE = "close"
    SAFE_STOP = "safe_stop"


class GripStateMachine:
    def __init__(self) -> None:
        self.state = State.INIT

    def reset(self) -> None:
        """Operator reset: the only way out of SAFE. Restarts from INIT."""
        self.state = State.INIT

    def step(self, active: bool, fault: bool = False, open_limit: bool = False, closed_limit: bool = False) -> Command:
        if fault or self.state is State.SAFE:
            self.state = State.SAFE
            return Command.SAFE_STOP

        s = self.state
        if s is State.INIT:
            s = State.OPENING  # always start by driving to the open position
        elif s is State.IDLE:
            if active:
                s = State.CLOSING
        elif s is State.CLOSING:
            if not active:
                s = State.OPENING
            elif closed_limit:
                s = State.HOLD
        elif s is State.HOLD:
            if not active:
                s = State.OPENING
        elif s is State.OPENING:
            if active:
                s = State.CLOSING
            elif open_limit:
                s = State.IDLE
        self.state = s

        return {
            State.IDLE: Command.STOP,
            State.HOLD: Command.STOP,
            State.CLOSING: Command.CLOSE,
            State.OPENING: Command.OPEN,
        }[s]
