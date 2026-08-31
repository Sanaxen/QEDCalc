"""Finite-field rank audit for a small candidate-master block.

For a homogeneous IBP system A x = 0 and a selected column block T, the
quantity relevant to whether variables in T are determined by the complement
is the rank of the restricted submatrix A_T itself.  If the complement is held
fixed, the residual freedom inside T is

    dim ker(A_T) = |T| - rank(A_T).

The older diagnostic rank(A) - rank(A without T) is retained only as an
auxiliary column-span statistic.  It must not be interpreted as the master
freedom of T: for the simple relation x + y = 0, deleting the x column leaves
the full rank unchanged even though x is completely determined by y.

This remains a structural finite-field diagnostic, not an exact symbolic
master proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import sympy as sp

from qedcalc.operations.ibp import (
    IBPEquation,
    IntegralFamily,
    IntegralIndex,
    prune_zero_sectors,
    specialize_ibp_system,
)
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .local_block_elimination import local_same_seed_equations
from .modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name


@dataclass(frozen=True)
class ModPLocalMasterRankProfile:
    target_count: int
    block_count: int
    seed_count: int
    equation_count: int
    integral_count: int
    primes: tuple[int, ...]
    full_ranks: tuple[int, ...]
    without_target_ranks: tuple[int, ...]
    target_added_column_ranks: tuple[int, ...]
    target_restricted_ranks: tuple[int, ...]
    target_conditional_free_dimensions: tuple[int, ...]
    without_block_ranks: tuple[int, ...]
    block_added_column_ranks: tuple[int, ...]
    block_restricted_ranks: tuple[int, ...]
    block_conditional_free_dimensions: tuple[int, ...]
    stable_across_primes: bool


def _drop_columns(
    equations: Iterable[IBPEquation], columns: set[IntegralIndex]
) -> tuple[IBPEquation, ...]:
    out = []
    for equation in equations:
        terms = {idx: coeff for idx, coeff in equation.terms.items() if idx not in columns}
        if terms:
            out.append(IBPEquation(terms, equation.label))
    return tuple(out)


def _keep_columns(
    equations: Iterable[IBPEquation], columns: set[IntegralIndex]
) -> tuple[IBPEquation, ...]:
    out = []
    for equation in equations:
        terms = {idx: coeff for idx, coeff in equation.terms.items() if idx in columns}
        if terms:
            out.append(IBPEquation(terms, equation.label))
    return tuple(out)


def _modp_rank(equations: Sequence[IBPEquation], prime: int, progress=None) -> int:
    rules = _forward_eliminate_mod_p(equations, int(prime), progress=progress)
    return len(rules)


def conditional_block_rank_mod_p(
    equations: Sequence[IBPEquation],
    columns: Iterable[IntegralIndex],
    prime: int,
    *,
    progress=None,
) -> tuple[int, int]:
    """Return (restricted rank, conditional free dimension) for a column block."""
    ordered = tuple(dict.fromkeys(columns))
    restricted = _keep_columns(equations, set(ordered))
    rank = _modp_rank(restricted, int(prime), progress=progress)
    return rank, len(ordered) - rank


def audit_local_master_rank_mod_p(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    block: Iterable[IntegralIndex],
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr],
    primes: Sequence[int] = (1000003, 1000033),
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    complexity_margin: int = 1,
    progress=None,
) -> ModPLocalMasterRankProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    block = tuple(dict.fromkeys(family.validate_index(t) for t in block))
    if not targets:
        raise ValueError("local master-rank audit requires targets")
    if not set(targets).issubset(set(block)):
        raise ValueError("target block must contain all targets")
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    _, seeds = dot_focused_two_neighbor_seeds(
        family,
        targets,
        templates=templates,
        complexity_margin=complexity_margin,
    )
    equations = []
    total = len(seeds)
    for n, seed in enumerate(seeds, start=1):
        equations.extend(local_same_seed_equations(family, seed, templates=templates))
        if progress is not None and (n == 1 or n == total or n % 25 == 0):
            progress("build local master-rank equations", n, total)
    equations = prune_zero_sectors(family, equations)
    integrals = {idx for equation in equations for idx in equation.terms}

    if progress is not None:
        progress("specialize local master-rank probe", 1, 1)
    probed = specialize_ibp_system(equations, probe_point)
    probed = _specialize_remaining_symbols_by_name(probed, probe_point)

    no_targets = _drop_columns(probed, set(targets))
    no_block = _drop_columns(probed, set(block))
    only_targets = _keep_columns(probed, set(targets))
    only_block = _keep_columns(probed, set(block))

    full_ranks = []
    without_target_ranks = []
    target_added_column_ranks = []
    target_restricted_ranks = []
    target_conditional_free_dimensions = []
    without_block_ranks = []
    block_added_column_ranks = []
    block_restricted_ranks = []
    block_conditional_free_dimensions = []
    run_primes = []

    for run_no, prime in enumerate(primes, start=1):
        if progress is not None:
            progress("rank full local system", run_no, len(primes))
        full_rank = _modp_rank(probed, int(prime), progress=progress)
        if progress is not None:
            progress("rank without dotted targets", run_no, len(primes))
        no_target_rank = _modp_rank(no_targets, int(prime), progress=progress)
        if progress is not None:
            progress("rank dotted-target restricted matrix", run_no, len(primes))
        target_rank = _modp_rank(only_targets, int(prime), progress=progress)
        if progress is not None:
            progress("rank without candidate block", run_no, len(primes))
        no_block_rank = _modp_rank(no_block, int(prime), progress=progress)
        if progress is not None:
            progress("rank candidate-block restricted matrix", run_no, len(primes))
        block_rank = _modp_rank(only_block, int(prime), progress=progress)

        full_ranks.append(full_rank)
        without_target_ranks.append(no_target_rank)
        target_added_column_ranks.append(full_rank - no_target_rank)
        target_restricted_ranks.append(target_rank)
        target_conditional_free_dimensions.append(len(targets) - target_rank)
        without_block_ranks.append(no_block_rank)
        block_added_column_ranks.append(full_rank - no_block_rank)
        block_restricted_ranks.append(block_rank)
        block_conditional_free_dimensions.append(len(block) - block_rank)
        run_primes.append(int(prime))

    signatures = list(zip(
        full_ranks,
        without_target_ranks,
        target_added_column_ranks,
        target_restricted_ranks,
        target_conditional_free_dimensions,
        without_block_ranks,
        block_added_column_ranks,
        block_restricted_ranks,
        block_conditional_free_dimensions,
    ))
    stable = all(sig == signatures[0] for sig in signatures[1:]) if signatures else True

    return ModPLocalMasterRankProfile(
        target_count=len(targets),
        block_count=len(block),
        seed_count=len(seeds),
        equation_count=len(equations),
        integral_count=len(integrals),
        primes=tuple(run_primes),
        full_ranks=tuple(full_ranks),
        without_target_ranks=tuple(without_target_ranks),
        target_added_column_ranks=tuple(target_added_column_ranks),
        target_restricted_ranks=tuple(target_restricted_ranks),
        target_conditional_free_dimensions=tuple(target_conditional_free_dimensions),
        without_block_ranks=tuple(without_block_ranks),
        block_added_column_ranks=tuple(block_added_column_ranks),
        block_restricted_ranks=tuple(block_restricted_ranks),
        block_conditional_free_dimensions=tuple(block_conditional_free_dimensions),
        stable_across_primes=stable,
    )
