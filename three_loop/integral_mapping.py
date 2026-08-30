"""Map finite-q Q01 scalar numerators into the 12-index integral family."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .integral_family import Q01_SEED, q01_integral_family


@dataclass(frozen=True)
class IntegralLinearCombination:
    """Sparse linear combination of integral-family indices."""

    terms: Mapping[IntegralIndex, sp.Expr]

    def simplified(self) -> "IntegralLinearCombination":
        out: dict[IntegralIndex, sp.Expr] = {}
        for index, coeff in self.terms.items():
            value = sp.cancel(sp.sympify(coeff))
            if value != 0:
                out[index] = value
        return IntegralLinearCombination(out)

    @property
    def integral_count(self) -> int:
        return len(self.terms)

    def add(self, other: "IntegralLinearCombination") -> "IntegralLinearCombination":
        out = dict(self.terms)
        for index, coeff in other.terms.items():
            out[index] = out.get(index, sp.Integer(0)) + coeff
            if out[index] == 0:
                out.pop(index)
        return IntegralLinearCombination(out)


def scalar_numerator_to_integrals(
    expr: sp.Expr,
    *,
    family: IntegralFamily | None = None,
    seed: IntegralIndex = Q01_SEED,
) -> IntegralLinearCombination:
    """Convert one scalar numerator into a sparse sum of integral indices.

    For a seed integral

        J(n_1,...,n_N) = int 1 / prod_i D_i^{n_i},

    a numerator monomial ``prod_i D_i^{a_i}`` shifts the index to
    ``(n_1-a_1,...,n_N-a_N)``.  This also handles auxiliary ISP variables:
    their seed powers are zero, so numerator ISP powers become negative indices.
    """
    family = q01_integral_family() if family is None else family
    seed = family.validate_index(seed)
    expression = sp.sympify(expr)

    reduced = sp.expand(expression.subs(family.scalar_product_rules))
    leftovers = sorted(
        str(symbol)
        for symbol in reduced.free_symbols
        if str(symbol).startswith("SP__")
    )
    if leftovers:
        raise ValueError(f"Unreduced scalar products in numerator mapping: {leftovers}")

    denominator_symbols = family.denominator_symbols
    polynomial = sp.Poly(reduced, *denominator_symbols, domain="EX")
    terms: dict[IntegralIndex, sp.Expr] = {}
    for monomial, coeff in polynomial.terms():
        powers = tuple(
            seed_power - int(numerator_power)
            for seed_power, numerator_power in zip(seed.powers, monomial)
        )
        index = IntegralIndex(powers)
        terms[index] = terms.get(index, sp.Integer(0)) + coeff

    return IntegralLinearCombination(terms).simplified()


def q01_scalar_numerator_to_integrals(expr: sp.Expr) -> IntegralLinearCombination:
    """Q01 convenience wrapper using the canonical finite-q family and seed."""
    return scalar_numerator_to_integrals(
        expr,
        family=q01_integral_family(),
        seed=Q01_SEED,
    )
