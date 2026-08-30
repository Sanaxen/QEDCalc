"""Local same-seed Laporta elimination for Q01 blocker integrals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import (
    IntegralFamily,
    IntegralIndex,
    laporta_forward_eliminate,
    sector_rank,
)
from .blocker_reduction import collect_unresolved_blockers
from .dependency_audit import ibp_equation_from_templates
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree


@dataclass(frozen=True)
class LocalBlockEliminationProfile:
    blocker_count: int
    dot_one_blocker_count: int
    locally_solved_blocker_count: int
    locally_unsolved_blocker_count: int
    locally_solved_dot_one_count: int
    locally_unsolved_dot_one_count: int
    total_local_equations: int
    total_local_rules: int
    max_rules_per_blocker: int


def _group_templates(
    templates: Iterable[IBPDerivativeTemplate],
) -> dict[tuple[str, str], tuple[IBPDerivativeTemplate, ...]]:
    grouped: dict[tuple[str, str], list[IBPDerivativeTemplate]] = {}
    for template in templates:
        grouped.setdefault((template.loop, template.vector), []).append(template)
    return {key: tuple(value) for key, value in grouped.items()}


def local_same_seed_equations(
    family: IntegralFamily,
    seed: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
):
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    grouped = _group_templates(templates)
    return tuple(
        ibp_equation_from_templates(family, seed, loop, vector, group)
        for (loop, vector), group in grouped.items()
    )


def blocker_locally_solved(
    family: IntegralFamily,
    blocker: IntegralIndex,
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
) -> tuple[bool, int]:
    """Run the 15 same-seed IBPs as one finite local Laporta system."""
    equations = local_same_seed_equations(
        family, blocker, templates=templates
    )
    rules = laporta_forward_eliminate(
        equations,
        rank=sector_rank,
        family=family,
        prune_scaleless=True,
    )
    solved = any(rule.lhs == blocker for rule in rules)
    return solved, len(rules)


def audit_local_block_elimination(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
) -> LocalBlockEliminationProfile:
    targets = tuple(dict.fromkeys(family.validate_index(target) for target in targets))
    if templates is None:
        templates = build_ibp_derivative_templates(family)
    blockers = collect_unresolved_blockers(
        family, targets, templates=templates
    )

    dot_one = 0
    solved = 0
    solved_dot_one = 0
    total_rules = 0
    max_rules = 0
    for blocker in blockers:
        is_dot_one = dot_degree(blocker, physical_count) == 1
        if is_dot_one:
            dot_one += 1
        is_solved, rule_count = blocker_locally_solved(
            family, blocker, templates=templates
        )
        total_rules += rule_count
        max_rules = max(max_rules, rule_count)
        if is_solved:
            solved += 1
            if is_dot_one:
                solved_dot_one += 1

    return LocalBlockEliminationProfile(
        blocker_count=len(blockers),
        dot_one_blocker_count=dot_one,
        locally_solved_blocker_count=solved,
        locally_unsolved_blocker_count=len(blockers) - solved,
        locally_solved_dot_one_count=solved_dot_one,
        locally_unsolved_dot_one_count=dot_one - solved_dot_one,
        total_local_equations=len(blockers) * len(_group_templates(templates)),
        total_local_rules=total_rules,
        max_rules_per_blocker=max_rules,
    )
