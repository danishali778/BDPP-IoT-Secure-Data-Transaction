from __future__ import annotations

import hashlib
import json
from typing import Any


class IPFSSimulator:
    scheme_name = "IPFS_SIM"

    def __init__(self) -> None:
        self._objects: dict[str, Any] = {}

    def add(self, payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        cid = "cid_" + hashlib.sha256(raw).hexdigest()[:24]
        self._objects[cid] = payload
        return cid

    def get(self, cid: str) -> Any:
        return self._objects[cid]
