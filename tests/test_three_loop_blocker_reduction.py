from qedcalc.operations.ibp import IntegralIndex
from three_loop.blocker_reduction import (
    audit_blocker_reducibility,
    collect_unresolved_blockers,
)
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family


def test_collect_unresolved_blockers_returns_unique_indices():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    blockers = collect_unresolved_blockers(family, targets, templates=templates)
    assert len(blockers) == len(set(blockers))
    assert all(len(index.powers) == 12 for index in blockers)


def test_blocker_reduction_profile_is_self_consistent():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    profile = audit_blocker_reducibility(family, targets, templates=templates)
    assert profile.blocker_count >= profile.directly_pivotable_blocker_count
    assert profile.blocker_count == (
        profile.directly_pivotable_blocker_count
        + profile.nonpivotable_blocker_count
    )
    assert profile.dot_one_blocker_count == (
        profile.directly_pivotable_dot_one_count
        + profile.nonpivotable_dot_one_count
    )
