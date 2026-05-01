from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EBRResult:
    operation: str
    expected: float
    observed: float
    error_percent: float
    threshold_percent: float
    reliable: bool


class ErrorBoundReporter:
    def __init__(self, threshold_percent: float) -> None:
        self.threshold_percent = threshold_percent

    def expected_result(self, vector: np.ndarray, operation: str) -> float:
        if operation == "mean":
            return float(np.mean(vector))
        if operation == "sum":
            return float(np.sum(vector))
        if operation == "variance":
            return float(np.var(vector))
        raise ValueError(f"Unsupported operation: {operation}")

    def check(self, vector: np.ndarray, operation: str, observed: float) -> EBRResult:
        expected = self.expected_result(vector, operation)
        denominator = max(abs(expected), 1e-9)
        error_percent = abs(observed - expected) / denominator * 100.0
        reliable = error_percent <= self.threshold_percent
        return EBRResult(
            operation=operation,
            expected=expected,
            observed=observed,
            error_percent=error_percent,
            threshold_percent=self.threshold_percent,
            reliable=reliable,
        )

