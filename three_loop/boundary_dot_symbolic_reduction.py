"""Exact symbolic reductions for directly pivotable dot-only Q01 boundary integrals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .direct_symbolic_reduction import DirectSymbolicRule, direct_symbolic_rule
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree
from .remaining_target_classification import full_numerator_degree


@dataclass(frozen=True)
class BoundaryDotSymbolicProfile:
    target_count: int
    directly_reduced_count: int
    unresolved_count: int
    rules: tuple[DirectSymbolicRule, ...]


def is_dot_only(index: IntegralIndex, physical_count: int = 9) -> bool:
    return dot_degree(index, physical_count) > 0 and full_numerator_degree(index, physical_count) == 0


def build_boundary_dot_symbolic_profile(
    family: IntegralFamily,
    indices: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> BoundaryDotSymbolicProfile:
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    targets = tuple(dict.fromkeys(
        family.validate_index(index)
        for index in indices
        if is_dot_only(index, physical_count)
    ))
    rules = []
    for target in targets:
        rule = direct_symbolic_rule(family, target, templates=templates)
        if rule is not None:
            rules.append(rule)
    return BoundaryDotSymbolicProfile(
        target_count=len(targets),
        directly_reduced_count=len(rules),
        unresolved_count=len(targets) - len(rules),
        rules=tuple(rules),
    )
