import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.reverse_dependency import (
    predecessor_candidates_for_target,
    reverse_pivot_equations_for_target,
    audit_reverse_dependencies,
)


def test_predecessor_candidates_have_family_width():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    candidates = predecessor_candidates_for_target(family, target, templates=templates)
    assert candidates
    assert all(len(index.powers) == family.size for index in candidates)


def test_reverse_pivot_hits_contain_target_as_pivot():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    hits = reverse_pivot_equations_for_target(family, target, templates=templates)
    assert isinstance(hits, tuple)


def test_reverse_dependency_profile_counts_consistently():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    profile = audit_reverse_dependencies(family, targets, templates=templates)
    assert profile.target_count == 2
    assert profile.rescued_target_count + profile.unresolved_target_count == profile.nonpivotable_target_count
    assert profile.unique_rescue_seed_count <= profile.candidate_seed_count
