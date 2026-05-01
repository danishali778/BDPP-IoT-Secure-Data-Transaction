from __future__ import annotations

import numpy as np

try:
    import tenseal as ts
except ImportError:  # pragma: no cover - exercised only when dependency is missing.
    ts = None


class TenSEALCKKSProcessor:
    """Real CKKS backend using TenSEAL.

    TenSEAL provides encrypted vector operations on top of Microsoft SEAL. This
    class keeps the same public API as the simulator so experiments can switch
    between simulated and real CKKS without changing the pipeline.
    """

    scheme_name = "TENSEAL_CKKS"

    def __init__(
        self,
        poly_modulus_degree: int = 8192,
        coeff_mod_bit_sizes: list[int] | None = None,
        global_scale: float = 2**40,
    ) -> None:
        if ts is None:
            raise RuntimeError("TenSEAL is not installed in the active Python environment.")

        coeffs = coeff_mod_bit_sizes or [60, 40, 40, 60]
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=coeffs,
        )
        self.context.generate_galois_keys()
        self.context.global_scale = global_scale

    def encrypt_vector(self, vector: np.ndarray) -> dict:
        encrypted = ts.ckks_vector(self.context, vector.astype(float).tolist())
        return {
            "ciphertext_hex": encrypted.serialize().hex(),
            "scheme": self.scheme_name,
            "length": int(len(vector)),
        }

    def _load_vector(self, encrypted: dict):
        serialized = bytes.fromhex(encrypted["ciphertext_hex"])
        return ts.ckks_vector_from(self.context, serialized)

    def compute(self, encrypted: dict, operation: str) -> float:
        vector = self._load_vector(encrypted)
        n = int(encrypted["length"])

        if operation == "sum":
            return float(vector.sum().decrypt()[0])
        if operation == "mean":
            return float(vector.sum().decrypt()[0] / n)
        if operation == "variance":
            total = float(vector.sum().decrypt()[0])
            squared_total = float(vector.dot(vector).decrypt()[0])
            mean = total / n
            return squared_total / n - (mean * mean)
        raise ValueError(f"Unsupported operation: {operation}")


def tenseal_available() -> bool:
    return ts is not None

