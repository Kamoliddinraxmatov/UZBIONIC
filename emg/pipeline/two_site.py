"""Two-site myoelectric control: one muscle closes the hand, the other opens it.

For a transhumeral (above-elbow) user the sites are biceps (close) and triceps (open). Each site
is processed by the single-channel pipeline with its own rest-calibrated thresholds. Co-contraction
(both active) and rest (neither active) both mean "stop where you are". Any fault latches SAFE until
reset(), as in GripStateMachine.
"""

from __future__ import annotations

from enum import Enum

import numpy as np

from .detector import Thresholds
from .pipeline import PipelineConfig, process
from .state_machine import Command


class Intent(Enum):
    REST = "rest"
    CLOSE = "close"
    OPEN = "open"
    CO_CONTRACTION = "co_contraction"


class TwoSiteState(Enum):
    STOPPED = "stopped"
    CLOSING = "closing"
    OPENING = "opening"
    SAFE = "safe"


def intent(close_active: bool, open_active: bool) -> Intent:
    if close_active and open_active:
        return Intent.CO_CONTRACTION
    if close_active:
        return Intent.CLOSE
    if open_active:
        return Intent.OPEN
    return Intent.REST


class TwoSiteController:
    def __init__(self) -> None:
        self.state = TwoSiteState.STOPPED

    def reset(self) -> None:
        """Operator reset: the only way out of SAFE."""
        self.state = TwoSiteState.STOPPED

    def step(
        self,
        close_active: bool,
        open_active: bool,
        fault: bool = False,
        open_limit: bool = False,
        closed_limit: bool = False,
    ) -> Command:
        if fault or self.state is TwoSiteState.SAFE:
            self.state = TwoSiteState.SAFE
            return Command.SAFE_STOP

        want = intent(close_active, open_active)
        if want is Intent.CLOSE and not closed_limit:
            self.state = TwoSiteState.CLOSING
            return Command.CLOSE
        if want is Intent.OPEN and not open_limit:
            self.state = TwoSiteState.OPENING
            return Command.OPEN
        self.state = TwoSiteState.STOPPED
        return Command.STOP


def process_two_site(
    close_x: np.ndarray,
    open_x: np.ndarray,
    fs: float,
    close_thr: Thresholds,
    open_thr: Thresholds,
    cfg: PipelineConfig = PipelineConfig(),
):
    """Run both channels and the controller offline. Returns (close_env, open_env, close_act, open_act, commands)."""
    _, close_env, close_act = process(close_x, fs, close_thr, cfg)
    _, open_env, open_act = process(open_x, fs, open_thr, cfg)
    ctl = TwoSiteController()
    commands = [ctl.step(bool(c), bool(o)) for c, o in zip(close_act, open_act)]
    return close_env, open_env, close_act, open_act, commands
