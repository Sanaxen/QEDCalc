"""Audit whether unresolved-target blocker integrals are locally reducible."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .dependency_audit import target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, numerator_degree
from .pivot_blockers import blocker_indices_for_target, unresolved_targets


@dataclass(frozen=True)
class BlockerReductionProfile:
    unresolved_target_count: int
    blocker_count: int
    dot_one_blocker_count: int
    directly_pivotable_blocker_count: int
    nonpivotable_blocker_count: int
    direct_pivot_equation_count: int
    max_direct_pivot_equations_per_blocker: int
    directly_pivotable_dot_one_count: int
    nonpivotable_dot_one_count: int
    max_blocker_dot_degree: int
    max_blocker_numerator_degree: int

    @property
    def directly_pivotable_fraction(self) -> float:
        if self.blocker_count == 0:
            return 0.0
        return self.directly_pivotable_blocker_count / self.blocker_count


def collect_unresolved_blockers(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IntegralIndex, ...]:
    """Collect unique same-seed blockers for targets not rescued at zero/one hop."""
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    unresolved = unresolved_targets(family, targets, templates=templates)
    blockers: set[IntegralIndex] = set()
    for target in unresolved:
        blockers.update(blocker_indices_for_target(
            family, target, templates=templates
        ))
    return tuple(sorted(blockers, key=lambda index: index.powers, reverse=True))


def audit_blocker_reducibility(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> BlockerReductionProfile:
    """Measure how much of the blocker layer can be eliminated locally."""
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    unresolved = unresolved_targets(family, targets, templates=templates)
    blockers = collect_unresolved_blockers(
        family, targets, templates=templates
    )

    directly_pivotable = 0
    direct_equations = 0
    max_equations = 0
    dot_one = 0
    pivotable_dot_one = 0
    max_dot = 0
    max_num = 0

    for blocker in blockers:
        bdot = dot_degree(blocker, physical_count)
        bnum = numerator_degree(blocker, physical_count)
        max_dot = max(max_dot, bdot)
        max_num = max(max_num, bnum)
        is_dot_one = bdot == 1
        if is_dot_one:
            dot_one += 1
        equations = target_direct_pivot_equations(
            family, blocker, templates=templates
        )
        count = len(equations)
        if count:
            directly_pivotable += 1
            if is_dot_one:
                pivotable_dot_one += 1
        direct_equations += count
        max_equations = max(max_equations, count)

    return BlockerReductionProfile(
        unresolved_target_count=len(unresolved),
        blocker_count=len(blockers),
        dot_one_blocker_count=dot_one,
        directly_pivotable_blocker_count=directly_pivotable,
        nonpivotable_blocker_count=len(blockers) - directly_pivotable,
        direct_pivot_equation_count=direct_equations,
        max_direct_pivot_equations_per_blocker=max_equations,
        directly_pivotable_dot_one_count=pivotable_dot_one,
        nonpivotable_dot_one_count=dot_one - pivotable_dot_one,
        max_blocker_dot_degree=max_dot,
        max_blocker_numerator_degree=max_num,
    )
