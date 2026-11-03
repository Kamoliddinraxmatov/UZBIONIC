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


def test_cover_mount_holes_stay_in_the_body_and_miss_the_tendon():
    """Each phalanx has two M2 pilot holes for the outer cover, off the return-tendon line and in solid
    material (cutting them removes exactly their own volume)."""
    import math

    from mechanical.cad.finger import _mount_holes, mount_points, phalanx

    p = FingerParams()
    for i in range(len(p.lengths)):
        pts = mount_points(p, i)
        assert len(pts) == 2
        for _, y, z in pts:
            assert abs(y) - p.mount_pilot_diameter / 2 > p.tendon_diameter / 2 + 0.5
            assert z == pytest.approx(p.height / 2)
        body = phalanx(p, i)
        whole = body.union(_mount_holes(p, i).intersect(cq.Workplane("XY").box(500, 500, p.height, centered=True)))
        hole_volume = 2 * math.pi * (p.mount_pilot_diameter / 2) ** 2 * p.mount_depth
        assert whole.val().Volume() - body.val().Volume() == pytest.approx(hole_volume, rel=0.05)
