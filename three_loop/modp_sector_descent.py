"""Finite-field descent audit for one Q01 physical sector.

Build same-seed IBP equations only from the requested sector targets, solve them
at one generic finite-field probe, and measure whether those targets descend to
strictly lower physical sectors.  This is a structural audit; it does not
reconstruct symbolic coefficients.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

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
from .modp_pivot_trace import forward_eliminate_mod_p_with_trace
from .modp_terminal_support import profile_terminal_support_mod_p
from .sector_local_modp import _specialize_remaining_symbols_by_name


@dataclass(frozen=True)
class ModPLowerSectorRow:
    sector: tuple[int, ...]
    terminal_count: int


@dataclass(frozen=True)
class ModPSectorDescentProfile:
    sector: tuple[int, ...]
    target_count: int
    equation_count: int
    integral_count: int
    prime: int
    pivot_count: int
    solved_target_count: int
    unsolved_target_count: int
    distinct_terminal_count: int
    same_sector_terminal_count: int
    lower_sector_terminal_count: int
    higher_or_other_sector_terminal_count: int
    lower_sector_count: int
    largest_lower_sector_terminal_count: int
    target_indices: tuple[tuple[int, ...], ...]
    unsolved_target_indices: tuple[tuple[int, ...], ...]
    terminal_indices: tuple[tuple[int, ...], ...]
    same_sector_terminal_indices: tuple[tuple[int, ...], ...]
    lower_sector_rows: tuple[ModPLowerSectorRow, ...]


def audit_modp_sector_descent(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr],
    prime: int = 1000003,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress=None,
) -> ModPSectorDescentProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if not targets:
        raise ValueError("sector descent requires at least one target")
    sectors = {physical_sector(t, physical_count) for t in targets}
    if len(sectors) != 1:
        raise ValueError(f"sector descent targets span multiple sectors: {sorted(sectors)}")
    sector = next(iter(sectors))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    equations = []
    total = len(targets)
    for n, target in enumerate(targets, start=1):
        equations.extend(local_same_seed_equations(family, target, templates=templates))
        if progress is not None and (n == 1 or n == total or n % 25 == 0):
            progress("build sector-target IBP equations", n, total)
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if progress is not None:
        progress("specialize probe coefficients", 1, 1)
    probed = specialize_ibp_system(equations, probe_point)
    probed = _specialize_remaining_symbols_by_name(probed, probe_point)
    trace = forward_eliminate_mod_p_with_trace(probed, int(prime), progress=progress)
    support = profile_terminal_support_mod_p(trace, targets)

    pivot_set = set(trace.pivot_indices)
    unsolved_targets = tuple(sorted((t for t in targets if t not in pivot_set), key=lambda index: index.powers))
    terminals = {
        IntegralIndex(powers)
        for record in support.records
        for powers in record.terminals
    }
    same_terminals: list[IntegralIndex] = []
    lower_counts: dict[tuple[int, ...], int] = {}
    other = 0
    source_lines = sum(sector)
    for terminal in terminals:
        t_sector = physical_sector(terminal, physical_count)
        if t_sector == sector:
            same_terminals.append(terminal)
        elif sum(t_sector) < source_lines:
            lower_counts[t_sector] = lower_counts.get(t_sector, 0) + 1
        else:
            other += 1

    ordered_targets = tuple(sorted(targets, key=lambda index: index.powers))
    ordered_terminals = tuple(sorted(terminals, key=lambda index: index.powers))
    ordered_same = tuple(sorted(same_terminals, key=lambda index: index.powers))
    lower_rows = tuple(
        ModPLowerSectorRow(sector=lower_sector, terminal_count=count)
        for lower_sector, count in sorted(
            lower_counts.items(), key=lambda item: (-item[1], item[0])
        )
    )

    return ModPSectorDescentProfile(
        sector=sector,
        target_count=len(targets),
        equation_count=len(equations),
        integral_count=len(integrals),
        prime=int(prime),
        pivot_count=trace.pivot_count,
        solved_target_count=support.solved_target_count,
        unsolved_target_count=support.unsolved_target_count,
        distinct_terminal_count=len(terminals),
        same_sector_terminal_count=len(same_terminals),
        lower_sector_terminal_count=sum(lower_counts.values()),
        higher_or_other_sector_terminal_count=other,
        lower_sector_count=len(lower_counts),
        largest_lower_sector_terminal_count=max(lower_counts.values(), default=0),
        target_indices=tuple(index.powers for index in ordered_targets),
        unsolved_target_indices=tuple(index.powers for index in unsolved_targets),
        terminal_indices=tuple(index.powers for index in ordered_terminals),
        same_sector_terminal_indices=tuple(index.powers for index in ordered_same),
        lower_sector_rows=lower_rows,
    )
