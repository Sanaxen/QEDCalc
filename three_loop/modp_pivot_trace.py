"""Trace finite-field Laporta pivots and dependency support without symbolic fill-in.

This records, for every pivot chosen by the existing forward mod-p elimination
ordering, the source equation label, pivot coefficient, and the immediate RHS
integrals after already-known pivots have been eliminated.  The trace is meant
to drive later selective symbolic replay; it does not itself claim a symbolic
reduction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from qedcalc.operations.ibp import IBPEquation, IntegralIndex, sector_rank
from .sector_local_modp import _rational_mod_p

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class ModPPivotRecord:
    pivot: tuple[int, ...]
    source_equation_index: int
    source_equation_label: str
    pivot_coefficient: int
    rhs: tuple[tuple[tuple[int, ...], int], ...]
    eliminated_prior_pivots: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ModPPivotTrace:
    prime: int
    equation_count: int
    integral_count: int
    pivot_count: int
    records: tuple[ModPPivotRecord, ...]

    @property
    def pivot_indices(self) -> tuple[IntegralIndex, ...]:
        return tuple(IntegralIndex(record.pivot) for record in self.records)


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def forward_eliminate_mod_p_with_trace(
    equations: Sequence[IBPEquation],
    prime: int,
    *,
    progress: ProgressCallback | None = None,
) -> ModPPivotTrace:
    """Run the current sparse forward elimination while recording pivot provenance."""
    indices = {idx for eq in equations for idx in eq.terms}
    ordered = sorted(indices, key=sector_rank, reverse=True)
    rank_pos = {idx: pos for pos, idx in enumerate(ordered)}

    rows = []
    for eq_no, eq in enumerate(equations):
        row = {}
        for idx, coeff in eq.terms.items():
            c = _rational_mod_p(coeff, prime)
            if c:
                row[idx] = c
        if row:
            rows.append((eq_no, eq.label, row))
    rows.sort(key=lambda item: min(rank_pos[idx] for idx in item[2]))

    rules: dict[IntegralIndex, dict[IntegralIndex, int]] = {}
    records = []
    total = len(rows)
    for n, (eq_no, label, row0) in enumerate(rows, start=1):
        row = dict(row0)
        eliminated = []
        while True:
            solved = [idx for idx in row if idx in rules]
            if not solved:
                break
            lhs = min(solved, key=lambda idx: rank_pos[idx])
            eliminated.append(lhs)
            fac = row.pop(lhs) % prime
            if fac:
                for idx, coeff in rules[lhs].items():
                    val = (row.get(idx, 0) + fac * coeff) % prime
                    if val:
                        row[idx] = val
                    else:
                        row.pop(idx, None)
        if row:
            pivot = min(row, key=lambda idx: rank_pos[idx])
            c = row.pop(pivot) % prime
            inv = pow(c, prime - 2, prime)
            rhs = {
                idx: (-coeff * inv) % prime
                for idx, coeff in row.items()
                if coeff % prime
            }
            rules[pivot] = rhs
            records.append(ModPPivotRecord(
                pivot=pivot.powers,
                source_equation_index=eq_no,
                source_equation_label=label,
                pivot_coefficient=c,
                rhs=tuple(
                    (idx.powers, int(coeff))
                    for idx, coeff in sorted(rhs.items(), key=lambda item: sector_rank(item[0]), reverse=True)
                ),
                eliminated_prior_pivots=tuple(idx.powers for idx in eliminated),
            ))
        if n == 1 or n == total or n % 100 == 0:
            _progress(progress, f"mod-p trace p={prime}", n, total)

    return ModPPivotTrace(
        prime=int(prime),
        equation_count=len(equations),
        integral_count=len(indices),
        pivot_count=len(records),
        records=tuple(records),
    )


def dependency_closure(
    trace: ModPPivotTrace,
    requested: Sequence[IntegralIndex],
) -> tuple[IntegralIndex, ...]:
    """Return pivot nodes needed to reduce requested integrals under this trace."""
    by_pivot = {IntegralIndex(record.pivot): record for record in trace.records}
    needed: set[IntegralIndex] = set()
    stack = list(requested)
    while stack:
        current = stack.pop()
        if current in needed or current not in by_pivot:
            continue
        needed.add(current)
        record = by_pivot[current]
        for powers, _coeff in record.rhs:
            child = IntegralIndex(powers)
            if child in by_pivot and child not in needed:
                stack.append(child)
    return tuple(sorted(needed, key=sector_rank, reverse=True))
