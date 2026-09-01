from __future__ import annotations

import os
import time
from pathlib import Path

from three_loop.parallel import run_process_jobs
from three_loop.runtime_config import format_runtime_config, load_runtime_config

ROOT = Path(__file__).resolve().parents[1]


def _square(value: int) -> tuple[int, int]:
    time.sleep(0.05)
    return os.getpid(), value * value


def main() -> None:
    config = load_runtime_config(root=ROOT, max_useful_processes=4)
    print("QEDCalc runtime multiprocessing smoke test")
    print(format_runtime_config(config))

    items = [1, 2, 3, 4]
    results = run_process_jobs(_square, items, processes=config.effective_processes)
    values = [result.result[1] for result in results]
    pids = [result.result[0] for result in results]

    if values != [1, 4, 9, 16]:
        raise RuntimeError(f"unexpected results: {values}")
    if config.effective_processes == 1 and len(set(pids)) != 1:
        raise RuntimeError("single-process mode unexpectedly used multiple worker PIDs")

    print(f"worker PIDs: {pids}")
    print(f"results: {values}")
    print("QEDCalc runtime multiprocessing smoke test PASS")


if __name__ == "__main__":
    main()
