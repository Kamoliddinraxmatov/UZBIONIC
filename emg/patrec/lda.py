"""Linear discriminant analysis with a shared, shrinkage-regularised covariance.

LDA is the classifier used in clinical myoelectric pattern recognition (Hargrove et al. 2017).
It is small enough for a microcontroller: prediction is one matrix-vector product per window.
"""

from __future__ import annotations

import numpy as np


class LDA:
    def __init__(self, shrinkage: float = 0.05):
        if not 0.0 <= shrinkage <= 1.0:
            raise ValueError("shrinkage must be in [0, 1]")
        self.shrinkage = shrinkage
        self.classes_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LDA":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        self.mu_ = X.mean(axis=0)
        self.sd_ = X.std(axis=0)
        self.sd_[self.sd_ == 0] = 1.0
        Z = (X - self.mu_) / self.sd_
        means = np.array([Z[y == c].mean(axis=0) for c in self.classes_])
        R = Z - means[np.searchsorted(self.classes_, y)]
        cov = R.T @ R / max(1, len(Z) - len(self.classes_))
        cov = (1 - self.shrinkage) * cov + self.shrinkage * np.eye(cov.shape[0]) * np.trace(cov) / cov.shape[0]
        inv = np.linalg.pinv(cov)
        priors = np.array([np.mean(y == c) for c in self.classes_])
        self.coef_ = means @ inv  # (n_classes, n_features)
        self.intercept_ = -0.5 * np.sum(self.coef_ * means, axis=1) + np.log(priors)
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        Z = (np.asarray(X, dtype=float) - self.mu_) / self.sd_
        return Z @ self.coef_.T + self.intercept_

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        s = self.decision_function(X)
        s = s - s.max(axis=1, keepdims=True)
        p = np.exp(s)
        return p / p.sum(axis=1, keepdims=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.classes_[np.argmax(self.decision_function(X), axis=1)]
