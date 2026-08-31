"""Exact symbolic reverse one-hop reductions for non-direct Q01 targets.

This turns the previously audited predecessor-seed rescue equations into real
finite-q symbolic reduction rules.  Only equations whose highest-ranked
integral is exactly the requested target are accepted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .dependency_audit import ibp_equation_from_templates, target_direct_pivot_equations
from .direct_symbolic_reduction import DirectSymbolicRule, solve_equation_for_target
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .reverse_dependency import reverse_pivot_equations_for_target


@dataclass(frozen=True)
class ReverseSymbolicProfile:
    target_count: int
    non_direct_target_count: int
    reverse_symbolic_rule_count: int
    unresolved_non_direct_target_count: int
    rules: tuple[DirectSymbolicRule, ...]


def reverse_symbolic_rule(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> DirectSymbolicRule | None:
    """Return the sparsest exact predecessor-seed pivot rule for target."""
    target = family.validate_index(target)
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    hits = reverse_pivot_equations_for_target(family, target, templates=templates)
    if not hits:
        return None

    equations = []
    grouped: dict[tuple[str, str], list[IBPDerivativeTemplate]] = {}
    for template in templates:
        grouped.setdefault((template.loop, template.vector), []).append(template)
    for seed, loop, vector in hits:
        equation = ibp_equation_from_templates(
            family,
            seed,
            loop,
            vector,
            grouped[(loop, vector)],
        )
        equations.append(equation)

    equation = min(
        equations,
        key=lambda eq: (
            len(eq.terms),
            sum(sp.count_ops(coeff) for coeff in eq.terms.values()),
            eq.label,
        ),
    )
    return solve_equation_for_target(equation, target)


def build_reverse_symbolic_profile(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> ReverseSymbolicProfile:
    """Build exact reverse one-hop rules for targets lacking direct rules."""
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    non_direct = []
    for target in targets:
        if not target_direct_pivot_equations(family, target, templates=templates):
            non_direct.append(target)

    rules = []
    for target in non_direct:
        rule = reverse_symbolic_rule(family, target, templates=templates)
        if rule is not None:
            rules.append(rule)

    return ReverseSymbolicProfile(
        target_count=len(targets),
        non_direct_target_count=len(non_direct),
        reverse_symbolic_rule_count=len(rules),
        unresolved_non_direct_target_count=len(non_direct) - len(rules),
        rules=tuple(rules),
    )
