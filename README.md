# BDPP-IoT Implementation

BDPP-IoT is a prototype implementation of the proposed methodology for secure IoT medical data transactions. It follows the base paper's simulated IoMT evaluation style and adds:

- Multi-Authority CP-ABE style access control with blockchain version revocation.
- Operation-aware CKKS error-bound reporting.
- ML-calibrated dynamic pricing.
- Ablation experiments for the proposed components.

## Folder Structure

```text
Info-Sec-Final-Project/
  README.md
  requirements.txt
  run_experiments.py
  docs/
    system_design.md
    algorithms.md
  outputs/
    figures/
    tables/
    logs/
  src/
    bdpp_iot/
      __init__.py
      config.py
      main.py
      pipeline.py
      access_control/
        __init__.py
        ma_abe.py
      blockchain/
        __init__.py
        ledger.py
      crypto/
        __init__.py
        ckks_sim.py
        ebr.py
      data/
        __init__.py
        generator.py
      experiments/
        __init__.py
        ablation.py
      pricing/
        __init__.py
        ml_pricing.py
      storage/
        __init__.py
        ipfs_sim.py
      visualization/
        __init__.py
        plots.py
```

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_experiments.py
```

Generated results are written to:

```text
outputs/tables/
outputs/figures/
outputs/logs/
```

Figures are saved at 400 DPI for report use.
The experiment also prints each pipeline stage, key metrics, blockchain benchmark values, and resource consumption to the terminal while it runs.

## Current Real Integrations

The CKKS component now uses TenSEAL by default:

```text
src/bdpp_iot/crypto/ckks_tenseal.py
```

The simulator remains available as a fallback if TenSEAL is not installed. Output tables include a `ckks_backend` column so the report can show whether the run used `TENSEAL_CKKS` or `CKKS_SIM`.

The current implementation status is:

| Component | Status |
|---|---|
| TenSEAL CKKS | Implemented |
| CKKS fallback simulator | Implemented |
| Error-Bound Reporting | Implemented |
| ML pricing | Implemented |
| IPFS Kubo | Implemented |
| Blockchain smart contracts | Implemented with Ganache + Solidity + Web3.py |
| MA-CP-ABE | Formal policy-level implementation with revocation and anti-collusion tests |

## Real IPFS Kubo

Kubo is installed locally in the project:

```text
tools/kubo/kubo/ipfs.exe
```

The implementation uses a project-local IPFS repository:

```text
.ipfs/
```

The real backend lives at:

```text
src/bdpp_iot/storage/ipfs_kubo.py
```

When Kubo is available, `secure_transaction_demo.csv` reports:

```text
storage_backend = IPFS_KUBO
```

If Kubo is missing or the local repository is unusable, the pipeline automatically falls back to `IPFS_SIM`.

## Real Blockchain Smart Contract

The real blockchain layer uses:

```text
Ganache local Ethereum chain
Solidity smart contract
Web3.py Python client
```

Contract:

```text
contracts/BDPPLedger.sol
```

Python client:

```text
src/bdpp_iot/blockchain/contract_client.py
```

The pipeline starts Ganache automatically during `run_experiments.py`, deploys the contract, writes the IPFS CID, records user revocation versions, logs the CKKS reliability flag, and stores a transaction price. Successful runs report:

```text
blockchain_backend = GANACHE_SOLIDITY
```

The generated contract artifact is:

```text
outputs/contracts/BDPPLedger.json
```

Base-paper-style blockchain and resource tables are generated at:

```text
outputs/tables/blockchain_benchmark_results.csv
outputs/tables/resource_consumption_results.csv
```

Related figures:

```text
outputs/figures/blockchain_benchmark_throughput.png
outputs/figures/resource_consumption.png
```

## MA-CP-ABE Access Control

Charm-Crypto was tested for real CP-ABE support, but it requires native Microsoft C++ Build Tools on this Windows setup. The project therefore uses a formal policy-level MA-CP-ABE implementation:

```text
src/bdpp_iot/access_control/ma_abe.py
src/bdpp_iot/access_control/policy.py
```

It supports:

```text
AND / OR policy parsing
independent attribute authorities
per-user authority key fragments
blockchain-style version revocation
simulated encrypted symmetric-key references
anti-collusion evaluation
```

The report should state this precisely:

```text
CP-ABE behavior is implemented at the access-policy and revocation level, while CKKS, IPFS storage, and blockchain logging are implemented with real tools.
```
