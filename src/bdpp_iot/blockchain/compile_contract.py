from __future__ import annotations

import json
from pathlib import Path

import solcx


def compile_bdpp_ledger(
    source_path: Path = Path("contracts") / "BDPPLedger.sol",
    artifact_path: Path = Path("outputs") / "contracts" / "BDPPLedger.json",
    solcx_binary_path: Path = Path("tools") / "solcx",
    solc_version: str = "0.8.24",
) -> Path:
    solcx_binary_path.mkdir(parents=True, exist_ok=True)
    installed = [
        str(version)
        for version in solcx.get_installed_solc_versions(solcx_binary_path=solcx_binary_path)
    ]
    if solc_version not in installed:
        solcx.install_solc(solc_version, solcx_binary_path=solcx_binary_path)
    solcx.set_solc_version(solc_version, solcx_binary_path=solcx_binary_path)

    source = source_path.read_text(encoding="utf-8")
    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        optimize=True,
    )
    contract_id = next(key for key in compiled if key.endswith(":BDPPLedger"))
    contract = compiled[contract_id]
    artifact = {
        "contractName": "BDPPLedger",
        "abi": contract["abi"],
        "bytecode": contract["bin"],
        "source": str(source_path),
        "solc_version": solc_version,
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact_path


if __name__ == "__main__":
    print(compile_bdpp_ledger())
