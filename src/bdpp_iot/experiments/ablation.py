from __future__ import annotations

import time

import pandas as pd

from bdpp_iot.access_control.ma_abe import MultiAuthorityAccessControl
from bdpp_iot.blockchain.ledger import Ledger
from bdpp_iot.config import ExperimentConfig
from bdpp_iot.crypto.ckks_backend import create_ckks_processor
from bdpp_iot.crypto.ebr import ErrorBoundReporter
from bdpp_iot.pricing.ml_pricing import evaluate_pricing


def evaluate_access_control() -> dict:
    ledger = Ledger()
    access = MultiAuthorityAccessControl(ledger)
    policy = "research_lab AND cardiology_researcher AND heart_rate"
    alternative_policy = "research_lab AND (cardiology_researcher OR doctor) AND heart_rate"

    valid = access.issue_key("user_valid", {"research_lab", "cardiology_researcher", "heart_rate", "remote"})
    invalid = access.issue_key("user_invalid", {"research_lab", "doctor", "temperature", "remote"})
    revoked = access.issue_key("user_revoked", {"research_lab", "cardiology_researcher", "heart_rate", "remote"})
    partial_a = access.issue_key("user_partial_a", {"research_lab", "remote"})
    partial_b = access.issue_key("user_partial_b", {"cardiology_researcher", "heart_rate"})
    doctor_heart = access.issue_key("user_doctor_heart", {"research_lab", "doctor", "heart_rate", "remote"})
    ledger.revoke_user("user_revoked")
    ciphertext = access.encrypt_key("session_key_heart_rate", policy)

    return {
        "base_valid_allow": int(access.can_decrypt(valid, policy, check_revocation=False)),
        "base_invalid_block": int(not access.can_decrypt(invalid, policy, check_revocation=False)),
        "base_revoked_block": int(not access.can_decrypt(revoked, policy, check_revocation=False)),
        "proposed_valid_allow": int(access.can_decrypt(valid, policy, check_revocation=True)),
        "proposed_invalid_block": int(not access.can_decrypt(invalid, policy, check_revocation=True)),
        "proposed_revoked_block": int(not access.can_decrypt(revoked, policy, check_revocation=True)),
        "or_policy_doctor_allow": int(access.can_decrypt(doctor_heart, alternative_policy, check_revocation=True)),
        "collusion_without_full_key_block": int(
            not access.collusion_can_decrypt([partial_a, partial_b], policy, check_revocation=True)
        ),
        "ciphertext_policy_authorities": len(ciphertext.required_authorities),
        "valid_authority_fragments": len(valid.authority_fragments),
    }


def evaluate_ebr(records: pd.DataFrame, config: ExperimentConfig) -> dict:
    vector = records["heart_rate"].head(1000).to_numpy(dtype=float)
    reporter = ErrorBoundReporter(config.ebr_threshold_percent)
    ckks = create_ckks_processor(config)

    encrypted = ckks.encrypt_vector(vector)
    normal_observed = ckks.compute(encrypted, "mean")
    normal_result = reporter.check(vector, "mean", normal_observed)

    faulty_observed = normal_observed * (1.0 + config.ckks_high_noise_std)
    noisy_result = reporter.check(vector, "mean", faulty_observed)

    return {
        "ckks_backend": getattr(ckks, "scheme_name", ckks.__class__.__name__),
        "normal_error_percent": normal_result.error_percent,
        "normal_reliable": int(normal_result.reliable),
        "high_noise_error_percent": noisy_result.error_percent,
        "high_noise_unreliable_detected": int(not noisy_result.reliable),
    }


def run_ablation(records: pd.DataFrame, history: pd.DataFrame, config: ExperimentConfig) -> pd.DataFrame:
    pricing = evaluate_pricing(history, config.random_seed, config.test_fraction)
    access_metrics = evaluate_access_control()
    ebr_metrics = evaluate_ebr(records, config)

    configs = [
        {
            "configuration": "Base paper simulation",
            "revocation_enabled": 0,
            "ebr_enabled": 0,
            "ml_pricing_enabled": 0,
            "revoked_user_blocked": access_metrics["base_revoked_block"],
            "unreliable_ckks_detected": 0,
            "pricing_mae": pricing["static_mae"],
        },
        {
            "configuration": "Full BDPP-IoT",
            "revocation_enabled": 1,
            "ebr_enabled": 1,
            "ml_pricing_enabled": 1,
            "revoked_user_blocked": access_metrics["proposed_revoked_block"],
            "unreliable_ckks_detected": ebr_metrics["high_noise_unreliable_detected"],
            "pricing_mae": pricing["ml_mae"],
        },
        {
            "configuration": "Without revocation",
            "revocation_enabled": 0,
            "ebr_enabled": 1,
            "ml_pricing_enabled": 1,
            "revoked_user_blocked": access_metrics["base_revoked_block"],
            "unreliable_ckks_detected": ebr_metrics["high_noise_unreliable_detected"],
            "pricing_mae": pricing["ml_mae"],
        },
        {
            "configuration": "Without EBR",
            "revocation_enabled": 1,
            "ebr_enabled": 0,
            "ml_pricing_enabled": 1,
            "revoked_user_blocked": access_metrics["proposed_revoked_block"],
            "unreliable_ckks_detected": 0,
            "pricing_mae": pricing["ml_mae"],
        },
        {
            "configuration": "Without ML pricing",
            "revocation_enabled": 1,
            "ebr_enabled": 1,
            "ml_pricing_enabled": 0,
            "revoked_user_blocked": access_metrics["proposed_revoked_block"],
            "unreliable_ckks_detected": ebr_metrics["high_noise_unreliable_detected"],
            "pricing_mae": pricing["static_mae"],
        },
    ]

    frame = pd.DataFrame(configs)
    frame["security_score"] = (
        frame["revoked_user_blocked"] + frame["unreliable_ckks_detected"]
    ) / 2.0
    frame["pricing_improvement_percent"] = (
        (pricing["static_mae"] - frame["pricing_mae"]) / pricing["static_mae"] * 100.0
    )
    return frame


def benchmark_runtime(records: pd.DataFrame, history: pd.DataFrame, config: ExperimentConfig) -> pd.DataFrame:
    rows = []
    for name, use_ebr, use_ml in [
        ("Base paper simulation", False, False),
        ("Full BDPP-IoT", True, True),
    ]:
        start = time.perf_counter()
        _ = evaluate_access_control()
        if use_ebr:
            _ = evaluate_ebr(records, config)
        if use_ml:
            _ = evaluate_pricing(history, config.random_seed, config.test_fraction)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        rows.append({"configuration": name, "runtime_ms": elapsed_ms})
    return pd.DataFrame(rows)
