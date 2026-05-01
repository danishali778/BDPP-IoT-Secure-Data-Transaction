# 7. System Architecture

The BDPP-IoT architecture follows the same layered style as the base paper, but it extends the original architecture with revocation-aware access control, operation-aware CKKS verification, and ML-based pricing. The architecture is organized into five layers:

1. Device Layer
2. Edge Layer
3. Data Service Layer
4. Blockchain Layer
5. Data Storage Layer

The generated architecture figure is available at:

```text
outputs/figures/bdpp_iot_layered_architecture.png
```

The generated methodology pipeline figure is available at:

```text
outputs/figures/bdpp_iot_methodology_pipeline.png
```

## 7.1 Device Layer

The device layer represents the Internet of Medical Things environment. In the implementation, real patient data is not used because medical data is sensitive and difficult to obtain due to privacy and consent restrictions. Instead, the system generates synthetic IoMT records.

Each synthetic record contains:

```text
patient_id
device_id
timestamp
data_type
heart_rate
temperature
systolic
diastolic
glucose
integrity_score
freshness
market_demand
seller_reputation
```

The default experiment generates:

```text
3500 synthetic sensor records
800 historical transaction records
```

This follows the base paper's simulated IoMT evaluation approach.

## 7.2 Edge Layer

The edge layer is responsible for access-control preparation and local preprocessing before storage and transaction. It contains:

1. Integrity and metadata preparation.
2. MA-CP-ABE policy creation.
3. User attribute validation.
4. Version-based revocation checking.

The access policy used in the secure transaction demo is:

```text
research_lab AND cardiology_researcher AND heart_rate
```

The access-control module supports Boolean policies with:

```text
AND
OR
parentheses
```

An example OR policy tested during the experiment is:

```text
research_lab AND (cardiology_researcher OR doctor) AND heart_rate
```

The experiment confirms:

```text
proposed_valid_allow = 1
proposed_invalid_block = 1
proposed_revoked_block = 1
or_policy_doctor_allow = 1
collusion_without_full_key_block = 1
```

This shows that the proposed access layer supports valid access, invalid-user blocking, revoked-user blocking, OR-policy access, and collusion resistance at the policy-model level.

## 7.3 Data Service Layer

The data service layer contains the computation and pricing logic. It has three main modules.

### 7.3.1 CKKS Encrypted Computation

CKKS encrypted computation is implemented using TenSEAL. The backend reported during the experiment is:

```text
ckks_backend = TENSEAL_CKKS
```

The secure transaction demo computes the daily mean heart rate over:

```text
1440 records
```

The result was:

```text
expected_result = 77.93935639865786
observed_result = 77.93935639801067
error_percent = 8.303773284056454e-10
reliable = 1
```

### 7.3.2 Error-Bound Reporting

The EBR module verifies whether the decrypted CKKS output is acceptable. It compares the observed approximate value against the operation-aware expected result. The experiment includes both normal CKKS behavior and a high-noise/fault-injection case.

The high-noise case was detected successfully:

```text
high_noise_error_percent = 4.500000002522298
high_noise_unreliable_detected = 1
```

### 7.3.3 ML Pricing

The ML pricing module uses a Random Forest Regressor trained on historical transaction records. It predicts transaction prices from data type, integrity, freshness, demand, reputation, volume, and access frequency.

The pricing results were:

```text
static_mae = 100.27005203097912
ml_mae = 11.217385659614619
static_rmse = 105.3339526638235
ml_rmse = 14.7401995782551
static_r2 = -4.276097844000223
ml_r2 = 0.8966803787227509
```

## 7.4 Blockchain Layer

The blockchain layer is implemented using:

```text
Ganache
Solidity
Web3.py
```

The deployed smart contract is:

```text
contracts/BDPPLedger.sol
```

The contract stores:

1. User version numbers.
2. Revocation updates.
3. IPFS CID mappings.
4. CKKS reliability logs.
5. Transaction logs.

The experiment confirms:

```text
blockchain_backend = GANACHE_SOLIDITY
contract_address = 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
onchain_valid_version = 1
onchain_revoked_version = 2
onchain_reliable = 1
onchain_price = 125
```

## 7.5 Data Storage Layer

The data storage layer is implemented using real IPFS Kubo. The encrypted TenSEAL payload is serialized and stored in IPFS. IPFS returns a content identifier, which is then stored on-chain.

The experiment confirms:

```text
storage_backend = IPFS_KUBO
cid = QmTjgnUVrxdjMGyXP6ZFNKz4sWw76DZ6j7nZnApyfFtRXq
onchain_cid = QmTjgnUVrxdjMGyXP6ZFNKz4sWw76DZ6j7nZnApyfFtRXq
```

Since the CID and on-chain CID match, the storage and blockchain layers are correctly connected.

## 7.6 Architecture Summary

The final implementation is a hybrid real/simulated prototype:

| Component | Implementation Status |
|---|---|
| CKKS encrypted computation | Real TenSEAL implementation |
| IPFS storage | Real Kubo implementation |
| Blockchain logging | Real Ganache + Solidity + Web3.py implementation |
| ML pricing | Real scikit-learn Random Forest implementation |
| MA-CP-ABE | Formal policy-level model |
| Medical IoT data | Synthetic simulated IoMT data |

The only component not implemented as real cryptographic CP-ABE is the MA-CP-ABE layer. Charm-Crypto was attempted, but it could not be built in the Windows environment because it requires native Microsoft C++ Build Tools and pairing-library dependencies. Therefore, access control is implemented at the policy, authority-fragment, revocation, and anti-collusion level.
