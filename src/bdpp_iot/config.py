from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentConfig:
    random_seed: int = 42
    sensor_records: int = 3500
    transaction_records: int = 800
    test_fraction: float = 0.25
    ckks_noise_std: float = 0.012
    ckks_high_noise_std: float = 0.045
    ebr_threshold_percent: float = 2.0
    use_tenseal_ckks: bool = True
    tenseal_poly_modulus_degree: int = 8192
    tenseal_global_scale: float = 2**40
    use_kubo_ipfs: bool = True
    ipfs_binary: str = "ipfs"
    ipfs_repo_path: Path = Path(".ipfs")
    use_ganache_blockchain: bool = True
    ganache_rpc_url: str = "http://127.0.0.1:8545"
    contract_artifact_path: Path = Path("outputs") / "contracts" / "BDPPLedger.json"
    contract_address: str = ""
    pricing_margin: float = 0.15
    min_training_records: int = 50
    output_dir: Path = Path("outputs")
