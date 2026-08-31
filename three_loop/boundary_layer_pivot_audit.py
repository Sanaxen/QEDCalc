"""Direct-pivot audit for classified Q01 symbolic-boundary layers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .dependency_audit import target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates


@dataclass(frozen=True)
class BoundaryLayerPivotRow:
    category: str
    target_count: int
    directly_pivotable_count: int
    nonpivotable_count: int
    direct_pivot_equation_count: int
    max_direct_pivot_equations_per_target: int


@dataclass(frozen=True)
class BoundaryLayerPivotProfile:
    target_count: int
    directly_pivotable_count: int
    nonpivotable_count: int
    rows: tuple[BoundaryLayerPivotRow, ...]


def audit_boundary_layer_direct_pivots(
    family: IntegralFamily,
    categories: Mapping[str, Iterable[IntegralIndex]],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> BoundaryLayerPivotProfile:
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    rows = []
    total_targets = 0
    total_pivotable = 0
    for category in sorted(categories):
        targets = tuple(dict.fromkeys(family.validate_index(index) for index in categories[category]))
        pivotable = 0
        equation_count = 0
        max_per_target = 0
        for target in targets:
            equations = target_direct_pivot_equations(family, target, templates=templates)
            count = len(equations)
            if count:
                pivotable += 1
            equation_count += count
            max_per_target = max(max_per_target, count)
        rows.append(BoundaryLayerPivotRow(
            category=category,
            target_count=len(targets),
            directly_pivotable_count=pivotable,
            nonpivotable_count=len(targets) - pivotable,
            direct_pivot_equation_count=equation_count,
            max_direct_pivot_equations_per_target=max_per_target,
        ))
        total_targets += len(targets)
        total_pivotable += pivotable

    return BoundaryLayerPivotProfile(
        target_count=total_targets,
        directly_pivotable_count=total_pivotable,
        nonpivotable_count=total_targets - total_pivotable,
        rows=tuple(rows),
    )
