"""AC-7: state machine transitions; any fault -> SAFE, SAFE exits only on reset()."""

import pytest

from emg.pipeline import Command, GripStateMachine, State


def _at(state):
    sm = GripStateMachine()
    sm.state = state
    return sm


def test_starts_by_opening():
    sm = GripStateMachine()
    assert sm.step(active=False) is Command.OPEN
    assert sm.state is State.OPENING


@pytest.mark.parametrize(
    "start, kwargs, end, cmd",
    [
        (State.OPENING, dict(active=False, open_limit=True), State.IDLE, Command.STOP),
        (State.OPENING, dict(active=True), State.CLOSING, Command.CLOSE),
        (State.IDLE, dict(active=False), State.IDLE, Command.STOP),
        (State.IDLE, dict(active=True), State.CLOSING, Command.CLOSE),
        (State.CLOSING, dict(active=True), State.CLOSING, Command.CLOSE),
        (State.CLOSING, dict(active=True, closed_limit=True), State.HOLD, Command.STOP),
        (State.CLOSING, dict(active=False), State.OPENING, Command.OPEN),
        (State.HOLD, dict(active=True), State.HOLD, Command.STOP),
        (State.HOLD, dict(active=False), State.OPENING, Command.OPEN),
    ],
)
def test_transitions(start, kwargs, end, cmd):
    sm = _at(start)
    assert sm.step(**kwargs) is cmd
    assert sm.state is end


@pytest.mark.parametrize("start", list(State))
def test_fault_from_any_state_goes_safe(start):
    sm = _at(start)
    assert sm.step(active=True, fault=True) is Command.SAFE_STOP
    assert sm.state is State.SAFE


def test_safe_is_latched_until_reset():
    sm = _at(State.SAFE)
    for kwargs in (dict(active=False), dict(active=True), dict(active=False, open_limit=True)):
        assert sm.step(**kwargs) is Command.SAFE_STOP
        assert sm.state is State.SAFE
    sm.reset()
    assert sm.step(active=False) is Command.OPEN
    assert sm.state is State.OPENING
