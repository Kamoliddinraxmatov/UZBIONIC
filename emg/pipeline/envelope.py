"""Signal envelope: causal moving RMS."""

from __future__ import annotations

import numpy as np


def moving_rms(x: np.ndarray, fs: float, window_ms: float = 100.0) -> np.ndarray:
    """RMS over the previous window_ms; the first samples use the shorter available window."""
    w = max(1, int(round(window_ms * fs / 1000.0)))
    c = np.concatenate(([0.0], np.cumsum(np.asarray(x, dtype=float) ** 2)))
    idx = np.arange(1, len(x) + 1)
    lo = np.maximum(idx - w, 0)
    return np.sqrt((c[idx] - c[lo]) / (idx - lo))
