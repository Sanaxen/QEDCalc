"""Structural classification of finite-field block-reduction RHS integrals."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import physical_sector
from .remaining_target_classification import classify_remaining_targets


@dataclass(frozen=True)
class BlockRHSectorRow:
    sector: tuple[int, ...]
    terminal_count: int


@dataclass(frozen=True)
class BlockRHSStructureProfile:
    source_sector: tuple[int, ...]
    unique_rhs_count: int
    same_sector_count: int
    lower_sector_count: int
    higher_or_other_count: int
    distinct_lower_sector_count: int
    largest_lower_sector_count: int
    active_line_histogram: tuple[tuple[int, int], ...]
    dot_degree_histogram: tuple[tuple[int, int], ...]
    full_numerator_degree_histogram: tuple[tuple[int, int], ...]
    scalar_count: int
    lower_sector_rows: tuple[BlockRHSectorRow, ...]
    same_sector_indices: tuple[tuple[int, ...], ...]
    higher_or_other_indices: tuple[tuple[int, ...], ...]


def classify_block_rhs_structure(
    rhs_indices: Iterable[IntegralIndex],
    *,
    source_sector: tuple[int, ...],
    physical_count: int = 9,
) -> BlockRHSStructureProfile:
    indices = tuple(sorted(set(rhs_indices), key=lambda idx: idx.powers))
    source_lines = sum(source_sector)
    same = []
    other = []
    lower_counts: Counter[tuple[int, ...]] = Counter()

    for index in indices:
        sector = physical_sector(index, physical_count)
        if sector == source_sector:
            same.append(index)
        elif sum(sector) < source_lines:
            lower_counts[sector] += 1
        else:
            other.append(index)

    classes = classify_remaining_targets(indices, physical_count=physical_count)
    active_hist = Counter(record.active_physical_lines for record in classes)
    dot_hist = Counter(record.dot_degree for record in classes)
    num_hist = Counter(record.full_numerator_degree for record in classes)
    scalar_count = sum(record.is_scalar_subtopology for record in classes)

    lower_rows = tuple(
        BlockRHSectorRow(sector=sector, terminal_count=count)
        for sector, count in sorted(lower_counts.items(), key=lambda item: (-item[1], item[0]))
    )

    return BlockRHSStructureProfile(
        source_sector=tuple(source_sector),
        unique_rhs_count=len(indices),
        same_sector_count=len(same),
        lower_sector_count=sum(lower_counts.values()),
        higher_or_other_count=len(other),
        distinct_lower_sector_count=len(lower_counts),
        largest_lower_sector_count=max(lower_counts.values(), default=0),
        active_line_histogram=tuple(sorted(active_hist.items())),
        dot_degree_histogram=tuple(sorted(dot_hist.items())),
        full_numerator_degree_histogram=tuple(sorted(num_hist.items())),
        scalar_count=scalar_count,
        lower_sector_rows=lower_rows,
        same_sector_indices=tuple(index.powers for index in same),
        higher_or_other_indices=tuple(index.powers for index in other),
    )
