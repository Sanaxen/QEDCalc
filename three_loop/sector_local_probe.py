"""Fast generic-point rank audit for the largest Q01 blocker sector."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralFamily,
    IntegralIndex,
    laporta_forward_eliminate,
    prune_zero_sectors,
    sector_rank,
    specialize_ibp_system,
)
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, physical_sector
from .local_block_elimination import local_same_seed_equations
from .sector_local_laporta import largest_blocker_sector

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class SectorLocalProbeProfile:
    sector: tuple[int, ...]
    blocker_count: int
    dot_one_blocker_count: int
    equation_count: int
    integral_count: int
    pivot_counts: tuple[int, ...]
    solved_blocker_counts: tuple[int, ...]
    solved_dot_one_counts: tuple[int, ...]
    stable_across_probes: bool


def _progress(callback: ProgressCallback | None, stage: str,
              current: int | None = None, total: int | None = None) -> None:
    if callback is not None:
        callback(stage, current, total)


def default_q01_probe_points(family: IntegralFamily) -> tuple[dict[sp.Symbol, sp.Expr], ...]:
    symbols = {str(symbol): symbol for expr in family.denominator_exprs for symbol in expr.free_symbols}
    symbols[str(family.dimension_symbol)] = family.dimension_symbol
    points = []
    for d_value, z_value in ((sp.Rational(17, 5), sp.Rational(2, 7)), (sp.Rational(19, 6), sp.Rational(3, 11))):
        point: dict[sp.Symbol, sp.Expr] = {family.dimension_symbol: d_value}
        if "m" in symbols:
            point[symbols["m"]] = sp.Integer(1)
        if "z" in symbols:
            point[symbols["z"]] = z_value
        points.append(point)
    return tuple(points)


def audit_sector_local_probes(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    sector: tuple[int, ...] | None = None,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> SectorLocalProbeProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    _progress(progress, "collect blockers")
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    if sector is None:
        _progress(progress, "select largest sector")
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
    dot_one_blockers = tuple(
        blocker for blocker in sector_blockers
        if dot_degree(blocker, physical_count) == 1
    )

    equations = []
    total_blockers = len(sector_blockers)
    for offset, blocker in enumerate(sector_blockers, start=1):
        equations.extend(local_same_seed_equations(family, blocker, templates=templates))
        if offset == 1 or offset == total_blockers or offset % 10 == 0:
            _progress(progress, "build IBP equations", offset, total_blockers)
    _progress(progress, "prune zero sectors")
    equations = prune_zero_sectors(family, equations)
    _progress(progress, "count integral indices")
    integrals = {index for equation in equations for index in equation.terms}

    if probe_points is None:
        probe_points = default_q01_probe_points(family)
    pivot_counts = []
    solved_counts = []
    solved_dot_counts = []
    solved_sets = []
    total_probes = len(probe_points)
    for probe_no, point in enumerate(probe_points, start=1):
        _progress(progress, "specialize probe coefficients", probe_no, total_probes)
        probed = specialize_ibp_system(equations, point)
        _progress(progress, "Laporta forward elimination", probe_no, total_probes)
        rules = laporta_forward_eliminate(
            probed,
            rank=sector_rank,
            family=None,
            prune_scaleless=False,
        )
        _progress(progress, "analyze probe result", probe_no, total_probes)
        solved = {rule.lhs for rule in rules}
        solved_sets.append(frozenset(blocker for blocker in sector_blockers if blocker in solved))
        pivot_counts.append(len(rules))
        solved_counts.append(sum(blocker in solved for blocker in sector_blockers))
        solved_dot_counts.append(sum(blocker in solved for blocker in dot_one_blockers))

    stable = all(solved == solved_sets[0] for solved in solved_sets[1:]) if solved_sets else True
    _progress(progress, "complete")
    return SectorLocalProbeProfile(
        sector=sector,
        blocker_count=len(sector_blockers),
        dot_one_blocker_count=len(dot_one_blockers),
        equation_count=len(equations),
        integral_count=len(integrals),
        pivot_counts=tuple(pivot_counts),
        solved_blocker_counts=tuple(solved_counts),
        solved_dot_one_counts=tuple(solved_dot_counts),
        stable_across_probes=stable,
    )
