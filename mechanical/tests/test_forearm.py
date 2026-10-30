"""Forearm shell: valid parts, fits over the wrist stator, no collisions with the hand, wrist or each
other, and the cuff turns with the hand without touching the forearm side."""

import itertools

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.cad.forearm import ForearmParams, forearm_parts  # noqa: E402
from mechanical.cad.hand import Grip, PalmParams  # noqa: E402
from mechanical.cad.shell import dressed  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402

FP = ForearmParams()
TOL = 1e-3


@pytest.fixture(scope="module")
def arm():
    return forearm_parts(FP)


def _volume(a, b):
    return a.intersect(b).val().Volume()


def test_parts_are_valid(arm):
    for name, part in arm.items():
        assert part.val().isValid(), name


def test_parts_do_not_collide(arm):
    hits = [(a, b) for a, b in itertools.combinations(arm, 2) if _volume(arm[a], arm[b]) > TOL]
    assert hits == []


def test_wrist_end_too_small_is_rejected():
    with pytest.raises(ValueError):
        ForearmParams(stations=((0.144, 29.0, 29.0),) + FP.stations[1:])


@pytest.mark.parametrize("angle", [-90.0, 0.0, 90.0])
def test_clear_of_wrist_and_hand(arm, angle):
    """Forearm parts are fixed; the cuff turns with the hand, so check it at the ends of wrist travel."""
    wp = WristParams()
    fixed = {k: v for k, v in arm.items() if k != "forearm_cuff"}
    turning = dict(dressed(PalmParams(), Grip()))
    turning["wrist_rotor"] = rotor(wp)
    turning["forearm_cuff"] = arm["forearm_cuff"]
    turning = {k: v.rotate((0, 0, 0), (1, 0, 0), angle) for k, v in turning.items()}
    others = {**turning, "wrist_stator": stator(wp)}
    hits = [(a, b) for a in fixed for b in others if _volume(fixed[a], others[b]) > TOL]
    hits += [("forearm_cuff", b) for b in others if b != "forearm_cuff" and _volume(others["forearm_cuff"], others[b]) > TOL]
    assert hits == []
