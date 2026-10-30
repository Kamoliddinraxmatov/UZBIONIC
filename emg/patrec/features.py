"""Windowed time-domain features (Hudgins set: MAV, WL, ZC, SSC) for pattern recognition.

All features use only samples inside the window, so a microcontroller can compute them on a
ring buffer. ZC and SSC use an amplitude dead-band so rest noise does not count.
"""

from __future__ import annotations

import numpy as np

FEATURES_PER_CHANNEL = 4


def window_starts(n: int, fs: float, window_ms: float = 200.0, increment_ms: float = 50.0) -> np.ndarray:
    """Start index of each full window; the decision for a window is available at its end."""
    w = int(round(window_ms * fs / 1000.0))
    inc = int(round(increment_ms * fs / 1000.0))
    if w < 2 or inc < 1:
        raise ValueError("window and increment must be at least 2 and 1 samples")
    return np.arange(0, n - w + 1, inc)


def td_features(win: np.ndarray, deadband: float = 0.01) -> np.ndarray:
    """Features of one window of shape (samples, channels) -> (channels * 4,).

    Order per channel: MAV, WL, ZC, SSC.
    """
    win = np.asarray(win, dtype=float)
    if win.ndim == 1:
        win = win[:, None]
    mav = np.mean(np.abs(win), axis=0)
    d = np.diff(win, axis=0)
    wl = np.sum(np.abs(d), axis=0)
    a, b = win[:-1], win[1:]
    zc = np.sum((a * b < 0) & (np.abs(a - b) >= deadband), axis=0)
    d1, d2 = d[:-1], d[1:]
    ssc = np.sum((d1 * d2 < 0) & ((np.abs(d1) >= deadband) | (np.abs(d2) >= deadband)), axis=0)
    return np.stack([mav, wl, zc, ssc], axis=1).reshape(-1)


def extract(
    x: np.ndarray,
    fs: float,
    window_ms: float = 200.0,
    increment_ms: float = 50.0,
    deadband: float = 0.01,
) -> tuple[np.ndarray, np.ndarray]:
    """Feature matrix (n_windows, channels*4) and the end index of each window."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    w = int(round(window_ms * fs / 1000.0))
    starts = window_starts(len(x), fs, window_ms, increment_ms)
    feats = np.array([td_features(x[s : s + w], deadband) for s in starts])
    return feats.reshape(len(starts), -1), starts + w - 1


def window_labels(labels: np.ndarray, ends: np.ndarray, w: int) -> np.ndarray:
    """Label of each window, or -1 when the window spans a label change (excluded from training)."""
    out = np.empty(len(ends), dtype=int)
    for i, e in enumerate(ends):
        seg = labels[e - w + 1 : e + 1]
        out[i] = seg[-1] if np.all(seg == seg[-1]) else -1
    return out


def window_mean(x: np.ndarray, ends: np.ndarray, w: int) -> np.ndarray:
    """Mean of x over each window, e.g. accelerometer -> gravity direction per window."""
    c = np.concatenate([np.zeros((1, x.shape[1])), np.cumsum(x, axis=0)])
    return (c[ends + 1] - c[ends + 1 - w]) / w
