"""AC-5, AC-6: burst detection and false activations on synthetic data.

Thresholds are calibrated on a separate rest recording (different seed), as an operator would.
"""

import numpy as np
import pytest

from emg.pipeline import calibrate_thresholds, onsets, process, signal_ok
from simulation.signal import generate_emg, regular_bursts

FS = 2000.0


@pytest.fixture(scope="module")
def thresholds():
    rest = generate_emg(30.0, FS, rest_rms=0.05, mains_amp=0.05, seed=101)
    _, env, _ = process(rest.x, FS, None)
    return calibrate_thresholds(env[int(0.5 * FS):])


def test_detects_all_bursts_with_small_onset_error(thresholds):
    bursts = regular_bursts(20, first_s=1.0, period_s=3.0, duration_s=1.0, amplitude=0.4)
    rec = generate_emg(62.0, FS, bursts, rest_rms=0.05, mains_amp=0.05, seed=7)
    _, _, active = process(rec.x, FS, thresholds)

    detected = onsets(active) / FS
    assert len(detected) == 20
    true_onsets = np.array([b.start_s for b in bursts])
    errors = detected - true_onsets
    assert np.all(errors >= 0), "detector fired before the burst started"
    assert np.max(errors) <= 0.100


def test_no_false_activations_at_rest(thresholds):
    rest = generate_emg(60.0, FS, rest_rms=0.05, mains_amp=0.05, seed=2024)
    _, _, active = process(rest.x, FS, thresholds)
    assert len(onsets(active)) == 0


def test_signal_ok_flags_flat_and_saturated():
    rec = generate_emg(1.0, FS, rest_rms=0.05, seed=1)
    assert signal_ok(rec.x, min_rms=0.01, max_abs=1.0)
    assert not signal_ok(np.zeros(2000), min_rms=0.01, max_abs=1.0)
    assert not signal_ok(np.full(2000, 1.5), min_rms=0.01, max_abs=1.0)
