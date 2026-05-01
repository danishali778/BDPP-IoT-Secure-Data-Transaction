# 9. Implementation Setup

This section describes the implementation environment, tools, libraries, project structure, and execution procedure used to validate BDPP-IoT.

## 9.1 Implementation Language and Environment

The implementation is written in Python and executed inside a local virtual environment:

```text
.venv/
```

The main command to run the full pipeline is:

```powershell
python run_experiments.py
```

or, without activating the virtual environment:

```powershell
.\.venv\Scripts\python.exe run_experiments.py
```

The implementation was tested on Windows PowerShell.

## 9.2 Major Tools and Libraries

| Component | Tool/Library |
|---|---|
| Programming language | Python |
| Data processing | pandas, numpy |
| ML pricing | scikit-learn Random Forest |
| CKKS encrypted computation | TenSEAL |
| IPFS storage | Kubo IPFS |
| Blockchain | Ganache |
| Smart contract | Solidity |
| Blockchain client | Web3.py |
| Resource monitoring | psutil |
| Graph generation | matplotlib |

## 9.3 Project Structure

The main project structure is:

```text
Info-Sec-Final-Project/
  contracts/
    BDPPLedger.sol
  docs/
    algorithms.md
    system_design.md
    report_sections/
  outputs/
    contracts/
    figures/
    tables/
    logs/
  src/
    bdpp_iot/
      access_control/
      blockchain/
      crypto/
      data/
      experiments/
      pricing/
      storage/
      visualization/
      workflow/
  run_experiments.py
  requirements.txt
```

## 9.4 Implemented Modules

### 9.4.1 Data Generation

The synthetic IoMT data generator is implemented in:

```text
src/bdpp_iot/data/generator.py
```

It generates:

```text
3500 synthetic sensor records
800 historical transaction records
```

The output files are:

```text
outputs/tables/synthetic_iomt_sample.csv
outputs/tables/transaction_history.csv
```

### 9.4.2 Access Control

The MA-CP-ABE policy-level model is implemented in:

```text
src/bdpp_iot/access_control/ma_abe.py
src/bdpp_iot/access_control/policy.py
```

It supports:

1. Multiple attribute authorities.
2. Authority-specific key fragments.
3. Boolean access policies.
4. Blockchain-style version revocation.
5. Anti-collusion evaluation.

Charm-Crypto was attempted for real CP-ABE, but it could not be built on the Windows setup because it requires native Microsoft C++ Build Tools and pairing-library dependencies. Therefore, the CP-ABE behavior is modeled at the access-policy and revocation level.

### 9.4.3 CKKS Encrypted Computation

CKKS is implemented using TenSEAL:

```text
src/bdpp_iot/crypto/ckks_tenseal.py
```

The fallback simulator is:

```text
src/bdpp_iot/crypto/ckks_sim.py
```

The backend selector is:

```text
src/bdpp_iot/crypto/ckks_backend.py
```

The experiment output confirms:

```text
ckks_backend = TENSEAL_CKKS
```

### 9.4.4 Error-Bound Reporting

The EBR module is implemented in:

```text
src/bdpp_iot/crypto/ebr.py
```

It calculates expected operation-specific values and compares them with decrypted CKKS outputs.

### 9.4.5 IPFS Storage

Real IPFS storage is implemented using Kubo:

```text
src/bdpp_iot/storage/ipfs_kubo.py
```

The storage backend selector is:

```text
src/bdpp_iot/storage/storage_backend.py
```

The experiment confirms:

```text
storage_backend = IPFS_KUBO
```

### 9.4.6 Blockchain and Smart Contract

The Solidity contract is:

```text
contracts/BDPPLedger.sol
```

It supports:

1. User registration.
2. User revocation.
3. User version retrieval.
4. CID storage.
5. CID retrieval.
6. Reliability logging.
7. Transaction logging.

The Web3.py client is:

```text
src/bdpp_iot/blockchain/contract_client.py
```

The Ganache manager is:

```text
src/bdpp_iot/blockchain/ganache_manager.py
```

The experiment confirms:

```text
blockchain_backend = GANACHE_SOLIDITY
```

### 9.4.7 ML Pricing

The pricing model is implemented in:

```text
src/bdpp_iot/pricing/ml_pricing.py
```

It compares static pricing with Random Forest pricing.

### 9.4.8 Ablation and Benchmarking

The ablation study is implemented in:

```text
src/bdpp_iot/experiments/ablation.py
```

The blockchain benchmark is implemented in:

```text
src/bdpp_iot/experiments/blockchain_benchmark.py
```

The resource monitor is implemented in:

```text
src/bdpp_iot/experiments/resource_monitor.py
```

## 9.5 Execution Flow

When the experiment is run, the terminal prints each stage:

```text
[1/12] Preparing output folders...
[2/12] Generating synthetic IoMT sensor records...
[3/12] Generating historical transaction records for ML pricing...
[4/12] Evaluating MA-CP-ABE access control and revocation...
[5/12] Running TenSEAL CKKS computation with EBR reliability checks...
[6/12] Training/evaluating ML-calibrated pricing model...
[7/12] Running ablation study...
[8/12] Running prototype runtime comparison...
[9/12] Running full secure transaction demo...
[10/12] Running smart-contract benchmark table...
[11/12] Collecting CPU and memory resource table...
[12/12] Saving CSV tables and 400 DPI figures...
```

## 9.6 Generated Outputs

The generated tables are:

```text
outputs/tables/access_control_results.csv
outputs/tables/ebr_results.csv
outputs/tables/pricing_results.csv
outputs/tables/ablation_results.csv
outputs/tables/secure_transaction_demo.csv
outputs/tables/blockchain_benchmark_results.csv
outputs/tables/resource_consumption_results.csv
outputs/tables/runtime_results.csv
```

The generated figures are:

```text
outputs/figures/bdpp_iot_layered_architecture.png
outputs/figures/bdpp_iot_methodology_pipeline.png
outputs/figures/access_control_comparison.png
outputs/figures/ckks_ebr_errors.png
outputs/figures/pricing_mae_comparison.png
outputs/figures/ablation_security_score.png
outputs/figures/blockchain_benchmark_throughput.png
outputs/figures/resource_consumption.png
outputs/figures/runtime_comparison.png
```

All figures are saved at 400 DPI.

