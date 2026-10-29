"""Activation detection: hysteresis thresholds with minimum on/off durations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Thresholds:
    on: float
    off: float

    def __post_init__(self) -> None:
        if not 0 <= self.off < self.on:
            raise ValueError(f"need 0 <= off < on, got on={self.on}, off={self.off}")


def calibrate_thresholds(rest_env: np.ndarray, k_on: float = 4.0, k_off: float = 2.5) -> Thresholds:
    """Thresholds as multiples of the median envelope of a rest recording."""
    level = float(np.median(rest_env))
    return Thresholds(on=k_on * level, off=k_off * level)


def detect(
    env: np.ndarray,
    fs: float,
    thr: Thresholds,
    min_on_ms: float = 50.0,
    min_off_ms: float = 100.0,
) -> np.ndarray:
    """True while active. Turns on after env > thr.on for min_on_ms, off after env < thr.off for min_off_ms."""
    need_on = max(1, int(round(min_on_ms * fs / 1000.0)))
    need_off = max(1, int(round(min_off_ms * fs / 1000.0)))
    out = np.zeros(len(env), dtype=bool)
    active = False
    count = 0
    for i, v in enumerate(env):
        if not active:
            count = count + 1 if v > thr.on else 0
            if count >= need_on:
                active, count = True, 0
        else:
            count = count + 1 if v < thr.off else 0
            if count >= need_off:
                active, count = False, 0
        out[i] = active
    return out


def onsets(mask: np.ndarray) -> np.ndarray:
    """Sample indices where mask goes False -> True."""
    m = np.asarray(mask, dtype=np.int8)
    return np.flatnonzero(np.diff(m, prepend=0) == 1)


def signal_ok(x: np.ndarray, min_rms: float, max_abs: float) -> bool:
    """False if the window looks like a lost electrode/cable (flat) or a saturated input."""
    x = np.asarray(x, dtype=float)
    return bool(np.sqrt(np.mean(x**2)) >= min_rms and np.max(np.abs(x)) < max_abs)
