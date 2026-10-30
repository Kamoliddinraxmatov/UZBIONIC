"""R1/R2: pattern recognition on synthetic multi-channel EMG (features, LDA, safety, arm position)."""

import numpy as np
import pytest

from emg.patrec import (
    LDA,
    REST,
    PatternRecognizer,
    PositionAwareRecognizer,
    RecognizerConfig,
    extract,
    majority_vote,
    td_features,
    window_labels,
)
from simulation.signal import Segment, generate_session, make_arm_model, training_protocol

FS = 1000.0
W = 200  # samples in the default 200 ms window at FS


def accuracy(decisions, ends, labels):
    y = window_labels(labels, ends, W)
    k = y >= 0
    return float(np.mean(decisions[k] == y[k]))


# --- features ---------------------------------------------------------------------------

def test_td_features_known_signal():
    t = np.arange(200) / FS
    x = np.sin(2 * np.pi * 10 * t)  # 10 Hz over 0.2 s: 2 full periods
    mav, wl, zc, ssc = td_features(x, deadband=0.0)
    assert mav == pytest.approx(2 / np.pi, rel=0.02)
    assert wl == pytest.approx(8.0, rel=0.02)  # 4 half-swings of amplitude 2
    assert zc in (3, 4)
    assert ssc == 4


def test_deadband_ignores_small_noise():
    x = 0.001 * np.random.default_rng(0).standard_normal(200)
    _, _, zc, ssc = td_features(x, deadband=0.01)
    assert zc == 0 and ssc == 0


def test_extract_shapes_and_window_ends():
    x = np.zeros((1000, 3))
    F, ends = extract(x, FS, window_ms=200, increment_ms=50)
    assert F.shape == (len(ends), 12)
    assert ends[0] == W - 1 and np.all(np.diff(ends) == 50)


def test_window_labels_drop_transitions():
    labels = np.r_[np.zeros(300, int), np.ones(300, int)]
    _, ends = extract(np.zeros((600, 1)), FS)
    y = window_labels(labels, ends, W)
    assert set(np.unique(y)) == {-1, 0, 1}
    assert y[0] == 0 and y[-1] == 1


# --- LDA --------------------------------------------------------------------------------

def test_lda_separates_gaussians_and_probabilities_sum_to_one():
    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(m, 1.0, (200, 4)) for m in (0.0, 4.0, 8.0)])
    y = np.repeat([0, 1, 2], 200)
    lda = LDA().fit(X, y)
    assert np.mean(lda.predict(X) == y) > 0.97
    assert np.allclose(lda.predict_proba(X).sum(axis=1), 1.0)


def test_lda_rejects_bad_shrinkage():
    with pytest.raises(ValueError):
        LDA(shrinkage=1.5)


# --- voting -----------------------------------------------------------------------------

def test_majority_vote_removes_single_glitch():
    d = np.array([1, 1, 1, 2, 1, 1, 1])
    assert np.all(majority_vote(d, 3) == 1)


def test_majority_vote_k1_is_identity():
    d = np.array([0, 2, 1, 2])
    assert np.array_equal(majority_vote(d, 1), d)


# --- end to end on synthetic arm ----------------------------------------------------------

@pytest.fixture(scope="module")
def arm():
    m = make_arm_model(seed=1)
    all_pos = tuple(range(m.n_positions))
    tr0 = generate_session(m, training_protocol(m, (0,), reps=2), FS, seed=11)
    tra = generate_session(m, training_protocol(m, all_pos, reps=2), FS, seed=12)
    te = generate_session(m, training_protocol(m, all_pos, reps=1, hold_s=3.0), FS, seed=13)
    return m, tr0, tra, te


def test_generator_is_deterministic():
    m = make_arm_model(seed=4)
    segs = [Segment(1, 0, 1.0)]
    a = generate_session(m, segs, FS, seed=7)
    b = generate_session(m, segs, FS, seed=7)
    assert np.array_equal(a.emg, b.emg) and np.array_equal(a.acc, b.acc)


def test_eight_channels_classify_held_out_session(arm):
    _, _, tra, te = arm
    rec = PatternRecognizer().fit(tra.emg, tra.labels, FS)
    assert accuracy(*rec.predict(te.emg, FS), te.labels) > 0.95


def test_limb_position_effect_and_multi_position_training(arm):
    _, tr0, tra, te = arm
    one = accuracy(*PatternRecognizer().fit(tr0.emg, tr0.labels, FS).predict(te.emg, FS), te.labels)
    many = accuracy(*PatternRecognizer().fit(tra.emg, tra.labels, FS).predict(te.emg, FS), te.labels)
    assert many > one + 0.1


def test_position_aware_recognizer_not_worse(arm):
    _, _, tra, te = arm
    many = accuracy(*PatternRecognizer().fit(tra.emg, tra.labels, FS).predict(te.emg, FS), te.labels)
    pa = PositionAwareRecognizer().fit(tra.emg, tra.labels, tra.positions, tra.acc, FS)
    assert accuracy(*pa.predict(te.emg, te.acc, FS), te.labels) >= many - 0.02


def test_acc_features_require_acc(arm):
    _, _, tra, _ = arm
    with pytest.raises(ValueError):
        PatternRecognizer(use_acc=True).fit(tra.emg, tra.labels, FS)


def test_rejection_and_voting_reduce_wrong_motions():
    """Safety: with too few channels for the class count, rejection turns wrong motions into rest."""
    m = make_arm_model(n_channels=4, seed=2)
    all_pos = tuple(range(m.n_positions))
    tra = generate_session(m, training_protocol(m, all_pos, reps=2), FS, seed=21)
    te = generate_session(m, training_protocol(m, all_pos, reps=1, hold_s=3.0), FS, seed=22)
    y = None

    def run(cfg):
        nonlocal y
        d, ends = PatternRecognizer(cfg).fit(tra.emg, tra.labels, FS).predict(te.emg, FS)
        y = window_labels(te.labels, ends, W)
        k = y >= 0
        wrong_motion = np.sum((d[k] != REST) & (d[k] != y[k]))
        return wrong_motion, int(np.sum(d[1:] != d[:-1]))

    plain_wrong, plain_flips = run(RecognizerConfig())
    safe_wrong, safe_flips = run(RecognizerConfig(reject_below=0.9, vote=5))
    assert safe_wrong < plain_wrong
    assert safe_flips < plain_flips
