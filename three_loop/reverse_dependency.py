"""Reverse one-hop dependency search for nonpivotable Q01 targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, sector_rank
from .dependency_audit import ibp_equation_from_templates, target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates


@dataclass(frozen=True)
class ReverseDependencyProfile:
    target_count: int
    nonpivotable_target_count: int
    rescued_target_count: int
    unresolved_target_count: int
    unique_rescue_seed_count: int
    candidate_seed_count: int
    rescue_equation_count: int
    max_rescue_equations_per_target: int


def _group_templates(
    templates: Iterable[IBPDerivativeTemplate],
) -> dict[tuple[str, str], tuple[IBPDerivativeTemplate, ...]]:
    grouped: dict[tuple[str, str], list[IBPDerivativeTemplate]] = {}
    for template in templates:
        grouped.setdefault((template.loop, template.vector), []).append(template)
    return {key: tuple(value) for key, value in grouped.items()}


def predecessor_candidates_for_target(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[IntegralIndex, ...]:
    """Invert all one-step template shifts to obtain possible equation seeds."""
    target = family.validate_index(target)
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    out: set[IntegralIndex] = set()
    for template in templates:
        a = template.denominator_index
        for _, monomial in template.terms:
            shifts = [0] * family.size
            shifts[a] += 1
            for j, power in enumerate(monomial):
                shifts[j] -= power
            seed = IntegralIndex(tuple(
                target.powers[j] - shifts[j]
                for j in range(family.size)
            ))
            # The source term exists only when the differentiated denominator
            # carries a nonzero power at the predecessor seed.
            if seed.powers[a] != 0:
                out.add(seed)
    return tuple(sorted(out, key=lambda index: index.powers, reverse=True))


def reverse_pivot_equations_for_target(
    family: IntegralFamily,
    target: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[tuple[IntegralIndex, str, str], ...]:
    """Find one-hop predecessor seeds whose IBP equation pivots on target."""
    target = family.validate_index(target)
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    predecessors = predecessor_candidates_for_target(
        family, target, templates=templates
    )
    hits: set[tuple[IntegralIndex, str, str]] = set()
    for seed in predecessors:
        for (loop, vector), group in grouped.items():
            equation = ibp_equation_from_templates(
                family, seed, loop, vector, group
            )
            if target not in equation.terms or equation.terms[target] == 0:
                continue
            if max(equation.terms, key=sector_rank) == target:
                hits.add((seed, loop, vector))
    return tuple(sorted(hits, key=lambda hit: (hit[0].powers, hit[1], hit[2]), reverse=True))


def audit_reverse_dependencies(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> ReverseDependencyProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    nonpivotable = []
    for target in targets:
        if not target_direct_pivot_equations(
            family, target, templates=templates
        ):
            nonpivotable.append(target)

    rescued = 0
    unique_seeds: set[IntegralIndex] = set()
    candidate_seeds: set[IntegralIndex] = set()
    rescue_equations = 0
    max_per_target = 0
    for target in nonpivotable:
        candidate_seeds.update(predecessor_candidates_for_target(
            family, target, templates=templates
        ))
        hits = reverse_pivot_equations_for_target(
            family, target, templates=templates
        )
        if hits:
            rescued += 1
        rescue_equations += len(hits)
        max_per_target = max(max_per_target, len(hits))
        unique_seeds.update(seed for seed, _, _ in hits)

    return ReverseDependencyProfile(
        target_count=len(targets),
        nonpivotable_target_count=len(nonpivotable),
        rescued_target_count=rescued,
        unresolved_target_count=len(nonpivotable) - rescued,
        unique_rescue_seed_count=len(unique_seeds),
        candidate_seed_count=len(candidate_seeds),
        rescue_equation_count=rescue_equations,
        max_rescue_equations_per_target=max_per_target,
    )
