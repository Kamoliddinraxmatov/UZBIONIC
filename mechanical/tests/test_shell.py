"""Outer shell: valid parts, no collisions with the skeleton or each other in the open hand, joints and
thumb still move freely with the covers on."""

import itertools

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.anthropometry import FINGERS  # noqa: E402
from mechanical.cad.hand import Grip, PalmParams, palm  # noqa: E402
from mechanical.cad.shell import dressed, finger_cover, palm_shell, thumb_cover  # noqa: E402

PP = PalmParams()
TOL = 1e-3


def _collisions(parts):
    return [(a, b) for a, b in itertools.combinations(parts, 2) if parts[a].intersect(parts[b]).val().Volume() > TOL]


@pytest.fixture(scope="module")
def open_hand():
    return dressed(PP, Grip())


def test_shell_parts_are_valid(open_hand):
    for name, part in open_hand.items():
        if name.startswith(("shell_", "pad_")):
            assert part.val().isValid(), name


def test_open_hand_with_shell_has_no_collisions(open_hand):
    assert _collisions(open_hand) == []


@pytest.mark.parametrize("angles", [(30, 30, 30), (60, 70, 50), (90, 90, 0)])
def test_fingers_bend_freely_with_covers_on(angles):
    grip = Grip(fingers={f: angles for f in FINGERS})
    parts = {k: v for k, v in dressed(PP, grip).items() if not k.startswith("thumb") and "thumb" not in k}
    assert _collisions(parts) == []


@pytest.mark.parametrize("rotation", [0.0, 54.0, PP.layout.thumb_opposed_deg])
def test_thumb_cover_clears_palm_through_travel(rotation):
    cover = thumb_cover(PP, rotation)
    assert palm(PP).intersect(cover).val().Volume() < TOL
    assert palm_shell(PP).intersect(cover).val().Volume() < TOL


def test_covers_are_thin_and_light():
    # a cover is a sleeve, not a solid block: its volume stays well under the phalanx's bounding box
    fp = PP.finger_params("middle")
    cover = finger_cover(fp, 0).val()
    assert cover.Volume() < 0.5 * fp.lengths[0] * fp.width * fp.height
