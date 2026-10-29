"""Mode switching by short co-contraction pulses."""

import pytest

from emg.pipeline import MODE_ACTUATORS, Command, Mode, ModeController

FS = 1000.0  # 1 sample = 1 ms keeps the timing arithmetic readable


def run(ctl, close, open_, n):
    return [ctl.step(close, open_) for _ in range(n)]


def pulse(ctl, ms):
    run(ctl, True, True, ms)


def test_mode_cycle_order():
    assert [m.next() for m in Mode] == [Mode.PINCH, Mode.POINT, Mode.WRIST, Mode.POWER]


def test_short_pulse_switches_mode_then_locks_out():
    ctl = ModeController(FS)
    pulse(ctl, 200)
    assert ctl.mode is Mode.POWER  # switch happens on release, not during
    out = run(ctl, True, False, 300)  # biceps still slightly active while relaxing
    assert ctl.mode is Mode.PINCH
    assert set(out) == {Command.STOP}
    assert ctl.step(True, False) is Command.CLOSE


@pytest.mark.parametrize("ms", [20, 1000])
def test_too_short_or_too_long_does_not_switch(ms):
    ctl = ModeController(FS)
    pulse(ctl, ms)
    run(ctl, False, False, 5)
    assert ctl.mode is Mode.POWER


def test_co_contraction_always_stops():
    ctl = ModeController(FS)
    assert set(run(ctl, True, True, 50)) == {Command.STOP}


def test_full_cycle_returns_to_power():
    ctl = ModeController(FS)
    seen = []
    for _ in range(4):
        pulse(ctl, 200)
        run(ctl, False, False, 400)
        seen.append(ctl.mode)
    assert seen == [Mode.PINCH, Mode.POINT, Mode.WRIST, Mode.POWER]


def test_actuators_follow_mode():
    ctl = ModeController(FS, mode=Mode.WRIST)
    assert ctl.actuators() == MODE_ACTUATORS[Mode.WRIST] == (5,)
    assert len(MODE_ACTUATORS[Mode.POWER]) == 5


def test_limits_stop_motion():
    ctl = ModeController(FS)
    assert ctl.step(True, False, closed_limit=True) is Command.STOP
    assert ctl.step(False, True, open_limit=True) is Command.STOP


def test_fault_latches_and_keeps_mode():
    ctl = ModeController(FS, mode=Mode.PINCH)
    assert ctl.step(True, False, fault=True) is Command.SAFE_STOP
    pulse(ctl, 200)
    run(ctl, False, False, 400)
    assert ctl.mode is Mode.PINCH  # no switching while SAFE
    assert ctl.step(True, False) is Command.SAFE_STOP
    ctl.reset()
    assert ctl.step(True, False) is Command.CLOSE
