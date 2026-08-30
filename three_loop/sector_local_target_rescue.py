"""Measure whether sector-local blocker equations rescue original Q01 targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, prune_zero_sectors, specialize_ibp_system
from .blocker_reduction import collect_unresolved_blockers
from .dependency_audit import target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import physical_sector
from .local_block_elimination import local_same_seed_equations
from .reverse_dependency import reverse_pivot_equations_for_target
from .sector_local_laporta import largest_blocker_sector
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name
from .sector_local_probe import default_q01_probe_points

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class SectorLocalTargetRescueProfile:
    sector: tuple[int, ...]
    original_target_count: int
    globally_unresolved_target_count: int
    sector_unresolved_target_count: int
    blocker_count: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    pivot_counts: tuple[int, ...]
    solved_sector_target_counts: tuple[int, ...]
    unsolved_sector_target_counts: tuple[int, ...]
    stable_across_runs: bool


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def unresolved_targets_after_one_hop(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    progress: ProgressCallback | None = None,
) -> tuple[IntegralIndex, ...]:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    unresolved = []
    total = len(targets)
    for n, target in enumerate(targets, start=1):
        if target_direct_pivot_equations(family, target, templates=templates):
            pass
        elif reverse_pivot_equations_for_target(family, target, templates=templates):
            pass
        else:
            unresolved.append(target)
        if n == 1 or n == total or n % 100 == 0:
            _progress(progress, "classify unresolved targets", n, total)
    return tuple(unresolved)


def audit_sector_local_target_rescue(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    sector: tuple[int, ...] | None = None,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> SectorLocalTargetRescueProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    unresolved = unresolved_targets_after_one_hop(
        family, targets, templates=templates, progress=progress
    )
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    if sector is None:
        sector = largest_blocker_sector(
            family, targets, templates=templates, physical_count=physical_count
        )

    sector_targets = tuple(
        target for target in unresolved
        if physical_sector(target, physical_count) == sector
    )
    sector_blockers = tuple(
        blocker for blocker in blockers
        if physical_sector(blocker, physical_count) == sector
    )

    equations = []
    total_blockers = len(sector_blockers)
    for n, blocker in enumerate(sector_blockers, start=1):
        equations.extend(local_same_seed_equations(family, blocker, templates=templates))
        if n == 1 or n == total_blockers or n % 10 == 0:
            _progress(progress, "build blocker IBP equations", n, total_blockers)
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if probe_points is None:
        probe_points = default_q01_probe_points(family)
    pivot_counts = []
    solved_counts = []
    solved_sets = []
    run_primes = []
    for run_no, point in enumerate(probe_points, start=1):
        _progress(progress, "specialize probe coefficients", run_no, len(probe_points))
        probed = specialize_ibp_system(equations, point)
        probed = _specialize_remaining_symbols_by_name(probed, point)
        prime = int(primes[(run_no - 1) % len(primes)])
        rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
        solved = frozenset(target for target in sector_targets if target in rules)
        solved_sets.append(solved)
        solved_counts.append(len(solved))
        pivot_counts.append(len(rules))
        run_primes.append(prime)

    stable = all(solved == solved_sets[0] for solved in solved_sets[1:]) if solved_sets else True
    return SectorLocalTargetRescueProfile(
        sector=sector,
        original_target_count=len(targets),
        globally_unresolved_target_count=len(unresolved),
        sector_unresolved_target_count=len(sector_targets),
        blocker_count=len(sector_blockers),
        equation_count=len(equations),
        integral_count=len(integrals),
        primes=tuple(run_primes),
        pivot_counts=tuple(pivot_counts),
        solved_sector_target_counts=tuple(solved_counts),
        unsolved_sector_target_counts=tuple(len(sector_targets) - count for count in solved_counts),
        stable_across_runs=stable,
    )
