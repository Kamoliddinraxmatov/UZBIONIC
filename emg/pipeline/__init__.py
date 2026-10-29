"""Reference sEMG processing pipeline (Python). Firmware DSP is tested against this."""

from .detector import Thresholds, calibrate_thresholds, detect, onsets, signal_ok
from .envelope import moving_rms
from .filters import bandpass, notch
from .pipeline import PipelineConfig, process
from .state_machine import Command, GripStateMachine, State

__all__ = [
    "Command",
    "GripStateMachine",
    "PipelineConfig",
    "State",
    "Thresholds",
    "bandpass",
    "calibrate_thresholds",
    "detect",
    "moving_rms",
    "notch",
    "onsets",
    "process",
    "signal_ok",
]
