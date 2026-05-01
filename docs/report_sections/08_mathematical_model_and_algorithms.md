# 8. Mathematical Model and Algorithms

This section defines the mathematical model and algorithmic flow of BDPP-IoT. The model combines access control, revocation, encrypted computation, reliability verification, dynamic pricing, and blockchain logging.

## 8.1 Notation

| Symbol | Meaning |
|---|---|
| `U` | Global attribute universe |
| `AA_k` | Attribute authority k |
| `U_k` | Attribute domain controlled by authority k |
| `S_u` | Attribute set of user u |
| `P` | Access policy |
| `v_key` | Version attached to user's issued key |
| `v_chain` | Latest valid user version stored on-chain |
| `M` | Medical IoT data vector |
| `CT` | CKKS encrypted ciphertext |
| `y` | Expected plaintext result |
| `y_hat` | Decrypted approximate CKKS result |
| `t` | Error threshold |
| `R` | Reliability decision |
| `x` | Pricing feature vector |
| `RF(x)` | Random Forest price prediction |

## 8.2 Multi-Authority Attribute Model

The global attribute universe is divided among independent authorities:

```text
U = U_1 union U_2 union ... union U_n
```

The domains are non-overlapping:

```text
U_i intersection U_j = empty, for i != j
```

In the implementation:

```text
AA_ORG      = {hospital_a, hospital_b, research_lab}
AA_ROLE     = {doctor, cardiology_researcher, admin}
AA_DATA     = {heart_rate, temperature, blood_pressure, glucose}
AA_LOCATION = {ward_a, ward_b, remote}
```

A user's key is represented as a set of authority fragments:

```text
SK_u = {SK_u,ORG, SK_u,ROLE, SK_u,DATA, SK_u,LOCATION}
```

The secure transaction demo uses the access policy:

```text
P = research_lab AND cardiology_researcher AND heart_rate
```

The ciphertext requires attributes from three authorities:

```text
abe_required_authorities = 3
```

## 8.3 Access-Control Decision

The policy decision is:

```text
Policy(S_u) = 1, if user attributes satisfy P
Policy(S_u) = 0, otherwise
```

The revocation-aware access decision is:

```text
Access(u) = 1 iff Policy(S_u) = 1 AND v_key = v_chain
```

If either the policy is false or the version does not match, access is denied:

```text
Access(u) = 0
```

The experiment produced:

```text
proposed_valid_allow = 1
proposed_invalid_block = 1
proposed_revoked_block = 1
```

## 8.4 Revocation Model

When a user is registered:

```text
v_chain(u) = 1
```

When a user is revoked:

```text
v_chain(u) = v_chain(u) + 1
```

In the secure transaction demo:

```text
onchain_valid_version = 1
onchain_revoked_version = 2
```

The revoked user is blocked:

```text
revoked_user_allowed = 0
```

## 8.5 CKKS Computation Model

Let the medical IoT vector be:

```text
M = {m_1, m_2, ..., m_n}
```

The system encrypts this vector using CKKS:

```text
CT = CKKS.Encrypt(M)
```

For the mean operation:

```text
y = (1/n) * sum(m_i)
```

The encrypted computation produces an approximate decrypted result:

```text
y_hat = CKKS.Decrypt(CKKS.Evaluate(CT))
```

In the secure transaction demo:

```text
n = 1440
y = 77.93935639865786
y_hat = 77.93935639801067
```

## 8.6 Error-Bound Reporting Model

The error percentage is:

```text
Error% = |y_hat - y| / |y| * 100
```

The reliability decision is:

```text
R = 1, if Error% <= t
R = 0, otherwise
```

The normal CKKS case produced:

```text
normal_error_percent = 2.4136912231415975e-09
normal_reliable = 1
```

The injected high-noise case produced:

```text
high_noise_error_percent = 4.500000002522298
high_noise_unreliable_detected = 1
```

This verifies that the EBR module can detect unreliable approximate computation.

## 8.7 ML Pricing Model

The transaction feature vector is:

```text
x = (data_type, integrity_score, freshness, market_demand,
     seller_reputation, data_volume, access_frequency)
```

The target value is:

```text
y_price = final transaction price
```

The Random Forest model predicts:

```text
p_hat = RF(x)
```

The negotiation bounds are:

```text
lower_bound = p_hat * (1 - margin)
upper_bound = p_hat * (1 + margin)
```

where:

```text
margin = 0.15
```

The pricing improvement is:

```text
Improvement% = (Static_MAE - ML_MAE) / Static_MAE * 100
```

The model-fit score is measured using R2:

```text
R2 = 1 - sum((y_i - y_hat_i)^2) / sum((y_i - y_bar)^2)
```

Using the experiment results:

```text
Static_MAE = 100.27005203097912
ML_MAE = 11.217385659614619
Static_R2 = -4.276097844000223
ML_R2 = 0.8966803787227509
Improvement = 88.81282553224473%
```

## 8.8 Algorithm 1: BDPP-IoT Setup

```text
Input:
  Attribute authorities, synthetic IoMT data, blockchain network, IPFS node

Output:
  Initialized BDPP-IoT system

Steps:
  1. Define attribute domains for each authority.
  2. Initialize user version registry on blockchain.
  3. Generate synthetic IoMT records.
  4. Generate historical transaction records.
  5. Initialize TenSEAL CKKS context.
  6. Initialize Kubo IPFS storage.
  7. Start Ganache local blockchain.
  8. Deploy BDPPLedger smart contract.
```

## 8.9 Algorithm 2: Secure Data Transaction

```text
Input:
  Medical sensor vector M, access policy P, user key SK_u

Output:
  Access decision, CKKS result, reliability flag, transaction log

Steps:
  1. Create MA-CP-ABE policy P.
  2. Encrypt symmetric key reference under P.
  3. Encrypt M using TenSEAL CKKS.
  4. Upload encrypted payload to IPFS Kubo.
  5. Store returned CID on blockchain.
  6. Check whether Policy(S_u) = 1.
  7. Check whether v_key = v_chain.
  8. If both checks pass, allow access.
  9. Retrieve encrypted payload using CID.
  10. Perform CKKS encrypted computation.
  11. Decrypt approximate result.
  12. Compute EBR error percentage.
  13. Store reliability flag on-chain.
  14. Store transaction price on-chain.
```

## 8.10 Algorithm 3: Ablation Study

```text
Input:
  Same dataset and transaction history for all configurations

Configurations:
  C1 = Base paper simulation
  C2 = Full BDPP-IoT
  C3 = Without revocation
  C4 = Without EBR
  C5 = Without ML pricing

Steps:
  1. Run each configuration.
  2. Measure revoked-user blocking.
  3. Measure unreliable CKKS detection.
  4. Measure pricing MAE.
  5. Compute security score.
  6. Compute pricing improvement percentage.
  7. Save results to ablation_results.csv.
```

## 8.11 Algorithm 4: Smart Contract Benchmark

```text
Input:
  Deployed BDPPLedger contract, number of runs N

Operations:
  storeCID
  getCID
  registerUser
  revokeUser
  logReliability
  logTransaction

Steps:
  1. Repeat each operation N times.
  2. Count successful and failed calls.
  3. Record max, min, and average latency.
  4. Compute send rate and throughput.
  5. Save results to blockchain_benchmark_results.csv.
```
