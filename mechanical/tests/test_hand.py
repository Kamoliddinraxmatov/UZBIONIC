"""Hand CAD: valid parts, no collisions in the open hand, thumb travel, joint stops, pinch geometry."""

import itertools

import numpy as np
import pytest

cq = pytest.importorskip("cadquery")

from mechanical.anthropometry import FINGERS  # noqa: E402
from mechanical.cad.hand import Grip, PalmParams, assembled, palm, palm_cover, thumb_metacarpal  # noqa: E402
from mechanical.hand_layout import best_pinch  # noqa: E402

PP = PalmParams()
TOL = 1e-3


@pytest.fixture(scope="module")
def the_palm():
    return palm(PP)


def _collisions(grip):
    parts = assembled(PP, grip)
    return {
        (a, b): v
        for a, b in itertools.combinations(parts, 2)
        if (v := parts[a].intersect(parts[b]).val().Volume()) > TOL
    }


def test_parts_are_valid(the_palm):
    for part in (the_palm, palm_cover(PP), thumb_metacarpal(PP)):
        assert part.val().isValid()
        assert part.val().Volume() > 1000.0


def test_open_hand_has_no_collisions():
    assert _collisions(Grip()) == {}


@pytest.mark.parametrize("rotation", [0.0, 25.0, 54.0, 81.0, PP.layout.thumb_opposed_deg])
def test_thumb_turns_freely_through_its_travel(the_palm, rotation):
    assert the_palm.intersect(thumb_metacarpal(PP, rotation)).val().Volume() < TOL


def test_fingers_cannot_bend_backwards_at_the_knuckle():
    hits = _collisions(Grip(fingers={f: (-5.0, 0.0, 0.0) for f in FINGERS}))
    assert {("palm", f"{f}_proximal") for f in FINGERS} <= set(hits)


def test_pinch_closes_on_a_small_object_without_collision():
    """Just short of the best pinch pose the pads are a few mm apart and nothing collides:
    a thin object (a coin, a card) would be held there."""
    L = PP.layout
    _, thumb, index, _ = best_pinch(L, "index", step=5)
    thumb = (thumb[0] - 5, thumb[1] - 5)
    fingers = {f: (0.0, 0.0, 0.0) for f in FINGERS}
    fingers["index"] = index
    grip = Grip(thumb_rotation=L.thumb_opposed_deg, thumb=thumb, fingers=fingers)
    gap = np.linalg.norm(L.thumb_tip(L.thumb_opposed_deg, thumb) - L.finger_tip("index", index))
    assert gap < 10.0
    assert _collisions(grip) == {}


def test_detent_holes_line_up_with_hub_pin(the_palm):
    """The pin through the thumb hub must point into a palm detent hole at both thumb positions."""
    L = PP.layout
    hub = L.thumb_hub
    x1 = hub[0] + PP.hub_length / 2 + PP.clearance
    for a in (0.0, L.thumb_opposed_deg):
        r = np.radians(a)
        y = hub[1] + L.mirror * PP.detent_radius * np.cos(r)
        z = hub[2] - PP.detent_radius * np.sin(r)
        probe = cq.Workplane("YZ").center(y, z).circle(PP.detent_diameter / 2 - 0.2).extrude(1.0).translate((x1 + 0.2, 0, 0))
        assert the_palm.intersect(probe).val().Volume() < TOL
