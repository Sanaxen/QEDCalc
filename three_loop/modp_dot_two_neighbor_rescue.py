"""Dot-focused two-neighbor finite-field rescue for a small residual set.

The target use case is the Q01 four-line residual layer where all remaining
integrals have zero numerator degree and only dot degree one or two.  The second
neighbor layer is therefore restricted to numerator-free seeds, source-sector
active-line count +/- 1, and a small corrected-complexity ceiling.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralFamily,
    IntegralIndex,
    prune_zero_sectors,
    specialize_ibp_system,
)
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import physical_sector
from .local_block_elimination import local_same_seed_equations
from .nonscalar_neighbor_rescue import focused_neighbor_seeds
from .remaining_target_classification import (
    corrected_total_complexity,
    full_numerator_degree,
)
from .reverse_dependency import predecessor_candidates_for_target
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name


@dataclass(frozen=True)
class DotTwoNeighborRescueProfile:
    sector: tuple[int, ...]
    target_count: int
    layer1_seed_count: int
    layer2_added_seed_count: int
    total_seed_count: int
    same_sector_seed_count: int
    adjacent_sector_seed_count: int
    complexity_ceiling: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    pivot_counts: tuple[int, ...]
    solved_target_counts: tuple[int, ...]
    unresolved_target_counts: tuple[int, ...]
    stable_across_primes: bool
    stable_solved_indices: tuple[tuple[int, ...], ...]
    stable_unresolved_indices: tuple[tuple[int, ...], ...]


def dot_focused_two_neighbor_seeds(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    complexity_margin: int = 1,
) -> tuple[tuple[IntegralIndex, ...], tuple[IntegralIndex, ...]]:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if not targets:
        raise ValueError("dot-focused rescue requires at least one target")
    sectors = {physical_sector(t, physical_count) for t in targets}
    if len(sectors) != 1:
        raise ValueError(f"targets span multiple sectors: {sorted(sectors)}")
    source_sector = next(iter(sectors))
    source_lines = sum(source_sector)
    if any(full_numerator_degree(t, physical_count) != 0 for t in targets):
        raise ValueError("dot-focused rescue requires numerator-free targets")
    ceiling = max(corrected_total_complexity(t, physical_count) for t in targets) + int(complexity_margin)

    if templates is None:
        templates = build_ibp_derivative_templates(family)

    raw_layer1 = focused_neighbor_seeds(
        family,
        targets,
        templates=templates,
        physical_count=physical_count,
    )

    def allowed(seed: IntegralIndex) -> bool:
        active = sum(physical_sector(seed, physical_count))
        return (
            abs(active - source_lines) <= 1
            and full_numerator_degree(seed, physical_count) == 0
            and corrected_total_complexity(seed, physical_count) <= ceiling
        )

    layer1 = set(targets)
    layer1.update(seed for seed in raw_layer1 if allowed(seed))

    all_seeds = set(layer1)
    for seed in tuple(sorted(layer1, key=lambda idx: idx.powers)):
        for predecessor in predecessor_candidates_for_target(
            family, seed, templates=templates
        ):
            predecessor = family.validate_index(predecessor)
            if allowed(predecessor):
                all_seeds.add(predecessor)

    ordered_layer1 = tuple(sorted(layer1, key=lambda idx: idx.powers))
    ordered_all = tuple(sorted(all_seeds, key=lambda idx: idx.powers))
    return ordered_layer1, ordered_all


def audit_dot_two_neighbor_rescue_mod_p(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr],
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    complexity_margin: int = 1,
    progress=None,
) -> DotTwoNeighborRescueProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    sectors = {physical_sector(t, physical_count) for t in targets}
    if len(sectors) != 1:
        raise ValueError(f"targets span multiple sectors: {sorted(sectors)}")
    sector = next(iter(sectors))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    layer1, seeds = dot_focused_two_neighbor_seeds(
        family,
        targets,
        templates=templates,
        physical_count=physical_count,
        complexity_margin=complexity_margin,
    )
    source_lines = sum(sector)
    same_sector_seed_count = sum(
        physical_sector(seed, physical_count) == sector for seed in seeds
    )
    adjacent_sector_seed_count = sum(
        physical_sector(seed, physical_count) != sector
        and abs(sum(physical_sector(seed, physical_count)) - source_lines) <= 1
        for seed in seeds
    )
    complexity_ceiling = max(
        corrected_total_complexity(t, physical_count) for t in targets
    ) + int(complexity_margin)

    equations = []
    total = len(seeds)
    for n, seed in enumerate(seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if progress is not None and (n == 1 or n == total or n % 25 == 0):
            progress("build dot-focused two-neighbor equations", n, total)
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if progress is not None:
        progress("specialize dot-focused probe", 1, 1)
    probed = specialize_ibp_system(equations, probe_point)
    probed = _specialize_remaining_symbols_by_name(probed, probe_point)

    solved_sets: list[frozenset[IntegralIndex]] = []
    pivot_counts = []
    solved_counts = []
    unresolved_counts = []
    run_primes = []
    for n, prime in enumerate(primes, start=1):
        if progress is not None:
            progress("finite-field dot-focused elimination", n, len(primes))
        rules = _forward_eliminate_mod_p(probed, int(prime), progress=progress)
        solved = frozenset(target for target in targets if target in rules)
        solved_sets.append(solved)
        pivot_counts.append(len(rules))
        solved_counts.append(len(solved))
        unresolved_counts.append(len(targets) - len(solved))
        run_primes.append(int(prime))

    stable = all(s == solved_sets[0] for s in solved_sets[1:]) if solved_sets else True
    stable_solved = (
        solved_sets[0]
        if stable and solved_sets
        else (frozenset.intersection(*solved_sets) if solved_sets else frozenset())
    )
    stable_unresolved = set(targets) - set(stable_solved)

    return DotTwoNeighborRescueProfile(
        sector=sector,
        target_count=len(targets),
        layer1_seed_count=len(layer1),
        layer2_added_seed_count=len(seeds) - len(layer1),
        total_seed_count=len(seeds),
        same_sector_seed_count=same_sector_seed_count,
        adjacent_sector_seed_count=adjacent_sector_seed_count,
        complexity_ceiling=complexity_ceiling,
        equation_count=len(equations),
        integral_count=len(integrals),
        primes=tuple(run_primes),
        pivot_counts=tuple(pivot_counts),
        solved_target_counts=tuple(solved_counts),
        unresolved_target_counts=tuple(unresolved_counts),
        stable_across_primes=stable,
        stable_solved_indices=tuple(idx.powers for idx in sorted(stable_solved, key=lambda x: x.powers)),
        stable_unresolved_indices=tuple(idx.powers for idx in sorted(stable_unresolved, key=lambda x: x.powers)),
    )
