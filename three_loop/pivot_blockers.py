"""Classify why unresolved Q01 targets fail to become local IBP pivots."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, sector_rank
from .dependency_audit import ibp_equation_from_templates, target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, numerator_degree, physical_sector
from .reverse_dependency import reverse_pivot_equations_for_target


@dataclass(frozen=True)
class PivotBlockerProfile:
    target_count: int
    unresolved_target_count: int
    blocked_equation_count: int
    blocker_index_count: int
    blocker_same_sector_count: int
    blocker_higher_sector_count: int
    blocker_higher_dot_count: int
    blocker_higher_numerator_count: int
    max_blocker_dot_degree: int
    max_blocker_numerator_degree: int


def _group_templates(
    templates: Iterable[IBPDerivativeTemplate],
) -> dict[tuple[str, str], tuple[IBPDerivativeTemplate, ...]]:
    grouped: dict[tuple[str, str], list[IBPDerivativeTemplate]] = {}
    for template in templates:
        grouped.setdefault((template.loop, template.vector), []).append(template)
    return {key: tuple(value) for key, value in grouped.items()}


def unresolved_targets(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IntegralIndex, ...]:
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    out = []
    for target in targets:
        target = family.validate_index(target)
        if target_direct_pivot_equations(family, target, templates=templates):
            continue
        if reverse_pivot_equations_for_target(family, target, templates=templates):
            continue
        out.append(target)
    return tuple(out)


def blocker_indices_for_target(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IntegralIndex, ...]:
    """Return harder-than-target integrals blocking same-seed IBP pivots."""
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    blockers: set[IntegralIndex] = set()
    trank = sector_rank(target)
    for (loop, vector), group in grouped.items():
        equation = ibp_equation_from_templates(family, target, loop, vector, group)
        if target not in equation.terms or equation.terms[target] == 0:
            continue
        for index in equation.terms:
            if sector_rank(index) > trank:
                blockers.add(index)
    return tuple(sorted(blockers, key=sector_rank, reverse=True))


def audit_pivot_blockers(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> PivotBlockerProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    unresolved = unresolved_targets(family, targets, templates=templates)

    blocker_set: set[IntegralIndex] = set()
    blocked_equations = 0
    same_sector = 0
    higher_sector = 0
    higher_dot = 0
    higher_num = 0
    max_dot = 0
    max_num = 0

    for target in unresolved:
        trank = sector_rank(target)
        tsector = physical_sector(target, physical_count)
        tdot = dot_degree(target, physical_count)
        tnum = numerator_degree(target, physical_count)
        for (loop, vector), group in grouped.items():
            equation = ibp_equation_from_templates(family, target, loop, vector, group)
            if target not in equation.terms or equation.terms[target] == 0:
                continue
            blockers = [idx for idx in equation.terms if sector_rank(idx) > trank]
            if not blockers:
                continue
            blocked_equations += 1
            for blocker in blockers:
                if blocker in blocker_set:
                    continue
                blocker_set.add(blocker)
                bsector = physical_sector(blocker, physical_count)
                bdot = dot_degree(blocker, physical_count)
                bnum = numerator_degree(blocker, physical_count)
                if bsector == tsector:
                    same_sector += 1
                else:
                    higher_sector += 1
                if bdot > tdot:
                    higher_dot += 1
                if bnum > tnum:
                    higher_num += 1
                max_dot = max(max_dot, bdot)
                max_num = max(max_num, bnum)

    return PivotBlockerProfile(
        target_count=len(targets),
        unresolved_target_count=len(unresolved),
        blocked_equation_count=blocked_equations,
        blocker_index_count=len(blocker_set),
        blocker_same_sector_count=same_sector,
        blocker_higher_sector_count=higher_sector,
        blocker_higher_dot_count=higher_dot,
        blocker_higher_numerator_count=higher_num,
        max_blocker_dot_degree=max_dot,
        max_blocker_numerator_degree=max_num,
    )
