# 11. Results and Discussion

This section presents the experimental results of BDPP-IoT and discusses how they compare with the base paper's methodology.

## 11.1 End-to-End Functional Results

The full secure transaction demo confirms that the proposed pipeline works end-to-end.

The secure transaction result is:

| Metric | Value |
|---|---|
| Task ID | `task_heart_rate_daily_mean` |
| Operation | `mean` |
| CKKS backend | `TENSEAL_CKKS` |
| Storage backend | `IPFS_KUBO` |
| Blockchain backend | `GANACHE_SOLIDITY` |
| Records processed | 1440 |
| Valid user allowed | 1 |
| Revoked user allowed | 0 |
| On-chain valid version | 1 |
| On-chain revoked version | 2 |
| On-chain reliable | 1 |
| On-chain price | 125 |

The IPFS CID and the CID stored on-chain are identical:

```text
cid = QmTjgnUVrxdjMGyXP6ZFNKz4sWw76DZ6j7nZnApyfFtRXq
onchain_cid = QmTjgnUVrxdjMGyXP6ZFNKz4sWw76DZ6j7nZnApyfFtRXq
```

This confirms that the IPFS storage layer and blockchain layer are correctly connected.

## 11.2 Access-Control Results

The access-control experiment produced:

| Metric | Value |
|---|---:|
| Base valid user allowed | 1 |
| Base invalid user blocked | 1 |
| Base revoked user blocked | 0 |
| Proposed valid user allowed | 1 |
| Proposed invalid user blocked | 1 |
| Proposed revoked user blocked | 1 |
| OR-policy doctor allowed | 1 |
| Collusion without full key blocked | 1 |
| Ciphertext policy authorities | 3 |
| Valid authority fragments | 4 |

The most important result is:

```text
base_revoked_block = 0
proposed_revoked_block = 1
```

This shows the main improvement of BDPP-IoT over the base paper's access-control design. The base-style access model can validate attributes but does not block a user whose key was previously issued. BDPP-IoT blocks revoked users by checking the blockchain version number.

The result:

```text
collusion_without_full_key_block = 1
```

shows that partial users cannot simply combine incomplete attribute fragments to satisfy the full policy in the implemented policy-level model.

## 11.3 CKKS and EBR Results

The EBR result is:

| Metric | Value |
|---|---:|
| CKKS backend | `TENSEAL_CKKS` |
| Normal error percent | 2.4136912231415975e-09 |
| Normal reliable | 1 |
| High-noise error percent | 4.500000002522298 |
| High-noise unreliable detected | 1 |

The secure transaction demo produced:

```text
expected_result = 77.93935639865786
observed_result = 77.93935639801067
error_percent = 8.303773284056454e-10
reliable = 1
```

This shows that TenSEAL CKKS produced a highly accurate approximate result for the mean heart-rate computation. The EBR module correctly marked this result as reliable.

The high-noise case was also detected:

```text
high_noise_unreliable_detected = 1
```

This is an improvement over the base paper, which uses CKKS but does not explicitly report whether a decrypted approximate result is reliable.

## 11.4 Pricing Results

The pricing experiment compared static pricing with ML-calibrated pricing.

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Static Pricing | 100.27005203097912 | 105.3339526638235 | -4.276097844000223 |
| ML Pricing | 11.217385659614619 | 14.7401995782551 | 0.8966803787227509 |

The pricing improvement is:

```text
88.81282553224473%
```

This shows that the ML pricing layer provides more accurate pricing than the static baseline. The base paper acknowledges that pricing parameters require empirical calibration. BDPP-IoT directly addresses this limitation by learning from historical transaction records.

The negative R2 value for static pricing means that the fixed formula performs worse than a simple mean-value predictor on the generated test set. The ML pricing model achieves a positive R2 of 0.8967, showing that it captures most of the price variance in the synthetic transaction history.

## 11.5 Ablation Study Results

The ablation study result is:

| Configuration | Revocation | EBR | ML Pricing | Security Score | Pricing Improvement |
|---|---:|---:|---:|---:|---:|
| Base paper simulation | 0 | 0 | 0 | 0.0 | 0.0 |
| Full BDPP-IoT | 1 | 1 | 1 | 1.0 | 88.81282553224473 |
| Without revocation | 0 | 1 | 1 | 0.5 | 88.81282553224473 |
| Without EBR | 1 | 0 | 1 | 0.5 | 88.81282553224473 |
| Without ML pricing | 1 | 1 | 0 | 1.0 | 0.0 |

The full BDPP-IoT configuration gives the best combined result:

```text
security_score = 1.0
pricing_improvement_percent = 88.81282553224473
```

Removing revocation reduces the security score to:

```text
0.5
```

Removing EBR also reduces the security score to:

```text
0.5
```

Removing ML pricing keeps the security score at 1.0 but removes the pricing improvement:

```text
pricing_improvement_percent = 0.0
```

This confirms that each proposed module contributes to a different part of the system. Revocation improves access security, EBR improves computation reliability, and ML pricing improves transaction valuation.

## 11.6 Blockchain Benchmark Results

The smart-contract benchmark produced the following results:

| Operation | Succ/Fail | Send Rate (TPS) | Max Latency (s) | Min Latency (s) | Avg Latency (s) | Throughput (TPS) |
|---|---:|---:|---:|---:|---:|---:|
| storeCID | 20/0 | 11.107438251291683 | 0.1347617999999784 | 0.06523220002418384 | 0.09002787499921397 | 11.107438251291683 |
| getCID | 20/0 | 51.59704462618116 | 0.031212100002449006 | 0.015574799966998398 | 0.01937997999775689 | 51.59704462618116 |
| registerUser | 20/0 | 16.362953879790446 | 0.08162910002283752 | 0.04989919997751713 | 0.06111265500076115 | 16.362953879790446 |
| revokeUser | 20/0 | 12.997228470853196 | 0.10420299996621907 | 0.05918570002540946 | 0.0769382999977097 | 12.997228470853196 |
| logReliability | 20/0 | 12.408316500358415 | 0.11272319999989122 | 0.06370009999955073 | 0.08059003499802202 | 12.408316500358415 |
| logTransaction | 20/0 | 8.393550060389519 | 0.27250100002856925 | 0.08182730001863092 | 0.11913793499115855 | 8.393550060389519 |

The read operation `getCID` has the highest throughput:

```text
51.59704462618116 TPS
```

This is expected because read operations do not require state-changing blockchain transactions. State-changing operations such as `storeCID`, `revokeUser`, `logReliability`, and `logTransaction` have lower throughput because they require transaction execution and confirmation.

The base paper uses Hyperledger Fabric and Hyperledger Caliper. BDPP-IoT uses Ganache and Solidity. Therefore, the exact numbers are not directly comparable, but the type of performance analysis is comparable.

## 11.7 Resource Consumption Results

The resource consumption result is:

| Process | CPU % Max | CPU % Avg | Memory Max (MB) | Memory Avg (MB) |
|---|---:|---:|---:|---:|
| ganache_node | 92.4 | 39.522666666666666 | 110.8125 | 89.7234375 |
| ipfs_kubo_cli | 49.9 | 34.35 | 29.33203125 | 23.34765625 |
| python_pipeline | 94.3 | 47.81333333333333 | 287.77734375 | 284.9491145833333 |

The Python pipeline uses more memory because it runs data generation, TenSEAL CKKS operations, ML pricing, graph generation, and experiment coordination. Ganache memory usage remains lower, with an average of about:

```text
89.72 MB
```

CPU values can exceed 100 percent because `psutil` reports CPU usage relative to logical cores. Therefore, values above 100 percent indicate multi-core utilization rather than an invalid measurement.

## 11.8 Runtime Results

The runtime comparison is:

| Configuration | Runtime (ms) |
|---|---:|
| Base paper simulation | 0.5221999599598348 |
| Full BDPP-IoT | 2154.418599966448 |

The proposed system has higher runtime because it performs additional operations:

1. TenSEAL CKKS encryption and computation.
2. EBR reliability checking.
3. ML pricing.
4. IPFS Kubo storage.
5. Ganache smart-contract calls.
6. Revocation-aware access checking.

This overhead is expected because BDPP-IoT provides stronger access control, computation reliability, and adaptive pricing than the base simulation.

## 11.9 Comparison With Base Paper Results

The base paper's Table 3 reports functional success for Fabric registration, IPFS upload/download, on-chain query, encrypted sharing, access control, homomorphic computation, and decryption recovery. BDPP-IoT produces the same type of functional validation, but with additional checks:

1. Revoked user blocking.
2. On-chain version checking.
3. CID equality between IPFS and blockchain.
4. CKKS reliability logging.
5. ML pricing evaluation.

The base paper's Table 4 reports blockchain throughput and latency for Fabric operations. BDPP-IoT reports equivalent smart-contract benchmark values for Ganache/Solidity operations.

The base paper's Table 5 reports peer-node CPU and memory usage. BDPP-IoT reports CPU and memory usage for the Python pipeline and Ganache blockchain process.

## 11.10 Overall Findings

The main findings are:

1. BDPP-IoT successfully completes the full secure IoMT transaction pipeline.
2. The proposed revocation mechanism blocks revoked users.
3. The EBR module detects unreliable CKKS outputs.
4. ML pricing significantly reduces pricing error.
5. Real IPFS Kubo and Ganache/Solidity integration works.
6. The proposed system introduces additional runtime and resource cost, but this cost is justified by improved security, reliability, and pricing adaptability.

The most important improvement over the base paper is that BDPP-IoT does not only provide secure storage and encrypted computation. It also verifies access validity after revocation, checks whether approximate encrypted computation is reliable, and adapts transaction pricing using learned historical behavior.
