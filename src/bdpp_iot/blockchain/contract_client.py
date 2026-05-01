from __future__ import annotations

import json
from pathlib import Path

from web3 import Web3


class BDPPLedgerContractClient:
    backend_name = "GANACHE_SOLIDITY"
    error_scale = 1_000_000_000_000

    def __init__(
        self,
        rpc_url: str,
        artifact_path: Path,
        contract_address: str | None = None,
    ) -> None:
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Could not connect to Ethereum RPC: {rpc_url}")

        self.account = self.w3.eth.accounts[0]
        self.artifact_path = artifact_path
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.abi = artifact["abi"]
        self.bytecode = artifact["bytecode"]

        if contract_address:
            self.address = Web3.to_checksum_address(contract_address)
        else:
            self.address = self._deploy()
        self.contract = self.w3.eth.contract(address=self.address, abi=self.abi)

    def _transact(self, function_call):
        tx_hash = function_call.transact({"from": self.account})
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def _deploy(self) -> str:
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact({"from": self.account})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.contractAddress

    def register_user(self, user_address: str) -> None:
        self._transact(self.contract.functions.registerUser(Web3.to_checksum_address(user_address)))

    def revoke_user(self, user_address: str) -> None:
        self._transact(self.contract.functions.revokeUser(Web3.to_checksum_address(user_address)))

    def get_user_version(self, user_address: str) -> int:
        return int(self.contract.functions.getUserVersion(Web3.to_checksum_address(user_address)).call())

    def store_cid(self, task_id: str, cid: str) -> None:
        self._transact(self.contract.functions.storeCID(task_id, cid))

    def get_cid(self, task_id: str) -> str:
        return self.contract.functions.getCID(task_id).call()

    def log_reliability(self, task_id: str, reliable: bool, error_percent: float) -> None:
        error_scaled = int(round(error_percent * self.error_scale))
        self._transact(self.contract.functions.logReliability(task_id, reliable, error_scaled))

    def get_reliability(self, task_id: str) -> dict:
        reliable, error_scaled, timestamp = self.contract.functions.getReliability(task_id).call()
        return {
            "reliable": bool(reliable),
            "error_percent": float(error_scaled) / self.error_scale,
            "timestamp": int(timestamp),
        }

    def log_transaction(self, task_id: str, buyer: str, price: int, data_type: str) -> None:
        self._transact(
            self.contract.functions.logTransaction(
                task_id,
                Web3.to_checksum_address(buyer),
                int(price),
                data_type,
            )
        )

    def get_transaction(self, task_id: str) -> dict:
        buyer, price, data_type, timestamp = self.contract.functions.getTransaction(task_id).call()
        return {
            "buyer": buyer,
            "price": int(price),
            "data_type": data_type,
            "timestamp": int(timestamp),
        }
