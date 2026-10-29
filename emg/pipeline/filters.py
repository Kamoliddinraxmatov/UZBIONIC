"""Causal IIR filters, so results match what a microcontroller can run sample by sample."""

from __future__ import annotations

import numpy as np
from scipy import signal as sps


def bandpass(x: np.ndarray, fs: float, low_hz: float = 20.0, high_hz: float = 450.0, order: int = 4) -> np.ndarray:
    """Butterworth band-pass, applied causally as second-order sections."""
    if not 0 < low_hz < high_hz < fs / 2:
        raise ValueError(f"need 0 < low_hz < high_hz < fs/2, got {low_hz}, {high_hz}, fs={fs}")
    sos = sps.butter(order, (low_hz, high_hz), btype="bandpass", fs=fs, output="sos")
    return sps.sosfilt(sos, x)


def notch(x: np.ndarray, fs: float, f0_hz: float = 50.0, q: float = 30.0) -> np.ndarray:
    """Second-order notch for mains interference (50 Hz in Uzbekistan)."""
    b, a = sps.iirnotch(f0_hz, q, fs=fs)
    return sps.lfilter(b, a, x)
