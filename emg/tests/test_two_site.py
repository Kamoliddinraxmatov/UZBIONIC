"""Two-site control: biceps closes, triceps opens, co-contraction and rest stop, faults latch SAFE."""

import numpy as np
import pytest

from emg.pipeline import (
    Command,
    Intent,
    TwoSiteController,
    TwoSiteState,
    calibrate_thresholds,
    intent,
    process,
    process_two_site,
)
from simulation.signal import Burst, generate_emg

FS = 2000.0


@pytest.mark.parametrize(
    "close_a, open_a, expected",
    [(False, False, Intent.REST), (True, False, Intent.CLOSE), (False, True, Intent.OPEN), (True, True, Intent.CO_CONTRACTION)],
)
def test_intent(close_a, open_a, expected):
    assert intent(close_a, open_a) is expected


@pytest.mark.parametrize(
    "kwargs, cmd, state",
    [
        (dict(close_active=True, open_active=False), Command.CLOSE, TwoSiteState.CLOSING),
        (dict(close_active=False, open_active=True), Command.OPEN, TwoSiteState.OPENING),
        (dict(close_active=False, open_active=False), Command.STOP, TwoSiteState.STOPPED),
        (dict(close_active=True, open_active=True), Command.STOP, TwoSiteState.STOPPED),
        (dict(close_active=True, open_active=False, closed_limit=True), Command.STOP, TwoSiteState.STOPPED),
        (dict(close_active=False, open_active=True, open_limit=True), Command.STOP, TwoSiteState.STOPPED),
    ],
)
def test_controller_step(kwargs, cmd, state):
    ctl = TwoSiteController()
    assert ctl.step(**kwargs) is cmd
    assert ctl.state is state


def test_fault_latches_until_reset():
    ctl = TwoSiteController()
    assert ctl.step(True, False, fault=True) is Command.SAFE_STOP
    assert ctl.step(True, False) is Command.SAFE_STOP
    assert ctl.step(False, True) is Command.SAFE_STOP
    ctl.reset()
    assert ctl.step(False, True) is Command.OPEN


def _calibrate(seed):
    rest = generate_emg(30.0, FS, rest_rms=0.05, mains_amp=0.05, seed=seed)
    _, env, _ = process(rest.x, FS, None)
    return calibrate_thresholds(env[int(0.5 * FS):])


def test_end_to_end_with_crosstalk():
    """Biceps then triceps then both, with 10 % crosstalk from each muscle into the other site."""
    biceps = [Burst(1.0, 1.0, 0.4), Burst(7.0, 1.0, 0.4)]
    triceps = [Burst(4.0, 1.0, 0.4), Burst(7.0, 1.0, 0.4)]
    b = generate_emg(10.0, FS, biceps, rest_rms=0.05, mains_amp=0.05, seed=11)
    t = generate_emg(10.0, FS, triceps, rest_rms=0.05, mains_amp=0.05, seed=12)
    close_x = b.x + 0.1 * t.x
    open_x = t.x + 0.1 * b.x

    *_, commands = process_two_site(close_x, open_x, FS, _calibrate(101), _calibrate(102))
    cmd = np.array([c.value for c in commands])

    def during(t0, t1):
        return set(cmd[int(t0 * FS) : int(t1 * FS)])

    assert during(1.2, 1.9) == {"close"}
    assert during(4.2, 4.9) == {"open"}
    assert during(7.2, 7.9) == {"stop"}  # co-contraction
    assert during(2.5, 3.5) == {"stop"}  # rest
    assert "open" not in during(0.0, 3.5), "biceps crosstalk opened the hand"
    assert "close" not in during(3.5, 6.5), "triceps crosstalk closed the hand"
