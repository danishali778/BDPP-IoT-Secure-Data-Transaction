# 10. Experimental Design

This section describes the experiments used to evaluate BDPP-IoT. The experiments are designed to follow the base paper's prototype/simulation style while adding evaluation for the proposed extensions.

## 10.1 Experimental Objectives

The experiments aim to answer the following questions:

1. Can BDPP-IoT complete an end-to-end secure IoMT transaction?
2. Can a valid user access encrypted data while a revoked user is blocked?
3. Can TenSEAL CKKS perform encrypted computation successfully?
4. Can EBR detect unreliable approximate CKKS results?
5. Does ML-calibrated pricing improve over static pricing?
6. What is the effect of removing revocation, EBR, or ML pricing?
7. What are the latency and throughput values for smart-contract operations?
8. What are the CPU and memory costs of the implemented prototype?

## 10.2 Dataset Design

The base paper evaluates its framework using a simulated IoMT prototype rather than a named real hospital dataset. BDPP-IoT follows the same approach.

The synthetic IoMT dataset includes:

```text
heart_rate
temperature
blood_pressure
glucose
integrity_score
freshness
market_demand
seller_reputation
```

The default experiment uses:

```text
sensor_records = 3500
transaction_records = 800
```

This dataset is sufficient for testing security, privacy, encrypted computation, pricing, and transaction logging without exposing real medical data.

## 10.3 Functional Experiment

The functional experiment checks whether the full workflow succeeds.

The workflow includes:

1. Synthetic data generation.
2. MA-CP-ABE policy creation.
3. Valid user access.
4. Revoked user blocking.
5. TenSEAL CKKS encryption and computation.
6. IPFS Kubo upload and retrieval.
7. Ganache/Solidity smart contract deployment.
8. CID storage on-chain.
9. EBR reliability logging.
10. Transaction price logging.

The secure transaction output is stored in:

```text
outputs/tables/secure_transaction_demo.csv
```

The expected functional success conditions are:

```text
ckks_backend = TENSEAL_CKKS
storage_backend = IPFS_KUBO
blockchain_backend = GANACHE_SOLIDITY
cid = onchain_cid
valid_user_allowed = 1
revoked_user_allowed = 0
onchain_reliable = 1
```

## 10.4 Access-Control Experiment

The access-control experiment compares base behavior and proposed behavior.

The tested cases are:

1. Valid user.
2. Invalid user.
3. Revoked user.
4. OR-policy user.
5. Colluding partial users.

The results are stored in:

```text
outputs/tables/access_control_results.csv
```

The key expected result is that the base model does not block a revoked user, while BDPP-IoT does.

## 10.5 CKKS and EBR Experiment

The CKKS experiment uses TenSEAL to perform encrypted computation over heart-rate values.

The EBR experiment compares:

1. Normal CKKS approximate output.
2. High-noise/fault-injection output.

The output file is:

```text
outputs/tables/ebr_results.csv
```

The goal is to show that normal CKKS output is reliable while high-noise output is detected as unreliable.

## 10.6 Pricing Experiment

The pricing experiment compares:

1. Static pricing.
2. ML-calibrated pricing.

The ML model is a Random Forest Regressor trained on historical transaction records.

The output file is:

```text
outputs/tables/pricing_results.csv
```

The metrics are:

```text
MAE
RMSE
R2 score
```

## 10.7 Ablation Study

The ablation study evaluates the effect of removing individual components.

The configurations are:

| Configuration | Revocation | EBR | ML Pricing |
|---|---:|---:|---:|
| Base paper simulation | 0 | 0 | 0 |
| Full BDPP-IoT | 1 | 1 | 1 |
| Without revocation | 0 | 1 | 1 |
| Without EBR | 1 | 0 | 1 |
| Without ML pricing | 1 | 1 | 0 |

The output file is:

```text
outputs/tables/ablation_results.csv
```

The evaluation metrics are:

```text
revoked_user_blocked
unreliable_ckks_detected
pricing_mae
security_score
pricing_improvement_percent
```

## 10.8 Blockchain Benchmark

The blockchain benchmark follows the style of the base paper's Caliper benchmark table, but it evaluates the Ganache/Solidity smart contract instead of Hyperledger Fabric.

The tested smart-contract operations are:

```text
storeCID
getCID
registerUser
revokeUser
logReliability
logTransaction
```

For each operation, the experiment records:

```text
Succ/Fail
Send Rate (TPS)
Max Latency (s)
Min Latency (s)
Avg Latency (s)
Throughput (TPS)
```

The output file is:

```text
outputs/tables/blockchain_benchmark_results.csv
```

## 10.9 Resource Consumption Experiment

The resource consumption experiment follows the idea of the base paper's resource table. Instead of Fabric peer nodes, BDPP-IoT records resource usage for:

```text
ganache_node
python_pipeline
```

The metrics are:

```text
CPU % (max)
CPU % (avg)
Memory max (MB)
Memory avg (MB)
```

The output file is:

```text
outputs/tables/resource_consumption_results.csv
```

## 10.10 Runtime Comparison

The runtime experiment compares:

```text
Base paper simulation
Full BDPP-IoT
```

The output file is:

```text
outputs/tables/runtime_results.csv
```

The goal is to show the additional runtime cost of BDPP-IoT's security and reliability improvements.

## 10.11 Figures

The experiment generates the following figures:

| Figure | Purpose |
|---|---|
| `bdpp_iot_layered_architecture.png` | Proposed layered architecture |
| `bdpp_iot_methodology_pipeline.png` | End-to-end methodology pipeline |
| `access_control_comparison.png` | Base vs proposed access behavior |
| `ckks_ebr_errors.png` | CKKS reliability checking |
| `pricing_mae_comparison.png` | Static vs ML pricing error |
| `pricing_r2_comparison.png` | Static vs ML pricing model fit |
| `ablation_security_score.png` | Ablation security impact |
| `blockchain_benchmark_throughput.png` | Smart-contract throughput |
| `resource_consumption.png` | CPU and memory usage |
| `runtime_comparison.png` | Runtime overhead |

All figures are generated at 400 DPI.
