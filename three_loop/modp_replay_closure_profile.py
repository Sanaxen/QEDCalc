"""Profile finite-field replay dependency closures for selected Q01 pivots."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .modp_pivot_trace import ModPPivotTrace, replay_dependency_closure


@dataclass(frozen=True)
class ReplayClosureRecord:
    target: tuple[int, ...]
    replay_pivot_count: int


@dataclass(frozen=True)
class ReplayClosureProfile:
    requested_target_count: int
    solved_target_count: int
    unsolved_target_count: int
    max_replay_pivot_count: int
    min_replay_pivot_count: int
    records: tuple[ReplayClosureRecord, ...]


def profile_replay_closure_sizes(
    trace: ModPPivotTrace,
    requested: Iterable[IntegralIndex],
) -> ReplayClosureProfile:
    requested = tuple(dict.fromkeys(requested))
    pivot_set = set(trace.pivot_indices)
    records = []
    for target in requested:
        if target not in pivot_set:
            continue
        closure = replay_dependency_closure(trace, (target,))
        records.append(ReplayClosureRecord(target.powers, len(closure)))
    counts = [record.replay_pivot_count for record in records]
    return ReplayClosureProfile(
        requested_target_count=len(requested),
        solved_target_count=len(records),
        unsolved_target_count=len(requested) - len(records),
        max_replay_pivot_count=max(counts, default=0),
        min_replay_pivot_count=min(counts, default=0),
        records=tuple(records),
    )
