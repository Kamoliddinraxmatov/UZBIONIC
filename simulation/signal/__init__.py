"""Synthetic surface-EMG generator for PC-only and bench-replay testing."""

from .synth import Burst, SyntheticEMG, generate_emg, regular_bursts

__all__ = ["Burst", "SyntheticEMG", "generate_emg", "regular_bursts"]
