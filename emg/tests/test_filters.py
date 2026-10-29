"""AC-3, AC-4: filter attenuation, measured in steady state (second half of the record)."""

import numpy as np
import pytest

from emg.pipeline import bandpass, notch

FS = 2000.0


def _sine(f, seconds=2.0):
    t = np.arange(int(seconds * FS)) / FS
    return np.sin(2 * np.pi * f * t)


def _gain_db(x, y):
    h = len(x) // 2
    return 20 * np.log10(np.sqrt(np.mean(y[h:] ** 2)) / np.sqrt(np.mean(x[h:] ** 2)))


@pytest.mark.parametrize("f", [5.0, 900.0])
def test_bandpass_rejects_out_of_band(f):
    x = _sine(f)
    assert _gain_db(x, bandpass(x, FS)) <= -20.0


def test_bandpass_passes_in_band():
    x = _sine(100.0)
    assert abs(_gain_db(x, bandpass(x, FS))) <= 3.0


def test_notch_removes_50hz():
    x = _sine(50.0)
    assert _gain_db(x, notch(x, FS)) <= -20.0


def test_notch_keeps_100hz():
    x = _sine(100.0)
    assert abs(_gain_db(x, notch(x, FS))) <= 1.0


def test_bandpass_rejects_bad_band():
    with pytest.raises(ValueError):
        bandpass(_sine(100.0), FS, low_hz=500.0, high_hz=450.0)
