"""Group lower-sector finite-field terminal supports by physical sector."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import physical_sector
from .remaining_target_classification import corrected_total_complexity


@dataclass(frozen=True)
class LowerSectorRow:
    sector: tuple[int, ...]
    terminal_count: int
    min_complexity: int
    max_complexity: int


@dataclass(frozen=True)
class LowerSectorDistributionProfile:
    source_sector: tuple[int, ...]
    lower_terminal_count: int
    lower_sector_count: int
    largest_sector_terminal_count: int
    rows: tuple[LowerSectorRow, ...]


def profile_lower_sector_distribution(
    terminals: Iterable[IntegralIndex],
    *,
    source_sector: tuple[int, ...],
    physical_count: int = 9,
) -> LowerSectorDistributionProfile:
    unique = tuple(dict.fromkeys(terminals))
    grouped: dict[tuple[int, ...], list[IntegralIndex]] = {}
    for index in unique:
        sector = physical_sector(index, physical_count)
        if sector == source_sector:
            continue
        grouped.setdefault(sector, []).append(index)

    rows = []
    for sector, indices in grouped.items():
        complexities = [corrected_total_complexity(index, physical_count) for index in indices]
        rows.append(LowerSectorRow(
            sector=sector,
            terminal_count=len(indices),
            min_complexity=min(complexities, default=0),
            max_complexity=max(complexities, default=0),
        ))
    rows.sort(key=lambda row: (row.terminal_count, row.sector), reverse=True)
    return LowerSectorDistributionProfile(
        source_sector=source_sector,
        lower_terminal_count=sum(row.terminal_count for row in rows),
        lower_sector_count=len(rows),
        largest_sector_terminal_count=max((row.terminal_count for row in rows), default=0),
        rows=tuple(rows),
    )


def sector_size_histogram(profile: LowerSectorDistributionProfile) -> dict[int, int]:
    return dict(sorted(Counter(row.terminal_count for row in profile.rows).items()))
