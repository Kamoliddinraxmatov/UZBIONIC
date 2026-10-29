"""Finger CAD: valid solids, no collisions while curling, extension stop, sane parameters."""

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.cad.finger import FingerParams, assembled, finger  # noqa: E402

P = FingerParams()


@pytest.fixture(scope="module")
def parts():
    return finger(P)


def test_parts_are_valid_solids(parts):
    assert len(parts) == 3
    for part in parts:
        solid = part.val()
        assert solid.isValid()
        assert solid.Volume() > 1000.0


def _overlaps(angles):
    a = assembled(P, angles)
    return [a[i].intersect(a[i + 1]).val().Volume() for i in range(len(a) - 1)]


@pytest.mark.parametrize("angles", [(0, 0, 0), (0, 30, 30), (0, 60, 60), (0, 90, 90), (0, 90, 0), (0, 0, 90)])
def test_no_collision_while_curling(angles):
    assert max(_overlaps(angles)) < 1e-3


@pytest.mark.parametrize("angles", [(0, -5, 0), (0, 0, -5)])
def test_cannot_bend_backwards(angles):
    assert max(_overlaps(angles)) > 1.0


def test_pin_holes_go_through(parts):
    # a pin along Y at the middle phalanx's proximal joint must not hit material
    pin = cq.Workplane("XZ").circle(P.pin_diameter / 2).extrude(P.width, both=True)
    assert parts[1].intersect(pin).val().Volume() < 1e-3


def test_too_short_phalanx_rejected():
    with pytest.raises(ValueError):
        finger(FingerParams(lengths=(42.0, 12.0, 22.0)))
