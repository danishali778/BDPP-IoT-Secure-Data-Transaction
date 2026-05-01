from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class KuboIPFSStorage:
    """Real IPFS backend using the Kubo command-line client.

    This backend requires:
      1. Kubo installed either on PATH or in the project tools directory.
      2. A local IPFS repository initialized for command-line add/cat.
    """

    scheme_name = "IPFS_KUBO"

    def __init__(
        self,
        binary: str = "ipfs",
        repo_path: Path | None = None,
        payload_dir: Path | None = None,
    ) -> None:
        self.binary = binary
        self.repo_path = repo_path or Path(".ipfs")
        self.payload_dir = payload_dir or Path("outputs") / "ipfs_payloads"
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.env = os.environ.copy()
        self.env["IPFS_PATH"] = str(self.repo_path.resolve())
        self._check_binary_and_repo()

    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.binary, *args],
            capture_output=True,
            text=True,
            check=True,
            env=self.env,
        )

    def _check_binary_and_repo(self) -> None:
        try:
            self._run(["--version"])
        except FileNotFoundError as exc:
            raise RuntimeError("Kubo IPFS CLI was not found on PATH.") from exc

        if not (self.repo_path / "config").exists():
            self._run(["init", "--profile", "server"])

        try:
            self._run(["id"])
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip()
            raise RuntimeError(f"Kubo IPFS repository is not usable: {detail}") from exc

    def add(self, payload: Any) -> str:
        file_path = self.payload_dir / "latest_payload.json"
        file_path.write_text(json.dumps(payload, sort_keys=True, default=str), encoding="utf-8")
        result = self._run(["add", "-Q", str(file_path)])
        return result.stdout.strip()

    def get(self, cid: str) -> Any:
        result = self._run(["cat", cid])
        return json.loads(result.stdout)
