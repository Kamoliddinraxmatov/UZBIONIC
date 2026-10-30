"""Myoelectric pattern recognition (R1/R2): TD features + LDA, rejection, voting, arm position."""

from .features import extract, td_features, window_labels, window_mean, window_starts
from .lda import LDA
from .recognizer import REST, PatternRecognizer, PositionAwareRecognizer, RecognizerConfig, majority_vote

__all__ = [
    "LDA",
    "REST",
    "PatternRecognizer",
    "PositionAwareRecognizer",
    "RecognizerConfig",
    "extract",
    "majority_vote",
    "td_features",
    "window_labels",
    "window_mean",
    "window_starts",
]
