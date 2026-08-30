"""Bounded seed selection for Q01 Laporta/IBP planning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import dot_degree, numerator_degree, physical_sector


@dataclass(frozen=True)
class SeedPruningPolicy:
    max_dot_degree: int
    max_numerator_degree: int
    allowed_physical_sectors: frozenset[tuple[int, ...]] | None = None

    def accepts(self, index: IntegralIndex, physical_count: int = 9) -> bool:
        if dot_degree(index, physical_count) > self.max_dot_degree:
            return False
        if numerator_degree(index, physical_count) > self.max_numerator_degree:
            return False
        if self.allowed_physical_sectors is not None:
            if physical_sector(index, physical_count) not in self.allowed_physical_sectors:
                return False
        return True


@dataclass(frozen=True)
class SeedPruningProfile:
    input_count: int
    accepted_count: int
    rejected_count: int
    accepted_sector_count: int
    rejected_for_dot_count: int
    rejected_for_numerator_count: int
    rejected_for_sector_count: int


def prune_seed_indices(
    indices: Iterable[IntegralIndex],
    policy: SeedPruningPolicy,
    *,
    physical_count: int = 9,
) -> tuple[IntegralIndex, ...]:
    """Apply a deterministic complexity/sector bound to a seed collection."""
    accepted = {
        index for index in indices
        if policy.accepts(index, physical_count)
    }
    return tuple(sorted(accepted, key=lambda index: index.powers, reverse=True))


def profile_seed_pruning(
    indices: Iterable[IntegralIndex],
    policy: SeedPruningPolicy,
    *,
    physical_count: int = 9,
) -> SeedPruningProfile:
    indices = tuple(set(indices))
    accepted = []
    reject_dot = 0
    reject_num = 0
    reject_sector = 0
    for index in indices:
        dot_bad = dot_degree(index, physical_count) > policy.max_dot_degree
        num_bad = numerator_degree(index, physical_count) > policy.max_numerator_degree
        sector_bad = (
            policy.allowed_physical_sectors is not None
            and physical_sector(index, physical_count) not in policy.allowed_physical_sectors
        )
        if not (dot_bad or num_bad or sector_bad):
            accepted.append(index)
            continue
        if dot_bad:
            reject_dot += 1
        if num_bad:
            reject_num += 1
        if sector_bad:
            reject_sector += 1

    return SeedPruningProfile(
        input_count=len(indices),
        accepted_count=len(accepted),
        rejected_count=len(indices) - len(accepted),
        accepted_sector_count=len({physical_sector(index, physical_count) for index in accepted}),
        rejected_for_dot_count=reject_dot,
        rejected_for_numerator_count=reject_num,
        rejected_for_sector_count=reject_sector,
    )


def descendant_sector_closure(
    sectors: Iterable[tuple[int, ...]],
) -> frozenset[tuple[int, ...]]:
    """Return all sub-sectors obtained by switching active physical lines off.

    Standard IBP reductions couple a sector to lower sectors.  For target-sector
    pruning we therefore retain the full downward closure rather than only the
    sectors observed directly in the numerator mapping.
    """
    closure: set[tuple[int, ...]] = set()
    for sector in sectors:
        active = [i for i, bit in enumerate(sector) if bit]
        for mask in range(1 << len(active)):
            child = list(sector)
            for j, position in enumerate(active):
                if not (mask & (1 << j)):
                    child[position] = 0
            closure.add(tuple(child))
    return frozenset(closure)
