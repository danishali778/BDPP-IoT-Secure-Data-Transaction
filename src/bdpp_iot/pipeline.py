from __future__ import annotations

from pathlib import Path

import pandas as pd

from bdpp_iot.config import ExperimentConfig
from bdpp_iot.blockchain.ganache_manager import managed_ganache
from bdpp_iot.data.generator import generate_iomt_records, generate_transaction_history
from bdpp_iot.experiments.blockchain_benchmark import run_blockchain_benchmark
from bdpp_iot.experiments.ablation import (
    benchmark_runtime,
    evaluate_access_control,
    evaluate_ebr,
    run_ablation,
)
from bdpp_iot.experiments.resource_monitor import ResourceMonitor
from bdpp_iot.pricing.ml_pricing import evaluate_pricing
from bdpp_iot.visualization.design_diagrams import (
    save_layered_architecture,
    save_methodology_pipeline,
)
from bdpp_iot.visualization.plots import (
    plot_ablation,
    plot_access_control,
    plot_blockchain_benchmark,
    plot_ebr,
    plot_pricing,
    plot_pricing_r2,
    plot_resource_usage,
    plot_runtime,
)
from bdpp_iot.workflow.secure_transaction import run_secure_transaction_demo


def ensure_output_dirs(output_dir: Path) -> dict[str, Path]:
    dirs = {
        "figures": output_dir / "figures",
        "tables": output_dir / "tables",
        "logs": output_dir / "logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def run_pipeline(config: ExperimentConfig) -> dict:
    print("[1/12] Preparing output folders...")
    dirs = ensure_output_dirs(config.output_dir)

    print("[2/12] Generating synthetic IoMT sensor records...")
    records = generate_iomt_records(config.sensor_records, config.random_seed)
    print(f"       Generated {len(records)} sensor records.")

    print("[3/12] Generating historical transaction records for ML pricing...")
    history = generate_transaction_history(records, config.transaction_records, config.random_seed)
    print(f"       Generated {len(history)} transaction records.")

    with managed_ganache(config.ganache_rpc_url):
        monitor = ResourceMonitor()
        monitor.start()
        try:
            print("[4/12] Evaluating MA-CP-ABE access control and revocation...")
            access_metrics = evaluate_access_control()
            print(
                "       Valid allowed:",
                access_metrics["proposed_valid_allow"],
                "| Revoked blocked:",
                access_metrics["proposed_revoked_block"],
                "| Collusion blocked:",
                access_metrics["collusion_without_full_key_block"],
            )

            print("[5/12] Running TenSEAL CKKS computation with EBR reliability checks...")
            ebr_metrics = evaluate_ebr(records, config)
            print(
                "       CKKS backend:",
                ebr_metrics["ckks_backend"],
                "| Normal reliable:",
                ebr_metrics["normal_reliable"],
                "| High-noise detected:",
                ebr_metrics["high_noise_unreliable_detected"],
            )

            print("[6/12] Training/evaluating ML-calibrated pricing model...")
            pricing_metrics = evaluate_pricing(history, config.random_seed, config.test_fraction)
            print(
                f"       Static MAE: {pricing_metrics['static_mae']:.3f} | "
                f"ML MAE: {pricing_metrics['ml_mae']:.3f} | "
                f"Static R2: {pricing_metrics['static_r2']:.3f} | "
                f"ML R2: {pricing_metrics['ml_r2']:.3f}"
            )

            print("[7/12] Running ablation study...")
            ablation = run_ablation(records, history, config)
            print(ablation[["configuration", "security_score", "pricing_improvement_percent"]].to_string(index=False))

            print("[8/12] Running prototype runtime comparison...")
            runtime = benchmark_runtime(records, history, config)
            print(runtime.to_string(index=False))

            print("[9/12] Running full secure transaction demo: MA-ABE + TenSEAL + IPFS + Ganache...")
            secure_transaction = run_secure_transaction_demo(records, config)
            print(
                "       CKKS:",
                secure_transaction["ckks_backend"],
                "| Storage:",
                secure_transaction["storage_backend"],
                "| Blockchain:",
                secure_transaction["blockchain_backend"],
            )
            print(
                "       CID matches on-chain:",
                secure_transaction["cid"] == secure_transaction["onchain_cid"],
                "| Valid allowed:",
                secure_transaction["valid_user_allowed"],
                "| Revoked allowed:",
                secure_transaction["revoked_user_allowed"],
            )

            print("[10/12] Running smart-contract benchmark table...")
            blockchain_benchmark = run_blockchain_benchmark(config)
            print(
                blockchain_benchmark[
                    [
                        "Name",
                        "Succ/Fail",
                        "Send Rate (TPS)",
                        "Avg Latency (s)",
                        "Throughput (TPS)",
                    ]
                ].to_string(index=False)
            )
        finally:
            print("[11/12] Collecting CPU and memory resource table...")
            resource_usage = monitor.stop()
            if not resource_usage.empty:
                print(resource_usage.to_string(index=False))
            else:
                print("       No process samples captured.")

    print("[12/12] Saving CSV tables and 400 DPI figures...")
    records.head(250).to_csv(dirs["tables"] / "synthetic_iomt_sample.csv", index=False)
    history.to_csv(dirs["tables"] / "transaction_history.csv", index=False)
    pd.DataFrame([access_metrics]).to_csv(dirs["tables"] / "access_control_results.csv", index=False)
    pd.DataFrame([ebr_metrics]).to_csv(dirs["tables"] / "ebr_results.csv", index=False)
    pd.DataFrame(
        [
            {
                "static_mae": pricing_metrics["static_mae"],
                "ml_mae": pricing_metrics["ml_mae"],
                "static_rmse": pricing_metrics["static_rmse"],
                "ml_rmse": pricing_metrics["ml_rmse"],
                "static_r2": pricing_metrics["static_r2"],
                "ml_r2": pricing_metrics["ml_r2"],
            }
        ]
    ).to_csv(dirs["tables"] / "pricing_results.csv", index=False)
    ablation.to_csv(dirs["tables"] / "ablation_results.csv", index=False)
    runtime.to_csv(dirs["tables"] / "runtime_results.csv", index=False)
    blockchain_benchmark.to_csv(dirs["tables"] / "blockchain_benchmark_results.csv", index=False)
    resource_usage.to_csv(dirs["tables"] / "resource_consumption_results.csv", index=False)
    pd.DataFrame([secure_transaction]).to_csv(
        dirs["tables"] / "secure_transaction_demo.csv", index=False
    )

    plot_access_control(access_metrics, dirs["figures"] / "access_control_comparison.png")
    plot_ebr(ebr_metrics, dirs["figures"] / "ckks_ebr_errors.png")
    plot_pricing(pricing_metrics, dirs["figures"] / "pricing_mae_comparison.png")
    plot_pricing_r2(pricing_metrics, dirs["figures"] / "pricing_r2_comparison.png")
    plot_ablation(ablation, dirs["figures"] / "ablation_security_score.png")
    plot_runtime(runtime, dirs["figures"] / "runtime_comparison.png")
    plot_blockchain_benchmark(blockchain_benchmark, dirs["figures"] / "blockchain_benchmark_throughput.png")
    plot_resource_usage(resource_usage, dirs["figures"] / "resource_consumption.png")
    save_layered_architecture(dirs["figures"] / "bdpp_iot_layered_architecture.png")
    save_methodology_pipeline(dirs["figures"] / "bdpp_iot_methodology_pipeline.png")

    return {
        "records": records,
        "history": history,
        "access_metrics": access_metrics,
        "ebr_metrics": ebr_metrics,
        "pricing_metrics": pricing_metrics,
        "ablation": ablation,
        "runtime": runtime,
        "blockchain_benchmark": blockchain_benchmark,
        "resource_usage": resource_usage,
        "secure_transaction": secure_transaction,
        "output_dirs": dirs,
    }
