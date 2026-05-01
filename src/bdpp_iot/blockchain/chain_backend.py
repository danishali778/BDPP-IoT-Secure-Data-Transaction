from __future__ import annotations

from pathlib import Path

from web3 import Web3

from bdpp_iot.blockchain.compile_contract import compile_bdpp_ledger
from bdpp_iot.blockchain.contract_client import BDPPLedgerContractClient
from bdpp_iot.config import ExperimentConfig


def create_chain_client(config: ExperimentConfig):
    if not config.use_ganache_blockchain:
        return None

    w3 = Web3(Web3.HTTPProvider(config.ganache_rpc_url))
    if not w3.is_connected():
        return None

    artifact_path = Path(config.contract_artifact_path)
    if not artifact_path.exists():
        artifact_path = compile_bdpp_ledger(artifact_path=artifact_path)
    return BDPPLedgerContractClient(
        rpc_url=config.ganache_rpc_url,
        artifact_path=artifact_path,
        contract_address=config.contract_address or None,
    )

