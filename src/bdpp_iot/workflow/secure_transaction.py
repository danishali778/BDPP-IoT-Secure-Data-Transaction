from __future__ import annotations

import pandas as pd

from bdpp_iot.access_control.ma_abe import MultiAuthorityAccessControl
from bdpp_iot.blockchain.chain_backend import create_chain_client
from bdpp_iot.blockchain.ledger import Ledger
from bdpp_iot.config import ExperimentConfig
from bdpp_iot.crypto.ckks_backend import create_ckks_processor
from bdpp_iot.crypto.ebr import ErrorBoundReporter
from bdpp_iot.storage.storage_backend import create_storage


def run_secure_transaction_demo(records: pd.DataFrame, config: ExperimentConfig) -> dict:
    ledger = Ledger()
    storage = create_storage(config)
    access = MultiAuthorityAccessControl(ledger)

    policy = "research_lab AND cardiology_researcher AND heart_rate"
    valid_key = access.issue_key(
        "researcher_valid",
        {"research_lab", "cardiology_researcher", "heart_rate", "remote"},
    )
    revoked_key = access.issue_key(
        "researcher_revoked",
        {"research_lab", "cardiology_researcher", "heart_rate", "remote"},
    )
    ledger.revoke_user("researcher_revoked")

    vector = records["heart_rate"].head(1440).to_numpy(dtype=float)
    ckks = create_ckks_processor(config)
    abe_ciphertext = access.encrypt_key("session_key_heart_rate", policy)
    encrypted_payload = ckks.encrypt_vector(vector)
    cid = storage.add(encrypted_payload)
    ledger.store_cid("task_heart_rate_daily_mean", cid)

    chain = create_chain_client(config)
    chain_backend = "SIM_LEDGER"
    contract_address = ""
    onchain_cid = ""
    onchain_valid_version = 1
    onchain_revoked_version = 2
    valid_eth_address = "0x0000000000000000000000000000000000000000"
    revoked_eth_address = "0x0000000000000000000000000000000000000000"

    if chain is not None:
        chain_backend = chain.backend_name
        contract_address = chain.address
        accounts = chain.w3.eth.accounts
        valid_eth_address = accounts[1]
        revoked_eth_address = accounts[2]
        chain.register_user(valid_eth_address)
        chain.register_user(revoked_eth_address)
        chain.revoke_user(revoked_eth_address)
        onchain_valid_version = chain.get_user_version(valid_eth_address)
        onchain_revoked_version = chain.get_user_version(revoked_eth_address)
        chain.store_cid("task_heart_rate_daily_mean", cid)
        onchain_cid = chain.get_cid("task_heart_rate_daily_mean")

    valid_allowed = access.can_decrypt(valid_key, policy, check_revocation=True)
    revoked_allowed = access.can_decrypt(revoked_key, policy, check_revocation=True)

    observed = ckks.compute(storage.get(cid), "mean")
    ebr = ErrorBoundReporter(config.ebr_threshold_percent).check(vector, "mean", observed)

    transaction = {
        "task_id": "task_heart_rate_daily_mean",
        "cid": cid,
        "onchain_cid": onchain_cid,
        "operation": "mean",
        "abe_policy": abe_ciphertext.policy,
        "abe_encrypted_key_ref": abe_ciphertext.encrypted_key_ref,
        "abe_required_authorities": len(abe_ciphertext.required_authorities),
        "ckks_backend": getattr(ckks, "scheme_name", ckks.__class__.__name__),
        "storage_backend": getattr(storage, "scheme_name", storage.__class__.__name__),
        "blockchain_backend": chain_backend,
        "contract_address": contract_address,
        "valid_eth_address": valid_eth_address,
        "revoked_eth_address": revoked_eth_address,
        "onchain_valid_version": onchain_valid_version,
        "onchain_revoked_version": onchain_revoked_version,
        "valid_user_allowed": int(valid_allowed and access.decrypt_key(abe_ciphertext, valid_key)),
        "revoked_user_allowed": int(revoked_allowed and access.decrypt_key(abe_ciphertext, revoked_key)),
        "expected_result": ebr.expected,
        "observed_result": ebr.observed,
        "error_percent": ebr.error_percent,
        "reliable": int(ebr.reliable),
        "records_processed": int(len(vector)),
    }
    ledger.log_reliability(transaction)
    ledger.log_transaction(
        {
            "task_id": transaction["task_id"],
            "buyer": valid_key.user_id,
            "data_type": "heart_rate",
            "status": "completed" if valid_allowed and ebr.reliable else "blocked",
        }
    )
    if chain is not None:
        chain.log_reliability(
            "task_heart_rate_daily_mean",
            bool(ebr.reliable),
            float(ebr.error_percent),
        )
        chain.log_transaction(
            "task_heart_rate_daily_mean",
            valid_eth_address,
            price=125,
            data_type="heart_rate",
        )
        onchain_reliability = chain.get_reliability("task_heart_rate_daily_mean")
        onchain_transaction = chain.get_transaction("task_heart_rate_daily_mean")
        transaction["onchain_reliable"] = int(onchain_reliability["reliable"])
        transaction["onchain_error_percent"] = onchain_reliability["error_percent"]
        transaction["onchain_price"] = onchain_transaction["price"]
    else:
        transaction["onchain_reliable"] = ""
        transaction["onchain_error_percent"] = ""
        transaction["onchain_price"] = ""
    return transaction
