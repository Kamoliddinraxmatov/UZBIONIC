"""Import tool for AI-made visual models: a fake arm, given in metres and turned at random, comes back
along our X axis, at our length, with the hand end at the fingertips."""

import numpy as np
import pytest

trimesh = pytest.importorskip("trimesh")

import tools.import_shell as imp  # noqa: E402


def fake_arm() -> "trimesh.Trimesh":
    forearm = trimesh.creation.cylinder(radius=0.035, height=0.26, sections=48)
    forearm.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    forearm.apply_translation([-0.13, 0, 0])
    hand = trimesh.creation.box([0.19, 0.10, 0.03])  # wider than the forearm, like a spread hand
    hand.apply_translation([0.095, 0, 0])
    arm = trimesh.util.concatenate([forearm, hand])
    rot = trimesh.transformations.random_rotation_matrix(np.random.default_rng(3).random(3))
    arm.apply_transform(rot)
    return arm


def test_align_puts_the_arm_on_our_axis_at_our_length():
    m = imp.align(fake_arm())
    x_elbow, x_tip = imp.target_length()
    b = m.bounds
    assert b[0, 0] == pytest.approx(x_elbow, abs=0.5)
    assert b[1, 0] == pytest.approx(x_tip, abs=0.5)
    # the wide (hand) end is at +X
    x = m.vertices[:, 0]
    assert np.ptp(m.vertices[x > x_tip - 60, 1]) > np.ptp(m.vertices[x < x_elbow + 60, 1])


def test_flip_reverses_the_ends():
    m = imp.align(fake_arm(), flip=True)
    x = m.vertices[:, 0]
    b = m.bounds
    assert np.ptp(m.vertices[x < b[0, 0] + 60, 1]) > np.ptp(m.vertices[x > b[1, 0] - 60, 1])
