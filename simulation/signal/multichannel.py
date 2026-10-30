"""Multi-channel synthetic sEMG + accelerometer for pattern-recognition tests (R1/R2).

Each motion class has a fixed activation pattern across channels (with crosstalk). Each arm
position scales channel gains and adds tonic activity, which is the "limb position effect"
(Fougner et al., IEEE TNSRE 2011). The accelerometer reports the gravity direction for the
position. This is a test signal, not a physiological model: amplitudes are arbitrary units
and the class/position structure is invented to exercise the code, not to predict how many
classes a real transhumeral user can produce.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .synth import _band_noise

DEFAULT_CLASSES = ("rest", "hand_open", "hand_close", "wrist_pronate", "wrist_supinate")


@dataclass(frozen=True)
class ArmModel:
    classes: tuple[str, ...]
    patterns: np.ndarray  # (n_classes, n_channels) activation RMS; row 0 is rest (zeros)
    position_gain: np.ndarray  # (n_positions, n_channels) multiplicative gain
    position_tonic: np.ndarray  # (n_positions, n_channels) extra RMS from holding the arm
    gravity: np.ndarray  # (n_positions, 3) accelerometer reading in g

    @property
    def n_channels(self) -> int:
        return self.patterns.shape[1]

    @property
    def n_positions(self) -> int:
        return self.position_gain.shape[0]


def make_arm_model(
    n_channels: int = 8,
    classes: tuple[str, ...] = DEFAULT_CLASSES,
    n_positions: int = 3,
    amplitude: float = 0.2,
    crosstalk: float = 0.6,
    gain_spread: float = 0.6,
    tonic_rms: float = 0.2,
    seed: int = 0,
) -> ArmModel:
    """Random but reproducible class patterns and position effects.

    Each active class drives two "dominant" channels at amplitude and the rest at up to
    crosstalk * amplitude. Position 0 is the neutral (arm hanging) reference.
    """
    rng = np.random.default_rng(seed)
    n_cls = len(classes)
    patterns = np.zeros((n_cls, n_channels))
    for k in range(1, n_cls):
        row = rng.uniform(0.0, crosstalk, n_channels)
        dom = rng.choice(n_channels, size=min(2, n_channels), replace=False)
        row[dom] = rng.uniform(0.7, 1.0, dom.size)
        patterns[k] = amplitude * row
    gain = np.ones((n_positions, n_channels))
    tonic = np.zeros((n_positions, n_channels))
    for p in range(1, n_positions):
        gain[p] = rng.uniform(1.0 - gain_spread, 1.0 + gain_spread, n_channels)
        tonic[p] = tonic_rms * rng.uniform(0.0, 1.0, n_channels)
    angles = np.linspace(0.0, np.pi / 2, n_positions)  # arm down -> arm forward
    gravity = np.stack([np.sin(angles), np.zeros(n_positions), -np.cos(angles)], axis=1)
    return ArmModel(classes, patterns, gain, tonic, gravity)


@dataclass(frozen=True)
class Segment:
    cls: int
    position: int
    duration_s: float


@dataclass(frozen=True)
class Session:
    emg: np.ndarray  # (n, n_channels)
    acc: np.ndarray  # (n, 3)
    labels: np.ndarray  # (n,) class index
    positions: np.ndarray  # (n,) position index
    fs: float


def generate_session(
    model: ArmModel,
    segments: list[Segment],
    fs: float = 1000.0,
    rest_rms: float = 0.05,
    effort_jitter: float = 0.3,
    acc_noise_g: float = 0.02,
    seed: int = 0,
) -> Session:
    """Concatenate segments; each segment holds one class in one arm position.

    effort_jitter varies contraction strength per segment (relative, uniform +-), so the
    classifier cannot rely on one exact amplitude.
    """
    rng = np.random.default_rng(seed)
    lens = [int(round(s.duration_s * fs)) for s in segments]
    n, ch = sum(lens), model.n_channels
    emg = np.empty((n, ch))
    labels = np.empty(n, dtype=int)
    positions = np.empty(n, dtype=int)
    i = 0
    for seg, m in zip(segments, lens):
        effort = 1.0 + rng.uniform(-effort_jitter, effort_jitter)
        rms = model.position_gain[seg.position] * (effort * model.patterns[seg.cls]) + model.position_tonic[seg.position]
        rms = np.sqrt(rms**2 + rest_rms**2)
        for c in range(ch):
            emg[i : i + m, c] = rms[c] * _band_noise(m, fs, rng)
        labels[i : i + m] = seg.cls
        positions[i : i + m] = seg.position
        i += m
    acc = model.gravity[positions] + acc_noise_g * rng.standard_normal((n, 3))
    return Session(emg, acc, labels, positions, fs)


def training_protocol(
    model: ArmModel,
    positions: tuple[int, ...] = (0,),
    reps: int = 2,
    hold_s: float = 3.0,
) -> list[Segment]:
    """Every class held for hold_s in every listed position, repeated reps times.

    Mirrors a clinical calibration routine (Coapt-style: hold each motion a few seconds).
    """
    return [Segment(c, p, hold_s) for _ in range(reps) for p in positions for c in range(len(model.classes))]
