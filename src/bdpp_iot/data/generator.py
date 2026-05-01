from __future__ import annotations

import numpy as np
import pandas as pd


DATA_TYPES = ["heart_rate", "temperature", "blood_pressure", "glucose"]


def generate_iomt_records(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=n, freq="min")
    data_type = rng.choice(DATA_TYPES, size=n, p=[0.35, 0.25, 0.25, 0.15])

    heart_rate = np.clip(rng.normal(78, 12, n), 45, 135)
    temperature = np.clip(rng.normal(37.0, 0.55, n), 35.4, 40.2)
    systolic = np.clip(rng.normal(122, 16, n), 85, 185)
    diastolic = np.clip(rng.normal(79, 10, n), 50, 120)
    glucose = np.clip(rng.normal(116, 28, n), 55, 260)

    missing_ratio = rng.uniform(0.0, 0.08, n)
    noise_ratio = rng.uniform(0.0, 0.10, n)
    integrity_score = np.clip(1.0 - missing_ratio - (noise_ratio * 0.8), 0.65, 1.0)
    freshness = np.clip(rng.beta(7, 2, n), 0.25, 1.0)
    market_demand = np.clip(rng.beta(4, 3, n), 0.10, 1.0)
    seller_reputation = np.clip(rng.normal(0.82, 0.11, n), 0.35, 1.0)

    return pd.DataFrame(
        {
            "record_id": [f"rec_{i:05d}" for i in range(n)],
            "patient_id": [f"pat_{i % 320:04d}" for i in range(n)],
            "device_id": [f"dev_{i % 80:03d}" for i in range(n)],
            "timestamp": timestamps,
            "data_type": data_type,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "systolic": systolic,
            "diastolic": diastolic,
            "glucose": glucose,
            "integrity_score": integrity_score,
            "freshness": freshness,
            "market_demand": market_demand,
            "seller_reputation": seller_reputation,
        }
    )


def generate_transaction_history(records: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 100)
    sampled = records.sample(n=n, replace=True, random_state=seed).reset_index(drop=True)

    type_weight = {
        "heart_rate": 1.05,
        "temperature": 0.90,
        "blood_pressure": 1.20,
        "glucose": 1.35,
    }
    base_price = 35.0
    data_volume = rng.integers(1000, 6000, n)
    access_frequency = rng.integers(1, 50, n)
    weights = sampled["data_type"].map(type_weight).to_numpy()

    true_price = (
        base_price
        * weights
        * (0.95 + sampled["integrity_score"].to_numpy())
        * (0.55 + sampled["market_demand"].to_numpy())
        * (0.65 + sampled["seller_reputation"].to_numpy())
        * (1.0 + data_volume / 12000.0)
        * (1.0 + access_frequency / 200.0)
    )
    final_price = np.clip(true_price + rng.normal(0, 6.5, n), 5.0, None)

    return pd.DataFrame(
        {
            "data_type": sampled["data_type"],
            "integrity_score": sampled["integrity_score"],
            "freshness": sampled["freshness"],
            "market_demand": sampled["market_demand"],
            "seller_reputation": sampled["seller_reputation"],
            "data_volume": data_volume,
            "access_frequency": access_frequency,
            "final_price": final_price,
        }
    )

