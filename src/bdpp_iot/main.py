from __future__ import annotations

from bdpp_iot.config import ExperimentConfig
from bdpp_iot.pipeline import run_pipeline


def main() -> None:
    config = ExperimentConfig()
    result = run_pipeline(config)

    pricing = result["pricing_metrics"]
    print("BDPP-IoT experiment completed.")
    print(f"Static pricing MAE: {pricing['static_mae']:.3f}")
    print(f"ML pricing MAE: {pricing['ml_mae']:.3f}")
    print(f"Static pricing R2: {pricing['static_r2']:.3f}")
    print(f"ML pricing R2: {pricing['ml_r2']:.3f}")
    print("New base-paper-style tables generated:")
    print("  - outputs/tables/blockchain_benchmark_results.csv")
    print("  - outputs/tables/resource_consumption_results.csv")
    print("Tables: outputs/tables")
    print("Figures: outputs/figures")
