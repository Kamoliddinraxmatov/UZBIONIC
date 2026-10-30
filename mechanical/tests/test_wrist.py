"""Wrist rotator CAD: valid parts, free travel inside the range, hard stop outside it, palm interface."""

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.cad.hand import PalmParams  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402

P = WristParams()
TOL = 1e-3


@pytest.fixture(scope="module")
def the_stator():
    return stator(P)


def test_parts_are_valid(the_stator):
    for part in (the_stator, rotor(P)):
        assert part.val().isValid()
        assert part.val().Volume() > 1000.0


@pytest.mark.parametrize("angle", [-90.0, -45.0, 0.0, 45.0, 90.0])
def test_turns_freely_inside_range(the_stator, angle):
    assert the_stator.intersect(rotor(P, angle)).val().Volume() < TOL


@pytest.mark.parametrize("angle", [-95.0, 95.0, 180.0])
def test_stop_blocks_outside_range(the_stator, angle):
    assert the_stator.intersect(rotor(P, angle)).val().Volume() > 1.0


def test_inconsistent_stop_rejected():
    with pytest.raises(ValueError):
        WristParams(rotation_range_deg=200.0)
    with pytest.raises(ValueError):
        WristParams(stator_length=30.0)


def test_palm_bolt_pattern_matches():
    pp = PalmParams()
    assert pp.bolt_circle == P.bolt_circle
    assert pp.cable_hole / 2 >= P.cable_slot_radius + P.cable_slot_width / 2
