from __future__ import annotations

import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class TimedResult:
    item: object
    result: object
    elapsed_seconds: float


def _timed_call(worker: Callable[[T], R], item: T) -> TimedResult:
    started = time.perf_counter()
    result = worker(item)
    return TimedResult(item=item, result=result, elapsed_seconds=time.perf_counter() - started)


def run_process_jobs(
    worker: Callable[[T], R],
    items: Iterable[T],
    *,
    processes: int,
) -> list[TimedResult]:
    """Run independent CPU-bound jobs sequentially or with Windows-safe processes.

    A process count of one deliberately avoids multiprocessing overhead and is
    the safe low-memory mode.  For process counts above one, a ``spawn`` context
    is used explicitly so behavior matches Windows even when tests are run on a
    different platform.
    """

    jobs = list(items)
    if not jobs:
        return []
    if processes <= 1 or len(jobs) == 1:
        return [_timed_call(worker, item) for item in jobs]

    worker_count = min(int(processes), len(jobs))
    context = mp.get_context("spawn")
    completed: dict[int, TimedResult] = {}
    with ProcessPoolExecutor(max_workers=worker_count, mp_context=context) as executor:
        future_to_position = {
            executor.submit(_timed_call, worker, item): position
            for position, item in enumerate(jobs)
        }
        for future in as_completed(future_to_position):
            position = future_to_position[future]
            completed[position] = future.result()
    return [completed[position] for position in range(len(jobs))]
