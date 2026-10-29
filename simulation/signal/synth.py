"""Synthetic sEMG: band-limited noise at rest level plus amplitude-modulated activation bursts.

This is a test signal, not a physiological model. Amplitudes are in arbitrary units; the
band (20-450 Hz) is a working assumption (A1 in docs/06) to be confirmed against literature.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal as sps

EMG_BAND_HZ = (20.0, 450.0)


@dataclass(frozen=True)
class Burst:
    start_s: float
    duration_s: float
    amplitude: float  # RMS of the burst component, arbitrary units


@dataclass(frozen=True)
class SyntheticEMG:
    t: np.ndarray
    x: np.ndarray
    active: np.ndarray  # ground-truth mask, True inside bursts
    fs: float
    bursts: tuple[Burst, ...]


def _band_noise(n: int, fs: float, rng: np.random.Generator) -> np.ndarray:
    """Unit-RMS white noise band-limited to EMG_BAND_HZ."""
    sos = sps.butter(4, EMG_BAND_HZ, btype="bandpass", fs=fs, output="sos")
    y = sps.sosfiltfilt(sos, rng.standard_normal(n))
    return y / np.sqrt(np.mean(y**2))


def _envelope(n: int, fs: float, burst: Burst, ramp_s: float) -> np.ndarray:
    """Trapezoid envelope with raised-cosine ramps of ramp_s at each edge."""
    env = np.zeros(n)
    i0 = int(round(burst.start_s * fs))
    i1 = min(n, int(round((burst.start_s + burst.duration_s) * fs)))
    if i1 <= i0:
        return env
    env[i0:i1] = 1.0
    r = max(1, min(int(round(ramp_s * fs)), (i1 - i0) // 2))
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, r))
    env[i0 : i0 + r] = ramp
    env[i1 - r : i1] = ramp[::-1]
    return env


def generate_emg(
    duration_s: float,
    fs: float = 2000.0,
    bursts: list[Burst] | tuple[Burst, ...] = (),
    rest_rms: float = 0.05,
    mains_amp: float = 0.0,
    mains_hz: float = 50.0,
    ramp_s: float = 0.03,
    seed: int = 0,
) -> SyntheticEMG:
    """Generate a reproducible synthetic sEMG record. Same arguments + seed -> identical output."""
    rng = np.random.default_rng(seed)
    n = int(round(duration_s * fs))
    t = np.arange(n) / fs
    x = rest_rms * _band_noise(n, fs, rng)
    active = np.zeros(n, dtype=bool)
    for b in bursts:
        env = _envelope(n, fs, b, ramp_s)
        x = x + b.amplitude * env * _band_noise(n, fs, rng)
        i0 = int(round(b.start_s * fs))
        i1 = min(n, int(round((b.start_s + b.duration_s) * fs)))
        active[i0:i1] = True
    if mains_amp:
        x = x + mains_amp * np.sin(2 * np.pi * mains_hz * t + rng.uniform(0, 2 * np.pi))
    return SyntheticEMG(t=t, x=x, active=active, fs=fs, bursts=tuple(bursts))


def regular_bursts(
    count: int,
    first_s: float = 1.0,
    period_s: float = 3.0,
    duration_s: float = 1.0,
    amplitude: float = 0.5,
) -> list[Burst]:
    """Evenly spaced bursts, e.g. for detection-rate tests."""
    return [Burst(first_s + k * period_s, duration_s, amplitude) for k in range(count)]
