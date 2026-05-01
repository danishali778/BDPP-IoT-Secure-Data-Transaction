from __future__ import annotations

import statistics
import time
from typing import Callable

import pandas as pd

from bdpp_iot.blockchain.chain_backend import create_chain_client
from bdpp_iot.config import ExperimentConfig


def _benchmark_operation(name: str, runs: int, operation: Callable[[int], object]) -> dict:
    latencies: list[float] = []
    success = 0
    failed = 0
    start_all = time.perf_counter()

    for i in range(runs):
        start = time.perf_counter()
        try:
            operation(i)
            success += 1
        except Exception:
            failed += 1
        latencies.append(time.perf_counter() - start)

    total = max(time.perf_counter() - start_all, 1e-9)
    return {
        "Name": name,
        "Succ/Fail": f"{success}/{failed}",
        "Send Rate (TPS)": runs / total,
        "Max Latency (s)": max(latencies) if latencies else 0.0,
        "Min Latency (s)": min(latencies) if latencies else 0.0,
        "Avg Latency (s)": statistics.mean(latencies) if latencies else 0.0,
        "Throughput (TPS)": success / total,
    }


def run_blockchain_benchmark(config: ExperimentConfig, runs: int = 20) -> pd.DataFrame:
    chain = create_chain_client(config)
    if chain is None:
        return pd.DataFrame(
            [
                {
                    "Name": "Ganache unavailable",
                    "Succ/Fail": "0/1",
                    "Send Rate (TPS)": 0.0,
                    "Max Latency (s)": 0.0,
                    "Min Latency (s)": 0.0,
                    "Avg Latency (s)": 0.0,
                    "Throughput (TPS)": 0.0,
                }
            ]
        )

    accounts = chain.w3.eth.accounts
    rows = [
        _benchmark_operation(
            "storeCID",
            runs,
            lambda i: chain.store_cid(f"bench_task_{i}", f"QmBenchmarkCID{i:04d}"),
        ),
        _benchmark_operation(
            "getCID",
            runs,
            lambda i: chain.get_cid(f"bench_task_{i % max(runs, 1)}"),
        ),
        _benchmark_operation(
            "registerUser",
            runs,
            lambda i: chain.register_user(accounts[i % len(accounts)]),
        ),
        _benchmark_operation(
            "revokeUser",
            runs,
            lambda i: chain.revoke_user(accounts[(i % (len(accounts) - 1)) + 1]),
        ),
        _benchmark_operation(
            "logReliability",
            runs,
            lambda i: chain.log_reliability(f"bench_task_{i}", reliable=(i % 2 == 0), error_percent=i / 1000),
        ),
        _benchmark_operation(
            "logTransaction",
            runs,
            lambda i: chain.log_transaction(f"bench_task_{i}", accounts[1], price=100 + i, data_type="heart_rate"),
        ),
    ]
    return pd.DataFrame(rows)

