"""End-to-end offline pipeline: filter -> envelope -> detection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detector import Thresholds, detect
from .envelope import moving_rms
from .filters import bandpass, notch


@dataclass(frozen=True)
class PipelineConfig:
    low_hz: float = 20.0
    high_hz: float = 450.0
    notch_hz: float | None = 50.0
    window_ms: float = 50.0
    min_on_ms: float = 30.0
    min_off_ms: float = 100.0


def process(x: np.ndarray, fs: float, thr: Thresholds | None, cfg: PipelineConfig = PipelineConfig()):
    """Return (filtered, envelope, active). active is None when thr is None (calibration run)."""
    y = bandpass(x, fs, cfg.low_hz, cfg.high_hz)
    if cfg.notch_hz:
        y = notch(y, fs, cfg.notch_hz)
    env = moving_rms(y, fs, cfg.window_ms)
    active = None if thr is None else detect(env, fs, thr, cfg.min_on_ms, cfg.min_off_ms)
    return y, env, active
