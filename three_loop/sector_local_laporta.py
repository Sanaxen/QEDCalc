"""Sector-local Laporta audit for the largest unresolved Q01 blocker sector."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, laporta_forward_eliminate, sector_rank
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, physical_sector
from .local_block_elimination import local_same_seed_equations
from .sector_block_profile import build_sector_block_profiles


@dataclass(frozen=True)
class SectorLocalLaportaProfile:
    sector: tuple[int, ...]
    blocker_count: int
    dot_one_blocker_count: int
    equation_count: int
    rule_count: int
    solved_blocker_count: int
    unsolved_blocker_count: int
    solved_dot_one_count: int
    unsolved_dot_one_count: int


def largest_blocker_sector(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> tuple[int, ...]:
    profiles = build_sector_block_profiles(
        family,
        targets,
        templates=templates,
        physical_count=physical_count,
    )
    if not profiles:
        raise ValueError("No unresolved blocker sectors found.")
    return profiles[0].sector


def audit_sector_local_laporta(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    sector: tuple[int, ...] | None = None,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> SectorLocalLaportaProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    if sector is None:
        sector = largest_blocker_sector(
            family,
            targets,
            templates=templates,
            physical_count=physical_count,
        )
    sector_blockers = tuple(
        blocker for blocker in blockers
        if physical_sector(blocker, physical_count) == sector
    )
    equations = []
    for blocker in sector_blockers:
        equations.extend(local_same_seed_equations(
            family,
            blocker,
            templates=templates,
        ))
    rules = laporta_forward_eliminate(
        equations,
        rank=sector_rank,
        family=family,
        prune_scaleless=True,
    )
    solved_lhs = {rule.lhs for rule in rules}
    solved = sum(blocker in solved_lhs for blocker in sector_blockers)
    dot_one_blockers = tuple(
        blocker for blocker in sector_blockers
        if dot_degree(blocker, physical_count) == 1
    )
    solved_dot_one = sum(blocker in solved_lhs for blocker in dot_one_blockers)
    return SectorLocalLaportaProfile(
        sector=sector,
        blocker_count=len(sector_blockers),
        dot_one_blocker_count=len(dot_one_blockers),
        equation_count=len(equations),
        rule_count=len(rules),
        solved_blocker_count=solved,
        unsolved_blocker_count=len(sector_blockers) - solved,
        solved_dot_one_count=solved_dot_one,
        unsolved_dot_one_count=len(dot_one_blockers) - solved_dot_one,
    )
