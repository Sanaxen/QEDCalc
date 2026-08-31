"""Exact one-step symbolic reductions for directly pivotable Q01 targets.

This module reuses the same-seed direct-pivot detector and solves one sparse IBP
equation for the target without running global symbolic Laporta elimination.
The resulting coefficients remain exact functions of D, m, z.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralFamily, IntegralIndex, sector_rank
from .dependency_audit import target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates


@dataclass(frozen=True)
class DirectSymbolicRule:
    target: tuple[int, ...]
    source_label: str
    target_coefficient: sp.Expr
    rhs: tuple[tuple[tuple[int, ...], sp.Expr], ...]

    @property
    def rhs_term_count(self) -> int:
        return len(self.rhs)


def solve_equation_for_target(
    equation: IBPEquation,
    target: IntegralIndex,
) -> DirectSymbolicRule:
    """Solve an exact linear IBP equation for one target integral."""
    if target not in equation.terms or equation.terms[target] == 0:
        raise ValueError("Target is absent from the IBP equation")
    pivot = max(equation.terms, key=sector_rank)
    if pivot != target:
        raise ValueError("Target is not the highest-ranked integral in the equation")

    coeff = sp.cancel(equation.terms[target])
    rhs = []
    for index, other in equation.terms.items():
        if index == target or other == 0:
            continue
        reduced = sp.cancel(-other / coeff)
        if reduced != 0:
            rhs.append((index.powers, reduced))
    rhs.sort(key=lambda item: sector_rank(IntegralIndex(item[0])), reverse=True)
    return DirectSymbolicRule(
        target=target.powers,
        source_label=equation.label,
        target_coefficient=coeff,
        rhs=tuple(rhs),
    )


def direct_symbolic_rule(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> DirectSymbolicRule | None:
    """Return the sparsest exact direct-pivot rule for target, if available."""
    target = family.validate_index(target)
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    equations = target_direct_pivot_equations(family, target, templates=templates)
    if not equations:
        return None
    equation = min(
        equations,
        key=lambda eq: (
            len(eq.terms),
            sum(sp.count_ops(coeff) for coeff in eq.terms.values()),
            eq.label,
        ),
    )
    return solve_equation_for_target(equation, target)


def build_direct_symbolic_rules(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[DirectSymbolicRule, ...]:
    """Build exact one-step rules for every directly pivotable target."""
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    out = []
    for target in targets:
        rule = direct_symbolic_rule(family, target, templates=templates)
        if rule is not None:
            out.append(rule)
    return tuple(out)
