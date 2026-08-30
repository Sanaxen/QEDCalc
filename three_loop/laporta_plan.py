"""Demand profiling for finite Q01 Laporta/IBP seed planning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex


@dataclass(frozen=True)
class SectorDemandProfile:
    """Observed reduction demand for one physical Q01 sector."""

    sector: tuple[int, ...]
    target_count: int
    max_dot_degree: int
    max_numerator_degree: int
    max_total_complexity: int
    min_powers: tuple[int, ...]
    max_powers: tuple[int, ...]

    @property
    def active_physical_lines(self) -> int:
        return sum(self.sector)


def physical_sector(index: IntegralIndex, physical_count: int = 9) -> tuple[int, ...]:
    """Return the positive-power presence mask of physical propagators."""
    return tuple(1 if power > 0 else 0 for power in index.powers[:physical_count])


def dot_degree(index: IntegralIndex, physical_count: int = 9) -> int:
    """Total extra positive physical denominator power above unit powers."""
    return sum(max(power - 1, 0) for power in index.powers[:physical_count])


def numerator_degree(index: IntegralIndex, physical_count: int = 9) -> int:
    """Total irreducible/numerator power, including auxiliary ISP indices."""
    return sum(max(-power, 0) for power in index.powers[physical_count:])


def total_complexity(index: IntegralIndex, physical_count: int = 9) -> int:
    return dot_degree(index, physical_count) + numerator_degree(index, physical_count)


def build_sector_demand_profiles(
    indices: Iterable[IntegralIndex],
    *,
    physical_count: int = 9,
) -> tuple[SectorDemandProfile, ...]:
    """Group target integrals by sector and record the exact observed bounds."""
    grouped: dict[tuple[int, ...], list[IntegralIndex]] = {}
    for index in indices:
        grouped.setdefault(physical_sector(index, physical_count), []).append(index)

    profiles = []
    for sector, members in grouped.items():
        width = len(members[0].powers)
        min_powers = tuple(min(index.powers[i] for index in members) for i in range(width))
        max_powers = tuple(max(index.powers[i] for index in members) for i in range(width))
        profiles.append(SectorDemandProfile(
            sector=sector,
            target_count=len(members),
            max_dot_degree=max(dot_degree(index, physical_count) for index in members),
            max_numerator_degree=max(numerator_degree(index, physical_count) for index in members),
            max_total_complexity=max(total_complexity(index, physical_count) for index in members),
            min_powers=min_powers,
            max_powers=max_powers,
        ))

    return tuple(sorted(
        profiles,
        key=lambda profile: (
            profile.active_physical_lines,
            profile.max_total_complexity,
            profile.target_count,
            profile.sector,
        ),
        reverse=True,
    ))
