from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=400, bbox_inches="tight")
    plt.close()


def plot_access_control(access_metrics: dict, path: Path) -> None:
    labels = ["Valid allowed", "Invalid blocked", "Revoked blocked"]
    base = [
        access_metrics["base_valid_allow"],
        access_metrics["base_invalid_block"],
        access_metrics["base_revoked_block"],
    ]
    proposed = [
        access_metrics["proposed_valid_allow"],
        access_metrics["proposed_invalid_block"],
        access_metrics["proposed_revoked_block"],
    ]

    x = np.arange(len(labels))
    width = 0.36
    plt.figure(figsize=(8, 4.8))
    plt.bar(x - width / 2, base, width, label="Base")
    plt.bar(x + width / 2, proposed, width, label="BDPP-IoT")
    plt.xticks(x, labels)
    plt.ylim(0, 1.15)
    plt.ylabel("Decision success")
    plt.title("Access Control Behavior")
    plt.legend()
    _save(path)


def plot_ebr(ebr_metrics: dict, path: Path) -> None:
    labels = ["Normal CKKS noise", "High CKKS noise"]
    values = [ebr_metrics["normal_error_percent"], ebr_metrics["high_noise_error_percent"]]
    colors = ["#2f7d32", "#b23b3b"]

    plt.figure(figsize=(7, 4.5))
    plt.bar(labels, values, color=colors)
    plt.axhline(2.0, linestyle="--", color="black", label="2 percent threshold")
    plt.ylabel("Error percent")
    plt.title("Operation-Aware CKKS Error-Bound Reporting")
    plt.legend()
    _save(path)


def plot_pricing(pricing: dict, path: Path) -> None:
    labels = ["Static pricing", "ML pricing"]
    values = [pricing["static_mae"], pricing["ml_mae"]]
    plt.figure(figsize=(7, 4.5))
    plt.bar(labels, values, color=["#7b8794", "#2563eb"])
    plt.ylabel("Mean absolute error")
    plt.title("Pricing Error Comparison")
    _save(path)


def plot_pricing_r2(pricing: dict, path: Path) -> None:
    labels = ["Static pricing", "ML pricing"]
    values = [pricing["static_r2"], pricing["ml_r2"]]
    plt.figure(figsize=(7, 4.5))
    plt.bar(labels, values, color=["#7b8794", "#2563eb"])
    plt.axhline(0.0, linestyle="--", color="black", linewidth=1)
    plt.ylabel("R2 score")
    plt.title("Pricing Model Fit Comparison")
    _save(path)


def plot_ablation(ablation: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(10, 5.2))
    plt.barh(ablation["configuration"], ablation["security_score"], color="#0f766e")
    plt.xlabel("Security detection score")
    plt.title("Ablation Study: Security Component Impact")
    plt.xlim(0, 1.05)
    _save(path)


def plot_runtime(runtime: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(7, 4.5))
    plt.bar(runtime["configuration"], runtime["runtime_ms"], color=["#64748b", "#9333ea"])
    plt.ylabel("Runtime in milliseconds")
    plt.title("Prototype Runtime Comparison")
    _save(path)


def plot_blockchain_benchmark(benchmark: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(benchmark["Name"], benchmark["Throughput (TPS)"], color="#2563eb")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Throughput (TPS)")
    plt.title("Ganache Smart Contract Throughput")
    _save(path)


def plot_resource_usage(resources: pd.DataFrame, path: Path) -> None:
    if resources.empty:
        return
    x = np.arange(len(resources["Name"]))
    width = 0.36
    plt.figure(figsize=(9, 5))
    plt.bar(x - width / 2, resources["CPU % (avg)"], width, label="CPU avg %", color="#0f766e")
    plt.bar(x + width / 2, resources["Memory avg (MB)"], width, label="Memory avg MB", color="#b45309")
    plt.xticks(x, resources["Name"], rotation=15, ha="right")
    plt.ylabel("Value")
    plt.title("Process Resource Consumption")
    plt.legend()
    _save(path)
