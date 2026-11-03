"""Standard sizes and hand layout: pure NumPy, runs without CAD."""

import numpy as np
import pytest

from mechanical.anthropometry import FINGERS, SEGMENT_PERCENT, HandSize
from mechanical.hand_layout import HandLayout, best_pinch


def test_default_size_inside_belter_range():
    s = HandSize()
    assert 180 <= s.hand_length <= 198
    assert 75 <= s.hand_breadth <= 90


def test_segments_scale_with_hand_length():
    small, big = HandSize(hand_length=180, tip_pad=0), HandSize(hand_length=198, tip_pad=0)
    for f in SEGMENT_PERCENT:
        ratio = np.array(big.segments(f)) / np.array(small.segments(f))
        assert np.allclose(ratio, 198 / 180, atol=1e-3)


def test_middle_finger_longest_and_palm_positive():
    s = HandSize()
    assert max(FINGERS, key=lambda f: sum(s.segments(f))) == "middle"
    assert 80 < s.palm_length < 110


@pytest.mark.parametrize("side", ["left", "right"])
def test_thumb_on_index_side(side):
    L = HandLayout(side=side)
    assert np.sign(L.thumb_hub[1]) == np.sign(L.mcp("index")[1])
    assert abs(L.mcp("index")[1] - L.thumb_hub[1]) < abs(L.mcp("little")[1] - L.thumb_hub[1])


def test_left_is_mirror_of_right():
    left, right = HandLayout(side="left"), HandLayout(side="right")
    m = np.array([1, -1, 1])
    assert np.allclose(left.thumb_tip(60, (20, 30)), right.thumb_tip(60, (20, 30)) * m)
    assert np.allclose(left.finger_tip("ring", (30, 40, 20)), right.finger_tip("ring", (30, 40, 20)) * m)


def test_opposed_thumb_reaches_index_tip_in_front_of_palm():
    L = HandLayout()
    d, _, _, point = best_pinch(L, "index", step=5)
    assert d < 5.0
    assert point[0] > L.palm_length  # the pinch happens in front of the palm
    assert point[2] < -L.palm_thickness / 2  # and on the palm side


def test_opposed_thumb_reaches_middle_tip_for_tripod():
    assert best_pinch(HandLayout(), "middle", step=5)[0] < 12.0


def test_lateral_thumb_cannot_pinch():
    lateral = HandLayout(thumb_opposed_deg=0.0)
    assert best_pinch(lateral, "index", step=10)[0] > 15.0
