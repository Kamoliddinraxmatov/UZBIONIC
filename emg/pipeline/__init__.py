"""Reference sEMG processing pipeline (Python). Firmware DSP is tested against this."""

from .detector import Thresholds, calibrate_thresholds, detect, onsets, signal_ok
from .envelope import moving_rms
from .filters import bandpass, notch
from .modes import ACTUATOR_NAMES, MODE_ACTUATORS, Mode, ModeController, ModeTiming
from .pipeline import PipelineConfig, process
from .state_machine import Command, GripStateMachine, State
from .two_site import Intent, TwoSiteController, TwoSiteState, intent, process_two_site

__all__ = [
    "ACTUATOR_NAMES",
    "MODE_ACTUATORS",
    "Mode",
    "ModeController",
    "ModeTiming",
    "Command",
    "GripStateMachine",
    "Intent",
    "PipelineConfig",
    "State",
    "Thresholds",
    "TwoSiteController",
    "TwoSiteState",
    "bandpass",
    "calibrate_thresholds",
    "detect",
    "intent",
    "moving_rms",
    "notch",
    "onsets",
    "process",
    "process_two_site",
    "signal_ok",
]
