"""Offline NumPy model used when optional scikit-learn is unavailable."""
import numpy as np


class NumpyRidge:
    """Standardized ridge regressor used only as an offline fallback."""
    def __init__(self, alpha: float = 35.0):
        self.alpha = alpha

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0)
        self.scale_[self.scale_ == 0] = 1
        Z = (X - self.mean_) / self.scale_
        self.y_mean_ = y.mean()
        A = np.column_stack([np.ones(len(Z)), Z])
        penalty = np.eye(A.shape[1]) * self.alpha
        penalty[0, 0] = 0
        self.coef_ = np.linalg.solve(A.T @ A + penalty, A.T @ (y - self.y_mean_))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        Z = (np.asarray(X, dtype=float) - self.mean_) / self.scale_
        return self.y_mean_ + np.column_stack([np.ones(len(Z)), Z]) @ self.coef_
