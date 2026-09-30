"""Sparse mandatory-target master-basis discovery for large three-loop families.

The ordinary generic Stage-2 path uses Kira's select_mandatory_recursively over
an r/s/d seed.  That is robust but can select an enormous number of integrals.
For master-basis *discovery* we instead build a deterministic skeleton that
touches every non-empty physical subsector and only a small number of local
complexity directions inside each sector.

Level 0
    one corner integral per non-empty physical sector.

Level 1
    level 0 plus one single dot on every active physical line and one single
    numerator power on every auxiliary slot.

Level 2
    level 1 plus physical dot pairs, auxiliary numerator pairs, and one
    dot-plus-numerator mixed probe.

This is a discovery accelerator, not a replacement for closure validation.
A candidate basis must still pass the existing mandatory-union / candidate
closure checks before promotion.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement
from typing import Iterable

from three_loop.master_basis_api import FamilySpec, Seed, integral_complexity


IndexTuple = tuple[int, ...]


@dataclass(frozen=True)
class SparseTargetPlan:
    family_id: str
    level: int
    targets: tuple[IndexTuple, ...]
    sector_count: int
    physical_count: int
    auxiliary_count: int
    envelope: Seed

    @property
    def target_count(self) -> int:
        return len(self.targets)


def _sector_indices(physical_count: int, sector: int, total_slots: int) -> list[int]:
    values = [0] * total_slots
    for i in range(physical_count):
        if sector & (1 << i):
            values[i] = 1
    return values


def _sector_id(indices: Iterable[int], physical_count: int) -> int:
    sector = 0
    values = tuple(indices)
    for i in range(physical_count):
        if values[i] > 0:
            sector |= 1 << i
    return sector


def build_sparse_target_plan(spec: FamilySpec, *, level: int = 1) -> SparseTargetPlan:
    if level not in {0, 1, 2}:
        raise ValueError("sparse discovery level must be 0, 1, or 2")

    p = spec.unique_physical_count
    total = len(spec.propagators)
    a = total - p
    if p <= 0 or a < 0:
        raise ValueError(f"{spec.family_id}: invalid physical/auxiliary split {p}+{a}")
    if spec.top_sector != (1 << p) - 1:
        raise ValueError(
            f"{spec.family_id}: sparse discovery expects contiguous physical slots; "
            f"top_sector={spec.top_sector} physical_count={p}"
        )

    targets: set[IndexTuple] = set()
    for sector in range(1, spec.top_sector + 1):
        corner = _sector_indices(p, sector, total)
        active = [i for i in range(p) if corner[i] > 0]

        targets.add(tuple(corner))

        if level >= 1:
            for i in active:
                row = corner.copy()
                row[i] += 1
                targets.add(tuple(row))
            for j in range(p, total):
                row = corner.copy()
                row[j] = -1
                targets.add(tuple(row))

        if level >= 2:
            for i, j in combinations_with_replacement(active, 2):
                row = corner.copy()
                row[i] += 1
                row[j] += 1
                targets.add(tuple(row))
            for i, j in combinations_with_replacement(range(p, total), 2):
                row = corner.copy()
                row[i] -= 1
                row[j] -= 1
                targets.add(tuple(row))
            for i in active:
                for j in range(p, total):
                    row = corner.copy()
                    row[i] += 1
                    row[j] -= 1
                    targets.add(tuple(row))

    ordered = tuple(sorted(targets, key=lambda row: (_sector_id(row, p), row)))
    envelope = Seed(r=p, s=0, d=0)
    for row in ordered:
        c = integral_complexity(row)
        envelope = Seed(
            max(envelope.r, c.r),
            max(envelope.s, c.s),
            max(envelope.d, c.d),
        )

    sectors = {_sector_id(row, p) for row in ordered}
    expected = set(range(1, spec.top_sector + 1))
    if sectors != expected:
        raise ValueError(
            f"{spec.family_id}: sparse plan sector coverage mismatch "
            f"covered={len(sectors)} expected={len(expected)}"
        )

    return SparseTargetPlan(
        family_id=spec.family_id,
        level=level,
        targets=ordered,
        sector_count=len(sectors),
        physical_count=p,
        auxiliary_count=a,
        envelope=envelope,
    )


def kira_integral_text(family_id: str, indices: IndexTuple) -> str:
    return f"{family_id}[{','.join(str(v) for v in indices)}]"


def render_mandatory_targets(plan: SparseTargetPlan) -> str:
    return "\n".join(kira_integral_text(plan.family_id, row) for row in plan.targets) + "\n"
