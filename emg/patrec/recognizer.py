"""Pattern recognizer: features -> LDA -> confidence rejection -> majority vote.

Safety rule (R1 #5 in docs/research): when the classifier is not confident, the output is
`rest` (no motion), never a guess. Majority voting trades a little latency for fewer
spurious class flips.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass

import numpy as np

from .features import extract, window_labels, window_mean
from .lda import LDA

REST = 0


@dataclass(frozen=True)
class RecognizerConfig:
    window_ms: float = 200.0
    increment_ms: float = 50.0
    deadband: float = 0.01
    shrinkage: float = 0.05
    reject_below: float = 0.0  # posterior threshold; 0 disables rejection
    vote: int = 1  # majority vote over this many decisions; 1 disables


def majority_vote(decisions: np.ndarray, k: int) -> np.ndarray:
    """Causal majority vote over the last k decisions (ties keep the newest decision)."""
    if k <= 1:
        return np.asarray(decisions).copy()
    buf: deque = deque(maxlen=k)
    out = np.empty(len(decisions), dtype=int)
    for i, d in enumerate(decisions):
        buf.append(int(d))
        counts = Counter(buf)
        best = max(counts.values())
        out[i] = next(c for c in reversed(buf) if counts[c] == best)
    return out


class PatternRecognizer:
    """One LDA over EMG features (optionally with accelerometer features appended)."""

    def __init__(self, cfg: RecognizerConfig = RecognizerConfig(), use_acc: bool = False):
        self.cfg = cfg
        self.use_acc = use_acc

    def _w(self, fs: float) -> int:
        return int(round(self.cfg.window_ms * fs / 1000.0))

    def features(self, emg: np.ndarray, fs: float, acc: np.ndarray | None = None):
        F, ends = extract(emg, fs, self.cfg.window_ms, self.cfg.increment_ms, self.cfg.deadband)
        if self.use_acc:
            if acc is None:
                raise ValueError("use_acc=True needs accelerometer data")
            F = np.hstack([F, window_mean(acc, ends, self._w(fs))])
        return F, ends

    def fit(self, emg: np.ndarray, labels: np.ndarray, fs: float, acc: np.ndarray | None = None):
        F, ends = self.features(emg, fs, acc)
        y = window_labels(labels, ends, self._w(fs))
        keep = y >= 0
        self.lda_ = LDA(self.cfg.shrinkage).fit(F[keep], y[keep])
        return self

    def decide(self, F: np.ndarray) -> np.ndarray:
        p = self.lda_.predict_proba(F)
        d = self.lda_.classes_[np.argmax(p, axis=1)]
        if self.cfg.reject_below > 0:
            d = np.where(p.max(axis=1) < self.cfg.reject_below, REST, d)
        return majority_vote(d, self.cfg.vote)

    def predict(self, emg: np.ndarray, fs: float, acc: np.ndarray | None = None):
        """Decision per window and the sample index at which each decision is available."""
        F, ends = self.features(emg, fs, acc)
        return self.decide(F), ends


class PositionAwareRecognizer:
    """Two stages (Fougner et al. 2011 idea): accelerometer picks the arm position, then a
    per-position EMG classifier decides the motion. Needs position labels at calibration.
    """

    def __init__(self, cfg: RecognizerConfig = RecognizerConfig()):
        self.cfg = cfg

    def fit(self, emg, labels, positions, acc, fs: float):
        base = PatternRecognizer(self.cfg)
        F, ends = base.features(emg, fs)
        w = base._w(fs)
        y = window_labels(labels, ends, w)
        pos = window_labels(positions, ends, w)
        g = window_mean(acc, ends, w)
        keep = (y >= 0) & (pos >= 0)
        self.pos_lda_ = LDA(self.cfg.shrinkage).fit(g[keep], pos[keep])
        self.by_pos_ = {int(p): LDA(self.cfg.shrinkage).fit(F[keep & (pos == p)], y[keep & (pos == p)]) for p in np.unique(pos[keep])}
        self._base = base
        return self

    def predict(self, emg, acc, fs: float):
        F, ends = self._base.features(emg, fs)
        g = window_mean(acc, ends, self._base._w(fs))
        pos = self.pos_lda_.predict(g)
        d = np.empty(len(F), dtype=int)
        for p, lda in self.by_pos_.items():
            m = pos == p
            if not np.any(m):
                continue
            pr = lda.predict_proba(F[m])
            dm = lda.classes_[np.argmax(pr, axis=1)]
            if self.cfg.reject_below > 0:
                dm = np.where(pr.max(axis=1) < self.cfg.reject_below, REST, dm)
            d[m] = dm
        return majority_vote(d, self.cfg.vote), ends
