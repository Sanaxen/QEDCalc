"""Efficient one-step IBP frontier analysis for Q01 target integrals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralFamily,
    IntegralIndex,
    reduce_directional_derivative,
)
from .laporta_plan import dot_degree, numerator_degree, physical_sector


@dataclass(frozen=True)
class IBPDerivativeTemplate:
    denominator_index: int
    loop: str
    vector: str
    terms: tuple[tuple[sp.Expr, tuple[int, ...]], ...]


@dataclass(frozen=True)
class IBPFrontierProfile:
    seed_count: int
    generated_index_count: int
    new_index_count: int
    physical_sector_count: int
    max_dot_degree: int
    max_numerator_degree: int
    max_active_physical_lines: int


def _denominator_polynomial_terms(
    expr: sp.Expr,
    denominator_symbols: tuple[sp.Symbol, ...],
) -> tuple[tuple[sp.Expr, tuple[int, ...]], ...]:
    poly = sp.Poly(sp.expand(expr), *denominator_symbols)
    return tuple(
        (sp.factor(coeff), tuple(int(power) for power in monomial))
        for monomial, coeff in poly.terms()
    )


def build_ibp_derivative_templates(
    family: IntegralFamily,
    *,
    vectors: tuple[str, ...] | None = None,
) -> tuple[IBPDerivativeTemplate, ...]:
    """Precompute seed-independent derivative polynomials once per family."""
    if vectors is None:
        vectors = family.loop_momenta + family.external_momenta
    denominator_symbols = family.denominator_symbols
    templates = []
    for loop in family.loop_momenta:
        for vector in vectors:
            for denominator_index in range(family.size):
                reduced = reduce_directional_derivative(
                    family, denominator_index, loop, vector
                )
                terms = _denominator_polynomial_terms(reduced, denominator_symbols)
                templates.append(IBPDerivativeTemplate(
                    denominator_index=denominator_index,
                    loop=loop,
                    vector=vector,
                    terms=terms,
                ))
    return tuple(templates)


def one_step_ibp_frontier(
    family: IntegralFamily,
    seeds: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IntegralIndex, ...]:
    """Return all integral indices appearing after one IBP layer.

    Coefficients are irrelevant for frontier planning.  The index shifts are
    determined entirely by the denominator derivative monomials and the
    nonzero seed powers.  The original seeds are included in the result.
    """
    seeds = tuple(family.validate_index(seed) for seed in seeds)
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    out = set(seeds)
    for seed in seeds:
        for template in templates:
            a = template.denominator_index
            if seed.powers[a] == 0:
                continue
            for _, monomial in template.terms:
                shifts = [0] * family.size
                shifts[a] += 1
                for j, power in enumerate(monomial):
                    shifts[j] -= power
                out.add(IntegralIndex(tuple(
                    seed.powers[j] + shifts[j] for j in range(family.size)
                )))
    return tuple(sorted(out, key=lambda index: index.powers, reverse=True))


def profile_ibp_frontier(
    seeds: Iterable[IntegralIndex],
    frontier: Iterable[IntegralIndex],
    *,
    physical_count: int = 9,
) -> IBPFrontierProfile:
    seeds = tuple(seeds)
    frontier = tuple(frontier)
    seed_set = set(seeds)
    sectors = {physical_sector(index, physical_count) for index in frontier}
    return IBPFrontierProfile(
        seed_count=len(seed_set),
        generated_index_count=len(frontier),
        new_index_count=len(set(frontier) - seed_set),
        physical_sector_count=len(sectors),
        max_dot_degree=max((dot_degree(index, physical_count) for index in frontier), default=0),
        max_numerator_degree=max((numerator_degree(index, physical_count) for index in frontier), default=0),
        max_active_physical_lines=max((sum(physical_sector(index, physical_count)) for index in frontier), default=0),
    )
