"""Finite-field one-neighbor rescue for residuals of one physical sector."""
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
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name


@dataclass(frozen=True)
class SectorNeighborRescueProfile:
    sector: tuple[int, ...]
    target_count: int
    seed_count: int
    same_sector_seed_count: int
    neighbor_sector_seed_count: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    pivot_counts: tuple[int, ...]
    solved_target_counts: tuple[int, ...]
    unresolved_target_counts: tuple[int, ...]
    stable_across_primes: bool
    stable_solved_indices: tuple[tuple[int, ...], ...]
    stable_unresolved_indices: tuple[tuple[int, ...], ...]


def audit_sector_neighbor_rescue_mod_p(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr],
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress=None,
) -> SectorNeighborRescueProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if not targets:
        raise ValueError("neighbor rescue requires at least one target")
    sectors = {physical_sector(t, physical_count) for t in targets}
    if len(sectors) != 1:
        raise ValueError(f"neighbor rescue targets span multiple sectors: {sorted(sectors)}")
    sector = next(iter(sectors))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    seeds = focused_neighbor_seeds(
        family,
        targets,
        templates=templates,
        physical_count=physical_count,
    )
    same_sector_seed_count = sum(
        physical_sector(seed, physical_count) == sector for seed in seeds
    )

    equations = []
    total = len(seeds)
    for n, seed in enumerate(seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if progress is not None and (n == 1 or n == total or n % 25 == 0):
            progress("build one-neighbor residual equations", n, total)
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if progress is not None:
        progress("specialize residual neighbor probe", 1, 1)
    probed = specialize_ibp_system(equations, probe_point)
    probed = _specialize_remaining_symbols_by_name(probed, probe_point)

    solved_sets: list[frozenset[IntegralIndex]] = []
    pivot_counts = []
    solved_counts = []
    unresolved_counts = []
    run_primes = []
    for n, prime in enumerate(primes, start=1):
        if progress is not None:
            progress("finite-field residual neighbor elimination", n, len(primes))
        rules = _forward_eliminate_mod_p(probed, int(prime), progress=progress)
        solved = frozenset(target for target in targets if target in rules)
        solved_sets.append(solved)
        pivot_counts.append(len(rules))
        solved_counts.append(len(solved))
        unresolved_counts.append(len(targets) - len(solved))
        run_primes.append(int(prime))

    stable = all(s == solved_sets[0] for s in solved_sets[1:]) if solved_sets else True
    if stable and solved_sets:
        stable_solved = solved_sets[0]
    elif solved_sets:
        stable_solved = frozenset.intersection(*solved_sets)
    else:
        stable_solved = frozenset()
    stable_unresolved = set(targets) - set(stable_solved)

    return SectorNeighborRescueProfile(
        sector=sector,
        target_count=len(targets),
        seed_count=len(seeds),
        same_sector_seed_count=same_sector_seed_count,
        neighbor_sector_seed_count=len(seeds) - same_sector_seed_count,
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
