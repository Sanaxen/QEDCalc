"""Generic normalization for exactly duplicate/proportional denominators.

If two denominator symbols obey D_dep = c * D_keep, then an integral factor

    D_keep**(-a_keep) * D_dep**(-a_dep)

is exactly

    c**(-a_dep) * D_keep**(-(a_keep + a_dep)).

This module performs that exponent merge without any diagram-specific logic.
It is intentionally small so multi-loop adapters can reuse it before sending a
family to external IBP reducers such as Kira.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import sympy as sp


@dataclass(frozen=True)
class DuplicateDenominatorRule:
    """One exact proportional-denominator elimination rule, using 1-based slots."""

    dependent_index: int
    keep_index: int
    scale: sp.Expr = sp.Integer(1)

    def validate(self, size: int) -> None:
        if not 1 <= self.dependent_index <= size:
            raise ValueError("dependent denominator index outside family")
        if not 1 <= self.keep_index <= size:
            raise ValueError("kept denominator index outside family")
        if self.dependent_index == self.keep_index:
            raise ValueError("dependent and kept denominator indices must differ")
        if sp.simplify(self.scale) == 0:
            raise ValueError("duplicate-denominator scale must be nonzero")


@dataclass(frozen=True)
class NormalizedIntegralPowers:
    powers: tuple[int, ...]
    prefactor: sp.Expr


def normalize_duplicate_denominator_powers(
    powers: Sequence[int],
    rules: Sequence[DuplicateDenominatorRule],
) -> NormalizedIntegralPowers:
    """Merge exponents for exact proportional denominators.

    The input and output keep the same slot count; eliminated dependent slots
    are set to zero.  A later family-layout adapter may remove/repurpose those
    zero slots for additional ISPs.
    """
    out = [int(value) for value in powers]
    prefactor = sp.Integer(1)
    for rule in rules:
        rule.validate(len(out))
        dep = rule.dependent_index - 1
        keep = rule.keep_index - 1
        exponent = out[dep]
        if exponent:
            out[keep] += exponent
            prefactor *= sp.sympify(rule.scale) ** (-exponent)
            out[dep] = 0
    return NormalizedIntegralPowers(tuple(out), sp.factor(prefactor))
