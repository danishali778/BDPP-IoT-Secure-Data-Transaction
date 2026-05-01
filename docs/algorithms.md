# BDPP-IoT Algorithms

## Algorithm 1: Multi-Authority Setup

```text
Input:
  A set of attribute domains U = {U_1, U_2, ..., U_n}

Output:
  Independent authority records AA_1 through AA_n

Steps:
  1. For each authority AA_k:
       a. Assign a non-overlapping attribute domain U_k.
       b. Generate authority public parameters PK_k.
       c. Keep authority secret parameters MK_k private.
  2. Store authority public metadata on the blockchain ledger.
  3. Initialize every user version v_u = 1.
```

Implementation note:

```text
The Windows environment could not build Charm-Crypto because it requires native Microsoft C++ Build Tools. Therefore, BDPP-IoT implements MA-CP-ABE at the policy, authority, key-fragment, revocation, and anti-collusion evaluation level.
```

## Algorithm 2: Version-Based Revocation

```text
Input:
  User u, current blockchain version v_chain

Steps:
  1. Read v_chain for user u from the ledger.
  2. Increment v_chain = v_chain + 1.
  3. Store the updated version on the ledger.
  4. Reject any future key where v_key != v_chain.
```

Access decision:

```text
Access(u, CT) = ALLOW if A(S_u) = 1 and v_key = v_chain
Access(u, CT) = DENY otherwise
```

## Algorithm 3: Operation-Aware CKKS Error-Bound Reporting

```text
Input:
  Plain vector M, operation op, decrypted approximate result y_hat, threshold t

Steps:
  1. Compute operation-aware expected result y:
       if op = mean: y = sum(M) / len(M)
       if op = sum: y = sum(M)
       if op = variance: y = variance(M)
  2. Compute error percentage:
       err = abs(y_hat - y) / max(abs(y), epsilon) * 100
  3. Return RELIABLE if err <= t.
  4. Return UNRELIABLE otherwise.
```

## Algorithm 4: ML-Calibrated Pricing

```text
Input:
  Historical transaction table H, new transaction feature vector x

Steps:
  1. If H has insufficient records, use base-paper static pricing.
  2. Train Random Forest Regressor on H.
  3. Predict fair price p_hat = RF(x).
  4. Set negotiation bounds:
       lower = p_hat * 0.85
       upper = p_hat * 1.15
  5. Pass bounds into the base-paper negotiation step.
```

## Algorithm 5: Ablation Study

```text
Input:
  Synthetic IoMT data, user requests, transaction history

Configurations:
  C1 = Base
  C2 = Full BDPP-IoT
  C3 = Without revocation
  C4 = Without EBR
  C5 = Without ML pricing

Steps:
  1. Run each configuration on the same data split.
  2. Measure revoked-user block rate.
  3. Measure CKKS unreliable-output detection rate.
  4. Measure pricing MAE.
  5. Measure average runtime.
  6. Save comparison tables and plots.
```

## Algorithm 6: Smart Contract Ledger Update

```text
Input:
  task_id, IPFS CID, user addresses, CKKS reliability result, final transaction price

Steps:
  1. Deploy BDPPLedger contract on Ganache.
  2. Register valid consumer and revoked consumer addresses.
  3. Revoke selected consumer by incrementing on-chain version.
  4. Store task_id -> IPFS CID on-chain.
  5. Store EBR reliability flag and scaled error value on-chain.
  6. Store buyer address, data type, and transaction price on-chain.
  7. Read back CID, user versions, reliability result, and transaction result.
  8. Compare on-chain values with local workflow values.
```
