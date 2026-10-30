"""Finger drive: motors, spools and carrier fit inside the palm without collisions; tendons run clear."""

import itertools

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.anthropometry import FINGERS  # noqa: E402
from mechanical.cad.drive import ROW_ORDER, DriveParams, drive_parts, tendon, tendon_tension_n  # noqa: E402
from mechanical.cad.hand import palm, palm_cover  # noqa: E402

DP = DriveParams()
TOL = 1e-3


@pytest.fixture(scope="module")
def parts():
    return drive_parts(DP)


@pytest.fixture(scope="module")
def shell():
    return {"palm": palm(DP.palm), "cover": palm_cover(DP.palm)}


def test_parts_are_valid(parts):
    for name, part in parts.items():
        assert part.val().isValid(), name


def test_drive_parts_do_not_collide_with_each_other(parts):
    for a, b in itertools.combinations(parts, 2):
        # a spool sits on its own motor's shaft: that overlap is intended
        if any({a, b} == {f"motor_{n}", f"spool_{n}"} for n in ROW_ORDER):
            continue
        assert parts[a].intersect(parts[b]).val().Volume() < TOL, (a, b)


def test_drive_fits_inside_palm_and_cover(parts, shell):
    for name, part in parts.items():
        for s_name, s in shell.items():
            assert part.intersect(s).val().Volume() < TOL, (name, s_name)


@pytest.mark.parametrize("finger", FINGERS)
def test_tendon_runs_clear_to_its_spool(parts, finger):
    t = tendon(DP, finger, radius=0.4)
    for name, part in parts.items():
        if name in (f"spool_{finger}", f"motor_{finger}"):
            continue
        assert t.intersect(part).val().Volume() < TOL, (finger, name)


def test_each_spool_is_behind_its_finger():
    for f in FINGERS:
        assert DP.spool_y(f) == pytest.approx(DP.palm.layout.mcp(f)[1])
    assert len(set(ROW_ORDER)) == 5


def test_tendon_pull_at_gearbox_limit():
    # Pololu: keep instantaneous torque on the 380:1 gearbox under 2.5 kg*cm
    assert 40 < tendon_tension_n(DP, 2.5) < 50
