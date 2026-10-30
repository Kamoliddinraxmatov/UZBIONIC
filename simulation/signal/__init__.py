"""Synthetic surface-EMG generator for PC-only and bench-replay testing."""

from .multichannel import ArmModel, Segment, Session, generate_session, make_arm_model, training_protocol
from .synth import Burst, SyntheticEMG, generate_emg, regular_bursts

__all__ = [
    "ArmModel",
    "Burst",
    "Segment",
    "Session",
    "SyntheticEMG",
    "generate_emg",
    "generate_session",
    "make_arm_model",
    "regular_bursts",
    "training_protocol",
]
