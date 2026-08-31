"""Back-substitute finite-field pivot rules to terminal support.

This module stays entirely in the finite field.  It recursively substitutes the
forward-elimination pivot rules until only non-pivot integrals remain, allowing
us to measure the terminal support of selected targets before attempting any
symbolic coefficient reconstruction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex, sector_rank
from .modp_pivot_trace import ModPPivotTrace


@dataclass(frozen=True)
class ModPTerminalSupportRecord:
    target: tuple[int, ...]
    terminal_count: int
    terminals: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ModPTerminalSupportProfile:
    requested_target_count: int
    solved_target_count: int
    unsolved_target_count: int
    distinct_terminal_count: int
    min_terminal_count: int
    max_terminal_count: int
    common_terminal_count: int
    records: tuple[ModPTerminalSupportRecord, ...]


def reduce_pivot_to_terminals_mod_p(
    trace: ModPPivotTrace,
    target: IntegralIndex,
) -> dict[IntegralIndex, int]:
    """Return the exact mod-p terminal expansion for one pivot target."""
    prime = trace.prime
    by_pivot = {IntegralIndex(record.pivot): record for record in trace.records}
    memo: dict[IntegralIndex, dict[IntegralIndex, int]] = {}
    visiting: set[IntegralIndex] = set()

    def reduce(index: IntegralIndex) -> dict[IntegralIndex, int]:
        cached = memo.get(index)
        if cached is not None:
            return dict(cached)
        record = by_pivot.get(index)
        if record is None:
            result = {index: 1}
            memo[index] = result
            return dict(result)
        if index in visiting:
            raise ValueError(f"Cycle in mod-p pivot graph at I{index.powers}")
        visiting.add(index)
        total: dict[IntegralIndex, int] = {}
        for powers, coeff in record.rhs:
            child = IntegralIndex(powers)
            child_reduction = reduce(child)
            factor = coeff % prime
            for terminal, child_coeff in child_reduction.items():
                value = (total.get(terminal, 0) + factor * child_coeff) % prime
                if value:
                    total[terminal] = value
                else:
                    total.pop(terminal, None)
        visiting.remove(index)
        memo[index] = dict(total)
        return dict(total)

    return reduce(target)


def profile_terminal_support_mod_p(
    trace: ModPPivotTrace,
    requested: Iterable[IntegralIndex],
) -> ModPTerminalSupportProfile:
    requested = tuple(dict.fromkeys(requested))
    pivot_set = set(trace.pivot_indices)
    records = []
    support_sets: list[set[IntegralIndex]] = []
    for target in requested:
        if target not in pivot_set:
            continue
        reduction = reduce_pivot_to_terminals_mod_p(trace, target)
        terminals = tuple(sorted(reduction, key=sector_rank, reverse=True))
        support_sets.append(set(terminals))
        records.append(ModPTerminalSupportRecord(
            target=target.powers,
            terminal_count=len(terminals),
            terminals=tuple(index.powers for index in terminals),
        ))

    counts = [record.terminal_count for record in records]
    union = set().union(*support_sets) if support_sets else set()
    common = set.intersection(*support_sets) if support_sets else set()
    return ModPTerminalSupportProfile(
        requested_target_count=len(requested),
        solved_target_count=len(records),
        unsolved_target_count=len(requested) - len(records),
        distinct_terminal_count=len(union),
        min_terminal_count=min(counts, default=0),
        max_terminal_count=max(counts, default=0),
        common_terminal_count=len(common),
        records=tuple(records),
    )
