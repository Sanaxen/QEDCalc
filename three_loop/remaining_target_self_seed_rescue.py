"""Finite-field rescue of the remaining Q01 targets by adding target IBPs themselves.

Earlier sector-local audits generated equations from blocker seeds only.  This
module keeps the same blocker layer but also inserts the 15 IBP equations of
each still-unresolved target in its own sector.  It is intentionally focused on
the final small target set rather than expanding the global frontier.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, prune_zero_sectors, specialize_ibp_system
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import physical_sector
from .local_block_elimination import local_same_seed_equations
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name
from .sector_local_probe import default_q01_probe_points

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class RemainingSelfSeedSectorRow:
    sector: tuple[int, ...]
    target_count: int
    blocker_seed_count: int
    target_seed_count: int
    total_seed_count: int
    equation_count: int
    integral_count: int
    pivot_counts: tuple[int, ...]
    solved_target_counts: tuple[int, ...]
    unsolved_target_counts: tuple[int, ...]
    stable_across_runs: bool


@dataclass(frozen=True)
class RemainingSelfSeedRescueProfile:
    original_target_count: int
    remaining_target_count: int
    sector_count: int
    blocker_seed_count: int
    target_seed_count: int
    total_seed_count: int
    solved_target_counts: tuple[int, ...]
    unsolved_target_counts: tuple[int, ...]
    stable_across_runs: bool
    rows: tuple[RemainingSelfSeedSectorRow, ...]


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def combined_sector_seeds(
    blockers: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
) -> tuple[IntegralIndex, ...]:
    """Return deterministic deduplicated blocker + target seed union."""
    return tuple(sorted(set(blockers) | set(targets), key=lambda idx: idx.powers))


def audit_remaining_target_self_seed_rescue(
    family: IntegralFamily,
    original_targets: Iterable[IntegralIndex],
    remaining_targets: Iterable[IntegralIndex],
    *,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> RemainingSelfSeedRescueProfile:
    original_targets = tuple(dict.fromkeys(family.validate_index(t) for t in original_targets))
    remaining_targets = tuple(dict.fromkeys(family.validate_index(t) for t in remaining_targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    blockers = collect_unresolved_blockers(family, original_targets, templates=templates)
    selected_sectors = {physical_sector(target, physical_count) for target in remaining_targets}

    target_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    blocker_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    for target in remaining_targets:
        target_groups[physical_sector(target, physical_count)].append(target)
    for blocker in blockers:
        sector = physical_sector(blocker, physical_count)
        if sector in selected_sectors:
            blocker_groups[sector].append(blocker)

    sectors = tuple(sorted(
        selected_sectors,
        key=lambda sector: (len(target_groups[sector]), len(blocker_groups.get(sector, ())), sum(sector), sector),
        reverse=True,
    ))
    if probe_points is None:
        probe_points = default_q01_probe_points(family)

    solved_sets_by_run = [set() for _ in probe_points]
    rows = []
    all_blockers: set[IntegralIndex] = set()
    all_target_seeds: set[IntegralIndex] = set()
    all_seeds: set[IntegralIndex] = set()

    for sector_no, sector in enumerate(sectors, start=1):
        sector_targets = tuple(target_groups[sector])
        sector_blockers = tuple(blocker_groups.get(sector, ()))
        seeds = combined_sector_seeds(sector_blockers, sector_targets)
        all_blockers.update(sector_blockers)
        all_target_seeds.update(sector_targets)
        all_seeds.update(seeds)

        _progress(
            progress,
            f"sector {sector_no}/{len(sectors)} start: targets={len(sector_targets)} blockers={len(sector_blockers)} seeds={len(seeds)}",
        )
        equations = []
        for n, seed in enumerate(seeds, start=1):
            equations.extend(local_same_seed_equations(family, seed, templates=templates))
            if n == 1 or n == len(seeds) or n % 25 == 0:
                _progress(progress, f"sector {sector_no}/{len(sectors)} build equations", n, len(seeds))
        equations = prune_zero_sectors(family, equations)
        integrals = {idx for equation in equations for idx in equation.terms}

        pivot_counts = []
        solved_counts = []
        solved_sets = []
        for run_no, point in enumerate(probe_points, start=1):
            _progress(progress, f"sector {sector_no}/{len(sectors)} specialize run", run_no, len(probe_points))
            probed = specialize_ibp_system(equations, point)
            probed = _specialize_remaining_symbols_by_name(probed, point)
            prime = int(primes[(run_no - 1) % len(primes)])
            rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
            solved = frozenset(target for target in sector_targets if target in rules)
            solved_sets.append(solved)
            solved_sets_by_run[run_no - 1].update(solved)
            pivot_counts.append(len(rules))
            solved_counts.append(len(solved))

        stable = all(s == solved_sets[0] for s in solved_sets[1:]) if solved_sets else True
        rows.append(RemainingSelfSeedSectorRow(
            sector=sector,
            target_count=len(sector_targets),
            blocker_seed_count=len(sector_blockers),
            target_seed_count=len(sector_targets),
            total_seed_count=len(seeds),
            equation_count=len(equations),
            integral_count=len(integrals),
            pivot_counts=tuple(pivot_counts),
            solved_target_counts=tuple(solved_counts),
            unsolved_target_counts=tuple(len(sector_targets) - count for count in solved_counts),
            stable_across_runs=stable,
        ))
        _progress(progress, f"sector {sector_no}/{len(sectors)} done: solved={solved_counts} stable={stable}")

    solved_counts_total = tuple(len(solved) for solved in solved_sets_by_run)
    unsolved_counts_total = tuple(len(remaining_targets) - count for count in solved_counts_total)
    stable_total = (
        all(s == solved_sets_by_run[0] for s in solved_sets_by_run[1:])
        if solved_sets_by_run else True
    ) and all(row.stable_across_runs for row in rows)

    return RemainingSelfSeedRescueProfile(
        original_target_count=len(original_targets),
        remaining_target_count=len(remaining_targets),
        sector_count=len(sectors),
        blocker_seed_count=len(all_blockers),
        target_seed_count=len(all_target_seeds),
        total_seed_count=len(all_seeds),
        solved_target_counts=solved_counts_total,
        unsolved_target_counts=unsolved_counts_total,
        stable_across_runs=stable_total,
        rows=tuple(rows),
    )
