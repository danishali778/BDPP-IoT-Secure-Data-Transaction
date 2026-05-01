from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field

import pandas as pd
import psutil


@dataclass
class ResourceMonitor:
    interval: float = 0.2
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)
    _samples: list[dict] = field(default_factory=list, init=False)
    _seen: dict[int, psutil.Process] = field(default_factory=dict, init=False)

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> pd.DataFrame:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        return self.summary()

    def _sample_loop(self) -> None:
        process = psutil.Process(os.getpid())
        while not self._stop.is_set():
            processes = [process]
            try:
                processes.extend(process.children(recursive=True))
            except psutil.Error:
                pass

            for proc in processes:
                try:
                    if proc.pid not in self._seen:
                        self._seen[proc.pid] = proc
                        proc.cpu_percent(interval=None)
                        continue
                    proc = self._seen[proc.pid]
                    name = proc.name().lower()
                    if "python" in name:
                        label = "python_pipeline"
                    elif "node" in name:
                        label = "ganache_node"
                    elif "ipfs" in name:
                        label = "ipfs_kubo_cli"
                    else:
                        continue
                    self._samples.append(
                        {
                            "Name": label,
                            "pid": proc.pid,
                            "CPU %": proc.cpu_percent(interval=None),
                            "Memory MB": proc.memory_info().rss / (1024 * 1024),
                        }
                    )
                except psutil.Error:
                    continue
            time.sleep(self.interval)

    def summary(self) -> pd.DataFrame:
        if not self._samples:
            return pd.DataFrame(
                columns=["Name", "CPU % (max)", "CPU % (avg)", "Memory max (MB)", "Memory avg (MB)"]
            )
        frame = pd.DataFrame(self._samples)
        grouped = frame.groupby("Name", as_index=False).agg(
            {
                "CPU %": ["max", "mean"],
                "Memory MB": ["max", "mean"],
            }
        )
        grouped.columns = ["Name", "CPU % (max)", "CPU % (avg)", "Memory max (MB)", "Memory avg (MB)"]
        return grouped
