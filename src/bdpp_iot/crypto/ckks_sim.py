from __future__ import annotations

import numpy as np


class CKKSSimulator:
    """Lightweight CKKS behavior simulator.

    This is not cryptographic CKKS. It models the approximate output behavior needed
    for the methodology experiments without requiring heavy HE libraries.
    """

    scheme_name = "CKKS_SIM"

    def __init__(self, noise_std: float, seed: int) -> None:
        self.noise_std = noise_std
        self.rng = np.random.default_rng(seed)

    def encrypt_vector(self, vector: np.ndarray) -> dict:
        return {"ciphertext": vector.astype(float).tolist(), "scheme": "CKKS_SIM"}

    def compute(self, encrypted: dict, operation: str) -> float:
        vector = np.array(encrypted["ciphertext"], dtype=float)
        if operation == "mean":
            exact = float(np.mean(vector))
        elif operation == "sum":
            exact = float(np.sum(vector))
        elif operation == "variance":
            exact = float(np.var(vector))
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        multiplicative_noise = self.rng.normal(0.0, self.noise_std)
        return exact * (1.0 + multiplicative_noise)
