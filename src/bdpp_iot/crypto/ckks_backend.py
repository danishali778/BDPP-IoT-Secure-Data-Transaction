from __future__ import annotations

from bdpp_iot.config import ExperimentConfig
from bdpp_iot.crypto.ckks_sim import CKKSSimulator
from bdpp_iot.crypto.ckks_tenseal import TenSEALCKKSProcessor, tenseal_available


def create_ckks_processor(config: ExperimentConfig):
    if config.use_tenseal_ckks and tenseal_available():
        return TenSEALCKKSProcessor(
            poly_modulus_degree=config.tenseal_poly_modulus_degree,
            global_scale=config.tenseal_global_scale,
        )
    return CKKSSimulator(config.ckks_noise_std, config.random_seed)

