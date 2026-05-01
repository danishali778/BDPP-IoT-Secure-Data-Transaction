from __future__ import annotations

import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

from web3 import Web3


def ganache_connected(rpc_url: str) -> bool:
    return Web3(Web3.HTTPProvider(rpc_url)).is_connected()


@contextmanager
def managed_ganache(rpc_url: str, project_root: Path = Path(".")):
    if ganache_connected(rpc_url):
        yield None
        return

    cli_path = project_root / "node_modules" / "ganache" / "dist" / "node" / "cli.js"
    if not cli_path.exists():
        yield None
        return

    log_dir = project_root / "outputs" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = (log_dir / "ganache.out.log").open("w", encoding="utf-8")
    stderr = (log_dir / "ganache.err.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            "node",
            str(cli_path),
            "--server.host",
            "127.0.0.1",
            "--server.port",
            "8545",
            "--wallet.deterministic",
            "--chain.chainId",
            "1337",
            "--logging.quiet",
        ],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    try:
        for _ in range(30):
            if ganache_connected(rpc_url):
                break
            if process.poll() is not None:
                break
            time.sleep(0.5)
        yield process
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        stdout.close()
        stderr.close()

