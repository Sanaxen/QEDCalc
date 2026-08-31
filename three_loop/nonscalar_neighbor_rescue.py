"""Focused finite-field rescue for the three remaining Q01 nonscalar targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, prune_zero_sectors, specialize_ibp_system
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import physical_sector
from .local_block_elimination import local_same_seed_equations
from .remaining_target_classification import full_numerator_degree
from .reverse_dependency import predecessor_candidates_for_target
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name
from .sector_local_probe import default_q01_probe_points

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class NonscalarNeighborRescueProfile:
    target_count: int
    seed_count: int
    same_sector_seed_count: int
    neighbor_sector_seed_count: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    pivot_counts: tuple[int, ...]
    solved_target_counts: tuple[int, ...]
    unsolved_target_counts: tuple[int, ...]
    stable_across_runs: bool


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def _active_lines(index: IntegralIndex, physical_count: int) -> int:
    return sum(physical_sector(index, physical_count))


def focused_neighbor_seeds(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> tuple[IntegralIndex, ...]:
    """Collect target/predecessor seeds, allowing only the same or one-adjacent sector.

    A predecessor is retained when its active physical-line count differs from
    the target by at most one.  This deliberately opens the parent/subsector
    boundary that the previous same-sector audit forbade, without expanding to
    the full one-step frontier.
    """
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    seeds: set[IntegralIndex] = set(targets)
    for target in targets:
        target_active = _active_lines(target, physical_count)
        for seed in predecessor_candidates_for_target(family, target, templates=templates):
            if abs(_active_lines(seed, physical_count) - target_active) <= 1:
                seeds.add(seed)
    return tuple(sorted(seeds, key=lambda idx: idx.powers))


def audit_nonscalar_neighbor_rescue(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> NonscalarNeighborRescueProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    targets = tuple(t for t in targets if full_numerator_degree(t, physical_count) > 0)
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    seeds = focused_neighbor_seeds(
        family, targets, templates=templates, physical_count=physical_count
    )
    target_sectors = {physical_sector(t, physical_count) for t in targets}
    same_sector = sum(physical_sector(seed, physical_count) in target_sectors for seed in seeds)
    neighbor_sector = len(seeds) - same_sector

    equations = []
    for n, seed in enumerate(seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if n == 1 or n == len(seeds) or n % 25 == 0:
            _progress(progress, "build focused neighbor equations", n, len(seeds))
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if probe_points is None:
        probe_points = default_q01_probe_points(family)
    solved_sets = []
    pivot_counts = []
    solved_counts = []
    run_primes = []
    for run_no, point in enumerate(probe_points, start=1):
        _progress(progress, "specialize focused probe", run_no, len(probe_points))
        probed = specialize_ibp_system(equations, point)
        probed = _specialize_remaining_symbols_by_name(probed, point)
        prime = int(primes[(run_no - 1) % len(primes)])
        rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
        solved = frozenset(target for target in targets if target in rules)
        solved_sets.append(solved)
        pivot_counts.append(len(rules))
        solved_counts.append(len(solved))
        run_primes.append(prime)

    stable = all(s == solved_sets[0] for s in solved_sets[1:]) if solved_sets else True
    return NonscalarNeighborRescueProfile(
        target_count=len(targets),
        seed_count=len(seeds),
        same_sector_seed_count=same_sector,
        neighbor_sector_seed_count=neighbor_sector,
        equation_count=len(equations),
        integral_count=len(integrals),
        primes=tuple(run_primes),
        pivot_counts=tuple(pivot_counts),
        solved_target_counts=tuple(solved_counts),
        unsolved_target_counts=tuple(len(targets) - count for count in solved_counts),
        stable_across_runs=stable,
    )
