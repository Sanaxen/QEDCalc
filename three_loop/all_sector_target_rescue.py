"""Finite-field target rescue audit over every unresolved Q01 target sector."""
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
from .sector_local_target_rescue import unresolved_targets_after_one_hop

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class AllSectorRow:
    sector: tuple[int, ...]
    unresolved_target_count: int
    blocker_count: int
    equation_count: int
    integral_count: int
    pivot_counts: tuple[int, ...]
    solved_target_counts: tuple[int, ...]
    unsolved_target_counts: tuple[int, ...]
    stable_across_runs: bool


@dataclass(frozen=True)
class AllSectorTargetRescueProfile:
    original_target_count: int
    unresolved_target_count: int
    sector_count: int
    blocker_count: int
    solved_target_counts: tuple[int, ...]
    unsolved_target_counts: tuple[int, ...]
    stable_across_runs: bool
    rows: tuple[AllSectorRow, ...]


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def audit_all_sector_target_rescue(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> AllSectorTargetRescueProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    unresolved = unresolved_targets_after_one_hop(
        family, targets, templates=templates, progress=progress
    )
    blockers = collect_unresolved_blockers(family, targets, templates=templates)

    target_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    blocker_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    for target in unresolved:
        target_groups[physical_sector(target, physical_count)].append(target)
    for blocker in blockers:
        blocker_groups[physical_sector(blocker, physical_count)].append(blocker)

    sectors = tuple(sorted(
        target_groups,
        key=lambda sector: (len(target_groups[sector]), len(blocker_groups.get(sector, ())), sum(sector), sector),
        reverse=True,
    ))
    if probe_points is None:
        probe_points = default_q01_probe_points(family)

    solved_sets_by_run = [set() for _ in probe_points]
    rows = []
    for sector_no, sector in enumerate(sectors, start=1):
        sector_targets = tuple(target_groups[sector])
        sector_blockers = tuple(blocker_groups.get(sector, ()))
        _progress(progress, f"sector {sector_no}/{len(sectors)} start: targets={len(sector_targets)} blockers={len(sector_blockers)}")

        equations = []
        for n, blocker in enumerate(sector_blockers, start=1):
            equations.extend(local_same_seed_equations(family, blocker, templates=templates))
            if n == 1 or n == len(sector_blockers) or n % 25 == 0:
                _progress(progress, f"sector {sector_no}/{len(sectors)} build equations", n, len(sector_blockers))
        equations = prune_zero_sectors(family, equations)
        integrals = {idx for equation in equations for idx in equation.terms}

        pivot_counts = []
        solved_counts = []
        solved_sector_sets = []
        for run_no, point in enumerate(probe_points, start=1):
            _progress(progress, f"sector {sector_no}/{len(sectors)} specialize run", run_no, len(probe_points))
            probed = specialize_ibp_system(equations, point)
            probed = _specialize_remaining_symbols_by_name(probed, point)
            prime = int(primes[(run_no - 1) % len(primes)])
            rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
            solved = frozenset(target for target in sector_targets if target in rules)
            solved_sector_sets.append(solved)
            solved_sets_by_run[run_no - 1].update(solved)
            pivot_counts.append(len(rules))
            solved_counts.append(len(solved))

        stable = all(s == solved_sector_sets[0] for s in solved_sector_sets[1:]) if solved_sector_sets else True
        rows.append(AllSectorRow(
            sector=sector,
            unresolved_target_count=len(sector_targets),
            blocker_count=len(sector_blockers),
            equation_count=len(equations),
            integral_count=len(integrals),
            pivot_counts=tuple(pivot_counts),
            solved_target_counts=tuple(solved_counts),
            unsolved_target_counts=tuple(len(sector_targets) - count for count in solved_counts),
            stable_across_runs=stable,
        ))
        _progress(progress, f"sector {sector_no}/{len(sectors)} done: solved={solved_counts} stable={stable}")

    solved_counts_total = tuple(len(solved) for solved in solved_sets_by_run)
    unsolved_counts_total = tuple(len(unresolved) - count for count in solved_counts_total)
    stable_total = (
        all(s == solved_sets_by_run[0] for s in solved_sets_by_run[1:])
        if solved_sets_by_run else True
    ) and all(row.stable_across_runs for row in rows)
    return AllSectorTargetRescueProfile(
        original_target_count=len(targets),
        unresolved_target_count=len(unresolved),
        sector_count=len(sectors),
        blocker_count=len(blockers),
        solved_target_counts=solved_counts_total,
        unsolved_target_counts=unsolved_counts_total,
        stable_across_runs=stable_total,
        rows=tuple(rows),
    )
