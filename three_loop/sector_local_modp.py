"""Finite-field sector-local Laporta rank probe for Q01."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, prune_zero_sectors, sector_rank, specialize_ibp_system
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, physical_sector
from .local_block_elimination import local_same_seed_equations
from .sector_local_probe import default_q01_probe_points
from .sector_local_laporta import largest_blocker_sector

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class SectorLocalModPProfile:
    sector: tuple[int, ...]
    blocker_count: int
    dot_one_blocker_count: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    pivot_counts: tuple[int, ...]
    solved_blocker_counts: tuple[int, ...]
    solved_dot_one_counts: tuple[int, ...]
    stable_across_runs: bool


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def _rational_mod_p(value: sp.Expr, prime: int) -> int:
    value = sp.cancel(sp.sympify(value))
    if not value.is_Rational:
        raise ValueError(f"Coefficient is not rational after probe substitution: {value}")
    num, den = value.as_numer_denom()
    den_mod = int(den) % prime
    if den_mod == 0:
        raise ZeroDivisionError("Probe denominator vanished modulo prime.")
    return (int(num) % prime) * pow(den_mod, prime - 2, prime) % prime


def _forward_eliminate_mod_p(equations, prime: int, progress: ProgressCallback | None = None):
    indices = {idx for eq in equations for idx in eq.terms}
    ordered = sorted(indices, key=sector_rank, reverse=True)
    rank_pos = {idx: pos for pos, idx in enumerate(ordered)}
    rows = []
    for eq in equations:
        row = {}
        for idx, coeff in eq.terms.items():
            c = _rational_mod_p(coeff, prime)
            if c:
                row[idx] = c
        if row:
            rows.append(row)
    rows.sort(key=lambda row: min(rank_pos[idx] for idx in row))

    rules = {}
    total = len(rows)
    for n, row in enumerate(rows, start=1):
        while True:
            solved = [idx for idx in row if idx in rules]
            if not solved:
                break
            lhs = min(solved, key=lambda idx: rank_pos[idx])
            fac = row.pop(lhs) % prime
            if fac:
                for idx, coeff in rules[lhs].items():
                    val = (row.get(idx, 0) + fac * coeff) % prime
                    if val:
                        row[idx] = val
                    else:
                        row.pop(idx, None)
        if row:
            pivot = min(row, key=lambda idx: rank_pos[idx])
            c = row.pop(pivot) % prime
            inv = pow(c, prime - 2, prime)
            rhs = {idx: (-coeff * inv) % prime for idx, coeff in row.items() if coeff % prime}
            rules[pivot] = rhs
        if n == 1 or n == total or n % 100 == 0:
            _progress(progress, f"mod-p eliminate p={prime}", n, total)
    return rules


def audit_sector_local_modp(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    sector: tuple[int, ...] | None = None,
    probe_points: Sequence[Mapping[sp.Symbol, sp.Expr]] | None = None,
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> SectorLocalModPProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    if sector is None:
        sector = largest_blocker_sector(family, targets, templates=templates, physical_count=physical_count)
    sector_blockers = tuple(b for b in blockers if physical_sector(b, physical_count) == sector)
    dot_one = tuple(b for b in sector_blockers if dot_degree(b, physical_count) == 1)

    equations = []
    for n, blocker in enumerate(sector_blockers, start=1):
        equations.extend(local_same_seed_equations(family, blocker, templates=templates))
        if n == 1 or n == len(sector_blockers) or n % 10 == 0:
            _progress(progress, "build IBP equations", n, len(sector_blockers))
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for eq in equations for idx in eq.terms}

    if probe_points is None:
        probe_points = default_q01_probe_points(family)
    runs = []
    run_primes = []
    for point_no, point in enumerate(probe_points, start=1):
        _progress(progress, "specialize probe coefficients", point_no, len(probe_points))
        probed = specialize_ibp_system(equations, point)
        prime = int(primes[(point_no - 1) % len(primes)])
        rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
        solved = frozenset(b for b in sector_blockers if b in rules)
        runs.append((len(rules), solved, sum(b in rules for b in dot_one)))
        run_primes.append(prime)

    stable = all(run[1] == runs[0][1] for run in runs[1:]) if runs else True
    return SectorLocalModPProfile(
        sector=sector,
        blocker_count=len(sector_blockers),
        dot_one_blocker_count=len(dot_one),
        equation_count=len(equations),
        integral_count=len(integrals),
        primes=tuple(run_primes),
        pivot_counts=tuple(run[0] for run in runs),
        solved_blocker_counts=tuple(len(run[1]) for run in runs),
        solved_dot_one_counts=tuple(run[2] for run in runs),
        stable_across_runs=stable,
    )
