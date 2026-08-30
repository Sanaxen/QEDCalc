"""Sector-wise distribution of unresolved Q01 blocker integrals."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, numerator_degree, physical_sector


@dataclass(frozen=True)
class SectorBlockProfile:
    sector: tuple[int, ...]
    blocker_count: int
    dot_one_count: int
    max_dot_degree: int
    max_numerator_degree: int
    active_physical_lines: int


def build_sector_block_profiles(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> tuple[SectorBlockProfile, ...]:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    blockers = collect_unresolved_blockers(family, targets, templates=templates)

    grouped: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    for blocker in blockers:
        grouped[physical_sector(blocker, physical_count)].append(blocker)

    profiles = []
    for sector, indices in grouped.items():
        profiles.append(SectorBlockProfile(
            sector=sector,
            blocker_count=len(indices),
            dot_one_count=sum(dot_degree(index, physical_count) == 1 for index in indices),
            max_dot_degree=max(dot_degree(index, physical_count) for index in indices),
            max_numerator_degree=max(numerator_degree(index, physical_count) for index in indices),
            active_physical_lines=sum(sector),
        ))

    return tuple(sorted(
        profiles,
        key=lambda profile: (
            profile.blocker_count,
            profile.active_physical_lines,
            profile.sector,
        ),
        reverse=True,
    ))
