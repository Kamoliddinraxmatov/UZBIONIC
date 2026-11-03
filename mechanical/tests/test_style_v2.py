"""Look v0.2: the new parts are valid and clear of everything else in the open hand and on the forearm,
including the thumb at both ends of its travel."""

import pytest

cq = pytest.importorskip("cadquery")

from mechanical.cad.hand import Grip, PalmParams  # noqa: E402
from mechanical.cad.style_v2 import dressed_v2, forearm_v2  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402

TOL = 1e-3
NEW = ("shell_palm_back", "shell_palm_frame", "pad_palm", "forearm_sleeve", "forearm_frame", "forearm_pad", "forearm_liner")


@pytest.mark.parametrize("thumb_rotation", [0.0, 108.0])
def test_new_parts_are_clear(thumb_rotation):
    parts = dressed_v2(PalmParams(), Grip(thumb_rotation=thumb_rotation))
    parts.update(forearm_v2())
    parts["wrist_rotor"] = rotor(WristParams())
    parts["wrist_stator"] = stator(WristParams())
    hits = []
    for a in NEW:
        assert parts[a].val().isValid(), a
        for b, other in parts.items():
            if b != a and (b not in NEW or a < b) and parts[a].intersect(other).val().Volume() > TOL:
                hits.append((a, b))
    assert hits == []
