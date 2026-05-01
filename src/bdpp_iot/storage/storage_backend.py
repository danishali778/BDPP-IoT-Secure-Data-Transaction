from __future__ import annotations

from bdpp_iot.config import ExperimentConfig
from bdpp_iot.storage.ipfs_kubo import KuboIPFSStorage
from bdpp_iot.storage.ipfs_sim import IPFSSimulator


def create_storage(config: ExperimentConfig):
    if config.use_kubo_ipfs:
        binary = config.ipfs_binary
        local_binary = "tools/kubo/kubo/ipfs.exe"
        if binary == "ipfs":
            from pathlib import Path

            if Path(local_binary).exists():
                binary = local_binary
        try:
            return KuboIPFSStorage(binary=binary, repo_path=config.ipfs_repo_path)
        except RuntimeError:
            return IPFSSimulator()
    return IPFSSimulator()
