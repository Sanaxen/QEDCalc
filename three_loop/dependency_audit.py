"""Dependency-driven IBP audit for Q01 target integrals.

The goal is to determine whether a target integral can be solved directly from
one of the 15 IBP identities generated at that same seed, using QEDCalc's
sector-aware Laporta ordering.  This is a cheap diagnostic before constructing
large multi-seed systems.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralFamily, IntegralIndex, sector_rank
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates


@dataclass(frozen=True)
class TargetPivotAudit:
    target_count: int
    equation_count: int
    directly_pivotable_target_count: int
    nonpivotable_target_count: int
    direct_pivot_equation_count: int
    max_direct_pivot_equations_per_target: int

    @property
    def directly_pivotable_fraction(self) -> float:
        if self.target_count == 0:
            return 0.0
        return self.directly_pivotable_target_count / self.target_count


def _group_templates(
    templates: Iterable[IBPDerivativeTemplate],
) -> dict[tuple[str, str], tuple[IBPDerivativeTemplate, ...]]:
    grouped: dict[tuple[str, str], list[IBPDerivativeTemplate]] = {}
    for template in templates:
        grouped.setdefault((template.loop, template.vector), []).append(template)
    return {key: tuple(value) for key, value in grouped.items()}


def ibp_equation_from_templates(
    family: IntegralFamily,
    seed: IntegralIndex,
    loop: str,
    vector: str,
    templates: Iterable[IBPDerivativeTemplate],
) -> IBPEquation:
    """Build one exact IBP equation without recomputing symbolic derivatives."""
    seed = family.validate_index(seed)
    terms: dict[IntegralIndex, sp.Expr] = {}
    if loop == vector:
        terms[seed] = family.dimension_symbol

    for template in templates:
        a = template.denominator_index
        n_a = seed.powers[a]
        if n_a == 0:
            continue
        for coeff, monomial in template.terms:
            shifts = [0] * family.size
            shifts[a] += 1
            for j, power in enumerate(monomial):
                shifts[j] -= power
            target = IntegralIndex(tuple(
                seed.powers[j] + shifts[j]
                for j in range(family.size)
            ))
            terms[target] = terms.get(target, sp.Integer(0)) - sp.Integer(n_a) * coeff

    terms = {
        index: sp.cancel(coeff)
        for index, coeff in terms.items()
        if coeff != 0
    }
    return IBPEquation(terms, f"d/d{loop} · {vector}")


def target_direct_pivot_equations(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IBPEquation, ...]:
    """Return same-seed IBPs whose highest-ranked integral is the target."""
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    direct = []
    for (loop, vector), group in grouped.items():
        equation = ibp_equation_from_templates(family, target, loop, vector, group)
        if target not in equation.terms or equation.terms[target] == 0:
            continue
        if not equation.terms:
            continue
        pivot = max(equation.terms, key=sector_rank)
        if pivot == target:
            direct.append(equation)
    return tuple(direct)


def audit_target_direct_pivots(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> TargetPivotAudit:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    equation_count = len(targets) * len(grouped)
    directly_pivotable = 0
    direct_equation_count = 0
    max_per_target = 0
    for target in targets:
        direct = target_direct_pivot_equations(
            family,
            target,
            templates=templates,
        )
        count = len(direct)
        if count:
            directly_pivotable += 1
        direct_equation_count += count
        max_per_target = max(max_per_target, count)

    return TargetPivotAudit(
        target_count=len(targets),
        equation_count=equation_count,
        directly_pivotable_target_count=directly_pivotable,
        nonpivotable_target_count=len(targets) - directly_pivotable,
        direct_pivot_equation_count=direct_equation_count,
        max_direct_pivot_equations_per_target=max_per_target,
    )
